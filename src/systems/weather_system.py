######################載入套件######################
import pygame
import random
import math
import time
from config.settings import *


######################粒子類別######################
class WeatherParticle:
    """
    天氣粒子基礎類別 - 雨滴、雪花等特效粒子的基底\n
    \n
    此類別定義了天氣特效粒子的基本行為：\n
    1. 位置和速度管理\n
    2. 生命週期控制\n
    3. 基本物理運動\n
    4. 螢幕邊界處理\n
    """

    def __init__(self, x, y, velocity_x, velocity_y, color, size=1):
        """
        初始化天氣粒子\n
        \n
        參數:\n
        x (float): 初始X位置\n
        y (float): 初始Y位置\n
        velocity_x (float): X方向速度（像素/秒）\n
        velocity_y (float): Y方向速度（像素/秒）\n
        color (tuple): RGB顏色值\n
        size (int): 粒子大小（像素）\n
        """
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.size = size
        self.alive = True

    def update(self, dt, wind_x=0):
        """
        更新粒子狀態\n
        \n
        參數:\n
        dt (float): 時間間隔（秒）\n
        wind_x (float): 風力影響（水平方向）\n
        """
        if not self.alive:
            return

        # 根據速度更新位置，加上風力影響
        self.x += (self.velocity_x + wind_x) * dt
        self.y += self.velocity_y * dt

        # 檢查是否超出螢幕範圍
        if (self.y > SCREEN_HEIGHT + 50 or 
            self.x < -50 or 
            self.x > SCREEN_WIDTH + 50):
            self.alive = False

    def draw(self, screen, camera_x, camera_y):
        """
        繪製粒子\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        if not self.alive:
            return

        # 計算螢幕座標（不受攝影機影響，因為天氣是全域效果）
        screen_x = int(self.x)
        screen_y = int(self.y)

        # 確保粒子在螢幕範圍內才繪製
        if (0 <= screen_x < SCREEN_WIDTH and 
            0 <= screen_y < SCREEN_HEIGHT):
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)


######################雨滴粒子######################
class RainDrop(WeatherParticle):
    """
    雨滴粒子 - 模擬雨水效果\n
    \n
    雨滴特性：\n
    - 垂直快速下降\n
    - 受風力影響水平移動\n
    - 線條形狀模擬雨滴軌跡\n
    """

    def __init__(self, x, y, intensity=1.0):
        """
        初始化雨滴\n
        \n
        參數:\n
        x (float): 初始X位置\n
        y (float): 初始Y位置\n
        intensity (float): 雨勢強度（0.5-2.0）\n
        """
        # 雨滴速度受強度影響
        velocity_y = RAIN_PARTICLE_SPEED * intensity
        velocity_x = random.uniform(-50, 50) * intensity  # 輕微的水平偏移
        
        super().__init__(x, y, velocity_x, velocity_y, RAIN_PARTICLE_COLOR, 1)
        self.intensity = intensity
        self.length = max(3, int(5 * intensity))  # 雨滴線條長度

    def draw(self, screen, camera_x, camera_y):
        """
        繪製雨滴（線條形狀）\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        if not self.alive:
            return

        screen_x = int(self.x)
        screen_y = int(self.y)

        # 確保雨滴在螢幕範圍內
        if (0 <= screen_x < SCREEN_WIDTH and 
            0 <= screen_y < SCREEN_HEIGHT):
            # 繪製雨滴線條（從當前位置到下方一點）
            end_x = screen_x + int(self.velocity_x * 0.01)  # 根據水平速度計算傾斜
            end_y = screen_y + self.length
            
            try:
                pygame.draw.line(screen, self.color, 
                               (screen_x, screen_y), 
                               (end_x, end_y), 1)
            except ValueError:
                # 如果座標超出範圍，用圓點代替
                pygame.draw.circle(screen, self.color, (screen_x, screen_y), 1)


######################雪花粒子######################
class SnowFlake(WeatherParticle):
    """
    雪花粒子 - 模擬下雪效果\n
    \n
    雪花特性：\n
    - 緩慢飄落\n
    - 左右搖擺運動\n
    - 受風力影響較大\n
    - 圓形或多角形外觀\n
    """

    def __init__(self, x, y):
        """
        初始化雪花\n
        \n
        參數:\n
        x (float): 初始X位置\n
        y (float): 初始Y位置\n
        """
        velocity_y = random.uniform(50, SNOW_PARTICLE_SPEED)  # 隨機下降速度
        velocity_x = random.uniform(-20, 20)  # 隨機水平漂移
        size = random.randint(1, 3)  # 隨機雪花大小
        
        super().__init__(x, y, velocity_x, velocity_y, SNOW_PARTICLE_COLOR, size)
        
        # 雪花搖擺參數
        self.sway_amplitude = random.uniform(10, 30)  # 搖擺幅度
        self.sway_frequency = random.uniform(1, 3)  # 搖擺頻率
        self.sway_phase = random.uniform(0, 2 * math.pi)  # 搖擺相位
        self.start_time = time.time()

    def update(self, dt, wind_x=0):
        """
        更新雪花狀態（包含搖擺運動）\n
        \n
        參數:\n
        dt (float): 時間間隔（秒）\n
        wind_x (float): 風力影響（水平方向）\n
        """
        if not self.alive:
            return

        # 計算搖擺運動
        current_time = time.time() - self.start_time
        sway_offset = self.sway_amplitude * math.sin(
            self.sway_frequency * current_time + self.sway_phase
        )

        # 更新位置（基本移動 + 搖擺 + 風力）
        self.x += (self.velocity_x + sway_offset * dt + wind_x * 0.5) * dt
        self.y += self.velocity_y * dt

        # 檢查邊界
        if (self.y > SCREEN_HEIGHT + 50 or 
            self.x < -50 or 
            self.x > SCREEN_WIDTH + 50):
            self.alive = False


######################閃電效果######################
class LightningFlash:
    """
    閃電效果系統 - 模擬雷暴天氣的閃電\n
    \n
    閃電特性：\n
    - 隨機時間間隔出現\n
    - 短暫的全螢幕亮白效果\n
    - 可配合音效系統\n
    - 影響環境光線\n
    """

    def __init__(self):
        """
        初始化閃電系統\n
        """
        self.is_active = False  # 是否正在閃電
        self.flash_start_time = 0  # 閃電開始時間
        self.next_lightning_time = 0  # 下次閃電時間
        self.flash_alpha = 0  # 閃電亮度（0-255）
        
        # 設定下一次閃電時間
        self._schedule_next_lightning()

    def _schedule_next_lightning(self):
        """
        安排下一次閃電時間\n
        """
        interval = random.uniform(LIGHTNING_INTERVAL_MIN, LIGHTNING_INTERVAL_MAX)
        self.next_lightning_time = time.time() + interval

    def update(self, dt):
        """
        更新閃電狀態\n
        \n
        參數:\n
        dt (float): 時間間隔（秒）\n
        """
        current_time = time.time()

        # 檢查是否該觸發新的閃電
        if not self.is_active and current_time >= self.next_lightning_time:
            self.trigger_lightning()

        # 更新正在進行的閃電
        if self.is_active:
            elapsed = current_time - self.flash_start_time
            
            if elapsed < LIGHTNING_DURATION:
                # 閃電進行中，計算亮度變化（先亮後暗）
                progress = elapsed / LIGHTNING_DURATION
                if progress < 0.3:
                    # 快速變亮
                    self.flash_alpha = int(255 * LIGHTNING_BRIGHTNESS * (progress / 0.3))
                else:
                    # 慢慢變暗
                    fade_progress = (progress - 0.3) / 0.7
                    self.flash_alpha = int(255 * LIGHTNING_BRIGHTNESS * (1.0 - fade_progress))
            else:
                # 閃電結束
                self.is_active = False
                self.flash_alpha = 0
                self._schedule_next_lightning()

    def trigger_lightning(self):
        """
        手動觸發閃電（用於測試或特殊事件）\n
        """
        self.is_active = True
        self.flash_start_time = time.time()
        print("⚡ 閃電！")

    def get_light_modifier(self):
        """
        獲取閃電的光線加成\n
        \n
        回傳:\n
        float: 光線加成值（0.0-1.0）\n
        """
        if self.is_active:
            return self.flash_alpha / 255.0 * LIGHTNING_BRIGHTNESS
        return 0.0

    def draw(self, screen):
        """
        繪製閃電效果\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        """
        if self.is_active and self.flash_alpha > 0:
            # 創建閃電覆蓋層
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.set_alpha(self.flash_alpha)
            flash_surface.fill((255, 255, 255))  # 白色閃光
            screen.blit(flash_surface, (0, 0))


######################天氣效果管理器######################
class WeatherEffectSystem:
    """
    天氣效果系統 - 統一管理所有天氣特效\n
    \n
    此系統負責：\n
    1. 管理不同類型的天氣粒子（雨、雪等）\n
    2. 控制特殊效果（閃電、霧等）\n
    3. 調整環境參數（光線、顏色、能見度）\n
    4. 與手機UI的天氣系統同步\n
    """

    def __init__(self, phone_ui=None):
        """
        初始化天氣效果系統\n
        \n
        參數:\n
        phone_ui (PhoneUI): 手機UI引用，用於同步天氣狀態\n
        """
        self.phone_ui = phone_ui
        self.current_weather = "☀️ 晴朗"  # 當前天氣
        
        # 粒子系統
        self.particles = []  # 當前活躍的天氣粒子
        self.max_particles = 0  # 最大粒子數量
        
        # 特殊效果
        self.lightning = LightningFlash()
        self.wind_strength = 0.0  # 風力強度
        self.fog_alpha = 0  # 霧的透明度
        
        # 環境修正值
        self.light_modifier = 1.0  # 光線修正
        self.sky_color_modifier = (1.0, 1.0, 1.0)  # 天空顏色修正
        self.visibility = 1.0  # 能見度
        
        print("天氣效果系統初始化完成")

    def set_weather(self, weather_type):
        """
        設定天氣類型\n
        \n
        參數:\n
        weather_type (str): 天氣類型，必須是 WEATHER_TYPES 中的鍵值\n
        """
        if weather_type not in WEATHER_TYPES:
            print(f"未知的天氣類型: {weather_type}")
            return

        self.current_weather = weather_type
        weather_config = WEATHER_TYPES[weather_type]
        
        # 更新環境參數
        self.sky_color_modifier = weather_config["sky_color_modifier"]
        self.light_modifier = weather_config["light_modifier"]
        self.visibility = weather_config["visibility"]
        
        # 清除現有粒子
        self.particles.clear()
        
        # 設定新的粒子系統
        particle_type = weather_config.get("particles")
        if particle_type == "light_rain":
            self.max_particles = RAIN_PARTICLE_COUNT // 2
        elif particle_type == "heavy_rain":
            self.max_particles = RAIN_PARTICLE_COUNT
        elif particle_type == "snow":
            self.max_particles = SNOW_PARTICLE_COUNT
        else:
            self.max_particles = 0

        # 設定風力
        if particle_type in ["light_rain", "heavy_rain"]:
            self.wind_strength = random.uniform(-30, 30)
        elif particle_type == "snow":
            self.wind_strength = random.uniform(-50, 50)
        else:
            self.wind_strength = 0

        # 設定霧效
        if weather_type in ["☁️ 陰天", "🌧️ 小雨", "⛈️ 雷雨"]:
            self.fog_alpha = FOG_ALPHA // 2
        elif weather_type == "🌨️ 下雪":
            self.fog_alpha = FOG_ALPHA
        else:
            self.fog_alpha = 0

        print(f"天氣變更為: {weather_type}")
        
        # 同步手機UI（如果有的話）
        if self.phone_ui:
            self.phone_ui.current_weather = weather_type

    def get_current_weather(self):
        """
        獲取當前天氣\n
        \n
        回傳:\n
        str: 當前天氣類型\n
        """
        return self.current_weather

    def update(self, dt):
        """
        更新天氣系統\n
        \n
        參數:\n
        dt (float): 時間間隔（秒）\n
        """
        # 同步手機UI的天氣狀態
        if self.phone_ui and self.phone_ui.current_weather != self.current_weather:
            self.set_weather(self.phone_ui.current_weather)

        # 更新特殊效果
        if self.current_weather == "⛈️ 雷雨":
            self.lightning.update(dt)

        # 更新現有粒子
        for particle in self.particles[:]:  # 使用切片複製來避免迭代時修改列表
            particle.update(dt, self.wind_strength)
            if not particle.alive:
                self.particles.remove(particle)

        # 生成新粒子（如果需要）
        self._spawn_particles()

    def _spawn_particles(self):
        """
        生成新的天氣粒子\n
        """
        if len(self.particles) >= self.max_particles:
            return

        particles_to_spawn = min(5, self.max_particles - len(self.particles))
        
        for _ in range(particles_to_spawn):
            # 在螢幕上方隨機位置生成粒子
            x = random.uniform(-50, SCREEN_WIDTH + 50)
            y = random.uniform(-100, -50)
            
            # 根據天氣類型創建不同粒子
            if self.current_weather in ["🌧️ 小雨"]:
                particle = RainDrop(x, y, intensity=0.7)
            elif self.current_weather in ["⛈️ 雷雨"]:
                particle = RainDrop(x, y, intensity=1.5)
            elif self.current_weather == "🌨️ 下雪":
                particle = SnowFlake(x, y)
            else:
                continue
            
            self.particles.append(particle)

    def get_modified_sky_color(self, original_color):
        """
        獲取天氣修正後的天空顏色\n
        \n
        參數:\n
        original_color (tuple): 原始天空顏色 RGB\n
        \n
        回傳:\n
        tuple: 修正後的天空顏色 RGB\n
        """
        r, g, b = original_color
        mod_r, mod_g, mod_b = self.sky_color_modifier
        
        # 應用顏色修正
        new_r = int(r * mod_r)
        new_g = int(g * mod_g)
        new_b = int(b * mod_b)
        
        # 確保顏色值在有效範圍內
        return (
            max(0, min(255, new_r)),
            max(0, min(255, new_g)),
            max(0, min(255, new_b))
        )

    def get_modified_ambient_light(self, original_light):
        """
        獲取天氣修正後的環境光\n
        \n
        參數:\n
        original_light (float): 原始環境光強度\n
        \n
        回傳:\n
        float: 修正後的環境光強度\n
        """
        # 基礎天氣修正
        modified_light = original_light * self.light_modifier
        
        # 添加閃電加成
        if self.current_weather == "⛈️ 雷雨":
            lightning_bonus = self.lightning.get_light_modifier()
            modified_light = min(1.0, modified_light + lightning_bonus)
        
        return max(0.1, min(1.0, modified_light))

    def draw(self, screen, camera_x, camera_y):
        """
        繪製所有天氣效果\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        # 繪製粒子效果
        for particle in self.particles:
            particle.draw(screen, camera_x, camera_y)

        # 繪製霧效
        if self.fog_alpha > 0:
            fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fog_surface.set_alpha(self.fog_alpha)
            fog_surface.fill(FOG_COLOR)
            screen.blit(fog_surface, (0, 0))

        # 繪製閃電效果
        if self.current_weather == "⛈️ 雷雨":
            self.lightning.draw(screen)

    def get_debug_info(self):
        """
        獲取除錯資訊\n
        \n
        回傳:\n
        dict: 包含天氣系統狀態的字典\n
        """
        return {
            "current_weather": self.current_weather,
            "particles_count": len(self.particles),
            "max_particles": self.max_particles,
            "light_modifier": f"{self.light_modifier:.2f}",
            "visibility": f"{self.visibility:.2f}",
            "wind_strength": f"{self.wind_strength:.1f}",
            "fog_alpha": self.fog_alpha,
            "lightning_active": self.lightning.is_active if self.current_weather == "⛈️ 雷雨" else False,
        }