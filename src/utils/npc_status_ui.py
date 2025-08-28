######################載入套件######################
import pygame
from src.utils.font_manager import get_font_manager
from config.settings import *


######################NPC狀態顯示UI######################
class NPCStatusDisplayUI:
    """
    NPC狀態顯示UI - 按TAB顯示所有NPC狀態\n
    \n
    顯示所有NPC的血量、職業和名字資訊\n
    提供友善的UI介面讓玩家了解NPC狀況\n
    """

    def __init__(self):
        """
        初始化NPC狀態顯示UI\n
        """
        self.is_visible = False
        self.font_manager = get_font_manager()
        
        # UI設定
        self.background_color = (0, 0, 0, 180)  # 半透明黑色背景
        self.text_color = (255, 255, 255)  # 白色文字
        self.header_color = (255, 255, 0)  # 黃色標題
        self.healthy_color = (0, 255, 0)  # 綠色（健康）
        self.injured_color = (255, 0, 0)  # 紅色（受傷）
        self.working_color = (0, 191, 255)  # 藍色（工作中）
        
        # UI尺寸和位置
        self.width = SCREEN_WIDTH - 100
        self.height = SCREEN_HEIGHT - 100
        self.x = 50
        self.y = 50
        
        # 滾動設定
        self.scroll_offset = 0
        self.max_scroll = 0
        self.line_height = 25
        self.items_per_page = (self.height - 80) // self.line_height  # 扣除標題空間
        
        print("📊 NPC狀態顯示UI已初始化")

    def toggle_visibility(self):
        """
        切換顯示狀態\n
        """
        self.is_visible = not self.is_visible
        self.scroll_offset = 0  # 重置滾動位置
        print(f"📊 NPC狀態顯示: {'開啟' if self.is_visible else '關閉'}")

    def show(self):
        """
        顯示NPC狀態\n
        """
        self.is_visible = True
        self.scroll_offset = 0

    def hide(self):
        """
        隱藏NPC狀態\n
        """
        self.is_visible = False

    def scroll_up(self):
        """
        向上滾動\n
        """
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def scroll_down(self):
        """
        向下滾動\n
        """
        if self.scroll_offset < self.max_scroll:
            self.scroll_offset += 1

    def handle_event(self, event):
        """
        處理輸入事件\n
        \n
        參數:\n
        event (pygame.Event): 事件物件\n
        """
        if not self.is_visible:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll_up()
            elif event.key == pygame.K_DOWN:
                self.scroll_down()
            elif event.key == pygame.K_TAB:
                self.hide()

    def update(self, dt):
        """
        更新UI狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # UI本身不需要特別的更新邏輯
        pass

    def draw(self, screen, npc_manager):
        """
        繪製NPC狀態顯示\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標\n
        npc_manager (NPCManager): NPC管理器\n
        """
        if not self.is_visible:
            return
        
        # 創建背景表面
        background_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        background_surface.fill(self.background_color)
        screen.blit(background_surface, (self.x, self.y))
        
        # 繪製邊框
        pygame.draw.rect(screen, self.text_color, (self.x, self.y, self.width, self.height), 2)
        
        # 繪製標題
        title_font = self.font_manager.get_font(UI_FONT_SIZE + 4)
        title_text = title_font.render("NPC 狀態總覽 (按↑↓滾動, TAB關閉)", True, self.header_color)
        screen.blit(title_text, (self.x + 10, self.y + 10))
        
        # 繪製統計資訊
        stats_text = self._get_statistics_text(npc_manager)
        stats_font = self.font_manager.get_font(UI_FONT_SIZE - 2)
        stats_surface = stats_font.render(stats_text, True, self.text_color)
        screen.blit(stats_surface, (self.x + 10, self.y + 40))
        
        # 繪製NPC列表
        self._draw_npc_list(screen, npc_manager)

    def _get_statistics_text(self, npc_manager):
        """
        獲取統計資訊文字\n
        \n
        參數:\n
        npc_manager (NPCManager): NPC管理器\n
        \n
        回傳:\n
        str: 統計資訊\n
        """
        if not hasattr(npc_manager, 'npcs'):
            return "無NPC資料"
        
        total_npcs = len(npc_manager.npcs)
        healthy_count = sum(1 for npc in npc_manager.npcs if not npc.is_injured)
        injured_count = total_npcs - healthy_count
        working_count = sum(1 for npc in npc_manager.npcs if hasattr(npc, 'state') and npc.state.name == 'WORKING')
        
        return f"總計: {total_npcs} | 健康: {healthy_count} | 受傷: {injured_count} | 工作中: {working_count}"

    def _draw_npc_list(self, screen, npc_manager):
        """
        繪製NPC列表\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標\n
        npc_manager (NPCManager): NPC管理器\n
        """
        if not hasattr(npc_manager, 'npcs'):
            return
        
        # 計算可顯示的NPC數量和滾動範圍
        total_npcs = len(npc_manager.npcs)
        self.max_scroll = max(0, total_npcs - self.items_per_page)
        
        # 起始Y位置
        start_y = self.y + 70
        font = self.font_manager.get_font(UI_FONT_SIZE - 4)
        
        # 顯示當前頁面的NPC
        start_index = self.scroll_offset
        end_index = min(start_index + self.items_per_page, total_npcs)
        
        for i in range(start_index, end_index):
            npc = npc_manager.npcs[i]
            y_pos = start_y + (i - start_index) * self.line_height
            
            # 準備NPC資訊
            npc_info = self._format_npc_info(npc)
            
            # 選擇顏色
            if npc.is_injured:
                text_color = self.injured_color
                status_icon = "🩹"
            elif hasattr(npc, 'state') and npc.state.name == 'WORKING':
                text_color = self.working_color
                status_icon = "🔧"
            else:
                text_color = self.healthy_color
                status_icon = "✅"
            
            # 繪製NPC資訊
            info_text = f"{status_icon} {npc_info}"
            text_surface = font.render(info_text, True, text_color)
            screen.blit(text_surface, (self.x + 15, y_pos))
        
        # 顯示滾動指示器
        if self.max_scroll > 0:
            self._draw_scroll_indicator(screen, total_npcs)

    def _format_npc_info(self, npc):
        """
        格式化NPC資訊\n
        \n
        參數:\n
        npc (NPC): NPC物件\n
        \n
        回傳:\n
        str: 格式化的資訊字串\n
        """
        # 基本資訊
        name = getattr(npc, 'name', f"NPC #{getattr(npc, 'id', 'Unknown')}")
        profession = getattr(npc, 'profession', 'Unknown').value if hasattr(getattr(npc, 'profession', None), 'value') else str(getattr(npc, 'profession', 'Unknown'))
        
        # 健康狀態
        if npc.is_injured:
            health_status = "受傷"
            if hasattr(npc, 'hospital_stay_time') and npc.hospital_stay_time > 0:
                health_status += f" (住院{npc.hospital_stay_time:.1f}小時)"
        else:
            health_status = "健康"
        
        # 工作狀態
        work_status = "未知"
        if hasattr(npc, 'state'):
            state_name = npc.state.name if hasattr(npc.state, 'name') else str(npc.state)
            work_status = {
                'WORKING': '工作中',
                'RESTING': '休息中',
                'MOVING': '移動中',
                'INJURED': '住院中',
                'IDLE': '閒置中',
                'SLEEPING': '睡覺中'
            }.get(state_name, state_name)
        
        # 位置資訊
        x, y = getattr(npc, 'x', 0), getattr(npc, 'y', 0)
        
        return f"{name} | {profession} | {health_status} | {work_status} | 位置:({x:.0f},{y:.0f})"

    def _draw_scroll_indicator(self, screen, total_npcs):
        """
        繪製滾動指示器\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標\n
        total_npcs (int): NPC總數\n
        """
        # 滾動條位置
        scrollbar_x = self.x + self.width - 20
        scrollbar_y = self.y + 70
        scrollbar_height = self.height - 80
        
        # 繪製滾動條背景
        pygame.draw.rect(screen, (64, 64, 64), (scrollbar_x, scrollbar_y, 15, scrollbar_height))
        
        # 計算滾動條位置
        if self.max_scroll > 0:
            scroll_ratio = self.scroll_offset / self.max_scroll
            indicator_height = max(20, scrollbar_height * self.items_per_page // total_npcs)
            indicator_y = scrollbar_y + int((scrollbar_height - indicator_height) * scroll_ratio)
            
            # 繪製滾動指示器
            pygame.draw.rect(screen, self.text_color, (scrollbar_x + 2, indicator_y, 11, indicator_height))
        
        # 顯示頁面資訊
        page_info = f"{self.scroll_offset + 1}-{min(self.scroll_offset + self.items_per_page, total_npcs)} / {total_npcs}"
        font = self.font_manager.get_font(UI_FONT_SIZE - 6)
        page_text = font.render(page_info, True, self.text_color)
        screen.blit(page_text, (scrollbar_x - 60, self.y + self.height - 25))