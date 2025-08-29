######################載入套件######################
import pygame
import random
import math
import os
from enum import Enum
from src.systems.wildlife.animal_data import (
    AnimalType,
    AnimalData,
    ThreatLevel,
    BehaviorType,
    RarityLevel,
)


######################動物狀態列舉######################
class AnimalState(Enum):
    """
    動物狀態列舉\n
    \n
    定義動物可能的行為狀態\n
    每個狀態對應不同的 AI 邏輯和行為模式\n
    """

    WANDERING = "漫遊中"  # 正常的隨機移動
    GRAZING = "覓食中"  # 停下來吃草或覓食
    ALERT = "警戒中"  # 發現潛在威脅，保持警覺
    FLEEING = "逃跑中"  # 被驚嚇，快速逃離
    ATTACKING = "攻擊中"  # 主動攻擊目標
    HIDING = "躲藏中"  # 躲在安全地點
    ROARING = "怒吼中"  # 傳奇動物警告玩家
    DEAD = "死亡"  # 動物已死亡


######################野生動物基礎類別######################
class Animal:
    """
    野生動物基礎類別\n
    \n
    代表遊戲中的一隻野生動物\n
    包含動物的行為 AI、生存狀態和與環境的互動\n
    \n
    主要功能:\n
    1. 動物行為 AI (覓食、警戒、逃跑、攻擊)\n
    2. 玩家互動檢測\n
    3. 狩獵和死亡機制\n
    4. 保育類動物的特殊保護\n
    5. 移動和動畫系統\n
    """

    # 動物編號計數器
    _id_counter = 1

    def __init__(self, animal_type, position, habitat_bounds, habitat=None):
        """
        初始化野生動物\n
        \n
        參數:\n
        animal_type (AnimalType): 動物種類\n
        position (tuple): 初始位置 (x, y)\n
        habitat_bounds (tuple): 棲息地邊界 (x, y, width, height)\n
        habitat (str): 棲息地類型 ("forest" 或 "lake")\n
        """
        # 基本身份
        self.id = Animal._id_counter
        Animal._id_counter += 1

        self.animal_type = animal_type
        self.state = AnimalState.WANDERING
        self.habitat = habitat  # 添加棲息地屬性

        # 位置和移動
        self.x, self.y = position
        self.target_x = self.x
        self.target_y = self.y
        self.habitat_bounds = habitat_bounds

        # 地形系統引用（用於檢查是否離開森林/水域）
        self.terrain_system = None

        # 從動物資料獲取屬性
        self.size = AnimalData.get_animal_property(animal_type, "size") or 8  # 預設與玩家相同大小
        self.max_speed = AnimalData.get_animal_property(animal_type, "speed") or 2.0
        self.current_speed = self.max_speed
        self.max_health = AnimalData.get_animal_property(animal_type, "health") or 50
        self.health = self.max_health

        # 水陸移動能力
        self.can_swim = AnimalData.get_animal_property(animal_type, "can_swim") or False

        # 行為屬性
        self.threat_level = AnimalData.get_animal_property(animal_type, "threat_level")
        self.behavior_type = AnimalData.get_animal_property(animal_type, "behavior")
        self.rarity = AnimalData.get_animal_property(animal_type, "rarity")  # 新增稀有度
        self.is_protected = (
            AnimalData.get_animal_property(animal_type, "is_protected") or False
        )

        # 戰鬥屬性
        self.damage = AnimalData.get_animal_property(animal_type, "damage") or 0
        self.agility = AnimalData.get_animal_property(animal_type, "agility") or 50
        self.attack_range = AnimalData.get_animal_property(animal_type, "attack_range") or 0
        self.territory_range = AnimalData.get_animal_property(animal_type, "territory_range") or 0
        self.flee_speed = AnimalData.get_animal_property(animal_type, "flee_speed") or self.max_speed
        
        # 戰鬥狀態
        self.is_injured = False
        self.last_attack_time = 0
        self.attack_cooldown = 1.0  # 攻擊冷卻時間（秒）
        self.has_attacked_player = False
        self.player_target = None  # 攻擊目標
        self.flee_target = None   # 逃跑目標位置

        # 外觀
        self.color = AnimalData.get_animal_property(animal_type, "color") or (
            128,
            128,
            128,
        )
        
        # 載入動物圖像
        self.image = self._load_animal_image()
        self.image_size = (self.size * 4, self.size * 4)  # 圖像大小為動物大小的4倍
        if self.image:
            self.image = pygame.transform.scale(self.image, self.image_size)

        # 視野系統 - 根據需求設定
        # 根據動物類型調整視野角度
        if animal_type == AnimalType.BEAR:
            self.vision_angle = 360  # 熊具有360度全方位視野（嗅覺敏銳）
            self.vision_distance = 30 * 20  # 熊的視野距離更遠（30公尺 = 600像素）
        else:
            self.vision_angle = 120  # 一般動物視野角度（度）
            self.vision_distance = 20 * 20  # 一般動物視野距離（20公尺 = 400像素）
        self.vision_direction = 0  # 當前面向方向（度）

        # 攻擊系統 - 根據需求設定
        self.attack_range = 1.5 * 20  # 攻擊距離（1.5公尺 = 30像素）

        # 熊的領地系統
        self.territory_radius = AnimalData.get_animal_property(animal_type, "territory_radius") or 0
        self.has_territory = self.territory_radius > 0  # 有領地半徑就表示有領地
        if self.territory_radius > 0:
            # 將公尺轉換為像素（假設1公尺=20像素）
            self.territory_radius = self.territory_radius * 20
            self.territory_center = (self.x, self.y)
            self.territory_invasion_timer = 0  # 玩家入侵領地計時器
            self.territory_warning_given = False  # 是否已給出警告
            
        # AI 相關變數
        self.last_target_change = 0  # 上次改變目標的時間
        self.alert_timer = 0  # 警戒狀態計時器
        self.flee_timer = 0  # 逃跑狀態計時器
        self.wander_timer = 0  # 漫遊計時器
        self.roar_timer = 0  # 怒吼計時器
        self.detection_range = 80  # 玩家檢測範圍

        # 生存狀態
        self.is_alive = True
        self.death_time = 0
        self.killer = None  # 殺死此動物的對象

        # 攻擊狀態標記
        self.has_attacked_player = False
        self.attack_damage = 0

        # 掉落物品
        self.drop_items = AnimalData.get_animal_loot(animal_type)

        print(f"創建動物: {animal_type.value} (ID: {self.id})")

    def _load_animal_image(self):
        """
        載入動物對應的圖像檔案\n
        \n
        回傳:\n
        pygame.Surface: 載入的圖像，失敗時回傳None\n
        """
        # 動物類型對應的檔案名稱
        image_map = {
            AnimalType.RABBIT: "rabbit.png",
            AnimalType.TURTLE: "turtle.png", 
            AnimalType.SHEEP: "sheep.png",
            AnimalType.MOUNTAIN_LION: "山獅.png",  # 使用山獅專屬圖像
            AnimalType.BLACK_PANTHER: "panther.png",
            AnimalType.BEAR: "bear.png",
        }
        
        # 獲取對應的檔案名稱
        filename = image_map.get(self.animal_type)
        if not filename:
            return None
            
        # 建構圖像檔案路徑
        image_path = os.path.join("assets", "images", filename)
        
        try:
            # 載入圖像
            image = pygame.image.load(image_path).convert_alpha()
            return image
        except (pygame.error, FileNotFoundError) as e:
            print(f"無法載入動物圖像 {image_path}: {e}")
            return None

    def set_terrain_system(self, terrain_system):
        """
        設定地形系統引用，用於檢查棲息地邊界\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統實例\n
        """
        self.terrain_system = terrain_system

    def _is_in_valid_habitat(self, x, y):
        """
        檢查指定位置是否在有效棲息地內\n
        \n
        參數:\n
        x (float): X座標\n
        y (float): Y座標\n
        \n
        回傳:\n
        bool: 如果在有效棲息地內則回傳True\n
        """
        if not self.terrain_system:
            # 沒有地形系統時只檢查基本邊界
            hx, hy, hw, hh = self.habitat_bounds
            return hx <= x <= hx + hw and hy <= y <= hy + hh
        
        # 檢查地形類型
        terrain_type = self.terrain_system.get_terrain_at_position(x, y)
        
        if self.habitat == "forest":
            # 森林動物只能在森林區域（地形代碼1）活動
            return terrain_type == 1
        elif self.habitat == "lake":
            # 湖泊動物只能在水域（地形代碼2）活動
            return terrain_type == 2
        else:
            # 其他棲息地使用基本邊界檢查
            hx, hy, hw, hh = self.habitat_bounds
            return hx <= x <= hx + hw and hy <= y <= hy + hh

    def update(self, dt, player_position):
        """
        更新動物邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔 (秒)\n
        player_position (tuple): 玩家位置 (x, y)\n
        """
        if not self.is_alive:
            return

        # 檢測玩家
        player_distance = self._calculate_distance_to_player(player_position)
        player_in_vision = self._is_player_in_vision(player_position)

        # 傳奇動物領地檢查
        if self.has_territory:
            self._update_territory_behavior(dt, player_position, player_distance)

        # 根據稀有度決定行為邏輯
        if self.rarity == RarityLevel.RARE:
            # 稀有動物：看到玩家會逃跑
            if player_in_vision and player_distance < self.vision_distance:
                if self.state not in [AnimalState.FLEEING, AnimalState.HIDING]:
                    self.state = AnimalState.FLEEING
                    self.flee_timer = random.uniform(4.0, 7.0)
                    self._set_flee_target(player_position)
        
        elif self.rarity == RarityLevel.SUPER_RARE:
            # 超稀有動物：繼續做原本的事，除非被攻擊
            # 只有在被直接攻擊時才會改變行為，否則忽略玩家
            pass  # 行為在 take_damage 方法中處理
        
        elif self.rarity == RarityLevel.LEGENDARY:
            # 傳奇動物：看到玩家就攻擊（熊的新行為）
            if self.animal_type == AnimalType.BEAR:
                if player_in_vision and player_distance < self.vision_distance:
                    if self.state not in [AnimalState.ATTACKING]:
                        self.state = AnimalState.ATTACKING
                        print(f"{self.animal_type.value} 看到玩家，立即發動攻擊！")
            # 領地行為仍然保留（在 _update_territory_behavior 中處理）
        
        else:
            # 舊版行為邏輯（向後相容）
            self._update_behavior_state(dt, player_position, player_distance)

        # 執行當前狀態的行為
        self._execute_current_behavior(dt, player_position, player_distance)

        # 更新移動（並更新面向方向）
        self._update_movement(dt)

        # 更新計時器
        self._update_timers(dt)

    def _calculate_distance_to_player(self, player_position):
        """
        計算與玩家的距離\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        \n
        回傳:\n
        float: 與玩家的距離\n
        """
        px, py = player_position
        return math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2)

    def _is_player_in_vision(self, player_position):
        """
        檢查玩家是否在動物的視野範圍內\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        \n
        回傳:\n
        bool: 如果玩家在視野內則回傳True\n
        """
        px, py = player_position
        
        # 計算到玩家的距離
        distance = self._calculate_distance_to_player(player_position)
        if distance > self.vision_distance:
            return False
        
        # 計算到玩家的角度
        angle_to_player = math.degrees(math.atan2(py - self.y, px - self.x))
        
        # 標準化角度到 0-360 度
        angle_to_player = angle_to_player % 360
        vision_dir = self.vision_direction % 360
        
        # 計算角度差
        angle_diff = abs(angle_to_player - vision_dir)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        # 檢查是否在視野角度範圍內
        return angle_diff <= (self.vision_angle / 2)

    def _update_territory_behavior(self, dt, player_position, player_distance):
        """
        更新傳奇動物的領地行為\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        player_distance (float): 與玩家的距離\n
        """
        if not self.has_territory:
            return
        
        # 檢查玩家是否在領地內
        territory_distance = math.sqrt(
            (player_position[0] - self.territory_center[0]) ** 2 + 
            (player_position[1] - self.territory_center[1]) ** 2
        )
        
        if territory_distance <= self.territory_range:
            # 對於熊，領地行為與視野攻擊集成，避免重複觸發
            if self.animal_type == AnimalType.BEAR:
                # 熊的領地攻擊已經在視野檢測中處理，這裡不重複設置
                pass
            else:
                # 其他傳奇動物：看到玩家進入領地便立即攻擊
                if self.state not in [AnimalState.ATTACKING]:
                    self.state = AnimalState.ATTACKING
                    print(f"{self.animal_type.value} 看到玩家進入領地，立即發動攻擊！")
        else:
            # 玩家離開領地，對於非熊動物停止攻擊
            if self.animal_type != AnimalType.BEAR and self.state == AnimalState.ATTACKING:
                self.state = AnimalState.WANDERING
                print(f"{self.animal_type.value} 停止攻擊，玩家已離開領地")
            
            # 重置領地狀態
            self.territory_invasion_timer = 0
            self.territory_warning_given = False

    def _update_behavior_state(self, dt, player_position, player_distance):
        """
        根據環境情況更新動物的行為狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        player_distance (float): 與玩家的距離\n
        """
        # 如果玩家太近，根據動物性格決定反應
        if player_distance < self.detection_range:

            if self.threat_level in [ThreatLevel.HARMLESS, ThreatLevel.LOW]:
                # 無害或低威脅動物：逃跑
                if self.state not in [AnimalState.FLEEING, AnimalState.HIDING]:
                    self.state = AnimalState.FLEEING
                    self.flee_timer = random.uniform(3.0, 6.0)  # 逃跑3-6秒
                    self._set_flee_target(player_position)

            elif self.threat_level == ThreatLevel.MEDIUM:
                # 中等威脅動物：根據行為類型決定
                if self.behavior_type == BehaviorType.DEFENSIVE:
                    if player_distance < 40:  # 很近時才攻擊
                        self.state = AnimalState.ATTACKING
                    else:
                        self.state = AnimalState.ALERT
                        self.alert_timer = 2.0
                else:
                    self.state = AnimalState.ALERT
                    self.alert_timer = 3.0

            elif self.threat_level in [ThreatLevel.HIGH, ThreatLevel.EXTREME]:
                # 高威脅動物：根據行為類型攻擊或警戒
                if self.behavior_type in [
                    BehaviorType.TERRITORIAL,
                    BehaviorType.DEFENSIVE,
                ]:
                    if player_distance < 60:
                        self.state = AnimalState.ATTACKING
                    else:
                        self.state = AnimalState.ALERT
                        self.alert_timer = 4.0

        else:
            # 玩家不在附近，回到正常狀態
            if self.state in [
                AnimalState.ALERT,
                AnimalState.FLEEING,
                AnimalState.ATTACKING,
            ]:
                if self.alert_timer <= 0 and self.flee_timer <= 0:
                    self.state = AnimalState.WANDERING
                    self._set_wander_target()

    def _execute_current_behavior(self, dt, player_position, player_distance):
        """
        執行當前狀態對應的行為\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        player_distance (float): 與玩家的距離\n
        """
        if self.state == AnimalState.WANDERING:
            self._wander_behavior(dt)

        elif self.state == AnimalState.GRAZING:
            self._grazing_behavior(dt)

        elif self.state == AnimalState.ALERT:
            self._alert_behavior(dt, player_position)

        elif self.state == AnimalState.FLEEING:
            self._fleeing_behavior(dt, player_position)

        elif self.state == AnimalState.ATTACKING:
            self._attacking_behavior(dt, player_position)

        elif self.state == AnimalState.HIDING:
            self._hiding_behavior(dt)
            
        elif self.state == AnimalState.ROARING:
            self._roaring_behavior(dt)

    def _wander_behavior(self, dt):
        """
        漫遊行為 - 隨機移動和覓食\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        self.current_speed = self.max_speed * 0.6  # 慢速移動

        # 到達目標點或需要新目標
        if self._is_at_target() or self.wander_timer <= 0:
            # 決定下一個行為
            if random.random() < 0.3:  # 30% 機率停下覓食
                self.state = AnimalState.GRAZING
                self.wander_timer = random.uniform(2.0, 5.0)
            else:
                self._set_wander_target()
                self.wander_timer = random.uniform(4.0, 8.0)

    def _grazing_behavior(self, dt):
        """
        覓食行為 - 停在原地吃草\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        self.current_speed = 0  # 停止移動

        # 覓食時間結束
        if self.wander_timer <= 0:
            self.state = AnimalState.WANDERING
            self._set_wander_target()

    def _alert_behavior(self, dt, player_position):
        """
        警戒行為 - 監視玩家但不移動\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        """
        self.current_speed = 0  # 停止移動，保持警戒

        # 警戒時間結束
        if self.alert_timer <= 0:
            # 根據玩家距離決定下一步行動
            distance = self._calculate_distance_to_player(player_position)
            if distance < 50:
                # 玩家仍然很近，開始逃跑或攻擊
                if self.threat_level in [ThreatLevel.HIGH, ThreatLevel.EXTREME]:
                    self.state = AnimalState.ATTACKING
                else:
                    self.state = AnimalState.FLEEING
                    self.flee_timer = 4.0
                    self._set_flee_target(player_position)
            else:
                self.state = AnimalState.WANDERING

    def _fleeing_behavior(self, dt, player_position):
        """
        逃跑行為 - 快速遠離玩家或威脅\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        """
        # 根據稀有度調整逃跑速度
        if self.rarity == RarityLevel.RARE:
            # 稀有動物逃跑時速度更快，更加驚恐
            self.current_speed = self.flee_speed * 1.5  # 比平常快50%
            
            # 受傷的稀有動物逃跑時更加不穩定
            if self.is_injured:
                # 隨機改變方向，模擬驚恐中的亂竄
                if random.random() < 0.15:  # 15% 機率突然改變方向
                    self._set_flee_target(player_position)
                    # 減少頻繁調試輸出
                    if not hasattr(self, '_flee_debug_counter'):
                        self._flee_debug_counter = 0
                    self._flee_debug_counter += 1
                    if self._flee_debug_counter % 20 == 0:  # 每20次才輸出一次
                        print(f"💨 {self.animal_type.value} 驚恐地改變逃跑方向！(第{self._flee_debug_counter}次)")
        else:
            # 其他動物正常逃跑速度
            self.current_speed = self.max_speed * 1.3  # 加速逃跑

        # 持續更新逃跑方向（遠離玩家）
        if random.random() < 0.08:  # 8% 機率調整逃跑方向
            self._set_flee_target(player_position)

        # 逃跑時間結束或到達安全距離
        distance = self._calculate_distance_to_player(player_position)
        safe_distance = self.detection_range * 3  # 安全距離是檢測範圍的3倍
        
        # 稀有動物需要跑得更遠才覺得安全
        if self.rarity == RarityLevel.RARE:
            safe_distance = self.detection_range * 4
        
        if self.flee_timer <= 0 or distance > safe_distance:
            if self.rarity == RarityLevel.RARE and self.is_injured:
                # 受傷的稀有動物會先躲藏一段時間
                self.state = AnimalState.HIDING
                self.wander_timer = random.uniform(8.0, 15.0)  # 躲藏8-15秒
                print(f"🫥 {self.animal_type.value} 躲藏起來恢復驚嚇")
            else:
                # 其他動物直接進入躲藏或回到正常狀態
                self.state = AnimalState.HIDING
                self.wander_timer = random.uniform(3.0, 6.0)  # 躲藏一段時間

    def _roaring_behavior(self, dt):
        """
        怒吼行為 - 傳奇動物警告玩家\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        self.current_speed = 0  # 停止移動，專注怒吼
        
        # 怒吼時間結束
        if self.roar_timer <= 0:
            self.state = AnimalState.ALERT
            self.alert_timer = 1.0

    def _attacking_behavior(self, dt, player_position):
        """
        攻擊行為 - 向玩家移動並攻擊\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        """
        # 根據敏捷度調整移動速度
        agility_factor = self.agility / 50.0  # 標準化敏捷度 (50為中等)
        self.current_speed = self.max_speed * (0.8 + agility_factor * 0.4)  # 敏捷度影響速度

        # 持續追蹤玩家
        self.target_x, self.target_y = player_position

        # 檢查是否接近到可以攻擊的距離
        distance = self._calculate_distance_to_player(player_position)
        if distance <= self.attack_range and self.damage > 0:
            # 嘗試攻擊玩家
            if self.attack_player(player_position):
                print(f"{self.animal_type.value} 攻擊了玩家！造成 {self.damage} 點傷害")

            # 攻擊後可能退開一些
            if random.random() < 0.3:  # 30% 機率攻擊後退開
                self.state = AnimalState.ALERT
                self.alert_timer = 2.0
        elif distance > self.vision_distance:
            # 如果玩家距離超出視野範圍，停止攻擊
            if self.animal_type == AnimalType.BEAR:
                # 熊失去視野後停止攻擊
                self.state = AnimalState.WANDERING
                print(f"{self.animal_type.value} 失去玩家視野，停止攻擊")
            else:
                # 其他動物使用原來的領地邏輯
                if distance > self.territory_range * 2:
                    self.state = AnimalState.WANDERING

    def _hiding_behavior(self, dt):
        """
        躲藏行為 - 保持靜止並逐漸恢復\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        self.current_speed = 0  # 完全停止
        
        # 躲藏期間稀有動物會逐漸恢復冷靜
        if self.rarity == RarityLevel.RARE and self.is_injured:
            # 受傷的稀有動物在躲藏時會漸漸恢復一些血量（代表休息恢復）
            if random.random() < 0.05:  # 5% 機率每幀恢復一點血量
                self.health = min(self.max_health, self.health + 1)
                if self.health >= self.max_health * 0.8:  # 恢復到80%血量時
                    self.is_injured = False
                    print(f"💚 {self.animal_type.value} 在躲藏中逐漸恢復了體力")

        # 躲藏時間結束
        if self.wander_timer <= 0:
            if self.rarity == RarityLevel.RARE and self.is_injured:
                # 受傷的稀有動物恢復後會更加小心謹慎
                self.state = AnimalState.ALERT
                self.alert_timer = 5.0  # 長時間保持警戒
                self.detection_range = self.detection_range * 1.5  # 提高警覺範圍
                print(f"👀 {self.animal_type.value} 變得更加警覺了")
            else:
                # 其他動物直接回到漫遊狀態
                self.state = AnimalState.WANDERING
                self._set_wander_target()

    def _set_wander_target(self):
        """
        設定隨機漫遊目標 - 確保目標在有效棲息地內\n
        """
        hx, hy, hw, hh = self.habitat_bounds
        margin = 50  # 離邊界保持距離
        
        # 嘗試找到有效的漫遊目標
        attempts = 0
        max_attempts = 20
        
        while attempts < max_attempts:
            # 在棲息地範圍內選擇隨機點
            test_x = random.randint(hx + margin, hx + hw - margin)
            test_y = random.randint(hy + margin, hy + hh - margin)
            
            # 檢查是否在有效棲息地內
            if self._is_in_valid_habitat(test_x, test_y):
                self.target_x = test_x
                self.target_y = test_y
                return
            
            attempts += 1
        
        # 如果找不到有效位置，使用當前位置附近的小範圍移動
        self.target_x = self.x + random.randint(-30, 30)
        self.target_y = self.y + random.randint(-30, 30)
        
        # 確保不超出基本邊界
        self.target_x = max(hx + margin, min(hx + hw - margin, self.target_x))
        self.target_y = max(hy + margin, min(hy + hh - margin, self.target_y))

    def _set_flee_target(self, player_position):
        """
        設定逃跑目標 - 遠離玩家的方向\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        """
        px, py = player_position

        # 計算遠離玩家的方向
        dx = self.x - px
        dy = self.y - py
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # 正規化方向向量
            dx /= distance
            dy /= distance

            # 設定逃跑距離
            flee_distance = 150

            # 計算逃跑目標
            new_x = self.x + dx * flee_distance
            new_y = self.y + dy * flee_distance

            # 確保不超出棲息地邊界
            hx, hy, hw, hh = self.habitat_bounds
            new_x = max(hx + 30, min(hx + hw - 30, new_x))
            new_y = max(hy + 30, min(hy + hh - 30, new_y))

            self.target_x = new_x
            self.target_y = new_y

    def _update_movement(self, dt):
        """
        更新動物移動 - 包含棲息地邊界檢查和面向方向更新\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        if self.current_speed <= 0:
            return

        # 計算到目標的方向
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 5:  # 還沒到達目標
            # 正規化方向向量並移動
            move_distance = self.current_speed * dt * 60  # 60 用於幀率補償

            if distance > 0:
                move_x = (dx / distance) * move_distance
                move_y = (dy / distance) * move_distance

                # 更新面向方向
                self.vision_direction = math.degrees(math.atan2(dy, dx))

                # 計算新位置
                new_x = self.x + move_x
                new_y = self.y + move_y

                # 檢查新位置是否在有效棲息地內
                if self._is_in_valid_habitat(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                else:
                    # 如果新位置超出棲息地，選擇新的隨機目標
                    self._set_wander_target()
                
                # 確保不超出基本棲息地邊界（後備檢查）
                hx, hy, hw, hh = self.habitat_bounds
                self.x = max(hx, min(hx + hw, self.x))
                self.y = max(hy, min(hy + hh, self.y))

    def _is_in_valid_habitat(self, x, y):
        """
        檢查位置是否在有效棲息地內\n
        考慮動物的水陸移動能力\n
        \n
        參數:\n
        x (float): X座標\n
        y (float): Y座標\n
        \n
        回傳:\n
        bool: 是否為有效位置\n
        """
        if not self.terrain_system:
            return True  # 如果沒有地形系統，允許移動
        
        # 將像素座標轉換為地形格子座標
        grid_x = int(x // 20)  # 假設每格20像素
        grid_y = int(y // 20)
        
        # 檢查邊界
        if (grid_x < 0 or grid_x >= self.terrain_system.map_width or 
            grid_y < 0 or grid_y >= self.terrain_system.map_height):
            return False
        
        # 獲取地形類型
        world_x = grid_x * 20 + 10
        world_y = grid_y * 20 + 10
        terrain_code = self.terrain_system.get_terrain_at_world_pos(world_x, world_y)
        
        # 水體地形檢查（地形代碼2）
        if terrain_code == 2:  # 水體
            return self.can_swim  # 只有烏龜可以在水上
        
        # 其他地形類型的檢查
        # 森林（代碼1）、草地（代碼0）、山丘（代碼9）等允許所有陸生動物
        if terrain_code in [0, 1, 7, 8, 9]:  # 草地、森林、公園、農地、山丘
            return True
        
        # 道路、住宅區等不適合野生動物
        if terrain_code in [3, 4, 5, 6, 10, 11]:  # 道路、高速公路、住宅、商業、鐵軌、火車站
            return False
        
        return True  # 其他情況允許移動

    def _update_timers(self, dt):
        """
        更新各種計時器\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        self.alert_timer = max(0, self.alert_timer - dt)
        self.flee_timer = max(0, self.flee_timer - dt)
        self.wander_timer = max(0, self.wander_timer - dt)
        self.roar_timer = max(0, self.roar_timer - dt)

    def _is_at_target(self):
        """
        檢查是否已到達目標位置\n
        \n
        回傳:\n
        bool: True 表示已到達目標\n
        """
        distance = math.sqrt(
            (self.x - self.target_x) ** 2 + (self.y - self.target_y) ** 2
        )
        return distance <= 10

    def take_damage(self, damage, attacker=None):
        """
        動物受到傷害\n
        \n
        參數:\n
        damage (int): 傷害值\n
        attacker (object): 攻擊者\n
        """
        if not self.is_alive:
            return

        self.health -= damage
        self.is_injured = True  # 標記為受傷狀態
        
        # 減少受傷調試輸出頻率
        if not hasattr(self, '_damage_debug_counter'):
            self._damage_debug_counter = 0
        self._damage_debug_counter += 1
        # 每5次受傷才輸出一次
        if self._damage_debug_counter % 5 == 0:
            print(f"{self.animal_type.value} 受到第{self._damage_debug_counter}次攻擊，本次 {damage} 點傷害，血量剩餘 {self.health}")
        elif self.health <= 0:
            # 死亡時一定要輸出
            print(f"{self.animal_type.value} 受到 {damage} 點傷害並死亡")

        # 受到攻擊時的反應 - 根據稀有度決定
        if self.health > 0:
            if self.rarity == RarityLevel.RARE:
                # 稀有動物：一被擊中就驚恐逃跑
                self.state = AnimalState.FLEEING
                self.flee_timer = 10.0  # 更長的逃跑時間
                self.current_speed = self.flee_speed  # 使用逃跑速度
                print(f"💨 {self.animal_type.value} 被擊中後驚恐逃跑！")
                
                # 設定逃跑目標
                if attacker and hasattr(attacker, 'get_center_position'):
                    self._set_flee_target(attacker.get_center_position())
                elif attacker and hasattr(attacker, 'get_position'):
                    self._set_flee_target(attacker.get_position())
                else:
                    # 如果攻擊者位置不明，隨機選擇逃跑方向
                    import random
                    angle = random.uniform(0, 2 * math.pi)
                    flee_x = self.x + math.cos(angle) * 200
                    flee_y = self.y + math.sin(angle) * 200
                    self.target_x = flee_x
                    self.target_y = flee_y
            
            elif self.rarity == RarityLevel.SUPER_RARE:
                # 超稀有動物：被攻擊後會反擊或逃跑
                if self.threat_level in [ThreatLevel.HIGH, ThreatLevel.EXTREME]:
                    self.state = AnimalState.ATTACKING
                    print(f"⚔️ {self.animal_type.value} 被激怒，開始反擊！")
                else:
                    self.state = AnimalState.FLEEING
                    self.flee_timer = 8.0
                    self.current_speed = self.flee_speed
                    print(f"💨 {self.animal_type.value} 被擊中後快速逃離！")
                    
                    if attacker and hasattr(attacker, 'get_center_position'):
                        self._set_flee_target(attacker.get_center_position())
                    elif attacker and hasattr(attacker, 'get_position'):
                        self._set_flee_target(attacker.get_position())
            
            elif self.rarity == RarityLevel.LEGENDARY:
                # 傳奇動物：被攻擊後變得更加兇猛
                self.state = AnimalState.ATTACKING
                print(f"🔥 {self.animal_type.value} 被激怒了，變得極度危險！")
            
            else:
                # 舊版邏輯（向後相容）
                if self.threat_level in [ThreatLevel.HARMLESS, ThreatLevel.LOW]:
                    # 無害動物受攻擊時驚恐逃跑
                    self.state = AnimalState.FLEEING
                    self.flee_timer = 8.0  # 較長的逃跑時間
                    self.current_speed = self.flee_speed
                    if attacker and hasattr(attacker, 'get_center_position'):
                        self._set_flee_target(attacker.get_center_position())
                    elif attacker and hasattr(attacker, 'get_position'):
                        self._set_flee_target(attacker.get_position())
                elif self.behavior_type in [
                    BehaviorType.DEFENSIVE,
                    BehaviorType.TERRITORIAL,
                ]:
                    # 防禦性或攻擊性動物反擊
                    self.state = AnimalState.ATTACKING
        else:
            # 動物死亡
            self._die(attacker)

    def _die(self, killer=None):
        """
        動物死亡處理\n
        \n
        參數:\n
        killer (object): 殺死動物的對象\n
        """
        if not self.is_alive:
            return

        self.is_alive = False
        self.state = AnimalState.DEAD
        self.killer = killer
        self.current_speed = 0

        print(f"{self.animal_type.value} 死亡了")

        # 保育類動物死亡的警告（僅顯示訊息，不觸發警察系統）
        if self.is_protected:
            print(f"警告：{self.animal_type.value} 是保育類動物！")

    def get_position(self):
        """
        獲取動物位置\n
        \n
        回傳:\n
        tuple: 當前座標 (x, y)\n
        """
        return (self.x, self.y)

    def get_rect(self):
        """
        獲取動物的碰撞矩形\n
        \n
        回傳:\n
        pygame.Rect: 碰撞檢測用的矩形\n
        """
        return pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )

    def draw(self, screen, camera_offset=(0, 0), show_vision=False, show_territory=False):
        """
        繪製動物\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_offset (tuple): 攝影機偏移量 (offset_x, offset_y)\n
        show_vision (bool): 是否顯示視野範圍\n
        show_territory (bool): 是否顯示領地範圍\n
        """
        offset_x, offset_y = camera_offset
        draw_x = int(self.x - offset_x)
        draw_y = int(self.y - offset_y)
        
        # 繪製熊的領地範圍（紅色圓圈）
        if self.territory_radius > 0 and self.animal_type == AnimalType.BEAR:
            territory_draw_x = int(self.territory_center[0] - offset_x)
            territory_draw_y = int(self.territory_center[1] - offset_y)
            
            # 檢查領地是否在螢幕可見範圍內
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            if (-self.territory_radius <= territory_draw_x <= screen_width + self.territory_radius and
                -self.territory_radius <= territory_draw_y <= screen_height + self.territory_radius):
                
                # 繪製紅色領地圓圈（較粗的邊框）
                pygame.draw.circle(screen, (255, 0, 0), (territory_draw_x, territory_draw_y), 
                                 self.territory_radius, 4)
                
                # 繪製半透明紅色填充（如果支援）
                try:
                    territory_surface = pygame.Surface((self.territory_radius * 2, self.territory_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(territory_surface, (255, 0, 0, 30), 
                                     (self.territory_radius, self.territory_radius), self.territory_radius)
                    screen.blit(territory_surface, (territory_draw_x - self.territory_radius, 
                                                  territory_draw_y - self.territory_radius))
                except:
                    pass  # 如果不支援透明度，只顯示邊框
        
        # 繪製領地範圍（傳奇動物，舊版相容）
        if show_territory and hasattr(self, 'has_territory') and self.has_territory:
            territory_draw_x = int(self.territory_center[0] - offset_x)
            territory_draw_y = int(self.territory_center[1] - offset_y)
            pygame.draw.circle(
                screen, 
                (255, 0, 0, 50),  # 半透明紅色
                (territory_draw_x, territory_draw_y), 
                150,  # 舊版固定半徑
                3
            )
        
        # 繪製視野範圍
        if show_vision and self.is_alive:
            self._draw_vision_cone(screen, draw_x, draw_y)
        
        if not self.is_alive:
            # 死亡動物變暗顯示
            if self.image:
                # 使用圖像但變暗
                darkened_image = self.image.copy()
                darkened_image.fill((100, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)
                image_rect = darkened_image.get_rect(center=(draw_x, draw_y))
                screen.blit(darkened_image, image_rect)
                # 紅色邊框
                pygame.draw.circle(screen, (255, 0, 0), (draw_x, draw_y), self.size + 10, 2)
            else:
                # 降級到圓形顯示
                dead_color = tuple(c // 3 for c in self.color)
                pygame.draw.circle(screen, dead_color, (draw_x, draw_y), self.size)
                pygame.draw.circle(screen, (255, 0, 0), (draw_x, draw_y), self.size, 2)
            return

        # 繪製動物本體
        if self.image:
            # 使用圖像繪製
            image_rect = self.image.get_rect(center=(draw_x, draw_y))
            screen.blit(self.image, image_rect)
        else:
            # 降級到圓形繪製
            pygame.draw.circle(screen, self.color, (draw_x, draw_y), self.size)

        # 根據狀態添加視覺效果
        # 計算效果半徑（圖像模式使用較大的半徑）
        effect_radius = max(self.size * 2, 20) if self.image else self.size
        
        if self.state == AnimalState.ALERT:
            # 警戒狀態：黃色邊框
            pygame.draw.circle(
                screen, (255, 255, 0), (draw_x, draw_y), effect_radius, 3
            )
        elif self.state == AnimalState.FLEEING:
            # 逃跑狀態：閃爍效果，稀有動物閃爍更快
            flash_interval = 150 if self.rarity == RarityLevel.RARE else 200
            if int(pygame.time.get_ticks() / flash_interval) % 2:  
                # 受傷的稀有動物用紅白閃爍表示驚恐
                if self.rarity == RarityLevel.RARE and self.is_injured:
                    flash_color = (255, 100, 100)  # 淡紅色
                else:
                    flash_color = (255, 255, 255)  # 白色
                
                pygame.draw.circle(
                    screen,
                    flash_color,
                    (draw_x, draw_y),
                    effect_radius + 5,
                    3,
                )
        elif self.state == AnimalState.ATTACKING:
            # 攻擊狀態：紅色邊框
            pygame.draw.circle(
                screen, (255, 0, 0), (draw_x, draw_y), effect_radius, 3
            )
        elif self.state == AnimalState.ROARING:
            # 怒吼狀態：橘色邊框閃爍
            if int(pygame.time.get_ticks() / 150) % 2:
                pygame.draw.circle(
                    screen, (255, 165, 0), (draw_x, draw_y), effect_radius + 5, 4
                )

        # 稀有度標記（調整位置適應圖像顯示）
        marker_offset_y = max(self.size * 2, 20) if self.image else self.size
        marker_offset_x = max(self.size * 2, 20) if self.image else self.size
        
        if self.rarity == RarityLevel.LEGENDARY:
            # 傳奇動物：金色王冠標記
            pygame.draw.circle(
                screen, (255, 215, 0), (draw_x, draw_y - marker_offset_y - 8), 6
            )
        elif self.rarity == RarityLevel.SUPER_RARE:
            # 超稀有動物：紫色星星標記
            pygame.draw.circle(
                screen, (128, 0, 128), (draw_x, draw_y - marker_offset_y - 8), 5
            )
        elif self.rarity == RarityLevel.RARE:
            # 稀有動物：藍色點標記
            pygame.draw.circle(
                screen, (0, 100, 255), (draw_x, draw_y - marker_offset_y - 8), 4
            )

        # 保育類動物特殊標記
        if self.is_protected:
            # 綠色保護標記
            pygame.draw.circle(
                screen, (0, 255, 0), (draw_x + marker_offset_x, draw_y - marker_offset_y), 4
            )

        # 健康條 (如果受傷或處於特殊狀態)
        if self.health < self.max_health or self.state == AnimalState.FLEEING:
            self._draw_health_bar(screen, draw_x, draw_y)

    def _draw_vision_cone(self, screen, draw_x, draw_y):
        """
        繪製動物的視野扇形\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        draw_x (int): 螢幕上的X座標\n
        draw_y (int): 螢幕上的Y座標\n
        """
        # 視野扇形的起始和結束角度（弧度）
        start_angle = math.radians(self.vision_direction - self.vision_angle / 2)
        end_angle = math.radians(self.vision_direction + self.vision_angle / 2)
        
        # 創建視野扇形的點列表
        points = [(draw_x, draw_y)]  # 動物位置作為扇形頂點
        
        # 添加扇形邊緣的點
        num_points = 20  # 扇形邊緣的細分程度
        for i in range(num_points + 1):
            angle = start_angle + (end_angle - start_angle) * i / num_points
            point_x = draw_x + self.vision_distance * math.cos(angle)
            point_y = draw_y + self.vision_distance * math.sin(angle)
            points.append((point_x, point_y))
        
        # 繪製半透明的視野扇形
        if len(points) > 2:
            # 創建半透明表面
            vision_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pygame.draw.polygon(vision_surface, (255, 255, 0, 80), points)  # 半透明黃色
            screen.blit(vision_surface, (0, 0))
            
            # 繪製視野邊界線
            pygame.draw.lines(screen, (255, 255, 0), False, points, 2)

    def _draw_health_bar(self, screen, draw_x, draw_y):
        """
        繪製健康條和狀態指示器\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        draw_x (int): 螢幕上的X座標\n
        draw_y (int): 螢幕上的Y座標\n
        """
        # 根據是否有圖像調整健康條大小和位置
        if self.image:
            bar_width = max(self.image_size[0], 40)
            bar_y_offset = self.image_size[1] // 2 + 8
        else:
            bar_width = self.size * 2
            bar_y_offset = self.size + 12
            
        bar_height = 5 if self.rarity == RarityLevel.RARE else 4  # 稀有動物的健康條稍厚
        bar_x = draw_x - bar_width // 2
        bar_y = draw_y - bar_y_offset

        # 背景條 (紅色)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # 健康條顏色根據動物狀態調整
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        
        if self.state == AnimalState.FLEEING and self.rarity == RarityLevel.RARE:
            # 逃跑中的稀有動物用橙色健康條
            health_color = (255, 165, 0)
        elif health_ratio > 0.7:
            health_color = (0, 255, 0)  # 綠色
        elif health_ratio > 0.3:
            health_color = (255, 255, 0)  # 黃色
        else:
            health_color = (255, 100, 100)  # 淡紅色
            
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # 稀有動物額外顯示驚恐狀態指示器
        if self.rarity == RarityLevel.RARE and self.state == AnimalState.FLEEING:
            # 在健康條上方顯示小驚嘆號
            status_y = bar_y - 10
            pygame.draw.circle(screen, (255, 200, 0), (draw_x, status_y), 3)
            pygame.draw.circle(screen, (255, 255, 255), (draw_x, status_y), 1)

    def draw_info(self, screen, font):
        """
        繪製動物詳細資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體物件\n
        """
        # 根據是否有圖像調整資訊位置
        if self.image:
            name_y_offset = self.image_size[1] // 2 + 25
            status_y_offset = self.image_size[1] // 2 + 15
        else:
            name_y_offset = self.size + 25
            status_y_offset = self.size + 15
        
        # 動物名稱
        name_surface = font.render(self.animal_type.value, True, (0, 0, 0))
        name_rect = name_surface.get_rect(
            center=(int(self.x), int(self.y) - name_y_offset)
        )
        screen.blit(name_surface, name_rect)

        # 狀態資訊
        status_text = f"{self.state.value}"
        if self.is_protected:
            status_text += " [保育類]"

        status_surface = font.render(status_text, True, (100, 100, 100))
        status_rect = status_surface.get_rect(
            center=(int(self.x), int(self.y) + status_y_offset)
        )
        screen.blit(status_surface, status_rect)

    def __str__(self):
        """
        動物的字串表示\n
        \n
        回傳:\n
        str: 動物描述\n
        """
        status = "死亡" if not self.is_alive else self.state.value
        protection = " [保育類]" if self.is_protected else ""
        return f"{self.animal_type.value} (ID: {self.id}) - {status}{protection}"
    
    def attack_player(self, player_position):
        """
        攻擊玩家\n
        
        參數:\n
        player_position (tuple): 玩家位置\n
        
        回傳:\n
        bool: 是否成功攻擊\n
        """
        if not self.is_alive or self.damage <= 0:
            return False
            
        # 檢查攻擊冷卻
        import time
        current_time = time.time()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
            
        # 檢查攻擊範圍
        distance = self._calculate_distance_to_player(player_position)
        if distance > self.attack_range:
            return False
            
        # 執行攻擊
        self.last_attack_time = current_time
        self.has_attacked_player = True
        print(f"{self.animal_type.value} 攻擊了玩家，造成 {self.damage} 點傷害！")
        return True
    
    def _set_flee_target(self, threat_position):
        """
        設定逃跑目標位置（遠離威脅）\n
        
        參數:\n
        threat_position (tuple): 威脅位置\n
        """
        if threat_position is None:
            return
            
        # 計算遠離威脅的方向
        dx = self.x - threat_position[0]
        dy = self.y - threat_position[1]
        
        # 標準化方向向量
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            dx /= distance
            dy /= distance
        else:
            # 如果在同一位置，隨機選擇方向
            import random
            angle = random.uniform(0, 2 * math.pi)
            dx = math.cos(angle)
            dy = math.sin(angle)
        
        # 設定逃跑目標（距離威脅200像素）
        flee_distance = 200
        self.flee_target = (
            self.x + dx * flee_distance,
            self.y + dy * flee_distance
        )
        
        # 確保逃跑目標在棲息地範圍內
        if self.habitat_bounds:
            hx, hy, hw, hh = self.habitat_bounds
            self.flee_target = (
                max(hx, min(hx + hw, self.flee_target[0])),
                max(hy, min(hy + hh, self.flee_target[1]))
            )
        
        # 更新移動目標
        self.target_x, self.target_y = self.flee_target
        
        # 提高逃跑時的速度
        self.current_speed = self.flee_speed
        
        print(f"{self.animal_type.value} 開始逃跑到 ({self.target_x:.1f}, {self.target_y:.1f})")
    
    def get_damage(self):
        """
        獲取動物的攻擊傷害\n
        
        回傳:\n
        int: 攻擊傷害值\n
        """
        return self.damage
