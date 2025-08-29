######################載入套件######################
import pygame
from src.utils.font_manager import FontManager


######################農夫狀態UI######################
class FarmerStatusUI:
    """
    農夫工作狀態顯示UI\n
    \n
    顯示農夫工作調度系統的狀態信息\n
    包括當前工作階段、農夫數量統計、時間資訊等\n
    """
    
    def __init__(self):
        """
        初始化農夫狀態UI\n
        """
        self.font_manager = FontManager()
        self.is_visible = False
        self.position = (10, 10)
        self.background_color = (0, 0, 0, 180)  # 半透明黑色背景
        self.text_color = (255, 255, 255)
        self.highlight_color = (255, 255, 0)  # 黃色高亮
        self.work_color = (0, 255, 0)  # 綠色表示工作中
        self.off_duty_color = (128, 128, 128)  # 灰色表示下班
        
    def toggle_visibility(self):
        """
        切換顯示狀態\n
        """
        self.is_visible = not self.is_visible
        
    def draw(self, screen, farmer_scheduler, time_manager):
        """
        繪製農夫狀態UI\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        farmer_scheduler: 農夫工作調度系統\n
        time_manager: 時間管理器\n
        """
        if not self.is_visible or not farmer_scheduler:
            return
        
        # 準備顯示資料
        status = farmer_scheduler.get_farmer_status()
        current_time = time_manager.get_time_string() if time_manager else "未知"
        
        # 準備文字內容
        lines = [
            "=== 農夫工作狀態 ===",
            f"當前時間: {current_time}",
            f"工作階段: {self._get_phase_display_name(status['current_phase'])}",
            "",
            f"總農夫數: {status['total_farmers']}",
            f"工作中: {status['working_farmers']}",
            f"集合中: {status['gathering_farmers']}",
            f"下班: {status['off_duty_farmers']}",
            "",
            "控制說明:",
            "F1 - 切換此顯示",
            "F2 - 強制9:00集合",
            "F3 - 強制9:20工作",
            "F4 - 強制17:00下班",
        ]
        
        # 計算背景大小
        font = self.font_manager.get_font(16)
        line_height = 20
        max_width = 0
        
        for line in lines:
            text_surface = font.render(line, True, self.text_color)
            max_width = max(max_width, text_surface.get_width())
        
        bg_width = max_width + 20
        bg_height = len(lines) * line_height + 20
        
        # 繪製背景
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill(self.background_color)
        screen.blit(bg_surface, self.position)
        
        # 繪製文字
        x, y = self.position
        for i, line in enumerate(lines):
            if line == "":
                continue
                
            # 選擇顏色
            color = self.text_color
            if "工作階段:" in line:
                if "工作中" in line:
                    color = self.work_color
                elif "集合" in line:
                    color = self.highlight_color
                else:
                    color = self.off_duty_color
            elif line.startswith("=== "):
                color = self.highlight_color
            elif line.startswith("F"):
                color = (200, 200, 200)  # 淺灰色控制說明
            
            text_surface = font.render(line, True, color)
            screen.blit(text_surface, (x + 10, y + 10 + i * line_height))
    
    def _get_phase_display_name(self, phase_value):
        """
        獲取工作階段的顯示名稱\n
        \n
        參數:\n
        phase_value (str): 工作階段值\n
        \n
        回傳:\n
        str: 顯示名稱\n
        """
        phase_names = {
            "off_duty": "下班時間",
            "gathering": "集合階段 (9:00-9:20)",
            "working": "工作階段 (9:20-17:00)",
            "returning": "下班返回 (17:00)"
        }
        return phase_names.get(phase_value, phase_value)
    
    def handle_key_event(self, event, farmer_scheduler):
        """
        處理鍵盤事件\n
        \n
        參數:\n
        event: pygame 鍵盤事件\n
        farmer_scheduler: 農夫工作調度系統\n
        """
        if not farmer_scheduler:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.toggle_visibility()
            elif event.key == pygame.K_F2:
                # 強制切換到集合階段
                from src.systems.npc.farmer_work_scheduler import FarmerWorkPhase
                farmer_scheduler.force_phase_transition(FarmerWorkPhase.GATHERING)
                print("🔧 強制切換到集合階段")
            elif event.key == pygame.K_F3:
                # 強制切換到工作階段
                from src.systems.npc.farmer_work_scheduler import FarmerWorkPhase
                farmer_scheduler.force_phase_transition(FarmerWorkPhase.WORKING)
                print("🔧 強制切換到工作階段")
            elif event.key == pygame.K_F4:
                # 強制切換到下班階段
                from src.systems.npc.farmer_work_scheduler import FarmerWorkPhase
                farmer_scheduler.force_phase_transition(FarmerWorkPhase.OFF_DUTY)
                print("🔧 強制切換到下班階段")
    
    def draw_farmer_info_on_map(self, screen, camera_x, camera_y, farmer_scheduler):
        """
        在地圖上顯示農夫資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        farmer_scheduler: 農夫工作調度系統\n
        """
        if not self.is_visible or not farmer_scheduler:
            return
        
        font = self.font_manager.get_font(12)
        
        # 為每個農夫顯示工作階段標記
        for farmer in farmer_scheduler.farmers:
            screen_x = farmer.x - camera_x
            screen_y = farmer.y - camera_y
            
            # 只顯示在螢幕範圍內的農夫
            if -50 <= screen_x <= screen.get_width() + 50 and -50 <= screen_y <= screen.get_height() + 50:
                # 根據工作階段選擇顏色
                if hasattr(farmer, 'work_phase') and farmer.work_phase:
                    if farmer.work_phase.value == "working":
                        color = self.work_color
                        symbol = "🚜"
                    elif farmer.work_phase.value == "gathering":
                        color = self.highlight_color
                        symbol = "📍"
                    else:
                        color = self.off_duty_color
                        symbol = "🏠"
                else:
                    color = self.text_color
                    symbol = "?"
                
                # 繪製農夫狀態標記
                text_surface = font.render(symbol, True, color)
                screen.blit(text_surface, (screen_x - 5, screen_y - 20))