######################載入套件######################
import pygame
import random
from config.settings import *


######################魚餌店系統######################
class BaitShop:
    """
    魚餌店類別 - 處理魚餌販售\n
    \n
    位於湖邊的專門店鋪，販售不同等級的魚餌\n
    提供魚餌購買和魚餌資訊查詢功能\n
    """

    def __init__(self, x, y, shop_id):
        """
        初始化魚餌店\n
        \n
        參數:\n
        x (float): 店鋪 X 座標\n
        y (float): 店鋪 Y 座標\n
        shop_id (int): 店鋪唯一識別碼\n
        """
        self.x = x
        self.y = y
        self.width = 60  # 店鋪寬度
        self.height = 40  # 店鋪高度
        self.shop_id = shop_id
        
        # 店鋪狀態
        self.is_open = True
        self.shop_name = f"魚餌店 #{shop_id}"
        
        # 商品庫存
        self.inventory = {
            "普通魚餌": {"price": 100, "stock": -1, "description": "基礎魚餌，提供標準釣魚效果"},
            "高級魚餌": {"price": 500, "stock": 50, "description": "高品質魚餌，提升釣魚成功率50%"},
            "頂級魚餌": {"price": 1000, "stock": 20, "description": "頂級魚餌，釣魚效果翻倍"}
        }
        
        # 店鋪外觀
        self.color = (139, 69, 19)  # 棕色建築
        self.door_color = (160, 82, 45)  # 淺棕色門
        
        # 互動相關
        self.interaction_range = 50  # 互動距離
        self.is_player_nearby = False
        
        print(f"🏪 {self.shop_name} 已建立在 ({x}, {y})")

    def update(self, dt, player_position):
        """
        更新店鋪狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        """
        # 檢查玩家是否在附近
        distance = self._calculate_distance(player_position, (self.x + self.width/2, self.y + self.height/2))
        self.is_player_nearby = distance <= self.interaction_range

    def _calculate_distance(self, pos1, pos2):
        """
        計算兩點間距離\n
        \n
        參數:\n
        pos1 (tuple): 第一個點的座標\n
        pos2 (tuple): 第二個點的座標\n
        \n
        回傳:\n
        float: 距離\n
        """
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

    def can_interact(self, player_position):
        """
        檢查是否可以互動\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        \n
        回傳:\n
        bool: 是否可以互動\n
        """
        if not self.is_open:
            return False
        
        distance = self._calculate_distance(player_position, (self.x + self.width/2, self.y + self.height/2))
        return distance <= self.interaction_range

    def buy_bait(self, player, bait_name, quantity=1):
        """
        購買魚餌\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        bait_name (str): 魚餌名稱\n
        quantity (int): 購買數量\n
        \n
        回傳:\n
        dict: 購買結果\n
        """
        if bait_name not in self.inventory:
            return {"success": False, "message": f"沒有販售 {bait_name}"}
        
        item_info = self.inventory[bait_name]
        total_cost = item_info["price"] * quantity
        
        # 檢查庫存
        if item_info["stock"] != -1 and item_info["stock"] < quantity:
            return {"success": False, "message": f"{bait_name} 庫存不足（剩餘 {item_info['stock']}）"}
        
        # 檢查玩家金錢
        if not player.spend_money(total_cost):
            return {"success": False, "message": f"金錢不足，需要 ${total_cost}"}
        
        # 執行購買
        player.add_bait(bait_name, quantity)
        
        # 更新庫存（普通魚餌庫存為-1，表示無限）
        if item_info["stock"] != -1:
            self.inventory[bait_name]["stock"] -= quantity
        
        return {
            "success": True, 
            "message": f"成功購買 {bait_name} x{quantity}，花費 ${total_cost}"
        }

    def get_shop_info(self):
        """
        獲取店鋪資訊\n
        \n
        回傳:\n
        dict: 店鋪詳細資訊\n
        """
        return {
            "name": self.shop_name,
            "location": (self.x, self.y),
            "is_open": self.is_open,
            "inventory": self.inventory.copy()
        }

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製魚餌店\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標\n
        camera_x (int): 攝影機 X 偏移\n
        camera_y (int): 攝影機 Y 偏移\n
        """
        # 計算螢幕座標
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # 繪製主建築
        building_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, self.color, building_rect)
        
        # 繪製門
        door_width = 16
        door_height = 20
        door_x = screen_x + (self.width - door_width) // 2
        door_y = screen_y + self.height - door_height
        door_rect = pygame.Rect(door_x, door_y, door_width, door_height)
        pygame.draw.rect(screen, self.door_color, door_rect)
        
        # 繪製邊框
        pygame.draw.rect(screen, (0, 0, 0), building_rect, 2)
        
        # 繪製店鋪標誌（簡單的魚圖標）
        fish_center_x = screen_x + self.width // 2
        fish_center_y = screen_y + 15
        pygame.draw.ellipse(screen, (0, 191, 255), 
                          (fish_center_x - 8, fish_center_y - 4, 16, 8))
        
        # 如果玩家在附近，顯示互動提示
        if self.is_player_nearby:
            font = pygame.font.Font(None, 24)
            text = font.render("按 E 進入魚餌店", True, (255, 255, 0))
            text_rect = text.get_rect(center=(screen_x + self.width//2, screen_y - 20))
            screen.blit(text, text_rect)


######################魚餌店管理器######################
class BaitShopManager:
    """
    魚餌店管理器 - 管理所有魚餌店\n
    \n
    負責在湖邊區域創建和管理多個魚餌店\n
    處理店鋪間的互動和狀態同步\n
    """

    def __init__(self, terrain_system):
        """
        初始化魚餌店管理器\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        """
        self.terrain_system = terrain_system
        self.shops = []
        self.next_shop_id = 1
        
        # 在湖邊創建魚餌店
        self._create_lakeside_shops()
        
        print(f"🏪 魚餌店管理器已初始化，共創建 {len(self.shops)} 間店鋪")

    def _create_lakeside_shops(self):
        """
        在湖邊創建魚餌店\n
        """
        # 尋找湖邊位置並放置店鋪
        shop_positions = self._find_lakeside_positions()
        
        for position in shop_positions:
            shop = BaitShop(position[0], position[1], self.next_shop_id)
            self.shops.append(shop)
            self.next_shop_id += 1

    def _find_lakeside_positions(self):
        """
        尋找適合放置魚餌店的湖邊位置\n
        \n
        回傳:\n
        list: 位置列表\n
        """
        positions = []
        
        # 簡化實作：在地圖上尋找水域邊緣的陸地位置
        # 這裡使用固定位置作為示例，實際應該基於地形數據
        if hasattr(self.terrain_system, 'map_width') and hasattr(self.terrain_system, 'map_height'):
            map_width = self.terrain_system.map_width * self.terrain_system.tile_size
            map_height = self.terrain_system.map_height * self.terrain_system.tile_size
            
            # 在地圖的不同區域放置魚餌店
            shop_locations = [
                (map_width * 0.2, map_height * 0.3),
                (map_width * 0.7, map_height * 0.4),
                (map_width * 0.5, map_height * 0.8),
                (map_width * 0.8, map_height * 0.6),
                (map_width * 0.3, map_height * 0.7)
            ]
            
            for location in shop_locations:
                positions.append(location)
        
        return positions

    def update(self, dt, player_position):
        """
        更新所有魚餌店\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        """
        for shop in self.shops:
            shop.update(dt, player_position)

    def get_nearby_shop(self, player_position):
        """
        獲取玩家附近的魚餌店\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        \n
        回傳:\n
        BaitShop: 最近的可互動店鋪，如果沒有則回傳 None\n
        """
        for shop in self.shops:
            if shop.can_interact(player_position):
                return shop
        return None

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製所有魚餌店\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標\n
        camera_x (int): 攝影機 X 偏移\n
        camera_y (int): 攝影機 Y 偏移\n
        """
        for shop in self.shops:
            # 只繪製在視野範圍內的店鋪
            screen_x = shop.x - camera_x
            screen_y = shop.y - camera_y
            
            if (-shop.width <= screen_x <= SCREEN_WIDTH and 
                -shop.height <= screen_y <= SCREEN_HEIGHT):
                shop.draw(screen, camera_x, camera_y)

    def get_all_shops_info(self):
        """
        獲取所有店鋪資訊\n
        \n
        回傳:\n
        list: 所有店鋪的資訊列表\n
        """
        return [shop.get_shop_info() for shop in self.shops]