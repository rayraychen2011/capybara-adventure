######################載入套件######################
import pygame
import random
import math
from config.settings import *
from src.utils.terrain_map_loader import TerrainMapLoader
from src.systems.building_system import Building, GunShop, Hospital
from src.systems.vehicle_system import Vehicle


######################基於地形的系統管理器######################
class TerrainBasedSystem:
    """
    基於地形的系統管理器 - 根據地形地圖自動配置遊戲系統\n
    \n
    此系統負責：\n
    1. 載入地形地圖數據\n
    2. 根據地形編碼自動放置建築物\n
    3. 在對應地形格子中配置森林、湖泊、停車場系統\n
    4. 提供地形查詢和互動功能\n
    \n
    地形編碼對應：\n
    - 5 (住宅區): 每格6個住宅，每棟至少為玩家尺寸5倍\n
    - 6 (商業區): 每格4個商業建築，優先放置重要建築\n
    - 1 (森林): 森林系統移植到此地形\n
    - 2 (水體): 湖泊系統移植到此地形\n
    - 8 (停車場): 每格20台車輛\n
    """

    def __init__(self, player):
        """
        初始化基於地形的系統管理器\n
        \n
        參數:\n
        player (Player): 玩家物件，用於計算建築尺寸\n
        """
        self.player = player
        self.terrain_loader = TerrainMapLoader()
        
        # 地形相關設定
        self.tile_size = 40  # 每個地形格子的像素大小
        self.map_data = []
        self.map_width = 0
        self.map_height = 0
        
        # 建築管理
        self.buildings = []
        self.residential_buildings = []  # 住宅建築
        self.commercial_buildings = []   # 商業建築
        
        # 地形系統
        self.forest_areas = []      # 森林區域
        self.water_areas = []       # 水體區域
        self.parking_areas = []     # 停車場區域
        
        # 載具管理
        self.vehicles = []
        self.parking_spots = []     # 停車位
        
        # 資源和動物 (從原始系統移植)
        self.forest_resources = []
        self.water_resources = []
        self.forest_animals = []
        self.water_animals = []
        
        # 建築類型優先級 (商業區)
        self.commercial_priority = [
            "hospital", "church", "gun_shop", "convenience_store",
            "fishing_shop", "market", "street_vendor", "power_plant"
        ]
        
        print("基於地形的系統管理器初始化完成")

    def load_terrain_map(self, csv_file_path):
        """
        載入地形地圖並初始化所有系統\n
        \n
        參數:\n
        csv_file_path (str): CSV地形檔案路徑\n
        \n
        回傳:\n
        bool: 載入成功回傳True，失敗回傳False\n
        """
        print(f"載入地形地圖: {csv_file_path}")
        
        # 載入地形數據
        if not self.terrain_loader.load_from_csv(csv_file_path):
            print("地形地圖載入失敗")
            return False
        
        self.map_data = self.terrain_loader.map_data
        self.map_width = self.terrain_loader.map_width
        self.map_height = self.terrain_loader.map_height
        
        print(f"地形地圖載入成功: {self.map_width}x{self.map_height}")
        
        # 分析地形並配置系統
        self._analyze_terrain()
        self._setup_residential_areas()
        self._setup_commercial_areas()
        self._setup_forest_areas()
        self._setup_water_areas()
        self._setup_parking_areas()
        
        return True

    def _analyze_terrain(self):
        """
        分析地形分佈，統計各類地形的數量和位置\n
        """
        terrain_stats = {}
        
        for y in range(self.map_height):
            for x in range(self.map_width):
                terrain_code = self.map_data[y][x]
                terrain_name = self.terrain_loader.get_terrain_name(terrain_code)
                
                if terrain_name not in terrain_stats:
                    terrain_stats[terrain_name] = {
                        'count': 0,
                        'positions': []
                    }
                
                terrain_stats[terrain_name]['count'] += 1
                terrain_stats[terrain_name]['positions'].append((x, y))
        
        print("\n=== 地形分析結果 ===")
        for terrain_name, stats in terrain_stats.items():
            print(f"{terrain_name}: {stats['count']} 格")
        print()

    def _setup_residential_areas(self):
        """
        設置住宅區 - 地形編碼5\n
        每格放置6個住宅，每棟至少為玩家尺寸的5倍\n
        """
        print("設置住宅區...")
        
        # 計算住宅尺寸 (玩家尺寸的5倍)
        player_size = max(self.player.rect.width, self.player.rect.height)
        house_size = player_size * 5
        
        residential_count = 0
        
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 5:  # 住宅區
                    # 計算格子的世界座標
                    tile_world_x = x * self.tile_size
                    tile_world_y = y * self.tile_size
                    
                    # 在格子內放置6個住宅 (2x3 排列)
                    houses_per_row = 2
                    houses_per_col = 3
                    house_spacing_x = self.tile_size // houses_per_row
                    house_spacing_y = self.tile_size // houses_per_col
                    
                    for house_y in range(houses_per_col):
                        for house_x in range(houses_per_row):
                            # 計算住宅位置 (在格子內均勻分佈)
                            house_pos_x = tile_world_x + house_x * house_spacing_x + house_spacing_x // 4
                            house_pos_y = tile_world_y + house_y * house_spacing_y + house_spacing_y // 4
                            
                            # 確保住宅不超出格子邊界
                            actual_house_size = min(house_size, house_spacing_x - 4, house_spacing_y - 4)
                            
                            # 創建住宅建築
                            house = Building(
                                "residential", 
                                (house_pos_x, house_pos_y), 
                                (actual_house_size, actual_house_size)
                            )
                            house.name = f"住宅{residential_count + 1}"
                            house.color = (255, 255, 224)  # 淺黃色
                            house.terrain_grid = (x, y)  # 記錄所屬地形格子
                            
                            self.buildings.append(house)
                            self.residential_buildings.append(house)
                            residential_count += 1
        
        print(f"住宅區設置完成，共創建 {residential_count} 棟住宅")

    def _setup_commercial_areas(self):
        """
        設置商業區 - 地形編碼6\n
        每格放置4個商業建築，優先放置重要建築\n
        """
        print("設置商業區...")
        
        commercial_positions = []
        
        # 收集所有商業區格子的位置
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 6:  # 商業區
                    commercial_positions.append((x, y))
        
        if not commercial_positions:
            print("沒有找到商業區地形")
            return
        
        print(f"找到 {len(commercial_positions)} 個商業區格子")
        
        # 計算建築尺寸 (每格4個建築，2x2排列)
        building_size_x = self.tile_size // 2 - 2
        building_size_y = self.tile_size // 2 - 2
        
        # 根據優先級分配建築類型
        building_assignments = self._assign_commercial_buildings(len(commercial_positions) * 4)
        
        building_index = 0
        commercial_count = 0
        
        for grid_x, grid_y in commercial_positions:
            # 計算格子的世界座標
            tile_world_x = grid_x * self.tile_size
            tile_world_y = grid_y * self.tile_size
            
            # 在格子內放置4個建築 (2x2 排列)
            for building_y in range(2):
                for building_x in range(2):
                    if building_index >= len(building_assignments):
                        break
                        
                    building_type = building_assignments[building_index]
                    
                    # 計算建築位置
                    pos_x = tile_world_x + building_x * (self.tile_size // 2) + 1
                    pos_y = tile_world_y + building_y * (self.tile_size // 2) + 1
                    
                    # 創建對應類型的建築
                    building = self._create_commercial_building(
                        building_type, 
                        (pos_x, pos_y), 
                        (building_size_x, building_size_y)
                    )
                    
                    if building:
                        building.terrain_grid = (grid_x, grid_y)
                        self.buildings.append(building)
                        self.commercial_buildings.append(building)
                        commercial_count += 1
                    
                    building_index += 1
        
        print(f"商業區設置完成，共創建 {commercial_count} 棟商業建築")

    def _assign_commercial_buildings(self, total_slots):
        """
        根據優先級分配商業建築類型\n
        \n
        參數:\n
        total_slots (int): 總建築位置數量\n
        \n
        回傳:\n
        list: 建築類型分配列表\n
        """
        assignments = []
        
        # 根據遊戲需求分配建築數量
        building_quotas = {
            "hospital": 5,      # 5座醫院
            "gun_shop": 10,     # 10座槍械店  
            "convenience_store": 15,  # 15座便利商店
            "church": 2,        # 2座教堂
            "fishing_shop": 20, # 20座釣魚店
            "market": 10,       # 10座市場
            "street_vendor": 10, # 10個小販
            "power_plant": 1    # 1座電力場
        }
        
        # 按優先級順序分配
        for building_type in self.commercial_priority:
            quota = building_quotas.get(building_type, 0)
            for _ in range(min(quota, total_slots - len(assignments))):
                assignments.append(building_type)
        
        # 如果還有剩餘位置，隨機填充
        while len(assignments) < total_slots:
            assignments.append(random.choice(["convenience_store", "market", "street_vendor"]))
        
        # 打亂順序以避免相同類型聚集
        random.shuffle(assignments)
        
        return assignments

    def _create_commercial_building(self, building_type, position, size):
        """
        創建商業建築\n
        \n
        參數:\n
        building_type (str): 建築類型\n
        position (tuple): 位置 (x, y)\n
        size (tuple): 尺寸 (width, height)\n
        \n
        回傳:\n
        Building: 建築物件\n
        """
        if building_type == "hospital":
            return Hospital(position, size)
        elif building_type == "gun_shop":
            return GunShop(position, size)
        else:
            return Building(building_type, position, size)

    def _setup_forest_areas(self):
        """
        設置森林區域 - 地形編碼1\n
        移植原森林系統到對應地形格子\n
        """
        print("設置森林區域...")
        
        forest_count = 0
        
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 1:  # 森林/密林
                    # 計算格子的世界座標範圍
                    tile_world_x = x * self.tile_size
                    tile_world_y = y * self.tile_size
                    
                    forest_area = {
                        'grid_pos': (x, y),
                        'world_bounds': (tile_world_x, tile_world_y, self.tile_size, self.tile_size),
                        'trees': [],
                        'resources': [],
                        'animals': []
                    }
                    
                    # 在格子內生成樹木 (3-6棵)
                    num_trees = random.randint(3, 6)
                    for _ in range(num_trees):
                        tree_x = tile_world_x + random.randint(2, self.tile_size - 2)
                        tree_y = tile_world_y + random.randint(2, self.tile_size - 2)
                        tree_size = random.randint(8, 15)
                        
                        tree = {
                            'position': (tree_x, tree_y),
                            'size': tree_size,
                            'color': (34, 100, 34)
                        }
                        forest_area['trees'].append(tree)
                    
                    # 在格子內生成資源 (1-3個)
                    num_resources = random.randint(1, 3)
                    for _ in range(num_resources):
                        resource_x = tile_world_x + random.randint(4, self.tile_size - 4)
                        resource_y = tile_world_y + random.randint(4, self.tile_size - 4)
                        
                        resource_type = random.choice([
                            {'name': '木材', 'color': (139, 69, 19), 'value': 5},
                            {'name': '草藥', 'color': (0, 128, 0), 'value': 8},
                            {'name': '蘑菇', 'color': (255, 228, 196), 'value': 12}
                        ])
                        
                        resource = {
                            'name': resource_type['name'],
                            'position': (resource_x, resource_y),
                            'color': resource_type['color'],
                            'value': resource_type['value'],
                            'collected': False,
                            'rect': pygame.Rect(resource_x - 4, resource_y - 4, 8, 8)
                        }
                        forest_area['resources'].append(resource)
                        self.forest_resources.append(resource)
                    
                    self.forest_areas.append(forest_area)
                    forest_count += 1
        
        print(f"森林區域設置完成，共創建 {forest_count} 個森林格子")

    def _setup_water_areas(self):
        """
        設置水體區域 - 地形編碼2\n
        移植原湖泊系統到對應地形格子\n
        """
        print("設置水體區域...")
        
        water_count = 0
        
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 2:  # 水體
                    # 計算格子的世界座標範圍
                    tile_world_x = x * self.tile_size
                    tile_world_y = y * self.tile_size
                    
                    water_area = {
                        'grid_pos': (x, y),
                        'world_bounds': (tile_world_x, tile_world_y, self.tile_size, self.tile_size),
                        'fishing_spots': [],
                        'resources': [],
                        'fish': []
                    }
                    
                    # 在格子內生成釣魚點 (1個)
                    fishing_x = tile_world_x + self.tile_size // 2
                    fishing_y = tile_world_y + self.tile_size // 2
                    
                    fishing_spot = {
                        'name': f'釣魚點({x},{y})',
                        'position': (fishing_x, fishing_y),
                        'area': pygame.Rect(fishing_x - 10, fishing_y - 10, 20, 20),
                        'fish_rate': random.uniform(0.3, 0.6),
                        'rare_rate': random.uniform(0.05, 0.2)
                    }
                    water_area['fishing_spots'].append(fishing_spot)
                    
                    # 在格子邊緣生成水邊資源 (1-2個)
                    num_resources = random.randint(1, 2)
                    for _ in range(num_resources):
                        # 隨機選擇邊緣位置
                        side = random.choice(['top', 'bottom', 'left', 'right'])
                        if side == 'top':
                            resource_x = tile_world_x + random.randint(2, self.tile_size - 2)
                            resource_y = tile_world_y + 1
                        elif side == 'bottom':
                            resource_x = tile_world_x + random.randint(2, self.tile_size - 2)
                            resource_y = tile_world_y + self.tile_size - 1
                        elif side == 'left':
                            resource_x = tile_world_x + 1
                            resource_y = tile_world_y + random.randint(2, self.tile_size - 2)
                        else:  # right
                            resource_x = tile_world_x + self.tile_size - 1
                            resource_y = tile_world_y + random.randint(2, self.tile_size - 2)
                        
                        resource_type = random.choice([
                            {'name': '水草', 'color': (0, 100, 0), 'value': 3},
                            {'name': '貝殼', 'color': (255, 192, 203), 'value': 8},
                            {'name': '漂流木', 'color': (139, 69, 19), 'value': 5}
                        ])
                        
                        resource = {
                            'name': resource_type['name'],
                            'position': (resource_x, resource_y),
                            'color': resource_type['color'],
                            'value': resource_type['value'],
                            'collected': False,
                            'rect': pygame.Rect(resource_x - 4, resource_y - 4, 8, 8)
                        }
                        water_area['resources'].append(resource)
                        self.water_resources.append(resource)
                    
                    self.water_areas.append(water_area)
                    water_count += 1
        
        print(f"水體區域設置完成，共創建 {water_count} 個水體格子")

    def _setup_parking_areas(self):
        """
        設置停車場區域 - 地形編碼8\n
        每格放置20台車輛\n
        """
        print("設置停車場區域...")
        
        parking_count = 0
        vehicle_count = 0
        
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 8:  # 停車場
                    # 計算格子的世界座標範圍
                    tile_world_x = x * self.tile_size
                    tile_world_y = y * self.tile_size
                    
                    parking_area = {
                        'grid_pos': (x, y),
                        'world_bounds': (tile_world_x, tile_world_y, self.tile_size, self.tile_size),
                        'vehicles': [],
                        'parking_spots': []
                    }
                    
                    # 在格子內生成20個停車位 (5x4 排列)
                    spots_per_row = 5
                    spots_per_col = 4
                    spot_width = self.tile_size // spots_per_row
                    spot_height = self.tile_size // spots_per_col
                    
                    for spot_y in range(spots_per_col):
                        for spot_x in range(spots_per_row):
                            # 計算停車位位置
                            spot_pos_x = tile_world_x + spot_x * spot_width + spot_width // 2
                            spot_pos_y = tile_world_y + spot_y * spot_height + spot_height // 2
                            
                            parking_spot = {
                                'position': (spot_pos_x, spot_pos_y),
                                'occupied': False,
                                'vehicle': None,
                                'rect': pygame.Rect(spot_pos_x - spot_width//4, spot_pos_y - spot_height//4, 
                                                  spot_width//2, spot_height//2)
                            }
                            
                            # 80% 機率生成停放的車輛
                            if random.random() < 0.8:
                                vehicle_type = random.choice(['car', 'motorcycle', 'bike'])
                                vehicle = Vehicle(vehicle_type, (spot_pos_x, spot_pos_y), is_ai_controlled=False)
                                
                                parking_spot['occupied'] = True
                                parking_spot['vehicle'] = vehicle
                                parking_area['vehicles'].append(vehicle)
                                self.vehicles.append(vehicle)
                                vehicle_count += 1
                            
                            parking_area['parking_spots'].append(parking_spot)
                            self.parking_spots.append(parking_spot)
                    
                    self.parking_areas.append(parking_area)
                    parking_count += 1
        
        print(f"停車場區域設置完成，共創建 {parking_count} 個停車場格子，停放 {vehicle_count} 台車輛")

    def get_terrain_at_world_pos(self, world_x, world_y):
        """
        獲取世界座標位置的地形類型\n
        \n
        參數:\n
        world_x (float): 世界X座標\n
        world_y (float): 世界Y座標\n
        \n
        回傳:\n
        int: 地形編碼，超出範圍回傳None\n
        """
        grid_x = int(world_x // self.tile_size)
        grid_y = int(world_y // self.tile_size)
        
        return self.terrain_loader.get_terrain_at(grid_x, grid_y)

    def get_buildings_in_area(self, center_pos, radius):
        """
        獲取指定區域內的建築\n
        \n
        參數:\n
        center_pos (tuple): 中心位置 (x, y)\n
        radius (float): 搜尋半徑\n
        \n
        回傳:\n
        list: 區域內的建築列表\n
        """
        nearby_buildings = []
        cx, cy = center_pos
        
        for building in self.buildings:
            bx = building.x + building.width // 2
            by = building.y + building.height // 2
            distance = math.sqrt((cx - bx) ** 2 + (cy - by) ** 2)
            
            if distance <= radius:
                nearby_buildings.append(building)
        
        return nearby_buildings

    def get_forest_resources_in_area(self, center_pos, radius):
        """
        獲取指定區域內的森林資源\n
        \n
        參數:\n
        center_pos (tuple): 中心位置 (x, y)\n
        radius (float): 搜尋半徑\n
        \n
        回傳:\n
        list: 可收集的森林資源列表\n
        """
        nearby_resources = []
        cx, cy = center_pos
        
        for resource in self.forest_resources:
            if resource['collected']:
                continue
                
            rx, ry = resource['position']
            distance = math.sqrt((cx - rx) ** 2 + (cy - ry) ** 2)
            
            if distance <= radius:
                nearby_resources.append(resource)
        
        return nearby_resources

    def get_water_resources_in_area(self, center_pos, radius):
        """
        獲取指定區域內的水邊資源\n
        \n
        參數:\n
        center_pos (tuple): 中心位置 (x, y)\n
        radius (float): 搜尋半徑\n
        \n
        回傳:\n
        list: 可收集的水邊資源列表\n
        """
        nearby_resources = []
        cx, cy = center_pos
        
        for resource in self.water_resources:
            if resource['collected']:
                continue
                
            rx, ry = resource['position']
            distance = math.sqrt((cx - rx) ** 2 + (cy - ry) ** 2)
            
            if distance <= radius:
                nearby_resources.append(resource)
        
        return nearby_resources

    def get_fishing_spots_in_area(self, center_pos, radius):
        """
        獲取指定區域內的釣魚點\n
        \n
        參數:\n
        center_pos (tuple): 中心位置 (x, y)\n
        radius (float): 搜尋半徑\n
        \n
        回傳:\n
        list: 可用的釣魚點列表\n
        """
        nearby_spots = []
        cx, cy = center_pos
        
        for water_area in self.water_areas:
            for spot in water_area['fishing_spots']:
                sx, sy = spot['position']
                distance = math.sqrt((cx - sx) ** 2 + (cy - sy) ** 2)
                
                if distance <= radius:
                    nearby_spots.append(spot)
        
        return nearby_spots

    def get_parking_spots_in_area(self, center_pos, radius):
        """
        獲取指定區域內的停車位\n
        \n
        參數:\n
        center_pos (tuple): 中心位置 (x, y)\n
        radius (float): 搜尋半徑\n
        \n
        回傳:\n
        list: 停車位列表\n
        """
        nearby_spots = []
        cx, cy = center_pos
        
        for spot in self.parking_spots:
            sx, sy = spot['position']
            distance = math.sqrt((cx - sx) ** 2 + (cy - sy) ** 2)
            
            if distance <= radius:
                nearby_spots.append(spot)
        
        return nearby_spots

    def draw_terrain_layer(self, screen, camera_x, camera_y):
        """
        繪製地形層 (背景)\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        # 計算可見區域的地形格子範圍
        start_x = max(0, int(camera_x // self.tile_size))
        start_y = max(0, int(camera_y // self.tile_size))
        end_x = min(self.map_width, start_x + screen.get_width() // self.tile_size + 2)
        end_y = min(self.map_height, start_y + screen.get_height() // self.tile_size + 2)
        
        # 繪製地形格子
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if y < len(self.map_data) and x < len(self.map_data[y]):
                    terrain_code = self.map_data[y][x]
                    color = self.terrain_loader.get_terrain_color(terrain_code)
                    
                    # 計算螢幕座標
                    screen_x = x * self.tile_size - camera_x
                    screen_y = y * self.tile_size - camera_y
                    
                    # 繪製地形格子
                    rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                    pygame.draw.rect(screen, color, rect)
                    
                    # 繪製格子邊框 (淡色)
                    pygame.draw.rect(screen, (128, 128, 128), rect, 1)

    def draw_forest_elements(self, screen, camera_x, camera_y):
        """
        繪製森林元素\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        for forest_area in self.forest_areas:
            # 檢查森林區域是否在可見範圍內
            fx, fy, fw, fh = forest_area['world_bounds']
            if (fx + fw < camera_x or fx > camera_x + screen.get_width() or
                fy + fh < camera_y or fy > camera_y + screen.get_height()):
                continue
            
            # 繪製樹木
            for tree in forest_area['trees']:
                tx, ty = tree['position']
                screen_x = tx - camera_x
                screen_y = ty - camera_y
                
                # 繪製樹冠
                pygame.draw.circle(screen, tree['color'], (int(screen_x), int(screen_y)), tree['size'] // 2)
                
                # 繪製樹幹
                trunk_rect = pygame.Rect(screen_x - 2, screen_y, 4, tree['size'] // 3)
                pygame.draw.rect(screen, (101, 67, 33), trunk_rect)
            
            # 繪製資源
            for resource in forest_area['resources']:
                if resource['collected']:
                    continue
                    
                rx, ry = resource['position']
                screen_x = rx - camera_x
                screen_y = ry - camera_y
                
                pygame.draw.circle(screen, resource['color'], (int(screen_x), int(screen_y)), 4)

    def draw_water_elements(self, screen, camera_x, camera_y):
        """
        繪製水體元素\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        for water_area in self.water_areas:
            # 檢查水體區域是否在可見範圍內
            wx, wy, ww, wh = water_area['world_bounds']
            if (wx + ww < camera_x or wx > camera_x + screen.get_width() or
                wy + wh < camera_y or wy > camera_y + screen.get_height()):
                continue
            
            # 繪製水波效果
            for i in range(3):
                wave_y = wy + (i + 1) * (wh / 4)
                screen_wave_y = wave_y - camera_y
                pygame.draw.line(screen, (100, 150, 255), 
                               (wx - camera_x, screen_wave_y), 
                               (wx + ww - camera_x, screen_wave_y), 1)
            
            # 繪製釣魚點
            for spot in water_area['fishing_spots']:
                sx, sy = spot['position']
                screen_x = sx - camera_x
                screen_y = sy - camera_y
                
                pygame.draw.circle(screen, (255, 255, 0), (int(screen_x), int(screen_y)), 6)
                pygame.draw.circle(screen, (0, 100, 200), (int(screen_x), int(screen_y)), 4)
            
            # 繪製水邊資源
            for resource in water_area['resources']:
                if resource['collected']:
                    continue
                    
                rx, ry = resource['position']
                screen_x = rx - camera_x
                screen_y = ry - camera_y
                
                pygame.draw.circle(screen, resource['color'], (int(screen_x), int(screen_y)), 4)

    def draw_buildings(self, screen, camera_x, camera_y):
        """
        繪製所有建築\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        for building in self.buildings:
            # 檢查建築是否在可見範圍內
            if (building.x + building.width < camera_x or building.x > camera_x + screen.get_width() or
                building.y + building.height < camera_y or building.y > camera_y + screen.get_height()):
                continue
            
            # 計算螢幕座標
            screen_x = building.x - camera_x
            screen_y = building.y - camera_y
            
            # 創建螢幕矩形
            screen_rect = pygame.Rect(screen_x, screen_y, building.width, building.height)
            
            # 繪製建築
            pygame.draw.rect(screen, building.color, screen_rect)
            pygame.draw.rect(screen, (0, 0, 0), screen_rect, 1)
            
            # 繪製建築名稱 (如果建築夠大)
            if building.width > 30 and building.height > 20:
                font = pygame.font.Font(None, 16)
                text = font.render(building.name, True, (0, 0, 0))
                text_rect = text.get_rect(center=screen_rect.center)
                screen.blit(text, text_rect)

    def draw_vehicles(self, screen, camera_x, camera_y):
        """
        繪製所有車輛\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        for vehicle in self.vehicles:
            # 檢查車輛是否在可見範圍內
            if (vehicle.x + vehicle.rect.width < camera_x or vehicle.x > camera_x + screen.get_width() or
                vehicle.y + vehicle.rect.height < camera_y or vehicle.y > camera_y + screen.get_height()):
                continue
            
            # 計算螢幕座標
            screen_x = vehicle.x - camera_x
            screen_y = vehicle.y - camera_y
            
            # 創建螢幕矩形
            screen_rect = pygame.Rect(screen_x, screen_y, vehicle.rect.width, vehicle.rect.height)
            
            # 繪製車輛
            pygame.draw.rect(screen, vehicle.color, screen_rect)
            pygame.draw.rect(screen, (0, 0, 0), screen_rect, 1)

    def get_statistics(self):
        """
        獲取系統統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊\n
        """
        return {
            'map_size': f"{self.map_width}x{self.map_height}",
            'buildings': len(self.buildings),
            'residential_buildings': len(self.residential_buildings),
            'commercial_buildings': len(self.commercial_buildings),
            'forest_areas': len(self.forest_areas),
            'water_areas': len(self.water_areas),
            'parking_areas': len(self.parking_areas),
            'vehicles': len(self.vehicles),
            'forest_resources': len([r for r in self.forest_resources if not r['collected']]),
            'water_resources': len([r for r in self.water_resources if not r['collected']])
        }

    def get_terrain_at_position(self, world_x, world_y):
        """
        獲取指定世界座標位置的地形類型\n
        \n
        參數:\n
        world_x (float): 世界座標 X\n
        world_y (float): 世界座標 Y\n
        \n
        回傳:\n
        int: 地形類型編碼，如果超出範圍則回傳 0 (草地)\n
        """
        # 將世界座標轉換為地形格子座標
        grid_x = int(world_x // self.tile_size)
        grid_y = int(world_y // self.tile_size)
        
        # 檢查是否在地圖範圍內
        if (0 <= grid_x < self.map_width and 0 <= grid_y < self.map_height):
            return self.map_data[grid_y][grid_x]
        else:
            return 0  # 超出範圍默認為草地