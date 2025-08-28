######################載入套件######################
import pygame
import random
from src.core.scene_manager import Scene
from src.core.state_manager import GameState
from src.player.player import Player
from src.player.input_controller import InputController
from src.utils.font_manager import get_font_manager
from src.systems.wildlife import WildlifeManager
from config.settings import *


######################森林場景######################
class ForestScene(Scene):
    """
    森林場景 - 狩獵和資源收集的主要區域\n
    \n
    森林充滿各種野生動物和天然資源\n
    玩家可以在這裡狩獵、收集材料、探索隱藏的寶藏\n
    提供豐富的戶外活動體驗\n
    """

    def __init__(self, state_manager):
        """
        初始化森林場景\n
        \n
        參數:\n
        state_manager (StateManager): 遊戲狀態管理器\n
        """
        super().__init__("森林")
        self.state_manager = state_manager

        # 建立玩家角色 - 初始位置會在 enter() 時設定
        self.player = Player(100, SCREEN_HEIGHT // 2)

        # 建立輸入控制器
        self.input_controller = InputController(self.player)

        # 建立野生動物管理器
        self.wildlife_manager = WildlifeManager()
        self.wildlife_manager.set_habitat_bounds(
            (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100),  # 森林邊界
            (0, 0, 0, 0),  # 湖泊邊界 (森林場景中不使用)
        )

        # 建立場景元素
        self._create_trees()
        self._create_resources()
        self._create_exit_area()

        # 狩獵系統狀態
        self.hunting_mode = False
        self.crosshair_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        print("森林場景已建立")

    def _create_trees(self):
        """
        建立森林中的樹木\n
        \n
        生成隨機分佈的樹木作為環境裝飾和障礙物\n
        """
        self.trees = []

        # 隨機生成 20-30 棵樹
        num_trees = random.randint(20, 30)

        for _ in range(num_trees):
            # 隨機位置，避免太靠近邊界
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)

            # 隨機樹木大小
            size = random.randint(20, 40)

            tree = {
                "position": (x, y),
                "size": size,
                "color": (34, 100, 34),  # 深綠色
                "rect": pygame.Rect(x - size // 2, y - size // 2, size, size),
            }

            self.trees.append(tree)

    def _create_animals(self):
        """
        建立森林中的動物 - 已移除，現在使用 WildlifeManager\n
        """
        # 此方法已被 WildlifeManager 取代
        pass

    def _create_resources(self):
        """
        建立可收集的資源\n
        \n
        生成木材、草藥等可收集物品\n
        """
        self.resources = []

        resource_types = [
            {"name": "木材", "color": (139, 69, 19), "value": 5},
            {"name": "草藥", "color": (0, 128, 0), "value": 8},
            {"name": "蘑菇", "color": (255, 228, 196), "value": 12},
            {"name": "石頭", "color": (128, 128, 128), "value": 3},
        ]

        # 隨機生成 15-25 個資源
        num_resources = random.randint(15, 25)

        for _ in range(num_resources):
            resource_type = random.choice(resource_types)

            # 隨機位置
            x = random.randint(30, SCREEN_WIDTH - 30)
            y = random.randint(30, SCREEN_HEIGHT - 30)

            resource = {
                "name": resource_type["name"],
                "position": (x, y),
                "color": resource_type["color"],
                "value": resource_type["value"],
                "collected": False,
                "rect": pygame.Rect(x - 8, y - 8, 16, 16),
            }

            self.resources.append(resource)

    def _create_exit_area(self):
        """
        建立場景切換區域 - 森林的各個出入口\n
        """
        # 返回小鎮的出口區域 - 森林西邊邊界
        self.town_exit_area = pygame.Rect(0, SCREEN_HEIGHT // 2 - 50, 30, 100)

        # 前往湖泊的出口區域 - 森林東邊邊界
        self.lake_exit_area = pygame.Rect(
            SCREEN_WIDTH - 30, SCREEN_HEIGHT // 2 - 50, 30, 100
        )

    def set_entry_from_scene(self, previous_scene_name):
        """
        設定玩家從指定場景進入森林時的位置\n
        \n
        參數:\n
        previous_scene_name (str): 前一個場景的名稱\n
        """
        self.entry_from_scene = previous_scene_name

    def enter(self):
        """
        進入森林場景\n
        """
        super().enter()
        print("玩家進入森林")

        # 根據前一個場景設定玩家入口位置
        self._set_entry_position()

        # 初始化野生動物系統 (只生成森林動物)
        self.wildlife_manager.initialize_animals("forest")

        # 設定正確的棲息地邊界
        self.wildlife_manager.set_habitat_bounds(
            (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100),  # 森林邊界
            (0, 0, 0, 0),  # 湖泊邊界 (森林場景中不使用)
        )

    def _set_entry_position(self):
        """
        根據前一個場景設定玩家的入口位置\n
        \n
        從不同場景進入時，玩家會出現在對應的邊界位置\n
        """
        if hasattr(self, "entry_from_scene") and self.entry_from_scene:
            previous_scene = self.entry_from_scene

            if previous_scene == "小鎮":
                # 從小鎮來，出現在西邊入口
                self.player.set_position(50, SCREEN_HEIGHT // 2)
            elif previous_scene == "湖泊":
                # 從湖泊回來，出現在東邊入口
                self.player.set_position(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)
            else:
                self._set_default_position()
        else:
            self._set_default_position()

    def _set_default_position(self):
        """
        設定玩家的預設位置（森林中央偏西）\n
        """
        self.player.set_position(100, SCREEN_HEIGHT // 2)

    def _respawn_some_animals(self):
        """
        重新生成一些動物 - 已移除，現在使用 WildlifeManager\n
        """
        # 此方法已被 WildlifeManager 取代
        pass

    def update(self, dt):
        """
        更新森林場景邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新輸入控制器
        self.input_controller.update(dt)

        # 更新玩家角色
        self.player.update(dt)

        # 更新野生動物系統
        self.wildlife_manager.update(dt, self.player.get_center_position(), "forest")

        # 檢查場景切換
        self._check_exit()

        # 檢查資源收集
        self._check_resource_collection()

        # 檢查狩獵
        if self.hunting_mode:
            self._update_hunting_mode()

    def _update_animals(self, dt):
        """
        更新動物的移動和行為 - 已移除，現在使用 WildlifeManager\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 此方法已被 WildlifeManager 取代
        pass

    def _check_exit(self):
        """
        檢查玩家是否要離開森林 - 檢查兩個方向的出口\n
        """
        # 檢查返回小鎮
        if self.player.rect.colliderect(self.town_exit_area):
            # 檢查玩家是否向左移動（向西回小鎮）
            if self.player.direction_x < 0:
                print("步行返回小鎮")
                self.request_scene_change(SCENE_TOWN)

        # 檢查前往湖泊
        elif self.player.rect.colliderect(self.lake_exit_area):
            # 檢查玩家是否向右移動（向東去湖泊）
            if self.player.direction_x > 0:
                print("步行前往湖泊")
                self.request_scene_change(SCENE_LAKE)

    def _check_resource_collection(self):
        """
        檢查資源收集\n
        """
        if self.input_controller.is_action_key_pressed("interact"):
            player_rect = self.player.rect

            for resource in self.resources:
                if not resource["collected"] and player_rect.colliderect(
                    resource["rect"]
                ):
                    # 收集資源
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

        # 添加到玩家背包
        if self.player.add_item(resource_name, 1):
            resource["collected"] = True
            self.player.add_money(value)
            print(f"收集了 {resource_name}，獲得 ${value}")
        else:
            print("背包已滿，無法收集更多物品")

    def _update_hunting_mode(self):
        """
        更新狩獵模式\n
        """
        # 獲取滑鼠位置作為準星位置
        self.crosshair_pos = pygame.mouse.get_pos()

    def _shoot_at_target(self, target_pos):
        """
        向目標射擊 - 使用新的狩獵系統\n
        \n
        參數:\n
        target_pos (tuple): 目標位置\n
        """
        player_pos = self.player.get_center_position()

        # 檢查射程
        distance = (
            (target_pos[0] - player_pos[0]) ** 2 + (target_pos[1] - player_pos[1]) ** 2
        ) ** 0.5

        if distance > GUN_RANGE:
            print("目標太遠，無法射擊")
            return

        # 使用野生動物管理器進行狩獵
        hunt_result = self.wildlife_manager.attempt_hunting(player_pos, self.player)

        if hunt_result["success"]:
            if hunt_result["animal"]:
                animal = hunt_result["animal"]
                if animal.is_alive:
                    print(f"射擊命中 {animal.animal_type.value}！")
                else:
                    print(f"成功獵殺 {animal.animal_type.value}！")

                    # 處理戰利品
                    for item_name, quantity in hunt_result["loot"]:
                        if self.player.add_item(item_name, quantity):
                            print(f"獲得 {item_name} x{quantity}")
                        else:
                            print(f"背包已滿，無法獲得 {item_name}")

                    # 檢查懲罰
                    if hunt_result["penalty"]:
                        print(hunt_result["penalty"])
        else:
            print("射擊落空")

    def _hunt_animal(self, animal):
        """
        狩獵動物 - 已移除，現在使用 WildlifeManager\n
        \n
        參數:\n
        animal (dict): 被獵殺的動物\n
        """
        # 此方法已被 WildlifeManager 取代
        pass

    def draw(self, screen):
        """
        繪製森林場景\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 清空背景為森林綠色
        screen.fill((34, 80, 34))

        # 繪製樹木
        self._draw_trees(screen)

        # 繪製資源
        self._draw_resources(screen)

        # 繪製野生動物
        self.wildlife_manager.draw_all_animals(screen, "forest")

        # 繪製出口區域
        self._draw_exit_area(screen)

        # 繪製玩家角色
        self.player.draw(screen)

        # 繪製狩獵介面
        if self.hunting_mode:
            self._draw_hunting_ui(screen)

        # 繪製 UI
        self._draw_ui(screen)

        # 繪製除錯資訊
    def _draw_trees(self, screen):
        """
        繪製樹木\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for tree in self.trees:
            position = tree["position"]
            size = tree["size"]
            color = tree["color"]

            # 繪製樹冠（圓形）
            pygame.draw.circle(screen, color, position, size // 2)

            # 繪製樹幹（矩形）
            trunk_rect = pygame.Rect(position[0] - 3, position[1], 6, size // 3)
            pygame.draw.rect(screen, (101, 67, 33), trunk_rect)

    def _draw_resources(self, screen):
        """
        繪製資源\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for resource in self.resources:
            if resource["collected"]:
                continue

            # 繪製資源（小方塊）
            pygame.draw.rect(screen, resource["color"], resource["rect"])
            pygame.draw.rect(screen, (0, 0, 0), resource["rect"], 1)

    def _draw_animals(self, screen):
        """
        繪製動物 - 已移除，現在使用 WildlifeManager\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 此方法已被 WildlifeManager 取代
        pass

    def _draw_exit_area(self, screen):
        """
        繪製出口區域 - 繪製返回小鎮和前往湖泊的出口\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 繪製回小鎮的出口（西邊）
        pygame.draw.rect(screen, (255, 255, 0), self.town_exit_area)
        pygame.draw.rect(screen, (0, 0, 0), self.town_exit_area, 2)

        font = pygame.font.Font(None, 20)
        town_text = font.render("回小鎮", True, (0, 0, 0))
        town_text_rect = town_text.get_rect(center=self.town_exit_area.center)
        screen.blit(town_text, town_text_rect)

        # 繪製往湖泊的出口（東邊）
        pygame.draw.rect(screen, (0, 191, 255), self.lake_exit_area)
        pygame.draw.rect(screen, (0, 0, 0), self.lake_exit_area, 2)

        lake_text = font.render("往湖泊", True, (0, 0, 0))
        lake_text_rect = lake_text.get_rect(center=self.lake_exit_area.center)
        screen.blit(lake_text, lake_text_rect)

    def _draw_hunting_ui(self, screen):
        """
        繪製狩獵模式的介面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 繪製準星
        crosshair_size = 20
        x, y = self.crosshair_pos

        # 十字準星
        pygame.draw.line(
            screen, (255, 0, 0), (x - crosshair_size, y), (x + crosshair_size, y), 2
        )
        pygame.draw.line(
            screen, (255, 0, 0), (x, y - crosshair_size), (x, y + crosshair_size), 2
        )

        # 準星圓圈
        pygame.draw.circle(screen, (255, 0, 0), (x, y), crosshair_size, 2)

        # 狩獵模式提示已移除

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

        # 顯示動物數量
        animals = self.wildlife_manager.get_animals_in_scene("forest")
        alive_animals = sum(1 for animal in animals if animal.is_alive)
        animal_text = font.render(f"動物: {alive_animals}", True, (255, 255, 255))
        screen.blit(animal_text, (10, 60))

        # 繪製物品欄（畫面底下）
        self.player.draw_item_bar(screen)

        # 操作提示已移除

    def handle_event(self, event):
        """
        處理森林場景的輸入事件\n
        \n
        參數:\n
        event (pygame.event.Event): 輸入事件\n
        \n
        回傳:\n
        bool: True 表示事件已處理\n
        """
        # 讓輸入控制器處理事件
        action = self.input_controller.handle_event(event)

        if action:
            if action == "hunting":
                # 切換狩獵模式
                self.hunting_mode = not self.hunting_mode
                if self.hunting_mode:
                    print("進入狩獵模式")
                else:
                    print("退出狩獵模式")
                return True

            elif action == "inventory":
                self.state_manager.change_state(GameState.INVENTORY)
                return True

        # 檢查物品欄選擇
        if event.type == pygame.KEYDOWN:
            # 數字鍵選擇物品欄格子 (1-9, 0代表第10格)
            if pygame.K_1 <= event.key <= pygame.K_9:
                slot_index = event.key - pygame.K_1  # 1鍵對應索引0
                self.player.select_slot(slot_index)
                print(f"選擇物品欄格子 {slot_index + 1}")
                return True
            elif event.key == pygame.K_0:
                self.player.select_slot(9)  # 0鍵對應第10格（索引9）
                print("選擇物品欄格子 10")
                return True

        # 處理狩獵模式的滑鼠點擊
        if self.hunting_mode and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵
                self._shoot_at_target(event.pos)
                return True

        return False
