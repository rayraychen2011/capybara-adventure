######################載入套件######################
import pygame
import random
import time
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.utils.font_manager import FontManager


######################蔬果園採集系統######################
class VegetableGardenSystem:
    """
    蔬果園採集系統 - 在公園區域放置蔬果園，玩家可採摘獲得金錢\nㄍ
    \n
    功能說明:\n
    1. 根據地形系統在公園區域自動放置蔬果園\n
    2. 玩家可採摘蔬果獲得 5 元\n
    3. 蔬果會定期重新生長\n
    4. 顯示蔬果的成熟狀態\n
    """

    def __init__(self, terrain_system=None):
        """
        初始化蔬果園採集系統\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        """
        self.terrain_system = terrain_system
        
        # 字體管理器
        self.font_manager = FontManager()
        
        # 蔬果園列表
        self.vegetable_gardens = []
        
        # 採集設定
        self.harvest_reward = 5  # 採摘獎勵金額
        self.regrow_time = 24   # 重新生長時間（現實秒數，對應遊戲內一天）
        self.interaction_range = 25  # 互動範圍（自動採收檢測範圍）
        
        # 蔬果類型和顏色
        self.vegetable_types = [
            {"name": "番茄", "color": (255, 0, 0)},
            {"name": "胡蘿蔔", "color": (255, 165, 0)},
            {"name": "高麗菜", "color": (0, 255, 0)},
            {"name": "茄子", "color": (128, 0, 128)},
            {"name": "玉米", "color": (255, 255, 0)},
        ]
        
        # 統計資料
        self.total_harvested = 0
        self.total_money_earned = 0
        
        print("蔬果園採集系統初始化完成")

    def initialize_gardens(self):
        """
        初始化蔬果園位置 - 從地形系統取得已創建的蔬果園\n
        """
        if not self.terrain_system:
            print("警告：沒有地形系統，無法放置蔬果園")
            return
            
        self.vegetable_gardens.clear()
        
        # 使用地形系統中已創建的蔬果園
        if hasattr(self.terrain_system, 'vegetable_gardens'):
            for i, garden_data in enumerate(self.terrain_system.vegetable_gardens):
                # 轉換為蔬果園系統需要的格式
                garden = {
                    "id": i + 1,
                    "position": garden_data['position'],
                    "vegetable_type": random.choice(self.vegetable_types),
                    "is_ready": garden_data.get('harvest_ready', True),  # 使用地形系統的狀態
                    "last_harvest_time": 0,  # 上次採摘時間
                    "size": garden_data.get('size', 10),  # 使用地形系統的大小
                    "terrain_garden": garden_data  # 保存對原始數據的引用
                }
                
                self.vegetable_gardens.append(garden)
        
        print(f"從地形系統載入 {len(self.vegetable_gardens)} 個蔬果園")

    def update(self, dt):
        """
        更新蔬果園系統\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        current_time = time.time()
        
        # 檢查蔬果重新生長
        for garden in self.vegetable_gardens:
            if not garden["is_ready"]:
                # 檢查是否到了重新生長時間
                if current_time - garden["last_harvest_time"] >= self.regrow_time:
                    garden["is_ready"] = True
                    print(f"蔬果園 {garden['id']} 的{garden['vegetable_type']['name']}重新生長完成")

    def check_auto_harvest(self, player_position, player):
        """
        檢查玩家位置是否有成熟蔬果可自動採收\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 採收結果，如果沒有可採收的蔬果則返回 None\n
        """
        # 尋找互動範圍內的蔬果園
        nearby_gardens = self.get_nearby_gardens(player_position, self.interaction_range)
        
        # 篩選出可採摘的蔬果園
        harvestable_gardens = [garden for garden in nearby_gardens if garden["is_ready"]]
        
        if not harvestable_gardens:
            return None
        
        # 選擇最近的蔬果園進行自動採收
        target_garden = min(
            harvestable_gardens,
            key=lambda g: self._calculate_distance(player_position, g["position"])
        )
        
        # 執行自動採摘
        return self._harvest_garden(target_garden, player)

    def attempt_harvest(self, player_position, player):
        """
        嘗試採摘蔬果\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 採摘結果\n
        """
        # 尋找互動範圍內的蔬果園
        nearby_gardens = self.get_nearby_gardens(player_position, self.interaction_range)
        
        # 篩選出可採摘的蔬果園
        harvestable_gardens = [garden for garden in nearby_gardens if garden["is_ready"]]
        
        if not harvestable_gardens:
            return {
                "success": False,
                "message": "附近沒有可採摘的蔬果",
                "money_earned": 0,
            }
        
        # 選擇最近的蔬果園
        target_garden = min(
            harvestable_gardens,
            key=lambda g: self._calculate_distance(player_position, g["position"])
        )
        
        # 執行採摘
        return self._harvest_garden(target_garden, player)

    def _harvest_garden(self, garden, player):
        """
        採摘指定蔬果園\n
        \n
        參數:\n
        garden (dict): 蔬果園物件\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 採摘結果\n
        """
        vegetable_name = garden["vegetable_type"]["name"]
        
        # 標記為已採摘
        garden["is_ready"] = False
        garden["last_harvest_time"] = time.time()
        
        # 同步更新地形系統中的蔬果園狀態
        if "terrain_garden" in garden:
            garden["terrain_garden"]["harvest_ready"] = False
            garden["terrain_garden"]["last_harvest_time"] = time.time()
        
        # 給玩家金錢獎勵
        if hasattr(player, 'money'):
            player.money += self.harvest_reward
        
        # 更新統計資料
        self.total_harvested += 1
        self.total_money_earned += self.harvest_reward
        
        print(f"🌱 自動採摘 {vegetable_name} 獲得 {self.harvest_reward} 元")
        
        return {
            "success": True,
            "message": f"採摘了 {vegetable_name}，獲得 {self.harvest_reward} 元",
            "money_earned": self.harvest_reward,
            "vegetable": vegetable_name,
        }

    def get_nearby_gardens(self, position, max_distance):
        """
        獲取指定位置附近的蔬果園\n
        \n
        參數:\n
        position (tuple): 中心位置\n
        max_distance (float): 最大距離\n
        \n
        回傳:\n
        list: 附近的蔬果園列表\n
        """
        nearby_gardens = []
        px, py = position
        
        for garden in self.vegetable_gardens:
            gx, gy = garden["position"]
            distance = self._calculate_distance((px, py), (gx, gy))
            
            if distance <= max_distance:
                nearby_gardens.append(garden)
        
        return nearby_gardens

    def _calculate_distance(self, pos1, pos2):
        """
        計算兩點間的距離\n
        \n
        參數:\n
        pos1 (tuple): 第一個點\n
        pos2 (tuple): 第二個點\n
        \n
        回傳:\n
        float: 距離\n
        """
        x1, y1 = pos1
        x2, y2 = pos2
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def draw(self, screen, camera_offset=(0, 0)):
        """
        繪製蔬果園\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_offset (tuple): 攝影機偏移\n
        """
        camera_x, camera_y = camera_offset
        
        for garden in self.vegetable_gardens:
            gx, gy = garden["position"]
            
            # 計算螢幕位置
            screen_x = gx - camera_x
            screen_y = gy - camera_y
            
            # 只繪製在螢幕範圍內的蔬果園
            if -50 <= screen_x <= SCREEN_WIDTH + 50 and -50 <= screen_y <= SCREEN_HEIGHT + 50:
                self._draw_garden(screen, garden, (screen_x, screen_y))

    def _draw_garden(self, screen, garden, position):
        """
        繪製單個蔬果園\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        garden (dict): 蔬果園物件\n
        position (tuple): 螢幕位置\n
        """
        x, y = position
        # 將農作物圓形半徑縮小為 4，不再使用garden["size"]
        crop_radius = 4
        vegetable_type = garden["vegetable_type"]
        is_ready = garden["is_ready"]
        
        if is_ready:
            # 可採摘狀態：使用蔬果的原始顏色
            color = vegetable_type["color"]
            # 繪製蔬果（圓形，縮小半徑）
            pygame.draw.circle(screen, color, (int(x), int(y)), crop_radius)
            # 繪製邊框
            pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), crop_radius, 2)
        else:
            # 未成熟狀態：使用灰色表示
            color = (100, 100, 100)
            pygame.draw.circle(screen, color, (int(x), int(y)), crop_radius - 2)
            pygame.draw.circle(screen, (50, 50, 50), (int(x), int(y)), crop_radius - 2, 1)

    def draw_interaction_hint(self, screen, player_position, camera_offset=(0, 0)):
        """
        繪製自動採收提示（現在只顯示視覺標記，不需要按鍵提示）\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        player_position (tuple): 玩家位置\n
        camera_offset (tuple): 攝影機偏移\n
        """
        # 尋找附近可採摘的蔬果園
        nearby_gardens = self.get_nearby_gardens(player_position, self.interaction_range)
        harvestable_gardens = [garden for garden in nearby_gardens if garden["is_ready"]]
        
        if harvestable_gardens:
            camera_x, camera_y = camera_offset
            
            for garden in harvestable_gardens:
                gx, gy = garden["position"]
                screen_x = gx - camera_x
                screen_y = gy - camera_y
                
                # 繪製自動採收範圍提示圓圈（縮小尺寸）
                pygame.draw.circle(screen, (50, 255, 50), (int(screen_x), int(screen_y)), 
                                 10, 2)  # 固定半徑為 10
                
                # 顯示自動採收提示（可選）
                font = self.font_manager.get_font(16)
                hint_text = font.render("🌱 自動採收", True, (50, 255, 50))
                hint_rect = hint_text.get_rect(center=(int(screen_x), int(screen_y) - 25))
                screen.blit(hint_text, hint_rect)

    def get_statistics(self):
        """
        獲取蔬果園系統統計資料\n
        \n
        回傳:\n
        dict: 統計資料\n
        """
        total_gardens = len(self.vegetable_gardens)
        ready_gardens = sum(1 for garden in self.vegetable_gardens if garden["is_ready"])
        
        vegetable_counts = {}
        for garden in self.vegetable_gardens:
            veg_name = garden["vegetable_type"]["name"]
            vegetable_counts[veg_name] = vegetable_counts.get(veg_name, 0) + 1
        
        return {
            "total_gardens": total_gardens,
            "ready_gardens": ready_gardens,
            "growing_gardens": total_gardens - ready_gardens,
            "total_harvested": self.total_harvested,
            "total_money_earned": self.total_money_earned,
            "vegetable_distribution": vegetable_counts,
        }

    def debug_print_info(self):
        """
        除錯用：印出蔬果園系統資訊\n
        """
        stats = self.get_statistics()
        print("\n=== 蔬果園系統狀態 ===")
        print(f"總蔬果園數量: {stats['total_gardens']}")
        print(f"可採摘數量: {stats['ready_gardens']}")
        print(f"生長中數量: {stats['growing_gardens']}")
        print(f"總採摘次數: {stats['total_harvested']}")
        print(f"總賺取金額: {stats['total_money_earned']} 元")
        print(f"蔬果種類分布: {stats['vegetable_distribution']}")
        print("========================\n")