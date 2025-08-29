######################載入套件######################
import pygame
import math
import random
import time
from config.settings import *


######################狩獵系統######################
class HuntingSystem:
    """
    狩獵系統 - 管理動物狩獵機制\n
    \n
    負責處理玩家對野生動物的狩獵行為\n
    整合射擊系統，提供完整的狩獵體驗\n
    \n
    主要功能:\n
    1. 狩獵模式切換（G鍵啟動）\n
    2. 動物追蹤和瞄準\n
    3. 狩獵獎勵計算\n
    4. 保育類動物保護\n
    5. 狩獵統計記錄\n
    """

    def __init__(self):
        """
        初始化狩獵系統\n
        """
        # 狩獵狀態
        self.hunting_mode_active = False  # 是否啟用狩獵模式
        self.target_animal = None  # 當前瞄準的動物
        self.hunting_range = 200  # 狩獵有效範圍（像素）
        
        # 瞄準系統
        self.crosshair_visible = False  # 十字準心是否顯示
        self.target_lock_time = 0  # 瞄準鎖定時間
        self.min_lock_time = 1.0  # 最小瞄準時間（秒）
        
        # 狩獵統計
        self.animals_hunted = 0  # 獵殺動物數量
        self.protected_animals_killed = 0  # 誤殺保育類動物數量
        self.total_hunting_attempts = 0  # 總狩獵嘗試次數
        self.successful_hunts = 0  # 成功狩獵次數
        
        # 狩獵獎勵
        self.hunt_rewards = {
            "common": {"meat": 1, "money": 50, "exp": 10},
            "rare": {"meat": 2, "money": 150, "exp": 25},
            "super_rare": {"meat": 3, "money": 300, "exp": 50},
            "legendary": {"meat": 5, "money": 1000, "exp": 100}
        }
        
        # 保育類動物懲罰
        self.protected_penalty = {
            "money": -500,  # 罰款
            "reputation": -100  # 聲譽損失（預留）
        }
        
        print("狩獵系統初始化完成")

    def toggle_hunting_mode(self, player):
        """
        切換狩獵模式（G鍵觸發）\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: 狩獵模式是否啟用\n
        """
        # 檢查玩家是否裝備槍械
        if not player.can_shoot():
            print("❌ 狩獵需要裝備槍械！請按中鍵選擇武器")
            return False
        
        # 切換狩獵模式
        self.hunting_mode_active = not self.hunting_mode_active
        
        if self.hunting_mode_active:
            print("🎯 進入狩獵模式 - 滑鼠瞄準動物，左鍵射擊")
            self.crosshair_visible = True
        else:
            print("🚫 退出狩獵模式")
            self.crosshair_visible = False
            self.target_animal = None
            self.target_lock_time = 0
        
        return self.hunting_mode_active

    def find_animals_in_range(self, player_position, wildlife_manager):
        """
        尋找玩家狩獵範圍內的動物\n
        \n
        參數:\n
        player_position (tuple): 玩家位置 (x, y)\n
        wildlife_manager (WildlifeManager): 野生動物管理器\n
        \n
        回傳:\n
        list: 範圍內的動物列表\n
        """
        if not wildlife_manager:
            return []
        
        px, py = player_position
        animals_in_range = []
        
        # 使用統一的animals屬性
        for animal in wildlife_manager.animals:
            if not animal.is_alive:
                continue
            
            # 計算距離
            ax, ay = animal.get_position()
            distance = math.sqrt((ax - px) ** 2 + (ay - py) ** 2)
            
            if distance <= self.hunting_range:
                animals_in_range.append({
                    "animal": animal,
                    "distance": distance,
                    "position": (ax, ay)
                })
        
        # 按距離排序，最近的在前面
        animals_in_range.sort(key=lambda x: x["distance"])
        return animals_in_range

    def update_target_selection(self, mouse_pos, camera_offset, animals_in_range):
        """
        更新目標選擇（滑鼠瞄準）\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠螢幕位置 (x, y)\n
        camera_offset (tuple): 攝影機偏移量 (offset_x, offset_y)\n
        animals_in_range (list): 範圍內的動物列表\n
        """
        if not self.hunting_mode_active:
            return
        
        # 將滑鼠位置轉換為世界座標
        world_x = mouse_pos[0] + camera_offset[0]
        world_y = mouse_pos[1] + camera_offset[1]
        
        # 尋找滑鼠最接近的動物
        closest_animal = None
        min_cursor_distance = 50  # 滑鼠必須在動物50像素範圍內才能瞄準
        
        for animal_data in animals_in_range:
            animal = animal_data["animal"]
            ax, ay = animal_data["position"]
            
            # 計算滑鼠到動物的距離
            cursor_distance = math.sqrt((ax - world_x) ** 2 + (ay - world_y) ** 2)
            
            if cursor_distance < min_cursor_distance:
                closest_animal = animal
                min_cursor_distance = cursor_distance
        
        # 更新目標
        if closest_animal != self.target_animal:
            self.target_animal = closest_animal
            self.target_lock_time = 0  # 重置瞄準時間
            
            if self.target_animal:
                print(f"🎯 瞄準: {self.target_animal.animal_type.value}")
            else:
                print("🎯 失去目標")

    def update_targeting(self, dt):
        """
        更新瞄準狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        if self.target_animal and self.hunting_mode_active:
            self.target_lock_time += dt
        else:
            self.target_lock_time = 0

    def can_shoot_target(self):
        """
        檢查是否可以射擊目標\n
        \n
        回傳:\n
        bool: 是否可以射擊\n
        """
        if not self.hunting_mode_active:
            return False
        
        if not self.target_animal:
            return False
        
        if not self.target_animal.is_alive:
            return False
        
        # 需要瞄準一定時間才能射擊
        if self.target_lock_time < self.min_lock_time:
            return False
        
        return True

    def attempt_hunt(self, player, shooting_system, mouse_pos, camera_offset):
        """
        嘗試狩獵（左鍵射擊）\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        shooting_system (ShootingSystem): 射擊系統\n
        mouse_pos (tuple): 滑鼠位置\n
        camera_offset (tuple): 攝影機偏移量\n
        \n
        回傳:\n
        dict: 狩獵結果\n
        """
        self.total_hunting_attempts += 1
        
        # 檢查是否可以射擊
        if not self.can_shoot_target():
            return {
                "success": False,
                "message": "瞄準時間不足或無有效目標",
                "hit": False
            }
        
        # 執行射擊
        target_pos = self.target_animal.get_position()
        shot_success = shooting_system.handle_mouse_shoot(player, mouse_pos, camera_offset)
        
        if not shot_success:
            return {
                "success": False,
                "message": "射擊失敗",
                "hit": False
            }
        
        # 計算命中機率（基於瞄準時間和距離）
        player_pos = player.get_center_position()
        distance = math.sqrt(
            (target_pos[0] - player_pos[0]) ** 2 + 
            (target_pos[1] - player_pos[1]) ** 2
        )
        
        # 基礎命中率
        base_accuracy = 0.8
        
        # 距離修正
        distance_factor = max(0.3, 1.0 - (distance / self.hunting_range) * 0.5)
        
        # 瞄準時間修正
        aim_factor = min(1.0, self.target_lock_time / (self.min_lock_time * 2))
        
        # 動物移動速度修正
        speed_factor = 1.0 - (self.target_animal.current_speed / self.target_animal.max_speed * 0.3)
        
        # 最終命中率
        hit_chance = base_accuracy * distance_factor * aim_factor * speed_factor
        
        # 判斷是否命中
        hit = random.random() <= hit_chance
        
        if hit:
            return self._process_successful_hunt(distance)
        else:
            print(f"❌ 射擊失誤！命中率: {hit_chance:.1%}")
            return {
                "success": True,
                "message": "射擊失誤",
                "hit": False
            }

    def _process_successful_hunt(self, distance):
        """
        處理成功狩獵\n
        \n
        參數:\n
        distance (float): 射擊距離\n
        \n
        回傳:\n
        dict: 狩獵結果\n
        """
        if not self.target_animal:
            return {"success": False, "message": "目標動物無效", "hit": False}
        
        # 造成傷害
        damage = random.randint(80, 120)  # 狩獵用槍傷害較高
        self.target_animal.take_damage(damage, attacker=None)
        
        # 檢查動物是否死亡
        if not self.target_animal.is_alive:
            self.successful_hunts += 1
            self.animals_hunted += 1
            
            # 檢查是否為保育類動物
            if self.target_animal.is_protected:
                self.protected_animals_killed += 1
                return self._process_protected_animal_kill()
            else:
                return self._process_normal_hunt_reward()
        else:
            print(f"🎯 命中 {self.target_animal.animal_type.value}！剩餘生命: {self.target_animal.health}")
            return {
                "success": True,
                "message": f"命中但未致命！剩餘生命: {self.target_animal.health}",
                "hit": True,
                "kill": False
            }

    def _process_normal_hunt_reward(self):
        """
        處理正常狩獵獎勵\n
        \n
        回傳:\n
        dict: 獎勵資訊\n
        """
        animal_type = self.target_animal.animal_type.value
        rarity = self.target_animal.rarity.name.lower()
        
        # 獲取獎勵
        if rarity in self.hunt_rewards:
            rewards = self.hunt_rewards[rarity].copy()
        else:
            rewards = self.hunt_rewards["common"].copy()
        
        # 距離獎勵加成
        distance = math.sqrt(
            (self.target_animal.x - self.target_animal.x) ** 2 + 
            (self.target_animal.y - self.target_animal.y) ** 2
        )
        
        if distance > 150:
            rewards["money"] = int(rewards["money"] * 1.2)
            rewards["exp"] = int(rewards["exp"] * 1.2)
            distance_bonus = True
        else:
            distance_bonus = False
        
        print(f"🎉 成功獵殺 {animal_type}！")
        print(f"💰 獲得獎勵: 肉類 x{rewards['meat']}, 金錢 +${rewards['money']}, 經驗 +{rewards['exp']}")
        
        if distance_bonus:
            print("🎯 遠距離射擊獎勵！（+20%）")
        
        # 重置狩獵狀態
        self.target_animal = None
        self.target_lock_time = 0
        
        return {
            "success": True,
            "message": f"成功獵殺 {animal_type}",
            "hit": True,
            "kill": True,
            "rewards": rewards,
            "distance_bonus": distance_bonus,
            "protected": False
        }

    def _process_protected_animal_kill(self):
        """
        處理保育類動物誤殺\n
        \n
        回傳:\n
        dict: 懲罰資訊\n
        """
        animal_type = self.target_animal.animal_type.value
        
        print(f"⚠️ 警告：{animal_type} 是保育類動物！")
        print(f"💸 罰款: ${abs(self.protected_penalty['money'])}")
        print("🚨 此行為將影響你的聲譽")
        
        # 重置狩獵狀態
        self.target_animal = None
        self.target_lock_time = 0
        
        return {
            "success": True,
            "message": f"誤殺保育類動物 {animal_type}",
            "hit": True,
            "kill": True,
            "penalty": self.protected_penalty.copy(),
            "protected": True
        }

    def draw_hunting_ui(self, screen, font, mouse_pos):
        """
        繪製狩獵相關UI\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體物件\n
        mouse_pos (tuple): 滑鼠位置\n
        """
        if not self.hunting_mode_active:
            return
        
        # 繪製狩獵模式提示
        mode_text = font.render("🎯 狩獵模式", True, (255, 255, 0))
        screen.blit(mode_text, (10, 10))
        
        # 繪製目標資訊
        if self.target_animal:
            target_info = f"目標: {self.target_animal.animal_type.value}"
            if self.target_animal.is_protected:
                target_info += " [保育類]"
            
            target_text = font.render(target_info, True, (255, 255, 255))
            screen.blit(target_text, (10, 40))
            
            # 瞄準進度條
            progress = min(1.0, self.target_lock_time / self.min_lock_time)
            bar_width = 200
            bar_height = 10
            bar_x = 10
            bar_y = 70
            
            # 背景條
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            
            # 進度條
            if progress >= 1.0:
                color = (0, 255, 0)  # 綠色 - 可以射擊
                status_text = "可以射擊！"
            else:
                color = (255, 255, 0)  # 黃色 - 瞄準中
                status_text = "瞄準中..."
            
            pygame.draw.rect(screen, color, (bar_x, bar_y, int(bar_width * progress), bar_height))
            
            # 狀態文字
            status_surface = font.render(status_text, True, color)
            screen.blit(status_surface, (bar_x, bar_y + 15))
        
        # 繪製準心
        self._draw_hunting_crosshair(screen, mouse_pos)

    def _draw_hunting_crosshair(self, screen, mouse_pos):
        """
        繪製狩獵準心\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        mouse_pos (tuple): 滑鼠位置\n
        """
        if not self.crosshair_visible:
            return
        
        x, y = mouse_pos
        
        # 準心顏色
        if self.target_animal:
            if self.can_shoot_target():
                color = (0, 255, 0)  # 綠色 - 可以射擊
            else:
                color = (255, 255, 0)  # 黃色 - 瞄準中
        else:
            color = (255, 255, 255)  # 白色 - 無目標
        
        # 繪製十字準心
        crosshair_size = 15
        thickness = 2
        
        # 水平線
        pygame.draw.line(screen, color, 
                        (x - crosshair_size, y), (x + crosshair_size, y), thickness)
        # 垂直線
        pygame.draw.line(screen, color, 
                        (x, y - crosshair_size), (x, y + crosshair_size), thickness)
        
        # 中心點
        pygame.draw.circle(screen, color, (x, y), 3)
        
        # 瞄準圈（如果有目標）
        if self.target_animal:
            circle_radius = 20 + int(math.sin(pygame.time.get_ticks() / 200) * 5)
            pygame.draw.circle(screen, color, (x, y), circle_radius, 2)

    def draw_target_indicators(self, screen, camera_offset, animals_in_range):
        """
        繪製動物目標指示器\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_offset (tuple): 攝影機偏移量\n
        animals_in_range (list): 範圍內的動物列表\n
        """
        if not self.hunting_mode_active:
            return
        
        offset_x, offset_y = camera_offset
        
        for animal_data in animals_in_range:
            animal = animal_data["animal"]
            ax, ay = animal_data["position"]
            
            # 轉換為螢幕座標
            screen_x = int(ax - offset_x)
            screen_y = int(ay - offset_y)
            
            # 跳過螢幕外的動物
            if (screen_x < -50 or screen_x > SCREEN_WIDTH + 50 or 
                screen_y < -50 or screen_y > SCREEN_HEIGHT + 50):
                continue
            
            # 決定指示器顏色
            if animal == self.target_animal:
                if self.can_shoot_target():
                    color = (0, 255, 0)  # 綠色 - 已鎖定
                else:
                    color = (255, 255, 0)  # 黃色 - 瞄準中
                radius = 25
            else:
                color = (255, 255, 255)  # 白色 - 可瞄準
                radius = 20
            
            # 繪製圓形指示器
            pygame.draw.circle(screen, color, (screen_x, screen_y), radius, 2)
            
            # 保育類動物特殊標記
            if animal.is_protected:
                pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y - radius - 10), 5)

    def get_hunting_statistics(self):
        """
        獲取狩獵統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊\n
        """
        success_rate = (
            (self.successful_hunts / self.total_hunting_attempts * 100) 
            if self.total_hunting_attempts > 0 else 0
        )
        
        return {
            "total_attempts": self.total_hunting_attempts,
            "successful_hunts": self.successful_hunts,
            "animals_hunted": self.animals_hunted,
            "protected_killed": self.protected_animals_killed,
            "success_rate": success_rate,
            "hunting_mode_active": self.hunting_mode_active
        }

    def reset_statistics(self):
        """
        重置狩獵統計\n
        """
        self.animals_hunted = 0
        self.protected_animals_killed = 0
        self.total_hunting_attempts = 0
        self.successful_hunts = 0
        print("狩獵統計已重置")

    def deactivate_hunting_mode(self):
        """
        強制退出狩獵模式\n
        """
        self.hunting_mode_active = False
        self.crosshair_visible = False
        self.target_animal = None
        self.target_lock_time = 0
        print("🚫 狩獵模式已停用")