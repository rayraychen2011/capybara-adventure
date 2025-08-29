######################載入套件######################
import pygame
import random
import math
from enum import Enum
from src.systems.npc.profession import Profession, ProfessionData
from config.settings import NPC_SPEED, NPC_COMMUTE_DISTANCE_THRESHOLD


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
        self.speed = NPC_SPEED  # 使用與玩家相同的移動速度
        
        # 載具系統
        self.has_vehicle = random.choice([True, False])  # 隨機決定是否擁有載具
        self.in_vehicle = False  # 是否正在使用載具
        self.commute_distance_threshold = NPC_COMMUTE_DISTANCE_THRESHOLD  # 使用載具的距離閾值
        self.vehicle_type = "car" if self.has_vehicle else None  # 載具類型
        self.can_use_train = True  # 可以使用火車通勤
        self.terrain_system = None  # 地形系統引用，用於火車站查找

        # 工作和住所
        self.workplace = None
        self.home_position = initial_position
        self.current_work_area = None  # 電力工人需要負責的區域

        # 農夫工作相關屬性
        self.is_farmer = False  # 是否為農夫
        self.work_phase = None  # 工作階段
        self.can_teleport = False  # 是否可以傳送
        self.is_working_farmer = False  # 是否為工作農夫

        # 生活時間表
        self.schedule = ProfessionData.get_profession_schedule(profession)
        self.current_hour = 8  # 初始時間設為早上8點
        self.current_day = 1  # 當前星期幾
        self.is_workday = True  # 是否為工作日

        # 健康狀態
        self.is_injured = False
        self.hospital_stay_time = 0  # 住院剩餘時間 (小時)
        self.injury_cause = None

        # 外觀屬性
        self.color = ProfessionData.get_profession_color(profession)
        self.size = 3  # NPC 顯示大小（縮小以配合玩家尺寸）

        # 對話系統（性格系統會重新生成這些對話）
        self.dialogue_lines = ["你好。"]  # 預設對話，等待性格系統更新
        self.last_interaction_time = 0
        
        # 性格系統相關屬性
        self.personality_type = None  # 性格類型，由性格系統設定
        self.personality_profile = None  # 完整的性格檔案

        # 特殊屬性
        self.assigned_area = None  # 電力工人的負責區域
        self.shop_id = None  # 商店員工的工作店鋪 ID
        self.is_interacting_with_building = False  # 是否正在與建築物互動

        # 電力系統整合（電力工人專用）
        self.power_manager = None  # 電力管理器引用
        self.worker_id = None  # 在電力系統中的工人 ID

        # 道路系統整合（路徑規劃用）
        self.road_system = None  # 道路系統引用，用於智能路徑規劃
        self.tile_map = None     # 格子地圖引用，用於路徑限制
        self.current_path = []  # 當前規劃的路徑點列表
        self.path_index = 0  # 當前路徑點索引

        print(f"創建 NPC: {self.name} ({self.profession.value})")

    def _generate_name(self):
        """
        生成隨機的 NPC 姓名（暫時用，實際姓名由性格系統分配）\n
        \n
        回傳:\n
        str: 臨時姓名\n
        """
        # 這個方法將被性格系統覆蓋，只是提供臨時名稱
        return f"居民{self.id}"

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

    def simple_update(self, dt, current_time_hour, is_workday=True):
        """
        簡化的 NPC 更新 - 用於中距離 NPC\n
        \n
        只更新必要的狀態，跳過複雜的移動計算\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        current_time_hour (int): 當前小時\n
        is_workday (bool): 是否為工作日\n
        """
        if self.is_injured:
            return

        # 只更新工作狀態，不計算移動
        if is_workday and 9 <= current_time_hour <= 17:
            self.current_state = NPCState.WORKING
        else:
            self.current_state = NPCState.RESTING

    def minimal_update(self, current_time_hour, is_workday=True):
        """
        最簡化的 NPC 更新 - 用於遠距離 NPC\n
        \n
        只更新最基本的狀態，幾乎不消耗效能\n
        \n
        參數:\n
        current_time_hour (int): 當前小時\n
        is_workday (bool): 是否為工作日\n
        """
        if self.is_injured:
            return

        # 只更新狀態，不做任何移動或複雜計算
        if is_workday and 9 <= current_time_hour <= 17:
            self.current_state = NPCState.WORKING
        else:
            self.current_state = NPCState.RESTING

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
                self.go_home()  # 使用載具感知回家
            return

        # 休息日邏輯 (星期一到五)
        if not self.is_workday:
            # 休息日時 NPC 只在住宅區附近活動
            if self.state not in [NPCState.IDLE, NPCState.MOVING]:
                self.state = NPCState.IDLE
                # 設定一個在住宅區附近的閒逛目標
                self._set_residential_wander_target()
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
                self.go_home()  # 使用載具感知回家

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

        # 檢查是否正在與工作場所建築物互動
        self._check_building_interaction()

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
        更新 NPC 移動，使用路徑點系統\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        """
        # 如果沒有路徑，直接返回
        if not hasattr(self, "current_path") or not self.current_path:
            return

        # 檢查當前路徑點是否有效
        if self.path_index >= len(self.current_path):
            return

        # 獲取當前目標路徑點
        current_waypoint = self.current_path[self.path_index]
        self.target_x, self.target_y = current_waypoint

        # 記錄移動前的位置，用於碰撞檢測
        prev_x = self.x
        prev_y = self.y

        # 計算到當前路徑點的距離
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # 如果還沒到達當前路徑點
        if distance > 5:  # 允許5像素的誤差
            # 正規化方向向量
            if distance > 0:
                # 根據是否使用載具調整移動速度
                current_speed = self.speed
                if self.in_vehicle:
                    from config.settings import VEHICLE_SPEED
                    current_speed = VEHICLE_SPEED
                
                move_x = (dx / distance) * current_speed * dt * 60  # 60 用於幀率補償
                move_y = (dy / distance) * current_speed * dt * 60

                # 更新位置
                self.x += move_x
                self.y += move_y

                # 檢查碰撞並修正位置
                if self._check_collision_with_environment():
                    # 如果發生碰撞，回到上一個位置
                    self.x = prev_x
                    self.y = prev_y

                    # 嘗試只在 X 方向移動
                    self.x += move_x
                    if self._check_collision_with_environment():
                        self.x = prev_x  # X 方向也有碰撞，恢復 X

                        # 嘗試只在 Y 方向移動
                        self.y += move_y
                        if self._check_collision_with_environment():
                            self.y = prev_y  # Y 方向也有碰撞，完全恢復
                            # 設定新的目標，避免卡住
                            self._find_alternative_target()
        else:
            # 到達當前路徑點，移動到下一個
            self.x = self.target_x
            self.y = self.target_y
            self.path_index += 1

            # 如果已經完成所有路徑點，停止移動
            if self.path_index >= len(self.current_path):
                self.current_path = []
                self.path_index = 0

    def _check_collision_with_environment(self):
        """
        檢查 NPC 是否與環境物件（建築物、水域、鐵軌、草地）發生碰撞\n
        根據新需求：NPC 只能從斑馬線處通過鐵軌，且永遠不會到湖泊地形和草地\n
        但農夫可以在農地上移動\n
        \n
        回傳:\n
        bool: True 表示發生碰撞，False 表示沒有碰撞\n
        """
        # 建立 NPC 的碰撞矩形
        npc_rect = pygame.Rect(
            self.x - self.size, self.y - self.size, self.size * 2, self.size * 2
        )

        # 檢查地形類型，避開湖泊（地形代碼2）和草地（地形代碼0）
        if hasattr(self, "terrain_system") and self.terrain_system:
            terrain_type = self.terrain_system.get_terrain_at_position(self.x, self.y)
            if terrain_type == 2:  # 湖泊地形
                return True  # 避開湖泊
            if terrain_type == 0:  # 草地地形 - 所有NPC都不能在草地上
                return True  # 避開草地
            
            # 檢查農地地形（地形代碼8）- 只有農夫可以進入
            if terrain_type == 8:  # 農地地形
                # 檢查是否為農夫
                try:
                    from src.systems.npc.profession import Profession
                    if hasattr(self, 'profession') and self.profession == Profession.FARMER:
                        # 農夫可以在農地上移動，不產生碰撞
                        pass
                    else:
                        # 非農夫NPC不能在農地上
                        return True
                except ImportError:
                    # 如果無法導入職業枚舉，非農夫NPC不能在農地上
                    return True
                
            # 檢查水域碰撞（NPC 不能進入水體）
            if self.terrain_system.check_water_collision(self.x, self.y):
                return True
            
            # 檢查鐵軌碰撞（新增）- NPC 只能從有斑馬線的地方通過
            if hasattr(self.terrain_system, 'railway_system'):
                if self.terrain_system.railway_system.check_railway_collision_for_npc(npc_rect):
                    return True

        # 檢查建築物碰撞
        if hasattr(self, "buildings") and self.buildings:
            for building in self.buildings:
                if npc_rect.colliderect(building.rect):
                    return True

        return False

    def set_terrain_system_reference(self, terrain_system):
        """
        設定地形系統參考，用於碰撞檢測\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統實例\n
        """
        self.terrain_system = terrain_system

    def _find_alternative_target(self):
        """
        當原目標無法到達時，尋找替代目標\n
        \n
        在目前位置附近隨機選擇一個新的目標點\n
        確保 NPC 不會卡在同一個位置\n
        """
        # 在當前位置附近尋找新目標
        attempts = 0
        max_attempts = 10

        while attempts < max_attempts:
            # 在較小範圍內隨機選擇新目標
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(30, 80)  # 較小的移動距離

            new_target_x = self.x + distance * math.cos(angle)
            new_target_y = self.y + distance * math.sin(angle)

            # 簡單檢查新目標是否可行（不在建築物內）
            temp_x, temp_y = self.x, self.y
            self.x, self.y = new_target_x, new_target_y

            if not self._check_collision_with_environment():
                # 新目標可行，設定為新目標
                self.target_x = new_target_x
                self.target_y = new_target_y
                self.x, self.y = temp_x, temp_y  # 恢復原位置
                return

            self.x, self.y = temp_x, temp_y  # 恢復原位置
            attempts += 1

        # 如果找不到替代目標，停在原地
        self.target_x = self.x
        self.target_y = self.y

    def _should_use_vehicle(self, destination_x, destination_y):
        """
        判斷是否應該使用載具前往目的地\n
        \n
        參數:\n
        destination_x (float): 目的地 X 座標\n
        destination_y (float): 目的地 Y 座標\n
        \n
        回傳:\n
        bool: True 表示應該使用載具\n
        """
        if not self.has_vehicle:
            return False
        
        # 計算到目的地的距離
        distance = math.sqrt((destination_x - self.x)**2 + (destination_y - self.y)**2)
        
        # 如果距離超過閾值，使用載具
        return distance > self.commute_distance_threshold

    def start_vehicle_use(self):
        """
        開始使用載具\n
        """
        if self.has_vehicle and not self.in_vehicle:
            self.in_vehicle = True
            print(f"NPC {self.name} 開始使用載具")

    def stop_vehicle_use(self):
        """
        停止使用載具\n
        """
        if self.in_vehicle:
            self.in_vehicle = False
            print(f"NPC {self.name} 停止使用載具")

    def move_to_location(self, destination_x, destination_y):
        """
        移動到指定位置，自動決定是否使用載具\n
        \n
        參數:\n
        destination_x (float): 目的地 X 座標\n
        destination_y (float): 目的地 Y 座標\n
        """
        # 根據距離決定是否使用載具
        if self._should_use_vehicle(destination_x, destination_y):
            self.start_vehicle_use()
        else:
            self.stop_vehicle_use()
        
        # 設定目標位置
        self.target_x = destination_x
        self.target_y = destination_y
        self.state = NPCState.MOVING

    def go_to_work(self):
        """
        前往工作場所 - 根據距離決定交通方式\n
        """
        if not self.workplace:
            return
        
        work_x, work_y = self.workplace
        
        # 計算到工作場所的距離
        distance = math.sqrt((work_x - self.x)**2 + (work_y - self.y)**2)
        
        # 如果距離很遠，考慮使用火車
        if distance > self.commute_distance_threshold * 2 and self.can_use_train:
            if self._try_train_commute(work_x, work_y):
                print(f"NPC {self.name} 搭乘火車前往工作場所")
                return
        
        # 否則使用正常移動
        self.move_to_location(work_x, work_y)
        # 大幅減少NPC工作輸出：每200次行動才輸出一次
        if not hasattr(self, '_work_debug_counter'):
            self._work_debug_counter = 0
        self._work_debug_counter += 1
        if self._work_debug_counter % 200 == 0:
            print(f"NPC {self.name} 前往工作場所 (第{self._work_debug_counter}次)")

    def _try_train_commute(self, dest_x, dest_y):
        """
        嘗試使用火車通勤\n
        \n
        參數:\n
        dest_x (float): 目的地 X 座標\n
        dest_y (float): 目的地 Y 座標\n
        \n
        回傳:\n
        bool: 是否成功使用火車通勤\n
        """
        # 檢查是否為農夫且不允許傳送
        if hasattr(self, 'is_farmer') and self.is_farmer and not getattr(self, 'can_teleport', True):
            return False  # 農夫在工作時間不能使用火車傳送
        
        if not self.terrain_system or not hasattr(self.terrain_system, 'railway_system'):
            return False
        
        railway_system = self.terrain_system.railway_system
        
        # 找最近的火車站
        nearest_station = self._find_nearest_train_station()
        if not nearest_station:
            return False
        
        # 找目的地附近的火車站
        dest_station = self._find_nearest_station_to_destination(dest_x, dest_y)
        if not dest_station or dest_station == nearest_station:
            return False
        
        # 移動到目的地火車站附近
        self.x = dest_station.x + dest_station.width // 2
        self.y = dest_station.y + dest_station.height + 10
        
        return True

    def _find_nearest_train_station(self):
        """
        找到最近的火車站\n
        \n
        回傳:\n
        TrainStation: 最近的火車站，如果沒有則返回 None\n
        """
        if not self.terrain_system or not hasattr(self.terrain_system, 'railway_system'):
            return None
        
        stations = self.terrain_system.railway_system.train_stations
        if not stations:
            return None
        
        nearest_station = None
        nearest_distance = float('inf')
        
        for station in stations:
            distance = math.sqrt((self.x - station.x)**2 + (self.y - station.y)**2)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_station = station
        
        return nearest_station

    def _find_nearest_station_to_destination(self, dest_x, dest_y):
        """
        找到目的地附近最近的火車站\n
        \n
        參數:\n
        dest_x (float): 目的地 X 座標\n
        dest_y (float): 目的地 Y 座標\n
        \n
        回傳:\n
        TrainStation: 最近的火車站，如果沒有則返回 None\n
        """
        if not self.terrain_system or not hasattr(self.terrain_system, 'railway_system'):
            return None
        
        stations = self.terrain_system.railway_system.train_stations
        if not stations:
            return None
        
        nearest_station = None
        nearest_distance = float('inf')
        
        for station in stations:
            distance = math.sqrt((dest_x - station.x)**2 + (dest_y - station.y)**2)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_station = station
        
        return nearest_station

    def go_home(self):
        """
        回家\n
        """
        home_x, home_y = self.home_position
        self.move_to_location(home_x, home_y)
        print(f"NPC {self.name} 回家")

    def set_buildings_reference(self, buildings):
        """
        設定建築物參考，用於碰撞檢測\n
        \n
        參數:\n
        buildings (list): 建築物列表\n
        """
        self.buildings = buildings

    def _check_building_interaction(self):
        """
        檢查 NPC 是否正在與建築物互動\n
        \n
        當 NPC 與工作場所或其他可互動建築物重疊時\n
        設定為互動狀態，這會讓 NPC 隱藏起來\n
        """
        if not hasattr(self, "buildings") or not self.buildings:
            self.is_interacting_with_building = False
            return

        # 建立 NPC 的碰撞矩形
        npc_rect = pygame.Rect(self.x - 10, self.y - 10, 20, 20)

        # 檢查與所有建築物的重疊
        for building in self.buildings:
            if npc_rect.colliderect(building.rect):
                # NPC 與建築物重疊，表示正在互動
                self.is_interacting_with_building = True
                return

        # 沒有與任何建築物重疊
        self.is_interacting_with_building = False

    def _set_target_position(self, position):
        """
        設定移動目標位置，使用格子地圖的智能路徑規劃\n
        \n
        參數:\n
        position (tuple): 目標位置 (x, y)\n
        """
        self.target_x, self.target_y = position

        # 優先使用格子地圖進行路徑規劃（限制在人行道和斑馬線）
        if hasattr(self, "tile_map") and self.tile_map:
            self._plan_path_using_tile_map(position)
        elif hasattr(self, "road_system") and self.road_system:
            # 備用：使用道路系統
            self._plan_path_using_roads(position)
        else:
            # 最後備用：直線移動
            self.current_path = [position]
            self.path_index = 0

        if not self._is_at_target():
            self.state = NPCState.MOVING

    def _plan_path_using_tile_map(self, target_position):
        """
        使用格子地圖系統規劃路徑，限制只能在人行道和斑馬線上移動\n
        \n
        參數:\n
        target_position (tuple): 目標位置 (x, y)\n
        """
        try:
            current_pos = (self.x, self.y)
            
            # 使用格子地圖的路徑搜尋功能
            path_points = self.tile_map.find_path_for_npc(current_pos, target_position)
            
            if path_points:
                self.current_path = path_points
                self.path_index = 0
            else:
                # 如果找不到路徑，嘗試移動到最近的可行走位置
                self._find_nearest_walkable_position(target_position)
        
        except Exception as e:
            print(f"格子地圖路徑規劃失敗: {e}")
            # 失敗時嘗試使用道路系統或直線移動
            if hasattr(self, "road_system") and self.road_system:
                self._plan_path_using_roads(target_position)
            else:
                self.current_path = [target_position]
                self.path_index = 0

    def _find_nearest_walkable_position(self, target_position):
        """
        尋找最近的可行走位置作為目標\n
        
        當目標位置不可行走時使用\n
        
        參數:\n
        target_position (tuple): 原始目標位置\n
        """
        if not hasattr(self, "tile_map") or not self.tile_map:
            self.current_path = [target_position]
            self.path_index = 0
            return
        
        # 在目標位置附近尋找可行走的格子
        target_x, target_y = target_position
        
        for radius in range(1, 10):  # 搜索半徑從1到9格
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) == radius or abs(dy) == radius:  # 只檢查邊界
                        check_x = target_x + dx * self.tile_map.tile_size
                        check_y = target_y + dy * self.tile_map.tile_size
                        
                        if self.tile_map.is_position_walkable(check_x, check_y):
                            # 找到可行走位置，規劃到此位置的路徑
                            path_points = self.tile_map.find_path_for_npc(
                                (self.x, self.y), (check_x, check_y)
                            )
                            if path_points:
                                self.current_path = path_points
                                self.path_index = 0
                                return
        
        # 如果找不到可行走位置，保持原地
        self.current_path = []
        self.path_index = 0

    def _plan_path_using_roads(self, target_position):
        """
        使用道路系統規劃路徑\n
        \n
        參數:\n
        target_position (tuple): 目標位置 (x, y)\n
        """
        try:
            # 尋找當前位置和目標位置最近的道路點
            current_pos = (self.x, self.y)
            current_road = self.road_system.get_nearest_road(current_pos)
            target_road = self.road_system.get_nearest_road(target_position)

            if current_road and target_road:
                # 如果當前位置和目標都在道路附近，規劃沿道路的路徑
                self._create_road_based_path(
                    current_pos, target_position, current_road, target_road
                )
            else:
                # 如果沒有找到適合的道路，使用直線路徑
                self.current_path = [target_position]
                self.path_index = 0

        except Exception as e:
            # 路徑規劃失敗時使用直線移動
            print(f"路徑規劃失敗: {e}")
            self.current_path = [target_position]
            self.path_index = 0

    def _create_road_based_path(self, start_pos, target_pos, start_road, target_road):
        """
        創建基於道路的移動路徑\n
        \n
        參數:\n
        start_pos (tuple): 起始位置\n
        target_pos (tuple): 目標位置\n
        start_road (RoadSegment): 起始道路\n
        target_road (RoadSegment): 目標道路\n
        """
        path_points = []

        # 添加到最近道路的中點
        start_road_center = (
            (start_road.start_pos[0] + start_road.end_pos[0]) / 2,
            (start_road.start_pos[1] + start_road.end_pos[1]) / 2,
        )

        # 如果不是同一條道路，添加中間路徑點
        if start_road != target_road:
            target_road_center = (
                (target_road.start_pos[0] + target_road.end_pos[0]) / 2,
                (target_road.start_pos[1] + target_road.end_pos[1]) / 2,
            )

            # 簡單的路徑：當前位置 -> 起始道路中點 -> 目標道路中點 -> 目標位置
            path_points = [start_road_center, target_road_center, target_pos]
        else:
            # 同一條道路，直接前往目標
            path_points = [target_pos]

        self.current_path = path_points
        self.path_index = 0

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
        前往工作場所 - 自動決定是否使用載具\n
        """
        if self.workplace:
            # 使用新的移動方法，自動處理載具
            self.go_to_work()

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

    def get_dialogue(self, interaction_type="daily"):
        """
        獲取根據性格定制的對話內容\n
        \n
        參數:\n
        interaction_type (str): 互動類型 ("greeting", "daily", "profession")\n
        \n
        回傳:\n
        str: 對話內容\n
        """
        # 如果有性格檔案，使用性格化對話
        if hasattr(self, 'personality_profile') and self.personality_profile:
            # 這裡應該由NPC管理器的性格系統處理
            # 暫時返回隨機對話
            return random.choice(self.dialogue_lines)
        else:
            # 備用方案：返回基本對話
            return random.choice(self.dialogue_lines)

    def set_workplace(self, workplace_position):
        """
        設定工作場所位置\n
        \n
        參數:\n
        workplace_position (tuple): 工作場所座標 (x, y)\n
        """
        self.workplace = workplace_position

    def set_terrain_system(self, terrain_system):
        """
        設定地形系統引用\n
        \n
        參數:\n
        terrain_system: 地形系統實例\n
        """
        self.terrain_system = terrain_system

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

    def get_status_info(self):
        """
        獲取 NPC 的詳細狀態資訊\n
        \n
        回傳:\n
        dict: 包含 NPC 詳細資訊的字典\n
        """
        # 計算當前活動描述
        current_activity = self._get_current_activity_description()

        # 計算下一個活動
        next_activity = self._get_next_activity_description()

        # 格式化位置資訊
        position_str = f"({int(self.x)}, {int(self.y)})"

        return {
            "name": self.name,
            "profession": self.profession.value,
            "position": position_str,
            "current_state": self.state.value,
            "current_activity": current_activity,
            "next_activity": next_activity,
            "is_injured": self.is_injured,
            "health_status": "住院中" if self.is_injured else "健康",
            "is_hidden": self._should_hide_npc(),
        }

    def _get_current_activity_description(self):
        """
        獲取當前活動的中文描述\n
        \n
        回傳:\n
        str: 當前活動描述\n
        """
        if self.is_injured:
            return f"在醫院治療中 (剩餘 {int(self.hospital_stay_time)} 小時)"

        if self.state == NPCState.SLEEPING:
            return "在家中睡覺"
        elif self.state == NPCState.WORKING:
            if self.profession == Profession.POWER_WORKER and self.assigned_area:
                return f"在區域 {self.assigned_area} 巡查電力設施"
            elif self.profession == Profession.FARMER:
                return "在農田工作"
            elif self.profession == Profession.HUNTER:
                return "在森林狩獵"
            elif (
                hasattr(self, "is_interacting_with_building")
                and self.is_interacting_with_building
            ):
                return f"在工作場所執行 {self.profession.value} 職務"
            else:
                return f"執行 {self.profession.value} 工作"
        elif self.state == NPCState.RESTING:
            return "休息中或下班時間"
        elif self.state == NPCState.MOVING:
            return f"前往目標位置 ({int(self.target_x)}, {int(self.target_y)})"
        elif self.state == NPCState.IDLE:
            if not self.is_workday:
                return "休息日閒逛中"
            else:
                return "待機中"
        else:
            return self.state.value

    def _get_next_activity_description(self):
        """
        獲取下一個活動的描述\n
        \n
        回傳:\n
        str: 下一個活動描述\n
        """
        if self.is_injured:
            return "康復後回到工作崗位"

        if not hasattr(self, "current_hour"):
            return "等待時間更新"

        current_hour = self.current_hour

        # 根據當前時間和狀態預測下一個活動
        if current_hour < 6 or current_hour >= 22:
            return "繼續睡覺直到早上 6 點"
        elif self.state == NPCState.SLEEPING:
            return "早上 6 點起床"
        elif not self.is_workday:
            return "繼續休息日活動"
        elif current_hour < 9:
            return "9 點開始工作"
        elif 9 <= current_hour < 17:
            work_end = self.schedule.get("work_end", 17)
            return f"{work_end} 點下班回家"
        else:
            return "22 點準備睡覺"

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

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製 NPC\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機 X 偏移量\n
        camera_y (float): 攝影機 Y 偏移量\n
        """
        # 根據狀態調整顯示
        if self.is_injured:
            # 受傷的 NPC 不在場景中顯示（在醫院）
            return

        # 檢查工作狀態，某些工作狀態下 NPC 不顯示
        if self._should_hide_npc():
            return

        # 計算在螢幕上的位置（世界座標轉螢幕座標）
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        # 繪製 NPC 本體
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)
        pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), self.size, 2)

        # 根據狀態添加狀態指示器
        if self.state == NPCState.WORKING:
            # 工作中顯示小工具圖示
            pygame.draw.rect(
                screen,
                (255, 255, 0),
                (screen_x - 3, screen_y - self.size - 8, 6, 6),
            )
        elif self.state == NPCState.SLEEPING:
            # 睡覺中顯示 Z 符號效果
            pygame.draw.circle(
                screen, (200, 200, 200), (screen_x, screen_y), self.size - 2
            )

        # 顯示 NPC 職業（無業遊民）文字標籤
        font = pygame.font.SysFont('Microsoft JhengHei', 14)
        label = f"{self.name} ({self.profession.value})"
        text_surface = font.render(label, True, (30, 30, 30))
        screen.blit(text_surface, (screen_x - self.size, screen_y + self.size + 2))

    def _should_hide_npc(self):
        """
        判斷 NPC 是否應該隱藏（不在戶外顯示）\n
        \n
        包含以下情況：\n
        1. 某些職業在工作時會進入建築物內部\n
        2. NPC 在睡覺時會在家中，不在戶外顯示\n
        3. NPC 在與建築物互動時會進入建築物內部\n
        \n
        回傳:\n
        bool: True 表示應該隱藏，False 表示正常顯示\n
        """
        # 睡覺時 NPC 在家中，不在戶外顯示
        if self.state == NPCState.SLEEPING:
            return True

        # 工作時某些職業會在建築物內部，不在戶外顯示
        if self.state == NPCState.WORKING:
            # 這些職業在工作時會在建築物內部，不在戶外顯示
            indoor_work_professions = [
                Profession.DOCTOR,  # 醫生在醫院內工作
                Profession.PRIEST,  # 牧師在教堂內工作
                Profession.GUN_SHOP_WORKER,  # 槍械店員工在店內工作
                Profession.CONVENIENCE_STORE_WORKER,  # 便利商店員工在店內工作
                Profession.FISHING_SHOP_WORKER,  # 釣魚店員工在店內工作
                # 可以根據需要添加更多室內工作的職業
            ]
            return self.profession in indoor_work_professions

        # 檢查是否正在與建築物互動（進入建築物內部）
        if (
            hasattr(self, "is_interacting_with_building")
            and self.is_interacting_with_building
        ):
            return True

        return False

    def _set_residential_wander_target(self):
        """
        設定住宅區附近的閒逛目標\n
        在假日時，NPC 只在住宅區附近活動\n
        """
        if not self.terrain_system:
            # 如果沒有地形系統，就在家附近閒逛
            home_x, home_y = self.home_position
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 150)  # 在家附近150像素範圍內
            
            self.target_x = home_x + distance * math.cos(angle)
            self.target_y = home_y + distance * math.sin(angle)
            return
        
        # 找住宅區 (地形代碼 5)
        attempts = 0
        max_attempts = 20
        
        while attempts < max_attempts:
            # 在住宅區範圍內隨機選擇位置
            home_x, home_y = self.home_position
            
            # 在家附近較大範圍內尋找住宅區
            search_radius = 200
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(30, search_radius)
            
            test_x = home_x + distance * math.cos(angle)
            test_y = home_y + distance * math.sin(angle)
            
            terrain_type = self.terrain_system.get_terrain_at_position(test_x, test_y)
            
            # 檢查是否在住宅區或草地（允許在住宅區和草地活動）
            if terrain_type in [0, 5]:  # 0=草地, 5=住宅區
                self.target_x = test_x
                self.target_y = test_y
                self.state = NPCState.MOVING
                return
            
            attempts += 1
        
        # 如果找不到合適的住宅區位置，就在家附近
        home_x, home_y = self.home_position
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(30, 100)
        
        self.target_x = home_x + distance * math.cos(angle)
        self.target_y = home_y + distance * math.sin(angle)
        self.state = NPCState.MOVING

    def draw_info(self, screen, font, camera_x=0, camera_y=0):
        """
        繪製 NPC 資訊 (姓名等)\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體物件\n
        camera_x (float): 攝影機 X 偏移量\n
        camera_y (float): 攝影機 Y 偏移量\n
        """
        if self.is_injured or self._should_hide_npc():
            return

        # 計算在螢幕上的位置（世界座標轉螢幕座標）
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        # 繪製姓名
        name_surface = font.render(self.name, True, (0, 0, 0))
        name_rect = name_surface.get_rect(center=(screen_x, screen_y - self.size - 15))
        screen.blit(name_surface, name_rect)

        # 繪製職業 (小字)
        profession_surface = font.render(self.profession.value, True, (100, 100, 100))
        profession_rect = profession_surface.get_rect(
            center=(screen_x, screen_y - self.size - 30)
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
