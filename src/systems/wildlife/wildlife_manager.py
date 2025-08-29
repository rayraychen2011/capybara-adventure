######################載入套件######################
import pygame
import random
import time
import math
from src.systems.wildlife.animal import Animal, AnimalState
from src.systems.wildlife.animal_data import AnimalType, AnimalData, RarityLevel
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


######################野生動物管理器######################
class WildlifeManager:
    """
    野生動物管理器\n
    \n
    負責管理遊戲中的所有野生動物\n
    包含動物生成、行為更新、互動檢測和環境模擬\n
    \n
    主要功能:\n
    1. 動物群體生成和管理\n
    2. 動物 AI 行為協調\n
    3. 玩家與動物互動\n
    4. 狩獵和釣魚機制\n
    5. 保育系統執行\n
    """

    def _handle_animal_attack_player(self, animal, player_position):
        """
        處理動物攻擊玩家事件\n
        \n
        參數:\n
        animal (Animal): 攻擊的動物\n
        player_position (tuple): 玩家位置\n
        """
        # 使用動物的攻擊傷害
        damage = animal.get_damage()
        
        # 這個方法需要由外部場景系統調用，因為野生動物管理器沒有直接的玩家引用
        # 設置一個回調機制供外部系統處理
        if hasattr(self, 'player_attack_callback') and self.player_attack_callback:
            self.player_attack_callback(damage, animal)
            print(f"{animal.animal_type.value} 對玩家造成了 {damage} 點傷害！")

    def set_player_attack_callback(self, callback):
        """
        設置玩家被攻擊時的回調函數\n
        \n
        參數:\n
        callback (function): 回調函數，接收 (damage, source) 參數\n
        """
        self.player_attack_callback = callback

    def __init__(self):
        """
        初始化野生動物管理器\n
        """
        # 動物群體容器
        self.forest_animals = []  # 森林動物 (地形代碼1)
        self.lake_animals = []  # 湖泊動物 (地形代碼2)
        self.all_animals = []  # 所有動物的統一列表

        print("野生動物管理器初始化完成")

        # 新的動物數量控制（按稀有度）
        self.target_counts = {
            RarityLevel.RARE: 20,       # 稀有動物20隻
            RarityLevel.SUPER_RARE: 10, # 超稀動物10隻
            RarityLevel.LEGENDARY: 5    # 傳奇動物5隻
        }
        
        self.current_counts = {
            RarityLevel.RARE: 0,
            RarityLevel.SUPER_RARE: 0,
            RarityLevel.LEGENDARY: 0
        }

        # 生成控制
        self.spawn_cooldown = 3.0  # 生成冷卻時間 (秒)
        self.last_spawn_time = 0  # 上次生成時間

        # 兼容性屬性（用於舊代碼）
        self.max_forest_animals = 25
        self.max_lake_animals = 10

        # 環境邊界 (會從場景傳入)
        self.forest_bounds = (100, 100, 600, 400)  # 森林區域邊界
        self.lake_bounds = (200, 200, 400, 300)  # 湖泊區域邊界

        # 地形系統引用 - 用於檢查地形代碼
        self.terrain_system = None
        
        # 小鎮中心位置（用於計算距離）
        self.town_center = (2000, 3000)  # 小鎮中心座標

        # 互動檢測
        self.interaction_range = 50  # 玩家互動範圍
        self.hunting_range = 40  # 狩獵攻擊範圍
        self.fishing_range = 60  # 釣魚範圍

        # 統計資料
        self.total_spawned = 0  # 總生成數量
        self.total_hunted = 0  # 總狩獵數量
        self.total_fished = 0  # 總釣魚數量
        
    def set_terrain_system(self, terrain_system):
        """設置地形系統引用"""
        self.terrain_system = terrain_system
        
    def set_world_bounds(self, bounds):
        """設置世界邊界"""
        self.forest_bounds = bounds
        self.lake_bounds = bounds
        
    def get_wildlife_statistics(self):
        """獲取野生動物統計信息"""
        return {
            "total_animals": len(self.all_animals),
            "forest_animals": len(self.forest_animals),
            "lake_animals": len(self.lake_animals),
            "rare_count": self.current_counts.get(RarityLevel.RARE, 0),
            "super_rare_count": self.current_counts.get(RarityLevel.SUPER_RARE, 0),
            "legendary_count": self.current_counts.get(RarityLevel.LEGENDARY, 0)
        }

    @property
    def animals(self):
        """
        獲取所有動物的統一列表\n
        \n
        回傳:\n
        list: 所有動物的列表\n
        """
        # 實時合併所有動物列表
        all_animals = []
        all_animals.extend(self.forest_animals)
        all_animals.extend(self.lake_animals)
        all_animals.extend(self.all_animals)
        
        # 去重（使用ID確保唯一性）
        unique_animals = []
        seen_ids = set()
        for animal in all_animals:
            if hasattr(animal, 'id') and animal.id not in seen_ids:
                unique_animals.append(animal)
                seen_ids.add(animal.id)
            elif not hasattr(animal, 'id'):
                unique_animals.append(animal)
        
        return unique_animals

    def set_habitat_bounds(self, forest_bounds, lake_bounds):
        """
        設定棲息地邊界\n
        \n
        參數:\n
        forest_bounds (tuple): 森林邊界 (x, y, width, height)\n
        lake_bounds (tuple): 湖泊邊界 (x, y, width, height)\n
        """
        self.forest_bounds = forest_bounds
        self.lake_bounds = lake_bounds
        print(f"設定棲息地邊界 - 森林: {forest_bounds}, 湖泊: {lake_bounds}")

    def set_terrain_system(self, terrain_system):
        """
        設定地形系統引用\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統實例\n
        """
        self.terrain_system = terrain_system
        print("野生動物管理器已連結地形系統")

    def _find_terrain_positions(self, terrain_code, max_positions=20):
        """
        找出指定地形代碼的位置\n
        \n
        參數:\n
        terrain_code (int): 地形代碼 (1=森林, 2=水域)\n
        max_positions (int): 最大搜尋位置數量\n
        \n
        回傳:\n
        list: 符合地形代碼的位置列表 [(x, y), ...]\n
        """
        if not self.terrain_system:
            return []
        
        positions = []
        map_width = self.terrain_system.map_width
        map_height = self.terrain_system.map_height
        tile_size = self.terrain_system.tile_size
        
        # 隨機搜尋地形位置
        attempts = 0
        max_attempts = max_positions * 10  # 避免無限迴圈
        
        while len(positions) < max_positions and attempts < max_attempts:
            attempts += 1
            
            # 隨機選擇一個位置
            tile_x = random.randint(0, map_width - 1)
            tile_y = random.randint(0, map_height - 1)
            
            # 轉換為世界座標
            world_x = tile_x * tile_size + tile_size // 2
            world_y = tile_y * tile_size + tile_size // 2
            
            # 檢查地形代碼
            if self.terrain_system.get_terrain_at_position(world_x, world_y) == terrain_code:
                positions.append((world_x, world_y))
        
        return positions

    def initialize_animals(self, scene_type="all"):
        """
        初始化動物生成系統 - 新的分佈式生成\n
        \n
        參數:\n
        scene_type (str): 場景類型 ("forest", "lake", "grassland", "all")\n
        """
        if not self.terrain_system:
            print("警告：沒有地形系統，使用簡化的動物生成")

        print("開始初始化野生動物...")
        
        # 清空現有動物
        self.forest_animals.clear()
        self.lake_animals.clear() 
        self.all_animals.clear()
        self.current_counts = {rarity: 0 for rarity in RarityLevel}

        # 按稀有度生成動物
        self._generate_animals_by_rarity()

        total_animals = len(self.all_animals)
        print(f"野生動物初始化完成：")
        print(f"  稀有動物: {self.current_counts[RarityLevel.RARE]}/{self.target_counts[RarityLevel.RARE]}")
        print(f"  超稀動物: {self.current_counts[RarityLevel.SUPER_RARE]}/{self.target_counts[RarityLevel.SUPER_RARE]}")  
        print(f"  傳奇動物: {self.current_counts[RarityLevel.LEGENDARY]}/{self.target_counts[RarityLevel.LEGENDARY]}")
        print(f"  總計: {total_animals} 隻動物")

    def _generate_animals_by_rarity(self):
        """按稀有度生成動物"""
        
        # 稀有動物 (20隻)
        rare_animals = AnimalData.get_animals_by_rarity(RarityLevel.RARE)
        for animal_type in rare_animals:
            count_per_type = self.target_counts[RarityLevel.RARE] // len(rare_animals)
            
            for _ in range(count_per_type):
                # 根據動物類型選擇棲息地
                if animal_type == AnimalType.TURTLE:
                    habitat = "lake"
                elif animal_type == AnimalType.SHEEP:
                    habitat = "grassland"
                else:
                    habitat = "forest"
                
                self._spawn_animal(animal_type, habitat)
        
        # 超稀動物 (10隻)  
        super_rare_animals = AnimalData.get_animals_by_rarity(RarityLevel.SUPER_RARE)
        for animal_type in super_rare_animals:
            count_per_type = self.target_counts[RarityLevel.SUPER_RARE] // len(super_rare_animals)
            
            for _ in range(count_per_type):
                habitat = "forest"  # 超稀動物主要在森林
                self._spawn_animal(animal_type, habitat)
        
        # 傳奇動物 (5隻)
        legendary_animals = AnimalData.get_animals_by_rarity(RarityLevel.LEGENDARY)
        for animal_type in legendary_animals:
            count_per_type = self.target_counts[RarityLevel.LEGENDARY] // len(legendary_animals)
            
            for _ in range(count_per_type):
                habitat = "forest"  # 傳奇動物在森林深處
                self._spawn_animal(animal_type, habitat)

        print(
            f"初始化完成：森林動物 {len(self.forest_animals)} 隻，湖泊動物 {len(self.lake_animals)} 隻，草原動物將分散在地圖各處"
        )

    def _spawn_animal(self, animal_type, habitat, position=None):
        """
        生成新動物 - 基於地形代碼和距離的位置選擇\n
        \n
        參數:\n
        animal_type (AnimalType): 動物種類\n
        habitat (str): 棲息地類型 ("forest", "lake", 或 "grassland")\n
        position (tuple): 指定位置，如果為None則自動選擇\n
        \n
        回傳:\n
        Animal: 生成的動物物件\n
        """
        # 檢查稀有度數量限制
        rarity = AnimalData.get_animal_property(animal_type, "rarity")
        if rarity and self.current_counts.get(rarity, 0) >= self.target_counts.get(rarity, 0):
            return None  # 達到該稀有度的數量上限

        # 根據棲息地選擇地形代碼
        if habitat == "forest":
            terrain_codes = [1, 9]  # 森林、山丘
            bounds = self.forest_bounds
        elif habitat == "lake":
            terrain_codes = [2]  # 水域
            bounds = self.lake_bounds
        elif habitat == "grassland":
            terrain_codes = [0, 7, 8]  # 草地、公園、農地
            bounds = self.forest_bounds
        else:
            print(f"未知的棲息地類型: {habitat}")
            return None

        # 選擇生成位置
        if position:
            x, y = position
        else:
            x, y = self._select_spawn_position(animal_type, terrain_codes, rarity)
            if x is None:
                print(f"無法為 {animal_type.value} 找到合適的生成位置")
                return None

        # 創建動物
        animal = Animal(animal_type, (x, y), bounds, habitat)
        
        # 設定地形系統引用
        if self.terrain_system:
            animal.set_terrain_system(self.terrain_system)

        # 添加到對應容器
        if habitat == "lake":
            self.lake_animals.append(animal)
        else:
            self.forest_animals.append(animal)
        
        self.all_animals.append(animal)
        
        # 更新數量統計
        if rarity:
            self.current_counts[rarity] = self.current_counts.get(rarity, 0) + 1
        
        self.total_spawned += 1

        print(f"在 {habitat} 生成 {animal_type.value}，距離小鎮: {self._distance_to_town(x, y):.0f}m")
        return animal

    def _select_spawn_position(self, animal_type, terrain_codes, rarity):
        """
        基於地形和均勻分布選擇生成位置\n
        新需求：確保動物在地圖上均勻分布，避免聚集在某些區域\n
        \n
        參數:\n
        animal_type (AnimalType): 動物種類\n
        terrain_codes (list): 允許的地形代碼\n
        rarity (RarityLevel): 稀有度\n
        \n
        回傳:\n
        tuple: (x, y) 位置座標，如果找不到則返回 (None, None)\n
        """
        if not self.terrain_system:
            # 沒有地形系統時使用簡單生成
            bounds = self.forest_bounds
            x = random.randint(bounds[0] + 30, bounds[0] + bounds[2] - 30)
            y = random.randint(bounds[1] + 30, bounds[1] + bounds[3] - 30)
            return x, y

        # 將地圖劃分為網格以確保均勻分布
        grid_size = 10  # 將地圖劃分為 10x10 的網格
        cell_width = self.terrain_system.map_width // grid_size
        cell_height = self.terrain_system.map_height // grid_size
        
        # 記錄每個網格已生成的動物數量
        if not hasattr(self, '_spawn_grid'):
            self._spawn_grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        
        # 找到動物數量最少的網格區域
        min_count = float('inf')
        candidate_cells = []
        
        for grid_y in range(grid_size):
            for grid_x in range(grid_size):
                current_count = self._spawn_grid[grid_y][grid_x]
                if current_count < min_count:
                    min_count = current_count
                    candidate_cells = [(grid_x, grid_y)]
                elif current_count == min_count:
                    candidate_cells.append((grid_x, grid_y))
        
        # 從候選網格中選擇一個進行生成
        attempts = 0
        max_attempts = 50
        
        while attempts < max_attempts and candidate_cells:
            # 隨機選擇一個候選網格
            grid_cell_x, grid_cell_y = random.choice(candidate_cells)
            
            # 在該網格內尋找合適的生成位置
            start_x = grid_cell_x * cell_width
            start_y = grid_cell_y * cell_height
            end_x = min((grid_cell_x + 1) * cell_width, self.terrain_system.map_width - 1)
            end_y = min((grid_cell_y + 1) * cell_height, self.terrain_system.map_height - 1)
            
            # 在網格內隨機選擇位置
            for _ in range(20):  # 在該網格內最多嘗試20次
                grid_x = random.randint(start_x, end_x)
                grid_y = random.randint(start_y, end_y)
                
                # 檢查地形是否合適
                world_x = grid_x * 20 + 10
                world_y = grid_y * 20 + 10
                terrain_code = self.terrain_system.get_terrain_at_world_pos(world_x, world_y)
                
                if terrain_code in terrain_codes:
                    # 檢查是否與現有動物過於靠近（最小距離100像素）
                    min_distance = 100
                    too_close = False
                    
                    for existing_animal in self.all_animals:
                        distance = math.sqrt((world_x - existing_animal.x)**2 + (world_y - existing_animal.y)**2)
                        if distance < min_distance:
                            too_close = True
                            break
                    
                    if not too_close:
                        # 更新網格計數
                        self._spawn_grid[grid_cell_y][grid_cell_x] += 1
                        print(f"在網格 ({grid_cell_x}, {grid_cell_y}) 生成 {animal_type.value}，距離其他動物 > {min_distance}px")
                        return world_x, world_y
            
            attempts += 1
        
        # 如果均勻分布失敗，使用原有的簡單隨機生成
        print(f"均勻分布生成失敗，使用隨機位置生成 {animal_type.value}")
        for _ in range(50):
            grid_x = random.randint(0, self.terrain_system.map_width - 1)
            grid_y = random.randint(0, self.terrain_system.map_height - 1)
            world_x = grid_x * 20 + 10
            world_y = grid_y * 20 + 10
            terrain_code = self.terrain_system.get_terrain_at_world_pos(world_x, world_y)
            if terrain_code in terrain_codes:
                return world_x, world_y
        
        return None, None

    def _distance_to_town(self, x, y):
        """計算到小鎮中心的距離"""
        dx = x - self.town_center[0]
        dy = y - self.town_center[1]
        return math.sqrt(dx * dx + dy * dy)

    def _is_near_water(self, grid_x, grid_y, radius=3):
        """檢查位置是否靠近水邊"""
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                check_x = grid_x + dx
                check_y = grid_y + dy
                if (0 <= check_x < self.terrain_system.map_width and 
                    0 <= check_y < self.terrain_system.map_height):
                    world_x = check_x * 20 + 10
                    world_y = check_y * 20 + 10
                    if self.terrain_system.get_terrain_at_world_pos(world_x, world_y) == 2:  # 水體
                        return True
        return False

    def update(self, dt, player_position, current_scene):
        """
        更新野生動物管理器\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        player_position (tuple): 玩家位置 (x, y)\n
        current_scene (str): 當前場景名稱\n
        """
        # 根據場景決定要更新的動物群體
        if current_scene in ["forest", "town"]:  # 小鎮場景也包含森林動物
            active_animals = self.forest_animals
        elif current_scene in ["lake", "town"]:  # 小鎮場景也包含湖泊動物
            if current_scene == "town":
                # 在小鎮場景中，同時更新森林和湖泊動物
                forest_animals = self.forest_animals
                lake_animals = self.lake_animals
                active_animals = forest_animals + lake_animals
            else:
                active_animals = self.lake_animals
        else:
            active_animals = []  # 其他場景沒有野生動物

        # 更新動物行為
        for animal in active_animals[:]:  # 使用切片複製，防止修改列表時出錯
            if animal.is_alive:
                animal.update(dt, player_position)
                
                # 檢查動物是否攻擊了玩家
                if hasattr(animal, 'has_attacked_player') and animal.has_attacked_player:
                    self._handle_animal_attack_player(animal, player_position)
                    animal.has_attacked_player = False  # 重置攻擊標記
            else:
                # 移除死亡動物 (延遲一段時間)
                if time.time() - animal.death_time > 10:  # 死亡10秒後移除
                    self._remove_animal(animal)

        # 嘗試生成新動物
        self._attempt_spawn_animals(current_scene)

    def _attempt_spawn_animals(self, current_scene):
        """
        嘗試生成新動物\n
        \n
        參數:\n
        current_scene (str): 當前場景\n
        """
        current_time = time.time()

        # 檢查生成冷卻
        if current_time - self.last_spawn_time < self.spawn_cooldown:
            return

        # 在小鎮場景或森林場景生成森林動物
        if (
            current_scene in ["forest", "town"]
            and len(self.forest_animals) < self.max_forest_animals
        ):
            # 選擇森林動物種類 (根據稀有度加權)
            spawn_weights = {
                AnimalType.MOUNTAIN_LION: 8,  # 超稀有，少見
                AnimalType.BLACK_PANTHER: 6,  # 超稀有，少見
                AnimalType.BEAR: 2,           # 傳奇，稀有
            }

            animal_type = self._weighted_random_choice(spawn_weights)
            if animal_type:
                self._spawn_animal(animal_type, "forest")
                self.last_spawn_time = current_time

        # 在小鎮場景生成草原動物
        elif current_scene == "town":
            # 隨機決定生成草原動物或湖泊動物
            if random.choice([True, False]):  # 50% 機率生成草原動物
                # 選擇草原動物種類 
                spawn_weights = {
                    AnimalType.RABBIT: 35,        # 兔子喜歡草原
                    AnimalType.SHEEP: 30,         # 羊群在草原覓食
                }

                animal_type = self._weighted_random_choice(spawn_weights)
                if animal_type:
                    self._spawn_animal(animal_type, "grassland")
                    self.last_spawn_time = current_time
            else:
                # 生成湖泊動物
                if len(self.lake_animals) < self.max_lake_animals:
                    spawn_weights = {
                        AnimalType.TURTLE: 25,  # 稀有，很常見
                    }

                    animal_type = self._weighted_random_choice(spawn_weights)
                    if animal_type:
                        self._spawn_animal(animal_type, "lake")
                        self.last_spawn_time = current_time

        # 在湖泊場景生成湖泊動物
        elif (
            current_scene == "lake" 
            and len(self.lake_animals) < self.max_lake_animals
        ):
            # 選擇湖泊動物種類
            spawn_weights = {
                AnimalType.TURTLE: 25,  # 稀有，很常見
            }

            animal_type = self._weighted_random_choice(spawn_weights)
            if animal_type:
                self._spawn_animal(animal_type, "lake")
                self.last_spawn_time = current_time

    def _weighted_random_choice(self, weights_dict):
        """
        根據權重隨機選擇\n
        \n
        參數:\n
        weights_dict (dict): 選項和權重的字典\n
        \n
        回傳:\n
        object: 隨機選中的選項\n
        """
        items = list(weights_dict.keys())
        weights = list(weights_dict.values())
        total_weight = sum(weights)

        if total_weight <= 0:
            return None

        rand_value = random.uniform(0, total_weight)
        cumulative = 0

        for item, weight in zip(items, weights):
            cumulative += weight
            if rand_value <= cumulative:
                return item

        return items[-1]  # 後備選項

    def _remove_animal(self, animal):
        """
        移除動物\n
        \n
        參數:\n
        animal (Animal): 要移除的動物\n
        """
        if animal in self.forest_animals:
            self.forest_animals.remove(animal)
        if animal in self.lake_animals:
            self.lake_animals.remove(animal)
        if animal in self.all_animals:
            self.all_animals.remove(animal)

        print(f"移除動物: {animal.animal_type.value} (ID: {animal.id})")

    def get_animals_in_scene(self, scene_name):
        """
        獲取指定場景的動物列表\n
        \n
        參數:\n
        scene_name (str): 場景名稱\n
        \n
        回傳:\n
        list: 動物列表\n
        """
        if scene_name == "forest":
            return self.forest_animals
        elif scene_name == "lake":
            return self.lake_animals
        else:
            return []

    def get_nearby_animals(self, position, max_distance, scene_name):
        """
        獲取指定範圍內的動物\n
        \n
        參數:\n
        position (tuple): 中心位置 (x, y)\n
        max_distance (float): 最大距離\n
        scene_name (str): 場景名稱\n
        \n
        回傳:\n
        list: 附近的動物列表\n
        """
        nearby_animals = []
        animals = self.get_animals_in_scene(scene_name)
        px, py = position

        for animal in animals:
            if not animal.is_alive:
                continue

            ax, ay = animal.get_position()
            distance = ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5

            if distance <= max_distance:
                nearby_animals.append(animal)

        return nearby_animals

    def attempt_hunting(self, player_position, player):
        """
        嘗試狩獵動物\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 狩獵結果 {\n
            'success': bool - 是否成功\n
            'animal': Animal - 被狩獵的動物\n
            'loot': list - 獲得的戰利品\n
            'penalty': str - 懲罰訊息 (如果有)\n
        }\n
        """
        # 檢查玩家是否有狩獵工具
        # (這裡假設狩獵邏輯，實際需要整合玩家物品系統)

        # 尋找攻擊範圍內的動物
        nearby_animals = self.get_nearby_animals(
            player_position, self.hunting_range, "forest"
        )

        if not nearby_animals:
            return {"success": False, "animal": None, "loot": [], "penalty": None}

        # 選擇最近的動物
        target_animal = min(
            nearby_animals,
            key=lambda a: (
                (a.x - player_position[0]) ** 2 + (a.y - player_position[1]) ** 2
            ),
        )

        # 執行狩獵攻擊
        hunting_damage = 50  # 基礎狩獵傷害
        target_animal.take_damage(hunting_damage, player)

        # 檢查動物是否死亡
        if not target_animal.is_alive:
            self.total_hunted += 1

            # 獲取戰利品
            loot = target_animal.drop_items.copy()

            # 根據動物稀有度獲得獎勵金額
            rarity = AnimalData.get_animal_property(target_animal.animal_type, "rarity")
            reward_money = AnimalData.get_animal_rarity_value(rarity)
            
            # 給玩家金錢獎勵
            if hasattr(player, 'money'):
                player.money += reward_money
                print(f"獵殺 {target_animal.animal_type.value} 獲得 {reward_money} 元")

            return {
                "success": True,
                "animal": target_animal,
                "loot": loot,
                "reward_money": reward_money,
                "penalty": None,
            }
        else:
            return {
                "success": True,
                "animal": target_animal,
                "loot": [],
                "reward_money": 0,
                "penalty": None,
            }

    def attempt_fishing(self, player_position, player):
        """
        嘗試釣魚\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 釣魚結果 {\n
            'success': bool - 是否釣到魚\n
            'fish': Animal - 釣到的魚\n
            'loot': list - 獲得的戰利品\n
            'penalty': str - 懲罰訊息 (如果有)\n
        }\n
        """
        # 釣魚系統已簡化，專注於陸地動物狩獵
        return {"success": False, "fish": None, "loot": [], "penalty": None}

    def get_statistics(self):
        """
        獲取野生動物統計資料\n
        \n
        回傳:\n
        dict: 統計資料\n
        """
        return {
            "total_spawned": self.total_spawned,
            "total_hunted": self.total_hunted,
            "total_fished": self.total_fished,
            "forest_animals": len(self.forest_animals),
            "lake_animals": len(self.lake_animals),
        }

    def draw_all_animals(self, screen, scene_name, camera_offset=(0, 0)):
        """
        繪製指定場景的所有動物\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        scene_name (str): 場景名稱\n
        camera_offset (tuple): 攝影機偏移 (camera_x, camera_y)\n
        """
        # 根據場景決定要繪製的動物
        if scene_name in ["forest", "town"]:
            animals_to_draw = self.forest_animals + self.lake_animals  # 小鎮場景繪製所有動物
        elif scene_name == "lake":
            animals_to_draw = self.lake_animals
        else:
            animals_to_draw = []

        camera_x, camera_y = camera_offset

        for animal in animals_to_draw:
            if animal.is_alive:
                # 計算動物在螢幕上的位置
                screen_x = animal.x - camera_x
                screen_y = animal.y - camera_y
                
                # 只繪製在螢幕範圍內的動物
                if -50 <= screen_x <= SCREEN_WIDTH + 50 and -50 <= screen_y <= SCREEN_HEIGHT + 50:
                    # 暫時設定動物的螢幕位置然後繪製
                    original_x, original_y = animal.x, animal.y
                    animal.x, animal.y = screen_x, screen_y
                    animal.draw(screen)
                    animal.x, animal.y = original_x, original_y

    def draw_debug_info(self, screen, font, scene_name):
        """
        繪製除錯資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體物件\n
        scene_name (str): 場景名稱\n
        """
        animals = self.get_animals_in_scene(scene_name)
        stats = self.get_statistics()

        # 顯示統計資料
        y_offset = 10
        info_texts = [
            f"場景動物數量: {len(animals)}",
            f"總生成: {stats['total_spawned']}",
            f"總狩獵: {stats['total_hunted']}",
            f"總釣魚: {stats['total_fished']}",
            f"保育類擊殺: {stats['protected_kills']}",
        ]

        for text in info_texts:
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 25

        # 顯示動物詳細資訊
        for i, animal in enumerate(animals[:5]):  # 只顯示前5隻動物的資訊
            if animal.is_alive:
                rarity = AnimalData.get_animal_property(animal.animal_type, "rarity")
                rarity_text = rarity.value if rarity else "未知"
                info_text = f"{animal.animal_type.value}: {animal.state.value} [{rarity_text}]"

                text_surface = font.render(info_text, True, (200, 200, 200))
                screen.blit(text_surface, (10, y_offset))
                y_offset += 20

    def is_player_in_legendary_territory(self, player_position):
        """
        檢查玩家是否在傳奇動物的領地範圍內\n
        \n
        參數:\n
        player_position (tuple): 玩家位置 (x, y)\n
        \n
        回傳:\n
        bool: 是否在傳奇動物領地\n
        """
        for animal in self.all_animals:
            # 檢查是否為傳奇動物且有領地
            if (hasattr(animal, 'rarity') and 
                animal.rarity == RarityLevel.LEGENDARY and
                hasattr(animal, 'territory_radius')):
                
                # 計算玩家與動物的距離
                distance = ((player_position[0] - animal.x) ** 2 + 
                           (player_position[1] - animal.y) ** 2) ** 0.5
                
                # 如果在領地範圍內
                if distance <= animal.territory_radius:
                    return True
        
        return False
    
    def handle_player_shoot(self, player_position, target_position, weapon_damage, weapon_range):
        """
        處理玩家射擊動物\n
        
        參數:\n
        player_position (tuple): 玩家位置\n
        target_position (tuple): 射擊目標位置\n
        weapon_damage (int): 武器傷害\n
        weapon_range (float): 武器射程\n
        
        回傳:\n
        dict: 射擊結果 {\n
            'hit_animal': Animal or None - 被擊中的動物\n
            'damage_dealt': int - 造成的傷害\n
            'kill': bool - 是否擊殺\n
        }\n
        """
        px, py = player_position
        tx, ty = target_position
        
        # 計算射擊距離
        shoot_distance = math.sqrt((tx - px) ** 2 + (ty - py) ** 2)
        
        # 檢查射程
        if shoot_distance > weapon_range:
            return {'hit_animal': None, 'damage_dealt': 0, 'kill': False}
        
        # 尋找射擊路徑上的動物
        hit_animal = None
        min_distance = float('inf')
        
        for animal in self.all_animals:
            if not animal.is_alive:
                continue
                
            # 計算動物到射擊線的距離
            ax, ay = animal.x, animal.y
            
            # 點到線段的距離計算
            # 射擊線：從玩家位置到目標位置
            line_length_sq = (tx - px) ** 2 + (ty - py) ** 2
            if line_length_sq == 0:
                continue
                
            # 計算動物位置在射擊線上的投影參數
            t = max(0, min(1, ((ax - px) * (tx - px) + (ay - py) * (ty - py)) / line_length_sq))
            
            # 投影點座標
            proj_x = px + t * (tx - px)
            proj_y = py + t * (ty - py)
            
            # 動物到投影點的距離
            distance_to_line = math.sqrt((ax - proj_x) ** 2 + (ay - proj_y) ** 2)
            
            # 檢查是否在動物的命中範圍內（動物大小的一半）
            hit_radius = animal.size / 2
            if distance_to_line <= hit_radius:
                # 計算玩家到動物的距離
                distance_to_animal = math.sqrt((ax - px) ** 2 + (ay - py) ** 2)
                if distance_to_animal < min_distance:
                    min_distance = distance_to_animal
                    hit_animal = animal
        
        # 如果擊中動物
        if hit_animal:
            # 動物受傷
            hit_animal.take_damage(weapon_damage, None)  # 可以傳入玩家物件作為攻擊者
            
            # 檢查是否擊殺
            is_kill = not hit_animal.is_alive
            
            if is_kill:
                print(f"擊殺了 {hit_animal.animal_type.value}！")
            
            return {
                'hit_animal': hit_animal,
                'damage_dealt': weapon_damage,
                'kill': is_kill
            }
        
        return {'hit_animal': None, 'damage_dealt': 0, 'kill': False}
