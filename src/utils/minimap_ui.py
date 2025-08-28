######################載入套件######################
import pygame
import math
from config.settings import *


######################小地圖UI類別######################
class MinimapUI:
    """
    小地圖UI - 提供小地圖顯示和操作功能\n
    \n
    小地圖可以顯示玩家位置、建築物和地形\n
    支援中鍵滾動縮放功能\n
    玩家在小地圖上以等腰三角形表示，頂點朝向玩家面向方向\n
    """

    def __init__(self):
        """
        初始化小地圖UI\n
        """
        # 小地圖基本屬性
        self.is_visible = True  # 小地圖預設顯示（依據需求）
        self.zoom_level = MINIMAP_DEFAULT_ZOOM  # 當前縮放等級
        
        # 小地圖表面
        self.minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA)
        
        # 視窗中心位置 (用於縮放時的固定點)
        self.center_x = 0
        self.center_y = 0
        
        # 小地圖偏移 (用於平移)
        self.offset_x = 0
        self.offset_y = 0
        
        print("小地圖UI初始化完成")

    def toggle_visibility(self):
        """
        切換小地圖顯示狀態\n
        \n
        回傳:\n
        bool: 切換後的顯示狀態\n
        """
        self.is_visible = not self.is_visible
        print(f"小地圖{'顯示' if self.is_visible else '隱藏'}")
        return self.is_visible

    def handle_scroll(self, scroll_direction):
        """
        處理中鍵滾動事件 - 縮放功能已禁用\n
        \n
        參數:\n
        scroll_direction (int): 滾動方向，正數為向上滾動，負數為向下滾動\n
        """
        # 根據需求，縮放功能已被移除
        print("小地圖縮放功能已禁用")

    def world_to_minimap(self, world_x, world_y):
        """
        將世界座標轉換為小地圖座標\n
        \n
        參數:\n
        world_x (float): 世界座標 X\n
        world_y (float): 世界座標 Y\n
        \n
        回傳:\n
        tuple: (minimap_x, minimap_y) 小地圖座標\n
        """
        # 計算相對於小地圖中心的位置
        map_x = (world_x - self.center_x) * self.zoom_level + MINIMAP_WIDTH // 2 + self.offset_x
        map_y = (world_y - self.center_y) * self.zoom_level + MINIMAP_HEIGHT // 2 + self.offset_y
        
        return (int(map_x), int(map_y))

    def draw_player_triangle(self, surface, map_x, map_y, facing_direction):
        """
        在小地圖上繪製等腰三角形表示玩家\n
        \n
        參數:\n
        surface (pygame.Surface): 繪製表面\n
        map_x (int): 小地圖 X 座標\n
        map_y (int): 小地圖 Y 座標\n
        facing_direction (str): 玩家面朝方向 ("up", "down", "left", "right")\n
        """
        size = MINIMAP_PLAYER_SIZE
        
        # 根據面朝方向計算三角形的三個頂點
        if facing_direction == "up":
            # 頂點朝上
            points = [
                (map_x, map_y - size),      # 頂點
                (map_x - size//2, map_y + size//2),  # 左下
                (map_x + size//2, map_y + size//2)   # 右下
            ]
        elif facing_direction == "down":
            # 頂點朝下
            points = [
                (map_x, map_y + size),      # 頂點
                (map_x - size//2, map_y - size//2),  # 左上
                (map_x + size//2, map_y - size//2)   # 右上
            ]
        elif facing_direction == "left":
            # 頂點朝左
            points = [
                (map_x - size, map_y),      # 頂點
                (map_x + size//2, map_y - size//2),  # 右上
                (map_x + size//2, map_y + size//2)   # 右下
            ]
        elif facing_direction == "right":
            # 頂點朝右
            points = [
                (map_x + size, map_y),      # 頂點
                (map_x - size//2, map_y - size//2),  # 左上
                (map_x - size//2, map_y + size//2)   # 左下
            ]
        else:
            # 預設朝下
            points = [
                (map_x, map_y + size),
                (map_x - size//2, map_y - size//2),
                (map_x + size//2, map_y - size//2)
            ]
        
        # 繪製三角形
        pygame.draw.polygon(surface, MINIMAP_PLAYER_COLOR, points)

    def draw_buildings(self, surface, buildings, player_x, player_y):
        """
        在小地圖上繪製建築物\n
        \n
        參數:\n
        surface (pygame.Surface): 繪製表面\n
        buildings (list): 建築物列表\n
        player_x (float): 玩家世界座標 X\n
        player_y (float): 玩家世界座標 Y\n
        """
        # 設定小地圖中心為玩家位置
        self.center_x = player_x
        self.center_y = player_y
        
        for building in buildings:
            # 將建築物世界座標轉換為小地圖座標
            map_x, map_y = self.world_to_minimap(building.x, building.y)
            
            # 檢查建築物是否在小地圖範圍內
            if 0 <= map_x < MINIMAP_WIDTH and 0 <= map_y < MINIMAP_HEIGHT:
                # 計算建築物在小地圖上的大小
                building_size = max(2, int(min(building.width, building.height) * self.zoom_level * 0.1))
                
                # 根據建築類型選擇顏色
                if hasattr(building, 'building_type'):
                    if building.building_type == "hospital":
                        color = (255, 255, 255)  # 白色 - 醫院
                    elif building.building_type == "gun_shop":
                        color = (139, 69, 19)    # 棕色 - 槍械店
                    elif building.building_type == "church":
                        color = (128, 0, 128)    # 紫色 - 教堂
                    elif building.building_type == "convenience_store":
                        color = (255, 215, 0)    # 金色 - 便利商店
                    else:
                        color = (100, 100, 100)  # 灰色 - 其他建築
                else:
                    color = (100, 100, 100)      # 預設灰色
                
                # 繪製建築物為小方塊
                pygame.draw.rect(surface, color, 
                    (map_x - building_size//2, map_y - building_size//2, 
                     building_size, building_size))

    def draw_terrain(self, surface, terrain_data, player_x, player_y):
        """
        在小地圖上繪製地形\n
        \n
        參數:\n
        surface (pygame.Surface): 繪製表面\n
        terrain_data (list): 地形資料 (二維陣列)\n
        player_x (float): 玩家世界座標 X\n
        player_y (float): 玩家世界座標 Y\n
        """
        if not terrain_data:
            return
            
        # 設定小地圖中心為玩家位置
        self.center_x = player_x
        self.center_y = player_y
        
        # 計算要繪製的地形範圍
        terrain_width = len(terrain_data[0]) if terrain_data else 0
        terrain_height = len(terrain_data)
        
        # 假設每個地形格子的大小 - 與 TerrainBasedSystem 的 tile_size 匹配
        terrain_cell_size = 40  # 與 TerrainBasedSystem 保持一致
        
        for row in range(terrain_height):
            for col in range(terrain_width):
                # 計算地形格子的世界座標
                world_x = col * terrain_cell_size
                world_y = row * terrain_cell_size
                
                # 轉換為小地圖座標
                map_x, map_y = self.world_to_minimap(world_x, world_y)
                
                # 檢查是否在小地圖範圍內
                if 0 <= map_x < MINIMAP_WIDTH and 0 <= map_y < MINIMAP_HEIGHT:
                    terrain_type = terrain_data[row][col]
                    
                    # 根據地形類型選擇顏色
                    if terrain_type == 0:  # 草地
                        color = (34, 139, 34)
                    elif terrain_type == 1:  # 森林
                        color = (0, 100, 0)
                    elif terrain_type == 2:  # 水面
                        color = (0, 191, 255)
                    elif terrain_type == 3:  # 道路
                        color = (105, 105, 105)
                    elif terrain_type == 4:  # 高速公路
                        color = (64, 64, 64)
                    elif terrain_type >= 5:  # 建築區域
                        color = (139, 69, 19)
                    else:
                        color = (100, 100, 100)  # 預設
                    
                    # 計算在小地圖上的大小
                    cell_size = max(1, int(terrain_cell_size * self.zoom_level * 0.1))
                    
                    # 繪製地形格子
                    pygame.draw.rect(surface, color, 
                        (map_x - cell_size//2, map_y - cell_size//2, 
                         cell_size, cell_size))

    def draw(self, screen, player_x, player_y, facing_direction, buildings=None, terrain_data=None):
        """
        繪製小地圖\n
        \n
        參數:\n
        screen (pygame.Surface): 主螢幕表面\n
        player_x (float): 玩家世界座標 X\n
        player_y (float): 玩家世界座標 Y\n
        facing_direction (str): 玩家面朝方向\n
        buildings (list): 建築物列表，可選\n
        terrain_data (list): 地形資料，可選\n
        """
        if not self.is_visible:
            return
        
        # 清空小地圖表面
        self.minimap_surface.fill(MINIMAP_BACKGROUND_COLOR)
        
        # 繪製地形 (最底層)
        if terrain_data:
            self.draw_terrain(self.minimap_surface, terrain_data, player_x, player_y)
        
        # 繪製建築物 (中間層)
        if buildings:
            self.draw_buildings(self.minimap_surface, buildings, player_x, player_y)
        
        # 繪製玩家 (最上層)
        player_map_x = MINIMAP_WIDTH // 2  # 玩家總是在小地圖中心
        player_map_y = MINIMAP_HEIGHT // 2
        self.draw_player_triangle(self.minimap_surface, player_map_x, player_map_y, facing_direction)
        
        # 繪製小地圖邊框
        pygame.draw.rect(self.minimap_surface, MINIMAP_BORDER_COLOR, 
                        (0, 0, MINIMAP_WIDTH, MINIMAP_HEIGHT), 2)
        
        # 將小地圖繪製到主螢幕
        screen.blit(self.minimap_surface, (MINIMAP_X, MINIMAP_Y))
        
        # 繪製縮放等級資訊
        self._draw_zoom_info(screen)

    def _draw_zoom_info(self, screen):
        """
        繪製縮放等級資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 主螢幕表面\n
        """
        font = pygame.font.Font(None, 20)
        zoom_text = f"縮放: {self.zoom_level:.1f}x"
        text_surface = font.render(zoom_text, True, (255, 255, 255))
        
        # 顯示在小地圖下方
        text_x = MINIMAP_X
        text_y = MINIMAP_Y + MINIMAP_HEIGHT + 5
        screen.blit(text_surface, (text_x, text_y))

    def reset_zoom(self):
        """
        重置縮放等級為預設值\n
        """
        self.zoom_level = MINIMAP_DEFAULT_ZOOM
        self.offset_x = 0
        self.offset_y = 0
        print("小地圖縮放等級已重置")

    def get_zoom_level(self):
        """
        獲取當前縮放等級\n
        \n
        回傳:\n
        float: 當前縮放等級\n
        """
        return self.zoom_level

    def set_zoom_level(self, zoom):
        """
        設定縮放等級\n
        \n
        參數:\n
        zoom (float): 要設定的縮放等級\n
        """
        self.zoom_level = max(MINIMAP_MIN_ZOOM, min(MINIMAP_MAX_ZOOM, zoom))

    def handle_mouse_input(self, event):
        """
        處理滑鼠輸入事件\n
        \n
        處理中鍵點擊切換顯示和滾輪縮放功能\n
        \n
        參數:\n
        event (pygame.event.Event): 滑鼠事件\n
        \n
        回傳:\n
        bool: 事件是否被處理\n
        """
        # 處理中鍵點擊切換小地圖顯示
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:  # 滑鼠中鍵
                self.toggle_visibility()
                return True
        
        # 處理滾輪縮放（只有在小地圖顯示時才處理）
        elif event.type == pygame.MOUSEWHEEL and self.is_visible:
            # 向上滾動放大，向下滾動縮小
            scroll_direction = event.y
            self.handle_scroll(scroll_direction)
            return True
        
        return False