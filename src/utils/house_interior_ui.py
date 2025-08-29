######################載入套件######################
import pygame
from config.settings import *


######################住宅內部檢視 UI######################
class HouseInteriorUI:
    """
    住宅內部檢視 UI - 顯示住宅內部狀況\n
    \n
    當玩家點擊住宅時顯示住宅內部資訊：\n
    - 居民列表\n
    - 居民狀態\n
    - 住宅基本資訊\n
    """

    def __init__(self):
        """
        初始化住宅內部檢視 UI\n
        """
        # UI 狀態
        self.visible = False
        self.current_house = None
        
        # UI 尺寸和位置
        self.ui_width = 400
        self.ui_height = 300
        self.ui_x = (SCREEN_WIDTH - self.ui_width) // 2
        self.ui_y = (SCREEN_HEIGHT - self.ui_height) // 2
        
        # 顏色設定
        self.background_color = (50, 50, 50, 230)
        self.border_color = (200, 200, 200)
        self.text_color = (255, 255, 255)
        self.title_color = (255, 215, 0)
        
        # 字體 - 使用字體管理器支援繁體中文
        from src.utils.font_manager import get_font_manager
        font_manager = get_font_manager()
        self.title_font = font_manager.get_font(28)
        self.text_font = font_manager.get_font(20)
        self.small_font = font_manager.get_font(16)

    def show(self, house):
        """
        顯示住宅內部檢視\n
        \n
        參數:\n
        house (ResidentialHouse): 要檢視的住宅\n
        """
        self.visible = True
        self.current_house = house
        print(f"顯示住宅內部檢視: {house.name if hasattr(house, 'name') else '住宅'}")

    def hide(self):
        """
        隱藏住宅內部檢視\n
        """
        self.visible = False
        self.current_house = None

    def is_visible(self):
        """
        檢查是否正在顯示\n
        \n
        回傳:\n
        bool: 是否顯示中\n
        """
        return self.visible

    def handle_click(self, mouse_pos):
        """
        處理滑鼠點擊事件\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠位置 (x, y)\n
        \n
        回傳:\n
        bool: 是否點擊在 UI 範圍內\n
        """
        if not self.visible:
            return False
        
        ui_rect = pygame.Rect(self.ui_x, self.ui_y, self.ui_width, self.ui_height)
        
        # 如果點擊在 UI 外部，關閉 UI
        if not ui_rect.collidepoint(mouse_pos):
            self.hide()
            return True
        
        return True

    def draw(self, screen):
        """
        繪製住宅內部檢視 UI\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        if not self.visible or not self.current_house:
            return
        
        # 繪製半透明背景遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 繪製 UI 背景
        ui_surface = pygame.Surface((self.ui_width, self.ui_height))
        ui_surface.set_alpha(230)
        ui_surface.fill((50, 50, 50))
        screen.blit(ui_surface, (self.ui_x, self.ui_y))
        
        # 繪製邊框
        ui_rect = pygame.Rect(self.ui_x, self.ui_y, self.ui_width, self.ui_height)
        pygame.draw.rect(screen, self.border_color, ui_rect, 3)
        
        # 繪製標題
        if hasattr(self.current_house, 'is_player_home') and self.current_house.is_player_home:
            title_text = "玩家之家"
        else:
            title_text = "住宅內部檢視"
        
        title_surface = self.title_font.render(title_text, True, self.title_color)
        title_x = self.ui_x + (self.ui_width - title_surface.get_width()) // 2
        title_y = self.ui_y + 15
        screen.blit(title_surface, (title_x, title_y))
        
        # 繪製住宅基本資訊
        info_y = title_y + 40
        
        # 住宅容量資訊
        if hasattr(self.current_house, 'residents'):
            capacity_text = f"居民數量: {len(self.current_house.residents)}/{self.current_house.max_residents if hasattr(self.current_house, 'max_residents') else 3}"
            capacity_surface = self.text_font.render(capacity_text, True, self.text_color)
            screen.blit(capacity_surface, (self.ui_x + 20, info_y))
            info_y += 30
        
        # 繪製居民列表
        residents_title = self.text_font.render("居民列表:", True, self.title_color)
        screen.blit(residents_title, (self.ui_x + 20, info_y))
        info_y += 25
        
        if hasattr(self.current_house, 'residents') and self.current_house.residents:
            for i, resident in enumerate(self.current_house.residents):
                # 居民名稱
                resident_name = getattr(resident, 'name', f'居民 {i+1}')
                name_surface = self.small_font.render(f"• {resident_name}", True, self.text_color)
                screen.blit(name_surface, (self.ui_x + 40, info_y))
                
                # 居民職業
                if hasattr(resident, 'profession'):
                    profession_text = resident.profession.value if hasattr(resident.profession, 'value') else str(resident.profession)
                    profession_surface = self.small_font.render(f"  職業: {profession_text}", True, (180, 180, 180))
                    screen.blit(profession_surface, (self.ui_x + 40, info_y + 15))
                
                # 居民狀態
                if hasattr(resident, 'is_at_work'):
                    status_text = "工作中" if resident.is_at_work else "在家"
                    status_color = (255, 255, 0) if resident.is_at_work else (0, 255, 0)
                    status_surface = self.small_font.render(f"  狀態: {status_text}", True, status_color)
                    screen.blit(status_surface, (self.ui_x + 40, info_y + 30))
                
                # 受傷狀態
                if hasattr(resident, 'is_injured') and resident.is_injured:
                    injured_surface = self.small_font.render("  ⚠️ 住院中", True, (255, 0, 0))
                    screen.blit(injured_surface, (self.ui_x + 40, info_y + 45))
                    info_y += 75
                else:
                    info_y += 60
                
                # 防止內容溢出
                if info_y > self.ui_y + self.ui_height - 40:
                    break
        else:
            # 沒有居民
            no_residents_surface = self.small_font.render("目前沒有居民", True, (150, 150, 150))
            screen.blit(no_residents_surface, (self.ui_x + 40, info_y))
        
        # 繪製關閉提示
        close_hint = self.small_font.render("點擊外部區域關閉", True, (150, 150, 150))
        close_x = self.ui_x + self.ui_width - close_hint.get_width() - 10
        close_y = self.ui_y + self.ui_height - 25
        screen.blit(close_hint, (close_x, close_y))

    def update(self, dt):
        """
        更新 UI 狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 目前沒有需要更新的內容
        pass