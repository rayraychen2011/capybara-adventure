######################載入套件######################
import pygame
from src.utils.font_manager import get_font_manager
from config.settings import *


######################時間顯示 UI 元件######################
class TimeDisplayUI:
    """
    時間顯示 UI 元件 - 在遊戲畫面上顯示時間資訊\n
    \n
    提供美觀的時間資訊顯示，包括：\n
    1. 當前時間（時:分）\n
    2. 日期資訊（第X天 星期X）\n
    3. 工作日/休息日狀態\n
    4. 時段提示（早晨、中午、傍晚等）\n
    \n
    支援多種顯示風格和位置設定\n
    """

    def __init__(self, position="top_right", style="compact"):
        """
        初始化時間顯示 UI\n
        \n
        參數:\n
        position (str): 顯示位置 ("top_left", "top_right", "bottom_left", "bottom_right")\n
        style (str): 顯示風格 ("compact", "detailed", "minimal")\n
        """
        self.position = position
        self.style = style

        # 獲取字體管理器
        self.font_manager = get_font_manager()

        # 設定字體大小
        self.time_font_size = UI_FONT_SIZE + 4  # 時間用稍大的字體
        self.info_font_size = UI_FONT_SIZE  # 資訊用正常字體
        self.small_font_size = UI_FONT_SIZE - 4  # 小字體

        # UI 元素設定
        self.background_color = (0, 0, 0, 180)  # 半透明黑色背景
        self.text_color = (255, 255, 255)  # 白色文字
        self.accent_color = (255, 215, 0)  # 金色強調色
        self.work_day_color = (255, 100, 100)  # 工作日紅色
        self.rest_day_color = (100, 255, 100)  # 休息日綠色

        # 顯示位置設定
        self.padding = 15  # 邊距
        self.line_spacing = 5  # 行距
        self.panel_padding = 12  # 面板內邊距

        # 計算顯示位置
        self._calculate_position()

        # 動畫效果
        self.fade_alpha = 255
        self.pulse_timer = 0.0

        print(f"時間顯示 UI 初始化完成 - 位置: {position}, 風格: {style}")

    def _calculate_position(self):
        """
        根據設定計算顯示位置\n
        """
        if self.position == "top_left":
            self.anchor_x = self.padding
            self.anchor_y = self.padding
        elif self.position == "top_right":
            self.anchor_x = SCREEN_WIDTH - self.padding
            self.anchor_y = self.padding
        elif self.position == "bottom_left":
            self.anchor_x = self.padding
            self.anchor_y = SCREEN_HEIGHT - self.padding
        elif self.position == "bottom_right":
            self.anchor_x = SCREEN_WIDTH - self.padding
            self.anchor_y = SCREEN_HEIGHT - self.padding
        else:
            # 預設右上角
            self.anchor_x = SCREEN_WIDTH - self.padding
            self.anchor_y = self.padding

    def update(self, dt):
        """
        更新 UI 狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新脈動動畫
        self.pulse_timer += dt
        if self.pulse_timer > 2 * 3.14159:  # 2π
            self.pulse_timer = 0.0

    def draw(self, screen, time_manager):
        """
        繪製時間顯示 UI\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        time_manager (TimeManager): 時間管理器實例\n
        """
        if self.style == "compact":
            self._draw_compact_style(screen, time_manager)
        elif self.style == "detailed":
            self._draw_detailed_style(screen, time_manager)
        elif self.style == "minimal":
            self._draw_minimal_style(screen, time_manager)

    def _draw_compact_style(self, screen, time_manager):
        """
        繪製緊湊風格的時間顯示\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        time_manager (TimeManager): 時間管理器實例\n
        """
        # 準備顯示文字
        time_text = time_manager.get_time_string()
        date_text = time_manager.get_date_string()

        # 獲取字體
        time_font = self.font_manager.get_font(self.time_font_size)
        info_font = self.font_manager.get_font(self.info_font_size)

        # 渲染文字
        time_surface = time_font.render(time_text, True, self.text_color)
        date_surface = info_font.render(date_text, True, self.text_color)

        # 計算面板尺寸
        panel_width = (
            max(time_surface.get_width(), date_surface.get_width())
            + self.panel_padding * 2
        )
        panel_height = (
            time_surface.get_height()
            + date_surface.get_height()
            + self.line_spacing
            + self.panel_padding * 2
        )

        # 計算面板位置
        if "right" in self.position:
            panel_x = self.anchor_x - panel_width
        else:
            panel_x = self.anchor_x

        if "bottom" in self.position:
            panel_y = self.anchor_y - panel_height
        else:
            panel_y = self.anchor_y

        # 繪製半透明背景
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.background_color)
        screen.blit(panel_surface, (panel_x, panel_y))

        # 繪製邊框
        pygame.draw.rect(
            screen, self.accent_color, (panel_x, panel_y, panel_width, panel_height), 2
        )

        # 繪製時間文字
        time_x = panel_x + self.panel_padding
        time_y = panel_y + self.panel_padding
        screen.blit(time_surface, (time_x, time_y))

        # 繪製日期文字
        date_x = panel_x + self.panel_padding
        date_y = time_y + time_surface.get_height() + self.line_spacing
        screen.blit(date_surface, (date_x, date_y))

    def _draw_detailed_style(self, screen, time_manager):
        """
        繪製詳細風格的時間顯示\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        time_manager (TimeManager): 時間管理器實例\n
        """
        # 準備顯示文字
        time_text = time_manager.get_time_string()
        date_text = time_manager.get_date_string()

        # 時段資訊
        time_of_day = time_manager.get_time_of_day()
        time_of_day_names = {
            "dawn": "🌅 黎明",
            "morning": "☀️ 早晨",
            "noon": "🌞 中午",
            "afternoon": "🌤️ 下午",
            "evening": "🌆 傍晚",
            "night": "🌙 夜晚",
        }
        time_period_text = time_of_day_names.get(time_of_day.value, "⏰ 未知時段")

        # 狀態資訊
        status_texts = []
        if time_manager.is_work_time():
            status_texts.append("💼 工作時間")
        elif time_manager.is_work_day:
            status_texts.append("📅 工作日")
        else:
            status_texts.append("🎉 休息日")

        if time_manager.is_shop_hours():
            status_texts.append("🏪 商店營業中")
        else:
            status_texts.append("🔒 商店休息中")

        # 獲取字體
        time_font = self.font_manager.get_font(self.time_font_size)
        info_font = self.font_manager.get_font(self.info_font_size)
        small_font = self.font_manager.get_font(self.small_font_size)

        # 渲染所有文字
        text_surfaces = []
        text_surfaces.append(
            ("time", time_font.render(time_text, True, self.accent_color))
        )
        text_surfaces.append(
            ("date", info_font.render(date_text, True, self.text_color))
        )
        text_surfaces.append(
            ("period", info_font.render(time_period_text, True, self.text_color))
        )

        for status_text in status_texts:
            color = (
                self.work_day_color
                if "工作" in status_text
                else self.rest_day_color if "休息" in status_text else self.text_color
            )
            text_surfaces.append(
                ("status", small_font.render(status_text, True, color))
            )

        # 計算面板尺寸
        panel_width = (
            max(surface[1].get_width() for surface in text_surfaces)
            + self.panel_padding * 2
        )
        panel_height = (
            sum(surface[1].get_height() for surface in text_surfaces)
            + self.line_spacing * (len(text_surfaces) - 1)
            + self.panel_padding * 2
        )

        # 計算面板位置
        if "right" in self.position:
            panel_x = self.anchor_x - panel_width
        else:
            panel_x = self.anchor_x

        if "bottom" in self.position:
            panel_y = self.anchor_y - panel_height
        else:
            panel_y = self.anchor_y

        # 繪製半透明背景
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.background_color)
        screen.blit(panel_surface, (panel_x, panel_y))

        # 繪製邊框
        pygame.draw.rect(
            screen, self.accent_color, (panel_x, panel_y, panel_width, panel_height), 2
        )

        # 繪製所有文字
        current_y = panel_y + self.panel_padding
        for text_type, surface in text_surfaces:
            text_x = panel_x + self.panel_padding
            screen.blit(surface, (text_x, current_y))
            current_y += surface.get_height() + self.line_spacing

    def _draw_minimal_style(self, screen, time_manager):
        """
        繪製極簡風格的時間顯示\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        time_manager (TimeManager): 時間管理器實例\n
        """
        # 只顯示時間
        time_text = time_manager.get_time_string()

        # 獲取字體
        time_font = self.font_manager.get_font(self.time_font_size)

        # 渲染文字
        time_surface = time_font.render(time_text, True, self.accent_color)

        # 計算位置
        if "right" in self.position:
            text_x = self.anchor_x - time_surface.get_width()
        else:
            text_x = self.anchor_x

        if "bottom" in self.position:
            text_y = self.anchor_y - time_surface.get_height()
        else:
            text_y = self.anchor_y

        # 繪製文字陰影
        shadow_surface = time_font.render(time_text, True, (0, 0, 0))
        screen.blit(shadow_surface, (text_x + 2, text_y + 2))

        # 繪製主文字
        screen.blit(time_surface, (text_x, text_y))

    def set_position(self, position):
        """
        設定顯示位置\n
        \n
        參數:\n
        position (str): 新的顯示位置\n
        """
        self.position = position
        self._calculate_position()
        print(f"時間顯示位置變更為: {position}")

    def set_style(self, style):
        """
        設定顯示風格\n
        \n
        參數:\n
        style (str): 新的顯示風格\n
        """
        self.style = style
        print(f"時間顯示風格變更為: {style}")

    def set_fade_alpha(self, alpha):
        """
        設定透明度\n
        \n
        參數:\n
        alpha (int): 透明度值 (0-255)\n
        """
        self.fade_alpha = max(0, min(255, alpha))

    def toggle_visibility(self):
        """
        切換顯示/隱藏狀態\n
        \n
        回傳:\n
        bool: 切換後的顯示狀態\n
        """
        if self.fade_alpha > 0:
            self.fade_alpha = 0
            return False
        else:
            self.fade_alpha = 255
            return True
