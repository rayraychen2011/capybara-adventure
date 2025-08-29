######################載入套件######################
import pygame
import math
import random
from config.settings import *


######################碰撞防止傳送系統######################
class AntiOverlapTeleportSystem:
    """
    碰撞防止傳送系統 - 防止玩家和NPC與建築物重疊\n
    \n
    當檢測到玩家或NPC與建築物、水體、樹木等物件重疊時，\n
    自動將其傳送到最近的平原或道路\n
    """

    def __init__(self, terrain_system):
        """
        初始化碰撞防止傳送系統\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        """
        self.terrain_system = terrain_system
        self.last_check_time = 0
        self.check_interval = 1.0  # 每秒檢查一次
        
        # 安全區域類型（可移動的地形）
        self.safe_terrain_types = [0, 3]  # 草地和道路
        
        # 傳送搜索範圍
        self.search_radius = 100  # 搜索安全位置的半徑
        self.max_search_attempts = 20  # 最大搜索嘗試次數
        
        print("🚧 碰撞防止傳送系統已初始化")

    def update(self, dt, player, npc_manager=None):
        """
        更新系統狀態，檢查並處理重疊\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player (Player): 玩家物件\n
        npc_manager (NPCManager): NPC管理器（可選）\n
        """
        current_time = pygame.time.get_ticks() / 1000.0
        
        # 限制檢查頻率以避免性能問題
        if current_time - self.last_check_time < self.check_interval:
            return
        
        self.last_check_time = current_time
        
        # 檢查玩家是否需要傳送
        self._check_and_teleport_player(player)
        
        # 檢查NPC是否需要傳送
        if npc_manager:
            self._check_and_teleport_npcs(npc_manager)

    def _check_and_teleport_player(self, player):
        """
        檢查並傳送玩家\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        player_pos = player.get_center_position()
        
        # 檢查玩家是否在不安全位置
        if not self._is_position_safe(player_pos[0], player_pos[1]):
            safe_position = self._find_safe_position(player_pos[0], player_pos[1])
            
            if safe_position:
                # 傳送玩家到安全位置
                player.set_position(safe_position[0] - player.width//2, safe_position[1] - player.height//2)
                print(f"🚁 玩家已傳送到安全位置: ({safe_position[0]:.1f}, {safe_position[1]:.1f})")
            else:
                # 找不到安全位置，傳送到地圖中心的草地
                self._emergency_teleport_player(player)

    def _check_and_teleport_npcs(self, npc_manager):
        """
        檢查並傳送NPC\n
        \n
        參數:\n
        npc_manager (NPCManager): NPC管理器\n
        """
        if not hasattr(npc_manager, 'npcs'):
            return
        
        teleported_count = 0
        
        for npc in npc_manager.all_npcs:
            npc_pos = (npc.x + 4, npc.y + 4)  # NPC中心位置（假設NPC大小為8x8）
            
            # 檢查NPC是否在不安全位置
            if not self._is_position_safe(npc_pos[0], npc_pos[1]):
                safe_position = self._find_safe_position(npc_pos[0], npc_pos[1])
                
                if safe_position:
                    # 傳送NPC到安全位置
                    npc.x = safe_position[0] - 4
                    npc.y = safe_position[1] - 4
                    teleported_count += 1
                else:
                    # 找不到安全位置，傳送到隨機草地
                    self._emergency_teleport_npc(npc)
                    teleported_count += 1
        
        if teleported_count > 0:
            print(f"🚁 已傳送 {teleported_count} 個NPC到安全位置")

    def _is_position_safe(self, x, y):
        """
        檢查位置是否安全（可移動）\n
        \n
        參數:\n
        x (float): X座標\n
        y (float): Y座標\n
        \n
        回傳:\n
        bool: 是否安全\n
        """
        if not self.terrain_system:
            return True
        
        # 使用地形系統的碰撞檢測
        dummy_rect = pygame.Rect(x-4, y-4, 8, 8)  # 創建小矩形進行檢測
        return self.terrain_system.can_move_to_position(x, y, dummy_rect)

    def _find_safe_position(self, center_x, center_y):
        """
        尋找最近的安全位置\n
        \n
        參數:\n
        center_x (float): 搜索中心X座標\n
        center_y (float): 搜索中心Y座標\n
        \n
        回傳:\n
        tuple: 安全位置座標，如果找不到則返回None\n
        """
        # 使用螺旋搜索方式尋找安全位置
        for radius in range(10, self.search_radius, 20):
            for angle_step in range(0, 360, 30):  # 每30度檢查一次
                angle = angle_step * 3.14159 / 180  # 轉換為弧度
                
                test_x = center_x + radius * math.cos(angle)
                test_y = center_y + radius * math.sin(angle)
                
                # 確保在地圖範圍內
                if self._is_within_map_bounds(test_x, test_y):
                    if self._is_position_safe(test_x, test_y):
                        return (test_x, test_y)
        
        return None

    def _is_within_map_bounds(self, x, y):
        """
        檢查座標是否在地圖範圍內\n
        \n
        參數:\n
        x (float): X座標\n
        y (float): Y座標\n
        \n
        回傳:\n
        bool: 是否在範圍內\n
        """
        if not self.terrain_system:
            return True
        
        map_width = getattr(self.terrain_system, 'map_width', 100) * getattr(self.terrain_system, 'tile_size', 32)
        map_height = getattr(self.terrain_system, 'map_height', 100) * getattr(self.terrain_system, 'tile_size', 32)
        
        return 0 <= x <= map_width and 0 <= y <= map_height

    def _emergency_teleport_player(self, player):
        """
        緊急傳送玩家到安全位置\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        # 傳送到玩家的重生點或地圖中心
        if hasattr(player, 'spawn_position') and player.spawn_position:
            safe_x, safe_y = player.spawn_position
        else:
            # 預設傳送到地圖中心附近的草地
            if self.terrain_system:
                map_width = getattr(self.terrain_system, 'map_width', 100) * getattr(self.terrain_system, 'tile_size', 32)
                map_height = getattr(self.terrain_system, 'map_height', 100) * getattr(self.terrain_system, 'tile_size', 32)
                safe_x = map_width // 2
                safe_y = map_height // 2
            else:
                safe_x, safe_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        player.set_position(safe_x - player.width//2, safe_y - player.height//2)
        print(f"🚨 緊急傳送玩家到: ({safe_x:.1f}, {safe_y:.1f})")

    def _emergency_teleport_npc(self, npc):
        """
        緊急傳送NPC到安全位置\n
        \n
        參數:\n
        npc (NPC): NPC物件\n
        """
        # 傳送到NPC的家或隨機安全位置
        if hasattr(npc, 'home_position') and npc.home_position:
            safe_x, safe_y = npc.home_position
        else:
            # 隨機選擇一個相對安全的位置
            if self.terrain_system:
                map_width = getattr(self.terrain_system, 'map_width', 100) * getattr(self.terrain_system, 'tile_size', 32)
                map_height = getattr(self.terrain_system, 'map_height', 100) * getattr(self.terrain_system, 'tile_size', 32)
                safe_x = random.uniform(map_width * 0.2, map_width * 0.8)
                safe_y = random.uniform(map_height * 0.2, map_height * 0.8)
            else:
                safe_x = random.uniform(100, SCREEN_WIDTH - 100)
                safe_y = random.uniform(100, SCREEN_HEIGHT - 100)
        
        npc.x = safe_x - 4
        npc.y = safe_y - 4

    def force_teleport_to_safe_position(self, entity, target_x=None, target_y=None):
        """
        強制傳送實體到安全位置\n
        \n
        參數:\n
        entity (Player/NPC): 要傳送的實體\n
        target_x (float): 目標X座標（可選）\n
        target_y (float): 目標Y座標（可選）\n
        \n
        回傳:\n
        bool: 是否成功傳送\n
        """
        if target_x is None or target_y is None:
            # 自動尋找安全位置
            current_pos = entity.get_center_position() if hasattr(entity, 'get_center_position') else (entity.x + 4, entity.y + 4)
            safe_position = self._find_safe_position(current_pos[0], current_pos[1])
            
            if safe_position:
                target_x, target_y = safe_position
            else:
                return False
        
        # 執行傳送
        if hasattr(entity, 'set_position'):  # 玩家
            entity.set_position(target_x - entity.width//2, target_y - entity.height//2)
        else:  # NPC
            entity.x = target_x - 4
            entity.y = target_y - 4
        
        print(f"🚁 強制傳送實體到: ({target_x:.1f}, {target_y:.1f})")
        return True

    def check_water_overlap_and_teleport(self, entity):
        """
        檢查實體是否在水中，如果是則傳送到安全位置\n
        \n
        參數:\n
        entity (Player/NPC): 要檢查的實體\n
        \n
        回傳:\n
        bool: 是否進行了傳送\n
        """
        if not self.terrain_system:
            return False
        
        # 獲取實體位置
        if hasattr(entity, 'get_center_position'):
            entity_pos = entity.get_center_position()
        else:
            entity_pos = (entity.x + 4, entity.y + 4)
        
        # 檢查是否在水中
        if hasattr(self.terrain_system, 'check_water_collision'):
            if self.terrain_system.check_water_collision(entity_pos[0], entity_pos[1]):
                # 在水中，需要傳送
                safe_position = self._find_safe_position(entity_pos[0], entity_pos[1])
                if safe_position:
                    self.force_teleport_to_safe_position(entity, safe_position[0], safe_position[1])
                    return True
        
        return False