######################載入套件######################
import pygame
import random
import math
from config.settings import *


######################NPC 移動行為模組######################
class NPCMovementBehavior:
    """
    NPC 移動行為管理器 - 處理所有移動相關的邏輯\n
    \n
    負責：\n
    1. 基礎移動計算\n
    2. 路徑規劃\n
    3. 碰撞避免\n
    4. 移動動畫\n
    5. 移動狀態管理\n
    """

    def __init__(self, npc):
        """
        初始化移動行為\n
        \n
        參數:\n
        npc: NPC 實例引用\n
        """
        self.npc = npc
        
        # 移動參數
        self.base_speed = 20  # 基礎移動速度
        self.current_speed = self.base_speed
        self.max_speed = 50   # 最大移動速度
        self.acceleration = 100  # 加速度
        
        # 目標和路徑
        self.target_position = None
        self.path_waypoints = []
        self.current_waypoint_index = 0
        self.waypoint_reached_distance = 5.0  # 認為到達路點的距離
        
        # 移動狀態
        self.is_moving = False
        self.movement_direction = (0, 0)
        self.stuck_timer = 0
        self.stuck_threshold = 3.0  # 卡住判定時間（秒）
        self.last_position = (npc.x, npc.y)
        self.position_change_threshold = 1.0  # 位置變化最小閾值
        
        # 隨機遊走設定
        self.wander_radius = 100  # 遊走半徑
        self.wander_change_interval = 5.0  # 改變遊走目標的間隔
        self.last_wander_change = 0
        
        print(f"NPC {npc.name} 移動行為初始化完成")

    def update(self, dt):
        """
        更新移動行為\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        # 更新卡住檢測
        self._update_stuck_detection(dt)
        
        # 更新移動邏輯
        if self.target_position:
            self._update_target_movement(dt)
        else:
            self._update_wander_movement(dt)
        
        # 應用移動
        self._apply_movement(dt)

    def _update_stuck_detection(self, dt):
        """
        更新卡住檢測\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        current_pos = (self.npc.x, self.npc.y)
        position_change = math.sqrt(
            (current_pos[0] - self.last_position[0]) ** 2 +
            (current_pos[1] - self.last_position[1]) ** 2
        )
        
        if position_change < self.position_change_threshold and self.is_moving:
            # NPC 在移動但位置變化很小，可能卡住了
            self.stuck_timer += dt
            
            if self.stuck_timer >= self.stuck_threshold:
                self._handle_stuck_situation()
        else:
            # 位置有變化，重置卡住計時器
            self.stuck_timer = 0
            self.last_position = current_pos

    def _handle_stuck_situation(self):
        """
        處理 NPC 卡住的情況\n
        """
        print(f"NPC {self.npc.name} 卡住了，重新規劃路徑")
        
        # 清除當前路徑
        self.path_waypoints.clear()
        self.current_waypoint_index = 0
        
        # 嘗試找到新的目標位置
        self._find_alternative_target()
        
        # 重置卡住計時器
        self.stuck_timer = 0

    def _update_target_movement(self, dt):
        """
        更新目標導向移動\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        if not self.path_waypoints:
            # 沒有路徑，直接朝目標移動
            self._move_directly_to_target()
        else:
            # 沿路徑移動
            self._follow_path()

    def _move_directly_to_target(self):
        """
        直接朝目標移動\n
        """
        if not self.target_position:
            return
        
        # 計算到目標的方向
        dx = self.target_position[0] - self.npc.x
        dy = self.target_position[1] - self.npc.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < self.waypoint_reached_distance:
            # 到達目標
            self._reach_target()
            return
        
        # 正規化方向向量
        self.movement_direction = (dx / distance, dy / distance)
        self.is_moving = True

    def _follow_path(self):
        """
        沿路徑移動\n
        """
        if self.current_waypoint_index >= len(self.path_waypoints):
            # 路徑完成
            self._reach_target()
            return
        
        current_waypoint = self.path_waypoints[self.current_waypoint_index]
        
        # 計算到當前路點的方向
        dx = current_waypoint[0] - self.npc.x
        dy = current_waypoint[1] - self.npc.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < self.waypoint_reached_distance:
            # 到達當前路點，移動到下一個
            self.current_waypoint_index += 1
            return
        
        # 正規化方向向量
        self.movement_direction = (dx / distance, dy / distance)
        self.is_moving = True

    def _update_wander_movement(self, dt):
        """
        更新遊走移動\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        self.last_wander_change += dt
        
        if self.last_wander_change >= self.wander_change_interval:
            self._set_random_wander_target()
            self.last_wander_change = 0

    def _apply_movement(self, dt):
        """
        應用移動到 NPC 位置\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        if not self.is_moving:
            return
        
        # 計算移動距離
        move_distance = self.current_speed * dt
        
        # 計算新位置
        new_x = self.npc.x + self.movement_direction[0] * move_distance
        new_y = self.npc.y + self.movement_direction[1] * move_distance
        
        # 檢查碰撞
        if self._can_move_to(new_x, new_y):
            self.npc.x = new_x
            self.npc.y = new_y
        else:
            # 碰撞處理
            self._handle_collision()

    def _can_move_to(self, x, y):
        """
        檢查是否可以移動到指定位置\n
        \n
        參數:\n
        x (float): 目標 X 座標\n
        y (float): 目標 Y 座標\n
        \n
        回傳:\n
        bool: 是否可以移動\n
        """
        # 檢查地圖邊界
        if x < 0 or y < 0:
            return False
        
        # 檢查建築物碰撞
        if hasattr(self.npc, 'buildings') and self.npc.buildings:
            npc_rect = pygame.Rect(x - self.npc.size//2, y - self.npc.size//2, 
                                  self.npc.size, self.npc.size)
            
            for building in self.npc.buildings:
                building_rect = pygame.Rect(
                    building["x"], building["y"], 
                    building["width"], building["height"]
                )
                if npc_rect.colliderect(building_rect):
                    return False
        
        # 檢查格子地圖限制
        if hasattr(self.npc, 'tile_map') and self.npc.tile_map:
            return self.npc.tile_map.is_walkable(x, y)
        
        return True

    def _handle_collision(self):
        """
        處理移動碰撞\n
        """
        # 嘗試繞過障礙物
        self._try_avoidance_movement()

    def _try_avoidance_movement(self):
        """
        嘗試避開障礙物的移動\n
        """
        # 嘗試幾個不同的方向
        avoidance_angles = [-45, 45, -90, 90, 180]  # 度數
        
        for angle_offset in avoidance_angles:
            # 計算新方向
            current_angle = math.atan2(self.movement_direction[1], self.movement_direction[0])
            new_angle = current_angle + math.radians(angle_offset)
            
            new_direction = (math.cos(new_angle), math.sin(new_angle))
            
            # 測試這個方向
            test_distance = 10  # 測試距離
            test_x = self.npc.x + new_direction[0] * test_distance
            test_y = self.npc.y + new_direction[1] * test_distance
            
            if self._can_move_to(test_x, test_y):
                self.movement_direction = new_direction
                return
        
        # 所有方向都被阻擋，停止移動
        self.is_moving = False

    def set_target(self, target_position):
        """
        設定移動目標\n
        \n
        參數:\n
        target_position (tuple): 目標位置 (x, y)\n
        """
        self.target_position = target_position
        self.path_waypoints.clear()
        self.current_waypoint_index = 0
        
        # 重置卡住檢測
        self.stuck_timer = 0

    def set_path(self, waypoints):
        """
        設定移動路徑\n
        \n
        參數:\n
        waypoints (list): 路點列表 [(x, y), ...]\n
        """
        self.path_waypoints = waypoints.copy()
        self.current_waypoint_index = 0
        
        if waypoints:
            self.target_position = waypoints[-1]  # 最後一個點作為最終目標

    def _reach_target(self):
        """
        到達目標位置\n
        """
        self.target_position = None
        self.path_waypoints.clear()
        self.current_waypoint_index = 0
        self.is_moving = False
        
        print(f"NPC {self.npc.name} 到達目標位置")

    def _set_random_wander_target(self):
        """
        設定隨機遊走目標\n
        """
        # 在當前位置周圍隨機選擇一個點
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(self.wander_radius * 0.3, self.wander_radius)
        
        target_x = self.npc.x + distance * math.cos(angle)
        target_y = self.npc.y + distance * math.sin(angle)
        
        # 確保目標在有效範圍內
        if self._can_move_to(target_x, target_y):
            self.set_target((target_x, target_y))

    def _find_alternative_target(self):
        """
        尋找替代目標位置\n
        """
        # 嘗試在附近找到一個可達的位置
        for _ in range(10):  # 最多嘗試 10 次
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(20, 50)
            
            alt_x = self.npc.x + distance * math.cos(angle)
            alt_y = self.npc.y + distance * math.sin(angle)
            
            if self._can_move_to(alt_x, alt_y):
                self.set_target((alt_x, alt_y))
                return
        
        # 如果找不到替代位置，就停止移動
        self.stop_movement()

    def stop_movement(self):
        """
        停止移動\n
        """
        self.target_position = None
        self.path_waypoints.clear()
        self.current_waypoint_index = 0
        self.is_moving = False
        self.movement_direction = (0, 0)

    def get_movement_info(self):
        """
        獲取移動狀態資訊\n
        \n
        回傳:\n
        dict: 移動狀態資訊\n
        """
        return {
            "is_moving": self.is_moving,
            "target_position": self.target_position,
            "current_speed": self.current_speed,
            "movement_direction": self.movement_direction,
            "stuck_timer": round(self.stuck_timer, 2),
            "waypoints_count": len(self.path_waypoints),
            "current_waypoint": self.current_waypoint_index
        }