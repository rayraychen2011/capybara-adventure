######################載入套件######################
import pygame
import json
import os
from datetime import datetime
from src.utils.font_manager import get_font_manager


######################手機UI系統######################
class PhoneUI:
    """
    手機UI系統 - 按P鍵召喚的多功能手機介面\n
    \n
    功能:\n
    1. 顯示當前遊戲時間和日期\n
    2. 顯示天氣資訊\n
    3. 遊戲存檔和讀檔功能\n
    4. 各種遊戲設定\n
    """

    def __init__(self):
        """
        初始化手機UI\n
        """
        self.font_manager = get_font_manager()
        self.is_visible = False
        
        # UI設定
        self.phone_width = 350
        self.phone_height = 500
        self.phone_x = 50  # 固定在右下角
        self.phone_y = 50
        
        # 顏色設定
        self.bg_color = (40, 40, 40, 230)  # 半透明深灰
        self.border_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.accent_color = (100, 200, 255)
        self.button_color = (60, 60, 60)
        self.button_hover_color = (80, 80, 80)
        self.button_text_color = (255, 255, 255)
        
        # 按鈕設定
        self.button_height = 40
        self.button_margin = 10
        
        # 存檔設定
        self.save_file = "game_save.json"
        self.current_save_data = None
        
        # 天氣系統
        self.weather_conditions = [
            "☀️ 晴朗", "⛅ 多雲", "☁️ 陰天", 
            "🌧️ 小雨", "⛈️ 雷雨", "🌨️ 下雪"
        ]
        self.current_weather = "☀️ 晴朗"
        
        print("手機UI系統初始化完成")

    def toggle_visibility(self):
        """
        切換手機UI的顯示/隱藏狀態\n
        """
        self.is_visible = not self.is_visible
        if self.is_visible:
            print("手機UI開啟")
        else:
            print("手機UI關閉")

    def update(self, dt):
        """
        更新手機UI\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        if not self.is_visible:
            return
        
        # 可以在這裡添加動畫效果或其他更新邏輯
        pass

    def handle_click(self, mouse_pos):
        """
        處理滑鼠點擊事件\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠位置\n
        \n
        回傳:\n
        bool: 是否有處理點擊\n
        """
        if not self.is_visible:
            return False
        
        # 檢查是否點擊在手機UI範圍內
        phone_rect = pygame.Rect(
            self.phone_x, self.phone_y, 
            self.phone_width, self.phone_height
        )
        
        if not phone_rect.collidepoint(mouse_pos):
            # 點擊手機外部，關閉手機
            self.is_visible = False
            return True
        
        # 檢查按鈕點擊
        button_y = self.phone_y + 200  # 按鈕開始位置
        
        # 存檔按鈕
        save_button_rect = pygame.Rect(
            self.phone_x + self.button_margin,
            button_y,
            self.phone_width - 2 * self.button_margin,
            self.button_height
        )
        
        if save_button_rect.collidepoint(mouse_pos):
            self.save_game()
            return True
        
        # 讀檔按鈕
        button_y += self.button_height + self.button_margin
        load_button_rect = pygame.Rect(
            self.phone_x + self.button_margin,
            button_y,
            self.phone_width - 2 * self.button_margin,
            self.button_height
        )
        
        if load_button_rect.collidepoint(mouse_pos):
            self.load_game()
            return True
        
        # 天氣切換按鈕
        button_y += self.button_height + self.button_margin
        weather_button_rect = pygame.Rect(
            self.phone_x + self.button_margin,
            button_y,
            self.phone_width - 2 * self.button_margin,
            self.button_height
        )
        
        if weather_button_rect.collidepoint(mouse_pos):
            self.change_weather()
            return True
        
        return True  # 阻止點擊穿透

    def save_game(self):
        """
        保存遊戲狀態\n
        """
        try:
            # 這裡需要從遊戲場景獲取玩家位置和其他狀態
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "player_position": [0, 0],  # 需要從實際玩家獲取
                "player_health": 100,       # 需要從實際玩家獲取
                "player_money": 500,        # 需要從實際玩家獲取
                "game_time": "12:00",       # 需要從時間管理器獲取
                "weather": self.current_weather
            }
            
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self.current_save_data = save_data
            print(f"遊戲已保存到 {self.save_file}")
            
        except Exception as e:
            print(f"保存遊戲失敗: {e}")

    def load_game(self):
        """
        讀取遊戲狀態\n
        """
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                self.current_save_data = save_data
                self.current_weather = save_data.get("weather", "☀️ 晴朗")
                
                print(f"遊戲已從 {self.save_file} 讀取")
                print(f"存檔時間: {save_data.get('timestamp', '未知')}")
                
                # 這裡需要實際應用讀取的數據到遊戲狀態
                # 比如設定玩家位置、血量、金錢等
                
            else:
                print("沒有找到存檔檔案")
                
        except Exception as e:
            print(f"讀取遊戲失敗: {e}")

    def change_weather(self):
        """
        切換天氣\n
        """
        current_index = self.weather_conditions.index(self.current_weather)
        next_index = (current_index + 1) % len(self.weather_conditions)
        self.current_weather = self.weather_conditions[next_index]
        print(f"天氣變更為: {self.current_weather}")

    def draw(self, screen, time_manager=None):
        """
        繪製手機UI\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        time_manager (TimeManager): 時間管理器\n
        """
        if not self.is_visible:
            return
        
        # 計算位置（右下角）
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        self.phone_x = screen_width - self.phone_width - 20
        self.phone_y = screen_height - self.phone_height - 20
        
        # 創建手機背景
        phone_surface = pygame.Surface(
            (self.phone_width, self.phone_height), 
            pygame.SRCALPHA
        )
        phone_surface.fill(self.bg_color)
        screen.blit(phone_surface, (self.phone_x, self.phone_y))
        
        # 繪製邊框
        pygame.draw.rect(
            screen, self.border_color,
            (self.phone_x, self.phone_y, self.phone_width, self.phone_height),
            3
        )
        
        # 繪製標題
        title_font = self.font_manager.get_font(24)
        title_text = title_font.render("📱 智慧手機", True, self.accent_color)
        title_x = self.phone_x + (self.phone_width - title_text.get_width()) // 2
        title_y = self.phone_y + 15
        screen.blit(title_text, (title_x, title_y))
        
        # 繪製時間資訊
        content_y = title_y + 50
        content_font = self.font_manager.get_font(16)
        
        # 當前時間
        if time_manager:
            time_text = f"🕐 時間: {time_manager.get_formatted_time()}"
            date_text = f"📅 日期: {time_manager.get_current_weekday()}"
        else:
            time_text = "🕐 時間: 12:00"
            date_text = "📅 日期: 週一"
        
        time_surface = content_font.render(time_text, True, self.text_color)
        screen.blit(time_surface, (self.phone_x + 20, content_y))
        
        content_y += 25
        date_surface = content_font.render(date_text, True, self.text_color)
        screen.blit(date_surface, (self.phone_x + 20, content_y))
        
        # 天氣資訊
        content_y += 35
        weather_text = f"🌤️ 天氣: {self.current_weather}"
        weather_surface = content_font.render(weather_text, True, self.text_color)
        screen.blit(weather_surface, (self.phone_x + 20, content_y))
        
        # 存檔資訊
        content_y += 35
        if self.current_save_data:
            save_time = self.current_save_data.get('timestamp', '無')[:19]  # 只取日期時間部分
            save_text = f"💾 上次存檔: {save_time}"
        else:
            save_text = "💾 尚未存檔"
        
        save_surface = content_font.render(save_text, True, self.text_color)
        screen.blit(save_surface, (self.phone_x + 20, content_y))
        
        # 繪製按鈕
        button_y = self.phone_y + 200
        self._draw_button(screen, "💾 保存遊戲", self.phone_x + self.button_margin, button_y)
        
        button_y += self.button_height + self.button_margin
        self._draw_button(screen, "📂 讀取遊戲", self.phone_x + self.button_margin, button_y)
        
        button_y += self.button_height + self.button_margin
        self._draw_button(screen, f"🌤️ 切換天氣", self.phone_x + self.button_margin, button_y)
        
        # 提示文字
        hint_y = self.phone_y + self.phone_height - 40
        hint_font = self.font_manager.get_font(12)
        hint_text = "點擊外部區域關閉手機"
        hint_surface = hint_font.render(hint_text, True, (180, 180, 180))
        hint_x = self.phone_x + (self.phone_width - hint_surface.get_width()) // 2
        screen.blit(hint_surface, (hint_x, hint_y))

    def _draw_button(self, screen, text, x, y):
        """
        繪製按鈕\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        text (str): 按鈕文字\n
        x (int): X座標\n
        y (int): Y座標\n
        """
        button_width = self.phone_width - 2 * self.button_margin
        
        # 繪製按鈕背景
        button_rect = pygame.Rect(x, y, button_width, self.button_height)
        pygame.draw.rect(screen, self.button_color, button_rect)
        pygame.draw.rect(screen, self.border_color, button_rect, 2)
        
        # 繪製按鈕文字
        button_font = self.font_manager.get_font(14)
        text_surface = button_font.render(text, True, self.button_text_color)
        text_x = x + (button_width - text_surface.get_width()) // 2
        text_y = y + (self.button_height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

    def set_player_data(self, player):
        """
        設定玩家資料（用於存檔）\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # 這個方法用於從外部設定玩家資料
        pass

    def get_save_data(self):
        """
        獲取存檔資料\n
        \n
        回傳:\n
        dict: 存檔資料\n
        """
        return self.current_save_data