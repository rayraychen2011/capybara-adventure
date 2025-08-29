######################載入套件######################
import pygame
import math
import time
from config.settings import *


######################武器類別######################
class Weapon:
    """
    武器基礎類別 - 管理各種武器的屬性和行為\n
    \n
    支援不同類型的武器，包括手槍、步槍、霰彈槍等\n
    每種武器都有不同的傷害、射程、精確度和彈藥容量\n
    武器可以透過槍械店購買或升級\n
    """

    def __init__(self, weapon_type):
        """
        初始化武器\n
        \n
        參數:\n
        weapon_type (str): 武器類型\n
        """
        self.weapon_type = weapon_type
        self._setup_weapon_properties()

        # 武器狀態
        self.current_ammo = self.magazine_size
        self.total_ammo = 0
        self.last_shot_time = 0
        self.is_reloading = False
        self.reload_start_time = 0

        print(f"創建武器: {self.name}")

    def _setup_weapon_properties(self):
        """
        根據武器類型設定屬性\n
        """
        if self.weapon_type == "pistol":
            self.name = "手槍"
            self.damage = 25
            self.range = 200
            self.accuracy = 0.8
            self.fire_rate = 2.0  # 每秒射擊次數
            self.magazine_size = 12
            self.reload_time = 2.0  # 重新裝彈時間 (秒)
            self.ammo_type = "9mm"
            self.price = 500

        elif self.weapon_type == "rifle":
            self.name = "步槍"
            self.damage = 50
            self.range = 400
            self.accuracy = 0.9
            self.fire_rate = 1.0
            self.magazine_size = 30
            self.reload_time = 3.0
            self.ammo_type = "7.62mm"
            self.price = 1500

        elif self.weapon_type == "shotgun":
            self.name = "霰彈槍"
            self.damage = 80
            self.range = 100
            self.accuracy = 0.6
            self.fire_rate = 0.5
            self.magazine_size = 6
            self.reload_time = 4.0
            self.ammo_type = "12gauge"
            self.price = 800

        elif self.weapon_type == "sniper":
            self.name = "狙擊槍"
            self.damage = 100
            self.range = 600
            self.accuracy = 0.95
            self.fire_rate = 0.3
            self.magazine_size = 5
            self.reload_time = 3.5
            self.ammo_type = ".308"
            self.price = 3000

        elif self.weapon_type == "unarmed":
            self.name = "空手"
            self.damage = 15
            self.range = 30  # 近戰範圍
            self.accuracy = 0.9  # 近戰命中率高
            self.fire_rate = 3.0  # 空手攻擊速度快
            self.magazine_size = 999  # 空手不需要彈藥
            self.reload_time = 0  # 空手不需要重新裝彈
            self.ammo_type = "無"
            self.price = 0  # 空手免費

        else:
            # 預設手槍設定
            self.name = "基本武器"
            self.damage = 20
            self.range = 150
            self.accuracy = 0.7
            self.fire_rate = 1.5
            self.magazine_size = 10
            self.reload_time = 2.5
            self.ammo_type = "通用"
            self.price = 300

    def can_shoot(self):
        """
        檢查是否可以射擊\n
        \n
        回傳:\n
        bool: 是否可以射擊\n
        """
        current_time = time.time()

        # 空手武器不需要彈藥檢查
        if self.weapon_type == "unarmed":
            # 只檢查攻擊速度限制
            time_since_last_shot = current_time - self.last_shot_time
            min_interval = 1.0 / self.fire_rate
            return time_since_last_shot >= min_interval

        # 檢查彈藥
        if self.current_ammo <= 0:
            return False

        # 檢查射速限制
        time_since_last_shot = current_time - self.last_shot_time
        min_interval = 1.0 / self.fire_rate

        if time_since_last_shot < min_interval:
            return False

        # 檢查是否在重新裝彈
        if self.is_reloading:
            return False

        return True

    def shoot(self, target_position, shooter_position):
        """
        射擊\n
        \n
        參數:\n
        target_position (tuple): 目標位置 (x, y)\n
        shooter_position (tuple): 射手位置 (x, y)\n
        \n
        回傳:\n
        dict: 射擊結果 {\n
            'success': bool - 是否成功射擊\n
            'hit': bool - 是否命中目標\n
            'damage': int - 造成的傷害\n
            'distance': float - 射擊距離\n
        }\n
        """
        if not self.can_shoot():
            return {"success": False, "hit": False, "damage": 0, "distance": 0}

        # 計算射擊距離
        sx, sy = shooter_position
        tx, ty = target_position
        distance = math.sqrt((tx - sx) ** 2 + (ty - sy) ** 2)

        # 檢查射程
        if distance > self.range:
            return {"success": True, "hit": False, "damage": 0, "distance": distance}

        # 空手武器不消耗彈藥
        if self.weapon_type != "unarmed":
            # 消耗彈藥
            self.current_ammo -= 1
        
        self.last_shot_time = time.time()

        # 計算命中率 (考慮距離和武器精確度)
        distance_factor = max(0.2, 1.0 - (distance / self.range) * 0.5)
        hit_chance = self.accuracy * distance_factor

        # 判斷是否命中
        import random

        hit = random.random() <= hit_chance

        # 計算傷害 (距離會影響傷害)
        damage = 0
        if hit:
            damage_reduction = min(0.5, distance / self.range * 0.3)
            damage = int(self.damage * (1.0 - damage_reduction))

        return {"success": True, "hit": hit, "damage": damage, "distance": distance}

    def start_reload(self):
        """
        開始重新裝彈\n
        \n
        回傳:\n
        bool: 是否開始重新裝彈\n
        """
        # 空手武器不需要重新裝彈
        if self.weapon_type == "unarmed":
            return False
            
        if self.is_reloading or self.total_ammo <= 0:
            return False

        self.is_reloading = True
        self.reload_start_time = time.time()
        print(f"開始為 {self.name} 重新裝彈...")
        return True

    def update_reload(self):
        """
        更新重新裝彈狀態\n
        \n
        回傳:\n
        bool: 重新裝彈是否完成\n
        """
        if not self.is_reloading:
            return False

        current_time = time.time()
        elapsed = current_time - self.reload_start_time

        if elapsed >= self.reload_time:
            # 重新裝彈完成
            ammo_needed = self.magazine_size - self.current_ammo
            ammo_to_load = min(ammo_needed, self.total_ammo)

            self.current_ammo += ammo_to_load
            self.total_ammo -= ammo_to_load

            self.is_reloading = False
            print(
                f"{self.name} 重新裝彈完成! 彈匣: {self.current_ammo}/{self.magazine_size}"
            )
            return True

        return False

    def add_ammo(self, amount):
        """
        新增彈藥\n
        \n
        參數:\n
        amount (int): 彈藥數量\n
        """
        self.total_ammo += amount
        print(f"為 {self.name} 新增 {amount} 發 {self.ammo_type} 彈藥")

    def get_ammo_info(self):
        """
        獲取彈藥資訊\n
        \n
        回傳:\n
        dict: 彈藥資訊\n
        """
        return {
            "current": self.current_ammo,
            "magazine": self.magazine_size,
            "total": self.total_ammo,
            "type": self.ammo_type,
        }


######################子彈類別######################
class Bullet:
    """
    子彈類別 - 處理子彈的飛行和碰撞\n
    \n
    管理子彈從發射到命中或消失的整個生命週期\n
    包含飛行軌跡、碰撞檢測和視覺效果\n
    """

    def __init__(self, start_pos, target_pos, damage, speed=BULLET_SPEED):
        """
        初始化子彈\n
        \n
        參數:\n
        start_pos (tuple): 起始位置 (x, y)\n
        target_pos (tuple): 目標位置 (x, y)\n
        damage (int): 傷害值\n
        speed (float): 飛行速度\n
        """
        self.x, self.y = start_pos
        self.damage = damage
        self.speed = speed
        self.is_active = True

        # 計算飛行方向
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            self.velocity_x = (dx / distance) * speed
            self.velocity_y = (dy / distance) * speed
        else:
            self.velocity_x = 0
            self.velocity_y = 0

        # 子彈生命週期
        self.life_time = 0
        self.max_life_time = 5.0  # 最大存在時間 (秒)

    def update(self, dt):
        """
        更新子彈位置\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        if not self.is_active:
            return

        # 更新位置
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # 更新生命時間
        self.life_time += dt

        # 檢查生命週期
        if self.life_time >= self.max_life_time:
            self.is_active = False

    def check_collision(self, target_rect):
        """
        檢查與目標的碰撞\n
        \n
        參數:\n
        target_rect (pygame.Rect): 目標碰撞框\n
        \n
        回傳:\n
        bool: 是否碰撞\n
        """
        if not self.is_active:
            return False

        bullet_rect = pygame.Rect(int(self.x) - 2, int(self.y) - 2, 4, 4)

        if bullet_rect.colliderect(target_rect):
            self.is_active = False
            return True

        return False

    def draw(self, screen):
        """
        繪製子彈\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        if self.is_active:
            # 繪製子彈 (小黃點)
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 3)

            # 繪製拖尾效果
            trail_length = 10
            trail_x = self.x - self.velocity_x * 0.1
            trail_y = self.y - self.velocity_y * 0.1
            pygame.draw.line(
                screen, (255, 200, 0), (trail_x, trail_y), (self.x, self.y), 2
            )


######################槍械管理器######################
class WeaponManager:
    """
    槍械管理器 - 統一管理玩家的武器和射擊系統\n
    \n
    負責武器切換、彈藥管理、射擊邏輯和子彈物理\n
    整合武器商店和彈藥補給系統\n
    """

    def __init__(self):
        """
        初始化槍械管理器\n
        """
        self.weapons = {}  # 玩家擁有的武器
        self.current_weapon = None
        self.bullets = []  # 活躍的子彈

        # 初始化玩家的手槍和空手
        initial_pistol = Weapon("pistol")
        initial_pistol.add_ammo(INITIAL_AMMO)
        self.add_weapon(initial_pistol)
        
        # 添加空手武器
        unarmed_weapon = Weapon("unarmed")
        self.add_weapon(unarmed_weapon)
        
        # 預設使用空手
        self.current_weapon = unarmed_weapon

        print("槍械管理器初始化完成，配發初始手槍和空手武器，預設為空手")

    def add_weapon(self, weapon):
        """
        新增武器到玩家裝備\n
        \n
        參數:\n
        weapon (Weapon): 武器物件\n
        """
        self.weapons[weapon.weapon_type] = weapon
        print(f"獲得新武器: {weapon.name}")

    def switch_weapon(self, weapon_type):
        """
        切換武器\n
        \n
        參數:\n
        weapon_type (str): 武器類型\n
        \n
        回傳:\n
        bool: 是否成功切換\n
        """
        if weapon_type in self.weapons:
            self.current_weapon = self.weapons[weapon_type]
            print(f"切換到: {self.current_weapon.name}")
            return True
        return False

    def get_available_weapons(self):
        """
        獲取可用武器列表\n
        \n
        回傳:\n
        list: 武器類型列表\n
        """
        return list(self.weapons.keys())

    def shoot(self, target_position, shooter_position):
        """
        射擊\n
        \n
        參數:\n
        target_position (tuple): 目標位置\n
        shooter_position (tuple): 射手位置\n
        \n
        回傳:\n
        dict: 射擊結果\n
        """
        if not self.current_weapon:
            return {"success": False, "reason": "沒有裝備武器"}

        # 檢查是否正在重新裝彈
        self.current_weapon.update_reload()

        # 嘗試射擊
        result = self.current_weapon.shoot(target_position, shooter_position)

        if result["success"]:
            # 空手攻擊不創建子彈
            if self.current_weapon.weapon_type == "unarmed":
                print(f"空手攻擊! 距離: {result['distance']:.1f}, 命中: {result['hit']}, 傷害: {result['damage']}")
            else:
                # 創建子彈
                bullet = Bullet(shooter_position, target_position, result["damage"])
                self.bullets.append(bullet)
                print(f"射擊! 距離: {result['distance']:.1f}, 命中: {result['hit']}, 傷害: {result['damage']}")

        return result

    def reload_current_weapon(self):
        """
        重新裝彈當前武器\n
        \n
        回傳:\n
        bool: 是否開始重新裝彈\n
        """
        if self.current_weapon:
            return self.current_weapon.start_reload()
        return False

    def update(self, dt):
        """
        更新槍械系統\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新當前武器的重新裝彈狀態
        if self.current_weapon:
            self.current_weapon.update_reload()

        # 更新所有子彈
        for bullet in self.bullets[:]:  # 使用切片複製避免修改列表時出錯
            bullet.update(dt)
            if not bullet.is_active:
                self.bullets.remove(bullet)

    def check_bullet_collisions(self, targets):
        """
        檢查子彈碰撞\n
        \n
        參數:\n
        targets (list): 目標列表，每個目標應該有 'rect' 和 'take_damage' 方法\n
        \n
        回傳:\n
        list: 命中的目標列表\n
        """
        hit_targets = []

        for bullet in self.bullets[:]:
            for target in targets:
                if hasattr(target, "rect") and bullet.check_collision(target.rect):
                    # 對目標造成傷害
                    if hasattr(target, "take_damage"):
                        target.take_damage(bullet.damage)

                    hit_targets.append(
                        {
                            "target": target,
                            "damage": bullet.damage,
                            "position": (bullet.x, bullet.y),
                        }
                    )

                    self.bullets.remove(bullet)
                    break

        return hit_targets

    def get_current_weapon_info(self):
        """
        獲取當前武器資訊\n
        \n
        回傳:\n
        dict: 武器資訊\n
        """
        if not self.current_weapon:
            return None

        return {
            "name": self.current_weapon.name,
            "type": self.current_weapon.weapon_type,
            "ammo": self.current_weapon.get_ammo_info(),
            "damage": self.current_weapon.damage,
            "range": self.current_weapon.range,
            "is_reloading": self.current_weapon.is_reloading,
        }

    def draw_bullets(self, screen):
        """
        繪製所有子彈\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for bullet in self.bullets:
            bullet.draw(screen)

    def draw_weapon_ui(self, screen, font):
        """
        繪製武器介面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體\n
        """
        if not self.current_weapon:
            return

        # 顯示當前武器名稱
        weapon_text = font.render(
            f"武器: {self.current_weapon.name}", True, (255, 255, 255)
        )
        screen.blit(weapon_text, (10, SCREEN_HEIGHT - 120))

        # 顯示彈藥資訊
        ammo_info = self.current_weapon.get_ammo_info()
        if self.current_weapon.weapon_type == "unarmed":
            # 空手武器顯示不同的資訊
            ammo_text = font.render("武器: 空手 (近戰攻擊)", True, (255, 255, 255))
        else:
            ammo_text = font.render(
                f"彈藥: {ammo_info['current']}/{ammo_info['magazine']} ({ammo_info['total']})",
                True,
                (255, 255, 255),
            )
        screen.blit(ammo_text, (10, SCREEN_HEIGHT - 100))

        # 顯示重新裝彈狀態
        if self.current_weapon.weapon_type != "unarmed":
            if self.current_weapon.is_reloading:
                reload_text = font.render("重新裝彈中...", True, (255, 255, 0))
                screen.blit(reload_text, (10, SCREEN_HEIGHT - 80))
            elif ammo_info["current"] == 0:
                empty_text = font.render("需要重新裝彈 (R鍵)", True, (255, 0, 0))
                screen.blit(empty_text, (10, SCREEN_HEIGHT - 80))
