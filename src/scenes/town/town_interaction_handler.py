######################載入套件######################
import pygame
from config.settings import *


######################小鎮互動處理器######################
class TownInteractionHandler:
    """
    小鎮場景互動處理器 - 處理玩家與環境的所有互動\n
    \n
    負責：\n
    1. 建築物互動\n
    2. NPC 互動\n
    3. 載具互動\n
    4. 地形特殊區域互動\n
    5. 物品拾取\n
    """

    def __init__(self, player, ui_manager):
        """
        初始化互動處理器\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        ui_manager (TownUIManager): UI 管理器\n
        """
        self.player = player
        self.ui_manager = ui_manager
        
        # 互動範圍設定
        self.interaction_range = 50  # 互動距離
        self.pickup_range = 30       # 拾取距離
        
        # 互動狀態
        self.last_interaction_time = 0
        self.interaction_cooldown = 0.5  # 互動冷卻時間（秒）
        
        print("小鎮互動處理器初始化完成")

    def update(self, dt):
        """
        更新互動系統\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        # 更新互動冷卻計時器
        if self.last_interaction_time > 0:
            self.last_interaction_time -= dt

    def handle_interaction(self, terrain_system, npc_manager, vehicle_manager):
        """
        處理玩家互動輸入\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        npc_manager (NPCManager): NPC 管理器\n
        vehicle_manager (VehicleManager): 載具管理器\n
        \n
        回傳:\n
        bool: 是否有執行互動\n
        """
        # 檢查互動冷卻
        if self.last_interaction_time > 0:
            return False
        
        player_pos = (self.player.x, self.player.y)
        
        # 按優先順序檢查互動對象
        
        # 1. 檢查載具互動（最高優先級）
        if self._check_vehicle_interaction(vehicle_manager, player_pos):
            return True
        
        # 2. 檢查 NPC 互動
        if self._check_npc_interaction(npc_manager, player_pos):
            return True
        
        # 3. 檢查建築物互動
        if self._check_building_interaction(terrain_system, player_pos):
            return True
        
        # 4. 檢查地形特殊區域
        if self._check_terrain_interaction(terrain_system, player_pos):
            return True
        
        # 沒有找到互動對象
        self.ui_manager.show_message("附近沒有可互動的對象", 1.5)
        return False

    def _check_vehicle_interaction(self, vehicle_manager, player_pos):
        """
        檢查載具互動\n
        \n
        參數:\n
        vehicle_manager (VehicleManager): 載具管理器\n
        player_pos (tuple): 玩家位置\n
        \n
        回傳:\n
        bool: 是否有互動\n
        """
        nearby_vehicle = vehicle_manager.get_nearby_vehicle(player_pos, self.interaction_range)
        
        if nearby_vehicle:
            if nearby_vehicle.driver is None:
                # 上車
                if nearby_vehicle.get_on(self.player):
                    self.ui_manager.show_message(f"上了{nearby_vehicle.vehicle_type}")
                    self._set_interaction_cooldown()
                    return True
                else:
                    self.ui_manager.show_message("無法上車")
            else:
                # 下車（如果玩家在車上）
                player_vehicle = vehicle_manager.get_player_vehicle(self.player)
                if player_vehicle and player_vehicle == nearby_vehicle:
                    if nearby_vehicle.get_off():
                        self.ui_manager.show_message("下車了")
                        self._set_interaction_cooldown()
                        return True
                    else:
                        self.ui_manager.show_message("無法在此處下車")
                else:
                    self.ui_manager.show_message("這輛車已經有人在開了")
            
            return True
        
        return False

    def _check_npc_interaction(self, npc_manager, player_pos):
        """
        檢查 NPC 互動\n
        \n
        參數:\n
        npc_manager (NPCManager): NPC 管理器\n
        player_pos (tuple): 玩家位置\n
        \n
        回傳:\n
        bool: 是否有互動\n
        """
        nearby_npc = npc_manager.get_npc_at_position(player_pos, self.interaction_range)
        
        if nearby_npc:
            # 與 NPC 對話
            npc_manager.interact_with_npc(nearby_npc)
            
            # 顯示對話內容
            dialogue_line = nearby_npc.get_dialogue_line()
            self.ui_manager.show_message(f"{nearby_npc.name}: {dialogue_line}", 3.0)
            
            self._set_interaction_cooldown()
            return True
        
        return False

    def _check_building_interaction(self, terrain_system, player_pos):
        """
        檢查建築物互動\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        player_pos (tuple): 玩家位置\n
        \n
        回傳:\n
        bool: 是否有互動\n
        """
        # 檢查玩家附近的建築物（使用新的建築物系統）
        for building in terrain_system.buildings:
            # 檢查是否是新的建築物類別（有 can_interact 方法）
            if hasattr(building, 'can_interact'):
                if building.can_interact(player_pos, self.interaction_range):
                    # 執行建築物互動
                    result = self._interact_with_new_building(building)
                    if result:
                        self._set_interaction_cooldown()
                        return True
            else:
                # 舊版建築物系統（保持兼容性）
                building_x = building.get("x", building.x if hasattr(building, 'x') else 0)
                building_y = building.get("y", building.y if hasattr(building, 'y') else 0)
                
                distance = ((player_pos[0] - building_x) ** 2 + 
                           (player_pos[1] - building_y) ** 2) ** 0.5
                
                if distance <= self.interaction_range:
                    # 執行舊版建築物互動
                    self._interact_with_old_building(building)
                    self._set_interaction_cooldown()
                    return True
        
        return False

    def _interact_with_new_building(self, building):
        """
        與新版建築物互動\n
        \n
        參數:\n
        building (Building): 建築物物件\n
        \n
        回傳:\n
        bool: 是否成功互動\n
        """
        try:
            result = building.interact(self.player)
            
            if result.get("success", False):
                message = result.get("message", "與建築物互動")
                self.ui_manager.show_message(message, 2.5)
                
                # 處理特殊互動動作
                action = result.get("action")
                
                if action == "enter_interior":
                    # 進入住宅內部檢視
                    self.ui_manager.show_message("進入住宅內部檢視模式", 2.0)
                    # 這裡可以觸發特殊的內部檢視模式邏輯
                    
                elif action == "exit_interior":
                    # 離開住宅內部檢視
                    self.ui_manager.show_message("離開住宅內部檢視模式", 2.0)
                    # 玩家位置會由建築物的 interact 方法處理
                    if "exterior_position" in result:
                        new_x, new_y = result["exterior_position"]
                        self.player.set_position(new_x, new_y)
                
                elif action == "enter_home":
                    # 玩家之家特殊互動
                    self.ui_manager.show_message("歡迎回到您的家！", 2.0)
                    
                elif action == "view_interior" or action == "view_exterior":
                    # 一般住宅檢視
                    residents = result.get("residents", [])
                    if residents:
                        resident_names = [getattr(r, 'name', '居民') for r in residents]
                        self.ui_manager.show_message(f"居民: {', '.join(resident_names[:3])}", 3.0)
                    else:
                        self.ui_manager.show_message("空房子", 2.0)
                
                # 處理建築物特殊服務
                services = result.get("services", [])
                if services:
                    service_text = ", ".join(services[:3])  # 顯示前3個服務
                    self.ui_manager.show_message(f"可用服務: {service_text}", 2.5)
                
                return True
            else:
                # 互動失敗
                error_message = result.get("message", "無法與此建築物互動")
                self.ui_manager.show_message(error_message, 2.0)
                return False
                
        except Exception as e:
            print(f"建築物互動錯誤: {e}")
            self.ui_manager.show_message("建築物互動出現問題", 2.0)
            return False

    def _interact_with_old_building(self, building):
        """
        與舊版建築物互動（保持兼容性）\n
        \n
        參數:\n
        building (dict): 建築物資訊\n
        """
        building_name = building.get("name", "建築物")
        building_type = building.get("type", "unknown")
        
        # 根據建築物類型顯示不同的互動訊息
        interaction_messages = {
            "house": f"{building_name}：這是某人的家",
            "gun_shop": f"{building_name}：歡迎來到槍械店！需要武器嗎？",
            "hospital": f"{building_name}：醫院為您服務，需要治療嗎？",
            "convenience_store": f"{building_name}：便利商店歡迎您！",
            "church": f"{building_name}：願神保佑你！",
            "fishing_shop": f"{building_name}：釣魚用品應有盡有！",
            "market": f"{building_name}：新鮮商品，快來選購！",
            "street_vendor": f"{building_name}：小攤販，便宜又好吃！",
            "power_plant": f"{building_name}：電力場 - 小鎮的能源中心",
            "bank": f"{building_name}：銀行為您提供金融服務",
            "school": f"{building_name}：學校 - 知識的殿堂",
            "tavern": f"{building_name}：酒館 - 來喝一杯放鬆一下！",
        }
        
        message = interaction_messages.get(building_type, f"{building_name}：普通建築物")
        self.ui_manager.show_message(message, 2.5)
        
        # 特殊建築物的額外功能
        if building_type == "hospital" and self.player.health < PLAYER_MAX_HEALTH:
            # 醫院可以治療
            self.player.health = PLAYER_MAX_HEALTH
            self.ui_manager.show_message("健康已完全恢復！", 2.0)
        
        elif building_type == "bank":
            # 銀行顯示餘額
            balance = self.player.get_money()
            self.ui_manager.show_message(f"您的帳戶餘額：${balance}", 2.0)

    def _check_terrain_interaction(self, terrain_system, player_pos):
        """
        檢查地形特殊區域互動\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        player_pos (tuple): 玩家位置\n
        \n
        回傳:\n
        bool: 是否有互動\n
        """
        # 獲取玩家當前位置的地形類型
        terrain_type = terrain_system.get_terrain_at_position(player_pos[0], player_pos[1])
        
        if terrain_type == 1:  # 森林區域
            self.ui_manager.show_message("🌲 森林生態區域 - 可以狩獵和採集", 2.0)
            self._set_interaction_cooldown()
            return True
        
        elif terrain_type == 2:  # 水體區域
            self.ui_manager.show_message("🏞️ 湖泊生態區域 - 可以釣魚", 2.0)
            self._set_interaction_cooldown()
            return True
        
        elif terrain_type == 8:  # 停車場
            self.ui_manager.show_message("🅿️ 停車場 - 載具停放區域", 1.5)
            self._set_interaction_cooldown()
            return True
        
        return False

    def check_automatic_pickups(self, terrain_system):
        """
        檢查自動拾取物品\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        """
        player_pos = (self.player.x, self.player.y)
        
        # 檢查森林資源
        picked_resources = []
        for resource in terrain_system.forest_resources[:]:  # 使用切片複製列表
            # 從 position 元組中獲取 x, y 座標
            resource_pos = resource["position"]
            distance = ((player_pos[0] - resource_pos[0]) ** 2 + 
                       (player_pos[1] - resource_pos[1]) ** 2) ** 0.5
            
            if distance <= self.pickup_range:
                # 拾取資源
                item_name = resource["name"]  # 使用 'name' 而不是 'type'
                if self.player.add_item(item_name, 1):
                    picked_resources.append(resource)
                    self.ui_manager.show_message(f"獲得 {item_name}", 1.5)
        
        # 移除已拾取的資源
        for resource in picked_resources:
            if resource in terrain_system.forest_resources:
                terrain_system.forest_resources.remove(resource)

    def _set_interaction_cooldown(self):
        """
        設定互動冷卻時間\n
        """
        self.last_interaction_time = self.interaction_cooldown

    def get_nearby_interactables(self, terrain_system, npc_manager, vehicle_manager):
        """
        獲取附近可互動對象的資訊\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        npc_manager (NPCManager): NPC 管理器\n
        vehicle_manager (VehicleManager): 載具管理器\n
        \n
        回傳:\n
        list: 可互動對象列表\n
        """
        player_pos = (self.player.x, self.player.y)
        interactables = []
        
        # 檢查載具
        nearby_vehicle = vehicle_manager.get_nearby_vehicle(player_pos, self.interaction_range)
        if nearby_vehicle:
            interactables.append({
                "type": "vehicle",
                "name": nearby_vehicle.vehicle_type,
                "distance": self._calculate_distance(player_pos, (nearby_vehicle.x, nearby_vehicle.y))
            })
        
        # 檢查 NPC
        nearby_npc = npc_manager.get_npc_at_position(player_pos, self.interaction_range)
        if nearby_npc:
            interactables.append({
                "type": "npc",
                "name": nearby_npc.name,
                "distance": self._calculate_distance(player_pos, (nearby_npc.x, nearby_npc.y))
            })
        
        # 檢查建築物
        for building in terrain_system.buildings:
            distance = self._calculate_distance(player_pos, (building["x"], building["y"]))
            if distance <= self.interaction_range:
                interactables.append({
                    "type": "building",
                    "name": building.get("name", "建築物"),
                    "distance": distance
                })
        
        return interactables

    def _calculate_distance(self, pos1, pos2):
        """
        計算兩點距離\n
        \n
        參數:\n
        pos1 (tuple): 第一個位置\n
        pos2 (tuple): 第二個位置\n
        \n
        回傳:\n
        float: 距離\n
        """
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5