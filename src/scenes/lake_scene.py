######################載入套件######################
import pygame
import random
import math
from src.core.scene_manager import Scene
from src.core.state_manager import GameState
from src.player.player import Player
from src.player.input_controller import InputController
from src.systems.wildlife import WildlifeManager
from config.settings import *


######################湖泊場景######################
class LakeScene(Scene):
    """
    湖泊場景 - 釣魚和休閒活動的主要區域\n
    \n
    湖泊提供寧靜的釣魚環境和水上活動\n
    玩家可以在這裡釣魚、收集水邊資源、享受悠閒時光\n
    是遊戲中重要的經濟來源和放鬆場所\n
    """

    def __init__(self, state_manager):
        """
        初始化湖泊場景\n
        \n
        參數:\n
        state_manager (StateManager): 遊戲狀態管理器\n
        """
        super().__init__("湖泊")
        self.state_manager = state_manager

        # 建立玩家角色 - 初始位置會在 enter() 時設定
        self.player = Player(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)

        # 建立輸入控制器
        self.input_controller = InputController(self.player)

        # 建立野生動物管理器
        self.wildlife_manager = WildlifeManager()
        self.wildlife_manager.set_habitat_bounds(
            (0, 0, 0, 0),  # 森林邊界 (湖泊場景中不使用)
            (100, 150, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 300),  # 湖泊邊界
        )

        # 建立場景元素
        self._create_lake()
        self._create_fishing_spots()
        self._create_water_resources()
        self._create_exit_area()

        # 釣魚系統狀態
        self.fishing_mode = False
        self.fishing_progress = 0.0
        self.fishing_time = 0.0
        self.current_fish = None
        self.fishing_spot = None

        # 除錯模式
        self.debug_mode = False

        print("湖泊場景已建立")

    def _create_lake(self):
        """
        建立湖泊的形狀和區域\n
        """
        # 主湖泊區域（不規則形狀）
        self.lake_area = pygame.Rect(100, 150, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 300)

        # 湖邊區域（可以釣魚的地方）
        self.shore_areas = [
            pygame.Rect(80, 130, 40, 200),  # 左岸
            pygame.Rect(100, 130, 300, 40),  # 上岸
            pygame.Rect(SCREEN_WIDTH - 220, 130, 40, 200),  # 右岸
            pygame.Rect(100, SCREEN_HEIGHT - 190, 300, 40),  # 下岸
        ]

    def _create_fishing_spots(self):
        """
        建立釣魚點\n
        \n
        在湖邊創建特定的釣魚位置\n
        """
        self.fishing_spots = [
            {
                "name": "北岸釣點",
                "position": (250, 120),
                "area": pygame.Rect(230, 100, 40, 40),
                "fish_rate": 0.4,  # 釣到魚的機率
                "rare_rate": 0.1,  # 釣到稀有魚的機率
            },
            {
                "name": "東岸釣點",
                "position": (SCREEN_WIDTH - 200, 250),
                "area": pygame.Rect(SCREEN_WIDTH - 220, 230, 40, 40),
                "fish_rate": 0.5,
                "rare_rate": 0.15,
            },
            {
                "name": "南岸釣點",
                "position": (350, SCREEN_HEIGHT - 170),
                "area": pygame.Rect(330, SCREEN_HEIGHT - 190, 40, 40),
                "fish_rate": 0.3,
                "rare_rate": 0.05,
            },
            {
                "name": "西岸釣點",
                "position": (100, 280),
                "area": pygame.Rect(80, 260, 40, 40),
                "fish_rate": 0.6,
                "rare_rate": 0.2,
            },
        ]

    def _create_fish_types(self):
        """
        定義魚類種類和屬性 - 已移除，現在使用 WildlifeManager\n
        """
        # 此方法已被 WildlifeManager 取代
        pass

    def _create_water_resources(self):
        """
        建立水邊可收集的資源\n
        """
        self.water_resources = []

        resource_types = [
            {"name": "水草", "color": (0, 100, 0), "value": 3},
            {"name": "貝殼", "color": (255, 192, 203), "value": 8},
            {"name": "漂流木", "color": (139, 69, 19), "value": 5},
            {"name": "水晶", "color": (173, 216, 230), "value": 25},
        ]

        # 沿著湖邊隨機生成資源
        for _ in range(12):
            resource_type = random.choice(resource_types)

            # 在湖邊區域隨機選擇位置
            shore = random.choice(self.shore_areas)
            x = random.randint(shore.left, shore.right - 16)
            y = random.randint(shore.top, shore.bottom - 16)

            resource = {
                "name": resource_type["name"],
                "position": (x, y),
                "color": resource_type["color"],
                "value": resource_type["value"],
                "collected": False,
                "rect": pygame.Rect(x, y, 16, 16),
            }

            self.water_resources.append(resource)

    def _create_exit_area(self):
        """
        建立返回森林的出口區域 - 湖泊西邊邊界\n
        """
        self.exit_area = pygame.Rect(0, SCREEN_HEIGHT // 2 - 50, 30, 100)

    def set_entry_from_scene(self, previous_scene_name):
        """
        設定玩家從指定場景進入湖泊時的位置\n
        \n
        參數:\n
        previous_scene_name (str): 前一個場景的名稱\n
        """
        self.entry_from_scene = previous_scene_name

    def enter(self):
        """
        進入湖泊場景\n
        """
        super().enter()
        print("玩家來到湖泊")

        # 根據前一個場景設定玩家入口位置
        self._set_entry_position()

        # 初始化野生動物系統 (只生成湖泊動物)
        self.wildlife_manager.initialize_animals("lake")

        # 設定正確的棲息地邊界
        self.wildlife_manager.set_habitat_bounds(
            (0, 0, 0, 0),  # 森林邊界 (湖泊場景中不使用)
            (100, 150, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 300),  # 湖泊邊界
        )

        # 重新生成一些資源
        self._respawn_some_resources()

    def _set_entry_position(self):
        """
        根據前一個場景設定玩家的入口位置\n
        \n
        從不同場景進入時，玩家會出現在對應的邊界位置\n
        """
        if hasattr(self, "entry_from_scene") and self.entry_from_scene:
            previous_scene = self.entry_from_scene

            if previous_scene == "森林":
                # 從森林來，出現在西邊入口
                self.player.set_position(50, SCREEN_HEIGHT // 2)
            else:
                self._set_default_position()
        else:
            self._set_default_position()

    def _set_default_position(self):
        """
        設定玩家的預設位置（湖泊西岸）\n
        """
        self.player.set_position(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)

    def _respawn_some_resources(self):
        """
        重新生成一些資源\n
        """
        collected_resources = [res for res in self.water_resources if res["collected"]]

        # 有 20% 機率重新生成已收集的資源
        for resource in collected_resources:
            if random.random() < 0.2:
                resource["collected"] = False

    def update(self, dt):
        """
        更新湖泊場景邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新輸入控制器
        self.input_controller.update(dt)

        # 更新玩家角色
        self.player.update(dt)

        # 更新野生動物系統
        self.wildlife_manager.update(dt, self.player.get_center_position(), "lake")

        # 更新釣魚系統
        if self.fishing_mode:
            self._update_fishing(dt)

        # 檢查場景切換
        self._check_exit()

        # 檢查資源收集
        self._check_resource_collection()

        # 檢查釣魚點互動
        self._check_fishing_spots()

    def _update_fishing(self, dt):
        """
        更新釣魚邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        self.fishing_time += dt

        # 釣魚進度計算
        progress_speed = 1.0 / FISHING_TIME  # 基於設定的釣魚時間
        self.fishing_progress += progress_speed * dt

        # 釣魚完成
        if self.fishing_progress >= 1.0:
            self._complete_fishing()

    def _complete_fishing(self):
        """
        完成釣魚 - 使用新的釣魚系統\n
        """
        if not self.fishing_spot:
            self.fishing_mode = False
            return

        # 使用野生動物管理器進行釣魚
        fishing_result = self.wildlife_manager.attempt_fishing(
            self.player.get_center_position(), self.player
        )

        if fishing_result["success"]:
            if fishing_result["fish"]:
                fish = fishing_result["fish"]
                print(f"釣到了 {fish.animal_type.value}！")

                # 處理戰利品
                for item_name, quantity in fishing_result["loot"]:
                    if self.player.add_item(item_name, quantity):
                        print(f"獲得 {item_name} x{quantity}")
                    else:
                        print(f"背包已滿，無法獲得 {item_name}")

                # 檢查懲罰
                if fishing_result["penalty"]:
                    print(fishing_result["penalty"])
        else:
            print("什麼都沒釣到...")

        # 重置釣魚狀態
        self.fishing_mode = False
        self.fishing_progress = 0.0
        self.fishing_time = 0.0
        self.current_fish = None
        self.fishing_spot = None

    def _get_random_fish(self):
        """
        根據機率獲取隨機魚類 - 已移除，現在使用 WildlifeManager\n
        \n
        回傳:\n
        dict: 魚類資料\n
        """
        # 此方法已被 WildlifeManager 取代
        pass

    def _catch_fish(self, fish):
        """
        捕獲魚類 - 已移除，現在使用 WildlifeManager\n
        \n
        參數:\n
        fish (dict): 捕獲的魚類資料\n
        """
        # 此方法已被 WildlifeManager 取代
        pass

    def _check_exit(self):
        """
        檢查玩家是否要離開湖泊 - 需要主動向西移動回森林\n
        """
        if self.player.rect.colliderect(self.exit_area):
            # 檢查玩家是否向左移動（向西回森林）
            if self.player.direction_x < 0:
                print("步行返回森林")
                self.request_scene_change(SCENE_FOREST)

    def _check_resource_collection(self):
        """
        檢查資源收集\n
        """
        if self.input_controller.is_action_key_pressed("interact"):
            player_rect = self.player.rect

            for resource in self.water_resources:
                if not resource["collected"] and player_rect.colliderect(
                    resource["rect"]
                ):
                    self._collect_resource(resource)
                    break

    def _collect_resource(self, resource):
        """
        收集資源\n
        \n
        參數:\n
        resource (dict): 要收集的資源\n
        """
        resource_name = resource["name"]
        value = resource["value"]

        if self.player.add_item(resource_name, 1):
            resource["collected"] = True
            self.player.add_money(value)
            print(f"收集了 {resource_name}，獲得 ${value}")
        else:
            print("背包已滿，無法收集更多物品")

    def _check_fishing_spots(self):
        """
        檢查釣魚點互動\n
        """
        if (
            self.input_controller.is_action_key_pressed("fishing")
            and not self.fishing_mode
        ):
            player_rect = self.player.rect

            for spot in self.fishing_spots:
                if player_rect.colliderect(spot["area"]):
                    self._start_fishing(spot)
                    break

    def _start_fishing(self, spot):
        """
        開始釣魚\n
        \n
        參數:\n
        spot (dict): 釣魚點資料\n
        """
        # 檢查是否有釣魚竿（這裡簡化，假設總是有）
        self.fishing_mode = True
        self.fishing_progress = 0.0
        self.fishing_time = 0.0
        self.fishing_spot = spot

        print(f"在 {spot['name']} 開始釣魚...")

    def draw(self, screen):
        """
        繪製湖泊場景\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 清空背景為天空藍色
        screen.fill(BACKGROUND_COLOR)

        # 繪製湖水
        self._draw_lake(screen)

        # 繪製湖邊
        self._draw_shore(screen)

        # 繪製湖水中的魚類
        self.wildlife_manager.draw_all_animals(screen, "lake")

        # 繪製釣魚點
        self._draw_fishing_spots(screen)

        # 繪製水邊資源
        self._draw_water_resources(screen)

        # 繪製出口區域
        self._draw_exit_area(screen)

        # 繪製玩家角色
        self.player.draw(screen)

        # 繪製釣魚介面
        if self.fishing_mode:
            self._draw_fishing_ui(screen)

        # 繪製 UI
        self._draw_ui(screen)

        # 繪製除錯資訊
        if self.debug_mode:
            font = pygame.font.Font(None, 16)
            self.wildlife_manager.draw_debug_info(screen, font, "lake")

    def _draw_lake(self, screen):
        """
        繪製湖水\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 繪製主湖水區域
        pygame.draw.rect(screen, WATER_COLOR, self.lake_area)

        # 添加水波效果（簡單的線條）
        for i in range(5):
            wave_y = self.lake_area.top + (i + 1) * (self.lake_area.height // 6)
            wave_color = (
                min(255, WATER_COLOR[0] + 20),
                min(255, WATER_COLOR[1] + 20),
                min(255, WATER_COLOR[2] + 20),
            )
            pygame.draw.line(
                screen,
                wave_color,
                (self.lake_area.left, wave_y),
                (self.lake_area.right, wave_y),
                2,
            )

    def _draw_shore(self, screen):
        """
        繪製湖邊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        shore_color = (194, 178, 128)  # 沙色

        for shore in self.shore_areas:
            pygame.draw.rect(screen, shore_color, shore)

    def _draw_fishing_spots(self, screen):
        """
        繪製釣魚點\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        font = pygame.font.Font(None, 20)

        for spot in self.fishing_spots:
            # 繪製釣魚點區域
            pygame.draw.rect(screen, (255, 255, 0), spot["area"])
            pygame.draw.rect(screen, (0, 0, 0), spot["area"], 2)

            # 繪製釣魚點標誌
            position = spot["position"]
            pygame.draw.circle(screen, (0, 100, 200), position, 8)

            # 繪製名稱
            text = font.render(spot["name"], True, (0, 0, 0))
            text_rect = text.get_rect(center=(position[0], position[1] - 20))
            screen.blit(text, text_rect)

    def _draw_water_resources(self, screen):
        """
        繪製水邊資源\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for resource in self.water_resources:
            if resource["collected"]:
                continue

            # 繪製資源
            pygame.draw.rect(screen, resource["color"], resource["rect"])
            pygame.draw.rect(screen, (0, 0, 0), resource["rect"], 1)

    def _draw_exit_area(self, screen):
        """
        繪製出口區域\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        pygame.draw.rect(screen, (255, 255, 0), self.exit_area)
        pygame.draw.rect(screen, (0, 0, 0), self.exit_area, 2)

        font = pygame.font.Font(None, 20)
        text = font.render("回森林", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.exit_area.center)
        screen.blit(text, text_rect)

    def _draw_fishing_ui(self, screen):
        """
        繪製釣魚介面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 繪製釣魚進度條
        progress_bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 50, 200, 20)
        progress_fill_width = int(progress_bar_rect.width * self.fishing_progress)
        progress_fill_rect = pygame.Rect(
            progress_bar_rect.x,
            progress_bar_rect.y,
            progress_fill_width,
            progress_bar_rect.height,
        )

        # 進度條背景
        pygame.draw.rect(screen, (100, 100, 100), progress_bar_rect)
        # 進度條填充
        pygame.draw.rect(screen, (0, 255, 0), progress_fill_rect)
        # 進度條邊框
        pygame.draw.rect(screen, (0, 0, 0), progress_bar_rect, 2)

        # 釣魚狀態文字
        font = pygame.font.Font(None, 36)
        status_text = font.render("正在釣魚...", True, (255, 255, 255))
        status_rect = status_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(status_text, status_rect)

        # 釣魚點資訊
        if self.fishing_spot:
            info_font = pygame.font.Font(None, 24)
            info_text = info_font.render(
                f"釣魚點: {self.fishing_spot['name']}", True, (255, 255, 255)
            )
            screen.blit(info_text, (SCREEN_WIDTH // 2 - 100, 80))

    def _draw_ui(self, screen):
        """
        繪製使用者介面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        font = pygame.font.Font(None, 24)

        # 顯示金錢
        money_text = font.render(
            f"金錢: ${self.player.get_money()}", True, (255, 255, 255)
        )
        screen.blit(money_text, (10, 10))

        # 顯示座標（以家為原點）
        relative_x, relative_y = self.player.get_relative_position()
        coord_text = font.render(
            f"座標: ({relative_x}, {relative_y})", True, (255, 255, 255)
        )
        screen.blit(coord_text, (10, 35))

        # 顯示魚類數量（統計背包中的魚）
        animals = self.wildlife_manager.get_animals_in_scene("lake")
        fish_count = len([animal for animal in animals if animal.is_alive])

        fish_text = font.render(f"魚類: {fish_count}", True, (255, 255, 255))
        screen.blit(fish_text, (10, 60))

        # 繪製物品欄（畫面底下）
        self.player.draw_item_bar(screen)

        # 顯示操作提示
        if not self.fishing_mode:
            hint_text = font.render(
                "E: 收集 | F: 釣魚 | 1-0: 選擇物品欄 | D: 除錯", True, (255, 255, 255)
            )
        else:
            hint_text = font.render("釣魚中，請等待...", True, (255, 255, 0))

        screen.blit(hint_text, (10, SCREEN_HEIGHT - 100))

    def handle_event(self, event):
        """
        處理湖泊場景的輸入事件\n
        \n
        參數:\n
        event (pygame.event.Event): 輸入事件\n
        \n
        回傳:\n
        bool: True 表示事件已處理\n
        """
        # 釣魚模式中不處理其他輸入
        if self.fishing_mode:
            return True

        # 讓輸入控制器處理事件
        action = self.input_controller.handle_event(event)

        if action:
            if action == "inventory":
                self.state_manager.change_state(GameState.INVENTORY)
                return True

        # 檢查除錯模式切換和物品欄選擇
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                self.debug_mode = not self.debug_mode
                print(f"除錯模式: {'開啟' if self.debug_mode else '關閉'}")
                return True

            # 數字鍵選擇物品欄格子 (1-9, 0代表第10格)
            elif pygame.K_1 <= event.key <= pygame.K_9:
                slot_index = event.key - pygame.K_1  # 1鍵對應索引0
                self.player.select_slot(slot_index)
                print(f"選擇物品欄格子 {slot_index + 1}")
                return True
            elif event.key == pygame.K_0:
                self.player.select_slot(9)  # 0鍵對應第10格（索引9）
                print("選擇物品欄格子 10")
                return True

        return False
