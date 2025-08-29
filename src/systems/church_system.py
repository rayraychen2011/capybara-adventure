######################載入套件######################
import pygame
import time
from config.settings import *
from src.utils.font_manager import get_font_manager, FontManager


######################教堂建築######################
class Church:
    """
    教堂建築 - 提供祝福效果的宗教建築\n
    \n
    玩家可以右鍵進入教堂場景\n
    在教堂內與祭壇互動可獲得祝福效果\n
    """

    def __init__(self, x, y):
        """
        初始化教堂\n
        \n
        參數:\n
        x (int): 教堂X座標\n
        y (int): 教堂Y座標\n
        """
        self.x = x
        self.y = y
        self.name = "教堂"
        
        # 字體管理器
        self.font_manager = FontManager()
        
        # 教堂尺寸
        self.width = 80
        self.height = 60
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # 互動範圍
        self.interaction_range = 50
        self.is_player_nearby = False
        
        print(f"創建教堂於 ({x}, {y})")

    def is_near_player(self, player_position):
        """
        檢查玩家是否在互動範圍內\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        \n
        回傳:\n
        bool: 是否在互動範圍內\n
        """
        player_x, player_y = player_position
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        
        was_nearby = self.is_player_nearby
        self.is_player_nearby = distance <= self.interaction_range
        
        if self.is_player_nearby and not was_nearby:
            print("進入教堂互動範圍")
        elif was_nearby and not self.is_player_nearby:
            print("離開教堂互動範圍")
        
        return self.is_player_nearby

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製教堂\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (int): 攝影機X偏移\n
        camera_y (int): 攝影機Y偏移\n
        """
        # 計算螢幕座標
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # 檢查是否在螢幕範圍內
        if (screen_x + self.width < 0 or screen_x > SCREEN_WIDTH or
            screen_y + self.height < 0 or screen_y > SCREEN_HEIGHT):
            return
        
        # 繪製教堂主體
        church_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, (200, 200, 200), church_rect)  # 淺灰色主體
        pygame.draw.rect(screen, (100, 100, 100), church_rect, 3)  # 深灰色邊框
        
        # 繪製教堂屋頂（三角形）
        roof_points = [
            (screen_x + self.width // 2, screen_y - 15),  # 頂點
            (screen_x, screen_y),  # 左下角
            (screen_x + self.width, screen_y)  # 右下角
        ]
        pygame.draw.polygon(screen, (160, 82, 45), roof_points)  # 棕色屋頂
        pygame.draw.polygon(screen, (100, 100, 100), roof_points, 2)  # 邊框
        
        # 繪製十字架
        cross_x = screen_x + self.width // 2
        cross_y = screen_y - 8
        # 垂直線
        pygame.draw.line(screen, (139, 69, 19), (cross_x, cross_y - 8), (cross_x, cross_y + 2), 3)
        # 水平線
        pygame.draw.line(screen, (139, 69, 19), (cross_x - 4, cross_y - 3), (cross_x + 4, cross_y - 3), 3)
        
        # 繪製大門
        door_width = 20
        door_height = 30
        door_x = screen_x + (self.width - door_width) // 2
        door_y = screen_y + self.height - door_height
        door_rect = pygame.Rect(door_x, door_y, door_width, door_height)
        pygame.draw.rect(screen, (139, 69, 19), door_rect)  # 棕色門
        pygame.draw.rect(screen, (0, 0, 0), door_rect, 2)  # 黑色邊框
        
        # 繪製窗戶
        window_size = 8
        # 左窗戶
        left_window = pygame.Rect(screen_x + 10, screen_y + 20, window_size, window_size)
        pygame.draw.rect(screen, (135, 206, 235), left_window)  # 淺藍色
        pygame.draw.rect(screen, (0, 0, 0), left_window, 1)
        
        # 右窗戶
        right_window = pygame.Rect(screen_x + self.width - 18, screen_y + 20, window_size, window_size)
        pygame.draw.rect(screen, (135, 206, 235), right_window)  # 淺藍色
        pygame.draw.rect(screen, (0, 0, 0), right_window, 1)
        
        # 繪製教堂名稱
        font = self.font_manager.get_font(18)
        name_text = font.render(self.name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(screen_x + self.width//2, screen_y - 25))
        screen.blit(name_text, name_rect)
        
        # 如果玩家在附近，顯示互動提示
        if self.is_player_nearby:
            hint_text = font.render("按右鍵進入教堂", True, (255, 255, 0))
            hint_rect = hint_text.get_rect(center=(screen_x + self.width//2, screen_y + self.height + 15))
            screen.blit(hint_text, hint_rect)


######################祭壇######################
class Altar:
    """
    祭壇 - 教堂內的互動物件\n
    \n
    玩家可以與祭壇互動獲得祝福效果\n
    """

    def __init__(self, x, y):
        """
        初始化祭壇\n
        \n
        參數:\n
        x (int): 祭壇X座標\n
        y (int): 祭壇Y座標\n
        """
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # 字體管理器
        self.font_manager = FontManager()
        
        # 互動範圍
        self.interaction_range = 30
        self.is_player_nearby = False

    def is_near_player(self, player_position):
        """
        檢查玩家是否在互動範圍內\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        \n
        回傳:\n
        bool: 是否在互動範圍內\n
        """
        player_x, player_y = player_position
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        
        was_nearby = self.is_player_nearby
        self.is_player_nearby = distance <= self.interaction_range
        
        return self.is_player_nearby

    def draw(self, screen):
        """
        繪製祭壇\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 繪製祭壇基座
        base_rect = pygame.Rect(self.x, self.y + 15, self.width, 15)
        pygame.draw.rect(screen, (160, 160, 160), base_rect)  # 淺灰色基座
        pygame.draw.rect(screen, (100, 100, 100), base_rect, 2)  # 深灰色邊框
        
        # 繪製祭壇台面
        table_rect = pygame.Rect(self.x + 5, self.y + 10, self.width - 10, 10)
        pygame.draw.rect(screen, (200, 200, 200), table_rect)  # 更淺的灰色台面
        pygame.draw.rect(screen, (100, 100, 100), table_rect, 1)
        
        # 繪製十字架裝飾
        cross_x = self.x + self.width // 2
        cross_y = self.y + 5
        # 垂直線
        pygame.draw.line(screen, (255, 215, 0), (cross_x, cross_y), (cross_x, cross_y + 8), 2)
        # 水平線
        pygame.draw.line(screen, (255, 215, 0), (cross_x - 3, cross_y + 2), (cross_x + 3, cross_y + 2), 2)
        
        # 繪製燭光效果
        candle_positions = [
            (self.x + 10, self.y + 12),
            (self.x + self.width - 10, self.y + 12)
        ]
        
        for candle_x, candle_y in candle_positions:
            # 蠟燭
            pygame.draw.rect(screen, (255, 255, 240), (candle_x - 1, candle_y, 2, 5))
            # 火焰
            pygame.draw.circle(screen, (255, 100, 0), (candle_x, candle_y - 2), 2)
        
        # 如果玩家在附近，顯示互動提示
        if self.is_player_nearby:
            font = self.font_manager.get_font(16)
            hint_text = font.render("按E鍵祈禱", True, (255, 255, 0))
            hint_rect = hint_text.get_rect(center=(self.x + self.width//2, self.y - 10))
            screen.blit(hint_text, hint_rect)


######################祝福效果系統######################
class BlessingSystem:
    """
    祝福效果系統 - 管理玩家的祝福狀態\n
    \n
    祝福效果：\n
    - 持續10分鐘\n
    - 打怪時掉落金幣數量為平常的雙倍\n
    """

    def __init__(self):
        """
        初始化祝福系統\n
        """
        self.active_blessings = {}  # 玩家ID -> 祝福資訊
        self.blessing_duration = 600  # 10分鐘（秒）
        
        print("祝福效果系統初始化完成")

    def grant_blessing(self, player):
        """
        給予玩家祝福效果\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        current_time = time.time()
        
        # 記錄祝福資訊
        blessing_info = {
            "start_time": current_time,
            "end_time": current_time + self.blessing_duration,
            "effect_type": "double_money_drop",
            "active": True
        }
        
        # 使用玩家物件作為key（簡化實作）
        self.active_blessings[id(player)] = blessing_info
        
        # 在玩家身上添加狀態效果
        player.status_effects["blessed"] = self.blessing_duration
        
        print("🙏 獲得神聖祝福！接下來10分鐘內，擊敗敵人時獲得雙倍金錢獎勵！")
        
        return True

    def is_blessed(self, player):
        """
        檢查玩家是否有祝福效果\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: 是否有祝福效果\n
        """
        player_id = id(player)
        
        if player_id not in self.active_blessings:
            return False
        
        blessing = self.active_blessings[player_id]
        current_time = time.time()
        
        # 檢查祝福是否過期
        if current_time > blessing["end_time"]:
            self._remove_blessing(player)
            return False
        
        return blessing["active"]

    def get_blessing_time_remaining(self, player):
        """
        獲取祝福剩餘時間\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        float: 剩餘時間（秒），如果沒有祝福則返回0\n
        """
        if not self.is_blessed(player):
            return 0
        
        player_id = id(player)
        blessing = self.active_blessings[player_id]
        current_time = time.time()
        
        return max(0, blessing["end_time"] - current_time)

    def apply_blessing_effect(self, player, base_money_reward):
        """
        應用祝福效果到金錢獎勵\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        base_money_reward (int): 基礎金錢獎勵\n
        \n
        回傳:\n
        int: 應用祝福效果後的金錢獎勵\n
        """
        if not self.is_blessed(player):
            return base_money_reward
        
        # 雙倍金錢獎勵
        blessed_reward = base_money_reward * 2
        
        print(f"💰 祝福效果發動！獲得 {blessed_reward} 元（原本 {base_money_reward} 元）")
        
        return blessed_reward

    def _remove_blessing(self, player):
        """
        移除玩家的祝福效果\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        player_id = id(player)
        
        if player_id in self.active_blessings:
            del self.active_blessings[player_id]
        
        # 從玩家狀態效果中移除
        if "blessed" in player.status_effects:
            del player.status_effects["blessed"]
        
        print("✨ 祝福效果已結束")

    def update(self, dt):
        """
        更新祝福系統\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        current_time = time.time()
        expired_blessings = []
        
        # 檢查過期的祝福
        for player_id, blessing in self.active_blessings.items():
            if current_time > blessing["end_time"]:
                expired_blessings.append(player_id)
        
        # 移除過期的祝福
        for player_id in expired_blessings:
            del self.active_blessings[player_id]
            print("✨ 祝福效果已結束")

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製教堂和相關效果\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (int): 攝影機X偏移\n
        camera_y (int): 攝影機Y偏移\n
        """
        # 檢查是否有教堂需要繪製
        if hasattr(self, 'church'):
            self.church.draw(screen, camera_x, camera_y)
        
        # 檢查是否有祭壇需要繪製
        if hasattr(self, 'altar'):
            self.altar.draw(screen)

    def get_blessing_status_text(self, player):
        """
        獲取祝福狀態文字\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        str: 祝福狀態文字\n
        """
        if not self.is_blessed(player):
            return ""
        
        remaining_time = self.get_blessing_time_remaining(player)
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        
        return f"🙏 祝福中 ({minutes:02d}:{seconds:02d})"


######################教堂場景######################
class ChurchScene:
    """
    教堂場景 - 教堂內部的互動場景\n
    \n
    包含祭壇和祝福互動功能\n
    """

    def __init__(self, blessing_system):
        """
        初始化教堂場景\n
        \n
        參數:\n
        blessing_system (BlessingSystem): 祝福系統引用\n
        """
        self.blessing_system = blessing_system
        self.font_manager = get_font_manager()
        
        # 場景設定
        self.background_color = (100, 80, 60)  # 溫暖的棕色背景
        
        # 創建祭壇
        altar_x = SCREEN_WIDTH // 2 - 20
        altar_y = SCREEN_HEIGHT // 2 - 15
        self.altar = Altar(altar_x, altar_y)
        
        print("教堂場景初始化完成")

    def handle_interaction(self, player):
        """
        處理玩家與祭壇的互動\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        player_pos = (player.x, player.y)
        
        if self.altar.is_near_player(player_pos):
            # 給予祝福效果
            self.blessing_system.grant_blessing(player)
            return True
        
        return False

    def update(self, dt, player):
        """
        更新教堂場景\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player (Player): 玩家物件\n
        """
        player_pos = (player.x, player.y)
        self.altar.is_near_player(player_pos)

    def draw(self, screen):
        """
        繪製教堂場景\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 繪製背景
        screen.fill(self.background_color)
        
        # 繪製彩色玻璃窗效果
        self._draw_stained_glass(screen)
        
        # 繪製地板圖案
        self._draw_floor_pattern(screen)
        
        # 繪製祭壇
        self.altar.draw(screen)
        
        # 繪製場景標題
        title_text = self.font_manager.render_text("神聖教堂", 24, (255, 215, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        screen.blit(title_text, title_rect)

    def _draw_stained_glass(self, screen):
        """
        繪製彩色玻璃窗效果\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 左側彩色玻璃窗
        left_window = pygame.Rect(50, 100, 60, 120)
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        
        for i, color in enumerate(colors):
            section = pygame.Rect(50, 100 + i * 30, 60, 30)
            pygame.draw.rect(screen, color, section)
            pygame.draw.rect(screen, (0, 0, 0), section, 2)
        
        # 右側彩色玻璃窗
        right_window = pygame.Rect(SCREEN_WIDTH - 110, 100, 60, 120)
        for i, color in enumerate(colors):
            section = pygame.Rect(SCREEN_WIDTH - 110, 100 + i * 30, 60, 30)
            pygame.draw.rect(screen, color, section)
            pygame.draw.rect(screen, (0, 0, 0), section, 2)

    def _draw_floor_pattern(self, screen):
        """
        繪製地板圖案\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 簡單的棋盤格地板
        tile_size = 40
        colors = [(150, 130, 110), (170, 150, 130)]
        
        for x in range(0, SCREEN_WIDTH, tile_size):
            for y in range(0, SCREEN_HEIGHT, tile_size):
                color_index = ((x // tile_size) + (y // tile_size)) % 2
                tile_rect = pygame.Rect(x, y, tile_size, tile_size)
                pygame.draw.rect(screen, colors[color_index], tile_rect)