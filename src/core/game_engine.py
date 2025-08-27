######################載入套件######################
import pygame
import sys
from config.settings import *
from src.core.state_manager import StateManager, GameState
from src.core.scene_manager import SceneManager
from src.scenes.menu_scene import MenuScene
from src.scenes.town_scene import TownScene
from src.scenes.forest_scene import ForestScene
from src.scenes.lake_scene import LakeScene
from src.scenes.home_scene import HomeScene
from src.scenes.inventory_scene import InventoryScene
from src.utils.font_manager import init_font_system


######################遊戲引擎######################
class GameEngine:
    """
    遊戲引擎主類別 - 小鎮生活模擬器的核心引擎\n
    \n
    負責整合所有遊戲系統，管理遊戲的主迴圈\n
    包含狀態管理、場景管理、輸入處理、時間管理等核心功能\n
    確保遊戲各個系統能夠協調運作\n
    \n
    主要職責:\n
    1. 初始化 Pygame 和遊戲系統\n
    2. 管理遊戲主迴圈和時間控制\n
    3. 協調狀態管理器和場景管理器\n
    4. 處理全域輸入事件\n
    5. 控制遊戲的啟動和關閉\n
    """

    def __init__(self):
        """
        初始化遊戲引擎\n
        \n
        設定遊戲視窗、建立管理器、註冊場景\n
        準備遊戲運行所需的所有基礎設施\n
        """
        # 建立遊戲視窗
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)

        # 初始化字體系統 - 支援繁體中文顯示
        init_font_system()

        # 建立時鐘物件，用於控制遊戲幀率
        self.clock = pygame.time.Clock()

        # 當前活躍的玩家實例（所有場景共享）
        self.current_player = None

        # 遊戲運行標誌
        self.running = True

        # 建立狀態管理器
        self.state_manager = StateManager()

        # 建立場景管理器
        self.scene_manager = SceneManager()

        # 註冊狀態變更回調
        self.state_manager.register_state_change_callback(
            "engine_state_handler", self._handle_state_change
        )

        # 初始化所有場景
        self._initialize_scenes()

        # 設定初始場景和狀態
        self.scene_manager.change_scene(SCENE_TOWN)  # 預設從小鎮開始
        self.state_manager.change_state(GameState.PLAYING)  # 設定為遊戲進行狀態

        print("遊戲引擎初始化完成")

    def _initialize_scenes(self):
        """
        初始化並註冊所有遊戲場景\n
        \n
        建立所有場景的實例並註冊到場景管理器\n
        每個場景都需要傳入必要的參數和依賴\n
        """
        try:
            # 建立主選單場景
            menu_scene = MenuScene(self.state_manager)
            self.scene_manager.register_scene("menu", menu_scene)

            # 建立小鎮場景
            town_scene = TownScene(self.state_manager)
            self.scene_manager.register_scene(SCENE_TOWN, town_scene)

            # 設定當前玩家為小鎮場景的玩家
            self.current_player = town_scene.get_player()

            # 建立森林場景
            forest_scene = ForestScene(self.state_manager)
            self.scene_manager.register_scene(SCENE_FOREST, forest_scene)

            # 建立湖泊場景
            lake_scene = LakeScene(self.state_manager)
            self.scene_manager.register_scene(SCENE_LAKE, lake_scene)

            # 建立家的場景
            home_scene = HomeScene(self.state_manager)
            self.scene_manager.register_scene(SCENE_HOME, home_scene)

            # 建立背包場景
            inventory_scene = InventoryScene(self.state_manager, self.current_player)
            self.scene_manager.register_scene("inventory", inventory_scene)

            print(f"成功註冊 {self.scene_manager.get_scene_count()} 個場景")

        except Exception as e:
            print(f"場景初始化失敗: {e}")
            raise

    def _handle_state_change(self, old_state, new_state):
        """
        處理遊戲狀態變更\n
        \n
        當狀態管理器改變狀態時，這個方法會被調用\n
        根據新狀態來調整遊戲引擎的行為\n
        \n
        參數:\n
        old_state (GameState): 前一個狀態\n
        new_state (GameState): 新的狀態\n
        """
        print(f"引擎處理狀態變更: {old_state.value} -> {new_state.value}")

        # 根據新狀態執行相應的動作
        if new_state == GameState.QUIT:
            # 準備退出遊戲
            self.running = False
            print("遊戲引擎準備關閉")

        elif new_state == GameState.MENU:
            # 切換到主選單場景
            self.scene_manager.change_scene("menu")

        elif new_state == GameState.PLAYING:
            # 確保在正確的遊戲場景中
            current_scene = self.scene_manager.get_current_scene_name()
            if current_scene == "menu":
                # 如果從選單進入遊戲，切換到小鎮
                self.scene_manager.change_scene(SCENE_TOWN)

        elif new_state == GameState.INVENTORY:
            # 切換到背包場景
            self.scene_manager.change_scene("inventory")

    def handle_events(self):
        """
        處理所有輸入事件\n
        \n
        收集並處理玩家的鍵盤、滑鼠、視窗等輸入\n
        先讓當前場景處理事件，再處理全域事件\n
        """
        for event in pygame.event.get():
            # 處理視窗關閉事件
            if event.type == pygame.QUIT:
                self.state_manager.change_state(GameState.QUIT)
                continue

            # 處理全域按鍵事件
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC 鍵處理
                    if self.state_manager.is_state(GameState.PLAYING):
                        self.state_manager.change_state(GameState.PAUSED)
                    elif self.state_manager.is_state(GameState.PAUSED):
                        self.state_manager.change_state(GameState.PLAYING)
                    elif self.state_manager.is_state(GameState.MENU):
                        self.state_manager.change_state(GameState.QUIT)
                    else:
                        # 其他狀態下 ESC 返回遊戲
                        self.state_manager.change_state(GameState.PLAYING)
                    continue

                elif event.key == pygame.K_F11:
                    # F11 切換全螢幕
                    self._toggle_fullscreen()
                    continue

            # 讓當前場景處理事件
            event_handled = self.scene_manager.handle_event(event)

            # 如果場景沒有處理事件，可以在這裡添加其他全域處理
            if not event_handled:
                pass  # 預留給其他全域事件處理

    def _toggle_fullscreen(self):
        """
        切換全螢幕/視窗模式\n
        \n
        提供全螢幕功能，改善遊戲體驗\n
        """
        try:
            # 獲取當前顯示模式的標誌
            current_flags = self.screen.get_flags()

            if current_flags & pygame.FULLSCREEN:
                # 目前是全螢幕，切換到視窗模式
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                print("切換到視窗模式")
            else:
                # 目前是視窗模式，切換到全螢幕
                self.screen = pygame.display.set_mode(
                    (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN
                )
                print("切換到全螢幕模式")

        except pygame.error as e:
            print(f"切換顯示模式失敗: {e}")

    def update(self, dt):
        """
        更新遊戲邏輯\n
        \n
        每幀調用一次，更新所有遊戲系統\n
        根據當前狀態決定要更新哪些系統\n
        \n
        參數:\n
        dt (float): 與上一幀的時間差，單位為秒\n
        """
        # 更新場景管理器
        self.scene_manager.update(dt)

        # 根據遊戲狀態執行特定的更新邏輯
        if self.state_manager.is_state(GameState.PLAYING):
            # 遊戲進行中的更新
            pass

        elif self.state_manager.is_state(GameState.PAUSED):
            # 暫停狀態的更新（通常不更新遊戲邏輯）
            pass

    def draw(self):
        """
        繪製遊戲畫面\n
        \n
        每幀調用一次，繪製所有視覺元素\n
        確保畫面更新順序正確\n
        """
        # 清空螢幕為背景色
        self.screen.fill(BACKGROUND_COLOR)

        # 讓場景管理器繪製當前場景
        self.scene_manager.draw(self.screen)

        # 根據遊戲狀態繪製額外的 UI
        if self.state_manager.is_state(GameState.PAUSED):
            self._draw_pause_overlay()

        # 更新螢幕顯示
        pygame.display.flip()

    def _draw_pause_overlay(self):
        """
        繪製暫停畫面的遮罩\n
        \n
        在暫停狀態時顯示半透明遮罩和暫停文字\n
        """
        # 建立半透明的暫停遮罩
        pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pause_overlay.set_alpha(128)  # 50% 透明度
        pause_overlay.fill((0, 0, 0))  # 黑色遮罩

        # 繪製遮罩
        self.screen.blit(pause_overlay, (0, 0))

        # 繪製暫停文字
        font = pygame.font.Font(None, 72)
        pause_text = font.render("遊戲暫停", True, TEXT_COLOR)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)

        # 繪製提示文字
        font_small = pygame.font.Font(None, 36)
        hint_text = font_small.render("按 ESC 繼續遊戲", True, TEXT_COLOR)
        hint_rect = hint_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        )
        self.screen.blit(hint_text, hint_rect)

    def run(self):
        """
        遊戲主迴圈 - 引擎的核心運行方法\n
        \n
        持續執行直到遊戲結束，每次迴圈執行：\n
        1. 處理輸入事件\n
        2. 更新遊戲邏輯\n
        3. 繪製遊戲畫面\n
        4. 控制幀率\n
        \n
        這是遊戲的心跳，確保遊戲以穩定的幀率運行\n
        """
        print("遊戲主迴圈開始")

        while self.running:
            # 計算這一幀與上一幀的時間差
            dt = self.clock.tick(FPS) / 1000.0  # 轉換為秒

            try:
                # 處理所有輸入事件
                self.handle_events()

                # 更新遊戲邏輯
                self.update(dt)

                # 繪製遊戲畫面
                self.draw()

            except Exception as e:
                # 捕捉並記錄遊戲運行時的錯誤
                import traceback

                print(f"遊戲運行時發生錯誤: {e}")
                print("完整錯誤追蹤:")
                traceback.print_exc()
                # 可以選擇繼續運行或結束遊戲
                break

        # 遊戲結束時的清理工作
        self._cleanup()
        print("遊戲主迴圈結束")

    def _cleanup(self):
        """
        遊戲結束時的清理工作\n
        \n
        釋放遊戲資源，確保程式正常退出\n
        """
        try:
            # 清理場景管理器
            self.scene_manager.cleanup()

            # 取消狀態變更回調
            self.state_manager.unregister_state_change_callback("engine_state_handler")

            print("遊戲引擎清理完成")

        except Exception as e:
            print(f"清理過程發生錯誤: {e}")

    def get_fps(self):
        """
        獲取當前幀率\n
        \n
        回傳:\n
        float: 當前每秒幀數\n
        """
        return self.clock.get_fps()

    def force_quit(self):
        """
        強制退出遊戲\n
        \n
        緊急退出方法，跳過正常的狀態切換\n
        """
        self.running = False
        print("強制退出遊戲")
