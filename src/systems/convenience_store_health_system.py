######################載入套件######################
import pygame
from config.settings import *


######################便利商店血量藥水系統######################
class ConvenienceStoreHealthSystem:
    """
    便利商店血量藥水系統 - 擴展便利商店功能\n
    \n
    為現有的便利商店添加血量藥水販售功能\n
    提供三種不同等級的血量藥水\n
    """

    def __init__(self):
        """
        初始化便利商店血量藥水系統\n
        """
        # 血量藥水商品資訊
        self.health_potion_inventory = {
            "小型血量藥水": {
                "price": 50,
                "heal_amount": 50,
                "stock": -1,  # 無限庫存
                "description": "回復 50 點血量"
            },
            "中型血量藥水": {
                "price": 150,
                "heal_amount": 150,
                "stock": -1,  # 無限庫存
                "description": "回復 150 點血量"
            },
            "大型血量藥水": {
                "price": 300,
                "heal_amount": 300,
                "stock": -1,  # 無限庫存
                "description": "回復 300 點血量"
            }
        }
        
        print("🏪 便利商店血量藥水系統已初始化")

    def buy_health_potion(self, player, potion_type):
        """
        購買血量藥水\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        potion_type (str): 藥水類型\n
        \n
        回傳:\n
        dict: 購買結果\n
        """
        if potion_type not in self.health_potion_inventory:
            return {"success": False, "message": f"沒有販售 {potion_type}"}
        
        potion_info = self.health_potion_inventory[potion_type]
        price = potion_info["price"]
        
        # 檢查玩家金錢
        if not player.spend_money(price):
            return {"success": False, "message": f"金錢不足，需要 ${price}"}
        
        # 直接使用藥水（立即回復血量）
        heal_result = player.use_health_potion(potion_type)
        
        if heal_result:
            return {
                "success": True,
                "message": f"成功購買並使用 {potion_type}，花費 ${price}"
            }
        else:
            # 如果使用失敗（血量已滿），退還金錢
            player.add_money(price)
            return {
                "success": False,
                "message": "血量已滿，無需購買藥水"
            }

    def get_inventory_info(self):
        """
        獲取血量藥水庫存資訊\n
        \n
        回傳:\n
        dict: 庫存資訊\n
        """
        return self.health_potion_inventory.copy()

    def can_afford_potion(self, player, potion_type):
        """
        檢查玩家是否負擔得起指定藥水\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        potion_type (str): 藥水類型\n
        \n
        回傳:\n
        bool: 是否負擔得起\n
        """
        if potion_type not in self.health_potion_inventory:
            return False
        
        price = self.health_potion_inventory[potion_type]["price"]
        return player.get_money() >= price

    def needs_health_potion(self, player):
        """
        檢查玩家是否需要血量藥水\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: 是否需要血量藥水\n
        """
        return player.health < player.max_health

    def recommend_potion(self, player):
        """
        為玩家推薦合適的血量藥水\n
        \n
        根據玩家當前血量和金錢狀況推薦最適合的藥水\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        str: 推薦的藥水類型，如果不需要則回傳 None\n
        """
        if not self.needs_health_potion(player):
            return None
        
        missing_health = player.max_health - player.health
        player_money = player.get_money()
        
        # 根據缺少的血量和玩家金錢推薦藥水
        if missing_health >= 300 and player_money >= 300:
            return "大型血量藥水"
        elif missing_health >= 150 and player_money >= 150:
            return "中型血量藥水"
        elif missing_health >= 50 and player_money >= 50:
            return "小型血量藥水"
        else:
            # 錢不夠買藥水
            return None

    def get_shop_menu_text(self, player):
        """
        獲取商店菜單文字\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        list: 菜單項目列表\n
        """
        menu_items = []
        menu_items.append("=== 血量藥水 ===")
        
        for potion_type, info in self.health_potion_inventory.items():
            price = info["price"]
            heal_amount = info["heal_amount"]
            affordable = "✅" if self.can_afford_potion(player, potion_type) else "❌"
            
            menu_items.append(f"{affordable} {potion_type} - ${price} (回復{heal_amount}血量)")
        
        # 添加推薦
        recommended = self.recommend_potion(player)
        if recommended:
            menu_items.append(f"💡 推薦: {recommended}")
        elif not self.needs_health_potion(player):
            menu_items.append("💚 您的血量充足，無需購買藥水")
        else:
            menu_items.append("💰 金錢不足以購買任何藥水")
        
        return menu_items