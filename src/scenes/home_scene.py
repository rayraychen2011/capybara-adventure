######################載入套件######################
import pygame
import json
import os
from src.core.scene_manager import Scene
from src.core.state_manager import GameState
from src.player.player import Player
from src.player.input_controller import InputController
from config.settings import *


######################家的場景######################
class HomeScene(Scene):
    """
    家的場景 - 玩家的私人空間和休息地點\n
    \n
    家是玩家的安全港，提供存檔、休息、物品展示等功能\n
    玩家可以在這裡管理收藏品、查看成就、規劃下一步行動\n
    是遊戲中重要的個人化空間\n
    """

    def __init__(self, state_manager):
        """
        初始化家的場景\n
        \n
        參數:\n
        state_manager (StateManager): 遊戲狀態管理器\n
        """
        super().__init__("家")
        self.state_manager = state_manager

        # 建立玩家角色
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # 建立輸入控制器
        self.input_controller = InputController(self.player)

        # 建立房間設施
        self._create_furniture()
        self._create_interaction_areas()
        self._create_exit_area()

        # 存檔系統
        self.save_file_path = "saves/game_save.json"

        # 展示區域
        self.trophy_display = []  # 展示的戰利品
        self.fish_display = []  # 展示的魚類

        print("家的場景已建立")

    def set_entry_from_scene(self, previous_scene_name):
        """
        設定玩家從指定場景進入家時的位置\n
        \n
        參數:\n
        previous_scene_name (str): 前一個場景的名稱\n
        """
        self.entry_from_scene = previous_scene_name

    def _create_furniture(self):
        """
        建立房間中的家具\n
        """
        self.furniture = [
            {
                "name": "床",
                "type": "bed",
                "area": pygame.Rect(50, 100, 100, 60),
                "color": (139, 69, 19),  # 棕色
                "interaction_point": (100, 180),
            },
            {
                "name": "書桌",
                "type": "desk",
                "area": pygame.Rect(200, 150, 80, 40),
                "color": (160, 82, 45),  # 淺棕色
                "interaction_point": (240, 210),
            },
            {
                "name": "衣櫃",
                "type": "wardrobe",
                "area": pygame.Rect(SCREEN_WIDTH - 150, 100, 60, 120),
                "color": (101, 67, 33),  # 深棕色
                "interaction_point": (SCREEN_WIDTH - 120, 240),
            },
            {
                "name": "展示櫃",
                "type": "display_case",
                "area": pygame.Rect(350, 120, 120, 50),
                "color": (218, 165, 32),  # 金棕色
                "interaction_point": (410, 190),
            },
            {
                "name": "存檔點",
                "type": "save_point",
                "area": pygame.Rect(SCREEN_WIDTH // 2 - 30, 200, 60, 40),
                "color": (0, 255, 0),  # 綠色
                "interaction_point": (SCREEN_WIDTH // 2, 260),
            },
        ]

    def _create_interaction_areas(self):
        """
        建立互動區域\n
        """
        self.interaction_areas = [
            {
                "name": "魚類展示區",
                "type": "fish_display",
                "area": pygame.Rect(50, 300, 150, 50),
                "color": (0, 191, 255),  # 藍色
            },
            {
                "name": "戰利品展示區",
                "type": "trophy_display",
                "area": pygame.Rect(250, 300, 150, 50),
                "color": (255, 215, 0),  # 金色
            },
            {
                "name": "工具架",
                "type": "tool_rack",
                "area": pygame.Rect(450, 300, 100, 50),
                "color": (128, 128, 128),  # 灰色
            },
        ]

    def _create_exit_area(self):
        """
        建立離開家的區域\n
        """
        self.exit_area = pygame.Rect(SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT - 50, 60, 40)

    def enter(self):
        """
        進入家的場景\n
        """
        super().enter()

        # 根據前一個場景設定玩家入口位置
        self._set_entry_position()

        print("玩家回到家中")

        # 更新展示內容
        self._update_displays()

    def _set_entry_position(self):
        """
        根據前一個場景設定玩家的入口位置\n
        \n
        避免玩家傳送到不合適的位置（如緊貼出口）\n
        """
        # 檢查是否有前一個場景信息
        if hasattr(self, "entry_from_scene") and self.entry_from_scene:
            previous_scene = self.entry_from_scene

            # 根據前一個場景設定合適的入口位置
            if previous_scene == "小鎮":
                # 從小鎮進來，放在房間中央偏上方，遠離出口
                self.player.rect.x = SCREEN_WIDTH // 2 - self.player.rect.width // 2
                self.player.rect.y = SCREEN_HEIGHT // 2 - 100  # 房間中央偏上方
            else:
                # 其他情況，使用安全的預設位置
                self._set_default_position()
        else:
            # 沒有前一個場景信息，使用安全的預設位置
            self._set_default_position()

    def _set_default_position(self):
        """
        設定玩家的安全預設位置（房間中央偏上方）\n
        """
        self.player.rect.x = SCREEN_WIDTH // 2 - self.player.rect.width // 2
        self.player.rect.y = SCREEN_HEIGHT // 2 - 100

    def _update_displays(self):
        """
        更新展示區域的內容\n
        """
        # 更新魚類展示
        self.fish_display.clear()
        player_inventory = self.player.get_inventory_list()

        fish_names = ["小魚", "鯉魚", "鱸魚", "虹鱒", "金魚王"]
        for fish_name in fish_names:
            if fish_name in player_inventory:
                self.fish_display.append(
                    {"name": fish_name, "count": player_inventory[fish_name]}
                )

        # 更新戰利品展示
        self.trophy_display.clear()
        meat_items = [item for item in player_inventory.keys() if "肉" in item]
        for meat in meat_items:
            self.trophy_display.append({"name": meat, "count": player_inventory[meat]})

    def update(self, dt):
        """
        更新家的場景邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新輸入控制器
        self.input_controller.update(dt)

        # 更新玩家角色
        self.player.update(dt)

        # 檢查場景切換
        self._check_exit()

        # 檢查家具互動
        self._check_furniture_interactions()

        # 檢查展示區域互動
        self._check_display_interactions()

    def _check_exit(self):
        """
        檢查玩家是否要離開家\n
        """
        if self.player.rect.colliderect(self.exit_area):
            self.request_scene_change(SCENE_TOWN)

    def _check_furniture_interactions(self):
        """
        檢查玩家與家具的互動\n
        """
        if self.input_controller.is_action_key_pressed("interact"):
            player_pos = self.player.get_center_position()

            for furniture in self.furniture:
                interaction_point = furniture["interaction_point"]
                distance = (
                    (player_pos[0] - interaction_point[0]) ** 2
                    + (player_pos[1] - interaction_point[1]) ** 2
                ) ** 0.5

                if distance < 50:  # 互動範圍
                    self._interact_with_furniture(furniture)
                    break

    def _interact_with_furniture(self, furniture):
        """
        與家具互動\n
        \n
        參數:\n
        furniture (dict): 家具資料\n
        """
        furniture_type = furniture["type"]
        furniture_name = furniture["name"]

        print(f"與{furniture_name}互動")

        if furniture_type == "bed":
            # 與床互動 - 恢復體力
            self._rest_in_bed()

        elif furniture_type == "desk":
            # 與書桌互動 - 查看統計資料
            self._check_statistics()

        elif furniture_type == "wardrobe":
            # 與衣櫃互動 - 更換服裝
            self._change_clothes()

        elif furniture_type == "display_case":
            # 與展示櫃互動 - 管理展示品
            self._manage_display()

        elif furniture_type == "save_point":
            # 與存檔點互動 - 儲存遊戲
            self._save_game()

    def _rest_in_bed(self):
        """
        在床上休息\n
        """
        # 恢復玩家體力（這裡簡化實作）
        print("在舒適的床上休息了一會兒...")
        print("體力已恢復！")
        # 這裡可以實作體力系統的恢復

    def _check_statistics(self):
        """
        查看遊戲統計資料\n
        """
        inventory = self.player.get_inventory_list()
        money = self.player.get_money()

        print("\n=== 遊戲統計 ===")
        print(f"當前金錢: ${money}")
        print(f"背包物品數: {sum(inventory.values())}")

        # 統計魚類
        fish_count = 0
        fish_names = ["小魚", "鯉魚", "鱸魚", "虹鱒", "金魚王"]
        for fish_name in fish_names:
            fish_count += inventory.get(fish_name, 0)
        print(f"釣到的魚: {fish_count} 條")

        # 統計狩獵成果
        meat_count = 0
        for item, count in inventory.items():
            if "肉" in item:
                meat_count += count
        print(f"狩獵收穫: {meat_count} 份")
        print("===============\n")

    def _change_clothes(self):
        """
        更換服裝\n
        """
        print("打開衣櫃...")
        print("服裝系統尚未完全實作")
        # 這裡可以實作服裝更換系統

    def _manage_display(self):
        """
        管理展示品\n
        """
        print("查看展示櫃...")
        print("展示管理系統尚未完全實作")
        # 這裡可以實作展示品管理

    def _save_game(self):
        """
        儲存遊戲進度\n
        """
        try:
            # 創建存檔目錄
            save_dir = os.path.dirname(self.save_file_path)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # 收集存檔資料
            save_data = {
                "player": self.player.get_save_data(),
                "scene": "home",
                "game_version": "1.0",
            }

            # 寫入存檔檔案
            with open(self.save_file_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            print("遊戲已儲存！")

        except Exception as e:
            print(f"儲存遊戲失敗: {e}")

    def _load_game(self):
        """
        載入遊戲進度\n
        """
        try:
            if not os.path.exists(self.save_file_path):
                print("沒有找到存檔檔案")
                return False

            # 讀取存檔檔案
            with open(self.save_file_path, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            # 載入玩家資料
            if "player" in save_data:
                self.player.load_save_data(save_data["player"])

            print("遊戲已載入！")
            return True

        except Exception as e:
            print(f"載入遊戲失敗: {e}")
            return False

    def _check_display_interactions(self):
        """
        檢查玩家與展示區域的互動\n
        """
        if self.input_controller.is_action_key_pressed("interact"):
            player_rect = self.player.rect

            for area in self.interaction_areas:
                if player_rect.colliderect(area["area"]):
                    self._interact_with_display(area)
                    break

    def _interact_with_display(self, area):
        """
        與展示區域互動\n
        \n
        參數:\n
        area (dict): 展示區域資料\n
        """
        area_type = area["type"]
        area_name = area["name"]

        print(f"查看{area_name}")

        if area_type == "fish_display":
            self._view_fish_display()
        elif area_type == "trophy_display":
            self._view_trophy_display()
        elif area_type == "tool_rack":
            self._view_tool_rack()

    def _view_fish_display(self):
        """
        查看魚類展示\n
        """
        print("\n=== 魚類收藏 ===")
        if self.fish_display:
            for fish in self.fish_display:
                print(f"{fish['name']}: {fish['count']} 條")
        else:
            print("還沒有收集到任何魚類")
        print("===============\n")

    def _view_trophy_display(self):
        """
        查看戰利品展示\n
        """
        print("\n=== 狩獵戰利品 ===")
        if self.trophy_display:
            for trophy in self.trophy_display:
                print(f"{trophy['name']}: {trophy['count']} 份")
        else:
            print("還沒有狩獵戰利品")
        print("=================\n")

    def _view_tool_rack(self):
        """
        查看工具架\n
        """
        current_tool = self.player.get_current_tool()
        print(f"\n當前裝備的工具: {current_tool if current_tool else '無'}")
        print("工具管理系統尚未完全實作\n")

    def draw(self, screen):
        """
        繪製家的場景\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 清空背景為溫暖的米色
        screen.fill((245, 245, 220))

        # 繪製地板
        self._draw_floor(screen)

        # 繪製牆壁
        self._draw_walls(screen)

        # 繪製家具
        self._draw_furniture(screen)

        # 繪製互動區域
        self._draw_interaction_areas(screen)

        # 繪製出口
        self._draw_exit_area(screen)

        # 繪製玩家角色
        self.player.draw(screen)

        # 繪製 UI
        self._draw_ui(screen)

    def _draw_floor(self, screen):
        """
        繪製地板\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        floor_color = (222, 184, 135)  # 淺棕色木地板

        # 繪製地板紋理（簡單的線條）
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, (200, 160, 120), (0, y), (SCREEN_WIDTH, y), 1)

    def _draw_walls(self, screen):
        """
        繪製牆壁\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        wall_color = (255, 228, 196)  # 淺米色

        # 上牆
        pygame.draw.rect(screen, wall_color, (0, 0, SCREEN_WIDTH, 80))
        # 左牆
        pygame.draw.rect(screen, wall_color, (0, 0, 40, SCREEN_HEIGHT))
        # 右牆
        pygame.draw.rect(screen, wall_color, (SCREEN_WIDTH - 40, 0, 40, SCREEN_HEIGHT))

    def _draw_furniture(self, screen):
        """
        繪製家具\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        font = pygame.font.Font(None, 20)

        for furniture in self.furniture:
            # 繪製家具主體
            pygame.draw.rect(screen, furniture["color"], furniture["area"])
            pygame.draw.rect(screen, (0, 0, 0), furniture["area"], 2)

            # 繪製家具名稱
            text = font.render(furniture["name"], True, (255, 255, 255))
            text_rect = text.get_rect(center=furniture["area"].center)
            screen.blit(text, text_rect)

            # 繪製互動點
            interaction_point = furniture["interaction_point"]
            pygame.draw.circle(screen, (255, 255, 0), interaction_point, 5)

    def _draw_interaction_areas(self, screen):
        """
        繪製互動區域\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        font = pygame.font.Font(None, 18)

        for area in self.interaction_areas:
            # 繪製區域背景
            pygame.draw.rect(screen, area["color"], area["area"])
            pygame.draw.rect(screen, (0, 0, 0), area["area"], 2)

            # 繪製區域名稱
            text = font.render(area["name"], True, (0, 0, 0))
            text_rect = text.get_rect(center=area["area"].center)
            screen.blit(text, text_rect)

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
        text = font.render("出門", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.exit_area.center)
        screen.blit(text, text_rect)

    def _draw_ui(self, screen):
        """
        繪製使用者介面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        font = pygame.font.Font(None, 24)

        # 顯示金錢
        money_text = font.render(f"金錢: ${self.player.get_money()}", True, (0, 0, 0))
        screen.blit(money_text, (10, 10))

        # 顯示背包使用情況
        inventory = self.player.get_inventory_list()
        item_count = sum(inventory.values())
        capacity = self.player.inventory_capacity
        inventory_text = font.render(f"背包: {item_count}/{capacity}", True, (0, 0, 0))
        screen.blit(inventory_text, (10, 35))

        # 顯示操作提示
        hint_text = font.render("E: 互動 | I: 背包 | 觀察各種展示區域", True, (0, 0, 0))
        screen.blit(hint_text, (10, SCREEN_HEIGHT - 30))

    def handle_event(self, event):
        """
        處理家的場景輸入事件\n
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
            if action == "inventory":
                self.state_manager.change_state(GameState.INVENTORY)
                return True

        return False

    def get_player(self):
        """
        獲取玩家角色實例\n
        \n
        回傳:\n
        Player: 玩家角色物件\n
        """
        return self.player
