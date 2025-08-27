######################載入套件######################
import pygame
from typing import Dict, List, Tuple, Optional

from ..utils.font_manager import get_font_manager
from ..systems.power_system import PowerStatus


######################電力 UI 顯示######################
class PowerDisplayUI:
    """
    電力系統 UI 顯示元件 - 顯示電力狀態與統計資料\n
    \n
    功能說明:\n
    1. 顯示全域電力狀態指示器\n
    2. 顯示電力統計資料（供電區域數、工人狀態等）\n
    3. 顯示電力網格地圖（選擇性）\n
    4. 支援多種顯示模式與主題\n
    \n
    設計特色:\n
    - 簡潔的狀態指示器\n
    - 詳細的統計資料面板\n
    - 可視化的電力網格地圖\n
    - 支援繁體中文顯示\n
    """

    def __init__(self, power_manager):
        """
        初始化電力 UI 顯示器\n
        \n
        參數:\n
        power_manager (PowerManager): 電力管理器實例\n
        """
        self.power_manager = power_manager
        self.font_manager = get_font_manager()

        # UI 設定
        self.show_detailed_stats = False  # 是否顯示詳細統計
        self.show_grid_map = False  # 是否顯示電力網格地圖

        # 字體設定
        self.title_font = self.font_manager.get_font(24)
        self.content_font = self.font_manager.get_font(18)
        self.small_font = self.font_manager.get_font(14)

        # 顏色設定
        self.colors = {
            "normal": (50, 255, 50),  # 正常供電 - 綠色
            "outage": (255, 50, 50),  # 停電 - 紅色
            "overload": (255, 255, 50),  # 超載 - 黃色
            "maintenance": (100, 100, 255),  # 維修 - 藍色
            "background": (0, 0, 0, 180),  # 半透明黑背景
            "text": (255, 255, 255),  # 白色文字
            "border": (200, 200, 200),  # 邊框顏色
        }

        # UI 位置設定
        self.indicator_position = (20, 20)  # 狀態指示器位置
        self.stats_position = (20, 80)  # 統計面板位置
        self.grid_position = (300, 100)  # 網格地圖位置

        print("電力 UI 顯示器初始化完成")

    def draw_power_indicator(self, screen: pygame.Surface):
        """
        繪製電力狀態指示器 - 顯示當前電力系統總體狀態\n
        \n
        在螢幕左上角顯示簡潔的電力狀態圖示和文字\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面\n
        """
        # 取得當前電力狀態
        status = self.power_manager.global_power_status
        stats = self.power_manager.get_power_stats()

        # 根據狀態選擇顏色
        if status == PowerStatus.NORMAL:
            color = self.colors["normal"]
            status_text = "電力正常"
        elif status == PowerStatus.OUTAGE:
            color = self.colors["outage"]
            status_text = "大範圍停電"
        elif status == PowerStatus.OVERLOAD:
            color = self.colors["overload"]
            status_text = "電力超載"
        else:
            color = self.colors["maintenance"]
            status_text = "系統維修"

        # 繪製狀態指示器背景
        indicator_rect = pygame.Rect(
            self.indicator_position[0] - 5, self.indicator_position[1] - 5, 200, 50
        )

        # 半透明背景
        bg_surface = pygame.Surface((indicator_rect.width, indicator_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        screen.blit(bg_surface, indicator_rect.topleft)

        # 邊框
        pygame.draw.rect(screen, self.colors["border"], indicator_rect, 2)

        # 狀態圓點
        circle_pos = (self.indicator_position[0] + 15, self.indicator_position[1] + 15)
        pygame.draw.circle(screen, color, circle_pos, 8)
        pygame.draw.circle(screen, self.colors["border"], circle_pos, 8, 2)

        # 狀態文字
        status_surface = self.content_font.render(
            status_text, True, self.colors["text"]
        )
        text_pos = (self.indicator_position[0] + 35, self.indicator_position[1] + 5)
        screen.blit(status_surface, text_pos)

        # 電力效率
        efficiency = stats.get("power_efficiency", 1.0)
        efficiency_text = f"效率：{efficiency:.1%}"
        efficiency_surface = self.small_font.render(
            efficiency_text, True, self.colors["text"]
        )
        efficiency_pos = (
            self.indicator_position[0] + 35,
            self.indicator_position[1] + 25,
        )
        screen.blit(efficiency_surface, efficiency_pos)

    def draw_power_stats(self, screen: pygame.Surface):
        """
        繪製電力統計面板 - 顯示詳細的電力系統數據\n
        \n
        顯示供電區域數、工人狀態、停電次數等統計資料\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面\n
        """
        if not self.show_detailed_stats:
            return

        stats = self.power_manager.get_power_stats()

        # 統計資料文字
        stats_lines = [
            "電力系統統計",
            f"供電區域：{stats.get('areas_with_power', 0)}/30",
            f"在職工人：{stats.get('workers_on_duty', 0)}/30",
            f"總停電次數：{stats.get('total_outages', 0)}",
            f"系統效率：{stats.get('power_efficiency', 1.0):.1%}",
        ]

        # 計算面板大小
        panel_width = 200
        panel_height = len(stats_lines) * 25 + 20

        panel_rect = pygame.Rect(
            self.stats_position[0], self.stats_position[1], panel_width, panel_height
        )

        # 繪製面板背景
        bg_surface = pygame.Surface((panel_width, panel_height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        screen.blit(bg_surface, panel_rect.topleft)

        # 繪製邊框
        pygame.draw.rect(screen, self.colors["border"], panel_rect, 2)

        # 繪製統計文字
        for i, line in enumerate(stats_lines):
            if i == 0:  # 標題使用較大字體
                text_surface = self.content_font.render(line, True, self.colors["text"])
            else:
                text_surface = self.small_font.render(line, True, self.colors["text"])

            text_pos = (
                self.stats_position[0] + 10,
                self.stats_position[1] + 10 + i * 25,
            )
            screen.blit(text_surface, text_pos)

    def draw_power_grid_map(self, screen: pygame.Surface):
        """
        繪製電力網格地圖 - 視覺化顯示 30 個電力區域的狀態\n
        \n
        以小方格顯示每個區域的電力狀態，提供整體電力分布概覽\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面\n
        """
        if not self.show_grid_map:
            return

        areas_info = self.power_manager.get_all_areas_info()

        # 網格設定
        grid_cols = 6
        grid_rows = 5
        cell_size = 20
        cell_spacing = 2

        # 計算網格總大小
        grid_width = grid_cols * (cell_size + cell_spacing) - cell_spacing
        grid_height = grid_rows * (cell_size + cell_spacing) - cell_spacing

        # 繪製網格背景
        grid_rect = pygame.Rect(
            self.grid_position[0] - 10,
            self.grid_position[1] - 30,
            grid_width + 20,
            grid_height + 40,
        )

        bg_surface = pygame.Surface((grid_rect.width, grid_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        screen.blit(bg_surface, grid_rect.topleft)

        pygame.draw.rect(screen, self.colors["border"], grid_rect, 2)

        # 繪製標題
        title_surface = self.content_font.render("電力網格", True, self.colors["text"])
        title_pos = (self.grid_position[0], self.grid_position[1] - 25)
        screen.blit(title_surface, title_pos)

        # 繪製各區域狀態
        for row in range(grid_rows):
            for col in range(grid_cols):
                area_id = row * grid_cols + col + 1

                # 計算方格位置
                cell_x = self.grid_position[0] + col * (cell_size + cell_spacing)
                cell_y = self.grid_position[1] + row * (cell_size + cell_spacing)
                cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)

                # 根據區域狀態選擇顏色
                if area_id in areas_info:
                    area_status = areas_info[area_id]["status"]

                    if area_status == PowerStatus.NORMAL:
                        color = self.colors["normal"]
                    elif area_status == PowerStatus.OUTAGE:
                        color = self.colors["outage"]
                    elif area_status == PowerStatus.OVERLOAD:
                        color = self.colors["overload"]
                    else:
                        color = self.colors["maintenance"]
                else:
                    color = (100, 100, 100)  # 灰色表示未初始化

                # 繪製方格
                pygame.draw.rect(screen, color, cell_rect)
                pygame.draw.rect(screen, self.colors["border"], cell_rect, 1)

                # 顯示區域 ID（小字）
                if cell_size >= 16:  # 只有方格夠大時才顯示 ID
                    id_text = str(area_id)
                    id_surface = self.small_font.render(id_text, True, (0, 0, 0))
                    id_rect = id_surface.get_rect()
                    id_rect.center = cell_rect.center
                    screen.blit(id_surface, id_rect)

    def draw_power_legend(self, screen: pygame.Surface):
        """
        繪製電力狀態圖例 - 說明各種顏色代表的意義\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面\n
        """
        if not self.show_grid_map:
            return

        legend_items = [
            ("正常供電", self.colors["normal"]),
            ("停電", self.colors["outage"]),
            ("超載", self.colors["overload"]),
            ("維修中", self.colors["maintenance"]),
        ]

        # 圖例位置（在網格地圖下方）
        legend_x = self.grid_position[0]
        legend_y = self.grid_position[1] + 120

        for i, (label, color) in enumerate(legend_items):
            # 顏色方塊
            color_rect = pygame.Rect(legend_x, legend_y + i * 20, 15, 15)
            pygame.draw.rect(screen, color, color_rect)
            pygame.draw.rect(screen, self.colors["border"], color_rect, 1)

            # 標籤文字
            label_surface = self.small_font.render(label, True, self.colors["text"])
            label_pos = (legend_x + 20, legend_y + i * 20)
            screen.blit(label_surface, label_pos)

    def toggle_detailed_stats(self):
        """
        切換詳細統計面板的顯示狀態\n
        """
        self.show_detailed_stats = not self.show_detailed_stats

    def toggle_grid_map(self):
        """
        切換電力網格地圖的顯示狀態\n
        """
        self.show_grid_map = not self.show_grid_map

    def draw(self, screen: pygame.Surface):
        """
        繪製所有電力 UI 元素\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面\n
        """
        # 總是顯示狀態指示器
        self.draw_power_indicator(screen)

        # 根據設定顯示其他元素
        if self.show_detailed_stats:
            self.draw_power_stats(screen)

        if self.show_grid_map:
            self.draw_power_grid_map(screen)
            self.draw_power_legend(screen)

    def handle_key_input(self, key: int):
        """
        處理鍵盤輸入以切換 UI 顯示模式\n
        \n
        參數:\n
        key (int): 按鍵碼\n
        """
        if key == pygame.K_F10:  # F10 切換詳細統計
            self.toggle_detailed_stats()
        elif key == pygame.K_F12:  # F12 切換網格地圖
            self.toggle_grid_map()

    def get_help_text(self) -> List[str]:
        """
        取得 UI 操作說明\n
        \n
        回傳:\n
        List[str]: 操作說明文字列表\n
        """
        return [
            "電力系統 UI 操作：",
            "F10 - 切換詳細統計面板",
            "F12 - 切換電力網格地圖",
            "",
            "狀態顏色說明：",
            "綠色 - 正常供電",
            "紅色 - 停電",
            "黃色 - 電力超載",
            "藍色 - 系統維修",
        ]
