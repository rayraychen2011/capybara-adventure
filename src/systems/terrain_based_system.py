######################載入套件######################
import pygame
import random
import math
from config.settings import *
from src.utils.terrain_map_loader import TerrainMapLoader
from src.systems.building_system import Building, GunShop, Hospital, ResidentialHouse
from src.systems.railway_system import RailwaySystem
from src.utils.font_manager import FontManager


######################基於地形的系統管理器######################
class TerrainBasedSystem:
    """
    基於地形的系統管理器 - 根據地形地圖自動配置遊戲系統\n
    \n
    此系統負責：\n
    1. 載入地形地圖數據\n
    2. 根據地形編碼自動放置建築物\n
    3. 在對應地形格子中配置森林、湖泊系統\n
    4. 管理鐵路系統（火車站和鐵軌）\n
    5. 提供地形查詢和互動功能\n
    \n
    地形編碼對應：\n
    - 5 (住宅區): 每格4個住宅，玩家家有特殊標記\n
    - 6 (商業區): 每格4個商業建築，優先放置重要建築\n
    - 10 (鐵軌): 火車軌道，有交通號誌和斑馬線\n
    - 11 (火車站): 火車站建築，2格填滿1個建築\n
    - 1 (森林): 森林系統移植到此地形\n
    - 2 (水體): 湖泊系統移植到此地形\n
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
        
        # 字體管理器
        self.font_manager = FontManager()
        
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
        self.vegetable_gardens = [] # 蔬果園區域（新增）
        self.farm_areas = []        # 農地區域（新增）
        
        # 鐵路系統
        self.railway_system = RailwaySystem()
        
        # 資源和動物 (從原始系統移植)
        self.forest_resources = []
        self.water_resources = []
        self.forest_animals = []
        self.water_animals = []
        
        # 建築類型優先級 (商業區) - 依據新需求優化建築類型
        self.commercial_priority = [
            "convenience_store", "clothing_store", "gun_shop", "church", 
            "office_building", "hospital", "park"  # 新增服裝店，移除market和street_vendor
        ]
        
        # 火車站3周圍商業區特殊配置 - 根據用戶需求設定
        self.station3_commercial_config = {
            "convenience_store": 2,  # 2個便利商店
            "factory": 0,           # 剩餘位置大部分為工廠
            "office_building": 2    # 2棟辦公大樓
        }
        
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
        self._setup_farm_areas()  # 新增農地設置
        self._setup_forest_areas()
        self._setup_water_areas()
        self._setup_railway_system()
        
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
        根據新需求：最多只能有 100 棟住宅，超過的住宅格位將改為蔬果園\n
        住宅區每格放4個住宅單位，將住宅區格子填滿\n
        其中一個住宅是玩家的家，要顯示文字\n
        """
        print("設置住宅區...")
        
        # 找到住宅區格子
        residential_tiles = []
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 5:  # 住宅區
                    residential_tiles.append((x, y))
        
        if not residential_tiles:
            print("警告：找不到住宅區格子")
            return
        
        # print(f"找到 {len(residential_tiles)} 個住宅區格子")  # 暫時關閉輸出
        
        # 每個住宅區格子放4個住宅單位
        houses_per_grid = HOUSES_PER_RESIDENTIAL_GRID
        total_houses_created = 0
        max_houses = MAX_RESIDENTIAL_BUILDINGS  # 新需求：最多 100 棟住宅
        
        # 住宅尺寸設定
        base_house_size = 30  # 基礎住宅大小
        house_spacing = 5     # 住宅間的間隙
        
        for tile_x, tile_y in residential_tiles:
            # 計算格子的世界座標
            tile_world_x = tile_x * self.tile_size
            tile_world_y = tile_y * self.tile_size
            
            # 檢查是否已達到住宅數量上限
            if total_houses_created >= max_houses:
                # 超過住宅數量上限，改為創建蔬果園
                self._create_vegetable_garden_at_tile(tile_x, tile_y)
                continue
            
            # 在每個格子內放置4個住宅（2x2排列）
            houses_in_grid = 0
            for row in range(2):
                for col in range(2):
                    if houses_in_grid >= houses_per_grid or total_houses_created >= max_houses:
                        break
                    
                    # 計算住宅在格子內的位置（2x2排列）
                    house_size_in_grid = (self.tile_size - house_spacing * 3) // 2  # 減去間隙後的可用空間
                    house_size = min(house_size_in_grid, base_house_size)  # 不超過基礎大小
                    
                    house_pos_x = tile_world_x + house_spacing + col * (house_size + house_spacing)
                    house_pos_y = tile_world_y + house_spacing + row * (house_size + house_spacing)
                    
                    # 碰撞檢測：確保新住宅不與現有建築重疊
                    new_house_rect = pygame.Rect(house_pos_x, house_pos_y, house_size, house_size)
                    collision_detected = False
                    
                    for existing_building in self.buildings:
                        existing_rect = pygame.Rect(existing_building.x, existing_building.y, 
                                                  existing_building.width, existing_building.height)
                        if new_house_rect.colliderect(existing_rect):
                            collision_detected = True
                            break
                    
                    # 如果沒有碰撞，創建住宅
                    if not collision_detected:
                        # 創建住宅建築 - 使用 ResidentialHouse 類別
                        house = ResidentialHouse(
                            "house", 
                            (house_pos_x, house_pos_y), 
                            (house_size, house_size)  # 正方形
                        )
                        
                        # 第一個住宅設為玩家之家
                        if total_houses_created == 0:
                            house.is_player_home = True
                            house.name = "玩家之家"
                            house.color = (255, 215, 0)  # 金色標記玩家之家
                            house.show_text = True  # 顯示家的文字
                        else:
                            house.name = f"住宅{total_houses_created + 1}"
                            house.color = (160, 82, 45)  # 住宅標準顏色
                            house.show_text = False
                        
                        house.terrain_grid = (tile_x, tile_y)  # 記錄所屬地形格子
                        
                        self.buildings.append(house)
                        self.residential_buildings.append(house)
                        total_houses_created += 1
                        houses_in_grid += 1
                        
                        print(f"在格子({tile_x},{tile_y})創建住宅 {house.name} 位置({house_pos_x},{house_pos_y})")
                    else:
                        print(f"住宅位置({house_pos_x},{house_pos_y})發生碰撞，跳過")
                
                if houses_in_grid >= houses_per_grid:
                    break
            
            # 如果這個格子沒有創建滿4個住宅且已達到總數上限，剩餘空間創建蔬果園
            if total_houses_created >= max_houses and houses_in_grid < houses_per_grid:
                self._create_vegetable_garden_at_tile(tile_x, tile_y, partial=True)
        
        print(f"住宅區設置完成，共創建 {total_houses_created} 棟住宅（上限 {max_houses} 棟）")
        print(f"玩家之家數量: {sum(1 for h in self.residential_buildings if hasattr(h, 'is_player_home') and h.is_player_home)}")
        
        # 為所有住宅初始化內部佈置
        for house in self.residential_buildings:
            if hasattr(house, 'initialize_interior'):
                house.initialize_interior()

    def _create_vegetable_garden_at_tile(self, tile_x, tile_y, partial=False):
        """
        在指定地形格子創建蔬果園\n
        根據新需求：蔬果園每天成熟一次，玩家可以右鍵採摘獲得金錢\n
        \n
        參數:\n
        tile_x (int): 地形格子 X 座標\n
        tile_y (int): 地形格子 Y 座標\n
        partial (bool): 是否為部分填充（與住宅共存）\n
        """
        # 計算格子的世界座標
        tile_world_x = tile_x * self.tile_size
        tile_world_y = tile_y * self.tile_size
        
        # 創建蔬果園
        garden = {
            'position': (tile_world_x, tile_world_y),
            'size': self.tile_size,
            'color': (34, 139, 34),  # 森林綠
            'growth_stage': 0,  # 0-3 生長階段
            'harvest_ready': False,
            'last_harvest_day': -1,  # 上次收穫的遊戲日
            'crops': [],
            'partial': partial,  # 是否為部分蔬果園
            'grid_pos': (tile_x, tile_y)
        }
        
        # 在蔬果園內隨機放置農作物
        crop_count = 6 if not partial else 3  # 部分蔬果園較少農作物
        for i in range(crop_count):
            crop_x = tile_world_x + random.randint(5, self.tile_size - 10)
            crop_y = tile_world_y + random.randint(5, self.tile_size - 10)
            
            # 隨機農作物顏色
            crop_colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0)]
            crop = {
                'position': (crop_x, crop_y),
                'color': random.choice(crop_colors),
                'harvested': False
            }
            garden['crops'].append(crop)
        
        self.vegetable_gardens.append(garden)
        print(f"在格子({tile_x},{tile_y})創建蔬果園")

    def _setup_commercial_areas(self):
        """
        設置商業區 - 地形編碼6\n
        每格放置4個商業建築，優先放置重要建築\n
        火車站3周圍的商業區有特殊配置：2個便利商店，剩下都是工廠和2棟辦公大樓\n
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
        
        # 找到火車站3的位置（CSV第50行第70列，轉換為0索引是第49行第69列）
        station3_row = 49
        station3_col = 69
        
        # 定義火車站3周圍的商業區範圍
        station3_commercial_positions = []
        for grid_x, grid_y in commercial_positions:
            # 檢查是否在火車站3附近（行49-51，列71-74範圍內）
            if (grid_y >= station3_row - 1 and grid_y <= station3_row + 1 and
                grid_x >= station3_col + 2 and grid_x <= station3_col + 5):
                station3_commercial_positions.append((grid_x, grid_y))
        
        # 為一般商業區和火車站3周圍商業區分別分配建築
        general_commercial_count = len(commercial_positions) - len(station3_commercial_positions)
        station3_commercial_count = len(station3_commercial_positions)
        
        print(f"火車站3周圍商業區: {station3_commercial_count} 格")
        print(f"一般商業區: {general_commercial_count} 格")
        
        # 根據優先級分配建築類型
        general_assignments = self._assign_commercial_buildings(general_commercial_count * 4)
        station3_assignments = self._assign_station3_commercial_buildings(station3_commercial_count * 4)
        
        building_index = 0
        station3_building_index = 0
        commercial_count = 0
        
        for grid_x, grid_y in commercial_positions:
            # 計算格子的世界座標
            tile_world_x = grid_x * self.tile_size
            tile_world_y = grid_y * self.tile_size
            
            # 判斷是否為火車站3周圍的商業區
            is_station3_area = (grid_x, grid_y) in station3_commercial_positions
            
            # 在格子內放置4個建築 (2x2 排列)
            for building_y in range(2):
                for building_x in range(2):
                    if is_station3_area:
                        if station3_building_index >= len(station3_assignments):
                            break
                        building_type = station3_assignments[station3_building_index]
                        station3_building_index += 1
                    else:
                        if building_index >= len(general_assignments):
                            break
                        building_type = general_assignments[building_index]
                        building_index += 1
                        
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
                        # 為火車站3周圍的建築添加特殊標記
                        if is_station3_area:
                            building.station3_area = True
                        self.buildings.append(building)
                        self.commercial_buildings.append(building)
                        commercial_count += 1
        
        print(f"商業區設置完成，共創建 {commercial_count} 棟商業建築")
        print(f"火車站3周圍商業區建築: {station3_building_index} 棟")

    def _setup_farm_areas(self):
        """
        設置農地區域 - 根據地形碼8設置農田系統\n
        \n
        農地功能：\n
        1. 農夫NPC的工作場地\n
        2. 農夫會在此區域一整天耕種\n
        3. 農夫不會消失，始終在農地工作\n
        """
        print("設置農地區域...")
        
        farm_count = 0
        
        # 遍歷所有地形格子，找到農地（代碼8）
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 8:  # 農地地形
                    # 計算農地位置
                    farm_x = x * self.tile_size
                    farm_y = y * self.tile_size
                    
                    # 創建農地區域
                    farm_area = {
                        'position': (farm_x, farm_y),
                        'size': (self.tile_size, self.tile_size),
                        'grid_pos': (x, y),
                        'type': 'farmland',
                        'is_tilled': random.choice([True, False]),  # 隨機耕作狀態
                        'crop_type': random.choice(['wheat', 'corn', 'vegetables', 'rice']),  # 作物類型
                        'growth_stage': random.randint(0, 4),  # 作物生長階段 (0-4)
                        'rect': pygame.Rect(farm_x, farm_y, self.tile_size, self.tile_size)
                    }
                    
                    self.farm_areas.append(farm_area)
                    farm_count += 1
        
        print(f"農地設置完成，共創建 {farm_count} 個農地格子")
        
        # 設置農夫工作區域
        if self.farm_areas:
            print("農地已準備完成，農夫NPC將在此區域工作")
        else:
            print("警告：沒有找到農地區域（地形碼8）")

    def _setup_vegetable_gardens(self):
        """
        設置蔬果園 - 在住宅區多餘的格子中創建蔬果園\n
        新需求：住宅區多餘的格子改為蔬果園\n
        """
        print("設置蔬果園...")
        
        from config.settings import VEGETABLE_GARDEN_COUNT, VEGETABLE_GARDEN_COLOR
        
        # 找到住宅區格子
        residential_tiles = []
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map_data[y][x] == 5:  # 住宅區
                    residential_tiles.append((x, y))
        
        if not residential_tiles:
            print("警告：找不到住宅區格子來放置蔬果園")
            return
        
        # 計算住宅數量和剩餘空間
        total_residential_slots = len(residential_tiles) * 4  # 每格4個位置
        used_housing_slots = 100  # 總共100個房子
        remaining_slots = total_residential_slots - used_housing_slots
        
        # 在剩餘空間中創建蔬果園
        gardens_to_create = min(VEGETABLE_GARDEN_COUNT, remaining_slots)
        garden_count = 0
        
        for tile_x, tile_y in residential_tiles:
            if garden_count >= gardens_to_create:
                break
                
            # 計算格子的世界座標
            tile_world_x = tile_x * self.tile_size
            tile_world_y = tile_y * self.tile_size
            
            # 檢查這個格子是否還有空間（不與現有建築重疊）
            available_positions = []
            garden_spacing = 5
            garden_size = 15
            
            # 在格子內尋找可用位置
            for row in range(2):
                for col in range(2):
                    pos_x = tile_world_x + garden_spacing + col * (self.tile_size // 2)
                    pos_y = tile_world_y + garden_spacing + row * (self.tile_size // 2)
                    
                    # 檢查是否與現有建築重疊
                    garden_rect = pygame.Rect(pos_x, pos_y, garden_size, garden_size)
                    collision = False
                    
                    for building in self.buildings:
                        building_rect = pygame.Rect(building.x, building.y, building.width, building.height)
                        if garden_rect.colliderect(building_rect):
                            collision = True
                            break
                    
                    if not collision:
                        available_positions.append((pos_x, pos_y))
            
            # 在可用位置中創建蔬果園
            for pos_x, pos_y in available_positions:
                if garden_count >= gardens_to_create:
                    break
                
                garden = {
                    'position': (pos_x, pos_y),
                    'size': garden_size,
                    'color': VEGETABLE_GARDEN_COLOR,
                    'crops': self._generate_crops(pos_x, pos_y, garden_size),
                    'growth_stage': random.randint(0, 3),  # 0-3生長階段
                    'harvest_ready': random.choice([True, False]),
                    'terrain_grid': (tile_x, tile_y)
                }
                
                self.vegetable_gardens.append(garden)
                garden_count += 1
                print(f"在格子({tile_x},{tile_y})創建蔬果園 位置({pos_x},{pos_y})")
        
        print(f"蔬果園設置完成，共創建 {garden_count} 個蔬果園")

    def _generate_crops(self, garden_x, garden_y, garden_size):
        """
        為蔬果園生成農作物\n
        \n
        參數:\n
        garden_x (int): 蔬果園X座標\n
        garden_y (int): 蔬果園Y座標\n
        garden_size (int): 蔬果園大小\n
        \n
        回傳:\n
        list: 農作物列表\n
        """
        crops = []
        crop_types = [
            {'name': '番茄', 'color': (255, 99, 71), 'value': 10},
            {'name': '玉米', 'color': (255, 215, 0), 'value': 8},
            {'name': '高麗菜', 'color': (50, 205, 50), 'value': 6},
            {'name': '紅蘿蔔', 'color': (255, 140, 0), 'value': 7}
        ]
        
        # 在蔬果園內隨機放置3-6個農作物
        num_crops = random.randint(3, 6)
        for _ in range(num_crops):
            crop_type = random.choice(crop_types)
            crop_x = garden_x + random.randint(2, garden_size - 2)
            crop_y = garden_y + random.randint(2, garden_size - 2)
            
            crop = {
                'name': crop_type['name'],
                'position': (crop_x, crop_y),
                'color': crop_type['color'],
                'value': crop_type['value'],
                'harvested': False,
                'rect': pygame.Rect(crop_x - 2, crop_y - 2, 4, 4)
            }
            crops.append(crop)
        
        return crops

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
        
        # 根據遊戲需求分配建築數量 - 專注於住宅區附近的類型
        building_quotas = {
            "convenience_store": max(1, total_slots // 8),  # 便利商店
            "clothing_store": max(1, total_slots // 10),    # 服裝店
            "gun_shop": max(1, total_slots // 12),          # 槍械店
            "church": max(1, total_slots // 20),            # 教堂
            "office_building": max(1, total_slots // 6),    # 辦公大樓
            "hospital": max(1, total_slots // 15),          # 醫院
            "park": max(1, total_slots // 8)                # 公園
        }
        
        # 按優先級順序分配
        for building_type in self.commercial_priority:
            quota = building_quotas.get(building_type, 0)
            for _ in range(min(quota, total_slots - len(assignments))):
                assignments.append(building_type)
        
        # 如果還有剩餘位置，隨機填充主要類型
        while len(assignments) < total_slots:
            assignments.append(random.choice(["convenience_store", "clothing_store", "office_building"]))
        
        # 打亂順序以避免相同類型聚集
        random.shuffle(assignments)
        
        return assignments

    def _assign_station3_commercial_buildings(self, total_slots):
        """
        為火車站3周圍商業區分配建築類型\n
        根據用戶需求：2個便利商店，剩下都是工廠和2棟辦公大樓\n
        \n
        參數:\n
        total_slots (int): 總建築位置數量\n
        \n
        回傳:\n
        list: 建築類型分配列表\n
        """
        assignments = []
        
        # 按照指定配置分配
        config = self.station3_commercial_config
        
        # 先分配便利商店
        for _ in range(min(config["convenience_store"], total_slots)):
            assignments.append("convenience_store")
        
        # 再分配辦公大樓
        office_count = min(config["office_building"], total_slots - len(assignments))
        for _ in range(office_count):
            assignments.append("office_building")
        
        # 剩餘位置都分配為工廠
        remaining_slots = total_slots - len(assignments)
        for _ in range(remaining_slots):
            assignments.append("factory")
        
        print(f"火車站3商業區建築分配: 便利商店={config['convenience_store']}, 辦公大樓={office_count}, 工廠={remaining_slots}")
        
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
        elif building_type == "factory":
            # 創建工廠建築
            factory = Building(building_type, position, size)
            factory.name = "工廠"
            factory.color = (105, 105, 105)  # 深灰色工廠
            return factory
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
                            'color': (34, 100, 34),
                            'collision_rect': pygame.Rect(tree_x - tree_size//2, tree_y - tree_size//2, tree_size, tree_size)  # 添加碰撞矩形
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
        移植原湖泊系統到對應地形格子（移除釣魚功能）\n
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
                        'resources': []
                    }
                    
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

    def _setup_railway_system(self):
        """
        設置鐵路系統 - 地形編碼10(鐵軌)和11(火車站)\n
        """
        print("設置鐵路系統...")
        
        # 設置火車站
        self.railway_system.setup_stations_from_terrain(self)
        
        # 設置鐵軌
        self.railway_system.setup_railway_tracks_from_terrain(self)
        
        print("鐵路系統設置完成")

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

    def can_move_to_position(self, world_x, world_y, entity_rect):
        """
        檢查實體是否可以移動到指定位置\n
        （NPC不能到鐵軌上，但玩家可以通過斑馬線）\n
        \n
        參數:\n
        world_x (float): 目標世界座標 X\n
        world_y (float): 目標世界座標 Y\n
        entity_rect (pygame.Rect): 實體的碰撞矩形\n
        \n
        回傳:\n
        bool: 如果可以移動則回傳 True\n
        """
        # 檢查水域碰撞
        if self.check_water_collision(world_x, world_y):
            return False
        
        # 創建目標位置的矩形
        target_rect = pygame.Rect(world_x - entity_rect.width//2, world_y - entity_rect.height//2, 
                                entity_rect.width, entity_rect.height)
        
        # 檢查樹木碰撞
        if self.check_tree_collision(target_rect):
            return False
        
        # 檢查建築物碰撞
        if self.check_building_collision(target_rect):
            return False
        
        # 檢查鐵軌碰撞（NPC不能上鐵軌）
        if self.railway_system.check_railway_collision(target_rect):
            return False
        
        return True

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
        繪製水體元素（移除釣魚點）\n
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
            
            # 繪製水邊資源
            for resource in water_area['resources']:
                if resource['collected']:
                    continue
                    
                rx, ry = resource['position']
                screen_x = rx - camera_x
                screen_y = ry - camera_y
                
                pygame.draw.circle(screen, resource['color'], (int(screen_x), int(screen_y)), 4)

    def draw_vegetable_gardens(self, screen, camera_x, camera_y):
        """
        繪製蔬果園\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        for garden in self.vegetable_gardens:
            gx, gy = garden['position']
            screen_x = gx - camera_x
            screen_y = gy - camera_y
            
            # 繪製蔬果園邊界
            garden_rect = pygame.Rect(screen_x, screen_y, garden['size'], garden['size'])
            pygame.draw.rect(screen, garden['color'], garden_rect)
            pygame.draw.rect(screen, (0, 100, 0), garden_rect, 2)
            
            # 繪製農作物
            for crop in garden['crops']:
                if crop['harvested']:
                    continue
                    
                cx, cy = crop['position']
                crop_screen_x = cx - camera_x
                crop_screen_y = cy - camera_y
                
                # 根據生長階段調整大小
                growth_factor = (garden['growth_stage'] + 1) / 4.0
                crop_size = max(2, int(4 * growth_factor))
                
                pygame.draw.circle(screen, crop['color'], 
                                 (int(crop_screen_x), int(crop_screen_y)), crop_size)
            
            # 如果可以收穫，顯示提示
            if garden['harvest_ready']:
                font = self.font_manager.get_font(12)
                ready_text = font.render("可收穫", True, (255, 255, 0))
                screen.blit(ready_text, (screen_x, screen_y - 15))

    def draw_farm_areas(self, screen, camera_x, camera_y):
        """
        繪製農地區域\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        for farm in self.farm_areas:
            fx, fy = farm['position']
            fw, fh = farm['size']
            
            # 計算螢幕位置
            screen_x = fx - camera_x
            screen_y = fy - camera_y
            
            # 檢查是否在螢幕範圍內
            if (screen_x + fw < 0 or screen_x > screen.get_width() or
                screen_y + fh < 0 or screen_y > screen.get_height()):
                continue
            
            # 繪製農地基底（已在地形層繪製，這裡添加細節）
            farm_rect = pygame.Rect(screen_x, screen_y, fw, fh)
            
            # 根據耕作狀態繪製不同效果
            if farm['is_tilled']:
                # 已耕作：繪製耕作溝紋
                num_furrows = 4  # 犁溝數量
                furrow_spacing = fh // num_furrows
                
                for i in range(num_furrows):
                    furrow_y = screen_y + i * furrow_spacing + furrow_spacing // 2
                    pygame.draw.line(screen, (139, 69, 19), 
                                   (screen_x + 2, furrow_y), 
                                   (screen_x + fw - 2, furrow_y), 1)
            else:
                # 未耕作：繪製雜草效果
                for i in range(8):
                    grass_x = screen_x + random.randint(2, fw - 2)
                    grass_y = screen_y + random.randint(2, fh - 2)
                    pygame.draw.circle(screen, (46, 125, 50), (grass_x, grass_y), 1)
            
            # 根據作物類型和生長階段繪製作物
            if farm['is_tilled'] and farm['growth_stage'] > 0:
                crop_color = self._get_crop_color(farm['crop_type'], farm['growth_stage'])
                crop_size = max(1, farm['growth_stage'])  # 生長階段決定大小
                
                # 在農田中繪製作物（簡化的網格排列）
                crops_per_row = 3
                crop_spacing_x = fw // (crops_per_row + 1)
                crop_spacing_y = fh // (crops_per_row + 1)
                
                for row in range(crops_per_row):
                    for col in range(crops_per_row):
                        crop_x = screen_x + (col + 1) * crop_spacing_x
                        crop_y = screen_y + (row + 1) * crop_spacing_y
                        
                        pygame.draw.circle(screen, crop_color, 
                                         (crop_x, crop_y), crop_size)
            
            # 繪製農地邊界（淡色）
            pygame.draw.rect(screen, (101, 67, 33), farm_rect, 1)

    def _get_crop_color(self, crop_type, growth_stage):
        """
        根據作物類型和生長階段獲取顏色\n
        \n
        參數:\n
        crop_type (str): 作物類型\n
        growth_stage (int): 生長階段 (0-4)\n
        \n
        回傳:\n
        tuple: RGB顏色值\n
        """
        # 基礎作物顏色
        base_colors = {
            'wheat': (255, 215, 0),      # 金黃色
            'corn': (255, 255, 0),       # 黃色
            'vegetables': (0, 128, 0),   # 綠色
            'rice': (154, 205, 50)       # 黃綠色
        }
        
        base_color = base_colors.get(crop_type, (0, 128, 0))
        
        # 根據生長階段調整顏色深淺
        growth_factor = growth_stage / 4.0
        
        # 早期階段更綠，成熟階段接近基礎顏色
        early_green = (46, 125, 50)
        
        # 插值計算最終顏色
        final_color = tuple(
            int(early_green[i] * (1 - growth_factor) + base_color[i] * growth_factor)
            for i in range(3)
        )
        
        return final_color

    def draw_buildings(self, screen, camera_x, camera_y, font_manager=None):
        """
        繪製所有建築\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        font_manager: 字體管理器（用於顯示家的文字）\n
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
            
            # 建築物名稱顯示已移除（依據新需求）
            
            # 玩家家的特殊文字顯示也已移除（依據新需求）

    def update(self, dt):
        """
        更新地形系統（主要更新鐵路系統和蔬果園）\n
        \n
        參數:\n
        dt (float): 時間增量\n
        """
        # 更新鐵路系統
        self.railway_system.update(dt)
        
        # 更新蔬果園（每日成熟檢查）
        self._update_vegetable_gardens()

    def get_statistics(self):
        """
        獲取系統統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊\n
        """
        railway_stats = self.railway_system.get_statistics()
        
        return {
            'map_size': f"{self.map_width}x{self.map_height}",
            'buildings': len(self.buildings),
            'residential_buildings': len(self.residential_buildings),
            'commercial_buildings': len(self.commercial_buildings),
            'vegetable_gardens': len(self.vegetable_gardens),  # 新增
            'forest_areas': len(self.forest_areas),
            'water_areas': len(self.water_areas),
            'train_stations': railway_stats['train_stations'],
            'trains': railway_stats['trains'],
            'railway_tracks': railway_stats['railway_tracks'],
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

    def get_areas_by_terrain_type(self, terrain_type):
        """
        獲取指定地形類型的所有區域\n
        \n
        參數:\n
        terrain_type (int): 地形代碼\n
        \n
        回傳:\n
        list: 區域列表，每個區域為 (x, y, width, height) 元組\n
        """
        areas = []
        visited = set()
        
        for y in range(self.map_height):
            for x in range(self.map_width):
                if (x, y) in visited:
                    continue
                
                if self.map_data[y][x] == terrain_type:
                    # 找到符合的地形，使用洪水填充算法找出整個區域
                    area = self._flood_fill_area(x, y, terrain_type, visited)
                    if area:
                        areas.append(area)
        
        return areas

    def _flood_fill_area(self, start_x, start_y, terrain_type, visited):
        """
        使用洪水填充算法計算連續地形區域\n
        \n
        參數:\n
        start_x (int): 起始X格子座標\n
        start_y (int): 起始Y格子座標\n
        terrain_type (int): 目標地形類型\n
        visited (set): 已訪問的格子集合\n
        \n
        回傳:\n
        tuple: (x, y, width, height) 區域邊界，使用世界座標\n
        """
        if (start_x, start_y) in visited:
            return None
        
        if (start_x < 0 or start_x >= self.map_width or 
            start_y < 0 or start_y >= self.map_height):
            return None
        
        if self.map_data[start_y][start_x] != terrain_type:
            return None
        
        # BFS 洪水填充
        queue = [(start_x, start_y)]
        area_cells = []
        
        while queue:
            x, y = queue.pop(0)
            
            if (x, y) in visited:
                continue
            
            if (x < 0 or x >= self.map_width or 
                y < 0 or y >= self.map_height):
                continue
            
            if self.map_data[y][x] != terrain_type:
                continue
            
            visited.add((x, y))
            area_cells.append((x, y))
            
            # 檢查四個方向的鄰接格子
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    queue.append((nx, ny))
        
        if not area_cells:
            return None
        
        # 計算區域邊界
        min_x = min(cell[0] for cell in area_cells)
        max_x = max(cell[0] for cell in area_cells)
        min_y = min(cell[1] for cell in area_cells)
        max_y = max(cell[1] for cell in area_cells)
        
        # 轉換為世界座標
        world_x = min_x * self.tile_size
        world_y = min_y * self.tile_size
        world_width = (max_x - min_x + 1) * self.tile_size
        world_height = (max_y - min_y + 1) * self.tile_size
        
        return (world_x, world_y, world_width, world_height)

    def check_tree_collision(self, player_rect):
        """
        檢查玩家與樹木的碰撞\n
        \n
        參數:\n
        player_rect (pygame.Rect): 玩家的碰撞矩形\n
        \n
        回傳:\n
        bool: 如果與樹木碰撞則回傳 True\n
        """
        for forest_area in self.forest_areas:
            for tree in forest_area['trees']:
                if player_rect.colliderect(tree['collision_rect']):
                    return True
        return False

    def check_water_collision(self, world_x, world_y):
        """
        檢查指定位置是否為水域（不可通行）\n
        \n
        參數:\n
        world_x (float): 世界座標 X\n
        world_y (float): 世界座標 Y\n
        \n
        回傳:\n
        bool: 如果是水域則回傳 True\n
        """
        terrain_type = self.get_terrain_at_position(world_x, world_y)
        return terrain_type == 2  # 地形代碼2為水域

    def can_move_to_position(self, world_x, world_y, entity_rect):
        """
        檢查實體是否可以移動到指定位置\n
        \n
        參數:\n
        world_x (float): 目標世界座標 X\n
        world_y (float): 目標世界座標 Y\n
        entity_rect (pygame.Rect): 實體的碰撞矩形\n
        \n
        回傳:\n
        bool: 如果可以移動則回傳 True\n
        """
        # 檢查水域碰撞
        if self.check_water_collision(world_x, world_y):
            return False
        
        # 創建目標位置的矩形
        target_rect = pygame.Rect(world_x - entity_rect.width//2, world_y - entity_rect.height//2, 
                                entity_rect.width, entity_rect.height)
        
        # 檢查樹木碰撞
        if self.check_tree_collision(target_rect):
            return False
        
        # 檢查建築物碰撞
        if self.check_building_collision(target_rect):
            return False
        
        return True

    def check_building_collision(self, entity_rect):
        """
        檢查實體是否與建築物發生碰撞\n
        \n
        參數:\n
        entity_rect (pygame.Rect): 實體的碰撞矩形\n
        \n
        回傳:\n
        bool: 如果發生碰撞則回傳 True\n
        """
        # 檢查所有建築物
        for building in self.buildings:
            building_rect = pygame.Rect(building.x, building.y, building.width, building.height)
            if entity_rect.colliderect(building_rect):
                return True
        
        return False

    def get_nearby_tree(self, player_position, max_distance=30):
        """
        獲取玩家附近的樹木\n
        \n
        參數:\n
        player_position (tuple): 玩家位置 (x, y)\n
        max_distance (float): 最大距離\n
        \n
        回傳:\n
        dict: 最近的樹木資訊，如果沒有則回傳 None\n
        """
        px, py = player_position
        closest_tree = None
        closest_distance = float('inf')
        
        for forest_area in self.forest_areas:
            for i, tree in enumerate(forest_area['trees']):
                tx, ty = tree['position']
                distance = math.sqrt((px - tx) ** 2 + (py - ty) ** 2)
                
                if distance <= max_distance and distance < closest_distance:
                    closest_distance = distance
                    closest_tree = {
                        'tree': tree,
                        'forest_area': forest_area,
                        'tree_index': i,
                        'distance': distance
                    }
        
        return closest_tree

    def chop_tree(self, player, tree_info):
        """
        砍伐樹木\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        tree_info (dict): 樹木資訊（由 get_nearby_tree 回傳）\n
        \n
        回傳:\n
        dict: 砍伐結果\n
        """
        if tree_info is None:
            return {'success': False, 'message': '附近沒有樹木可以砍伐'}
        
        # 移除樹木
        forest_area = tree_info['forest_area']
        tree_index = tree_info['tree_index']
        tree = tree_info['tree']
        
        # 從森林區域中移除樹木
        forest_area['trees'].pop(tree_index)
        
        # 給玩家獎勵
        player.add_money(100)
        
        print(f"🪓 砍伐了一棵樹木，獲得 100 元！")
        
        return {
            'success': True,
            'message': '砍伐成功！獲得 100 元',
            'money_earned': 100
        }

    def draw_railway_elements(self, screen, camera_x, camera_y, font_manager):
        """
        繪製鐵路系統元素\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        font_manager: 字體管理器\n
        """
        # 繪製鐵軌
        self.railway_system.draw_railway_tracks(screen, camera_x, camera_y)
        
        # 繪製火車站
        self.railway_system.draw_stations(screen, camera_x, camera_y, font_manager)
        
        # 繪製火車
        self.railway_system.draw_trains(screen, camera_x, camera_y)

    def handle_railway_click(self, click_position, player):
        """
        處理鐵路相關的點擊事件\n
        \n
        參數:\n
        click_position (tuple): 點擊位置 (x, y)\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 如果處理了點擊事件則回傳True\n
        """
        return self.railway_system.handle_station_click(click_position, player)
    
    def check_player_near_railway_station(self, player_position):
        """
        檢查玩家是否在火車站附近 - 自動顯示傳送選項\n
        \n
        參數:\n
        player_position (tuple): 玩家位置 (x, y)\n
        \n
        回傳:\n
        TrainStation: 如果在車站附近則回傳車站物件，否則回傳None\n
        """
        return self.railway_system.check_player_near_station(player_position)

    def can_player_cross_railway(self, position):
        """
        檢查玩家是否可以穿越鐵軌（通過斑馬線）\n
        \n
        參數:\n
        position (tuple): 玩家位置 (x, y)\n
        \n
        回傳:\n
        bool: 如果可以通行則回傳True\n
        """
        return self.railway_system.can_cross_railway(position)
    
    def _update_vegetable_gardens(self):
        """
        更新蔬果園狀態\n
        根據新需求：蔬果園每天成熟一次\n
        """
        # 這裡需要從時間管理器獲取當前遊戲日
        # 暫時使用簡單的計數器模擬日期變化
        if not hasattr(self, '_garden_update_counter'):
            self._garden_update_counter = 0
        
        self._garden_update_counter += 1
        
        # 每1800幀（約30秒）模擬一天
        if self._garden_update_counter >= 1800:
            self._garden_update_counter = 0
            current_day = getattr(self, '_current_game_day', 0) + 1
            self._current_game_day = current_day
            
            # 更新所有蔬果園
            for garden in self.vegetable_gardens:
                if garden['last_harvest_day'] < current_day:
                    # 重置農作物為可收穫狀態
                    garden['harvest_ready'] = True
                    garden['growth_stage'] = 3  # 完全成熟
                    for crop in garden['crops']:
                        crop['harvested'] = False
    
    def harvest_vegetable_garden(self, player_position, player):
        """
        採摘蔬果園\n
        根據新需求：玩家右鍵採摘，獲得 10 元收益\n
        \n
        參數:\n
        player_position (tuple): 玩家位置 (x, y)\n
        player: 玩家物件\n
        \n
        回傳:\n
        dict: 採摘結果\n
        """
        px, py = player_position
        
        for garden in self.vegetable_gardens:
            gx, gy = garden['position']
            garden_rect = pygame.Rect(gx, gy, garden['size'], garden['size'])
            
            # 檢查玩家是否在蔬果園附近
            if garden_rect.collidepoint(px, py):
                if garden['harvest_ready']:
                    # 計算收穫數量
                    unharvested_crops = [crop for crop in garden['crops'] if not crop['harvested']]
                    if unharvested_crops:
                        # 標記所有農作物為已收穫
                        for crop in garden['crops']:
                            crop['harvested'] = True
                        
                        # 標記蔬果園為已收穫
                        garden['harvest_ready'] = False
                        garden['growth_stage'] = 0
                        garden['last_harvest_day'] = getattr(self, '_current_game_day', 0)
                        
                        # 給予玩家金錢
                        harvest_income = VEGETABLE_GARDEN_HARVEST_INCOME
                        player.add_money(harvest_income)
                        
                        return {
                            'success': True,
                            'message': f"收穫蔬果園，獲得 ${harvest_income}！",
                            'income': harvest_income
                        }
                    else:
                        return {
                            'success': False,
                            'message': "這個蔬果園已經收穫過了"
                        }
                else:
                    return {
                        'success': False,
                        'message': "蔬果園還沒有成熟，請等待"
                    }
        
        return {
            'success': False,
            'message': "附近沒有蔬果園"
        }
    
    def get_nearby_vegetable_garden(self, player_position, max_distance=50):
        """
        獲取附近的蔬果園資訊\n
        \n
        參數:\n
        player_position (tuple): 玩家位置 (x, y)\n
        max_distance (float): 最大檢測距離\n
        \n
        回傳:\n
        dict: 蔬果園資訊，如果沒有則回傳None\n
        """
        px, py = player_position
        
        for garden in self.vegetable_gardens:
            gx, gy = garden['position']
            distance = math.sqrt((px - gx) ** 2 + (py - gy) ** 2)
            
            if distance <= max_distance:
                return garden
        
        return None