######################載入套件######################
import pygame
from src.systems.shop_system import BaseShop
from config.settings import *
from src.utils.font_manager import FontManager


######################便利商店######################
class ConvenienceStore(BaseShop):
    """
    便利商店 - 販售日常用品和補給品\n
    \n
    提供基本的生活用品和健康補給\n
    按右鍵可以打開商店介面\n
    """

    def __init__(self, x, y):
        """
        初始化便利商店\n
        \n
        參數:\n
        x (int): 商店X座標\n
        y (int): 商店Y座標\n
        """
        super().__init__(x, y, "便利商店", "convenience_store")

    def _setup_inventory(self):
        """
        設定便利商店庫存\n
        """
        self.inventory = {
            "energy_drink": {
                "name": "能量飲料",
                "price": 50,
                "description": "恢復50點生命值",
                "stock": 20,
                "effect": "health",
                "effect_value": 50
            },
            "health_potion": {
                "name": "治療藥水",
                "price": 100,
                "description": "恢復100點生命值",
                "stock": 15,
                "effect": "health",
                "effect_value": 100
            },
            "bandage": {
                "name": "繃帶",
                "price": 25,
                "description": "恢復25點生命值",
                "stock": 30,
                "effect": "health",
                "effect_value": 25
            },
            "snack": {
                "name": "零食",
                "price": 20,
                "description": "恢復10點生命值",
                "stock": 50,
                "effect": "health",
                "effect_value": 10
            },
            "water_bottle": {
                "name": "礦泉水",
                "price": 15,
                "description": "恢復5點生命值",
                "stock": 40,
                "effect": "health",
                "effect_value": 5
            }
        }

    def _apply_item_effect(self, item_id, player):
        """
        應用便利商店商品效果\n
        \n
        參數:\n
        item_id (str): 商品ID\n
        player (Player): 玩家物件\n
        """
        item = self.inventory[item_id]
        
        if item.get('effect') == 'health':
            # 恢復生命值
            heal_amount = item['effect_value']
            old_health = player.health
            player.health = min(player.max_health, player.health + heal_amount)
            actual_heal = player.health - old_health
            
            print(f"使用 {item['name']}，恢復了 {actual_heal} 點生命值")


######################路邊小販######################
class StreetVendor(BaseShop):
    """
    路邊小販 - 販售特色商品\n
    \n
    提供與便利商店不同的特色商品\n
    通常價格較便宜但品質較低\n
    """

    def __init__(self, x, y, vendor_id=1):
        """
        初始化路邊小販\n
        \n
        參數:\n
        x (int): 小販X座標\n
        y (int): 小販Y座標\n
        vendor_id (int): 小販編號（用於區分不同小販）\n
        """
        self.vendor_id = vendor_id
        super().__init__(x, y, f"路邊小販#{vendor_id}", "street_vendor")
        
        # 字體管理器
        self.font_manager = FontManager()
        
        # 小販外觀設定
        self.width = 40
        self.height = 30
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def _setup_inventory(self):
        """
        設定路邊小販庫存\n
        """
        # 根據小販ID提供不同商品
        if self.vendor_id == 1:
            # 食物小販
            self.inventory = {
                "street_food": {
                    "name": "街頭小食",
                    "price": 30,
                    "description": "便宜的街頭美食，恢復30點生命值",
                    "stock": 25,
                    "effect": "health",
                    "effect_value": 30
                },
                "fruit_juice": {
                    "name": "現榨果汁",
                    "price": 35,
                    "description": "新鮮果汁，恢復35點生命值",
                    "stock": 20,
                    "effect": "health",
                    "effect_value": 35
                },
                "local_snack": {
                    "name": "在地零嘴",
                    "price": 18,
                    "description": "當地特色零食，恢復15點生命值",
                    "stock": 40,
                    "effect": "health",
                    "effect_value": 15
                }
            }
        elif self.vendor_id == 2:
            # 工具小販
            self.inventory = {
                "cheap_bandage": {
                    "name": "便宜繃帶",
                    "price": 15,
                    "description": "品質一般的繃帶，恢復15點生命值",
                    "stock": 30,
                    "effect": "health",
                    "effect_value": 15
                },
                "herb_tea": {
                    "name": "草藥茶",
                    "price": 40,
                    "description": "傳統草藥茶，恢復40點生命值",
                    "stock": 15,
                    "effect": "health",
                    "effect_value": 40
                },
                "energy_bar": {
                    "name": "能量棒",
                    "price": 28,
                    "description": "補充體力的能量棒，恢復25點生命值",
                    "stock": 35,
                    "effect": "health",
                    "effect_value": 25
                }
            }
        else:
            # 預設商品
            self.inventory = {
                "mystery_item": {
                    "name": "神秘商品",
                    "price": 50,
                    "description": "不知道效果的神秘商品",
                    "stock": 10,
                    "effect": "health",
                    "effect_value": 20
                }
            }

    def _apply_item_effect(self, item_id, player):
        """
        應用路邊小販商品效果\n
        \n
        參數:\n
        item_id (str): 商品ID\n
        player (Player): 玩家物件\n
        """
        item = self.inventory[item_id]
        
        if item.get('effect') == 'health':
            # 恢復生命值
            heal_amount = item['effect_value']
            old_health = player.health
            player.health = min(player.max_health, player.health + heal_amount)
            actual_heal = player.health - old_health
            
            print(f"使用 {item['name']}，恢復了 {actual_heal} 點生命值")

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製路邊小販\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (int): 攝影機X偏移\n
        camera_y (int): 攝影機Y偏移\n
        """
        # 計算螢幕座標
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # 檢查是否在螢幕範圍內
        if (screen_x + self.width < 0 or screen_x > SCREEN_WIDTH or
            screen_y + self.height < 0 or screen_y > SCREEN_HEIGHT):
            return
        
        # 繪製小販攤位（較小的建築）
        vendor_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, (160, 82, 45), vendor_rect)  # 淺棕色
        pygame.draw.rect(screen, (139, 69, 19), vendor_rect, 2)  # 深棕色邊框
        
        # 繪製遮陽篷
        canopy_rect = pygame.Rect(screen_x - 5, screen_y - 5, self.width + 10, 8)
        pygame.draw.rect(screen, (255, 69, 0), canopy_rect)  # 橘紅色遮陽篷
        
        # 繪製小販名稱
        font = self.font_manager.get_font(14)
        name_text = font.render(self.shop_name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(screen_x + self.width//2, screen_y - 15))
        screen.blit(name_text, name_rect)
        
        # 如果玩家在附近，顯示互動提示
        if self.is_player_nearby:
            hint_text = font.render("按右鍵購買", True, (255, 255, 0))
            hint_rect = hint_text.get_rect(center=(screen_x + self.width//2, screen_y + self.height + 12))
            screen.blit(hint_text, hint_rect)


######################槍械店######################
class GunShop(BaseShop):
    """
    槍械店 - 販售各種武器和彈藥\n
    \n
    提供多種武器選擇，每把槍有不同優點和數值\n
    按右鍵可以打開商店介面\n
    """

    def __init__(self, x, y):
        """
        初始化槍械店\n
        \n
        參數:\n
        x (int): 商店X座標\n
        y (int): 商店Y座標\n
        """
        super().__init__(x, y, "槍械店", "gun_shop")

    def _setup_inventory(self):
        """
        設定槍械店庫存\n
        """
        self.inventory = {
            "bb_gun": {
                "name": "BB槍",
                "price": 200,
                "description": "初學者武器，傷害20，高射速",
                "stock": 10,
                "effect": "weapon",
                "weapon_type": "bb_gun"
            },
            "pistol": {
                "name": "手槍",
                "price": 500,
                "description": "平衡的武器，傷害25，中等射速",
                "stock": 8,
                "effect": "weapon",
                "weapon_type": "pistol"
            },
            "rifle": {
                "name": "步槍",
                "price": 1500,
                "description": "高傷害武器，傷害50，低射速",
                "stock": 5,
                "effect": "weapon",
                "weapon_type": "rifle"
            },
            "shotgun": {
                "name": "霰彈槍",
                "price": 800,
                "description": "近距離強力武器，傷害80",
                "stock": 6,
                "effect": "weapon",
                "weapon_type": "shotgun"
            },
            "sniper_rifle": {
                "name": "狙擊槍",
                "price": 3000,
                "description": "遠距離精密武器，傷害100",
                "stock": 3,
                "effect": "weapon",
                "weapon_type": "sniper"
            },
            "ammo_9mm": {
                "name": "9mm彈藥",
                "price": 50,
                "description": "手槍彈藥，50發",
                "stock": 20,
                "effect": "ammo",
                "ammo_type": "9mm",
                "amount": 50
            },
            "ammo_762mm": {
                "name": "7.62mm彈藥",
                "price": 80,
                "description": "步槍彈藥，30發",
                "stock": 15,
                "effect": "ammo",
                "ammo_type": "7.62mm",
                "amount": 30
            }
        }

    def _apply_item_effect(self, item_id, player):
        """
        應用槍械店商品效果\n
        \n
        參數:\n
        item_id (str): 商品ID\n
        player (Player): 玩家物件\n
        """
        item = self.inventory[item_id]
        
        if item.get('effect') == 'weapon':
            # 給玩家武器
            weapon_type = item['weapon_type']
            print(f"獲得武器: {item['name']}")
            
            # 這裡需要與武器系統整合
            # 暫時只是輸出訊息
            
        elif item.get('effect') == 'ammo':
            # 給玩家彈藥
            ammo_type = item['ammo_type']
            amount = item['amount']
            print(f"獲得彈藥: {item['name']} x{amount}")
            
            # 這裡需要與武器系統整合
            # 暫時只是輸出訊息


######################服裝店######################
class ClothingStore(BaseShop):
    """
    服裝店 - 販售各種服裝\n
    \n
    提供5種不同的服裝選擇\n
    購買服裝會改變玩家外觀\n
    """

    def __init__(self, x, y):
        """
        初始化服裝店\n
        \n
        參數:\n
        x (int): 商店X座標\n
        y (int): 商店Y座標\n
        """
        super().__init__(x, y, "服裝店", "clothing_store")

    def _setup_inventory(self):
        """
        設定服裝店庫存\n
        """
        self.inventory = {
            "casual_outfit": {
                "name": "休閒服裝",
                "price": 150,
                "description": "舒適的日常穿著",
                "stock": 5,
                "effect": "outfit",
                "outfit_id": 1,
                "color": (100, 150, 200)  # 淺藍色
            },
            "formal_outfit": {
                "name": "正式服裝",
                "price": 300,
                "description": "適合正式場合的服裝",
                "stock": 5,
                "effect": "outfit",
                "outfit_id": 2,
                "color": (50, 50, 50)  # 深灰色
            },
            "sporty_outfit": {
                "name": "運動服裝",
                "price": 200,
                "description": "適合運動的輕便服裝",
                "stock": 5,
                "effect": "outfit",
                "outfit_id": 3,
                "color": (255, 100, 100)  # 淺紅色
            },
            "elegant_outfit": {
                "name": "優雅服裝",
                "price": 500,
                "description": "高雅精緻的服裝",
                "stock": 3,
                "effect": "outfit",
                "outfit_id": 4,
                "color": (128, 0, 128)  # 紫色
            },
            "adventure_outfit": {
                "name": "冒險服裝",
                "price": 400,
                "description": "適合戶外冒險的耐用服裝",
                "stock": 4,
                "effect": "outfit",
                "outfit_id": 5,
                "color": (139, 69, 19)  # 棕色
            }
        }

    def _apply_item_effect(self, item_id, player):
        """
        應用服裝店商品效果\n
        \n
        參數:\n
        item_id (str): 商品ID\n
        player (Player): 玩家物件\n
        """
        item = self.inventory[item_id]
        
        if item.get('effect') == 'outfit':
            # 改變玩家服裝
            outfit_id = item['outfit_id']
            outfit_color = item['color']
            
            # 更新玩家外觀
            player.current_outfit = outfit_id
            player.color = outfit_color
            
            # 添加到玩家擁有的服裝列表
            if outfit_id not in player.owned_outfits:
                player.owned_outfits.append(outfit_id)
            
            print(f"換上 {item['name']}！外觀已更新")


######################商店管理器######################
class ShopManager:
    """
    商店管理器 - 統一管理所有類型的商店\n
    \n
    負責：\n
    - 創建和管理各種商店\n
    - 處理商店互動\n
    - 更新商店狀態\n
    """

    def __init__(self):
        """
        初始化商店管理器\n
        """
        self.shops = []
        self.convenience_stores = []
        self.street_vendors = []
        self.gun_shops = []
        self.clothing_stores = []
        
        print("商店管理器初始化完成")

    def add_convenience_store(self, x, y):
        """
        添加便利商店\n
        \n
        參數:\n
        x (int): X座標\n
        y (int): Y座標\n
        """
        store = ConvenienceStore(x, y)
        self.shops.append(store)
        self.convenience_stores.append(store)
        return store

    def add_street_vendor(self, x, y, vendor_id=1):
        """
        添加路邊小販\n
        \n
        參數:\n
        x (int): X座標\n
        y (int): Y座標\n
        vendor_id (int): 小販編號\n
        """
        vendor = StreetVendor(x, y, vendor_id)
        self.shops.append(vendor)
        self.street_vendors.append(vendor)
        return vendor

    def add_gun_shop(self, x, y):
        """
        添加槍械店\n
        \n
        參數:\n
        x (int): X座標\n
        y (int): Y座標\n
        """
        shop = GunShop(x, y)
        self.shops.append(shop)
        self.gun_shops.append(shop)
        return shop

    def add_clothing_store(self, x, y):
        """
        添加服裝店\n
        \n
        參數:\n
        x (int): X座標\n
        y (int): Y座標\n
        """
        store = ClothingStore(x, y)
        self.shops.append(store)
        self.clothing_stores.append(store)
        return store

    def update(self, dt, player_position):
        """
        更新所有商店\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        """
        for shop in self.shops:
            shop.is_near_player(player_position)

    def get_nearby_shop(self, player_position):
        """
        獲取玩家附近的商店\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        \n
        回傳:\n
        BaseShop: 附近的商店，如果沒有則返回None\n
        """
        for shop in self.shops:
            if shop.is_near_player(player_position):
                return shop
        return None

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製所有商店\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (int): 攝影機X偏移\n
        camera_y (int): 攝影機Y偏移\n
        """
        for shop in self.shops:
            shop.draw(screen, camera_x, camera_y)