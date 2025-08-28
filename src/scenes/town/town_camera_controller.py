######################載入套件######################
import pygame
from config.settings import *


######################小鎮攝影機控制器######################
class TownCameraController:
    """
    小鎮場景攝影機控制器 - 管理攝影機跟隨和邊界限制\n
    \n
    負責：\n
    1. 攝影機跟隨玩家移動\n
    2. 地圖邊界限制\n
    3. 平滑跟隨效果\n
    4. 視野範圍計算\n
    """

    def __init__(self, map_width, map_height):
        """
        初始化攝影機控制器\n
        \n
        參數:\n
        map_width (int): 地圖總寬度\n
        map_height (int): 地圖總高度\n
        """
        self.camera_x = 0
        self.camera_y = 0
        
        # 地圖邊界
        self.map_width = map_width
        self.map_height = map_height
        
        # 攝影機跟隨設定
        self.follow_speed = 0.1  # 跟隨速度 (0.0 到 1.0)
        self.dead_zone_x = 100   # X軸死區大小
        self.dead_zone_y = 100   # Y軸死區大小
        
        print("小鎮攝影機控制器初始化完成")

    def update(self, player):
        """
        更新攝影機位置，跟隨玩家\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        # 計算玩家在螢幕上的位置
        player_screen_x = player.x - self.camera_x
        player_screen_y = player.y - self.camera_y
        
        # 計算螢幕中心位置
        screen_center_x = SCREEN_WIDTH // 2
        screen_center_y = SCREEN_HEIGHT // 2
        
        # 計算玩家與螢幕中心的距離
        offset_x = player_screen_x - screen_center_x
        offset_y = player_screen_y - screen_center_y
        
        # 只有當玩家離開死區時才移動攝影機
        if abs(offset_x) > self.dead_zone_x:
            # 計算目標攝影機位置
            target_camera_x = player.x - screen_center_x
            # 平滑跟隨
            self.camera_x += (target_camera_x - self.camera_x) * self.follow_speed
        
        if abs(offset_y) > self.dead_zone_y:
            # 計算目標攝影機位置
            target_camera_y = player.y - screen_center_y
            # 平滑跟隨
            self.camera_y += (target_camera_y - self.camera_y) * self.follow_speed
        
        # 限制攝影機不超出地圖邊界
        self._constrain_to_map_bounds()

    def _constrain_to_map_bounds(self):
        """
        限制攝影機位置在地圖邊界內\n
        """
        # 限制 X 軸邊界
        self.camera_x = max(0, min(self.camera_x, self.map_width - SCREEN_WIDTH))
        
        # 限制 Y 軸邊界
        self.camera_y = max(0, min(self.camera_y, self.map_height - SCREEN_HEIGHT))

    def get_visible_rect(self):
        """
        獲取當前可見區域的矩形\n
        \n
        回傳:\n
        pygame.Rect: 可見區域矩形\n
        """
        return pygame.Rect(
            self.camera_x, 
            self.camera_y, 
            SCREEN_WIDTH, 
            SCREEN_HEIGHT
        )

    def world_to_screen(self, world_x, world_y):
        """
        將世界座標轉換為螢幕座標\n
        \n
        參數:\n
        world_x (float): 世界 X 座標\n
        world_y (float): 世界 Y 座標\n
        \n
        回傳:\n
        tuple: (screen_x, screen_y) 螢幕座標\n
        """
        screen_x = world_x - self.camera_x
        screen_y = world_y - self.camera_y
        return (screen_x, screen_y)

    def screen_to_world(self, screen_x, screen_y):
        """
        將螢幕座標轉換為世界座標\n
        \n
        參數:\n
        screen_x (float): 螢幕 X 座標\n
        screen_y (float): 螢幕 Y 座標\n
        \n
        回傳:\n
        tuple: (world_x, world_y) 世界座標\n
        """
        world_x = screen_x + self.camera_x
        world_y = screen_y + self.camera_y
        return (world_x, world_y)

    def is_in_view(self, world_x, world_y, width=0, height=0):
        """
        檢查物體是否在攝影機視野內\n
        \n
        參數:\n
        world_x (float): 物體世界 X 座標\n
        world_y (float): 物體世界 Y 座標\n
        width (float): 物體寬度（可選）\n
        height (float): 物體高度（可選）\n
        \n
        回傳:\n
        bool: 是否在視野內\n
        """
        # 加上一定的邊界緩衝，避免物體在邊緣突然出現/消失
        margin = 50
        
        visible_left = self.camera_x - margin
        visible_right = self.camera_x + SCREEN_WIDTH + margin
        visible_top = self.camera_y - margin
        visible_bottom = self.camera_y + SCREEN_HEIGHT + margin
        
        # 檢查物體是否與可見區域重疊
        object_left = world_x
        object_right = world_x + width
        object_top = world_y
        object_bottom = world_y + height
        
        return (object_right > visible_left and 
                object_left < visible_right and 
                object_bottom > visible_top and 
                object_top < visible_bottom)

    def set_position(self, x, y):
        """
        直接設定攝影機位置\n
        \n
        參數:\n
        x (float): 攝影機 X 位置\n
        y (float): 攝影機 Y 位置\n
        """
        self.camera_x = x
        self.camera_y = y
        self._constrain_to_map_bounds()

    def center_on_player(self, player):
        """
        立即將攝影機置中到玩家位置\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        self.camera_x = player.x - SCREEN_WIDTH // 2
        self.camera_y = player.y - SCREEN_HEIGHT // 2
        self._constrain_to_map_bounds()

    def get_debug_info(self):
        """
        獲取攝影機除錯資訊\n
        \n
        回傳:\n
        dict: 攝影機狀態資訊\n
        """
        return {
            "camera_x": round(self.camera_x, 2),
            "camera_y": round(self.camera_y, 2),
            "map_width": self.map_width,
            "map_height": self.map_height,
            "visible_area": f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}"
        }