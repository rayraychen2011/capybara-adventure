######################載入套件######################
import pygame
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


######################路燈系統######################
class StreetLightSystem:
    """
    路燈系統 - 夜晚時路燈點亮並照亮周圍區域\n
    \n
    功能說明:\n
    1. 根據地形系統自動在道路上放置路燈\n
    2. 夜晚時路燈會點亮\n
    3. 路燈會照亮周圍區域\n
    4. 與時間系統整合，根據時間控制開關\n
    """

    def __init__(self, time_manager=None, terrain_system=None):
        """
        初始化路燈系統\n
        \n
        參數:\n
        time_manager (TimeManager): 時間管理器\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        """
        self.time_manager = time_manager
        self.terrain_system = terrain_system
        
        # 路燈列表
        self.street_lights = []
        
        # 路燈設定
        self.light_radius = 60  # 路燈照亮範圍
        self.light_spacing = 80  # 路燈間距
        self.light_color = (255, 255, 200, 100)  # 暖黃色光線
        self.light_pole_color = (100, 100, 100)  # 路燈桿顏色
        
        # 夜晚判定時間（小時）
        self.night_start_hour = 18  # 晚上6點開始
        self.night_end_hour = 6     # 早上6點結束
        
        print("路燈系統初始化完成")

    def initialize_street_lights(self):
        """
        初始化路燈位置 - 在道路和高速公路上放置路燈\n
        """
        if not self.terrain_system:
            print("警告：沒有地形系統，無法放置路燈")
            return
            
        self.street_lights.clear()
        light_id = 1
        
        # 遍歷地圖，在道路和高速公路地形上放置路燈
        for y in range(0, self.terrain_system.map_height, 2):  # 每2格放一個路燈
            for x in range(0, self.terrain_system.map_width, 2):
                terrain_code = self.terrain_system.map_data[y][x]
                
                # 檢查是否為道路或高速公路
                if terrain_code in [3, 4]:  # 3=道路, 4=高速公路
                    # 計算世界座標
                    world_x = x * self.terrain_system.tile_size + self.terrain_system.tile_size // 2
                    world_y = y * self.terrain_system.tile_size + self.terrain_system.tile_size // 2
                    
                    # 創建路燈
                    street_light = {
                        "id": light_id,
                        "position": (world_x, world_y),
                        "is_on": False,  # 初始狀態為關閉
                        "terrain_type": "highway" if terrain_code == 4 else "road",
                    }
                    
                    self.street_lights.append(street_light)
                    light_id += 1
        
        print(f"已放置 {len(self.street_lights)} 盞路燈")

    def update(self, dt):
        """
        更新路燈系統\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 根據時間決定路燈開關狀態
        is_night = self._is_night_time()
        
        # 更新所有路燈狀態
        for light in self.street_lights:
            light["is_on"] = is_night

    def _is_night_time(self):
        """
        判斷當前是否為夜晚\n
        \n
        回傳:\n
        bool: True表示夜晚，False表示白天\n
        """
        if not self.time_manager:
            return False
            
        current_hour = self.time_manager.hour
        
        # 夜晚時間：18:00-06:00
        if self.night_start_hour > self.night_end_hour:  # 跨越午夜
            return current_hour >= self.night_start_hour or current_hour < self.night_end_hour
        else:
            return self.night_start_hour <= current_hour < self.night_end_hour

    def draw(self, screen, camera_offset=(0, 0)):
        """
        繪製路燈系統\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_offset (tuple): 攝影機偏移\n
        """
        camera_x, camera_y = camera_offset
        
        for light in self.street_lights:
            light_x, light_y = light["position"]
            
            # 計算螢幕位置
            screen_x = light_x - camera_x
            screen_y = light_y - camera_y
            
            # 只繪製在螢幕範圍內的路燈
            if -100 <= screen_x <= SCREEN_WIDTH + 100 and -100 <= screen_y <= SCREEN_HEIGHT + 100:
                # 繪製路燈桿
                self._draw_light_pole(screen, (screen_x, screen_y))
                
                # 如果是夜晚且路燈開啟，繪製光圈
                if light["is_on"]:
                    self._draw_light_circle(screen, (screen_x, screen_y))

    def _draw_light_pole(self, screen, position):
        """
        繪製路燈桿\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        position (tuple): 路燈桿位置\n
        """
        x, y = position
        
        # 繪製路燈桿（垂直線）
        pygame.draw.line(screen, self.light_pole_color, (x, y), (x, y - 15), 3)
        
        # 繪製路燈頭（小圓圈）
        pygame.draw.circle(screen, self.light_pole_color, (x, y - 15), 4)

    def _draw_light_circle(self, screen, position):
        """
        繪製路燈光圈\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        position (tuple): 路燈位置\n
        """
        x, y = position
        
        # 創建透明表面用於光圈效果
        light_surface = pygame.Surface((self.light_radius * 2, self.light_radius * 2), pygame.SRCALPHA)
        
        # 繪製漸層光圈效果
        for radius in range(self.light_radius, 0, -5):
            alpha = int(50 * (radius / self.light_radius))  # 漸層透明度
            color = (*self.light_color[:3], alpha)
            
            pygame.draw.circle(light_surface, color, 
                             (self.light_radius, self.light_radius), radius)
        
        # 將光圈表面貼到主螢幕上
        screen.blit(light_surface, (x - self.light_radius, y - self.light_radius))

    def is_position_lit(self, position):
        """
        檢查指定位置是否被路燈照亮\n
        \n
        參數:\n
        position (tuple): 位置座標 (x, y)\n
        \n
        回傳:\n
        bool: True表示被照亮，False表示在黑暗中\n
        """
        if not self._is_night_time():
            return True  # 白天時所有地方都是亮的
            
        px, py = position
        
        # 檢查是否在任何路燈的照亮範圍內
        for light in self.street_lights:
            if light["is_on"]:
                lx, ly = light["position"]
                distance = math.sqrt((px - lx) ** 2 + (py - ly) ** 2)
                
                if distance <= self.light_radius:
                    return True
        
        return False

    def get_nearby_lights(self, position, max_distance):
        """
        獲取指定位置附近的路燈\n
        \n
        參數:\n
        position (tuple): 中心位置\n
        max_distance (float): 最大距離\n
        \n
        回傳:\n
        list: 附近的路燈列表\n
        """
        nearby_lights = []
        px, py = position
        
        for light in self.street_lights:
            lx, ly = light["position"]
            distance = math.sqrt((px - lx) ** 2 + (py - ly) ** 2)
            
            if distance <= max_distance:
                nearby_lights.append(light)
        
        return nearby_lights

    def get_light_statistics(self):
        """
        獲取路燈系統統計資料\n
        \n
        回傳:\n
        dict: 統計資料\n
        """
        total_lights = len(self.street_lights)
        lights_on = sum(1 for light in self.street_lights if light["is_on"])
        
        terrain_counts = {}
        for light in self.street_lights:
            terrain_type = light["terrain_type"]
            terrain_counts[terrain_type] = terrain_counts.get(terrain_type, 0) + 1
        
        return {
            "total_lights": total_lights,
            "lights_on": lights_on,
            "lights_off": total_lights - lights_on,
            "is_night": self._is_night_time(),
            "terrain_distribution": terrain_counts,
        }

    def debug_print_info(self):
        """
        除錯用：印出路燈系統資訊\n
        """
        stats = self.get_light_statistics()
        print("\n=== 路燈系統狀態 ===")
        print(f"總路燈數量: {stats['total_lights']}")
        print(f"開啟數量: {stats['lights_on']}")
        print(f"關閉數量: {stats['lights_off']}")
        print(f"當前是否夜晚: {stats['is_night']}")
        print(f"地形分布: {stats['terrain_distribution']}")
        print("=====================\n")