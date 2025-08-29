######################載入套件######################
import pygame
from src.core.scene_manager import Scene
from src.core.state_manager import GameState
from src.utils.font_manager import get_font_manager
from config.settings import *

######################主選單場景######################
class MenuScene(Scene):
    """
    主選單場景 - 遊戲的開始畫面\n
    \n
    提供開始遊戲、載入存檔、設定等功能\n
    玩家首次進入遊戲時看到的畫面\n
    """
    
    def __init__(self, state_manager):
        """
        初始化主選單場景\n
        \n
        參數:\n
        state_manager (StateManager): 遊戲狀態管理器\n
        """
        super().__init__("主選單")
        self.state_manager = state_manager
        
        # 取得字體管理器
        self.font_manager = get_font_manager()
        
        # 選單選項
        self.menu_options = [
            "開始遊戲",
            "載入存檔", 
            "遊戲設定",
            "退出遊戲"
        ]
        
        # 當前選中的選項
        self.selected_option = 0
        
        print("主選單場景已建立")
    
    def enter(self):
        """
        進入主選單場景\n
        """
        super().enter()
        self.selected_option = 0  # 重置選項
    
    def update(self, dt):
        """
        更新主選單邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 主選單通常不需要特別的更新邏輯
        pass
    
    def draw(self, screen):
        """
        繪製主選單畫面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 清空背景為天空藍色
        screen.fill(BACKGROUND_COLOR)
        
        # 繪製遊戲標題
        self._draw_title(screen)
        
        # 繪製選單選項
        self._draw_menu_options(screen)
        
        # 繪製版本資訊
        self._draw_version_info(screen)
    
    def _draw_title(self, screen):
        """
        繪製遊戲標題\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        title_text = self.font_manager.render_text(GAME_TITLE, TITLE_FONT_SIZE, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
    
    def _draw_menu_options(self, screen):
        """
        繪製選單選項\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        start_y = 300
        option_spacing = 60
        
        for i, option in enumerate(self.menu_options):
            # 如果是當前選中的選項，使用不同顏色
            if i == self.selected_option:
                color = (255, 255, 0)  # 黃色
                # 繪製選中指示器
                indicator = "► "
                option_text = indicator + option
            else:
                color = TEXT_COLOR  # 白色
                option_text = "  " + option
            
            # 繪製選項文字
            text_surface = self.font_manager.render_text(option_text, LARGE_FONT_SIZE, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * option_spacing))
            screen.blit(text_surface, text_rect)
    
    def _draw_version_info(self, screen):
        """
        繪製版本資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        version_text = self.font_manager.render_text("版本 1.0 - 開發中", 24, (200, 200, 200))
        version_rect = version_text.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
        screen.blit(version_text, version_rect)
        
        # 操作提示已移除
    
    def handle_event(self, event):
        """
        處理主選單輸入事件\n
        \n
        參數:\n
        event (pygame.event.Event): 輸入事件\n
        \n
        回傳:\n
        bool: True 表示事件已處理\n
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # 向上選擇
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                return True
                
            elif event.key == pygame.K_DOWN:
                # 向下選擇
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                return True
                
            elif event.key == pygame.K_RETURN:
                # 確認選擇
                self._execute_selected_option()
                return True
        
        return False
    
    def _execute_selected_option(self):
        """
        執行當前選中的選單選項\n
        """
        option = self.menu_options[self.selected_option]
        
        if option == "開始遊戲":
            # 開始新遊戲
            print("開始新遊戲")
            self.state_manager.change_state(GameState.PLAYING)
            
        elif option == "載入存檔":
            # 載入存檔（暫時未實作）
            print("載入存檔功能尚未實作")
            
        elif option == "遊戲設定":
            # 遊戲設定（暫時未實作）
            print("遊戲設定功能尚未實作")
            
        elif option == "退出遊戲":
            # 退出遊戲
            print("退出遊戲")
            self.state_manager.change_state(GameState.QUIT)