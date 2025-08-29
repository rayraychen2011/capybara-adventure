######################載入套件######################
import pygame
from config.settings import *
from src.utils.font_manager import get_font_manager

######################物件類別######################
class OperationGuideUI:
    """
    操作指南UI - 顯示遊戲操作說明\n
    \n
    此類別負責：\n
    1. 顯示遊戲控制說明\n
    2. 提供快捷鍵參考\n
    3. 系統功能介紹\n
    """
    
    def __init__(self):
        """
        初始化操作指南UI\n
        """
        self.font_manager = get_font_manager()
        self.is_visible = False
        
        # UI 尺寸設定
        self.width = 700
        self.height = 600  # 增加高度以容納更多內容
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # 背景顏色
        self.bg_color = (0, 0, 0, 200)  # 半透明黑色
        self.border_color = (255, 255, 255)
        
        # 滾動相關設定
        self.scroll_offset = 0  # 滾動偏移量
        self.line_height = 20  # 每行高度
        self.content_area_height = self.height - 80  # 內容區域高度（扣除標題和邊距）
        self.max_visible_lines = self.content_area_height // self.line_height  # 最大可見行數
        
        # 操作指南內容
        self.guide_content = [
            "🎮 遊戲操作指南",
            "",
            "📍 基本移動：",
            "  ▪ WASD 或方向鍵 - 移動角色",
            "  ▪ Shift + 移動鍵 - 奔跑",
            "",
            "🎯 互動操作：",
            "  ▪ WASD 或方向鍵 - 移動角色",
            "  ▪ Shift + 移動鍵 - 奔跑",
            "  ▪ E鍵或空格鍵 - 與物件互動",
            "  ▪ C鍵 - 與NPC對話",
            "  ▪ Q鍵 - 砍伐樹木",
            "  ▪ 滑鼠左鍵 - 點擊建築物進入商店/射擊",
            "  ▪ 滑鼠中鍵 - 召喚武器圓盤",
            "",
            "🗡️ 武器系統：",
            "  ▪ 1鍵 - 選擇槍械",
            "  ▪ 2鍵 - 選擇斧頭",
            "  ▪ 3鍵 - 空手格鬥",
            "  ▪ G鍵 - 切換武器裝備狀態",
            "",
            "📱 智慧手機系統：",
            "  ▪ P鍵 - 召喚手機介面",
            "  ▪ 手機功能：查看時間、天氣、存檔/讀檔",
            "  ▪ 點擊外部區域關閉手機",
            "",
            " NPC系統：",
            "  ▪ Tab鍵 - 顯示所有NPC狀態列表",
            "  ▪ 左鍵點擊NPC - 開啟對話視窗",
            "  ▪ 每個NPC有不同職業和對話內容",
            "",
            "🏪 建築物互動：",
            "  ▪ 槍械店 - 購買武器和子彈",
            "  ▪ 便利商店 - 購買食物回血",
            "  ▪ 路邊小販 - 隨機物品交易",
            "  ▪ 服裝店 - 更換角色外觀",
            "  ▪ 教堂 - 進入內部場景祈禱",
            "  ▪ 住宅 - 休息和存檔",
            "",
            "🦌 野生動物系統：",
            "  ▪ 稀有動物（兔子、烏龜、羊）- 獎勵30元",
            "  ▪ 超稀有動物（山獅、黑豹）- 獎勵50元",
            "  ▪ 傳奇動物（熊）- 獎勵100元",
            "  ▪ 注意：熊具有高度攻擊性，需謹慎接近",
            "",
            "🌱 蔬果園系統：",
            "  ▪ 走到蔬果園附近自動採收成熟蔬果",
            "  ▪ 每次採收獲得5元獎勵",
            "  ▪ 蔬果在下一個遊戲日重新成熟",
            "",
            "🚂 交通系統：",
            "  ▪ 點擊火車站 - 快速旅行",
            "  ▪ 數字鍵4-9 - 選擇火車站目的地",
            "  ▪ 在斑馬線通過鐵軌",
            "  ▪ 注意交通號誌",
            "",
            "🌍 地圖系統：",
            "  ▪ 右上角小地圖導航",
            "  ▪ 紅點標示玩家位置",
            "  ▪ 不同顏色代表不同地形",
            "",
            "💡 路燈系統：",
            "  ▪ 夜晚時路燈會自動點亮",
            "  ▪ 路燈照亮周圍區域",
            "",
            "⏰ 時間系統控制：",
            "  ▪ F1 - 切換時間顯示風格",
            "  ▪ F2 - 切換時間流速",
            "  ▪ F4 - 快進1小時",
            "  ▪ F5 - 快進6小時",
            "  ▪ F6 - 快進12小時",
            "  ▪ F7 - 快進24小時",
            "  ▪ F8 - 重置為早上8:00",
            "  ▪ F9 - 設定為晚上8:00",
            "",
            "🔌 電力系統：",
            "  ▪ F10 - 切換電力詳細統計",
            "  ▪ F12 - 切換電力網格地圖",
            "",
            "⚙️ 系統功能：",
            "  ▪ 0鍵或\\鍵 - 顯示/隱藏操作指南",
            "  ▪ 滑鼠滾輪 - 在操作指南中上下滾動",
            "  ▪ ESC鍵 - 暫停遊戲/返回主選單/關閉UI",
            "  ▪ F11 - 切換全螢幕",
            "  ▪ H鍵 - 顯示開發者快捷鍵幫助",
            "  ▪ 遊戲自動存檔",
            "",
            "🖱️ 滑鼠滾輪操作說明：",
            "  ▪ 操作指南顯示時可使用滾輪上下瀏覽",
            "  ▪ 小地圖顯示時可使用滾輪縮放",
            "",
            "按0鍵或\\鍵或ESC關閉此畫面"
        ]
        
        print("操作指南UI初始化完成")

    def handle_scroll(self, direction):
        """
        處理滾輪滾動事件\n
        \n
        參數:\n
        direction (int): 滾動方向 (正數向上滾動, 負數向下滾動)\n
        """
        if not self.is_visible:
            return
        
        # 計算需要滾動的行數（每次滾動3行）
        scroll_lines = 3
        self.scroll_offset -= direction * scroll_lines
        
        # 限制滾動範圍
        max_scroll = max(0, len(self.guide_content) - self.max_visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        
        print(f"操作指南滾動: offset={self.scroll_offset}, max={max_scroll}")

    def toggle_visibility(self):
        """
        切換顯示/隱藏狀態\n
        """
        self.is_visible = not self.is_visible
        if self.is_visible:
            self.scroll_offset = 0  # 顯示時重置滾動位置
        print(f"操作指南 {'顯示' if self.is_visible else '隱藏'}")

    def show(self):
        """
        顯示操作指南\n
        """
        self.is_visible = True
        self.scroll_offset = 0  # 顯示時重置滾動位置

    def hide(self):
        """
        隱藏操作指南\n
        """
        self.is_visible = False

    def handle_key_press(self, key):
        """
        處理按鍵事件\n
        \n
        參數:\n
        key: pygame按鍵常數\n
        \n
        回傳:\n
        bool: 如果處理了按鍵事件則回傳True\n
        """
        if key == pygame.K_BACKSLASH:  # 反斜線鍵
            self.toggle_visibility()
            return True
        elif key == pygame.K_ESCAPE and self.is_visible:
            self.hide()
            return True
        
        return False

    def draw(self, screen):
        """
        繪製操作指南\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        if not self.is_visible:
            return
        
        # 創建半透明背景表面
        overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay_surface.set_alpha(150)
        overlay_surface.fill((0, 0, 0))
        screen.blit(overlay_surface, (0, 0))
        
        # 繪製主窗口背景
        main_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (30, 30, 30), main_rect)
        pygame.draw.rect(screen, self.border_color, main_rect, 3)
        
        # 繪製標題（固定在頂部）
        title_line = self.guide_content[0]  # "🎮 遊戲操作指南"
        title_surface = self.font_manager.render_text(title_line, 24, (255, 215, 0))
        title_x = self.x + (self.width - title_surface.get_width()) // 2
        title_y = self.y + 15
        screen.blit(title_surface, (title_x, title_y))
        
        # 繪製滾動指示（如果需要滾動）
        if len(self.guide_content) > self.max_visible_lines:
            self._draw_scroll_indicators(screen)
        
        # 計算內容繪製區域
        content_start_y = self.y + 50  # 標題下方開始
        
        # 計算要顯示的內容範圍（跳過標題）
        content_lines = self.guide_content[1:]  # 跳過標題
        start_index = self.scroll_offset
        end_index = min(start_index + self.max_visible_lines, len(content_lines))
        visible_lines = content_lines[start_index:end_index]
        
        # 繪製可見內容
        current_y = content_start_y
        for line in visible_lines:
            if line == "":
                # 空行，減少間距
                current_y += self.line_height // 3
                continue
            
            # 根據內容類型設定顏色和字體大小
            if line.startswith(("📍", "🎯", "📦", "🦌", "🌱", "🚂", "🏠", "🌍", "💡", "⚙️", "📱", " NPC", "🏪", "🔌", "🖱️")):
                # 章節標題
                text_color = (100, 149, 237)  # 淺藍色
                font_size = 18
            elif line.startswith("  ▪"):
                # 說明項目
                text_color = (220, 220, 220)  # 淺灰色
                font_size = 14
            elif line.startswith("按0鍵或\\鍵或ESC關閉此畫面"):
                # 關閉提示
                text_color = (180, 180, 180)  # 中等灰色
                font_size = 14
            else:
                # 一般文字
                text_color = (255, 255, 255)  # 白色
                font_size = 16
            
            # 渲染文字
            text_surface = self.font_manager.render_text(line, font_size, text_color)
            
            # 計算文字位置
            if line.startswith("按0鍵或\\鍵或ESC關閉此畫面"):
                # 底部說明置中
                text_x = self.x + (self.width - text_surface.get_width()) // 2
            else:
                # 其他內容左對齊
                text_x = self.x + 20
            
            # 檢查是否超出內容區域
            if current_y + self.line_height > self.y + self.height - 30:
                break
            
            # 繪製文字
            screen.blit(text_surface, (text_x, current_y))
            current_y += self.line_height
    
    def _draw_scroll_indicators(self, screen):
        """
        繪製滾動條和滾動指示器\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 滾動條位置和尺寸
        scrollbar_x = self.x + self.width - 20
        scrollbar_y = self.y + 50
        scrollbar_width = 12
        scrollbar_height = self.height - 80
        
        # 繪製滾動條背景
        pygame.draw.rect(screen, (50, 50, 50), 
                        (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
        
        # 計算滾動手柄的位置和大小
        content_lines = len(self.guide_content) - 1  # 減去標題行
        if content_lines > self.max_visible_lines:
            handle_height = max(20, int(scrollbar_height * self.max_visible_lines / content_lines))
            handle_y = scrollbar_y + int(scrollbar_height * self.scroll_offset / content_lines)
            
            # 繪製滾動手柄
            pygame.draw.rect(screen, (150, 150, 150),
                            (scrollbar_x + 1, handle_y, scrollbar_width - 2, handle_height))
        
        # 繪製滾動提示文字
        if self.scroll_offset > 0:
            up_text = self.font_manager.render_text("↑ 向上滾動", 12, (180, 180, 180))
            screen.blit(up_text, (self.x + 20, self.y + self.height - 45))
        
        if self.scroll_offset < content_lines - self.max_visible_lines:
            down_text = self.font_manager.render_text("↓ 向下滾動", 12, (180, 180, 180))
            screen.blit(down_text, (self.x + 20, self.y + self.height - 25))

    def update(self, dt):
        """
        更新操作指南（目前無需更新邏輯）\n
        \n
        參數:\n
        dt (float): 時間增量\n
        """
        pass