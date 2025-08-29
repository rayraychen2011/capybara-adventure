######################載入套件######################
import pygame
import math
import time
from config.settings import *


######################子彈類別######################
class Bullet:
    """
    子彈類別 - 處理子彈的飛行和碰撞\n
    \n
    管理子彈從發射到命中或消失的整個生命週期\n
    包含飛行軌跡、碰撞檢測和視覺效果\n
    """

    def __init__(self, start_pos, target_pos, damage=25, speed=300):
        """
        初始化子彈\n
        \n
        參數:\n
        start_pos (tuple): 起始位置 (x, y)\n
        target_pos (tuple): 目標位置 (x, y)\n
        damage (int): 傷害值\n
        speed (float): 飛行速度（像素/秒）- 調慢以便玩家觀察\n
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
        self.max_life_time = 3.0  # 最大存在時間 (秒)

        # 視覺效果（BB槍專用增強特效）
        self.radius = 6  # 增大子彈半徑讓子彈更明顯
        self.color = (255, 255, 100)  # 亮黃色子彈
        self.trail_positions = []   # 拖尾軌跡
        
        # BB槍特效屬性
        self.glow_intensity = 1.0  # 光暈強度
        self.sparkle_timer = 0  # 閃爍計時器

    def update(self, dt):
        """
        更新子彈位置\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        if not self.is_active:
            return

        # 記錄軌跡位置（增加拖尾長度讓子彈更明顯）
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > 12:  # 更長的拖尾
            self.trail_positions.pop(0)

        # 更新位置
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # 更新生命時間
        self.life_time += dt
        
        # 更新特效
        self.sparkle_timer += dt
        
        # 光暈強度隨時間變化（閃爍效果）
        self.glow_intensity = 0.8 + 0.4 * math.sin(self.sparkle_timer * 15)

        # 檢查生命週期
        if self.life_time >= self.max_life_time:
            self.is_active = False

        # 檢查是否飛出世界地圖邊界（而不是螢幕邊界）
        if (self.x < -50 or self.x > TOWN_TOTAL_WIDTH + 50 or 
            self.y < -50 or self.y > TOWN_TOTAL_HEIGHT + 50):
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

        bullet_rect = pygame.Rect(int(self.x) - self.radius, int(self.y) - self.radius, 
                                 self.radius * 2, self.radius * 2)

        if bullet_rect.colliderect(target_rect):
            self.is_active = False
            return True

        return False

    def draw(self, screen, camera_offset=(0, 0)):
        """
        繪製子彈（簡化版）\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_offset (tuple): 攝影機偏移量\n
        """
        if not self.is_active:
            return

        # 計算螢幕位置
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        # 檢查子彈是否在螢幕範圍內
        if (screen_x < -10 or screen_x > SCREEN_WIDTH + 10 or 
            screen_y < -10 or screen_y > SCREEN_HEIGHT + 10):
            return  # 不在螢幕範圍內，不繪製

        # 簡化子彈繪製 - 只繪製核心圓點
        pygame.draw.circle(screen, (255, 255, 0), (screen_x, screen_y), 3)  # 黃色圓點
        pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), 1)  # 白色中心點
        

######################射擊系統######################
class ShootingSystem:
    """
    射擊系統 - 管理玩家的射擊行為和子彈物理\n
    \n
    負責處理射擊輸入、子彈生成、飛行軌跡和碰撞檢測\n
    整合武器系統，提供完整的射擊遊戲體驗\n
    """

    def __init__(self):
        """
        初始化射擊系統\n
        """
        self.bullets = []  # 活躍的子彈列表
        self.last_shot_time = 0  # 上次射擊時間
        
        # 全自動射擊設定 - BB槍每秒10發
        self.is_auto_firing = True  # 永遠開啟全自動模式
        self.auto_fire_rate = 10.0  # 每秒10發子彈
        self.shot_cooldown = 1.0 / self.auto_fire_rate  # 0.1秒間隔
        
        # 射擊統計
        self.shots_fired = 0
        self.hits_count = 0
        
        # 初始化音效系統
        self.sound_manager = ShootingSoundManager()
        
        print("射擊系統初始化完成（BB槍全自動模式 - 每秒10發）")

    def can_shoot(self, player):
        """
        檢查是否可以射擊（BB槍全自動模式）\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: 是否可以射擊\n
        """
        current_time = time.time()
        
        # BB槍永遠可以射擊（假設有無限彈藥）
        # 只檢查射速冷卻時間
        if current_time - self.last_shot_time < self.shot_cooldown:
            return False
        
        return True

    def shoot(self, player, target_pos):
        """
        執行射擊\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        target_pos (tuple): 目標位置 (x, y)（世界座標）\n
        \n
        回傳:\n
        bool: 是否成功射擊\n
        """
        if not self.can_shoot(player):
            return False

        # 獲取玩家中心位置作為射擊起點
        start_pos = player.get_center_position()
        
        # 創建子彈，使用玩家當前武器的傷害值
        weapon_damage = player.get_weapon_damage()
        bullet = Bullet(start_pos, target_pos, damage=weapon_damage)
        self.bullets.append(bullet)
        
        # 播放BB槍射擊音效
        self.sound_manager.play_shot_sound("bb_gun")
        
        # 更新射擊時間和統計
        self.last_shot_time = time.time()
        self.shots_fired += 1
        
        print(f"🔫 BB槍射擊! 目標: ({target_pos[0]:.0f}, {target_pos[1]:.0f})")
        return True

    def start_auto_fire(self):
        """
        開始全自動射擊模式（BB槍永遠開啟）\n
        """
        self.is_auto_firing = True
        print("🔥 BB槍全自動射擊模式（永遠開啟）")

    def stop_auto_fire(self):
        """
        停止全自動射擊模式（BB槍不會停止）\n
        """
        # BB槍永遠保持全自動
        self.is_auto_firing = True
        print("⚡ BB槍全自動模式無法關閉")

    def handle_auto_fire(self, player, target_pos):
        """
        處理全自動射擊\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        target_pos (tuple): 目標位置 (x, y)（世界座標）\n
        \n
        回傳:\n
        bool: 是否成功射擊\n
        """
        if not self.is_auto_firing:
            return False
            
        return self.shoot(player, target_pos)
    def handle_mouse_shoot(self, player, mouse_pos, camera_offset=(0, 0)):
        """
        處理滑鼠射擊（BB槍全自動模式）\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        mouse_pos (tuple): 滑鼠螢幕位置 (x, y)\n
        camera_offset (tuple): 攝影機偏移量\n
        \n
        回傳:\n
        bool: 是否成功射擊\n
        """
        # 將滑鼠位置轉換為世界座標
        world_x = mouse_pos[0] + camera_offset[0]
        world_y = mouse_pos[1] + camera_offset[1]
        
        # BB槍永遠處於全自動模式
        return self.handle_auto_fire(player, (world_x, world_y))

    def update(self, dt):
        """
        更新射擊系統（包含全自動射擊邏輯）\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新所有子彈
        for bullet in self.bullets[:]:  # 使用切片複製避免修改列表時出錯
            bullet.update(dt)
            
            # 子彈更新調試
            if len(self.bullets) <= 3:  # 只在子彈數量少時顯示，避免刷屏
                print(f"🔹 子彈更新: 位置 ({bullet.x:.1f}, {bullet.y:.1f}), 存活 {bullet.life_time:.2f}s, 狀態: {'活躍' if bullet.is_active else '失效'}")
            
            if not bullet.is_active:
                self.bullets.remove(bullet)

    def check_bullet_collisions(self, targets):
        """
        檢查子彈碰撞\n
        \n
        參數:\n
        targets (list): 目標列表，每個目標應該有 'rect' 屬性或 'get_rect()' 方法，以及可選的 'take_damage' 方法\n
        \n
        回傳:\n
        list: 命中的目標資訊列表\n
        """
        hit_targets = []

        for bullet in self.bullets[:]:
            for target in targets:
                # 獲取目標的碰撞矩形
                target_rect = None
                if hasattr(target, "rect"):
                    target_rect = target.rect
                elif hasattr(target, "get_rect"):
                    target_rect = target.get_rect()
                
                # 檢查碰撞
                if target_rect and bullet.check_collision(target_rect):
                    # 對目標造成傷害
                    if hasattr(target, "take_damage"):
                        target.take_damage(bullet.damage)

                    hit_targets.append({
                        "target": target,
                        "damage": bullet.damage,
                        "position": (bullet.x, bullet.y),
                    })

                    self.bullets.remove(bullet)
                    self.hits_count += 1
                    print(f"💥 命中目標! 傷害: {bullet.damage}")
                    break

        return hit_targets

    def draw_bullets(self, screen, camera_offset=(0, 0)):
        """
        繪製所有子彈\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_offset (tuple): 攝影機偏移量\n
        """
        for bullet in self.bullets:
            bullet.draw(screen, camera_offset)

    def draw_shooting_ui(self, screen, player):
        """
        繪製射擊相關UI（包含全自動模式指示）\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        player (Player): 玩家物件\n
        """
        # 顯示當前武器
        from src.utils.font_manager import get_font_manager
        font_manager = get_font_manager()
        
        weapon_text = font_manager.render_text_with_outline("武器: 全自動BB槍", 20, TEXT_COLOR)
        screen.blit(weapon_text, (10, SCREEN_HEIGHT - 60))
        
        # 顯示射擊模式
        mode_text = font_manager.render_text_with_outline("🔥 BB槍全自動射擊中（每秒10發）", 20, (255, 100, 100))
        screen.blit(mode_text, (10, SCREEN_HEIGHT - 90))
        
        # 顯示射擊統計（調試用）
        if self.shots_fired > 0:
            accuracy = (self.hits_count / self.shots_fired) * 100
            stats_text = font_manager.render_text_with_outline(
                f"射擊: {self.shots_fired} | 命中: {self.hits_count} | 精確度: {accuracy:.1f}%", 
                18, TEXT_COLOR)
            screen.blit(stats_text, (10, SCREEN_HEIGHT - 40))

        # 顯示準星（BB槍永遠顯示）
        mouse_pos = pygame.mouse.get_pos()
        self._draw_crosshair(screen, mouse_pos)

    def _draw_crosshair(self, screen, mouse_pos):
        """
        繪製準星\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        mouse_pos (tuple): 滑鼠位置\n
        """
        x, y = mouse_pos
        crosshair_size = 10
        crosshair_color = (255, 0, 0)  # 紅色準星
        
        # 繪製十字準星
        pygame.draw.line(screen, crosshair_color, 
                        (x - crosshair_size, y), (x + crosshair_size, y), 2)
        pygame.draw.line(screen, crosshair_color, 
                        (x, y - crosshair_size), (x, y + crosshair_size), 2)
        
        # 繪製中心點
        pygame.draw.circle(screen, crosshair_color, (x, y), 2)

    def get_bullet_count(self):
        """
        獲取當前場景中的子彈數量\n
        \n
        回傳:\n
        int: 子彈數量\n
        """
        return len(self.bullets)

    def clear_all_bullets(self):
        """
        清除所有子彈\n
        """
        self.bullets.clear()
        print("已清除所有子彈")

    def get_statistics(self):
        """
        獲取射擊統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊\n
        """
        accuracy = (self.hits_count / self.shots_fired * 100) if self.shots_fired > 0 else 0
        return {
            "shots_fired": self.shots_fired,
            "hits_count": self.hits_count,
            "accuracy": accuracy,
            "active_bullets": len(self.bullets)
        }


######################準心系統######################
class CrosshairSystem:
    """
    準心系統 - 武器瞄準用的準心顯示\n
    \n
    當玩家裝備槍械時顯示準心，準心會跟隨滑鼠移動\n
    提供視覺化的瞄準輔助\n
    """

    def __init__(self):
        """
        初始化準心系統\n
        """
        # 準心樣式設定
        self.crosshair_size = 20  # 準心大小
        self.crosshair_color = (255, 0, 0)  # 紅色準心
        self.crosshair_thickness = 2  # 準心線條粗細
        
        # 準心位置
        self.position = (0, 0)
        
        # 是否顯示準心
        self.visible = False
        
        print("準心系統初始化完成")

    def update(self, mouse_pos):
        """
        更新準心位置\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠位置 (x, y)\n
        """
        self.position = mouse_pos

    def show(self):
        """
        顯示準心\n
        """
        self.visible = True

    def hide(self):
        """
        隱藏準心\n
        """
        self.visible = False


######################射擊音效系統######################
class ShootingSoundManager:
    """
    射擊音效管理器 - 處理各種武器的射擊音效\n
    \n
    管理不同武器類型的音效播放\n
    提供音效的載入、播放和音量控制\n
    """

    def __init__(self):
        """
        初始化射擊音效管理器\n
        """
        # 初始化 pygame 音效系統
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            except pygame.error as e:
                print(f"音效系統初始化失敗: {e}")
                self.sound_enabled = False
                return

        self.sound_enabled = True
        self.sounds = {}
        
        # 載入射擊音效
        self._load_sounds()
        
        print("射擊音效管理器初始化完成")

    def _load_sounds(self):
        """
        載入射擊音效文件\n
        """
        # 射擊音效文件路徑
        sound_files = {
            "bb_gun": "assets/sounds/bb_gun_shot.wav",  # BB槍音效
            "pistol": "assets/sounds/pistol_shot.wav",   # 手槍音效
            "rifle": "assets/sounds/rifle_shot.wav",     # 步槍音效
            "shotgun": "assets/sounds/shotgun_shot.wav", # 霰彈槍音效
        }

        for weapon_type, file_path in sound_files.items():
            try:
                # 嘗試載入音效檔案
                if weapon_type == "bb_gun":
                    # BB槍使用實際音效文件（雖然是空文件，但會觸發創建模擬音效）
                    try:
                        sound = pygame.mixer.Sound(file_path)
                        sound.set_volume(0.7)  # BB槍音量較大
                        self.sounds[weapon_type] = sound
                        print(f"載入BB槍音效成功: {weapon_type}")
                    except:
                        # 如果載入失敗，創建模擬音效
                        self.sounds[weapon_type] = self._create_mock_sound(weapon_type)
                        print(f"創建BB槍模擬音效: {weapon_type}")
                else:
                    # 其他武器直接創建模擬音效
                    self.sounds[weapon_type] = self._create_mock_sound(weapon_type)
                    print(f"創建模擬音效: {weapon_type}")
            except Exception as e:
                # 如果所有嘗試都失敗，創建模擬音效
                self.sounds[weapon_type] = self._create_mock_sound(weapon_type)
                print(f"音效載入失敗，使用模擬音效 {weapon_type}: {e}")

    def _create_mock_sound(self, weapon_type):
        """
        創建模擬音效（當檔案不存在時）\n
        \n
        參數:\n
        weapon_type (str): 武器類型\n
        \n
        回傳:\n
        pygame.mixer.Sound: 模擬音效物件\n
        """
        try:
            # 創建簡單的模擬音效
            duration = 0.1  # 音效持續時間（秒）
            sample_rate = 22050
            
            # 根據武器類型設定不同的頻率
            if weapon_type == "bb_gun":
                frequency = 1200  # BB槍較高頻率，短促的"噗噗"聲
            elif weapon_type == "pistol":
                frequency = 400  # 中等頻率
            elif weapon_type == "rifle":
                frequency = 200  # 較低頻率
            elif weapon_type == "shotgun":
                frequency = 150  # 最低頻率
            else:
                frequency = 300  # 預設頻率

            # 創建音效陣列（縮短BB槍音效持續時間）
            if weapon_type == "bb_gun":
                duration = 0.05  # BB槍音效更短促
            else:
                duration = 0.1  # 其他武器音效持續時間
            
            frames = int(duration * sample_rate)
            arr = []
            
            for i in range(frames):
                # 創建衰減的正弦波
                time_ratio = i / frames
                amplitude = int(4096 * (1 - time_ratio))  # 音量衰減
                wave = amplitude * math.sin(frequency * 2 * math.pi * i / sample_rate)
                arr.append([int(wave), int(wave)])  # 立體聲

            # 轉換為 pygame Sound 物件
            try:
                import numpy as np
                sound_array = np.array(arr, dtype=np.int16)
                sound = pygame.sndarray.make_sound(sound_array)
                sound.set_volume(0.5 if weapon_type == "bb_gun" else 0.3)
                return sound
            except ImportError:
                # 如果沒有numpy，創建簡單的空音效
                print("NumPy 未安裝，創建空音效")
                return pygame.mixer.Sound(buffer=bytes(1024))
            except Exception as e:
                print(f"創建音效陣列失敗: {e}")
                return pygame.mixer.Sound(buffer=bytes(1024))
            
        except Exception as e:
            print(f"創建模擬音效失敗: {e}")
            # 返回空音效物件
            return pygame.mixer.Sound(buffer=bytes(100))

    def play_shot_sound(self, weapon_type):
        """
        播放射擊音效\n
        \n
        參數:\n
        weapon_type (str): 武器類型\n
        """
        if not self.sound_enabled:
            return

        if weapon_type in self.sounds:
            try:
                self.sounds[weapon_type].play()
            except pygame.error as e:
                print(f"播放音效失敗: {e}")
        else:
            print(f"找不到武器音效: {weapon_type}")

    def set_volume(self, volume):
        """
        設定音效音量\n
        \n
        參數:\n
        volume (float): 音量大小 (0.0 到 1.0)\n
        """
        volume = max(0.0, min(1.0, volume))  # 限制音量範圍
        
        for sound in self.sounds.values():
            sound.set_volume(volume)


######################BB槍武器類別######################
class BBGun:
    """
    BB槍 - 玩家預設武器（全自動版本）\n
    \n
    特性：\n
    - 傷害：20\n
    - 射速：全自動，每秒20發\n
    - 彈藥：100發（無限子彈）\n
    - 換彈時間：1秒\n
    - 射擊模式：全自動\n
    """

    def __init__(self):
        """
        初始化BB槍（全自動版本）\n
        """
        self.name = "全自動BB槍"
        self.weapon_type = "bb_gun"
        
        # 武器屬性 - 每秒10發設定
        self.damage = 20
        self.range = 250
        self.accuracy = 0.85
        self.fire_rate = 10.0  # 每秒10發子彈
        self.magazine_size = 100
        self.reload_time = 1.0  # 1秒換彈時間
        self.ammo_type = "BB彈"
        self.is_automatic = True  # 標記為全自動武器
        
        # 武器狀態
        self.current_ammo = self.magazine_size
        self.total_ammo = -1  # -1 表示無限彈藥
        self.last_shot_time = 0
        self.is_reloading = False
        self.reload_start_time = 0
        
        print(f"創建武器: {self.name}（每秒10發全自動模式）")

    def can_shoot(self):
        """
        檢查是否可以射擊\n
        \n
        回傳:\n
        bool: 是否可以射擊\n
        """
        current_time = time.time()

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
        dict: 射擊結果\n
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

        # 消耗彈藥
        self.current_ammo -= 1
        self.last_shot_time = time.time()

        # 計算命中率
        distance_factor = max(0.3, 1.0 - (distance / self.range) * 0.4)
        hit_chance = self.accuracy * distance_factor

        # 判斷是否命中
        import random
        hit = random.random() <= hit_chance

        # 計算傷害
        damage = 0
        if hit:
            damage_reduction = min(0.3, distance / self.range * 0.2)
            damage = int(self.damage * (1.0 - damage_reduction))

        return {"success": True, "hit": hit, "damage": damage, "distance": distance}

    def start_reload(self):
        """
        開始重新裝彈\n
        \n
        回傳:\n
        bool: 是否開始重新裝彈\n
        """
        if self.is_reloading:
            return False

        if self.current_ammo >= self.magazine_size:
            return False  # 不需要重新裝彈

        # BB槍有無限彈藥，所以總是可以重新裝彈
        self.is_reloading = True
        self.reload_start_time = time.time()
        print(f"{self.name} 開始重新裝彈...")
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
            # 重新裝彈完成 - BB槍有無限彈藥
            self.current_ammo = self.magazine_size
            self.is_reloading = False
            print(f"{self.name} 重新裝彈完成! 彈匣: {self.current_ammo}/{self.magazine_size}")
            return True

        return False

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
            "total": "∞" if self.total_ammo == -1 else self.total_ammo
        }