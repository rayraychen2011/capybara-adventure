######################載入套件######################
import pygame
import random
import math
from enum import Enum
from config.settings import *


######################農夫工作階段列舉######################
class FarmerWorkPhase(Enum):
    """
    農夫工作階段列舉\n
    \n
    定義農夫一天中的不同工作階段\n
    """
    OFF_DUTY = "off_duty"  # 下班時間：在鎮上自由活動
    GATHERING = "gathering"  # 集合時間：9:00-9:20 在火車站前集合
    WORKING = "working"  # 工作時間：9:20-17:00 在農地工作
    RETURNING = "returning"  # 下班回程：17:00 從農地傳送回火車站前


######################農夫工作調度系統######################
class FarmerWorkScheduler:
    """
    農夫工作調度系統 - 管理50名農夫的集體工作行為\n
    \n
    負責：\n
    1. 農夫工作時間表管理\n
    2. 集體傳送控制\n
    3. 工作區域限制\n
    4. 農夫行為狀態管理\n
    \n
    工作流程：\n
    - 09:00：農夫到火車站前集合\n
    - 09:20：集體傳送到農地旁農地工作\n
    - 17:00：集體傳送回小鎮火車站前解散\n
    - 其他時間：在鎮上自由活動\n
    """

    def __init__(self, npc_manager, terrain_system=None):
        """
        初始化農夫工作調度系統\n
        \n
        參數:\n
        npc_manager: NPC管理器實例\n
        terrain_system: 地形系統實例\n
        """
        self.npc_manager = npc_manager
        self.terrain_system = terrain_system
        
        # 農夫清單
        self.farmers = []  # 所有農夫NPC
        self.working_farmers = []  # 正在工作的農夫
        
        # 工作階段管理
        self.current_phase = FarmerWorkPhase.OFF_DUTY
        self.last_phase_hour = -1  # 記錄上次檢查的小時，避免重複觸發
        
        # 位置設定
        self.town_station_position = None  # 小鎮火車站位置
        self.farm_station_position = None  # 農地旁位置
        self.farm_work_area = None  # 農地工作區域
        
        # 集合和工作區域
        self.gathering_radius = 50  # 集合半徑
        self.work_area_bounds = None  # 工作區域邊界
        
        # 傳送控制
        self.teleport_enabled = True  # 是否允許傳送
        self.emergency_teleport_threshold = 300  # 緊急傳送距離閾值（卡住檢測）
        
        print("農夫工作調度系統初始化完成")

    def initialize_farmers(self):
        """
        初始化農夫清單和工作區域\n
        """
        if not self.npc_manager.all_npcs:
            print("警告：NPC管理器中沒有NPC")
            return
        
        # 找出所有農夫NPC
        from src.systems.npc.profession import Profession
        self.farmers = [npc for npc in self.npc_manager.all_npcs 
                       if npc.profession == Profession.FARMER]
        
        print(f"找到 {len(self.farmers)} 名農夫NPC")
        
        # 設定工作區域
        self._setup_work_areas()
        
        # 為農夫設定特殊標記
        for farmer in self.farmers:
            farmer.is_farmer = True
            farmer.work_phase = FarmerWorkPhase.OFF_DUTY
            farmer.can_teleport = False  # 預設不能傳送
            farmer.is_working_farmer = True  # 標記為工作農夫
            
    def _setup_work_areas(self):
        """
        設定工作區域和火車站位置\n
        """
        # 尋找火車站位置
        if self.terrain_system and hasattr(self.terrain_system, 'railway_system'):
            stations = self.terrain_system.railway_system.train_stations
            if len(stations) >= 2:
                # 假設第一個火車站是小鎮火車站，第二個是農地旁
                self.town_station_position = (stations[0].x + stations[0].width//2, 
                                            stations[0].y + stations[0].height + 20)
                self.farm_station_position = (stations[1].x + stations[1].width//2, 
                                            stations[1].y + stations[1].height + 20)
                print(f"火車站位置設定完成：小鎮站 {self.town_station_position}, 農地旁 {self.farm_station_position}")
            else:
                print("警告：找不到足夠的火車站")
                # 使用預設位置
                self.town_station_position = (400, 300)
                self.farm_station_position = (800, 200)
        
        # 尋找農地工作區域
        if self.terrain_system and hasattr(self.terrain_system, 'farm_areas'):
            if self.terrain_system.farm_areas:
                # 計算農地區域邊界
                farm_positions = [area['position'] for area in self.terrain_system.farm_areas]
                if farm_positions:
                    min_x = min(pos[0] for pos in farm_positions)
                    max_x = max(pos[0] for pos in farm_positions)
                    min_y = min(pos[1] for pos in farm_positions)
                    max_y = max(pos[1] for pos in farm_positions)
                    
                    # 擴大工作區域邊界
                    padding = 50
                    self.work_area_bounds = {
                        'min_x': min_x - padding,
                        'max_x': max_x + padding,
                        'min_y': min_y - padding,
                        'max_y': max_y + padding
                    }
                    print(f"農地工作區域設定完成：{self.work_area_bounds}")
                else:
                    print("警告：沒有找到農地區域")
            else:
                print("警告：地形系統中沒有農地區域")

    def update(self, dt, time_manager):
        """
        更新農夫工作調度\n
        \n
        參數:\n
        dt (float): 時間差\n
        time_manager: 時間管理器\n
        """
        if not time_manager or not self.farmers:
            return
        
        current_hour = time_manager.hour
        current_minute = time_manager.minute
        
        # 檢查是否需要更新工作階段
        if current_hour != self.last_phase_hour:
            self._check_phase_transition(current_hour, current_minute)
            self.last_phase_hour = current_hour
        
        # 更新農夫狀態
        self._update_farmers_behavior(dt, current_hour, current_minute)
        
        # 檢查卡住的農夫（緊急傳送）
        self._check_stuck_farmers()

    def _check_phase_transition(self, hour, minute):
        """
        檢查工作階段轉換\n
        \n
        參數:\n
        hour (int): 當前小時\n
        minute (int): 當前分鐘\n
        """
        old_phase = self.current_phase
        
        # 判斷當前應該在哪個階段
        if hour == 9 and minute < 20:
            self.current_phase = FarmerWorkPhase.GATHERING
        elif (hour == 9 and minute >= 20) or (9 < hour < 17):
            self.current_phase = FarmerWorkPhase.WORKING
        elif hour == 17 and minute == 0:
            self.current_phase = FarmerWorkPhase.RETURNING
        else:
            self.current_phase = FarmerWorkPhase.OFF_DUTY
        
        # 如果階段發生變化，觸發相應行為
        if old_phase != self.current_phase:
            self._handle_phase_transition(old_phase, self.current_phase)

    def _handle_phase_transition(self, old_phase, new_phase):
        """
        處理工作階段轉換\n
        \n
        參數:\n
        old_phase: 舊階段\n
        new_phase: 新階段\n
        """
        print(f"農夫工作階段轉換: {old_phase.value} -> {new_phase.value}")
        
        if new_phase == FarmerWorkPhase.GATHERING:
            self._start_gathering_phase()
        elif new_phase == FarmerWorkPhase.WORKING:
            self._start_working_phase()
        elif new_phase == FarmerWorkPhase.RETURNING:
            self._start_returning_phase()
        elif new_phase == FarmerWorkPhase.OFF_DUTY:
            self._start_off_duty_phase()

    def _start_gathering_phase(self):
        """
        開始集合階段 (09:00-09:20)\n
        """
        print("📢 農夫集合階段開始 - 農夫們前往火車站前集合")
        
        if not self.town_station_position:
            print("警告：小鎮火車站位置未設定")
            return
        
        for farmer in self.farmers:
            farmer.work_phase = FarmerWorkPhase.GATHERING
            farmer.can_teleport = False  # 集合期間不能傳送
            
            # 設定前往集合點的目標
            gathering_x = self.town_station_position[0] + random.randint(-30, 30)
            gathering_y = self.town_station_position[1] + random.randint(-30, 30)
            farmer.move_to_location(gathering_x, gathering_y)
            
            # 清除其他移動目標
            farmer.target_position = (gathering_x, gathering_y)

    def _start_working_phase(self):
        """
        開始工作階段 (09:20-17:00)\n
        """
        print("🚜 農夫工作階段開始 - 集體傳送到農地工作")
        
        if not self.farm_station_position or not self.work_area_bounds:
            print("警告：農地工作區域未設定")
            return
        
        # 集體傳送到農地
        self._teleport_farmers_to_farm()
        
        for farmer in self.farmers:
            farmer.work_phase = FarmerWorkPhase.WORKING
            farmer.can_teleport = False  # 工作期間不能傳送
            
            # 設定在農地內的隨機工作位置
            work_x = random.randint(self.work_area_bounds['min_x'], 
                                  self.work_area_bounds['max_x'])
            work_y = random.randint(self.work_area_bounds['min_y'], 
                                  self.work_area_bounds['max_y'])
            farmer.move_to_location(work_x, work_y)

    def _start_returning_phase(self):
        """
        開始返回階段 (17:00)\n
        """
        print("🏠 農夫下班階段開始 - 集體傳送回火車站前")
        
        if not self.town_station_position:
            print("警告：小鎮火車站位置未設定")
            return
        
        # 集體傳送回小鎮火車站
        self._teleport_farmers_to_town()
        
        for farmer in self.farmers:
            farmer.work_phase = FarmerWorkPhase.RETURNING
            farmer.can_teleport = False  # 剛下班時不能傳送

    def _start_off_duty_phase(self):
        """
        開始下班階段 (其他時間)\n
        """
        print("🎯 農夫下班時間 - 在鎮上自由活動")
        
        for farmer in self.farmers:
            farmer.work_phase = FarmerWorkPhase.OFF_DUTY
            farmer.can_teleport = False  # 正常情況下不能傳送
            
            # 取消工作相關的移動目標，讓農夫自由活動
            farmer.target_position = None

    def _teleport_farmers_to_farm(self):
        """
        將農夫傳送到農地工作區域\n
        """
        if not self.work_area_bounds:
            print("警告：農地工作區域未設定，無法傳送")
            return
        
        teleported_count = 0
        
        for farmer in self.farmers:
            # 在農地區域內隨機選擇位置
            farm_x = random.randint(self.work_area_bounds['min_x'], 
                                  self.work_area_bounds['max_x'])
            farm_y = random.randint(self.work_area_bounds['min_y'], 
                                  self.work_area_bounds['max_y'])
            
            # 檢查位置是否安全
            if self._is_position_safe_for_farmer(farm_x, farm_y):
                farmer.x = farm_x
                farmer.y = farm_y
                teleported_count += 1
            else:
                # 如果位置不安全，使用農地中心點
                center_x = (self.work_area_bounds['min_x'] + self.work_area_bounds['max_x']) // 2
                center_y = (self.work_area_bounds['min_y'] + self.work_area_bounds['max_y']) // 2
                farmer.x = center_x + random.randint(-20, 20)
                farmer.y = center_y + random.randint(-20, 20)
                teleported_count += 1
        
        print(f"✅ 成功傳送 {teleported_count} 名農夫到農地工作")

    def _teleport_farmers_to_town(self):
        """
        將農夫傳送回小鎮火車站前\n
        """
        if not self.town_station_position:
            print("警告：小鎮火車站位置未設定，無法傳送")
            return
        
        teleported_count = 0
        
        for farmer in self.farmers:
            # 在火車站前隨機分散
            town_x = self.town_station_position[0] + random.randint(-40, 40)
            town_y = self.town_station_position[1] + random.randint(-40, 40)
            
            farmer.x = town_x
            farmer.y = town_y
            teleported_count += 1
        
        print(f"✅ 成功傳送 {teleported_count} 名農夫回到小鎮火車站前")

    def _is_position_safe_for_farmer(self, x, y):
        """
        檢查位置對農夫是否安全\n
        \n
        參數:\n
        x (int): X座標\n
        y (int): Y座標\n
        \n
        回傳:\n
        bool: 位置是否安全\n
        """
        # 檢查是否在農地區域內
        if self.work_area_bounds:
            if not (self.work_area_bounds['min_x'] <= x <= self.work_area_bounds['max_x'] and
                    self.work_area_bounds['min_y'] <= y <= self.work_area_bounds['max_y']):
                return False
        
        # 檢查地形（農夫可以在農地上）
        if self.terrain_system:
            terrain_code = self.terrain_system.get_terrain_at_position(x, y)
            if terrain_code == 8:  # 農地
                return True
        
        return True

    def _update_farmers_behavior(self, dt, hour, minute):
        """
        更新農夫行為\n
        \n
        參數:\n
        dt (float): 時間差\n
        hour (int): 當前小時\n
        minute (int): 當前分鐘\n
        """
        for farmer in self.farmers:
            # 確保農夫的工作階段與系統同步
            farmer.work_phase = self.current_phase
            
            # 工作時間限制檢查
            if self.current_phase == FarmerWorkPhase.WORKING:
                self._enforce_work_area_restriction(farmer)
            
            # 更新農夫的傳送權限
            self._update_farmer_teleport_permission(farmer)

    def _enforce_work_area_restriction(self, farmer):
        """
        強制農夫在工作區域內\n
        \n
        參數:\n
        farmer: 農夫NPC\n
        """
        if not self.work_area_bounds:
            return
        
        # 檢查農夫是否在工作區域外
        if not (self.work_area_bounds['min_x'] <= farmer.x <= self.work_area_bounds['max_x'] and
                self.work_area_bounds['min_y'] <= farmer.y <= self.work_area_bounds['max_y']):
            
            # 將農夫拉回工作區域
            center_x = (self.work_area_bounds['min_x'] + self.work_area_bounds['max_x']) // 2
            center_y = (self.work_area_bounds['min_y'] + self.work_area_bounds['max_y']) // 2
            
            farmer.x = center_x + random.randint(-30, 30)
            farmer.y = center_y + random.randint(-30, 30)
            
            print(f"農夫 {farmer.name} 被拉回工作區域")

    def _update_farmer_teleport_permission(self, farmer):
        """
        更新農夫的傳送權限\n
        \n
        參數:\n
        farmer: 農夫NPC\n
        """
        # 正常情況下農夫不能傳送
        farmer.can_teleport = False
        
        # 只有在緊急情況（卡住）時才允許傳送
        # 這個邏輯在 _check_stuck_farmers 中處理

    def _check_stuck_farmers(self):
        """
        檢查卡住的農夫並進行緊急傳送\n
        """
        for farmer in self.farmers:
            # 檢查農夫是否長時間沒有移動（卡住）
            if hasattr(farmer, 'last_position') and hasattr(farmer, 'stuck_timer'):
                current_pos = (farmer.x, farmer.y)
                
                # 如果位置沒有變化
                if farmer.last_position == current_pos:
                    farmer.stuck_timer += 1
                    
                    # 如果卡住超過5秒（300幀 @ 60fps）
                    if farmer.stuck_timer > 300:
                        self._emergency_teleport_farmer(farmer)
                        farmer.stuck_timer = 0
                else:
                    farmer.stuck_timer = 0
                
                farmer.last_position = current_pos
            else:
                # 初始化卡住檢測
                farmer.last_position = (farmer.x, farmer.y)
                farmer.stuck_timer = 0

    def _emergency_teleport_farmer(self, farmer):
        """
        緊急傳送卡住的農夫\n
        \n
        參數:\n
        farmer: 卡住的農夫NPC\n
        """
        print(f"⚠️ 緊急傳送卡住的農夫 {farmer.name}")
        
        # 根據當前工作階段決定傳送目標
        if self.current_phase == FarmerWorkPhase.WORKING and self.work_area_bounds:
            # 傳送到農地工作區域
            center_x = (self.work_area_bounds['min_x'] + self.work_area_bounds['max_x']) // 2
            center_y = (self.work_area_bounds['min_y'] + self.work_area_bounds['max_y']) // 2
            farmer.x = center_x + random.randint(-20, 20)
            farmer.y = center_y + random.randint(-20, 20)
        elif self.current_phase == FarmerWorkPhase.GATHERING and self.town_station_position:
            # 傳送到集合點
            farmer.x = self.town_station_position[0] + random.randint(-30, 30)
            farmer.y = self.town_station_position[1] + random.randint(-30, 30)
        else:
            # 傳送到小鎮中心安全位置
            if self.town_station_position:
                farmer.x = self.town_station_position[0] + random.randint(-50, 50)
                farmer.y = self.town_station_position[1] + random.randint(-50, 50)

    def get_farmer_status(self):
        """
        獲取農夫狀態資訊\n
        \n
        回傳:\n
        dict: 農夫狀態統計\n
        """
        status = {
            'total_farmers': len(self.farmers),
            'current_phase': self.current_phase.value,
            'working_farmers': len([f for f in self.farmers if f.work_phase == FarmerWorkPhase.WORKING]),
            'gathering_farmers': len([f for f in self.farmers if f.work_phase == FarmerWorkPhase.GATHERING]),
            'off_duty_farmers': len([f for f in self.farmers if f.work_phase == FarmerWorkPhase.OFF_DUTY]),
        }
        return status

    def set_terrain_system(self, terrain_system):
        """
        設定地形系統引用\n
        \n
        參數:\n
        terrain_system: 地形系統實例\n
        """
        self.terrain_system = terrain_system
        self._setup_work_areas()  # 重新設定工作區域

    def force_phase_transition(self, new_phase):
        """
        強制切換工作階段（用於測試）\n
        \n
        參數:\n
        new_phase (FarmerWorkPhase): 新的工作階段\n
        """
        old_phase = self.current_phase
        self.current_phase = new_phase
        self._handle_phase_transition(old_phase, new_phase)
        print(f"強制切換農夫工作階段: {old_phase.value} -> {new_phase.value}")