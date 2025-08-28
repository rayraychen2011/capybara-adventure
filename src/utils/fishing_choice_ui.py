######################載入套件######################
import pygame
import time
from src.utils.font_manager import get_font_manager
from config.settings import *


######################釣魚選擇UI######################
class FishingChoiceUI:
    """
    釣魚選擇UI - 顯示放生/賣掉選擇介面\n
    \n
    當玩家釣到魚後，顯示選擇介面讓玩家決定是要放生還是賣掉\n
    包含3秒倒數計時和按鈕互動功能\n
    """

    def __init__(self):
        """
        初始化釣魚選擇UI\n
        """
        self.font_manager = get_font_manager()
        self.is_visible = False
        self.fish_data = None
        self.choice_start_time = 0
        self.choice_duration = 3.0
        
        # UI設定
        self.background_color = (0, 0, 0, 200)  # 半透明黑色背景
        self.text_color = (255, 255, 255)  # 白色文字
        self.button_color = (64, 64, 64)  # 灰色按鈕
        self.button_hover_color = (96, 96, 96)  # 滑鼠懸停顏色
        self.button_text_color = (255, 255, 255)  # 按鈕文字顏色
        self.release_button_color = (0, 150, 0)  # 放生按鈕 - 綠色
        self.sell_button_color = (150, 150, 0)  # 賣掉按鈕 - 黃色
        
        # UI尺寸和位置
        self.width = 400
        self.height = 250
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # 按鈕設定
        self.button_width = 120
        self.button_height = 50
        self.release_button_rect = pygame.Rect(
            self.x + 60, 
            self.y + 180, 
            self.button_width, 
            self.button_height
        )
        self.sell_button_rect = pygame.Rect(
            self.x + 220, 
            self.y + 180, 
            self.button_width, 
            self.button_height
        )
        
        # 互動狀態
        self.hovered_button = None
        
        print("🎣 釣魚選擇UI已初始化")

    def show_choice(self, fish_data, choice_duration=3.0):
        """
        顯示選擇介面\n
        \n
        參數:\n
        fish_data (dict): 魚類資料\n
        choice_duration (float): 選擇時間限制\n
        """
        self.is_visible = True
        self.fish_data = fish_data
        self.choice_start_time = time.time()
        self.choice_duration = choice_duration
        print(f"🎣 顯示釣魚選擇介面: {fish_data['name']}")

    def hide(self):
        """
        隱藏選擇介面\n
        """
        self.is_visible = False
        self.fish_data = None
        self.hovered_button = None
        print("🎣 隱藏釣魚選擇介面")

    def get_remaining_time(self):
        """
        獲取剩餘選擇時間\n
        \n
        回傳:\n
        float: 剩餘秒數\n
        """
        if not self.is_visible:
            return 0
        
        elapsed = time.time() - self.choice_start_time
        return max(0, self.choice_duration - elapsed)

    def is_time_up(self):
        """
        檢查時間是否已到\n
        \n
        回傳:\n
        bool: 時間是否已到\n
        """
        return self.get_remaining_time() <= 0

    def handle_event(self, event):
        """
        處理輸入事件\n
        \n
        參數:\n
        event (pygame.Event): 事件物件\n
        \n
        回傳:\n
        str: 玩家選擇 ('release', 'sell', None)\n
        """
        if not self.is_visible:
            return None
        
        if event.type == pygame.MOUSEMOTION:
            # 更新滑鼠懸停狀態
            mouse_pos = event.pos
            if self.release_button_rect.collidepoint(mouse_pos):
                self.hovered_button = "release"
            elif self.sell_button_rect.collidepoint(mouse_pos):
                self.hovered_button = "sell"
            else:
                self.hovered_button = None
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵
                mouse_pos = event.pos
                if self.release_button_rect.collidepoint(mouse_pos):
                    return "release"
                elif self.sell_button_rect.collidepoint(mouse_pos):
                    return "sell"
        
        elif event.type == pygame.KEYDOWN:
            # 鍵盤快捷鍵
            if event.key == pygame.K_r or event.key == pygame.K_1:
                return "release"
            elif event.key == pygame.K_s or event.key == pygame.K_2:
                return "sell"
        
        return None

    def update(self, dt):
        """
        更新UI狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 檢查時間是否到期
        if self.is_visible and self.is_time_up():
            return "time_up"
        
        return None

    def draw(self, screen):
        """
        繪製選擇介面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標\n
        """
        if not self.is_visible or not self.fish_data:
            return
        
        # 繪製背景
        background_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        background_surface.fill(self.background_color)
        screen.blit(background_surface, (self.x, self.y))
        
        # 繪製邊框
        pygame.draw.rect(screen, self.text_color, (self.x, self.y, self.width, self.height), 3)
        
        # 繪製魚類資訊
        self._draw_fish_info(screen)
        
        # 繪製選擇按鈕
        self._draw_buttons(screen)
        
        # 繪製倒數計時
        self._draw_countdown(screen)
        
        # 繪製操作提示
        self._draw_instructions(screen)

    def _draw_fish_info(self, screen):
        """
        繪製魚類資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標\n
        """
        # 標題
        title_font = self.font_manager.get_font(UI_FONT_SIZE + 4)
        title_text = title_font.render("🎣 釣到魚了！", True, (255, 255, 0))
        title_rect = title_text.get_rect(center=(self.x + self.width // 2, self.y + 30))
        screen.blit(title_text, title_rect)
        
        # 魚類名稱
        name_font = self.font_manager.get_font(UI_FONT_SIZE + 2)
        name_text = name_font.render(f"🐟 {self.fish_data['name']}", True, self.fish_data['color'])
        name_rect = name_text.get_rect(center=(self.x + self.width // 2, self.y + 65))
        screen.blit(name_text, name_rect)
        
        # 稀有度
        rarity_font = self.font_manager.get_font(UI_FONT_SIZE)
        rarity_text = rarity_font.render(f"稀有度: {self.fish_data['rarity']}", True, self.text_color)
        rarity_rect = rarity_text.get_rect(center=(self.x + self.width // 2, self.y + 95))
        screen.blit(rarity_text, rarity_rect)
        
        # 價值
        value_text = f"價值: ${self.fish_data['base_reward']}"
        value_surface = rarity_font.render(value_text, True, self.text_color)
        value_rect = value_surface.get_rect(center=(self.x + self.width // 2, self.y + 120))
        screen.blit(value_surface, value_rect)

    def _draw_buttons(self, screen):
        """
        繪製選擇按鈕\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標\n
        """
        button_font = self.font_manager.get_font(UI_FONT_SIZE)
        
        # 放生按鈕
        release_color = self.release_button_color
        if self.hovered_button == "release":
            release_color = tuple(min(255, c + 30) for c in release_color)
        
        pygame.draw.rect(screen, release_color, self.release_button_rect)
        pygame.draw.rect(screen, self.text_color, self.release_button_rect, 2)
        
        release_text = button_font.render("放生 (R)", True, self.button_text_color)
        release_text_rect = release_text.get_rect(center=self.release_button_rect.center)
        screen.blit(release_text, release_text_rect)
        
        # 賣掉按鈕
        sell_color = self.sell_button_color
        if self.hovered_button == "sell":
            sell_color = tuple(min(255, c + 30) for c in sell_color)
        
        pygame.draw.rect(screen, sell_color, self.sell_button_rect)
        pygame.draw.rect(screen, self.text_color, self.sell_button_rect, 2)
        
        sell_text = button_font.render("賣掉 (S)", True, self.button_text_color)
        sell_text_rect = sell_text.get_rect(center=self.sell_button_rect.center)
        screen.blit(sell_text, sell_text_rect)

    def _draw_countdown(self, screen):
        """
        繪製倒數計時\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標\n
        """
        remaining_time = self.get_remaining_time()
        
        # 倒數文字
        countdown_font = self.font_manager.get_font(UI_FONT_SIZE - 2)
        countdown_text = f"剩餘時間: {remaining_time:.1f}秒"
        
        # 時間不足時變紅色
        text_color = (255, 100, 100) if remaining_time < 1.0 else self.text_color
        countdown_surface = countdown_font.render(countdown_text, True, text_color)
        countdown_rect = countdown_surface.get_rect(center=(self.x + self.width // 2, self.y + 150))
        screen.blit(countdown_surface, countdown_rect)

    def _draw_instructions(self, screen):
        """
        繪製操作說明\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標\n
        """
        instruction_font = self.font_manager.get_font(UI_FONT_SIZE - 4)
        instructions = [
            "💚 放生：血量 × 1.1（上限1000）",
            "💰 賣掉：獲得金錢",
            "⏰ 時間到自動放生"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = instruction_font.render(instruction, True, (200, 200, 200))
            text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height - 45 + i * 15))
            screen.blit(text_surface, text_rect)