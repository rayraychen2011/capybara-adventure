import pygame
import os
from enum import Enum
from config.settings import *
from src.utils.font_manager import FontManager


class ShopType(Enum):
    """商店類型枚舉"""
    CONVENIENCE_STORE = "便利商店"
    GUN_STORE = "槍械店" 
    CLOTHING_STORE = "服裝店"
    HOSPITAL = "醫院"
    BOOKSTORE = "書店"


class ShopItem:
    """商品類別"""
    def __init__(self, item_id, name, price, category, effect=None, effect_value=0, description="", image_path=None):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.category = category
        self.effect = effect
        self.effect_value = effect_value
        self.description = description
        self.image_path = image_path
        self.image = None
        self.load_image()
    
    def load_image(self):
        """載入商品圖片"""
        if self.image_path and os.path.exists(self.image_path):
            try:
                self.image = pygame.image.load(self.image_path).convert_alpha()
                # 調整圖片大小以適應商品格子
                self.image = pygame.transform.scale(self.image, (50, 50))
                print(f"✅ 成功載入圖片: {self.image_path}")
            except pygame.error as e:
                print(f"❌ 載入圖片失敗 {self.image_path}: {e}")
                self.image = None
        else:
            if self.image_path:
                print(f"⚠️ 圖片檔案不存在: {self.image_path}")
            self.image = None


class ShopData:
    """商店資料庫"""
    
    # 圖片基礎路徑
    IMAGES_PATH = "assets/images/things/"
    
    @staticmethod
    def get_gun_store_items():
        return [
            ShopItem("ak47", "AK47", 5000, "weapon", "weapon", 0, "高穩定,中射程,低射速,高傷害,40發子彈", ShopData.IMAGES_PATH + "AK47.png"),
            ShopItem("gatling", "加特靈", 4000, "weapon", "weapon", 0, "低穩定,中射程,高射速,低傷害,200發子彈", ShopData.IMAGES_PATH + "加特靈.png"),
            ShopItem("spas12", "SPAS12", 3000, "weapon", "weapon", 0, "低穩定,低射程,高射速,高傷害,12發散彈(一發散成10個彈片)", ShopData.IMAGES_PATH + "SPAS12.png")
        ]
    
    @staticmethod
    def get_convenience_store_items():
        return [
            ShopItem("cola", "可樂", 50, "health_restore", "health_restore", 50, "生命回復50", ShopData.IMAGES_PATH + "可樂.png"),
            ShopItem("fries", "薯條", 60, "health_restore", "health_restore", 60, "生命回復60", ShopData.IMAGES_PATH + "薯條.png"),
            ShopItem("hotdog", "熱狗", 70, "health_restore", "health_restore", 70, "生命回復70", ShopData.IMAGES_PATH + "熱狗.png"),
            ShopItem("burger", "漢堡", 80, "health_restore", "health_restore", 80, "生命回復80", ShopData.IMAGES_PATH + "漢堡.png")
        ]
    
    @staticmethod
    def get_clothing_store_items():
        return [
            # 原服裝防禦商品
            ShopItem("banana_suit", "香蕉裝", 100, "defense", "defense", 5, "防禦+5", ShopData.IMAGES_PATH + "香蕉裝.png"),
            ShopItem("headphones", "耳機", 200, "defense", "defense", 10, "防禦+10", ShopData.IMAGES_PATH + "耳機.png"),
            ShopItem("hat", "帽帽", 300, "defense", "defense", 15, "防禦+15", ShopData.IMAGES_PATH + "帽帽.png"),
            ShopItem("hoodie", "帽衣", 400, "defense", "defense", 20, "防禦+20", ShopData.IMAGES_PATH + "帽衣.png"),
            ShopItem("clothes", "衣服", 500, "defense", "defense", 25, "防禦+25", ShopData.IMAGES_PATH + "衣服.png"),
            # 原漫畫主題商城血量回復商品（使用現有圖片替代）
            ShopItem("homer", "HOMER", 800, "health_regen", "health_regen", 4, "每秒血量回復+4", ShopData.IMAGES_PATH + "急救箱.png"),
            ShopItem("mushroom", "香菇", 600, "health_regen", "health_regen", 3, "每秒血量回復+3", ShopData.IMAGES_PATH + "止痛藥.png"),
            ShopItem("labubu", "LABUBU", 400, "health_regen", "health_regen", 2, "每秒血量回復+2", ShopData.IMAGES_PATH + "繃帶.png"),
            ShopItem("clown", "CLOWN", 200, "health_regen", "health_regen", 1, "每秒血量回復+1", ShopData.IMAGES_PATH + "可樂.png")
        ]
    
    @staticmethod
    def get_hospital_items():
        return [
            ShopItem("bandage", "繃帶", 100, "health_restore", "health_restore", 100, "生命回復100", ShopData.IMAGES_PATH + "繃帶.png"),
            ShopItem("first_aid", "急救包", 200, "health_restore", "health_restore", 200, "生命回復200", ShopData.IMAGES_PATH + "急救箱.png"),
            ShopItem("painkiller", "止痛藥", 300, "health_restore", "health_restore", 300, "生命回復300", ShopData.IMAGES_PATH + "止痛藥.png")
        ]
    
    @staticmethod
    def get_bookstore_items():
        return [
            ShopItem("cookbook", "食譜書", 150, "knowledge", "skill", 1, "學習烹飪技能", "assets/images/things/漢堡.png"),
            ShopItem("combat_manual", "戰鬥手冊", 250, "knowledge", "skill", 1, "學習戰鬥技能", "assets/images/things/AK47.png"),
            ShopItem("survival_guide", "生存指南", 200, "knowledge", "skill", 1, "學習生存技能", "assets/images/things/急救箱.png"),
            ShopItem("encyclopedia", "百科全書", 500, "knowledge", "skill", 1, "學習所有技能", "assets/images/things/HOMER.png")
        ]


class Shop:
    """商店類別"""
    def __init__(self, shop_type, name, items):
        self.shop_type = shop_type
        self.name = name
        self.items = items
        self.is_open = False


class ShopManager:
    """商店管理器"""
    
    def __init__(self):
        self.shops = {
            ShopType.CONVENIENCE_STORE: Shop(ShopType.CONVENIENCE_STORE, "便利商店", ShopData.get_convenience_store_items()),
            ShopType.GUN_STORE: Shop(ShopType.GUN_STORE, "槍械店", ShopData.get_gun_store_items()),
            ShopType.CLOTHING_STORE: Shop(ShopType.CLOTHING_STORE, "服裝店", ShopData.get_clothing_store_items()),
            ShopType.HOSPITAL: Shop(ShopType.HOSPITAL, "醫院", ShopData.get_hospital_items()),
            ShopType.BOOKSTORE: Shop(ShopType.BOOKSTORE, "書店", ShopData.get_bookstore_items())
        }
        self.current_shop_type = None
        self.font_manager = FontManager()
        
    def open_shop(self, shop_type):
        if shop_type in self.shops:
            self.current_shop_type = shop_type
            print(f"🛍️ 歡迎光臨{shop_type.value}！")
            print(f"DEBUG: 商店已開啟，類型={shop_type}, is_shop_open={self.is_shop_open()}")
        else:
            print(f"DEBUG: 商店類型 {shop_type} 不存在於 shops 中")
    
    def close_shop(self):
        if self.current_shop_type:
            print(f"👋 謝謝您光臨{self.current_shop_type.value}！")
            self.current_shop_type = None
    
    def is_shop_open(self):
        return self.current_shop_type is not None
    
    def handle_mouse_click(self, mouse_pos, player):
        if not self.is_shop_open():
            return False
            
        current_shop = self.shops[self.current_shop_type]
        
        # 計算商品網格位置 - 調整為2x2的4格佈局
        start_x, start_y = 450, 220
        item_width, item_height = 120, 120  # 加大商品格子
        grid_cols = 2  # 改為每行2格
        spacing = 30  # 格子間距
        
        # 只顯示前4個商品
        items_to_show = current_shop.items[:4]
        
        for i, item in enumerate(items_to_show):
            col = i % grid_cols
            row = i // grid_cols
            
            item_x = start_x + col * (item_width + spacing)
            item_y = start_y + row * (item_height + spacing)
            
            # 檢查點擊是否在商品區域內
            if (item_x <= mouse_pos[0] <= item_x + item_width and 
                item_y <= mouse_pos[1] <= item_y + item_height):
                
                # 嘗試購買商品
                if player.money >= item.price:
                    player.money -= item.price
                    self._apply_item_effect(item, player)
                    print(f"✅ 購買了 {item.name}，花費 ${item.price}")
                    return True
                else:
                    print(f"❌ 金錢不足！需要 ${item.price}，您只有 ${player.money}")
                    return True
        
        return False
    
    def handle_key_input(self, event):
        if not self.is_shop_open():
            return False
            
        if event.key == pygame.K_ESCAPE:
            self.close_shop()
            return True
            
        return False
    
    def _apply_item_effect(self, item, player):
        if item.effect == "health_restore":
            player.health = min(player.max_health, player.health + item.effect_value)
            print(f"💊 血量回復 {item.effect_value}，當前血量：{player.health}")
            
        elif item.effect == "health_regen":
            if not hasattr(player, 'health_regen_rate'):
                player.health_regen_rate = 0
            player.health_regen_rate += item.effect_value
            print(f"💚 每秒血量回復 +{item.effect_value}，總回復率：{player.health_regen_rate}")
            
        elif item.effect == "defense":
            player.defense += item.effect_value
            print(f"🛡️ 防禦力 +{item.effect_value}，當前防禦：{player.defense}")
            
        elif item.effect == "weapon":
            print(f"🔫 獲得武器：{item.name}")
    
    def update_player_effects(self, player):
        if hasattr(player, 'health_regen_rate') and player.health_regen_rate > 0:
            old_health = player.health
            player.health = min(player.max_health, player.health + player.health_regen_rate / 60)
    
    def draw(self, screen, player):
        if not self.is_shop_open():
            return
            
        current_shop = self.shops[self.current_shop_type]
        
        # 繪製商店背景
        shop_bg = pygame.Rect(400, 150, 400, 400)  # 增加高度適應新佈局
        pygame.draw.rect(screen, (245, 245, 220), shop_bg)  # 改為米白色
        pygame.draw.rect(screen, (139, 69, 19), shop_bg, 3)  # 棕色邊框
        
        # 繪製商店標題
        title_font = self.font_manager.get_font(24)
        title_text = title_font.render(f"{current_shop.name}", True, (139, 69, 19))  # 棕色標題
        title_rect = title_text.get_rect(center=(600, 170))
        screen.blit(title_text, title_rect)
        
        # 繪製玩家金錢
        money_font = self.font_manager.get_font(18)
        money_text = money_font.render(f"金錢: ${player.money}", True, (255, 215, 0))  # 金色
        screen.blit(money_text, (420, 190))
        
        # 繪製商品網格 - 2x2的4格佈局
        start_x, start_y = 450, 220
        item_width, item_height = 120, 120  # 加大商品格子
        grid_cols = 2  # 改為每行2格
        spacing = 30  # 格子間距
        
        # 只顯示前4個商品
        items_to_show = current_shop.items[:4]
        
        for i, item in enumerate(items_to_show):
            col = i % grid_cols
            row = i // grid_cols
            
            item_x = start_x + col * (item_width + spacing)
            item_y = start_y + row * (item_height + spacing)
            
            # 繪製商品格子背景
            item_rect = pygame.Rect(item_x, item_y, item_width, item_height)
            if player.money >= item.price:
                pygame.draw.rect(screen, (255, 255, 255), item_rect)  # 白色表示可購買
            else:
                pygame.draw.rect(screen, (200, 200, 200), item_rect)  # 灰色表示買不起
            pygame.draw.rect(screen, (139, 69, 19), item_rect, 3)  # 棕色邊框
            
            # 繪製商品圖片（如果有載入成功）
            if item.image:
                # 計算圖片居中位置
                image_rect = item.image.get_rect()
                image_x = item_x + (item_width - image_rect.width) // 2
                image_y = item_y + 10  # 距離上邊距10像素
                screen.blit(item.image, (image_x, image_y))
            else:
                # 如果圖片載入失敗，顯示預設圖示
                no_image_font = self.font_manager.get_font(36)
                no_image_text = no_image_font.render("?", True, (100, 100, 100))
                text_rect = no_image_text.get_rect()
                text_x = item_x + (item_width - text_rect.width) // 2
                text_y = item_y + 30
                screen.blit(no_image_text, (text_x, text_y))
            
            # 繪製商品名稱
            name_font = self.font_manager.get_font(12)
            name_text = name_font.render(item.name, True, (0, 0, 0))
            name_rect = name_text.get_rect()
            
            # 如果文字太長，縮放顯示
            if name_rect.width > item_width - 10:
                scale_ratio = (item_width - 10) / name_rect.width
                scaled_width = int(name_rect.width * scale_ratio)
                scaled_height = int(name_rect.height * scale_ratio)
                name_text = pygame.transform.scale(name_text, (scaled_width, scaled_height))
                name_rect = name_text.get_rect()
            
            name_x = item_x + (item_width - name_rect.width) // 2
            name_y = item_y + item_height - 40
            screen.blit(name_text, (name_x, name_y))
            
            # 繪製商品價格
            price_font = self.font_manager.get_font(14)
            price_text = price_font.render(f"${item.price}", True, (255, 0, 0))  # 紅色價格
            price_rect = price_text.get_rect()
            price_x = item_x + (item_width - price_rect.width) // 2
            price_y = item_y + item_height - 20
            screen.blit(price_text, (price_x, price_y))
        
        # 繪製說明文字
        help_font = self.font_manager.get_font(14)
        help_text = help_font.render("點擊商品購買，按 ESC 關閉", True, (100, 100, 100))
        screen.blit(help_text, (420, 510))
