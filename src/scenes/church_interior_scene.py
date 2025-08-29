######################載入套件######################
import pygame
from config.settings import *
from src.core.scene_manager import Scene
from src.systems.church_system import ChurchScene, BlessingSystem, Altar
from src.utils.font_manager import get_font_manager


######################教堂內部場景######################
class ChurchInteriorScene(Scene):
    """
    教堂內部場景 - 玩家進入教堂後的內部環境\n
    \n
    包含功能：\n
    - 祭壇互動（獲得祝福效果）\n
    - 座位擺設\n
    - 祈禱功能\n
    - 返回小鎮的出口\n
    """

    def __init__(self):
        """
        初始化教堂內部場景\n
        """
        super().__init__("教堂內部")
        
        # 字體管理器
        self.font_manager = get_font_manager()
        
        # 場景設定
        self.background_color = (100, 80, 60)  # 溫暖的棕色背景
        
        # 祝福系統
        self.blessing_system = BlessingSystem()
        
        # 創建祭壇（位於場景中央偏上）
        altar_x = SCREEN_WIDTH // 2 - 20
        altar_y = SCREEN_HEIGHT // 3
        self.altar = Altar(altar_x, altar_y)
        
        # 座位設定
        self.chairs = []
        self._create_chairs()
        
        # 出口區域（門口）
        self.exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT - 50, 60, 30)
        
        # 玩家在教堂內的位置
        self.player_church_x = SCREEN_WIDTH // 2
        self.player_church_y = SCREEN_HEIGHT - 80
        
        # 互動狀態
        self.show_exit_hint = False
        self.show_altar_hint = False
        
        print("教堂內部場景初始化完成")

    def _create_chairs(self):
        """
        創建教堂座位\n
        """
        chair_width = 25
        chair_height = 15
        chair_spacing = 10
        
        # 左側座位（3排，每排4個座位）
        for row in range(3):
            for col in range(4):
                x = 100 + col * (chair_width + chair_spacing)
                y = SCREEN_HEIGHT // 2 + row * (chair_height + chair_spacing)
                chair = {
                    'rect': pygame.Rect(x, y, chair_width, chair_height),
                    'color': (139, 69, 19)  # 棕色
                }
                self.chairs.append(chair)
        
        # 右側座位（3排，每排4個座位）
        for row in range(3):
            for col in range(4):
                x = SCREEN_WIDTH - 250 + col * (chair_width + chair_spacing)
                y = SCREEN_HEIGHT // 2 + row * (chair_height + chair_spacing)
                chair = {
                    'rect': pygame.Rect(x, y, chair_width, chair_height),
                    'color': (139, 69, 19)  # 棕色
                }
                self.chairs.append(chair)

    def enter(self):
        """
        進入教堂場景\n
        """
        super().enter()
        print("🏛️ 進入神聖的教堂")
        print("在這裡你可以：")
        print("- 與祭壇互動獲得祝福（按E鍵）")
        print("- 在座位上休息")
        print("- 按ESC鍵或走到門口離開教堂")

    def exit(self):
        """
        離開教堂場景\n
        """
        super().exit()
        print("🚪 離開教堂，回到小鎮")

    def handle_event(self, event):
        """
        處理場景事件\n
        \n
        參數:\n
        event (pygame.Event): Pygame事件\n
        \n
        回傳:\n
        bool: True表示事件已處理，False表示需要傳遞給其他處理器\n
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC鍵離開教堂
                self.transition_target = "小鎮"
                return True
            
            elif event.key == pygame.K_e:
                # E鍵與祭壇互動
                if self.show_altar_hint:
                    return self._interact_with_altar()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵點擊
                # 檢查是否點擊出口
                if self.exit_rect.collidepoint(event.pos):
                    self.transition_target = "小鎮"
                    return True
        
        return False

    def _interact_with_altar(self):
        """
        與祭壇互動\n
        \n
        回傳:\n
        bool: 互動是否成功\n
        """
        # 這裡需要獲取玩家物件，暫時模擬
        # 在實際整合時需要從場景管理器或其他方式獲取玩家
        from src.core.game_engine import GameEngine
        engine = GameEngine.get_instance()
        if engine and hasattr(engine, 'player'):
            player = engine.player
            success = self.blessing_system.grant_blessing(player)
            if success:
                print("🙏 你虔誠地祈禱，感受到神聖的力量加持")
                return True
        else:
            # 測試用的祝福效果
            print("🙏 你虔誠地祈禱，獲得了神聖的祝福！")
            print("✨ 祝福效果：接下來10分鐘內，擊敗敵人獲得雙倍金錢！")
            return True
        
        return False

    def update(self, dt):
        """
        更新場景\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新祝福系統
        self.blessing_system.update(dt)
        
        # 檢查玩家是否靠近祭壇（簡化實作，使用固定位置）
        altar_distance = ((self.player_church_x - (self.altar.x + self.altar.width//2))**2 + 
                         (self.player_church_y - (self.altar.y + self.altar.height//2))**2)**0.5
        
        self.show_altar_hint = altar_distance < 50
        
        # 檢查玩家是否靠近出口
        player_rect = pygame.Rect(self.player_church_x - 10, self.player_church_y - 10, 20, 20)
        self.show_exit_hint = self.exit_rect.colliderect(player_rect)

    def draw(self, screen):
        """
        繪製場景\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 清空螢幕並填充背景色
        screen.fill(self.background_color)
        
        # 繪製彩色玻璃窗
        self._draw_stained_glass(screen)
        
        # 繪製地板圖案
        self._draw_floor_pattern(screen)
        
        # 繪製座位
        self._draw_chairs(screen)
        
        # 繪製祭壇
        self.altar.draw(screen)
        
        # 繪製出口
        self._draw_exit(screen)
        
        # 繪製玩家（簡單的圓點）
        pygame.draw.circle(screen, (255, 255, 255), 
                         (int(self.player_church_x), int(self.player_church_y)), 8)
        pygame.draw.circle(screen, (0, 0, 0), 
                         (int(self.player_church_x), int(self.player_church_y)), 8, 2)
        
        # 繪製UI元素
        self._draw_ui(screen)

    def _draw_stained_glass(self, screen):
        """
        繪製彩色玻璃窗\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 左側彩色玻璃窗
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
        
        # 左窗戶
        for i, color in enumerate(colors):
            section = pygame.Rect(30, 80 + i * 40, 80, 40)
            pygame.draw.rect(screen, color, section)
            pygame.draw.rect(screen, (0, 0, 0), section, 3)
        
        # 右窗戶
        for i, color in enumerate(colors):
            section = pygame.Rect(SCREEN_WIDTH - 110, 80 + i * 40, 80, 40)
            pygame.draw.rect(screen, color, section)
            pygame.draw.rect(screen, (0, 0, 0), section, 3)

    def _draw_floor_pattern(self, screen):
        """
        繪製地板圖案\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 棋盤格地板
        tile_size = 40
        colors = [(160, 140, 120), (180, 160, 140)]
        
        for x in range(0, SCREEN_WIDTH, tile_size):
            for y in range(0, SCREEN_HEIGHT, tile_size):
                color_index = ((x // tile_size) + (y // tile_size)) % 2
                tile_rect = pygame.Rect(x, y, tile_size, tile_size)
                pygame.draw.rect(screen, colors[color_index], tile_rect)

    def _draw_chairs(self, screen):
        """
        繪製座位\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for chair in self.chairs:
            # 座位基座
            pygame.draw.rect(screen, chair['color'], chair['rect'])
            pygame.draw.rect(screen, (100, 50, 0), chair['rect'], 2)
            
            # 座位靠背
            back_rect = pygame.Rect(chair['rect'].x, chair['rect'].y - 8, 
                                  chair['rect'].width, 8)
            pygame.draw.rect(screen, chair['color'], back_rect)
            pygame.draw.rect(screen, (100, 50, 0), back_rect, 2)

    def _draw_exit(self, screen):
        """
        繪製出口\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 門框
        pygame.draw.rect(screen, (139, 69, 19), self.exit_rect)
        pygame.draw.rect(screen, (100, 50, 0), self.exit_rect, 3)
        
        # 門把手
        handle_x = self.exit_rect.x + self.exit_rect.width - 8
        handle_y = self.exit_rect.y + self.exit_rect.height // 2
        pygame.draw.circle(screen, (255, 215, 0), (handle_x, handle_y), 3)
        
        # 出口提示
        if self.show_exit_hint:
            font = pygame.font.Font(None, 18)
            hint_text = font.render("按ESC或點擊離開教堂", True, (255, 255, 0))
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 20))
            screen.blit(hint_text, hint_rect)

    def _draw_ui(self, screen):
        """
        繪製UI元素\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 場景標題
        title_text = self.font_manager.render_text("神聖教堂", 28, (255, 215, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 30))
        screen.blit(title_text, title_rect)
        
        # 祭壇互動提示
        if self.show_altar_hint:
            hint_text = self.font_manager.render_text("按E鍵祈禱獲得祝福", 18, (255, 255, 0))
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH//2, self.altar.y - 20))
            screen.blit(hint_text, hint_rect)
        
        # 操作說明
        instructions = [
            "操作說明：",
            "E鍵 - 在祭壇前祈禱獲得祝福",
            "ESC鍵 - 離開教堂",
            "點擊門口 - 離開教堂"
        ]
        
        for i, instruction in enumerate(instructions):
            color = (255, 255, 255) if i == 0 else (200, 200, 200)
            size = 18 if i == 0 else 14
            text = self.font_manager.render_text(instruction, size, color)
            text_rect = text.get_rect(topleft=(20, 20 + i * 20))
            screen.blit(text, text_rect)