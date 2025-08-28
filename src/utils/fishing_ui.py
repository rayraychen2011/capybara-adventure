######################載入套件######################
import pygame
import time
from src.utils.font_manager import get_font_manager
from config.settings import *


######################釣魚 UI 管理器######################
class FishingUI:
    """
    釣魚 UI 管理器 - 顯示釣魚相關的用戶界面\n
    \n
    負責顯示：\n
    1. 釣魚狀態提示\n
    2. 釣魚計時器\n
    3. 成功/失敗訊息\n
    4. 魚類資訊展示\n
    \n
    使用繁體中文文字顯示所有內容\n
    """

    def __init__(self):
        """
        初始化釣魚 UI\n
        """
        self.font_manager = get_font_manager()
        
        # UI 狀態
        self.is_showing_message = False
        self.message_text = ""
        self.message_color = TEXT_COLOR
        self.message_start_time = 0
        self.message_duration = 3.0  # 訊息顯示時間（秒）
        
        # 釣魚狀態 UI
        self.show_fishing_status = False
        self.fishing_status_text = ""
        
        # 魚類展示 UI
        self.show_fish_info = False
        self.fish_info = None
        self.fish_info_start_time = 0
        self.fish_info_duration = 5.0  # 魚類資訊顯示時間（秒）
        
        # UI 位置
        self.message_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.status_position = (SCREEN_WIDTH // 2, 100)
        self.fish_info_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        
        print("釣魚 UI 初始化完成")

    def show_message(self, message, color=TEXT_COLOR, duration=3.0):
        """
        顯示訊息\n
        \n
        參數:\n
        message (str): 要顯示的訊息文字\n
        color (tuple): 文字顏色\n
        duration (float): 顯示時間（秒）\n
        """
        self.message_text = message
        self.message_color = color
        self.message_duration = duration
        self.message_start_time = time.time()
        self.is_showing_message = True

    def show_fishing_success(self, fish_info, reward):
        """
        顯示釣魚成功資訊\n
        \n
        參數:\n
        fish_info (dict): 魚類資訊\n
        reward (int): 獎勵金錢\n
        """
        # 顯示成功訊息
        success_message = f"🎣 釣到了魚！"
        self.show_message(success_message, (0, 255, 0), 2.0)  # 綠色訊息
        
        # 顯示魚類詳細資訊
        self.fish_info = {
            "name": fish_info["name"],
            "rarity": fish_info["rarity"],
            "reward": reward
        }
        self.show_fish_info = True
        self.fish_info_start_time = time.time()

    def show_fishing_failure(self):
        """
        顯示釣魚失敗訊息\n
        """
        failure_message = "🐟 魚跑掉了！"
        self.show_message(failure_message, (255, 100, 100), 2.0)  # 紅色訊息

    def show_fishing_bite(self):
        """
        顯示魚咬鉤訊息\n
        """
        bite_message = "🐟 釣到了！快按右鍵！"
        self.show_message(bite_message, (255, 255, 0), 1.0)  # 黃色訊息

    def update_fishing_status(self, fishing_system):
        """
        更新釣魚狀態顯示\n
        \n
        參數:\n
        fishing_system (FishingSystem): 釣魚系統實例\n
        """
        if fishing_system.is_fishing_active():
            status = fishing_system.get_fishing_status()
            
            if status["waiting_for_bite"]:
                self.fishing_status_text = "🎣 等待魚兒咬鉤..."
                self.show_fishing_status = True
            elif status["has_bite"]:
                remaining_time = status.get("time_remaining", 0)
                self.fishing_status_text = f"⚡ 快按右鍵！剩餘時間: {remaining_time:.1f}秒"
                self.show_fishing_status = True
            else:
                self.show_fishing_status = False
        else:
            self.show_fishing_status = False

    def update(self, dt):
        """
        更新 UI 狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        current_time = time.time()
        
        # 更新訊息顯示
        if self.is_showing_message:
            if current_time - self.message_start_time >= self.message_duration:
                self.is_showing_message = False
        
        # 更新魚類資訊顯示
        if self.show_fish_info:
            if current_time - self.fish_info_start_time >= self.fish_info_duration:
                self.show_fish_info = False

    def draw(self, screen):
        """
        繪製釣魚 UI\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲螢幕\n
        """
        # 繪製一般訊息
        if self.is_showing_message and self.message_text:
            self._draw_centered_message(screen, self.message_text, self.message_position, self.message_color)
        
        # 繪製釣魚狀態
        if self.show_fishing_status and self.fishing_status_text:
            self._draw_centered_message(screen, self.fishing_status_text, self.status_position, (255, 255, 255))
        
        # 繪製魚類資訊
        if self.show_fish_info and self.fish_info:
            self._draw_fish_info(screen)

    def _draw_centered_message(self, screen, text, position, color):
        """
        繪製置中的訊息\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲螢幕\n
        text (str): 訊息文字\n
        position (tuple): 位置 (x, y)\n
        color (tuple): 文字顏色\n
        """
        font = self.font_manager.get_font(24)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        
        # 繪製背景
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        screen.blit(bg_surface, bg_rect)
        
        # 繪製文字
        screen.blit(text_surface, text_rect)

    def _draw_fish_info(self, screen):
        """
        繪製魚類詳細資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲螢幕\n
        """
        if not self.fish_info:
            return
        
        # 準備文字行
        lines = [
            f"🐟 品種：{self.fish_info['name']}",
            f"✨ 稀有度：{self.fish_info['rarity']}",
            f"💰 獲得金錢：${self.fish_info['reward']}"
        ]
        
        # 計算總高度
        font = self.font_manager.get_font(20)
        line_height = font.get_height()
        total_height = len(lines) * line_height + (len(lines) - 1) * 5  # 5像素行間距
        
        # 計算背景大小
        max_width = 0
        for line in lines:
            text_width = font.size(line)[0]
            max_width = max(max_width, text_width)
        
        # 繪製背景
        bg_width = max_width + 40
        bg_height = total_height + 20
        bg_x = self.fish_info_position[0] - bg_width // 2
        bg_y = self.fish_info_position[1] - bg_height // 2
        
        bg_surface = pygame.Surface((bg_width, bg_height))
        bg_surface.set_alpha(200)
        bg_surface.fill((0, 0, 50))  # 深藍色背景
        screen.blit(bg_surface, (bg_x, bg_y))
        
        # 繪製邊框
        pygame.draw.rect(screen, (255, 215, 0), (bg_x, bg_y, bg_width, bg_height), 2)  # 金色邊框
        
        # 繪製文字行
        y_offset = bg_y + 10
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            text_x = self.fish_info_position[0] - text_surface.get_width() // 2
            screen.blit(text_surface, (text_x, y_offset))
            y_offset += line_height + 5

    def handle_fishing_event(self, event_data):
        """
        處理釣魚事件\n
        \n
        參數:\n
        event_data (dict): 釣魚事件資料\n
        """
        if not event_data:
            return
        
        event_type = event_data.get("event")
        
        if event_type == "bite":
            self.show_fishing_bite()
        elif event_type == "catch_success":
            fish_info = event_data.get("fish", {})
            reward = event_data.get("reward", 0)
            self.show_fishing_success(fish_info, reward)
        elif event_type == "catch_failed":
            self.show_fishing_failure()

    def hide_all(self):
        """
        隱藏所有 UI 元素\n
        """
        self.is_showing_message = False
        self.show_fishing_status = False
        self.show_fish_info = False