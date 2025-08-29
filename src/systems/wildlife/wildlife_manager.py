######################載入套件######################
import pygame
import random
import time
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
        # 這個方法需要由外部場景系統調用，因為野生動物管理器沒有直接的玩家引用
        # 設置一個回調機制供外部系統處理
        if hasattr(self, 'player_attack_callback') and self.player_attack_callback:
            self.player_attack_callback(animal.attack_damage, animal)

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

        # 生成控制
        self.max_forest_animals = 15  # 森林最大動物數量
        self.max_lake_animals = 10  # 湖泊最大動物數量
        self.spawn_cooldown = 5.0  # 生成冷卻時間 (秒)
        self.last_spawn_time = 0  # 上次生成時間

        # 環境邊界 (會從場景傳入)
        self.forest_bounds = (100, 100, 600, 400)  # 森林區域邊界
        self.lake_bounds = (200, 200, 400, 300)  # 湖泊區域邊界

        # 地形系統引用 - 用於檢查地形代碼
        self.terrain_system = None

        # 互動檢測
        self.interaction_range = 50  # 玩家互動範圍
        self.hunting_range = 40  # 狩獵攻擊範圍
        self.fishing_range = 60  # 釣魚範圍

        # 保育系統已移除

        # 統計資料
        self.total_spawned = 0  # 總生成數量
        self.total_hunted = 0  # 總狩獵數量
        self.total_fished = 0  # 總釣魚數量

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
        初始化動物群體 - 生成初始動物\n
        \n
        參數:\n
        scene_type (str): 場景類型 ("forest", "lake", 或 "all")\n
        """
        # 清空現有動物
        self.forest_animals.clear()
        self.lake_animals.clear()
        self.all_animals.clear()

        # 根據場景類型生成對應動物
        if scene_type in ["forest", "all"]:
            # 檢查森林邊界有效性
            if self.forest_bounds[2] > 60 and self.forest_bounds[3] > 60:
                # 生成森林動物 - 新的動物系統
                forest_species = [
                    AnimalType.RABBIT,      # 稀有
                    AnimalType.SHEEP,       # 稀有
                    AnimalType.MOUNTAIN_LION, # 超稀有
                    AnimalType.BLACK_PANTHER, # 超稀有
                    AnimalType.BEAR,        # 傳奇
                ]

                for _ in range(8):  # 初始生成8隻森林動物
                    animal_type = random.choice(forest_species)
                    self._spawn_animal(animal_type, "forest")

        if scene_type in ["lake", "all"]:
            # 檢查湖泊邊界有效性
            if self.lake_bounds[2] > 60 and self.lake_bounds[3] > 60:
                # 生成湖泊動物 - 主要是烏龜
                lake_species = [
                    AnimalType.TURTLE,      # 稀有
                ]

                for _ in range(4):  # 初始生成4隻湖泊動物
                    animal_type = random.choice(lake_species)
                    self._spawn_animal(animal_type, "lake")

        print(
            f"初始化完成：森林動物 {len(self.forest_animals)} 隻，湖泊動物 {len(self.lake_animals)} 隻"
        )

    def _spawn_animal(self, animal_type, habitat):
        """
        生成新動物 - 基於地形代碼的位置選擇\n
        \n
        參數:\n
        animal_type (AnimalType): 動物種類\n
        habitat (str): 棲息地類型 ("forest" 或 "lake")\n
        \n
        回傳:\n
        Animal: 生成的動物物件\n
        """
        # 根據棲息地選擇容器和地形代碼
        if habitat == "forest":
            container = self.forest_animals
            max_count = self.max_forest_animals
            terrain_code = 1  # 森林地形代碼
            bounds = self.forest_bounds  # 後備邊界
        elif habitat == "lake":
            container = self.lake_animals
            max_count = self.max_lake_animals
            terrain_code = 2  # 水域地形代碼
            bounds = self.lake_bounds  # 後備邊界
        else:
            print(f"未知的棲息地類型: {habitat}")
            return None

        # 檢查數量限制
        if len(container) >= max_count:
            return None

        # 嘗試在對應地形代碼的位置生成動物
        if self.terrain_system:
            terrain_positions = self._find_terrain_positions(terrain_code, 5)
            if terrain_positions:
                # 從符合地形的位置中隨機選擇
                x, y = random.choice(terrain_positions)
            else:
                # 如果找不到合適的地形位置，使用後備邊界
                print(f"找不到地形代碼 {terrain_code} 的位置，使用後備邊界")
                x = random.randint(bounds[0] + 30, bounds[0] + bounds[2] - 30)
                y = random.randint(bounds[1] + 30, bounds[1] + bounds[3] - 30)
        else:
            # 沒有地形系統時使用原始邊界生成方法
            if bounds[2] <= 60 or bounds[3] <= 60:  # 寬度或高度太小
                print(f"棲息地 {habitat} 邊界太小，無法生成動物: {bounds}")
                return None

            x = random.randint(bounds[0] + 30, bounds[0] + bounds[2] - 30)
            y = random.randint(bounds[1] + 30, bounds[1] + bounds[3] - 30)

        # 創建動物
        animal = Animal(animal_type, (x, y), bounds, habitat)
        
        # 設定地形系統引用
        if self.terrain_system:
            animal.set_terrain_system(self.terrain_system)

        # 添加到對應容器
        container.append(animal)
        self.all_animals.append(animal)
        self.total_spawned += 1

        print(f"在 {habitat} (地形代碼:{terrain_code}) 生成 {animal_type.value} (總計: {self.total_spawned})")
        return animal

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
                AnimalType.RABBIT: 30,        # 稀有，很常見
                AnimalType.SHEEP: 25,         # 稀有，很常見
                AnimalType.MOUNTAIN_LION: 8,  # 超稀有，少見
                AnimalType.BLACK_PANTHER: 6,  # 超稀有，少見
                AnimalType.BEAR: 2,           # 傳奇，稀有
            }

            animal_type = self._weighted_random_choice(spawn_weights)
            if animal_type:
                self._spawn_animal(animal_type, "forest")
                self.last_spawn_time = current_time

        # 在小鎮場景或湖泊場景生成湖泊動物
        elif (
            current_scene in ["lake", "town"] 
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
