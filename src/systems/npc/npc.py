######################載入套件######################
import pygame
import random
import math
from enum import Enum
from src.systems.npc.profession import Profession, ProfessionData


######################NPC 狀態列舉######################
class NPCState(Enum):
    """
    NPC 狀態列舉\n
    \n
    定義 NPC 可能的行為狀態\n
    每個狀態對應不同的行為模式和 AI 邏輯\n
    """

    WORKING = "工作中"  # 在工作場所執行職務
    RESTING = "休息中"  # 休息時間或下班時間
    MOVING = "移動中"  # 在不同地點間移動
    INJURED = "受傷住院"  # 在醫院接受治療
    IDLE = "閒置中"  # 待機狀態
    SLEEPING = "睡覺中"  # 夜間睡眠時間


######################NPC 基礎類別######################
class NPC:
    """
    非玩家角色 (NPC) 基礎類別\n
    \n
    包含 NPC 的基本屬性和行為邏輯\n
    每個 NPC 都有獨特的身份、職業和生活軌跡\n
    支援智能的行為模式和與環境的互動\n
    \n
    主要功能:\n
    1. 個人身份管理 (姓名、職業、住所)\n
    2. 工作時間表管理\n
    3. 移動和位置管理\n
    4. 健康狀態和受傷機制\n
    5. 對話和互動系統\n
    """

    # NPC 編號計數器，確保每個 NPC 都有唯一 ID
    _id_counter = 1

    def __init__(self, profession, initial_position=(0, 0)):
        """
        初始化 NPC\n
        \n
        參數:\n
        profession (Profession): NPC 的職業類型\n
        initial_position (tuple): 初始位置座標 (x, y)\n
        """
        # 基本身份資訊
        self.id = NPC._id_counter
        NPC._id_counter += 1

        self.name = self._generate_name()
        self.profession = profession
        self.state = NPCState.IDLE

        # 位置和移動相關
        self.x, self.y = initial_position
        self.target_x = self.x
        self.target_y = self.y
        self.speed = random.uniform(1.0, 2.5)  # 隨機移動速度

        # 工作和住所
        self.workplace = None
        self.home_position = initial_position
        self.current_work_area = None  # 電力工人需要負責的區域

        # 生活時間表
        self.schedule = ProfessionData.get_profession_schedule(profession)
        self.current_hour = 8  # 初始時間設為早上8點

        # 健康狀態
        self.is_injured = False
        self.hospital_stay_time = 0  # 住院剩餘時間 (小時)
        self.injury_cause = None

        # 外觀屬性
        self.color = ProfessionData.get_profession_color(profession)
        self.size = 12  # NPC 顯示大小

        # 對話系統
        self.dialogue_lines = self._generate_dialogue()
        self.last_interaction_time = 0

        # 特殊屬性
        self.assigned_area = None  # 電力工人的負責區域
        self.shop_id = None  # 商店員工的工作店鋪 ID

        # 電力系統整合（電力工人專用）
        self.power_manager = None  # 電力管理器引用
        self.worker_id = None  # 在電力系統中的工人 ID

        print(f"創建 NPC: {self.name} ({self.profession.value})")

    def _generate_name(self):
        """
        生成隨機的 NPC 姓名\n
        \n
        使用繁體中文常見姓氏和名字組合\n
        \n
        回傳:\n
        str: 生成的姓名\n
        """
        # 常見姓氏
        surnames = [
            "王",
            "李",
            "張",
            "劉",
            "陳",
            "楊",
            "趙",
            "黃",
            "周",
            "吳",
            "徐",
            "孫",
            "胡",
            "朱",
            "高",
            "林",
            "何",
            "郭",
            "馬",
            "羅",
            "梁",
            "宋",
            "鄭",
            "謝",
            "韓",
            "唐",
            "馮",
            "于",
            "董",
            "蕭",
        ]

        # 常見名字 (單字)
        given_names_male = [
            "偉",
            "明",
            "強",
            "軍",
            "峰",
            "勇",
            "波",
            "輝",
            "剛",
            "健",
            "華",
            "超",
            "建",
            "文",
            "亮",
            "志",
            "宇",
            "鵬",
            "瑞",
            "龍",
        ]

        given_names_female = [
            "麗",
            "娜",
            "靜",
            "敏",
            "雯",
            "蓉",
            "萍",
            "婷",
            "秀",
            "芳",
            "玲",
            "欣",
            "慧",
            "晶",
            "琪",
            "薇",
            "瑤",
            "嘉",
            "純",
            "美",
        ]

        # 隨機選擇性別
        is_male = random.choice([True, False])

        surname = random.choice(surnames)

        if is_male:
            # 男性名字可能是單字或雙字
            if random.random() < 0.3:  # 30% 機率是單字名
                given_name = random.choice(given_names_male)
            else:  # 70% 機率是雙字名
                given_name = random.choice(given_names_male) + random.choice(
                    given_names_male
                )
        else:
            # 女性名字生成邏輯類似
            if random.random() < 0.3:
                given_name = random.choice(given_names_female)
            else:
                given_name = random.choice(given_names_female) + random.choice(
                    given_names_female
                )

        return surname + given_name

    def _generate_dialogue(self):
        """
        根據職業生成對話內容\n
        \n
        回傳:\n
        list: 對話句子列表\n
        """
        # 基礎對話 - 所有 NPC 都可能說的話
        base_dialogues = [
            "你好！",
            "天氣真不錯呢。",
            "小鎮最近很熱鬧。",
            "希望你在這裡玩得開心！",
        ]

        # 職業專屬對話
        profession_dialogues = {
            Profession.FARMER: [
                "今年的收成很不錯！",
                "農田需要好好照顧。",
                "新鮮的蔬菜正在生長。",
            ],
            Profession.DOCTOR: [
                "保持健康很重要。",
                "如果身體不舒服記得來醫院。",
                "預防勝於治療。",
            ],
            Profession.PRIEST: [
                "願神保佑你。",
                "歡迎來教堂祈禱。",
                "內心的平靜最重要。",
            ],
            Profession.HUNTER: [
                "森林裡要小心野生動物。",
                "狩獵需要技巧和耐心。",
                "記住要保護保育類動物。",
            ],
            Profession.GUN_SHOP_WORKER: [
                "需要什麼武器嗎？",
                "安全使用武器很重要。",
                "我們有最好的狩獵裝備。",
            ],
        }

        # 合併基礎對話和職業對話
        dialogues = base_dialogues.copy()
        if self.profession in profession_dialogues:
            dialogues.extend(profession_dialogues[self.profession])

        return dialogues

    def update(self, dt, current_time_hour, current_day=1, is_workday=True):
        """
        更新 NPC 狀態和行為\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        current_time_hour (int): 當前遊戲時間 (小時制)\n
        current_day (int): 當前星期幾 (1-7，1是星期一)\n
        is_workday (bool): 是否為工作日 (星期六日為工作日，一到五為休息日)\n
        """
        self.current_hour = current_time_hour
        self.current_day = current_day
        self.is_workday = is_workday

        # 更新健康狀態
        self._update_health_status(dt)

        # 如果受傷住院，暫停其他行為
        if self.is_injured:
            self.state = NPCState.INJURED
            return

        # 根據時間表和星期決定當前應該做什麼
        self._update_daily_schedule()

        # 根據當前狀態執行對應行為
        self._execute_current_behavior(dt)

        # 更新位置 (移動)
        self._update_movement(dt)

    def _update_health_status(self, dt):
        """
        更新健康狀態\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        if self.is_injured:
            # 住院時間倒計時
            self.hospital_stay_time -= dt / 3600  # 轉換為小時

            if self.hospital_stay_time <= 0:
                # 康復出院
                self.is_injured = False
                self.hospital_stay_time = 0
                self.injury_cause = None
                self.state = NPCState.IDLE

                # 如果是電力工人，通知電力系統工人復工
                if (
                    self.profession == Profession.POWER_WORKER
                    and self.power_manager
                    and self.worker_id
                ):
                    self.power_manager.update_worker_status(self.worker_id, True)

                print(f"{self.name} 康復出院了")

    def _update_daily_schedule(self):
        """
        根據時間表和星期更新 NPC 的行為狀態\n
        \n
        包含工作日/休息日邏輯：\n
        - 工作日 (星期六、日)：按照職業時間表工作\n
        - 休息日 (星期一到五)：到處亂晃，不工作\n
        """
        if self.is_injured:
            return

        # 睡覺時間 (凌晨和深夜)
        if self.current_hour < 6 or self.current_hour >= 22:
            if self.state != NPCState.SLEEPING:
                self.state = NPCState.SLEEPING
                self._set_target_position(self.home_position)
            return

        # 休息日邏輯 (星期一到五)
        if not self.is_workday:
            # 休息日時 NPC 到處亂晃，不工作
            if self.state not in [NPCState.IDLE, NPCState.MOVING]:
                self.state = NPCState.IDLE
                # 設定一個隨機的閒逛目標
                self._set_random_wander_target()
            return

        # 工作日邏輯 (星期六、日)
        work_start = self.schedule.get("work_start", 9)
        work_end = self.schedule.get("work_end", 17)
        break_start = self.schedule.get("break_start")
        break_end = self.schedule.get("break_end")

        # 判斷當前應該處於什麼狀態
        if work_start <= self.current_hour < work_end:
            # 工作時間
            if break_start and break_start <= self.current_hour < break_end:
                # 休息時間
                if self.state != NPCState.RESTING:
                    self.state = NPCState.RESTING
            else:
                # 正常工作時間
                if self.state != NPCState.WORKING:
                    self.state = NPCState.WORKING
                    self._go_to_workplace()
        else:
            # 下班時間
            if self.state not in [NPCState.RESTING, NPCState.IDLE]:
                self.state = NPCState.RESTING
                self._set_target_position(self.home_position)

    def _execute_current_behavior(self, dt):
        """
        根據當前狀態執行對應的行為\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        if self.state == NPCState.WORKING:
            self._work_behavior(dt)
        elif self.state == NPCState.RESTING:
            self._rest_behavior(dt)
        elif self.state == NPCState.SLEEPING:
            self._sleep_behavior(dt)
        elif self.state == NPCState.MOVING:
            self._moving_behavior(dt)
        elif self.state == NPCState.IDLE:
            self._idle_behavior(dt)

    def _work_behavior(self, dt):
        """
        工作行為邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        # 確保在工作場所
        if self.workplace and not self._is_at_target():
            self.state = NPCState.MOVING
            return

        # 根據職業執行特定工作行為
        if self.profession == Profession.POWER_WORKER:
            self._power_worker_behavior(dt)
        elif self.profession == Profession.FARMER:
            self._farmer_behavior(dt)
        elif self.profession == Profession.HUNTER:
            self._hunter_behavior(dt)
        # 其他職業的工作行為可以在這裡添加

    def _power_worker_behavior(self, dt):
        """
        電力工人特殊行為 - 巡查負責區域\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        # 電力工人會在負責的區域中巡邏
        if self.assigned_area:
            # 在指定區域內隨機移動
            area_center = self.assigned_area
            patrol_radius = 50

            # 如果到達目標，設定新的巡邏點
            if self._is_at_target():
                new_x = area_center[0] + random.uniform(-patrol_radius, patrol_radius)
                new_y = area_center[1] + random.uniform(-patrol_radius, patrol_radius)
                self._set_target_position((new_x, new_y))

    def _farmer_behavior(self, dt):
        """
        農夫特殊行為 - 農田工作\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        # 農夫在農田中工作
        pass  # 暫時保留，等農田系統完成後實作

    def _hunter_behavior(self, dt):
        """
        獵人特殊行為 - 森林狩獵\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        # 獵人在森林中活動
        pass  # 暫時保留，等森林系統完成後實作

    def _rest_behavior(self, dt):
        """
        休息行為邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        # 休息時可能會在小鎮中隨意走動
        if random.random() < 0.01:  # 1% 機率改變休息地點
            self._wander_around()

    def _sleep_behavior(self, dt):
        """
        睡覺行為邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        # 睡覺時應該在家中，保持靜止
        if not self._is_near_position(self.home_position, 10):
            self._set_target_position(self.home_position)

    def _moving_behavior(self, dt):
        """
        移動行為邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        # 移動中的 NPC，到達目標後改變狀態
        if self._is_at_target():
            self.state = NPCState.IDLE

    def _idle_behavior(self, dt):
        """
        閒置行為邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        # 閒置時偶爾會隨機移動
        if random.random() < 0.005:  # 0.5% 機率開始隨機移動
            self._wander_around()

    def _update_movement(self, dt):
        """
        更新 NPC 移動\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        # 計算到目標的距離
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # 如果還沒到達目標
        if distance > 2:  # 允許2像素的誤差
            # 正規化方向向量
            if distance > 0:
                move_x = (dx / distance) * self.speed * dt * 60  # 60 用於幀率補償
                move_y = (dy / distance) * self.speed * dt * 60

                # 更新位置
                self.x += move_x
                self.y += move_y
        else:
            # 到達目標
            self.x = self.target_x
            self.y = self.target_y

    def _set_target_position(self, position):
        """
        設定移動目標位置\n
        \n
        參數:\n
        position (tuple): 目標位置 (x, y)\n
        """
        self.target_x, self.target_y = position
        if not self._is_at_target():
            self.state = NPCState.MOVING

    def _set_random_wander_target(self):
        """
        設定隨機閒逛目標 - 用於休息日時的亂晃行為\n
        \n
        在家附近隨機選擇一個點作為閒逛目標\n
        確保 NPC 在休息日有自然的移動模式\n
        """
        # 在家附近隨機選擇一個點作為閒逛目標
        wander_radius = 150  # 閒逛半徑

        # 從家的位置開始，在附近隨機選擇目標
        home_x, home_y = self.home_position

        # 使用極座標生成隨機點，確保分布均勻
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(20, wander_radius)  # 最少離家20像素

        target_x = home_x + radius * math.cos(angle)
        target_y = home_y + radius * math.sin(angle)

        # 確保目標在合理範圍內 (不超出地圖邊界)
        target_x = max(50, min(target_x, 950))  # 假設地圖寬度1000
        target_y = max(50, min(target_y, 650))  # 假設地圖高度700

        self._set_target_position((target_x, target_y))

    def _go_to_workplace(self):
        """
        前往工作場所\n
        """
        if self.workplace:
            self._set_target_position(self.workplace)

    def _wander_around(self):
        """
        隨機漫遊\n
        """
        # 在當前位置附近隨機選擇一個點
        wander_radius = 100
        new_x = self.x + random.uniform(-wander_radius, wander_radius)
        new_y = self.y + random.uniform(-wander_radius, wander_radius)

        # 確保不會移動到螢幕外
        new_x = max(50, min(1000, new_x))  # 假設螢幕寬度為1024
        new_y = max(50, min(700, new_y))  # 假設螢幕高度為768

        self._set_target_position((new_x, new_y))

    def _is_at_target(self):
        """
        檢查是否已到達目標位置\n
        \n
        回傳:\n
        bool: True 表示已到達目標\n
        """
        distance = math.sqrt(
            (self.x - self.target_x) ** 2 + (self.y - self.target_y) ** 2
        )
        return distance <= 5  # 5像素內算作到達

    def _is_near_position(self, position, threshold):
        """
        檢查是否靠近指定位置\n
        \n
        參數:\n
        position (tuple): 指定位置 (x, y)\n
        threshold (float): 距離閾值\n
        \n
        回傳:\n
        bool: True 表示在閾值範圍內\n
        """
        distance = math.sqrt((self.x - position[0]) ** 2 + (self.y - position[1]) ** 2)
        return distance <= threshold

    def injure(self, cause="未知原因"):
        """
        讓 NPC 受傷住院\n
        \n
        參數:\n
        cause (str): 受傷原因\n
        """
        if not self.is_injured:
            self.is_injured = True
            self.hospital_stay_time = 24  # 住院24小時
            self.injury_cause = cause
            self.state = NPCState.INJURED

            # 如果是電力工人，通知電力系統工人離線
            if (
                self.profession == Profession.POWER_WORKER
                and self.power_manager
                and self.worker_id
            ):
                self.power_manager.update_worker_status(self.worker_id, False)

            print(f"{self.name} 因為 {cause} 而受傷住院")

    def get_dialogue(self):
        """
        獲取隨機對話內容\n
        \n
        回傳:\n
        str: 對話內容\n
        """
        return random.choice(self.dialogue_lines)

    def set_workplace(self, workplace_position):
        """
        設定工作場所位置\n
        \n
        參數:\n
        workplace_position (tuple): 工作場所座標 (x, y)\n
        """
        self.workplace = workplace_position

    def set_home(self, home_position):
        """
        設定住所位置\n
        \n
        參數:\n
        home_position (tuple): 住所座標 (x, y)\n
        """
        self.home_position = home_position

    def assign_area(self, area_center):
        """
        為電力工人分配負責區域\n
        \n
        參數:\n
        area_center (tuple): 區域中心座標 (x, y)\n
        """
        if self.profession == Profession.POWER_WORKER:
            self.assigned_area = area_center
            print(f"電力工人 {self.name} 被分配到區域 {area_center}")

    def get_position(self):
        """
        獲取當前位置\n
        \n
        回傳:\n
        tuple: 當前座標 (x, y)\n
        """
        return (self.x, self.y)

    def get_rect(self):
        """
        獲取 NPC 的碰撞矩形\n
        \n
        回傳:\n
        pygame.Rect: 碰撞檢測用的矩形\n
        """
        return pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )

    def draw(self, screen):
        """
        繪製 NPC\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 根據狀態調整顯示
        if self.is_injured:
            # 受傷的 NPC 不在場景中顯示（在醫院）
            return

        # 繪製 NPC 本體
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), self.size, 2)

        # 根據狀態添加狀態指示器
        if self.state == NPCState.WORKING:
            # 工作中顯示小工具圖示
            pygame.draw.rect(
                screen,
                (255, 255, 0),
                (int(self.x) - 3, int(self.y) - self.size - 8, 6, 6),
            )
        elif self.state == NPCState.SLEEPING:
            # 睡覺中顯示 Z 符號效果
            pygame.draw.circle(
                screen, (200, 200, 200), (int(self.x), int(self.y)), self.size - 2
            )

    def draw_info(self, screen, font):
        """
        繪製 NPC 資訊 (姓名等)\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體物件\n
        """
        if self.is_injured:
            return

        # 繪製姓名
        name_surface = font.render(self.name, True, (0, 0, 0))
        name_rect = name_surface.get_rect(
            center=(int(self.x), int(self.y) - self.size - 15)
        )
        screen.blit(name_surface, name_rect)

        # 繪製職業 (小字)
        profession_surface = font.render(self.profession.value, True, (100, 100, 100))
        profession_rect = profession_surface.get_rect(
            center=(int(self.x), int(self.y) - self.size - 30)
        )
        screen.blit(profession_surface, profession_rect)

    def __str__(self):
        """
        NPC 的字串表示\n
        \n
        回傳:\n
        str: NPC 描述\n
        """
        status = "住院中" if self.is_injured else self.state.value
        return f"{self.name} ({self.profession.value}) - {status}"
