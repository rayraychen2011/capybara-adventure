######################載入套件######################
import pygame
from src.utils.font_manager import get_font_manager
from src.utils.helpers import draw_text
from config.settings import *


######################小鎮 UI 管理器######################
class TownUIManager:
    """
    小鎮場景 UI 管理器 - 統一管理所有 UI 元素\n
    \n
    負責：\n
    1. HUD 顯示（金錢、物品欄等）\n
    2. 小地圖顯示\n
    3. NPC 資訊面板\n
    4. 提示訊息\n
    5. 控制說明\n
    """

    def __init__(self, player, minimap_ui, npc_info_ui, terrain_system=None):
        """
        初始化 UI 管理器\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        minimap_ui (MinimapUI): 小地圖 UI\n
        npc_info_ui (NPCInfoUI): NPC 資訊 UI\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        """
        self.player = player
        self.minimap_ui = minimap_ui
        self.npc_info_ui = npc_info_ui
        self.terrain_system = terrain_system
        
        # 取得字體管理器
        self.font_manager = get_font_manager()
        
        # UI 狀態
        self.show_npc_info = False
        self.show_controls_hint = True
        self.show_minimap = True
        
        # 訊息系統
        self.current_message = ""
        self.message_timer = 0
        self.message_duration = 3.0  # 訊息顯示時間（秒）
        
        # HUD 設定
        self.hud_background_color = (0, 0, 0, 128)  # 半透明黑色
        self.hud_text_color = TEXT_COLOR
        
        print("小鎮 UI 管理器初始化完成")

    def update(self, dt):
        """
        更新 UI 狀態\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        # 更新訊息計時器
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.current_message = ""

    def draw(self, screen, camera_controller, npc_manager, time_manager):
        """
        繪製所有 UI 元素\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        camera_controller (TownCameraController): 攝影機控制器\n
        npc_manager (NPCManager): NPC 管理器\n
        time_manager (TimeManager): 時間管理器\n
        """
        # 繪製玩家 HUD
        self._draw_player_hud(screen)
        
        # 繪製小地圖
        if self.show_minimap:
            self._draw_minimap(screen, camera_controller)
        
        # 繪製 NPC 資訊面板
        if self.show_npc_info:
            self._draw_npc_info(screen, npc_manager)
        
        # 繪製當前訊息
        if self.current_message:
            self._draw_message(screen)
        
        # 繪製控制提示
        if self.show_controls_hint:
            self._draw_controls_hint(screen)

    def _draw_player_hud(self, screen):
        """
        繪製玩家 HUD（金錢、物品欄）\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        """
        # 繪製 HUD 背景
        hud_rect = pygame.Rect(10, 10, 300, 80)
        hud_surface = pygame.Surface((hud_rect.width, hud_rect.height))
        hud_surface.set_alpha(128)
        hud_surface.fill((0, 0, 0))
        screen.blit(hud_surface, hud_rect.topleft)
        
        # 繪製玩家金錢
        money_text = f"金錢: ${self.player.get_money()}"
        font = self.font_manager.get_font(DEFAULT_FONT_SIZE)
        draw_text(screen, money_text, font, self.hud_text_color, 20, 20)
        
        # 繪製玩家健康值
        health_text = f"健康: {self.player.health}/{PLAYER_MAX_HEALTH}"
        draw_text(screen, health_text, font, self.hud_text_color, 20, 45)
        
        # 繪製當前選中的物品
        selected_item = self.player.get_selected_item()
        if selected_item:
            item_text = f"手持: {selected_item['name']} x{selected_item['count']}"
        else:
            item_text = "手持: 無"
        draw_text(screen, item_text, font, self.hud_text_color, 20, 70)

    def _draw_minimap(self, screen, camera_controller):
        """
        繪製小地圖\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        camera_controller (TownCameraController): 攝影機控制器\n
        """
        # 獲取地形資料
        terrain_data = None
        buildings = None
        if self.terrain_system:
            terrain_data = self.terrain_system.map_data  # 正確的屬性名稱
            buildings = self.terrain_system.buildings
            
            # 調試：檢查地形資料傳遞
            if hasattr(self, '_minimap_debug_counter'):
                self._minimap_debug_counter += 1
            else:
                self._minimap_debug_counter = 0
            
            if self._minimap_debug_counter % 300 == 0:  # 每5秒輸出一次
                terrain_status = "有地形資料" if terrain_data else "無地形資料"
                building_count = len(buildings) if buildings else 0
                print(f"小地圖調試 - {terrain_status}, 建築數量: {building_count}")
        
        # 使用 MinimapUI.draw 方法並傳遞地形資料
        self.minimap_ui.draw(
            screen, 
            self.player.x, 
            self.player.y, 
            self.player.facing_direction,
            buildings=buildings,
            terrain_data=terrain_data
        )

    def _draw_npc_info(self, screen, npc_manager):
        """
        繪製 NPC 資訊面板\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        npc_manager (NPCManager): NPC 管理器\n
        """
        # 獲取附近的 NPC
        player_pos = (self.player.x, self.player.y)
        nearby_npcs = npc_manager.get_npcs_in_range(player_pos, 200)
        
        # 更新並繪製 NPC 資訊
        self.npc_info_ui.update_npc_list(nearby_npcs)
        self.npc_info_ui.draw(screen)

    def _draw_message(self, screen):
        """
        繪製當前訊息\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        """
        if not self.current_message:
            return
        
        # 計算訊息位置（螢幕中央上方）
        message_y = SCREEN_HEIGHT // 4
        
        # 繪製訊息背景
        font = self.font_manager.get_font(LARGE_FONT_SIZE)
        text_surface = font.render(self.current_message, True, self.hud_text_color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = SCREEN_WIDTH // 2
        text_rect.y = message_y
        
        # 背景矩形稍微大一點
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        
        # 繪製背景和文字
        screen.blit(bg_surface, bg_rect.topleft)
        screen.blit(text_surface, text_rect.topleft)

    def _draw_controls_hint(self, screen):
        """
        繪製控制提示 - 已移除\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        """
        # 控制提示已移除

    def show_message(self, message, duration=3.0):
        """
        顯示訊息\n
        \n
        參數:\n
        message (str): 要顯示的訊息\n
        duration (float): 顯示時間（秒）\n
        """
        self.current_message = message
        self.message_timer = duration
        print(f"UI 訊息: {message}")

    def toggle_npc_info(self):
        """
        切換 NPC 資訊面板顯示\n
        """
        self.show_npc_info = not self.show_npc_info
        print(f"NPC 資訊面板: {'開啟' if self.show_npc_info else '關閉'}")

    def toggle_minimap(self):
        """
        切換小地圖顯示\n
        """
        self.show_minimap = not self.show_minimap
        print(f"小地圖: {'開啟' if self.show_minimap else '關閉'}")

    def toggle_controls_hint(self):
        """
        切換控制提示顯示\n
        """
        self.show_controls_hint = not self.show_controls_hint
        print(f"控制提示: {'開啟' if self.show_controls_hint else '關閉'}")

    def handle_mouse_input(self, event):
        """
        處理滑鼠輸入（主要是小地圖互動）\n
        \n
        參數:\n
        event (pygame.Event): 滑鼠事件\n
        \n
        回傳:\n
        bool: 是否有處理事件\n
        """
        if self.show_minimap:
            return self.minimap_ui.handle_mouse_input(event)
        return False

    def get_debug_info(self):
        """
        獲取 UI 狀態除錯資訊\n
        \n
        回傳:\n
        dict: UI 狀態資訊\n
        """
        return {
            "show_npc_info": self.show_npc_info,
            "show_minimap": self.show_minimap,
            "show_controls_hint": self.show_controls_hint,
            "current_message": self.current_message,
            "message_timer": round(self.message_timer, 2) if self.message_timer > 0 else 0
        }