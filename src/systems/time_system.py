######################載入套件######################
import pygame
import math
from enum import Enum
from config.settings import *


######################時間相關列舉######################
class TimeOfDay(Enum):
    """
    一天中的時段列舉\n
    \n
    用於區分不同時段，影響遊戲中的光線、NPC行為等\n
    每個時段對應不同的遊戲機制和視覺效果\n
    """

    DAWN = "dawn"  # 黎明 (05:00-07:00)
    MORNING = "morning"  # 早晨 (07:00-11:00)
    NOON = "noon"  # 中午 (11:00-14:00)
    AFTERNOON = "afternoon"  # 下午 (14:00-18:00)
    EVENING = "evening"  # 傍晚 (18:00-20:00)
    NIGHT = "night"  # 夜晚 (20:00-05:00)


class DayOfWeek(Enum):
    """
    星期列舉 - 特殊設定：週六日為工作日，週一至五為休息日\n
    \n
    這個設定與現實相反，創造獨特的遊戲體驗\n
    影響 NPC 的行為模式和商店營業時間\n
    """

    MONDAY = "monday"  # 週一 (休息日)
    TUESDAY = "tuesday"  # 週二 (休息日)
    WEDNESDAY = "wednesday"  # 週三 (休息日)
    THURSDAY = "thursday"  # 週四 (休息日)
    FRIDAY = "friday"  # 週五 (休息日)
    SATURDAY = "saturday"  # 週六 (工作日)
    SUNDAY = "sunday"  # 週日 (工作日)


######################時間管理器######################
class TimeManager:
    """
    遊戲時間系統管理器 - 控制遊戲內的時間流逝和相關機制\n
    \n
    負責管理遊戲內的時間流逝，包括：\n
    1. 日夜循環系統 - 影響光線和視覺效果\n
    2. 星期循環系統 - 影響 NPC 行為和商店營業\n
    3. 時間事件觸發 - 在特定時間點觸發事件\n
    4. 時間相關的遊戲機制控制\n
    \n
    特色設定：\n
    - 週六日為工作日，NPC 會去工作\n
    - 週一至五為休息日，NPC 會到處閒逛\n
    - 一天 24 小時，每小時對應現實中的特定時間\n
    """

    def __init__(self, time_scale=1.0):
        """
        初始化時間管理器\n
        \n
        參數:\n
        time_scale (float): 時間流逝倍率，1.0 表示正常速度，範圍 0.1-10.0\n
        """
        # 基本時間設定
        self.time_scale = max(0.1, min(10.0, time_scale))  # 限制在合理範圍內

        # 遊戲時間 (24小時制)
        self.hour = 8  # 遊戲開始時間：早上8點
        self.minute = 0  # 分鐘
        self.second = 0.0  # 秒（用浮點數以支援平滑時間流逝）

        # 星期設定 (從週六開始，這是工作日)
        self.day_of_week = DayOfWeek.SATURDAY
        self.day_number = 1  # 遊戲開始第1天

        # 時間流逝速度設定 (現實1秒 = 遊戲中多少秒)
        self.seconds_per_real_second = 60.0  # 現實1秒 = 遊戲1分鐘

        # 時間事件回調系統
        self.time_callbacks = {}  # 時間點回調 (小時:分鐘 -> 回調函數清單)
        self.interval_callbacks = {}  # 間隔回調 (間隔秒數 -> 上次觸發時間)

        # 光線和環境設定
        self.ambient_light = 1.0  # 環境光強度 (0.0-1.0)
        self.sky_color = BACKGROUND_COLOR

        # 時間相關的遊戲狀態
        self.is_work_day = True  # 今天是否為工作日
        self.shops_open = True  # 商店是否營業

        print(f"時間系統初始化完成 - 開始時間: {self.get_time_string()}")
        print(f"時間流逝倍率: {self.time_scale}x")

    def update(self, dt):
        """
        更新時間系統\n
        \n
        每幀調用此方法來推進遊戲時間\n
        處理時間流逝、事件觸發、環境變化等\n
        \n
        參數:\n
        dt (float): 自上次更新以來的現實時間間隔（秒）\n
        """
        # 計算這一幀遊戲時間的增量
        game_time_delta = dt * self.seconds_per_real_second * self.time_scale

        # 記錄舊的時間以檢測小時變化
        old_hour = self.hour
        old_day = self.day_number

        # 更新遊戲時間
        self.second += game_time_delta

        # 處理時間進位 (秒 -> 分 -> 時 -> 日)
        if self.second >= 60.0:
            minutes_to_add = int(self.second // 60.0)
            self.second = self.second % 60.0
            self.minute += minutes_to_add

            if self.minute >= 60:
                hours_to_add = self.minute // 60
                self.minute = self.minute % 60
                self.hour += hours_to_add

                if self.hour >= 24:
                    days_to_add = self.hour // 24
                    self.hour = self.hour % 24
                    self._advance_days(days_to_add)

        # 檢查是否有小時變化，觸發相關事件
        if old_hour != self.hour:
            self._on_hour_changed(old_hour, self.hour)

        # 檢查是否有日期變化
        if old_day != self.day_number:
            self._on_day_changed()

        # 更新環境效果（光線、天空顏色等）
        self._update_environment_effects()

        # 處理時間回調
        self._check_time_callbacks()

    def _advance_days(self, days):
        """
        推進日期\n
        \n
        參數:\n
        days (int): 要推進的天數\n
        """
        for _ in range(days):
            self.day_number += 1

            # 推進星期
            current_day_index = list(DayOfWeek).index(self.day_of_week)
            next_day_index = (current_day_index + 1) % 7
            self.day_of_week = list(DayOfWeek)[next_day_index]

    def _on_hour_changed(self, old_hour, new_hour):
        """
        小時變化時的處理\n
        \n
        參數:\n
        old_hour (int): 舊的小時\n
        new_hour (int): 新的小時\n
        """
        print(f"時間變化: {old_hour:02d}:xx -> {new_hour:02d}:xx")

        # 觸發小時變化的特殊事件
        if new_hour == 0:
            print("🌙 午夜時分")
        elif new_hour == 6:
            print("🌅 日出時分")
        elif new_hour == 12:
            print("☀️ 正午時分")
        elif new_hour == 18:
            print("🌆 日落時分")

    def _on_day_changed(self):
        """
        日期變化時的處理\n
        """
        # 更新工作日狀態
        self.is_work_day = self._is_current_work_day()

        # 輸出新的一天資訊
        day_type = "工作日" if self.is_work_day else "休息日"
        print(
            f"🗓️ 新的一天開始！第 {self.day_number} 天，{self._get_day_name()}（{day_type}）"
        )

    def _update_environment_effects(self):
        """
        更新環境效果（光線、天空顏色等）\n
        """
        # 根據時間計算環境光強度
        time_of_day = self.get_time_of_day()

        if time_of_day == TimeOfDay.NIGHT:
            # 夜晚較暗
            self.ambient_light = 0.3 + 0.2 * math.sin(math.pi * self.hour / 12)
        elif time_of_day == TimeOfDay.DAWN:
            # 黎明漸亮
            dawn_progress = (self.hour - 5) / 2.0  # 5-7點的進度
            self.ambient_light = 0.4 + 0.6 * dawn_progress
        elif time_of_day in [TimeOfDay.MORNING, TimeOfDay.NOON, TimeOfDay.AFTERNOON]:
            # 白天最亮
            self.ambient_light = 1.0
        elif time_of_day == TimeOfDay.EVENING:
            # 傍晚漸暗
            evening_progress = (self.hour - 18) / 2.0  # 18-20點的進度
            self.ambient_light = 1.0 - 0.6 * evening_progress

        # 確保光線強度在合理範圍內
        self.ambient_light = max(0.1, min(1.0, self.ambient_light))

        # 根據時間設定天空顏色
        self._update_sky_color()

    def _update_sky_color(self):
        """
        根據時間更新天空顏色\n
        """
        time_of_day = self.get_time_of_day()

        # 定義不同時段的天空顏色
        if time_of_day == TimeOfDay.NIGHT:
            # 深藍色夜空
            self.sky_color = (25, 25, 112)  # Midnight Blue
        elif time_of_day == TimeOfDay.DAWN:
            # 黎明的橘紅色
            self.sky_color = (255, 140, 0)  # Dark Orange
        elif time_of_day in [TimeOfDay.MORNING, TimeOfDay.NOON]:
            # 清朗的天空藍
            self.sky_color = (135, 206, 235)  # Sky Blue
        elif time_of_day == TimeOfDay.AFTERNOON:
            # 午後的淺藍
            self.sky_color = (176, 224, 230)  # Powder Blue
        elif time_of_day == TimeOfDay.EVENING:
            # 傍晚的金黃色
            self.sky_color = (255, 215, 0)  # Gold

    def _check_time_callbacks(self):
        """
        檢查並觸發時間回調\n
        """
        # 檢查特定時間點的回調
        current_time_key = f"{self.hour:02d}:{self.minute:02d}"
        if current_time_key in self.time_callbacks:
            for callback in self.time_callbacks[current_time_key]:
                try:
                    callback(self)
                except Exception as e:
                    print(f"時間回調執行錯誤: {e}")

    def get_time_of_day(self):
        """
        獲取當前時段\n
        \n
        回傳:\n
        TimeOfDay: 當前時段列舉值\n
        """
        if 5 <= self.hour < 7:
            return TimeOfDay.DAWN
        elif 7 <= self.hour < 11:
            return TimeOfDay.MORNING
        elif 11 <= self.hour < 14:
            return TimeOfDay.NOON
        elif 14 <= self.hour < 18:
            return TimeOfDay.AFTERNOON
        elif 18 <= self.hour < 20:
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT

    def get_time_string(self, include_seconds=False):
        """
        獲取格式化的時間字串\n
        \n
        參數:\n
        include_seconds (bool): 是否包含秒數\n
        \n
        回傳:\n
        str: 格式化的時間字串，如 "08:30" 或 "08:30:45"\n
        """
        if include_seconds:
            return f"{self.hour:02d}:{self.minute:02d}:{int(self.second):02d}"
        else:
            return f"{self.hour:02d}:{self.minute:02d}"

    def get_date_string(self):
        """
        獲取格式化的日期字串\n
        \n
        回傳:\n
        str: 格式化的日期字串，如 "第3天 週一（休息日）"\n
        """
        day_type = "工作日" if self.is_work_day else "休息日"
        day_name = self._get_day_name()
        return f"第{self.day_number}天 {day_name}（{day_type}）"

    def _get_day_name(self):
        """
        獲取星期名稱\n
        \n
        回傳:\n
        str: 中文星期名稱\n
        """
        day_names = {
            DayOfWeek.MONDAY: "週一",
            DayOfWeek.TUESDAY: "週二",
            DayOfWeek.WEDNESDAY: "週三",
            DayOfWeek.THURSDAY: "週四",
            DayOfWeek.FRIDAY: "週五",
            DayOfWeek.SATURDAY: "週六",
            DayOfWeek.SUNDAY: "週日",
        }
        return day_names.get(self.day_of_week, "未知")

    def _is_current_work_day(self):
        """
        檢查當前是否為工作日\n
        \n
        根據遊戲設定：週六日為工作日，週一至五為休息日\n
        \n
        回傳:\n
        bool: 是否為工作日\n
        """
        return self.day_of_week in [DayOfWeek.SATURDAY, DayOfWeek.SUNDAY]

    def is_work_time(self):
        """
        檢查當前是否為工作時間\n
        \n
        工作時間定義：工作日的 9:00-17:00\n
        \n
        回傳:\n
        bool: 是否為工作時間\n
        """
        if not self.is_work_day:
            return False
        return 9 <= self.hour < 17

    def is_shop_hours(self):
        """
        檢查當前是否為商店營業時間\n
        \n
        商店營業時間：每天 7:00-22:00\n
        \n
        回傳:\n
        bool: 商店是否營業\n
        """
        return 7 <= self.hour < 22

    def register_time_callback(self, hour, minute, callback):
        """
        註冊特定時間的回調函數\n
        \n
        參數:\n
        hour (int): 小時 (0-23)\n
        minute (int): 分鐘 (0-59)\n
        callback (function): 回調函數，接收 TimeManager 作為參數\n
        """
        time_key = f"{hour:02d}:{minute:02d}"
        if time_key not in self.time_callbacks:
            self.time_callbacks[time_key] = []
        self.time_callbacks[time_key].append(callback)
        print(f"註冊時間回調: {time_key}")

    def set_time(self, hour, minute=0, second=0):
        """
        設定當前時間（主要用於測試）\n
        \n
        參數:\n
        hour (int): 小時 (0-23)\n
        minute (int): 分鐘 (0-59)\n
        second (float): 秒 (0-59.999)\n
        """
        self.hour = max(0, min(23, hour))
        self.minute = max(0, min(59, minute))
        self.second = max(0.0, min(59.999, float(second)))

        print(f"時間已設定為: {self.get_time_string(True)}")
        self._update_environment_effects()

    def set_time_scale(self, scale):
        """
        設定時間流逝倍率\n
        \n
        參數:\n
        scale (float): 時間倍率，範圍 0.1-10.0\n
        """
        old_scale = self.time_scale
        self.time_scale = max(0.1, min(10.0, scale))
        print(f"時間倍率變更: {old_scale}x -> {self.time_scale}x")

    def get_ambient_light(self):
        """
        獲取當前環境光強度\n
        \n
        回傳:\n
        float: 環境光強度 (0.0-1.0)\n
        """
        return self.ambient_light

    def get_sky_color(self):
        """
        獲取當前天空顏色\n
        \n
        回傳:\n
        tuple: RGB 顏色值\n
        """
        return self.sky_color

    def get_debug_info(self):
        """
        獲取除錯資訊\n
        \n
        回傳:\n
        dict: 包含所有時間系統狀態的字典\n
        """
        return {
            "time": self.get_time_string(True),
            "date": self.get_date_string(),
            "time_of_day": self.get_time_of_day().value,
            "is_work_day": self.is_work_day,
            "is_work_time": self.is_work_time(),
            "is_shop_hours": self.is_shop_hours(),
            "ambient_light": f"{self.ambient_light:.2f}",
            "time_scale": f"{self.time_scale}x",
            "sky_color": self.sky_color,
        }

    def update_time_state(self):
        """
        更新時間相關狀態 - 供外部快進時間時調用\n
        \n
        更新工作日狀態、環境效果等\n
        """
        # 更新工作日狀態
        self.is_work_day = self._is_current_work_day()

        # 更新環境效果
        self._update_environment_effects()

        # 觸發時間相關回調
        self._check_time_callbacks()
