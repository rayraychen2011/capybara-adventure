######################載入套件######################
import random
import math
from src.systems.npc.profession import Profession, ProfessionData
from config.settings import *


######################NPC 工作行為模組######################
class NPCWorkBehavior:
    """
    NPC 工作行為管理器 - 處理所有工作相關的邏輯\n
    \n
    負責：\n
    1. 工作時間管理\n
    2. 工作場所導航\n
    3. 工作任務執行\n
    4. 休息時間管理\n
    5. 特殊工作行為（如電力工人）\n
    """

    def __init__(self, npc):
        """
        初始化工作行為\n
        \n
        參數:\n
        npc: NPC 實例引用\n
        """
        self.npc = npc
        
        # 工作狀態
        self.is_at_workplace = False
        self.work_efficiency = random.uniform(0.7, 1.0)  # 工作效率
        self.work_stamina = 100  # 工作體力
        self.max_work_stamina = 100
        
        # 工作場所相關
        self.workplace_position = None
        self.workplace_arrival_distance = 30  # 認為到達工作場所的距離
        self.work_area_radius = 50  # 工作區域半徑
        
        # 工作任務
        self.current_work_task = None
        self.work_task_progress = 0
        self.work_tasks = self._generate_work_tasks()
        
        # 休息管理
        self.break_timer = 0
        self.break_interval = random.uniform(120, 180)  # 休息間隔（秒）
        self.break_duration = 30  # 休息時長（秒）
        self.is_on_break = False
        
        # 工作統計
        self.total_work_time = 0
        self.tasks_completed_today = 0
        self.productivity_score = 0
        
        print(f"NPC {npc.name} 工作行為初始化完成 - 職業: {npc.profession.value}")

    def update(self, dt, time_manager):
        """
        更新工作行為\n
        \n
        參數:\n
        dt (float): 時間差\n
        time_manager (TimeManager): 時間管理器\n
        """
        if not time_manager:
            return
        
        # 檢查是否應該工作
        should_work = time_manager.is_work_time()
        
        if should_work:
            self._update_work_behavior(dt, time_manager)
        else:
            self._update_off_work_behavior(dt)
        
        # 更新工作統計
        self._update_work_statistics(dt, should_work)

    def _update_work_behavior(self, dt, time_manager):
        """
        更新工作時間的行為\n
        \n
        參數:\n
        dt (float): 時間差\n
        time_manager (TimeManager): 時間管理器\n
        """
        # 檢查是否在工作場所
        if not self.is_at_workplace:
            self._go_to_workplace()
            return
        
        # 管理休息時間
        self._manage_break_time(dt)
        
        if self.is_on_break:
            return
        
        # 執行工作任務
        self._execute_work_tasks(dt)
        
        # 特殊職業的專門工作
        self._handle_profession_specific_work(dt, time_manager)

    def _update_off_work_behavior(self, dt):
        """
        更新下班時間的行為\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        self.is_at_workplace = False
        self.is_on_break = False
        
        # 重置工作狀態
        if self.current_work_task:
            self.current_work_task = None
            self.work_task_progress = 0

    def _go_to_workplace(self):
        """
        前往工作場所\n
        """
        if not self.workplace_position:
            # 如果沒有指定工作場所，設定一個預設位置
            self._find_workplace_position()
        
        if self.workplace_position:
            # 檢查是否已經在工作場所附近
            distance = math.sqrt(
                (self.npc.x - self.workplace_position[0]) ** 2 +
                (self.npc.y - self.workplace_position[1]) ** 2
            )
            
            if distance <= self.workplace_arrival_distance:
                self.is_at_workplace = True
                print(f"{self.npc.name} 到達工作場所")
            else:
                # 設定移動目標到工作場所
                self.npc.movement_behavior.set_target(self.workplace_position)

    def _find_workplace_position(self):
        """
        尋找工作場所位置\n
        """
        # 根據職業類型尋找合適的工作場所
        profession_workplaces = {
            Profession.FARMER: self._find_farm_workplace(),
            Profession.DOCTOR: self._find_hospital_workplace(),
            Profession.NURSE: self._find_hospital_workplace(),
            Profession.GUN_SHOP_STAFF: self._find_gun_shop_workplace(),
            Profession.VENDOR: self._find_vendor_workplace(),
            Profession.FISHING_SHOP_STAFF: self._find_fishing_shop_workplace(),
            Profession.CONVENIENCE_STAFF: self._find_convenience_store_workplace(),
            Profession.POWER_WORKER: self._find_power_workplace(),
            Profession.HUNTER: self._find_hunting_area()
        }
        
        workplace_finder = profession_workplaces.get(self.npc.profession)
        if workplace_finder:
            self.workplace_position = workplace_finder()
        else:
            # 預設工作場所（家附近）
            self.workplace_position = self.npc.home_position

    def _find_farm_workplace(self):
        """
        尋找農田工作場所\n
        """
        # 農田通常在小鎮外圍
        base_x, base_y = 100, 100  # 假設農田起始位置
        return (base_x + random.randint(-50, 50), base_y + random.randint(-50, 50))

    def _find_hospital_workplace(self):
        """
        尋找醫院工作場所\n
        """
        # 從建築物中尋找醫院
        if hasattr(self.npc, 'buildings') and self.npc.buildings:
            hospitals = [b for b in self.npc.buildings if b.get("type") == "hospital"]
            if hospitals:
                hospital = random.choice(hospitals)
                return (hospital["x"] + hospital["width"]//2, hospital["y"] + hospital["height"]//2)
        
        # 預設醫院位置
        return (TOWN_TOTAL_WIDTH // 3, TOWN_TOTAL_HEIGHT // 3)

    def _find_gun_shop_workplace(self):
        """
        尋找槍械店工作場所\n
        """
        if hasattr(self.npc, 'buildings') and self.npc.buildings:
            gun_shops = [b for b in self.npc.buildings if b.get("type") == "gun_shop"]
            if gun_shops:
                shop = random.choice(gun_shops)
                return (shop["x"] + shop["width"]//2, shop["y"] + shop["height"]//2)
        
        return (TOWN_TOTAL_WIDTH // 2, TOWN_TOTAL_HEIGHT // 4)

    def _find_vendor_workplace(self):
        """
        尋找小販工作場所\n
        """
        # 小販在街道上工作
        return (
            random.randint(100, TOWN_TOTAL_WIDTH - 100),
            random.randint(100, TOWN_TOTAL_HEIGHT - 100)
        )

    def _find_fishing_shop_workplace(self):
        """
        尋找釣魚店工作場所\n
        """
        if hasattr(self.npc, 'buildings') and self.npc.buildings:
            fishing_shops = [b for b in self.npc.buildings if b.get("type") == "fishing_shop"]
            if fishing_shops:
                shop = random.choice(fishing_shops)
                return (shop["x"] + shop["width"]//2, shop["y"] + shop["height"]//2)
        
        return (TOWN_TOTAL_WIDTH * 3 // 4, TOWN_TOTAL_HEIGHT // 2)

    def _find_convenience_store_workplace(self):
        """
        尋找便利商店工作場所\n
        """
        if hasattr(self.npc, 'buildings') and self.npc.buildings:
            stores = [b for b in self.npc.buildings if b.get("type") == "convenience_store"]
            if stores:
                store = random.choice(stores)
                return (store["x"] + store["width"]//2, store["y"] + store["height"]//2)
        
        return (TOWN_TOTAL_WIDTH // 2, TOWN_TOTAL_HEIGHT // 2)

    def _find_power_workplace(self):
        """
        尋找電力工作場所\n
        """
        # 電力工人在指定區域工作
        if hasattr(self.npc, 'assigned_area') and self.npc.assigned_area is not None:
            # 根據分配的區域確定工作位置
            area_id = self.npc.assigned_area
            areas_per_row = 6  # 假設每行6個區域
            area_row = area_id // areas_per_row
            area_col = area_id % areas_per_row
            
            area_width = TOWN_TOTAL_WIDTH // areas_per_row
            area_height = TOWN_TOTAL_HEIGHT // 5  # 假設5行
            
            area_center_x = area_col * area_width + area_width // 2
            area_center_y = area_row * area_height + area_height // 2
            
            return (area_center_x, area_center_y)
        
        # 預設電力場位置
        return (TOWN_TOTAL_WIDTH // 2, TOWN_TOTAL_HEIGHT // 6)

    def _find_hunting_area(self):
        """
        尋找狩獵區域\n
        """
        # 獵人在森林區域工作
        return (TOWN_TOTAL_WIDTH + 100, TOWN_TOTAL_HEIGHT + 100)

    def _manage_break_time(self, dt):
        """
        管理休息時間\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        if self.is_on_break:
            self.break_timer -= dt
            if self.break_timer <= 0:
                self.is_on_break = False
                self.work_stamina = min(self.max_work_stamina, self.work_stamina + 30)
                print(f"{self.npc.name} 休息結束，回到工作")
        else:
            self.break_timer += dt
            if self.break_timer >= self.break_interval and self.work_stamina < 30:
                self.is_on_break = True
                self.break_timer = self.break_duration
                print(f"{self.npc.name} 開始休息")

    def _execute_work_tasks(self, dt):
        """
        執行工作任務\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        if not self.current_work_task:
            self._start_new_work_task()
        
        if self.current_work_task:
            # 執行當前任務
            task_progress_rate = self.work_efficiency * (self.work_stamina / self.max_work_stamina)
            self.work_task_progress += task_progress_rate * dt * 10  # 進度速率調整
            
            # 消耗體力
            self.work_stamina = max(0, self.work_stamina - dt * 2)
            
            # 檢查任務是否完成
            if self.work_task_progress >= 100:
                self._complete_work_task()

    def _start_new_work_task(self):
        """
        開始新的工作任務\n
        """
        if self.work_tasks:
            self.current_work_task = random.choice(self.work_tasks)
            self.work_task_progress = 0
            print(f"{self.npc.name} 開始工作任務: {self.current_work_task}")

    def _complete_work_task(self):
        """
        完成工作任務\n
        """
        if self.current_work_task:
            self.tasks_completed_today += 1
            self.productivity_score += self.work_efficiency
            print(f"{self.npc.name} 完成工作任務: {self.current_work_task}")
            
            self.current_work_task = None
            self.work_task_progress = 0

    def _generate_work_tasks(self):
        """
        根據職業生成工作任務列表\n
        \n
        回傳:\n
        list: 工作任務列表\n
        """
        profession_tasks = {
            Profession.FARMER: ["澆水", "施肥", "除草", "收穫", "整理農具"],
            Profession.DOCTOR: ["診斷病人", "開處方", "檢查報告", "手術準備", "病歷記錄"],
            Profession.NURSE: ["照顧病人", "測量體溫", "發藥", "協助醫生", "整理病房"],
            Profession.GUN_SHOP_STAFF: ["整理武器", "清潔槍械", "接待顧客", "檢查庫存", "安全檢查"],
            Profession.VENDOR: ["準備商品", "接待顧客", "收款", "整理攤位", "補充貨品"],
            Profession.FISHING_SHOP_STAFF: ["整理釣具", "接待顧客", "修理設備", "檢查庫存", "清潔店面"],
            Profession.CONVENIENCE_STAFF: ["整理貨架", "收銀", "補充商品", "清潔店面", "檢查庫存"],
            Profession.POWER_WORKER: ["檢查電線", "維護設備", "修理故障", "巡視區域", "記錄數據"],
            Profession.HUNTER: ["巡邏森林", "設置陷阱", "追蹤動物", "維護裝備", "記錄觀察"]
        }
        
        return profession_tasks.get(self.npc.profession, ["一般工作"])

    def _handle_profession_specific_work(self, dt, time_manager):
        """
        處理特定職業的專門工作\n
        \n
        參數:\n
        dt (float): 時間差\n
        time_manager (TimeManager): 時間管理器\n
        """
        if self.npc.profession == Profession.POWER_WORKER:
            self._handle_power_worker_duties(dt)
        elif self.npc.profession == Profession.DOCTOR or self.npc.profession == Profession.NURSE:
            self._handle_medical_duties(dt)
        elif self.npc.profession == Profession.FARMER:
            self._handle_farming_duties(dt, time_manager)

    def _handle_power_worker_duties(self, dt):
        """
        處理電力工人的特殊職責\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        # 電力工人需要巡視分配的區域
        if hasattr(self.npc, 'power_manager') and self.npc.power_manager:
            # 檢查是否有電力故障需要處理
            if hasattr(self.npc, 'worker_id'):
                district_id = self.npc.assigned_area
                if district_id is not None:
                    # 這裡可以添加電力系統的互動邏輯
                    pass

    def _handle_medical_duties(self, dt):
        """
        處理醫療人員的特殊職責\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        # 醫療人員需要照顧傷患
        # 這裡可以添加傷患治療的邏輯
        pass

    def _handle_farming_duties(self, dt, time_manager):
        """
        處理農夫的特殊職責\n
        \n
        參數:\n
        dt (float): 時間差\n
        time_manager (TimeManager): 時間管理器\n
        """
        # 農夫的工作受天氣和季節影響
        # 這裡可以添加季節性農務的邏輯
        pass

    def _update_work_statistics(self, dt, is_working):
        """
        更新工作統計\n
        \n
        參數:\n
        dt (float): 時間差\n
        is_working (bool): 是否在工作時間\n
        """
        if is_working and self.is_at_workplace and not self.is_on_break:
            self.total_work_time += dt

    def set_workplace(self, position):
        """
        設定工作場所位置\n
        \n
        參數:\n
        position (tuple): 工作場所位置 (x, y)\n
        """
        self.workplace_position = position

    def get_work_info(self):
        """
        獲取工作狀態資訊\n
        \n
        回傳:\n
        dict: 工作狀態資訊\n
        """
        return {
            "is_at_workplace": self.is_at_workplace,
            "workplace_position": self.workplace_position,
            "current_task": self.current_work_task,
            "task_progress": round(self.work_task_progress, 1),
            "work_stamina": round(self.work_stamina, 1),
            "is_on_break": self.is_on_break,
            "tasks_completed": self.tasks_completed_today,
            "productivity_score": round(self.productivity_score, 2),
            "total_work_time": round(self.total_work_time, 1)
        }