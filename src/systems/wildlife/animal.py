######################載入套件######################
import pygame
import random
import math
from enum import Enum
from src.systems.wildlife.animal_data import (
    AnimalType,
    AnimalData,
    ThreatLevel,
    BehaviorType,
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

        # 從動物資料獲取屬性
        self.size = AnimalData.get_animal_property(animal_type, "size") or 16
        self.max_speed = AnimalData.get_animal_property(animal_type, "speed") or 2.0
        self.current_speed = self.max_speed
        self.max_health = AnimalData.get_animal_property(animal_type, "health") or 50
        self.health = self.max_health

        # 行為屬性
        self.threat_level = AnimalData.get_animal_property(animal_type, "threat_level")
        self.behavior_type = AnimalData.get_animal_property(animal_type, "behavior")
        self.is_protected = (
            AnimalData.get_animal_property(animal_type, "is_protected") or False
        )

        # 外觀
        self.color = AnimalData.get_animal_property(animal_type, "color") or (
            128,
            128,
            128,
        )

        # AI 相關變數
        self.last_target_change = 0  # 上次改變目標的時間
        self.alert_timer = 0  # 警戒狀態計時器
        self.flee_timer = 0  # 逃跑狀態計時器
        self.wander_timer = 0  # 漫遊計時器
        self.detection_range = 80  # 玩家檢測範圍

        # 生存狀態
        self.is_alive = True
        self.death_time = 0
        self.killer = None  # 殺死此動物的對象

        # 掉落物品
        self.drop_items = AnimalData.get_animal_loot(animal_type)

        print(f"創建動物: {animal_type.value} (ID: {self.id})")

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

        # 根據當前狀態更新行為
        self._update_behavior_state(dt, player_position, player_distance)

        # 執行當前狀態的行為
        self._execute_current_behavior(dt, player_position, player_distance)

        # 更新移動
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
                    BehaviorType.AGGRESSIVE,
                    BehaviorType.PREDATOR,
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
        逃跑行為 - 快速遠離玩家\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        """
        self.current_speed = self.max_speed * 1.3  # 加速逃跑

        # 持續更新逃跑方向
        if random.random() < 0.1:  # 10% 機率調整逃跑方向
            self._set_flee_target(player_position)

        # 逃跑時間結束或到達安全距離
        distance = self._calculate_distance_to_player(player_position)
        if self.flee_timer <= 0 or distance > self.detection_range * 2:
            self.state = AnimalState.HIDING
            self.wander_timer = random.uniform(3.0, 6.0)  # 躲藏一段時間

    def _attacking_behavior(self, dt, player_position):
        """
        攻擊行為 - 向玩家移動並攻擊\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        """
        self.current_speed = self.max_speed * 1.1  # 稍微加速

        # 持續追蹤玩家
        self.target_x, self.target_y = player_position

        # 檢查是否接近到可以攻擊的距離
        distance = self._calculate_distance_to_player(player_position)
        if distance < 25:  # 接近攻擊範圍
            # 執行攻擊 (這裡可以添加攻擊邏輯)
            print(f"{self.animal_type.value} 攻擊了玩家！")

            # 攻擊後可能退開一些
            if random.random() < 0.3:  # 30% 機率攻擊後退開
                self.state = AnimalState.ALERT
                self.alert_timer = 2.0

    def _hiding_behavior(self, dt):
        """
        躲藏行為 - 保持靜止\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        self.current_speed = 0  # 完全停止

        # 躲藏時間結束
        if self.wander_timer <= 0:
            self.state = AnimalState.WANDERING
            self._set_wander_target()

    def _set_wander_target(self):
        """
        設定隨機漫遊目標\n
        """
        hx, hy, hw, hh = self.habitat_bounds

        # 在棲息地範圍內選擇隨機點
        margin = 50  # 離邊界保持距離
        self.target_x = random.randint(hx + margin, hx + hw - margin)
        self.target_y = random.randint(hy + margin, hy + hh - margin)

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
        更新動物移動\n
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

                self.x += move_x
                self.y += move_y

                # 確保不超出棲息地邊界
                hx, hy, hw, hh = self.habitat_bounds
                self.x = max(hx, min(hx + hw, self.x))
                self.y = max(hy, min(hy + hh, self.y))

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
        print(f"{self.animal_type.value} 受到 {damage} 點傷害")

        # 受到攻擊時的反應
        if self.health > 0:
            if self.threat_level in [ThreatLevel.HARMLESS, ThreatLevel.LOW]:
                # 無害動物受攻擊時驚恐逃跑
                self.state = AnimalState.FLEEING
                self.flee_timer = 8.0  # 較長的逃跑時間
                if attacker:
                    self._set_flee_target(attacker.get_center_position())
            elif self.behavior_type in [
                BehaviorType.DEFENSIVE,
                BehaviorType.AGGRESSIVE,
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

    def draw(self, screen):
        """
        繪製動物\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        if not self.is_alive:
            # 死亡動物變暗顯示
            dead_color = tuple(c // 3 for c in self.color)
            pygame.draw.circle(
                screen, dead_color, (int(self.x), int(self.y)), self.size
            )
            pygame.draw.circle(
                screen, (255, 0, 0), (int(self.x), int(self.y)), self.size, 2
            )  # 紅色邊框
            return

        # 繪製動物本體
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

        # 根據狀態添加視覺效果
        if self.state == AnimalState.ALERT:
            # 警戒狀態：黃色邊框
            pygame.draw.circle(
                screen, (255, 255, 0), (int(self.x), int(self.y)), self.size, 3
            )
        elif self.state == AnimalState.FLEEING:
            # 逃跑狀態：閃爍效果
            if int(pygame.time.get_ticks() / 200) % 2:  # 每200ms閃爍一次
                pygame.draw.circle(
                    screen,
                    (255, 255, 255),
                    (int(self.x), int(self.y)),
                    self.size + 3,
                    2,
                )
        elif self.state == AnimalState.ATTACKING:
            # 攻擊狀態：紅色邊框
            pygame.draw.circle(
                screen, (255, 0, 0), (int(self.x), int(self.y)), self.size, 3
            )

        # 保育類動物特殊標記
        if self.is_protected:
            # 綠色保護標記
            pygame.draw.circle(
                screen, (0, 255, 0), (int(self.x), int(self.y) - self.size - 8), 4
            )

        # 健康條 (如果受傷)
        if self.health < self.max_health:
            self._draw_health_bar(screen)

    def _draw_health_bar(self, screen):
        """
        繪製健康條\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        bar_width = self.size * 2
        bar_height = 4
        bar_x = int(self.x - bar_width // 2)
        bar_y = int(self.y - self.size - 12)

        # 背景條 (紅色)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # 健康條 (綠色)
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))

    def draw_info(self, screen, font):
        """
        繪製動物詳細資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體物件\n
        """
        # 動物名稱
        name_surface = font.render(self.animal_type.value, True, (0, 0, 0))
        name_rect = name_surface.get_rect(
            center=(int(self.x), int(self.y) - self.size - 25)
        )
        screen.blit(name_surface, name_rect)

        # 狀態資訊
        status_text = f"{self.state.value}"
        if self.is_protected:
            status_text += " [保育類]"

        status_surface = font.render(status_text, True, (100, 100, 100))
        status_rect = status_surface.get_rect(
            center=(int(self.x), int(self.y) + self.size + 15)
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
