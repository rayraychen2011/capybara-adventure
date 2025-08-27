######################載入套件######################
import pygame
from src.utils.font_manager import get_font_manager
from config.settings import *


######################NPC 資訊顯示器######################
class NPCInfoUI:
    """
    NPC 資訊顯示器 - 顯示 NPC 狀態清單\n
    \n
    提供一個從上到下的清單，顯示：\n
    1. NPC 姓名\n
    2. 當前位置\n
    3. 職業\n
    4. 當前狀態和活動\n
    5. 下一個活動\n
    \n
    支援捲動瀏覽和搜尋功能\n
    """

    def __init__(self):
        """
        初始化 NPC 資訊顯示器\n
        """
        self.font_manager = get_font_manager()

        # UI 尺寸和位置
        self.width = 500
        self.height = SCREEN_HEIGHT - 100
        self.x = 20
        self.y = 50

        # 字體設定
        self.title_font = self.font_manager.get_font(24)
        self.header_font = self.font_manager.get_font(18)
        self.content_font = self.font_manager.get_font(14)
        self.small_font = self.font_manager.get_font(12)

        # 顏色設定
        self.bg_color = (0, 0, 0, 180)  # 半透明黑色背景
        self.border_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.header_color = (200, 200, 0)
        self.accent_color = (0, 200, 255)

        # 捲動設定
        self.scroll_offset = 0
        self.max_visible_items = 25
        self.item_height = 22

        # 當前顯示的 NPC 清單
        self.npc_list = []

    def update_npc_list(self, npc_status_list):
        """
        更新要顯示的 NPC 清單\n
        \n
        參數:\n
        npc_status_list (list): NPC 狀態資訊清單\n
        """
        self.npc_list = npc_status_list
        # 重置捲動位置
        if len(self.npc_list) <= self.max_visible_items:
            self.scroll_offset = 0

    def handle_scroll(self, direction):
        """
        處理捲動\n
        \n
        參數:\n
        direction (int): 捲動方向 (1向下, -1向上)\n
        """
        if len(self.npc_list) <= self.max_visible_items:
            return

        self.scroll_offset += direction

        # 限制捲動範圍
        max_scroll = len(self.npc_list) - self.max_visible_items
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def draw(self, screen):
        """
        繪製 NPC 資訊清單\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        if not self.npc_list:
            return

        # 創建半透明背景表面
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        screen.blit(bg_surface, (self.x, self.y))

        # 繪製邊框
        pygame.draw.rect(
            screen, self.border_color, (self.x, self.y, self.width, self.height), 2
        )

        # 繪製標題
        title_text = f"NPC 狀態清單 ({len(self.npc_list)} 個)"
        title_surface = self.title_font.render(title_text, True, self.header_color)
        screen.blit(title_surface, (self.x + 10, self.y + 10))

        # 繪製欄位標題
        headers_y = self.y + 45
        self._draw_headers(screen, headers_y)

        # 繪製 NPC 清單
        content_start_y = headers_y + 25
        self._draw_npc_list(screen, content_start_y)

        # 繪製捲動提示
        if len(self.npc_list) > self.max_visible_items:
            self._draw_scroll_indicators(screen)

    def _draw_headers(self, screen, y):
        """
        繪製欄位標題\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        y (int): Y 座標\n
        """
        headers = [
            ("姓名", 10),
            ("職業", 120),
            ("位置", 220),
            ("狀態", 320),
            ("活動", 400),
        ]

        for header_text, x_offset in headers:
            header_surface = self.header_font.render(
                header_text, True, self.accent_color
            )
            screen.blit(header_surface, (self.x + x_offset, y))

        # 繪製分隔線
        line_y = y + 20
        pygame.draw.line(
            screen,
            self.border_color,
            (self.x + 5, line_y),
            (self.x + self.width - 5, line_y),
        )

    def _draw_npc_list(self, screen, start_y):
        """
        繪製 NPC 清單內容\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        start_y (int): 起始 Y 座標\n
        """
        visible_npcs = self.npc_list[
            self.scroll_offset : self.scroll_offset + self.max_visible_items
        ]

        for i, npc_info in enumerate(visible_npcs):
            y = start_y + i * self.item_height

            # 交替背景色
            if i % 2 == 1:
                item_bg = pygame.Surface(
                    (self.width - 10, self.item_height), pygame.SRCALPHA
                )
                item_bg.fill((255, 255, 255, 20))
                screen.blit(item_bg, (self.x + 5, y - 2))

            # 決定文字顏色（受傷或隱藏的 NPC 用不同顏色）
            text_color = self.text_color
            if npc_info.get("is_injured", False):
                text_color = (255, 100, 100)  # 紅色表示受傷
            elif npc_info.get("is_hidden", False):
                text_color = (150, 150, 150)  # 灰色表示隱藏

            # 繪製各欄位
            self._draw_field(screen, npc_info["name"], self.x + 10, y, text_color)
            self._draw_field(
                screen, npc_info["profession"], self.x + 120, y, text_color
            )
            self._draw_field(screen, npc_info["position"], self.x + 220, y, text_color)
            self._draw_field(
                screen, npc_info["current_state"], self.x + 320, y, text_color
            )

            # 活動描述可能比較長，需要截短
            activity = npc_info["current_activity"]
            if len(activity) > 15:
                activity = activity[:12] + "..."
            self._draw_field(screen, activity, self.x + 400, y, text_color)

    def _draw_field(self, screen, text, x, y, color):
        """
        繪製單個欄位\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        text (str): 文字內容\n
        x (int): X 座標\n
        y (int): Y 座標\n
        color (tuple): 文字顏色\n
        """
        text_surface = self.content_font.render(str(text), True, color)
        screen.blit(text_surface, (x, y))

    def _draw_scroll_indicators(self, screen):
        """
        繪製捲動指示器\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 捲動條背景
        scrollbar_x = self.x + self.width - 15
        scrollbar_y = self.y + 70
        scrollbar_height = self.height - 90

        pygame.draw.rect(
            screen, (50, 50, 50), (scrollbar_x, scrollbar_y, 10, scrollbar_height)
        )

        # 捲動條把手
        if len(self.npc_list) > 0:
            handle_height = max(
                20, int(scrollbar_height * self.max_visible_items / len(self.npc_list))
            )
            handle_y = scrollbar_y + int(
                scrollbar_height * self.scroll_offset / len(self.npc_list)
            )

            pygame.draw.rect(
                screen, self.accent_color, (scrollbar_x, handle_y, 10, handle_height)
            )

        # 捲動提示文字
        scroll_info = f"{self.scroll_offset + 1}-{min(self.scroll_offset + self.max_visible_items, len(self.npc_list))} / {len(self.npc_list)}"
        info_surface = self.small_font.render(scroll_info, True, self.text_color)
        screen.blit(info_surface, (self.x + self.width - 80, self.y + self.height - 20))

    def handle_keydown(self, event):
        """
        處理鍵盤輸入\n
        \n
        參數:\n
        event (pygame.event.Event): 鍵盤事件\n
        \n
        回傳:\n
        bool: 是否處理了事件\n
        """
        if event.key == pygame.K_UP:
            self.handle_scroll(-1)
            return True
        elif event.key == pygame.K_DOWN:
            self.handle_scroll(1)
            return True
        elif event.key == pygame.K_PAGEUP:
            self.handle_scroll(-5)
            return True
        elif event.key == pygame.K_PAGEDOWN:
            self.handle_scroll(5)
            return True

        return False
