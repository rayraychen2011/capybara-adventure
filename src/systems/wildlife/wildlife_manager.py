######################載入套件######################
import pygame
import random
import time
from src.systems.wildlife.animal import Animal, AnimalState
from src.systems.wildlife.animal_data import AnimalType, AnimalData


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
    6. 季節性動物遷移\n
    """

    def __init__(self):
        """
        初始化野生動物管理器\n
        """
        # 動物群體容器
        self.forest_animals = []  # 森林動物
        self.lake_animals = []  # 湖泊動物
        self.all_animals = []  # 所有動物的統一列表

        # 生成控制
        self.max_forest_animals = 15  # 森林最大動物數量
        self.max_lake_animals = 10  # 湖泊最大動物數量
        self.spawn_cooldown = 5.0  # 生成冷卻時間 (秒)
        self.last_spawn_time = 0  # 上次生成時間

        # 環境邊界 (會從場景傳入)
        self.forest_bounds = (100, 100, 600, 400)  # 森林區域邊界
        self.lake_bounds = (200, 200, 400, 300)  # 湖泊區域邊界

        # 互動檢測
        self.interaction_range = 50  # 玩家互動範圍
        self.hunting_range = 40  # 狩獵攻擊範圍
        self.fishing_range = 60  # 釣魚範圍

        # 保育系統
        self.protected_kills = []  # 保育類動物擊殺記錄

        # 統計資料
        self.total_spawned = 0  # 總生成數量
        self.total_hunted = 0  # 總狩獵數量
        self.total_fished = 0  # 總釣魚數量

        print("野生動物管理器初始化完成")

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
                # 生成森林動物
                forest_species = [
                    AnimalType.RABBIT,
                    AnimalType.DEER,
                    AnimalType.WILD_BOAR,
                    AnimalType.PHEASANT,
                    AnimalType.SQUIRREL,
                    AnimalType.FOX,
                    AnimalType.BEAR,
                ]

                for _ in range(8):  # 初始生成8隻森林動物
                    animal_type = random.choice(forest_species)
                    self._spawn_animal(animal_type, "forest")

        if scene_type in ["lake", "all"]:
            # 檢查湖泊邊界有效性
            if self.lake_bounds[2] > 60 and self.lake_bounds[3] > 60:
                # 生成湖泊動物 (魚類)
                lake_species = [
                    AnimalType.BASS,
                    AnimalType.CARP,
                    AnimalType.TROUT,
                    AnimalType.CATFISH,
                    AnimalType.SALMON,
                ]

                for _ in range(6):  # 初始生成6條魚
                    animal_type = random.choice(lake_species)
                    self._spawn_animal(animal_type, "lake")

        print(
            f"初始化完成：森林動物 {len(self.forest_animals)} 隻，湖泊動物 {len(self.lake_animals)} 隻"
        )

    def _spawn_animal(self, animal_type, habitat):
        """
        生成新動物\n
        \n
        參數:\n
        animal_type (AnimalType): 動物種類\n
        habitat (str): 棲息地類型 ("forest" 或 "lake")\n
        \n
        回傳:\n
        Animal: 生成的動物物件\n
        """
        # 根據棲息地選擇邊界和容器
        if habitat == "forest":
            bounds = self.forest_bounds
            container = self.forest_animals
            max_count = self.max_forest_animals
        elif habitat == "lake":
            bounds = self.lake_bounds
            container = self.lake_animals
            max_count = self.max_lake_animals
        else:
            print(f"未知的棲息地類型: {habitat}")
            return None

        # 檢查數量限制
        if len(container) >= max_count:
            return None

        # 在棲息地範圍內生成隨機位置
        # 檢查邊界有效性
        if bounds[2] <= 60 or bounds[3] <= 60:  # 寬度或高度太小
            print(f"棲息地 {habitat} 邊界太小，無法生成動物: {bounds}")
            return None

        x = random.randint(bounds[0] + 30, bounds[0] + bounds[2] - 30)
        y = random.randint(bounds[1] + 30, bounds[1] + bounds[3] - 30)

        # 創建動物
        animal = Animal(animal_type, (x, y), bounds, habitat)

        # 添加到對應容器
        container.append(animal)
        self.all_animals.append(animal)
        self.total_spawned += 1

        print(f"在 {habitat} 生成 {animal_type.value} (總計: {self.total_spawned})")
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
        if current_scene == "forest":
            active_animals = self.forest_animals
        elif current_scene == "lake":
            active_animals = self.lake_animals
        else:
            active_animals = []  # 其他場景沒有野生動物

        # 更新動物行為
        for animal in active_animals[:]:  # 使用切片複製，防止修改列表時出錯
            if animal.is_alive:
                animal.update(dt, player_position)
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

        # 只在對應場景生成動物
        if (
            current_scene == "forest"
            and len(self.forest_animals) < self.max_forest_animals
        ):
            # 選擇森林動物種類 (根據稀有度加權)
            spawn_weights = {
                AnimalType.RABBIT: 30,  # 很常見
                AnimalType.SQUIRREL: 25,  # 很常見
                AnimalType.PHEASANT: 20,  # 常見
                AnimalType.DEER: 15,  # 普通
                AnimalType.FOX: 10,  # 較少見
                AnimalType.WILD_BOAR: 8,  # 少見
                AnimalType.BEAR: 2,  # 稀有
            }

            animal_type = self._weighted_random_choice(spawn_weights)
            if animal_type:
                self._spawn_animal(animal_type, "forest")
                self.last_spawn_time = current_time

        elif current_scene == "lake" and len(self.lake_animals) < self.max_lake_animals:
            # 選擇湖泊動物種類
            spawn_weights = {
                AnimalType.CARP: 25,  # 很常見
                AnimalType.BASS: 20,  # 常見
                AnimalType.CATFISH: 18,  # 常見
                AnimalType.TROUT: 15,  # 普通
                AnimalType.SALMON: 12,  # 較少見
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

            # 檢查保育類動物
            penalty = None
            if target_animal.is_protected:
                self._trigger_protected_kill(target_animal, player)
                penalty = (
                    f"警告：您獵殺了保育類動物 {target_animal.animal_type.value}！"
                )

            return {
                "success": True,
                "animal": target_animal,
                "loot": loot,
                "penalty": penalty,
            }
        else:
            return {
                "success": True,
                "animal": target_animal,
                "loot": [],
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
        # 檢查玩家是否在釣魚範圍內
        # (這裡需要檢查玩家是否靠近水邊)

        # 尋找釣魚範圍內的魚
        nearby_fish = self.get_nearby_animals(
            player_position, self.fishing_range, "lake"
        )

        # 釣魚成功率計算
        base_success_rate = 0.3  # 基礎30%成功率
        if nearby_fish:
            # 附近有魚時提高成功率
            base_success_rate += len(nearby_fish) * 0.1

        if random.random() > base_success_rate:
            return {"success": False, "fish": None, "loot": [], "penalty": None}

        # 釣魚成功，隨機選擇一條魚
        if nearby_fish:
            target_fish = random.choice(nearby_fish)
        else:
            # 沒有附近的魚，生成一條新魚
            lake_species = [
                AnimalType.BASS,
                AnimalType.CARP,
                AnimalType.TROUT,
                AnimalType.CATFISH,
                AnimalType.SALMON,
            ]
            fish_type = random.choice(lake_species)
            target_fish = self._spawn_animal(fish_type, "lake")

        if target_fish:
            # 魚被釣上來 (直接死亡)
            target_fish._die(player)
            self.total_fished += 1

            # 獲取戰利品
            loot = target_fish.drop_items.copy()

            # 檢查保育類魚類
            penalty = None
            if target_fish.is_protected:
                self._trigger_protected_kill(target_fish, player)
                penalty = f"警告：您釣到了保育類魚類 {target_fish.animal_type.value}！"

            return {
                "success": True,
                "fish": target_fish,
                "loot": loot,
                "penalty": penalty,
            }

        return {"success": False, "fish": None, "loot": [], "penalty": None}

    def _trigger_protected_kill(self, animal, killer):
        """
        觸發保育類動物擊殺事件\n
        \n
        參數:\n
        animal (Animal): 被殺的保育類動物\n
        killer (Player): 殺手\n
        """
        # 記錄擊殺事件
        kill_record = {
            "animal": animal,
            "killer": killer,
            "time": time.time(),
            "location": animal.get_position(),
        }
        self.protected_kills.append(kill_record)

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
            "protected_kills": len(self.protected_kills),
        }

    def draw_all_animals(self, screen, scene_name):
        """
        繪製指定場景的所有動物\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        scene_name (str): 場景名稱\n
        """
        animals = self.get_animals_in_scene(scene_name)

        for animal in animals:
            animal.draw(screen)

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
                info_text = f"{animal.animal_type.value}: {animal.state.value}"
                if animal.is_protected:
                    info_text += " [保育類]"

                text_surface = font.render(info_text, True, (200, 200, 200))
                screen.blit(text_surface, (10, y_offset))
                y_offset += 20
