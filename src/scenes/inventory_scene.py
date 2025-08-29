######################載入套件######################
import pygame
from src.core.scene_manager import Scene
from src.core.state_manager import GameState
from src.utils.font_manager import get_font_manager
from config.settings import *

######################背包場景######################
class InventoryScene(Scene):
    """
    背包場景 - 物品管理介面\n
    \n
    顯示玩家的背包內容，允許查看和管理物品\n
    提供物品詳細資訊和基本的物品操作功能\n
    """
    
    def __init__(self, state_manager, player):
        """
        初始化背包場景\n
        \n
        參數:\n
        state_manager (StateManager): 遊戲狀態管理器\n
        player (Player): 玩家角色實例\n
        """
        super().__init__("背包")
        self.state_manager = state_manager
        self.player = player
        
        # 取得字體管理器
        self.font_manager = get_font_manager()
        
        # 背包顯示設定
        self.items_per_row = 5
        self.item_size = 64
        self.item_padding = 10
        self.start_x = 100
        self.start_y = 150
        
        # 當前選中的物品索引
        self.selected_item_index = 0
        
        print("背包場景已建立")
    
    def enter(self):
        """
        進入背包場景\n
        """
        super().enter()
        print("打開背包")
        self.selected_item_index = 0  # 重置選中物品
    
    def update(self, dt):
        """
        更新背包場景邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 背包場景通常不需要更新邏輯
        pass
    
    def draw(self, screen):
        """
        繪製背包場景\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 半透明黑色背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 繪製背包標題
        self._draw_title(screen)
        
        # 繪製玩家資訊
        self._draw_player_info(screen)
        
        # 繪製物品格子
        self._draw_inventory_grid(screen)
        
        # 繪製操作說明
        self._draw_controls(screen)
    
    def _draw_title(self, screen):
        """
        繪製背包標題\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        title_text = self.font_manager.render_text("背包", TITLE_FONT_SIZE, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_text, title_rect)
    
    def _draw_player_info(self, screen):
        """
        繪製玩家資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 顯示金錢
        money_text = self.font_manager.render_text(
            f"金錢: ${self.player.get_money()}", 
            DEFAULT_FONT_SIZE, 
            TEXT_COLOR
        )
        screen.blit(money_text, (50, 120))
        
        # 顯示背包容量
        inventory = self.player.get_inventory_list()
        # 由於物品系統已刪除，inventory 是空列表，所以物品數量為0
        item_count = len(inventory) if isinstance(inventory, list) else sum(inventory.values())
        capacity = self.player.inventory_capacity
        capacity_text = self.font_manager.render_text(
            f"容量: {item_count}/{capacity}", 
            DEFAULT_FONT_SIZE, 
            TEXT_COLOR
        )
        screen.blit(capacity_text, (SCREEN_WIDTH - 200, 120))
    
    def _draw_inventory_grid(self, screen):
        """
        繪製物品格子\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        inventory = self.player.get_inventory_list()
        
        # 由於物品系統已刪除，inventory 是空列表
        if isinstance(inventory, list):
            # 如果是列表（物品系統已刪除），顯示空的背包格子
            item_keys = []
        else:
            # 如果是字典，獲取所有物品的鍵值列表
            item_keys = list(inventory.keys())
        
        # 繪製空的背包格子
        for i in range(self.rows * self.cols):
            row = i // self.cols
            col = i % self.cols
            
            # 計算格子位置
            x = self.start_x + col * (self.item_size + self.item_padding)
            y = self.start_y + row * (self.item_size + self.item_padding)
            
            # 創建格子矩形
            item_rect = pygame.Rect(x, y, self.item_size, self.item_size)
            
            # 繪製格子背景
            if i == self.selected_item_index and i < len(item_keys):
                # 選中的格子用亮色背景
                pygame.draw.rect(screen, (100, 100, 150), item_rect)
            else:
                # 普通格子用深色背景
                pygame.draw.rect(screen, (50, 50, 50), item_rect)
            
            # 繪製格子邊框
            pygame.draw.rect(screen, (200, 200, 200), item_rect, 2)
            
            # 如果有物品，繪製物品資訊
            if i < len(item_keys):
                item_name = item_keys[i]
                quantity = inventory[item_name] if not isinstance(inventory, list) else 0
                
                # 繪製物品名稱（簡化顯示）
                if len(item_name) > 6:
                    display_name = item_name[:5] + "..."
                else:
                    display_name = item_name
                
                name_text = self.font_manager.render_text(
                    display_name, 
                    12, 
                    TEXT_COLOR
                )
                name_rect = name_text.get_rect(center=(x + self.item_size // 2, y + 20))
                screen.blit(name_text, name_rect)
                
                # 繪製數量
                if quantity > 1:
                    qty_text = self.font_manager.render_text(
                        str(quantity), 
                        10, 
                        (255, 255, 0)
                    )
                    screen.blit(qty_text, (x + self.item_size - 15, y + self.item_size - 15))
        
        # 如果沒有物品，顯示提示
        if not item_keys:
            empty_text = self.font_manager.render_text("背包空空如也", 20, (128, 128, 128))
            empty_rect = empty_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(empty_text, empty_rect)
    
    def _get_item_color(self, item_name):
        """
        根據物品名稱返回對應的顏色\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        \n
        回傳:\n
        tuple: RGB 顏色值\n
        """
        # 簡單的物品顏色映射
        color_map = {
            "小魚": (0, 191, 255),      # 藍色
            "鯉魚": (255, 165, 0),      # 橘色
            "鱸魚": (50, 205, 50),      # 綠色
            "虹鱒": (255, 20, 147),     # 深粉色
            "金魚王": (255, 215, 0),    # 金色
            "兔肉": (139, 69, 19),      # 棕色
            "鹿肉": (160, 82, 45),      # 淺棕色
            "熊肉": (105, 105, 105),    # 灰色
            "鳥肉": (255, 255, 255),    # 白色
            "工具": (128, 128, 128),    # 灰色
            "材料": (34, 139, 34),      # 森林綠
        }
        
        # 檢查物品名稱中是否包含關鍵字
        for keyword, color in color_map.items():
            if keyword in item_name:
                return color
        
        # 預設顏色
        return (200, 200, 200)
    
    def _draw_controls(self, screen):
        """
        繪製操作說明\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        controls = [
            "I 或 ESC: 關閉背包",
            "方向鍵: 選擇物品",
            "E: 使用物品（預留）"
        ]
        
        y_offset = SCREEN_HEIGHT - 100
        for i, control in enumerate(controls):
            text = self.font_manager.render_text(control, DEFAULT_FONT_SIZE, TEXT_COLOR)
            screen.blit(text, (50, y_offset + i * 25))
    
    def handle_event(self, event):
        """
        處理背包場景輸入事件\n
        \n
        參數:\n
        event (pygame.event.Event): 輸入事件\n
        \n
        回傳:\n
        bool: True 表示事件已處理\n
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                # 關閉背包，回到遊戲
                self.state_manager.change_state(GameState.PLAYING)
                return True
            
            elif event.key == pygame.K_LEFT:
                # 向左選擇物品
                self._move_selection(-1)
                return True
                
            elif event.key == pygame.K_RIGHT:
                # 向右選擇物品
                self._move_selection(1)
                return True
                
            elif event.key == pygame.K_UP:
                # 向上選擇物品
                self._move_selection(-self.items_per_row)
                return True
                
            elif event.key == pygame.K_DOWN:
                # 向下選擇物品
                self._move_selection(self.items_per_row)
                return True
                
            elif event.key == pygame.K_e:
                # 使用選中的物品
                self._use_selected_item()
                return True
        
        return False
    
    def _move_selection(self, delta):
        """
        移動選中的物品\n
        \n
        參數:\n
        delta (int): 移動的距離\n
        """
        inventory = self.player.get_inventory_list()
        item_count = len(inventory)
        
        if item_count > 0:
            self.selected_item_index = (self.selected_item_index + delta) % item_count
            if self.selected_item_index < 0:
                self.selected_item_index = item_count - 1
    
    def _use_selected_item(self):
        """
        使用選中的物品\n
        """
        inventory = self.player.get_inventory_list()
        item_keys = list(inventory.keys())
        
        if 0 <= self.selected_item_index < len(item_keys):
            selected_item = item_keys[self.selected_item_index]
            print(f"使用物品: {selected_item}")
            # 這裡可以實作物品使用邏輯
            # 例如：self.player.use_item(selected_item)
        else:
            print("沒有選中的物品")