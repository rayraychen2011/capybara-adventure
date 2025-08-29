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
        try:
            self.font_manager = get_font_manager()
        except Exception as e:
            print(f"字體管理器初始化失敗: {e}")
            self.font_manager = None
            
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
        
        # 存檔設定 - 確保檔案存放在安全的位置
        import os
        try:
            # 嘗試建立存檔目錄
            save_dir = os.path.join(os.getcwd(), "saves")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            self.save_file = os.path.join(save_dir, "game_save.json")
        except Exception as e:
            print(f"存檔目錄建立失敗，使用當前目錄: {e}")
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
        try:
            self.is_visible = not self.is_visible
            if self.is_visible:
                print("手機UI開啟")
            else:
                print("手機UI關閉")
        except Exception as e:
            print(f"手機UI切換失敗: {e}")
            # 如果切換失敗，確保UI處於安全狀態
            self.is_visible = False

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

    def handle_click(self, mouse_pos, player=None, time_manager=None):
        """
        處理滑鼠點擊事件\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠位置\n
        player: 玩家物件（可選）\n
        time_manager: 時間管理器（可選）\n
        \n
        回傳:\n
        bool: 是否有處理點擊\n
        """
        if not self.is_visible:
            return False
        
        try:
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
                try:
                    self.save_game(player, time_manager)
                except Exception as e:
                    print(f"存檔按鈕處理失敗: {e}")
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
                try:
                    self.load_game()
                except Exception as e:
                    print(f"讀檔按鈕處理失敗: {e}")
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
                try:
                    self.change_weather()
                except Exception as e:
                    print(f"天氣切換按鈕處理失敗: {e}")
                return True
            
            return True  # 阻止點擊穿透
            
        except Exception as e:
            print(f"手機點擊處理失敗: {e}")
            # 如果處理失敗，關閉手機UI
            self.is_visible = False
            return True

    def save_game(self, player=None, time_manager=None):
        """
        保存遊戲狀態\n
        \n
        參數:\n
        player: 玩家物件（可選）\n
        time_manager: 時間管理器（可選）\n
        """
        try:
            # 收集實際的遊戲資料
            player_position = [0, 0]
            player_health = 100
            player_money = 500
            game_time = "12:00"
            
            # 如果有提供玩家資料，使用實際資料
            if player:
                try:
                    # 獲取玩家位置
                    if hasattr(player, 'x') and hasattr(player, 'y'):
                        player_position = [float(player.x), float(player.y)]
                    elif hasattr(player, 'position'):
                        pos = player.position
                        if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                            player_position = [float(pos[0]), float(pos[1])]
                    
                    # 獲取玩家血量
                    if hasattr(player, 'health'):
                        player_health = int(player.health)
                    
                    # 獲取玩家金錢
                    if hasattr(player, 'money'):
                        player_money = int(player.money)
                        
                    print(f"已收集玩家資料: 位置={player_position}, 血量={player_health}, 金錢={player_money}")
                    
                except Exception as e:
                    print(f"收集玩家資料時發生錯誤: {e}")
            
            # 如果有提供時間管理器，使用實際時間
            if time_manager:
                try:
                    game_time = time_manager.get_time_string()
                    print(f"已收集時間資料: {game_time}")
                except Exception as e:
                    print(f"收集時間資料時發生錯誤: {e}")
            
            # 建立存檔資料
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "player_position": player_position,
                "player_health": player_health,
                "player_money": player_money,
                "game_time": game_time,
                "weather": self.current_weather
            }
            
            # 確保存檔目錄存在
            save_dir = os.path.dirname(self.save_file)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 先寫入臨時檔案，再重新命名，避免存檔過程中斷導致檔案損壞
            temp_file = self.save_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            # 如果寫入成功，重新命名為正式檔案
            if os.path.exists(temp_file):
                if os.path.exists(self.save_file):
                    os.remove(self.save_file)
                os.rename(temp_file, self.save_file)
            
            self.current_save_data = save_data
            print(f"遊戲已保存到 {self.save_file}")
            print(f"存檔內容: {save_data}")
            
        except (OSError, IOError) as e:
            print(f"檔案操作失敗: {e}")
        except json.JSONEncodeError as e:
            print(f"JSON 編碼失敗: {e}")
        except Exception as e:
            print(f"保存遊戲失敗: {e}")
            # 清理臨時檔案
            temp_file = self.save_file + ".tmp"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def load_game(self):
        """
        讀取遊戲狀態\n
        \n
        回傳:\n
        dict: 載入的存檔資料，如果載入失敗則回傳 None\n
        """
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                # 驗證存檔數據的完整性
                required_fields = ['timestamp', 'weather']
                for field in required_fields:
                    if field not in save_data:
                        print(f"存檔檔案缺少必要欄位: {field}")
                        return None
                
                self.current_save_data = save_data
                self.current_weather = save_data.get("weather", "☀️ 晴朗")
                
                print(f"遊戲已從 {self.save_file} 讀取")
                print(f"存檔時間: {save_data.get('timestamp', '未知')}")
                
                return save_data
                
            else:
                print("沒有找到存檔檔案")
                return None
                
        except (OSError, IOError) as e:
            print(f"檔案讀取失敗: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"存檔檔案格式錯誤: {e}")
            return None
        except Exception as e:
            print(f"讀取遊戲失敗: {e}")
            return None

    def change_weather(self):
        """
        切換天氣\n
        """
        try:
            current_index = self.weather_conditions.index(self.current_weather)
            next_index = (current_index + 1) % len(self.weather_conditions)
            self.current_weather = self.weather_conditions[next_index]
            print(f"天氣變更為: {self.current_weather}")
        except (ValueError, IndexError) as e:
            print(f"天氣切換失敗: {e}")
            # 如果出現問題，重設為預設天氣
            self.current_weather = "☀️ 晴朗"

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
        
        try:
            # 計算位置（右下角）
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            self.phone_x = max(0, screen_width - self.phone_width - 20)
            self.phone_y = max(0, screen_height - self.phone_height - 20)
            
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
            
            # 安全繪製標題
            if self.font_manager:
                try:
                    title_font = self.font_manager.get_font(24)
                    title_text = title_font.render("📱 智慧手機", True, self.accent_color)
                    title_x = self.phone_x + (self.phone_width - title_text.get_width()) // 2
                    title_y = self.phone_y + 15
                    screen.blit(title_text, (title_x, title_y))
                except Exception as e:
                    print(f"標題渲染失敗: {e}")
                    # 使用預設字體作為備用
                    try:
                        fallback_font = pygame.font.Font(None, 24)
                        title_text = fallback_font.render("智慧手機", True, self.accent_color)
                        title_x = self.phone_x + (self.phone_width - title_text.get_width()) // 2
                        title_y = self.phone_y + 15
                        screen.blit(title_text, (title_x, title_y))
                    except:
                        pass  # 如果連備用字體都失敗，就跳過標題
            
            # 繪製時間資訊
            content_y = self.phone_y + 65  # 調整起始位置
            
            # 安全繪製內容
            if self.font_manager:
                try:
                    content_font = self.font_manager.get_font(16)
                    
                    # 當前時間
                    if time_manager:
                        time_text = f"🕐 時間: {time_manager.get_time_string()}"
                        date_text = f"📅 日期: {time_manager._get_day_name()}"
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
                        save_time = str(self.current_save_data.get('timestamp', '無'))[:19]  # 確保轉換為字串
                        save_text = f"💾 上次存檔: {save_time}"
                    else:
                        save_text = "💾 尚未存檔"
                    
                    save_surface = content_font.render(save_text, True, self.text_color)
                    screen.blit(save_surface, (self.phone_x + 20, content_y))
                    
                except Exception as e:
                    print(f"內容渲染失敗: {e}")
                    # 如果內容渲染失敗，至少確保按鈕能正常顯示
                    pass
            
            # 繪製按鈕
            button_y = self.phone_y + 200
            self._draw_button(screen, "💾 保存遊戲", self.phone_x + self.button_margin, button_y)
            
            button_y += self.button_height + self.button_margin
            self._draw_button(screen, "📂 讀取遊戲", self.phone_x + self.button_margin, button_y)
            
            button_y += self.button_height + self.button_margin
            self._draw_button(screen, f"🌤️ 切換天氣", self.phone_x + self.button_margin, button_y)
            
            # 提示文字
            if self.font_manager:
                try:
                    hint_y = self.phone_y + self.phone_height - 40
                    hint_font = self.font_manager.get_font(12)
                    hint_text = "點擊外部區域關閉手機"
                    hint_surface = hint_font.render(hint_text, True, (180, 180, 180))
                    hint_x = self.phone_x + (self.phone_width - hint_surface.get_width()) // 2
                    screen.blit(hint_surface, (hint_x, hint_y))
                except Exception as e:
                    print(f"提示文字渲染失敗: {e}")
            
        except Exception as e:
            print(f"手機UI繪製失敗: {e}")
            # 如果繪製失敗，隱藏手機UI以避免持續錯誤
            self.is_visible = False

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
        try:
            button_width = self.phone_width - 2 * self.button_margin
            
            # 繪製按鈕背景
            button_rect = pygame.Rect(x, y, button_width, self.button_height)
            pygame.draw.rect(screen, self.button_color, button_rect)
            pygame.draw.rect(screen, self.border_color, button_rect, 2)
            
            # 繪製按鈕文字
            if self.font_manager:
                try:
                    button_font = self.font_manager.get_font(14)
                    text_surface = button_font.render(text, True, self.button_text_color)
                except Exception as e:
                    print(f"按鈕字體渲染失敗: {e}")
                    # 使用預設字體作為備用
                    try:
                        fallback_font = pygame.font.Font(None, 14)
                        # 移除emoji，只保留文字部分
                        clean_text = text.split(' ', 1)[-1] if ' ' in text else text
                        text_surface = fallback_font.render(clean_text, True, self.button_text_color)
                    except Exception as e2:
                        print(f"備用字體也失敗: {e2}")
                        return  # 如果都失敗，只繪製按鈕背景
            else:
                # 如果沒有字體管理器，使用pygame預設字體
                try:
                    default_font = pygame.font.Font(None, 14)
                    clean_text = text.split(' ', 1)[-1] if ' ' in text else text
                    text_surface = default_font.render(clean_text, True, self.button_text_color)
                except Exception as e:
                    print(f"預設字體渲染失敗: {e}")
                    return
            
            # 置中繪製文字
            try:
                text_x = x + (button_width - text_surface.get_width()) // 2
                text_y = y + (self.button_height - text_surface.get_height()) // 2
                screen.blit(text_surface, (text_x, text_y))
            except Exception as e:
                print(f"文字繪製失敗: {e}")
                
        except Exception as e:
            print(f"按鈕繪製失敗: {e}")

    def set_player_data(self, player):
        """
        設定玩家資料（用於存檔）\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        # 這個方法用於從外部設定玩家資料
        pass

    @staticmethod
    def check_save_exists():
        """
        檢查是否存在存檔檔案\n
        \n
        回傳:\n
        bool: 如果存檔檔案存在且有效則回傳 True\n
        """
        try:
            # 建立存檔路徑
            save_dir = os.path.join(os.getcwd(), "saves")
            save_file = os.path.join(save_dir, "game_save.json")
            
            if os.path.exists(save_file):
                # 嘗試讀取並驗證存檔格式
                with open(save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                # 檢查基本欄位是否存在
                required_fields = ['timestamp', 'weather']
                for field in required_fields:
                    if field not in save_data:
                        print(f"存檔檔案缺少必要欄位: {field}")
                        return False
                
                return True
            
            return False
            
        except (OSError, IOError, json.JSONDecodeError) as e:
            print(f"檢查存檔檔案時發生錯誤: {e}")
            return False
        except Exception as e:
            print(f"檢查存檔時發生未知錯誤: {e}")
            return False

    @staticmethod
    def load_save_data():
        """
        載入存檔資料（靜態方法，用於遊戲啟動時載入）\n
        \n
        回傳:\n
        dict: 載入的存檔資料，如果載入失敗則回傳 None\n
        """
        try:
            # 建立存檔路徑
            save_dir = os.path.join(os.getcwd(), "saves")
            save_file = os.path.join(save_dir, "game_save.json")
            
            if os.path.exists(save_file):
                with open(save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                # 驗證存檔數據的完整性
                required_fields = ['timestamp', 'weather']
                for field in required_fields:
                    if field not in save_data:
                        print(f"存檔檔案缺少必要欄位: {field}")
                        return None
                
                print(f"成功載入存檔，存檔時間: {save_data.get('timestamp', '未知')}")
                return save_data
            
            return None
            
        except (OSError, IOError) as e:
            print(f"檔案讀取失敗: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"存檔檔案格式錯誤: {e}")
            return None
        except Exception as e:
            print(f"載入存檔失敗: {e}")
            return None

    def get_save_data(self):
        """
        獲取存檔資料\n
        \n
        回傳:\n
        dict: 存檔資料\n
        """
        return self.current_save_data