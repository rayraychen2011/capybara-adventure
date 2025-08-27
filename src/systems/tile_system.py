from enum import Enum
import heapq
import math
from config.settings import TOWN_TOTAL_WIDTH, TOWN_TOTAL_HEIGHT, TOWN_GRID_WIDTH, TOWN_GRID_HEIGHT, BLOCK_SIZE, STREET_WIDTH

######################列舉類別######################

class TileType(Enum):
    """
    格子類型列舉 - 定義地圖上每個格子的類型\n
    
    這個系統是實現 NPC 移動限制和建築放置規範的核心\n
    每個格子都有明確的類型，用於路徑搜尋和碰撞檢測\n
    """
    GRASS = "grass"           # 草地 - 預設地形
    ROAD = "road"             # 車道/馬路 - NPC 不能行走，建築不能放置
    SIDEWALK = "sidewalk"     # 人行道 - NPC 可以行走，建築不能放置
    CROSSWALK = "crosswalk"   # 斑馬線 - NPC 可以行走穿越馬路
    BUILDING = "building"     # 建築 - 已建造的區域
    BUILDABLE = "buildable"   # 可建造區域 - 街區內可放建築的地方


######################格子資料類別######################
class Tile:
    """
    單個格子的資料類別\n
    
    儲存格子的類型和其他相關資訊\n
    """
    
    def __init__(self, x, y, tile_type=TileType.GRASS):
        self.x = x                    # 格子 X 座標
        self.y = y                    # 格子 Y 座標
        self.tile_type = tile_type    # 格子類型


######################格子地圖管理器######################
class TileMapManager:
    """
    格子地圖管理器 - 管理整個遊戲世界的格子地圖\n
    
    這個類別負責:\n
    1. 創建和管理格子地圖\n
    2. 提供座標轉換功能（世界座標 ↔ 格子座標）\n
    3. 檢查建築放置是否可行\n
    4. 提供 NPC 路徑搜尋功能\n
    5. 生成小鎮街道佈局\n
    """
    
    def __init__(self, world_width=TOWN_TOTAL_WIDTH, world_height=TOWN_TOTAL_HEIGHT, grid_size=20):
        # 世界尺寸
        self.world_width = world_width
        self.world_height = world_height
        
        # 格子設定
        self.grid_size = grid_size  # 每個格子的大小（像素）
        self.tile_size = grid_size  # 為了向後兼容性
        self.grid_width = world_width // grid_size
        self.grid_height = world_height // grid_size
        
        # 初始化格子地圖
        self.grid = []
        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                tile = Tile(x, y, TileType.GRASS)
                row.append(tile)
            self.grid.append(row)
        
        print(f"格子地圖已創建: {self.grid_width}x{self.grid_height} 格子")
    
    def world_to_grid(self, world_x, world_y):
        """
        將世界座標轉換為格子座標\n
        
        參數:\n
        world_x (float): 世界 X 座標\n
        world_y (float): 世界 Y 座標\n
        
        回傳:\n
        tuple: (grid_x, grid_y) 格子座標\n
        """
        grid_x = int(world_x // self.grid_size)
        grid_y = int(world_y // self.grid_size)
        return grid_x, grid_y
    
    def grid_to_world(self, grid_x, grid_y):
        """
        將格子座標轉換為世界座標（格子中心點）\n
        
        參數:\n
        grid_x (int): 格子 X 座標\n
        grid_y (int): 格子 Y 座標\n
        
        回傳:\n
        tuple: (world_x, world_y) 世界座標\n
        """
        world_x = grid_x * self.grid_size + self.grid_size // 2
        world_y = grid_y * self.grid_size + self.grid_size // 2
        return world_x, world_y
    
    def is_valid_grid_position(self, grid_x, grid_y):
        """
        檢查格子座標是否在有效範圍內\n
        
        參數:\n
        grid_x (int): 格子 X 座標\n
        grid_y (int): 格子 Y 座標\n
        
        回傳:\n
        bool: 是否有效\n
        """
        return 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height
    
    def get_tile(self, grid_x, grid_y):
        """
        獲取指定格子的資料\n
        
        參數:\n
        grid_x (int): 格子 X 座標\n
        grid_y (int): 格子 Y 座標\n
        
        回傳:\n
        Tile or None: 格子資料，如果座標無效則回傳 None\n
        """
        if self.is_valid_grid_position(grid_x, grid_y):
            return self.grid[grid_y][grid_x]
        return None
    
    def set_tile_type(self, grid_x, grid_y, tile_type):
        """
        設定指定格子的類型\n
        
        參數:\n
        grid_x (int): 格子 X 座標\n
        grid_y (int): 格子 Y 座標\n
        tile_type (TileType): 新的格子類型\n
        """
        if self.is_valid_grid_position(grid_x, grid_y):
            self.grid[grid_y][grid_x].tile_type = tile_type
    
    def can_place_building(self, world_x, world_y, width, height):
        """
        檢查是否可以在指定位置放置建築\n
        
        參數:\n
        world_x (float): 建築左上角世界 X 座標\n
        world_y (float): 建築左上角世界 Y 座標\n
        width (float): 建築寬度\n
        height (float): 建築高度\n
        
        回傳:\n
        tuple: (bool, str) - (是否可以放置, 錯誤信息)\n
        """
        # 計算建築覆蓋的格子範圍
        start_grid_x, start_grid_y = self.world_to_grid(world_x, world_y)
        end_grid_x, end_grid_y = self.world_to_grid(world_x + width - 1, world_y + height - 1)
        
        # 檢查範圍內的每個格子
        for grid_y in range(start_grid_y, end_grid_y + 1):
            for grid_x in range(start_grid_x, end_grid_x + 1):
                tile = self.get_tile(grid_x, grid_y)
                if not tile:
                    error_msg = f"建築放置失敗: 格子 ({grid_x}, {grid_y}) 超出地圖邊界"
                    print(error_msg)
                    return False, error_msg
                
                # 只有可建造區域（BUILDABLE）才能放置建築
                if tile.tile_type != TileType.BUILDABLE:
                    if tile.tile_type == TileType.ROAD:
                        error_msg = f"無法放置建築：位置被馬路阻擋"
                    elif tile.tile_type == TileType.SIDEWALK:
                        error_msg = f"無法放置建築：位置被人行道阻擋"
                    elif tile.tile_type == TileType.CROSSWALK:
                        error_msg = f"無法放置建築：位置被斑馬線阻擋"
                    elif tile.tile_type == TileType.BUILDING:
                        error_msg = f"無法放置建築：位置已有建築"
                    else:
                        error_msg = f"無法放置建築：位置不適合建築 (類型: {tile.tile_type.value})"
                    
                    print(error_msg)
                    return False, error_msg
        
        return True, ""
    
    def place_building(self, world_x, world_y, width, height):
        """
        在指定位置放置建築（標記為建築類型）\n
        
        參數:\n
        world_x (float): 建築左上角世界 X 座標\n
        world_y (float): 建築左上角世界 Y 座標\n
        width (float): 建築寬度\n
        height (float): 建築高度\n
        
        回傳:\n
        bool: 是否成功放置\n
        """
        can_place, error_msg = self.can_place_building(world_x, world_y, width, height)
        if can_place:
            # 計算建築覆蓋的格子範圍
            start_grid_x, start_grid_y = self.world_to_grid(world_x, world_y)
            end_grid_x, end_grid_y = self.world_to_grid(world_x + width - 1, world_y + height - 1)
            
            # 標記所有格子為建築
            for grid_y in range(start_grid_y, end_grid_y + 1):
                for grid_x in range(start_grid_x, end_grid_x + 1):
                    self.set_tile_type(grid_x, grid_y, TileType.BUILDING)
            
            return True
        
        return False
    
    def create_town_layout(self, town_bounds):
        """
        創建小鎮的街道和人行道佈局\n
        
        參數:\n
        town_bounds (tuple): (x, y, width, height) 小鎮邊界\n
        """
        town_x, town_y, town_width, town_height = town_bounds
        
        # 街區配置 - 從 settings.py 獲取
        block_size = BLOCK_SIZE  # 150
        street_width = STREET_WIDTH  # 50
        
        # 計算可以容納多少個街區
        blocks_x = town_width // (block_size + street_width)
        blocks_y = town_height // (block_size + street_width)
        
        print(f"創建 {blocks_x}x{blocks_y} 街區佈局，街區大小 {block_size}x{block_size}，街道寬度 {street_width}")
        
        # 先將整個區域設為草地
        start_grid_x, start_grid_y = self.world_to_grid(town_x, town_y)
        end_grid_x, end_grid_y = self.world_to_grid(town_x + town_width, town_y + town_height)
        
        for grid_y in range(start_grid_y, end_grid_y + 1):
            for grid_x in range(start_grid_x, end_grid_x + 1):
                self.set_tile_type(grid_x, grid_y, TileType.GRASS)
        
        # 2. 先標記所有街區為可建造區域
        self._mark_buildable_blocks(town_bounds, blocks_x, blocks_y, block_size, street_width)
        
        # 3. 創建街道網格（只在非街區區域）
        self._create_street_grid(town_bounds, blocks_x, blocks_y, block_size, street_width)
        
        # 4. 創建路口斑馬線
        self._create_crosswalks_simple(town_bounds, blocks_x, blocks_y, block_size, street_width)
        
        # 5. 最終確認：再次標記街區為可建造區域（確保街道不覆蓋街區）
        self._mark_buildable_blocks(town_bounds, blocks_x, blocks_y, block_size, street_width)
        
        print("小鎮街道和人行道佈局創建完成")
    
    def _create_street_grid(self, town_bounds, blocks_x, blocks_y, block_size, street_width):
        """創建街道網格，確保不覆蓋街區"""
        town_x, town_y, town_width, town_height = town_bounds
        
        # 創建水平街道
        for row in range(blocks_y + 1):
            street_y = town_y + row * (block_size + street_width)
            self._create_simple_horizontal_street(town_x, street_y, town_width, street_width)
        
        # 創建垂直街道
        for col in range(blocks_x + 1):
            street_x = town_x + col * (block_size + street_width)
            self._create_simple_vertical_street(street_x, town_y, street_width, town_height)
    
    def _create_simple_horizontal_street(self, start_x, start_y, length, width):
        """創建簡單的水平街道"""
        # 街道中央是馬路
        road_start_y = start_y + width // 4
        road_end_y = start_y + 3 * width // 4
        
        for y in range(start_y, start_y + width):
            for x in range(start_x, start_x + length):
                grid_x, grid_y = self.world_to_grid(x, y)
                if self.is_valid_grid_position(grid_x, grid_y):
                    if road_start_y <= y < road_end_y:
                        self.set_tile_type(grid_x, grid_y, TileType.ROAD)
                    else:
                        self.set_tile_type(grid_x, grid_y, TileType.SIDEWALK)
    
    def _create_simple_vertical_street(self, start_x, start_y, width, length):
        """創建簡單的垂直街道"""
        # 街道中央是馬路
        road_start_x = start_x + width // 4
        road_end_x = start_x + 3 * width // 4
        
        for x in range(start_x, start_x + width):
            for y in range(start_y, start_y + length):
                grid_x, grid_y = self.world_to_grid(x, y)
                if self.is_valid_grid_position(grid_x, grid_y):
                    if road_start_x <= x < road_end_x:
                        self.set_tile_type(grid_x, grid_y, TileType.ROAD)
                    else:
                        self.set_tile_type(grid_x, grid_y, TileType.SIDEWALK)
    
    def _create_crosswalks_simple(self, town_bounds, blocks_x, blocks_y, block_size, street_width):
        """創建簡單的路口斑馬線"""
        town_x, town_y, town_width, town_height = town_bounds
        
        # 在每個路口創建斑馬線
        for row in range(1, blocks_y + 1):
            for col in range(1, blocks_x + 1):
                intersection_x = town_x + col * (block_size + street_width) - street_width // 2
                intersection_y = town_y + row * (block_size + street_width) - street_width // 2
                
                # 創建小範圍的斑馬線
                crosswalk_size = street_width // 2
                start_grid_x, start_grid_y = self.world_to_grid(intersection_x, intersection_y)
                end_grid_x, end_grid_y = self.world_to_grid(intersection_x + crosswalk_size, intersection_y + crosswalk_size)
                
                for grid_y in range(start_grid_y, end_grid_y + 1):
                    for grid_x in range(start_grid_x, end_grid_x + 1):
                        if self.is_valid_grid_position(grid_x, grid_y):
                            tile = self.get_tile(grid_x, grid_y)
                            if tile and tile.tile_type == TileType.ROAD:
                                self.set_tile_type(grid_x, grid_y, TileType.CROSSWALK)
    
    def _mark_buildable_blocks(self, town_bounds, blocks_x, blocks_y, block_size, street_width):
        """標記街區為可建造區域"""
        town_x, town_y, town_width, town_height = town_bounds
        
        print(f"標記街區邊界 - 小鎮: ({town_x}, {town_y}, {town_width}, {town_height})")
        print(f"街區配置: {blocks_x}x{blocks_y}, 街區大小: {block_size}, 街道寬度: {street_width}")
        
        for row in range(blocks_y):
            for col in range(blocks_x):
                # 街區座標：每個街區都在街道網格之間
                block_x = town_x + col * (block_size + street_width)
                block_y = town_y + row * (block_size + street_width)
                
                if row == 0 and col == 0:  # 只輸出第一個街區的詳細信息
                    print(f"第一個街區 (0,0): 世界座標 ({block_x}, {block_y}) -> ({block_x + block_size}, {block_y + block_size})")
                
                # 標記街區內部為可建造
                start_grid_x, start_grid_y = self.world_to_grid(block_x, block_y)
                end_grid_x, end_grid_y = self.world_to_grid(block_x + block_size - 1, block_y + block_size - 1)
                
                if row == 0 and col == 0:  # 只輸出第一個街區的詳細信息
                    print(f"第一個街區 (0,0): 格子座標 ({start_grid_x}, {start_grid_y}) -> ({end_grid_x}, {end_grid_y})")
                
                # 確保範圍在地圖邊界內
                start_grid_x = max(0, start_grid_x)
                start_grid_y = max(0, start_grid_y)
                end_grid_x = min(self.grid_width - 1, end_grid_x)
                end_grid_y = min(self.grid_height - 1, end_grid_y)
                
                for grid_y in range(start_grid_y, end_grid_y + 1):
                    for grid_x in range(start_grid_x, end_grid_x + 1):
                        # 強制將街區內部設為可建造，不管之前是什麼類型
                        # 這樣可以確保街區內部不被街道或人行道覆蓋
                        tile = self.get_tile(grid_x, grid_y)
                        if tile:
                            self.set_tile_type(grid_x, grid_y, TileType.BUILDABLE)
    
    def find_path_for_npc(self, start_pos, end_pos):
        """
        為 NPC 尋找路徑，只使用人行道和斑馬線\n
        
        使用簡化的 A* 算法，限制只能在 SIDEWALK 和 CROSSWALK 上移動\n
        
        參數:\n
        start_pos (tuple): 起始位置 (world_x, world_y)\n
        end_pos (tuple): 目標位置 (world_x, world_y)\n
        
        回傳:\n
        list: 路徑點列表 [(world_x, world_y), ...] 如果找不到路徑則回傳 []\n
        """
        # 轉換為格子座標
        start_grid = self.world_to_grid(start_pos[0], start_pos[1])
        end_grid = self.world_to_grid(end_pos[0], end_pos[1])
        
        # 檢查起點和終點是否有效
        start_tile = self.get_tile(start_grid[0], start_grid[1])
        end_tile = self.get_tile(end_grid[0], end_grid[1])
        
        if not start_tile or not end_tile:
            return []
        
        # NPC 只能在人行道和斑馬線上移動
        if start_tile.tile_type not in [TileType.SIDEWALK, TileType.CROSSWALK]:
            return []
        
        if end_tile.tile_type not in [TileType.SIDEWALK, TileType.CROSSWALK]:
            return []
        
        # A* 路徑搜尋
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        # 優先佇列: (f_score, g_score, position, path)
        open_set = [(0, 0, start_grid, [start_grid])]
        closed_set = set()
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 上下左右
        
        while open_set:
            current_f, current_g, current_pos, path = heapq.heappop(open_set)
            
            if current_pos in closed_set:
                continue
            
            closed_set.add(current_pos)
            
            # 到達目標
            if current_pos == end_grid:
                # 轉換回世界座標
                world_path = []
                for grid_pos in path:
                    world_pos = self.grid_to_world(grid_pos[0], grid_pos[1])
                    world_path.append(world_pos)
                return world_path
            
            # 檢查相鄰格子
            for dx, dy in directions:
                next_x = current_pos[0] + dx
                next_y = current_pos[1] + dy
                next_pos = (next_x, next_y)
                
                if next_pos in closed_set:
                    continue
                
                next_tile = self.get_tile(next_x, next_y)
                if not next_tile:
                    continue
                
                # NPC 只能走人行道和斑馬線
                if next_tile.tile_type not in [TileType.SIDEWALK, TileType.CROSSWALK]:
                    continue
                
                new_g = current_g + 1
                new_f = new_g + heuristic(next_pos, end_grid)
                new_path = path + [next_pos]
                
                heapq.heappush(open_set, (new_f, new_g, next_pos, new_path))
        
        # 找不到路徑
        return []
    
    def is_npc_walkable(self, world_x, world_y):
        """
        檢查 NPC 是否可以在指定世界座標行走\n
        
        參數:\n
        world_x (float): 世界 X 座標\n
        world_y (float): 世界 Y 座標\n
        
        回傳:\n
        bool: 是否可以行走\n
        """
        grid_x, grid_y = self.world_to_grid(world_x, world_y)
        tile = self.get_tile(grid_x, grid_y)
        
        if not tile:
            return False
        
        # NPC 只能在人行道和斑馬線上行走
        return tile.tile_type in [TileType.SIDEWALK, TileType.CROSSWALK]
    
    def is_position_walkable(self, world_x, world_y):
        """
        檢查位置是否可以行走（為了向後兼容性）\n
        
        參數:\n
        world_x (float): 世界 X 座標\n
        world_y (float): 世界 Y 座標\n
        
        回傳:\n
        bool: 是否可以行走\n
        """
        return self.is_npc_walkable(world_x, world_y)
    
    def draw_debug(self, screen, camera_x, camera_y, show_grid=True):
        """
        繪製除錯信息（格子地圖可視化）\n
        
        參數:\n
        screen: Pygame 螢幕物件\n
        camera_x (float): 攝影機 X 偏移\n
        camera_y (float): 攝影機 Y 偏移\n
        show_grid (bool): 是否顯示格子邊框\n
        """
        import pygame
        
        # 定義顏色 - 道路相關類型將被跳過繪製
        colors = {
            TileType.GRASS: (34, 139, 34),      # 森林綠
            TileType.ROAD: (105, 105, 105),     # 暗灰色（不會被使用）
            TileType.SIDEWALK: (192, 192, 192), # 淺灰色（不會被使用）
            TileType.CROSSWALK: (255, 255, 0),  # 黃色（不會被使用）
            TileType.BUILDING: (139, 69, 19),   # 棕色
            TileType.BUILDABLE: (50, 205, 50),  # 亮綠色
        }
        
        # 計算可見區域
        start_x = max(0, int(camera_x // self.grid_size))
        start_y = max(0, int(camera_y // self.grid_size))
        end_x = min(self.grid_width, start_x + screen.get_width() // self.grid_size + 2)
        end_y = min(self.grid_height, start_y + screen.get_height() // self.grid_size + 2)
        
        # 繪製格子
        for grid_y in range(start_y, end_y):
            for grid_x in range(start_x, end_x):
                tile = self.get_tile(grid_x, grid_y)
                if tile:
                    # 跳過道路相關的格子，不進行任何繪製
                    if tile.tile_type in [TileType.ROAD, TileType.SIDEWALK, TileType.CROSSWALK]:
                        continue
                        
                    # 計算螢幕座標
                    screen_x = grid_x * self.grid_size - camera_x
                    screen_y = grid_y * self.grid_size - camera_y
                    
                    # 繪製格子背景
                    color = colors.get(tile.tile_type, (128, 128, 128))
                    rect = pygame.Rect(screen_x, screen_y, self.grid_size, self.grid_size)
                    pygame.draw.rect(screen, color, rect)
                    
                    # 繪製格子邊框
                    if show_grid:
                        pygame.draw.rect(screen, (0, 0, 0), rect, 1)