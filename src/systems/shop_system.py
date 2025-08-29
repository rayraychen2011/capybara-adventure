######################載入套件######################
import pygame
from config.settings import *
from src.utils.font_manager import get_font_manager, FontManager


######################通用商店介面######################
class ShopUI:
    """
    通用商店介面 - 處理所有類型商店的UI顯示\n
    \n
    提供統一的商店界面，包括：\n
    - 玩家金錢顯示\n
    - 商品列表顯示\n
    - 購買按鈕互動\n
    - 統一的中文界面\n
    """

    def __init__(self):
        """
        初始化商店UI\n
        """
        self.font_manager = get_font_manager()
        self.is_visible = False
        self.current_shop = None
        self.current_items = []
        
        # UI 尺寸設定
        self.width = 500
        self.height = 600
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # 顏色設定
        self.bg_color = (50, 50, 50)
        self.border_color = (255, 255, 255)
        self.button_color = (70, 130, 180)
        self.button_hover_color = (100, 149, 237)
        self.button_disabled_color = (128, 128, 128)
        
        # 按鈕列表
        self.buttons = []
        self.hovered_button = None
        
        print("通用商店UI初始化完成")

    def show(self, shop_name, items, player_money):
        """
        顯示商店界面\n
        \n
        參數:\n
        shop_name (str): 商店名稱\n
        items (list): 商品列表，每個項目包含 {'name': str, 'price': int, 'description': str}\n
        player_money (int): 玩家當前金錢\n
        """
        self.is_visible = True
        self.current_shop = shop_name
        self.current_items = items
        self.player_money = player_money
        
        # 創建購買按鈕
        self._create_buttons()
        
        print(f"顯示商店: {shop_name}")

    def hide(self):
        """
        隱藏商店界面\n
        """
        self.is_visible = False
        self.current_shop = None
        self.current_items = []
        self.buttons = []
        self.hovered_button = None

    def _create_buttons(self):
        """
        創建購買按鈕\n
        """
        self.buttons = []
        button_width = 80
        button_height = 30
        
        # 為每個商品創建購買按鈕
        for i, item in enumerate(self.current_items):
            button_x = self.x + self.width - button_width - 20
            button_y = self.y + 120 + i * 60
            
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # 檢查玩家是否有足夠金錢
            can_afford = self.player_money >= item['price']
            
            button_data = {
                'rect': button_rect,
                'item_index': i,
                'item': item,
                'can_afford': can_afford,
                'text': '購買'
            }
            
            self.buttons.append(button_data)

    def handle_mouse_move(self, mouse_pos):
        """
        處理滑鼠移動事件\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠位置\n
        """
        self.hovered_button = None
        
        for button in self.buttons:
            if button['rect'].collidepoint(mouse_pos):
                self.hovered_button = button
                break

    def handle_mouse_click(self, mouse_pos):
        """
        處理滑鼠點擊事件\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠位置\n
        \n
        回傳:\n
        dict: 購買結果，如果沒有點擊則返回None\n
        """
        for button in self.buttons:
            if button['rect'].collidepoint(mouse_pos) and button['can_afford']:
                # 返回購買信息
                return {
                    'action': 'buy',
                    'item': button['item'],
                    'item_index': button['item_index']
                }
        
        return None

    def update_player_money(self, new_money):
        """
        更新玩家金錢顯示\n
        \n
        參數:\n
        new_money (int): 新的金錢數量\n
        """
        self.player_money = new_money
        
        # 更新按鈕狀態
        for button in self.buttons:
            button['can_afford'] = self.player_money >= button['item']['price']

    def draw(self, screen):
        """
        繪製商店界面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        if not self.is_visible:
            return
        
        # 繪製半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 繪製主視窗
        main_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, main_rect)
        pygame.draw.rect(screen, self.border_color, main_rect, 3)
        
        # 繪製標題
        title_text = self.font_manager.render_text(self.current_shop, 24, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.x + self.width//2, self.y + 30))
        screen.blit(title_text, title_rect)
        
        # 繪製玩家金錢
        money_text = self.font_manager.render_text(f"當前金錢: ${self.player_money}", 18, (255, 215, 0))
        money_rect = money_text.get_rect(center=(self.x + self.width//2, self.y + 70))
        screen.blit(money_text, money_rect)
        
        # 繪製商品列表
        current_y = self.y + 120
        for i, item in enumerate(self.current_items):
            # 商品名稱
            name_text = self.font_manager.render_text(item['name'], 16, (255, 255, 255))
            screen.blit(name_text, (self.x + 20, current_y))
            
            # 商品價格
            price_text = self.font_manager.render_text(f"${item['price']}", 16, (255, 215, 0))
            screen.blit(price_text, (self.x + 20, current_y + 20))
            
            # 商品描述（如果有）
            if 'description' in item and item['description']:
                desc_text = self.font_manager.render_text(item['description'], 12, (200, 200, 200))
                screen.blit(desc_text, (self.x + 20, current_y + 40))
            
            current_y += 60
        
        # 繪製購買按鈕
        self._draw_buttons(screen)
        
        # 繪製關閉提示
        close_text = self.font_manager.render_text("按ESC關閉商店", 14, (180, 180, 180))
        close_rect = close_text.get_rect(center=(self.x + self.width//2, self.y + self.height - 20))
        screen.blit(close_text, close_rect)

    def _draw_buttons(self, screen):
        """
        繪製購買按鈕\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for button in self.buttons:
            # 決定按鈕顏色
            if not button['can_afford']:
                color = self.button_disabled_color
            elif button == self.hovered_button:
                color = self.button_hover_color
            else:
                color = self.button_color
            
            # 繪製按鈕背景
            pygame.draw.rect(screen, color, button['rect'])
            pygame.draw.rect(screen, self.border_color, button['rect'], 2)
            
            # 繪製按鈕文字
            text_color = (255, 255, 255) if button['can_afford'] else (128, 128, 128)
            button_text = self.font_manager.render_text(button['text'], 14, text_color)
            text_rect = button_text.get_rect(center=button['rect'].center)
            screen.blit(button_text, text_rect)


######################商店基礎類別######################
class BaseShop:
    """
    商店基礎類別 - 所有商店的共同基礎\n
    \n
    提供商店的基本功能：\n
    - 位置和範圍管理\n
    - 庫存管理\n
    - 購買邏輯\n
    - 玩家互動檢測\n
    """

    def __init__(self, x, y, shop_name, shop_type):
        """
        初始化商店\n
        \n
        參數:\n
        x (int): 商店X座標\n
        y (int): 商店Y座標\n
        shop_name (str): 商店名稱\n
        shop_type (str): 商店類型\n
        """
        self.x = x
        self.y = y
        self.shop_name = shop_name
        self.shop_type = shop_type
        
        # 字體管理器
        self.font_manager = FontManager()
        
        # 商店尺寸
        self.width = 60
        self.height = 40
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # 互動範圍
        self.interaction_range = 50
        self.is_player_nearby = False
        
        # 商店庫存
        self.inventory = {}
        
        # 初始化商店特定庫存
        self._setup_inventory()
        
        print(f"創建商店: {shop_name} 於 ({x}, {y})")

    def _setup_inventory(self):
        """
        設定商店庫存 - 子類別需要重寫\n
        """
        pass

    def is_near_player(self, player_position):
        """
        檢查玩家是否在互動範圍內\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        \n
        回傳:\n
        bool: 是否在互動範圍內\n
        """
        player_x, player_y = player_position
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        
        was_nearby = self.is_player_nearby
        self.is_player_nearby = distance <= self.interaction_range
        
        # 如果狀態改變，輸出提示
        if self.is_player_nearby and not was_nearby:
            print(f"進入 {self.shop_name} 互動範圍")
        elif was_nearby and not self.is_player_nearby:
            print(f"離開 {self.shop_name} 互動範圍")
        
        return self.is_player_nearby

    def get_shop_items(self):
        """
        獲取商店商品列表\n
        \n
        回傳:\n
        list: 商品列表\n
        """
        items = []
        for item_id, item_data in self.inventory.items():
            if item_data['stock'] > 0:  # 只顯示有庫存的商品
                items.append({
                    'id': item_id,
                    'name': item_data['name'],
                    'price': item_data['price'],
                    'description': item_data.get('description', ''),
                    'stock': item_data['stock']
                })
        
        return items

    def buy_item(self, item_id, player):
        """
        購買商品\n
        \n
        參數:\n
        item_id (str): 商品ID\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 購買結果\n
        """
        if item_id not in self.inventory:
            return {"success": False, "message": "商品不存在"}
        
        item = self.inventory[item_id]
        
        # 檢查庫存
        if item['stock'] <= 0:
            return {"success": False, "message": f"{item['name']}已售完"}
        
        # 檢查玩家金錢
        if player.money < item['price']:
            return {"success": False, "message": "金錢不足"}
        
        # 執行購買
        player.money -= item['price']
        item['stock'] -= 1
        
        # 處理特定商品的效果
        self._apply_item_effect(item_id, player)
        
        return {
            "success": True,
            "message": f"成功購買 {item['name']}！",
            "item": item
        }

    def _apply_item_effect(self, item_id, player):
        """
        應用商品效果 - 子類別可以重寫\n
        \n
        參數:\n
        item_id (str): 商品ID\n
        player (Player): 玩家物件\n
        """
        pass

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製商店\n
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
        
        # 繪製商店建築
        shop_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, (139, 69, 19), shop_rect)  # 棕色
        pygame.draw.rect(screen, (0, 0, 0), shop_rect, 2)  # 黑色邊框
        
        # 繪製商店名稱
        font = self.font_manager.get_font(16)
        name_text = font.render(self.shop_name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(screen_x + self.width//2, screen_y - 10))
        screen.blit(name_text, name_rect)
        
        # 如果玩家在附近，顯示互動提示
        if self.is_player_nearby:
            hint_text = font.render("按右鍵進入商店", True, (255, 255, 0))
            hint_rect = hint_text.get_rect(center=(screen_x + self.width//2, screen_y + self.height + 15))
            screen.blit(hint_text, hint_rect)