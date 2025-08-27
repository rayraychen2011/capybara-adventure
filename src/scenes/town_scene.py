######################載入套件######################
import pygame
import random
import math
from src.core.scene_manager import Scene
from src.core.state_manager import GameState
from src.player.player import Player
from src.player.input_controller import InputController
from src.utils.font_manager import get_font_manager
from src.utils.npc_info_ui import NPCInfoUI
from src.systems.npc.npc_manager import NPCManager
from src.systems.road_system import RoadManager
from src.systems.vehicle_system import VehicleManager
from config.settings import *


######################小鎮場景######################
class TownScene(Scene):
    """
    小鎮場景 - 30x30街道的大型城鎮\n
    \n
    這是一個大型的小鎮場景，包含：\n
    - 30x30的街道網格系統\n
    - 各種建築物分佈在街區中\n
    - 城牆圍繞整個小鎮\n
    - 攝影機系統跟隨玩家移動\n
    - 各種 NPC 和設施\n
    """

    def __init__(self, state_manager, time_manager=None, power_manager=None):
        """
        初始化大型小鎮場景\n
        \n
        參數:\n
        state_manager (StateManager): 遊戲狀態管理器\n
        time_manager (TimeManager): 時間管理器，用於 NPC 行為控制\n
        power_manager (PowerManager): 電力管理器，用於區域電力控制\n
        """
        super().__init__("小鎮")
        self.state_manager = state_manager
        self.time_manager = time_manager
        self.power_manager = power_manager

        # 取得字體管理器
        self.font_manager = get_font_manager()

        # 攝影機位置 (用於顯示大地圖的一部分)
        self.camera_x = CAMERA_START_X
        self.camera_y = CAMERA_START_Y

        # 建立玩家角色 (放在小鎮中央)
        player_start_x = TOWN_TOTAL_WIDTH // 2
        player_start_y = TOWN_TOTAL_HEIGHT // 2
        self.player = Player(player_start_x, player_start_y)

        # 建立輸入控制器
        self.input_controller = InputController(self.player)

        # 生成小鎮結構
        self._generate_town_layout()
        self._generate_buildings()
        self._create_scene_transitions()

        # 建立 NPC 管理器，傳入時間管理器
        self.npc_manager = NPCManager(self.time_manager)

        # 建立道路管理器
        self.road_manager = RoadManager()

        # 建立載具管理器
        self.vehicle_manager = VehicleManager()

        # 定義小鎮邊界 (扣除城牆)
        town_bounds = (
            WALL_THICKNESS,
            WALL_THICKNESS,
            TOWN_TOTAL_WIDTH - WALL_THICKNESS * 2,
            TOWN_TOTAL_HEIGHT - WALL_THICKNESS * 2,
        )
        forest_bounds = (0, 0, SCREEN_WIDTH * 8, SCREEN_HEIGHT * 8)

        # 為 NPC 管理器設定建築物參考（在創建 NPC 之前）
        self.npc_manager.buildings = self.buildings

        # 初始化道路網絡
        self.road_manager.create_road_network_for_town(town_bounds)

        # 初始化載具生成點
        self._setup_vehicle_spawns(town_bounds)

        # 初始化電力網格（如果有電力管理器）
        if self.power_manager:
            self.power_manager.initialize_power_grid(town_bounds)

        # 初始化所有 NPC（建築物已經存在）
        self.npc_manager.initialize_npcs(town_bounds, forest_bounds)

        # 為 NPC 設定建築物參考，用於碰撞檢測
        self.npc_manager.set_buildings_reference(self.buildings)

        # 為 NPC 設定道路系統參考，用於智能路徑規劃
        self.npc_manager.set_road_system_reference(self.road_manager)

        # 將電力工人註冊到電力系統
        if self.power_manager:
            self._register_power_workers()

        # 生成初始載具
        self.vehicle_manager.spawn_initial_vehicles()

        # NPC 資訊顯示控制
        self.show_npc_info = False

        # NPC 資訊顯示器
        self.npc_info_ui = NPCInfoUI()

        print("大型小鎮場景已建立 (30x30 街道)")

    def _setup_vehicle_spawns(self, town_bounds):
        """
        設置載具生成點\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界\n
        """
        # 在地圖邊緣創建 AI 載具生成點
        self.vehicle_manager.create_map_edge_spawns(town_bounds)

        # 在小鎮內創建玩家載具停車點
        tx, ty, tw, th = town_bounds

        # 在各個街區附近創建停車位
        for i in range(10):  # 創建10個停車位
            # 隨機選擇一個街區
            block = random.choice(self.street_blocks)

            # 在街區邊緣創建停車位
            park_x = block["rect"].x + block["rect"].width + 10
            park_y = block["rect"].y + random.randint(0, block["rect"].height - 30)

            # 確保停車位在小鎮範圍內
            if park_x < tx + tw - 50 and park_y < ty + th - 50:
                vehicle_types = ["car", "bike", "motorcycle"]  # 玩家可用的載具類型
                self.vehicle_manager.add_spawn_point(
                    (park_x, park_y), vehicle_types, is_ai_spawn=False
                )

    def _generate_town_layout(self):
        """
        生成小鎮的街道佈局\n
        \n
        建立 30x30 的街道網格系統\n
        """
        self.streets = []
        self.street_blocks = []

        # 生成橫向街道
        for y in range(TOWN_GRID_HEIGHT + 1):
            street_y = y * (BLOCK_SIZE + STREET_WIDTH)
            street_rect = pygame.Rect(0, street_y, TOWN_TOTAL_WIDTH, STREET_WIDTH)
            self.streets.append(street_rect)

        # 生成縱向街道
        for x in range(TOWN_GRID_WIDTH + 1):
            street_x = x * (BLOCK_SIZE + STREET_WIDTH)
            street_rect = pygame.Rect(street_x, 0, STREET_WIDTH, TOWN_TOTAL_HEIGHT)
            self.streets.append(street_rect)

        # 生成街區 (建築物可以放置的區域)
        for y in range(TOWN_GRID_HEIGHT):
            for x in range(TOWN_GRID_WIDTH):
                block_x = x * (BLOCK_SIZE + STREET_WIDTH) + STREET_WIDTH
                block_y = y * (BLOCK_SIZE + STREET_WIDTH) + STREET_WIDTH
                block_rect = pygame.Rect(block_x, block_y, BLOCK_SIZE, BLOCK_SIZE)
                self.street_blocks.append(
                    {
                        "rect": block_rect,
                        "grid_x": x,
                        "grid_y": y,
                        "occupied": False,
                        "building": None,
                    }
                )

    def _generate_buildings(self):
        """
        在街區中生成各種建築物 - 確保每個街區至少有4棟建築，330個住宅\n
        """
        self.buildings = []

        # 建築物類型及其數量 (使用配置檔案中的設定)
        building_types = [
            {
                "name": "住宅",
                "type": "house",
                "color": (222, 184, 135),
                "count": HOUSE_COUNT,
                "priority": 1,
            },
            {
                "name": "便利商店",
                "type": "shop",
                "color": (160, 82, 45),
                "count": CONVENIENCE_STORE_COUNT,
                "priority": 2,
            },
            {
                "name": "服裝店",
                "type": "clothing_store",
                "color": (218, 165, 32),
                "count": CLOTHING_STORE_COUNT,
                "priority": 2,
            },
            {
                "name": "酒館",
                "type": "tavern",
                "color": (139, 69, 19),
                "count": TAVERN_COUNT,
                "priority": 2,
            },
            {
                "name": "醫院",
                "type": "hospital",
                "color": (255, 255, 255),
                "count": HOSPITAL_COUNT,
                "priority": 2,
            },
            {
                "name": "槍械店",
                "type": "gun_shop",
                "color": (105, 105, 105),
                "count": GUN_SHOP_COUNT,
                "priority": 2,
            },
            {
                "name": "銀行",
                "type": "bank",
                "color": (255, 215, 0),
                "count": BANK_COUNT,
                "priority": 2,
            },
            {
                "name": "學校",
                "type": "school",
                "color": (255, 182, 193),
                "count": SCHOOL_COUNT,
                "priority": 2,
            },
            {
                "name": "教堂",
                "type": "church",
                "color": (147, 112, 219),
                "count": CHURCH_COUNT,
                "priority": 2,
            },
            {
                "name": "公園",
                "type": "park",
                "color": (144, 238, 144),
                "count": PARK_COUNT,
                "priority": 3,
            },
            {
                "name": "辦公大樓",
                "type": "office",
                "color": (169, 169, 169),
                "count": OFFICE_BUILDING_COUNT,
                "priority": 3,
            },
        ]

        # 建立建築物分配清單
        building_queue = []
        for building_type in building_types:
            for _ in range(building_type["count"]):
                building_queue.append(
                    {
                        "name": building_type["name"],
                        "type": building_type["type"],
                        "color": building_type["color"],
                        "priority": building_type["priority"],
                    }
                )

        # 按優先級排序 - 住宅優先
        building_queue.sort(key=lambda x: x["priority"])
        random.shuffle(building_queue)  # 在同優先級內隨機排序

        # 為每個街區分配建築物
        building_index = 0
        for block in self.street_blocks:
            if block["occupied"]:
                continue

            # 每個街區放置 4-6 棟建築物
            buildings_in_block = random.randint(
                BUILDINGS_PER_BLOCK, MAX_BUILDINGS_PER_BLOCK
            )

            # 計算街區內建築物的精確配置，確保不重疊
            building_configs = self._calculate_building_layout(
                buildings_in_block, block["rect"]
            )

            # 記錄當前街區開始前的建築物數量
            block_start_building_count = len(self.buildings)

            # 在街區內放置建築物
            for i, building_config in enumerate(building_configs):
                if building_index >= len(building_queue):
                    # 如果建築物用完了，用住宅填滿剩餘空間
                    building_data = {
                        "name": "住宅",
                        "type": "house",
                        "color": (222, 184, 135),
                        "priority": 1,
                    }
                else:
                    building_data = building_queue[building_index]
                    building_index += 1

                building_rect = building_config["rect"]

                # 安全檢查：確保建築物不會與所有已存在的建築物重疊
                # 檢查整個建築物清單，確保沒有重疊
                collision = False
                for existing_building in self.buildings:
                    if building_rect.colliderect(existing_building["area"]):
                        collision = True
                        break

                if collision:
                    # 發生碰撞，跳過此建築物
                    continue

                # 互動點在建築物前方 (下方)
                interaction_point = (building_rect.centerx, building_rect.bottom + 5)

                building = {
                    "name": building_data["name"],
                    "type": building_data["type"],
                    "area": building_rect,
                    "color": building_data["color"],
                    "interaction_point": interaction_point,
                    "grid_x": block["grid_x"],
                    "grid_y": block["grid_y"],
                    "block_id": f"{block['grid_x']}_{block['grid_y']}",
                }

                self.buildings.append(building)

            # 標記街區為已使用
            block["occupied"] = True
            block["building_count"] = len(self.buildings) - block_start_building_count

    def _calculate_building_layout(self, building_count, block_rect):
        """
        計算街區內建築物的精確布局，確保不重疊\n
        \n
        參數:\n
        building_count (int): 要放置的建築物數量\n
        block_rect (pygame.Rect): 街區矩形區域\n
        \n
        回傳:\n
        list: 建築物配置清單，每個包含位置和尺寸\n
        """
        configs = []

        # 街區內可用空間（扣除加大的邊距）
        margin = BUILDING_MARGIN * 2  # 加大邊距
        usable_width = block_rect.width - margin * 2
        usable_height = block_rect.height - margin * 2
        base_x = block_rect.x + margin
        base_y = block_rect.y + margin

        if building_count == 3:
            # 3個建築物：上排2個，下排1個居中
            gap = BUILDING_MARGIN
            building_width = (usable_width - gap) // 2
            building_height = (usable_height - gap) // 2

            # 上排2個建築物
            configs.append(
                {"rect": pygame.Rect(base_x, base_y, building_width, building_height)}
            )
            configs.append(
                {
                    "rect": pygame.Rect(
                        base_x + building_width + gap,
                        base_y,
                        building_width,
                        building_height,
                    )
                }
            )

            # 下排1個居中建築物
            center_x = base_x + (usable_width - building_width) // 2
            center_y = base_y + building_height + gap
            configs.append(
                {
                    "rect": pygame.Rect(
                        center_x, center_y, building_width, building_height
                    )
                }
            )

        elif building_count == 4:
            # 2x2 配置 - 四個等大的建築物
            gap = BUILDING_MARGIN  # 建築物間的間距
            building_width = (usable_width - gap) // 2
            building_height = (usable_height - gap) // 2

            positions = [(0, 0), (1, 0), (0, 1), (1, 1)]  # 上排  # 下排

            for col, row in positions:
                x = base_x + col * (building_width + gap)
                y = base_y + row * (building_height + gap)
                configs.append(
                    {"rect": pygame.Rect(x, y, building_width, building_height)}
                )

        elif building_count == 5:
            # 2x2 + 1個中央較小建築
            gap = BUILDING_MARGIN
            # 四角的建築稍微小一些，為中央建築留空間
            building_width = (usable_width - gap * 3) // 2
            building_height = (usable_height - gap * 3) // 2

            # 四角建築物
            corner_positions = [(0, 0), (1, 0), (0, 1), (1, 1)]
            for col, row in corner_positions:
                x = base_x + col * (building_width + gap * 1.5)
                y = base_y + row * (building_height + gap * 1.5)
                configs.append(
                    {"rect": pygame.Rect(x, y, building_width, building_height)}
                )

            # 中央小建築 - 確保不重疊
            center_size = min(building_width, building_height) // 2
            center_x = base_x + (usable_width - center_size) // 2
            center_y = base_y + (usable_height - center_size) // 2
            configs.append(
                {"rect": pygame.Rect(center_x, center_y, center_size, center_size)}
            )

        else:  # building_count == 6
            # 3x2 配置 - 六個等大的建築物
            gap = BUILDING_MARGIN
            building_width = (usable_width - gap * 2) // 3
            building_height = (usable_height - gap) // 2

            positions = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]  # 上排  # 下排

            for col, row in positions:
                x = base_x + col * (building_width + gap)
                y = base_y + row * (building_height + gap)
                configs.append(
                    {"rect": pygame.Rect(x, y, building_width, building_height)}
                )

        return configs

    def _check_building_collision(self, new_building_rect):
        """
        檢查新建築物是否與已存在的建築物重疊\n
        \n
        參數:\n
        new_building_rect (pygame.Rect): 新建築物的矩形區域\n
        \n
        回傳:\n
        bool: True 如果有重疊，False 如果沒有重疊\n
        """
        for existing_building in self.buildings:
            if new_building_rect.colliderect(existing_building["area"]):
                return True
        return False

        print(f"建築物生成完成: 總共 {len(self.buildings)} 棟建築物")

        # 統計建築物類型
        building_stats = {}
        for building in self.buildings:
            building_type = building["type"]
            building_stats[building_type] = building_stats.get(building_type, 0) + 1

        print("建築物統計:")
        for building_type, count in building_stats.items():
            type_name = {
                "house": "住宅",
                "shop": "便利商店",
                "clothing_store": "服裝店",
                "tavern": "酒館",
                "hospital": "醫院",
                "gun_shop": "槍械店",
                "bank": "銀行",
                "school": "學校",
                "church": "教堂",
                "park": "公園",
                "office": "辦公大樓",
            }.get(building_type, building_type)
            print(f"  {type_name}: {count} 棟")

    def _create_scene_transitions(self):
        """
        建立場景切換區域 - 在城牆的出入口\n
        """
        self.scene_transitions = [
            {
                "name": "森林入口",
                "target_scene": SCENE_FOREST,
                "area": pygame.Rect(
                    0, TOWN_TOTAL_HEIGHT // 2 - 50, WALL_THICKNESS, 100
                ),
                "color": (34, 139, 34),
                "description": "向西進入森林",
            },
            {
                "name": "湖泊入口",
                "target_scene": SCENE_LAKE,
                "area": pygame.Rect(
                    TOWN_TOTAL_WIDTH - WALL_THICKNESS,
                    TOWN_TOTAL_HEIGHT // 2 - 50,
                    WALL_THICKNESS,
                    100,
                ),
                "color": (0, 191, 255),
                "description": "向東前往湖泊",
            },
            {
                "name": "家入口",
                "target_scene": SCENE_HOME,
                "area": pygame.Rect(
                    TOWN_TOTAL_WIDTH // 2 - 50,
                    TOWN_TOTAL_HEIGHT - WALL_THICKNESS,
                    100,
                    WALL_THICKNESS,
                ),
                "color": (255, 215, 0),
                "description": "向南回家 (可傳送)",
            },
        ]

    def set_entry_from_scene(self, previous_scene_name):
        """
        設定玩家從指定場景進入小鎮時的位置\n
        \n
        參數:\n
        previous_scene_name (str): 前一個場景的名稱\n
        """
        self.entry_from_scene = previous_scene_name

    def enter(self):
        """
        進入小鎮場景\n
        """
        super().enter()

        # 根據前一個場景設定玩家入口位置
        self._set_entry_position()

        print("歡迎來到大型小鎮！")

    def _set_entry_position(self):
        """
        根據前一個場景設定玩家的入口位置\n
        \n
        從不同場景進入時，玩家會出現在對應的城門位置\n
        """
        if hasattr(self, "entry_from_scene") and self.entry_from_scene:
            previous_scene = self.entry_from_scene

            if previous_scene == "森林":
                # 從森林回來，出現在西城門
                self.player.set_position(WALL_THICKNESS + 50, TOWN_TOTAL_HEIGHT // 2)
            elif previous_scene == "湖泊":
                # 從湖泊回來，出現在東城門
                self.player.set_position(
                    TOWN_TOTAL_WIDTH - WALL_THICKNESS - 100, TOWN_TOTAL_HEIGHT // 2
                )
            elif previous_scene == "家":
                # 從家回來，出現在南城門
                self.player.set_position(
                    TOWN_TOTAL_WIDTH // 2, TOWN_TOTAL_HEIGHT - WALL_THICKNESS - 100
                )
            else:
                self._set_default_position()
        else:
            self._set_default_position()

        # 更新攝影機位置跟隨玩家
        self._update_camera()

    def _set_default_position(self):
        """
        設定玩家的預設位置（小鎮中央）\n
        """
        self.player.set_position(
            TOWN_TOTAL_WIDTH // 2 - self.player.width // 2,
            TOWN_TOTAL_HEIGHT // 2 - self.player.height // 2,
        )

    def _update_camera(self):
        """
        更新攝影機位置，讓它跟隨玩家移動\n
        """
        # 攝影機居中跟隨玩家
        target_camera_x = self.player.x - SCREEN_WIDTH // 2
        target_camera_y = self.player.y - SCREEN_HEIGHT // 2

        # 限制攝影機不超出小鎮邊界
        self.camera_x = max(0, min(target_camera_x, TOWN_TOTAL_WIDTH - SCREEN_WIDTH))
        self.camera_y = max(0, min(target_camera_y, TOWN_TOTAL_HEIGHT - SCREEN_HEIGHT))

    def update(self, dt):
        """
        更新小鎮場景邏輯 - 已優化效能\n
        \n
        優化更新順序：優先處理玩家輸入和移動\n
        減少不必要的計算，提升操控響應性\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 記錄玩家移動前的位置
        prev_player_x = self.player.x
        prev_player_y = self.player.y

        # 第一優先級：更新輸入控制器（最重要）
        self.input_controller.update(dt)

        # 第二優先級：更新玩家角色（立即響應輸入）
        self.player.update(dt)

        # 第三優先級：碰撞檢測（使用優化算法）
        self._fast_collision_check(prev_player_x, prev_player_y)

        # 第四優先級：更新攝影機位置
        self._update_camera()

        # 較低優先級：其他系統更新（不影響玩家操控）
        # 使用時間片輪轉，避免每幀都更新所有系統
        frame_count = int(pygame.time.get_ticks() / 16.67)  # 假設60FPS

        if frame_count % 2 == 0:  # 每隔一幀更新道路系統
            self.road_manager.update(dt)

        if frame_count % 3 == 0:  # 每隔兩幀更新載具系統
            current_vehicle = self.vehicle_manager.get_player_vehicle(self.player)
            pedestrians = self.npc_manager.get_nearby_npcs(
                self.player.get_center_position(), 500
            )

            self.vehicle_manager.update(
                dt,
                self.input_controller,
                self.player if current_vehicle else None,
                self.road_manager,
                pedestrians,
            )

        # NPC 系統使用距離優化，只更新附近的 NPC
        player_position = self.player.get_center_position()
        self.npc_manager.update_optimized(dt, player_position)

        # 最低優先級：場景切換和互動檢查
        if frame_count % 4 == 0:  # 每隔三幀檢查一次場景切換
            self._check_scene_transitions()
            self._check_building_interactions()
            self._check_npc_interactions()

    def _fast_collision_check(self, prev_x, prev_y):
        """
        快速碰撞檢測 - 使用空間優化算法\n
        \n
        只檢測玩家附近的建築物，大幅提升效能\n
        使用粗略距離檢測進行預篩選\n
        \n
        參數:\n
        prev_x (float): 玩家移動前的 X 座標\n
        prev_y (float): 玩家移動前的 Y 座標\n
        """
        # 建立玩家當前的碰撞矩形
        player_rect = pygame.Rect(
            self.player.x, self.player.y, self.player.width, self.player.height
        )

        # 定義檢測範圍（只檢查玩家附近的建築物）
        check_distance = 100  # 檢測範圍為100像素
        player_center_x = self.player.x + self.player.width // 2
        player_center_y = self.player.y + self.player.height // 2

        # 快速預篩選：只檢查距離玩家較近的建築物
        collision_detected = False
        for building in self.buildings:
            # 粗略距離檢測（使用曼哈頓距離，比歐幾里得距離快）
            building_center_x = building["area"].centerx
            building_center_y = building["area"].centery

            manhattan_distance = abs(player_center_x - building_center_x) + abs(
                player_center_y - building_center_y
            )

            # 如果距離太遠，跳過精確碰撞檢測
            if manhattan_distance > check_distance:
                continue

            # 精確碰撞檢測
            if player_rect.colliderect(building["area"]):
                collision_detected = True
                break

        # 如果發生碰撞，將玩家移回安全位置
        if collision_detected:
            # 嘗試只回退 X 座標
            self.player.x = prev_x
            player_rect.x = int(self.player.x)

            # 快速檢查只回退 X 是否還有碰撞
            x_collision = False
            for building in self.buildings:
                # 再次使用距離預篩選
                building_center_x = building["area"].centerx
                building_center_y = building["area"].centery

                manhattan_distance = abs(
                    (self.player.x + self.player.width // 2) - building_center_x
                ) + abs((self.player.y + self.player.height // 2) - building_center_y)

                if manhattan_distance > check_distance:
                    continue

                if player_rect.colliderect(building["area"]):
                    x_collision = True
                    break

            if x_collision:
                # 如果還有碰撞，也回退 Y 座標
                self.player.y = prev_y

            # 停止玩家移動方向，防止持續撞牆
            self.player.stop_movement()

        # 確保玩家不會穿越城牆（簡單邊界檢查，效能最佳）
        if self.player.x < WALL_THICKNESS:
            self.player.x = WALL_THICKNESS
        elif self.player.x > TOWN_TOTAL_WIDTH - WALL_THICKNESS - self.player.width:
            self.player.x = TOWN_TOTAL_WIDTH - WALL_THICKNESS - self.player.width

        if self.player.y < WALL_THICKNESS:
            self.player.y = WALL_THICKNESS
        elif self.player.y > TOWN_TOTAL_HEIGHT - WALL_THICKNESS - self.player.height:
            self.player.y = TOWN_TOTAL_HEIGHT - WALL_THICKNESS - self.player.height
            self.player.x = WALL_THICKNESS
        elif self.player.x + self.player.width > TOWN_TOTAL_WIDTH - WALL_THICKNESS:
            self.player.x = TOWN_TOTAL_WIDTH - WALL_THICKNESS - self.player.width

        if self.player.y < WALL_THICKNESS:
            self.player.y = WALL_THICKNESS
        elif self.player.y + self.player.height > TOWN_TOTAL_HEIGHT - WALL_THICKNESS:
            self.player.y = TOWN_TOTAL_HEIGHT - WALL_THICKNESS - self.player.height

        # 更新玩家矩形位置
        self.player.rect.x = int(self.player.x)
        self.player.rect.y = int(self.player.y)

    def _check_scene_transitions(self):
        """
        檢查場景切換 - 檢查玩家是否接觸城門出入口\n
        """
        player_rect = self.player.rect

        for transition in self.scene_transitions:
            if player_rect.colliderect(transition["area"]):
                target_scene = transition["target_scene"]

                if target_scene == SCENE_HOME:
                    # 回家可以直接傳送
                    print(f"傳送回家: {transition['name']}")
                    self.request_scene_change(target_scene)
                    break
                else:
                    # 其他場景需要確認移動方向
                    if self._is_player_moving_towards_transition(transition):
                        print(f"步行前往: {transition['name']}")
                        self.request_scene_change(target_scene)
                        break

    def _is_player_moving_towards_transition(self, transition):
        """
        檢查玩家是否正在向指定方向移動\n
        \n
        參數:\n
        transition (dict): 場景切換區域資料\n
        \n
        回傳:\n
        bool: 是否正在向該方向移動\n
        """
        direction_x = self.player.direction_x
        direction_y = self.player.direction_y

        # 如果玩家沒有移動，不觸發場景切換
        if direction_x == 0 and direction_y == 0:
            return False

        target_scene = transition["target_scene"]

        # 根據目標場景檢查移動方向
        if target_scene == SCENE_FOREST:
            # 森林在西邊，需要向左移動
            return direction_x < 0
        elif target_scene == SCENE_LAKE:
            # 湖泊在東邊，需要向右移動
            return direction_x > 0

        return False

    def _check_building_interactions(self):
        """
        檢查建築物互動\n
        """
        if self.input_controller.is_action_key_just_pressed("interact"):
            player_pos = self.player.get_center_position()

            for building in self.buildings:
                interaction_point = building["interaction_point"]
                distance = math.sqrt(
                    (player_pos[0] - interaction_point[0]) ** 2
                    + (player_pos[1] - interaction_point[1]) ** 2
                )

                if distance < 60:  # 互動範圍
                    self._interact_with_building(building)
                    break

    def _interact_with_building(self, building):
        """
        與建築物互動\n
        \n
        參數:\n
        building (dict): 建築物資料\n
        """
        building_type = building["type"]
        building_name = building["name"]

        print(f"與{building_name}互動")

        interaction_messages = {
            "shop": "便利商店：歡迎光臨！想買些什麼嗎？",
            "clothing_store": "服裝店：我們有最時尚的服裝！",
            "tavern": "酒館：來杯飲料休息一下吧！",
            "hospital": "醫院：需要醫療服務嗎？",
            "gun_shop": "槍械店：合法的武器在這裡！",
            "bank": "銀行：您需要金融服務嗎？",
            "school": "學校：知識改變命運！",
            "church": "教堂：願神保佑你！",
            "park": "公園：享受大自然的美好！",
            "house": "住宅：有人在家嗎？",
            "office": "辦公大樓：商業活動繁忙中...",
        }

        message = interaction_messages.get(building_type, f"{building_name}：您好！")
        print(message)

    def _check_npc_interactions(self):
        """
        檢查 NPC 互動\n
        """
        if self.input_controller.is_action_key_just_pressed("interact"):
            player_pos = self.player.get_center_position()

            # 使用 NPC 管理器查找附近的 NPC
            nearby_npc = self.npc_manager.get_npc_at_position(player_pos, 50)

            if nearby_npc:
                self.npc_manager.interact_with_npc(nearby_npc)

    def draw(self, screen):
        """
        繪製大型小鎮場景\n
        \n
        使用攝影機系統只繪製可見區域的內容\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 清空背景為草地綠色
        screen.fill(GRASS_COLOR)

        # 計算可見區域
        visible_rect = pygame.Rect(
            self.camera_x, self.camera_y, SCREEN_WIDTH, SCREEN_HEIGHT
        )

        # 繪製城牆
        self._draw_walls(screen, visible_rect)

        # 繪製道路網格（舊的簡單街道）
        self._draw_streets(screen, visible_rect)

        # 繪製新的道路系統（人行道、斑馬線、交通號誌）
        self._draw_road_system(screen, visible_rect)

        # 繪製建築物
        self._draw_buildings(screen, visible_rect)

        # 繪製載具系統
        self._draw_vehicles(screen, visible_rect)

        # 繪製場景切換區域（城門）
        self._draw_scene_transitions(screen, visible_rect)

        # 繪製 NPC（相對於攝影機位置）
        # 傳遞實際的攝影機座標，而不是攝影機中心點
        self.npc_manager.draw(
            screen, (self.camera_x, self.camera_y), self.show_npc_info
        )

        # 繪製玩家角色（相對於攝影機位置）
        player_screen_x = self.player.x - self.camera_x
        player_screen_y = self.player.y - self.camera_y

        # 只有當玩家在可見範圍內時才繪製
        if 0 <= player_screen_x < SCREEN_WIDTH and 0 <= player_screen_y < SCREEN_HEIGHT:
            # 暫時移動玩家矩形位置來繪製
            original_rect = self.player.rect.copy()
            self.player.rect.x = player_screen_x
            self.player.rect.y = player_screen_y
            self.player.draw(screen)
            self.player.rect = original_rect

        # 繪製 UI（固定在螢幕上）
        self._draw_ui(screen)

        # 繪製小地圖
        self._draw_minimap(screen)

    def _draw_walls(self, screen, visible_rect):
        """
        繪製城牆\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        visible_rect (pygame.Rect): 可見區域\n
        """
        walls = [
            # 上牆
            pygame.Rect(0, 0, TOWN_TOTAL_WIDTH, WALL_THICKNESS),
            # 下牆
            pygame.Rect(
                0, TOWN_TOTAL_HEIGHT - WALL_THICKNESS, TOWN_TOTAL_WIDTH, WALL_THICKNESS
            ),
            # 左牆
            pygame.Rect(0, 0, WALL_THICKNESS, TOWN_TOTAL_HEIGHT),
            # 右牆
            pygame.Rect(
                TOWN_TOTAL_WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, TOWN_TOTAL_HEIGHT
            ),
        ]

        for wall in walls:
            if wall.colliderect(visible_rect):
                screen_x = wall.x - self.camera_x
                screen_y = wall.y - self.camera_y
                screen_rect = pygame.Rect(screen_x, screen_y, wall.width, wall.height)
                pygame.draw.rect(screen, WALL_COLOR, screen_rect)
                pygame.draw.rect(screen, (0, 0, 0), screen_rect, 2)

    def _draw_streets(self, screen, visible_rect):
        """
        繪製街道網格\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        visible_rect (pygame.Rect): 可見區域\n
        """
        for street in self.streets:
            if street.colliderect(visible_rect):
                screen_x = street.x - self.camera_x
                screen_y = street.y - self.camera_y
                screen_rect = pygame.Rect(
                    screen_x, screen_y, street.width, street.height
                )
                pygame.draw.rect(screen, ROAD_COLOR, screen_rect)

    def _draw_buildings(self, screen, visible_rect):
        """
        繪製建築物\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        visible_rect (pygame.Rect): 可見區域\n
        """
        for building in self.buildings:
            if building["area"].colliderect(visible_rect):
                # 建築物主體
                screen_x = building["area"].x - self.camera_x
                screen_y = building["area"].y - self.camera_y
                screen_rect = pygame.Rect(
                    screen_x, screen_y, building["area"].width, building["area"].height
                )

                pygame.draw.rect(screen, building["color"], screen_rect)
                pygame.draw.rect(screen, (0, 0, 0), screen_rect, 2)

                # 建築物名稱（只在接近時顯示）
                player_distance = math.sqrt(
                    (self.player.x - building["area"].centerx) ** 2
                    + (self.player.y - building["area"].centery) ** 2
                )

                if player_distance < 150:  # 150像素內才顯示名稱
                    text = self.font_manager.render_text(
                        building["name"], 16, (255, 255, 255)
                    )
                    text_rect = text.get_rect(
                        center=(screen_rect.centerx, screen_rect.centery)
                    )
                    screen.blit(text, text_rect)

                # 互動點（只在很接近時顯示）
                if player_distance < 80:
                    interaction_point = building["interaction_point"]
                    screen_interaction_x = interaction_point[0] - self.camera_x
                    screen_interaction_y = interaction_point[1] - self.camera_y
                    pygame.draw.circle(
                        screen,
                        (255, 255, 0),
                        (int(screen_interaction_x), int(screen_interaction_y)),
                        5,
                    )

    def _draw_scene_transitions(self, screen, visible_rect):
        """
        繪製場景切換區域（城門）\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        visible_rect (pygame.Rect): 可見區域\n
        """
        for transition in self.scene_transitions:
            if transition["area"].colliderect(visible_rect):
                screen_x = transition["area"].x - self.camera_x
                screen_y = transition["area"].y - self.camera_y
                screen_rect = pygame.Rect(
                    screen_x,
                    screen_y,
                    transition["area"].width,
                    transition["area"].height,
                )

                pygame.draw.rect(screen, transition["color"], screen_rect)
                pygame.draw.rect(screen, (0, 0, 0), screen_rect, 2)

                # 標籤文字
                text = self.font_manager.render_text(transition["name"], 14, (0, 0, 0))
                text_rect = text.get_rect(center=screen_rect.center)
                screen.blit(text, text_rect)

    def _draw_minimap(self, screen):
        """
        繪製小地圖顯示玩家在城市中的位置\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        minimap_size = 150
        minimap_x = SCREEN_WIDTH - minimap_size - 10
        minimap_y = 10

        # 小地圖背景
        minimap_rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)
        pygame.draw.rect(screen, (0, 0, 0, 128), minimap_rect)
        pygame.draw.rect(screen, (255, 255, 255), minimap_rect, 2)

        # 計算縮放比例
        scale_x = minimap_size / TOWN_TOTAL_WIDTH
        scale_y = minimap_size / TOWN_TOTAL_HEIGHT

        # 繪製城牆
        wall_thickness_scaled = max(1, int(WALL_THICKNESS * scale_x))
        pygame.draw.rect(
            screen,
            WALL_COLOR,
            (minimap_x, minimap_y, minimap_size, wall_thickness_scaled),
        )
        pygame.draw.rect(
            screen,
            WALL_COLOR,
            (
                minimap_x,
                minimap_y + minimap_size - wall_thickness_scaled,
                minimap_size,
                wall_thickness_scaled,
            ),
        )
        pygame.draw.rect(
            screen,
            WALL_COLOR,
            (minimap_x, minimap_y, wall_thickness_scaled, minimap_size),
        )
        pygame.draw.rect(
            screen,
            WALL_COLOR,
            (
                minimap_x + minimap_size - wall_thickness_scaled,
                minimap_y,
                wall_thickness_scaled,
                minimap_size,
            ),
        )

        # 繪製玩家位置
        player_minimap_x = minimap_x + int(self.player.x * scale_x)
        player_minimap_y = minimap_y + int(self.player.y * scale_y)
        pygame.draw.circle(screen, (255, 0, 0), (player_minimap_x, player_minimap_y), 3)

        # 繪製可見範圍
        camera_minimap_x = minimap_x + int(self.camera_x * scale_x)
        camera_minimap_y = minimap_y + int(self.camera_y * scale_y)
        camera_minimap_w = int(SCREEN_WIDTH * scale_x)
        camera_minimap_h = int(SCREEN_HEIGHT * scale_y)
        camera_minimap_rect = pygame.Rect(
            camera_minimap_x, camera_minimap_y, camera_minimap_w, camera_minimap_h
        )
        pygame.draw.rect(screen, (255, 255, 0), camera_minimap_rect, 1)

    def _draw_ui(self, screen):
        """
        繪製使用者介面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 顯示金錢
        money_text = self.font_manager.render_text(
            f"金錢: ${self.player.get_money()}", DEFAULT_FONT_SIZE, (0, 0, 0)
        )
        screen.blit(money_text, (10, 10))

        # 顯示座標（以家為原點）
        relative_x, relative_y = self.player.get_relative_position()
        coord_text = self.font_manager.render_text(
            f"座標: ({relative_x}, {relative_y})", DEFAULT_FONT_SIZE, (0, 0, 0)
        )
        screen.blit(coord_text, (10, 35))

        # 顯示 NPC 系統統計
        stats = self.npc_manager.get_statistics()
        npc_text = self.font_manager.render_text(
            f"NPC: {stats['total_npcs']} 人 | 住院: {stats['injured_npcs']} 人 | 時間: {stats['current_hour']:02d}:00",
            DEFAULT_FONT_SIZE,
            (0, 0, 0),
        )
        screen.blit(npc_text, (10, 60))

        # 顯示電力系統狀態
        font = pygame.font.Font(None, 20)
        self.npc_manager.draw_power_grid_status(screen, font)

        # 繪製物品欄（畫面底下）
        self.player.draw_item_bar(screen)

        # 顯示操作提示
        hint_text = self.font_manager.render_text(
            "E: 互動 | 1-0: 選擇物品欄 | Tab: NPC資訊 | 走到邊界切換場景",
            DEFAULT_FONT_SIZE,
            (0, 0, 0),
        )
        screen.blit(hint_text, (10, SCREEN_HEIGHT - 100))

        # 應用時間系統的視覺效果（天空顏色和光線遮罩）
        self._apply_time_visual_effects(screen)

        # 顯示 NPC 資訊清單（如果開啟）
        if self.show_npc_info:
            self.npc_info_ui.draw(screen)

    def _apply_time_visual_effects(self, screen):
        """
        應用時間系統的視覺效果 - 天空顏色和光線遮罩\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 獲取當前的環境光強度和天空顏色
        ambient_light = self.time_manager.ambient_light
        sky_color = self.time_manager.sky_color

        # 創建光線遮罩（根據環境光強度調整不透明度）
        # 環境光越暗，遮罩越不透明
        overlay_alpha = int((1.0 - ambient_light) * 180)  # 最大180透明度

        if overlay_alpha > 0:
            # 創建半透明遮罩
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(overlay_alpha)

            # 使用深藍色作為夜晚遮罩
            if ambient_light < 0.5:  # 夜晚或黃昏
                overlay.fill((20, 20, 80))  # 深藍色
            else:  # 黎明或傍晚
                overlay.fill((40, 30, 60))  # 紫藍色

            # 應用遮罩
            screen.blit(overlay, (0, 0))

        # 在畫面上方顯示天空顏色帶（可選）
        if sky_color != (135, 206, 235):  # 不是預設的天空藍
            sky_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 30)
            sky_surface = pygame.Surface((SCREEN_WIDTH, 30))
            sky_surface.fill(sky_color)
            sky_surface.set_alpha(100)  # 半透明
            screen.blit(sky_surface, sky_rect)

    def handle_event(self, event):
        """
        處理小鎮場景輸入事件\n
        \n
        參數:\n
        event (pygame.event.Event): 輸入事件\n
        \n
        回傳:\n
        bool: True 表示事件已處理\n
        """
        # 讓輸入控制器處理事件
        action = self.input_controller.handle_event(event)

        # 處理鍵盤事件
        if event.type == pygame.KEYDOWN:
            # 如果 NPC 資訊顯示中，優先處理 UI 事件
            if self.show_npc_info and self.npc_info_ui.handle_keydown(event):
                return True

            if event.key == pygame.K_TAB:
                # Tab 鍵切換 NPC 資訊顯示
                self.show_npc_info = not self.show_npc_info

                # 如果開啟 NPC 資訊，更新清單
                if self.show_npc_info:
                    player_pos = (self.player.x, self.player.y)
                    npc_status_list = self.npc_manager.get_npc_status_list(
                        player_pos, 1000
                    )
                    self.npc_info_ui.update_npc_list(npc_status_list)

                return True
            elif event.key == pygame.K_e:
                # E 鍵與載具互動
                return self._handle_vehicle_interaction()

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

        if action:
            # 移除原本的背包系統
            pass

        return False

    def get_player(self):
        """
        獲取玩家角色實例\n
        \n
        回傳:\n
        Player: 玩家角色物件\n
        """
        return self.player

    def _register_power_workers(self):
        """
        將 NPC 管理器中的電力工人註冊到電力管理系統\n
        \n
        遍歷所有電力工人 NPC，將他們註冊到電力管理器\n
        建立電力工人與電力區域的對應關係\n
        """
        if not self.power_manager:
            return

        # 從 NPC 管理器取得所有電力工人
        power_workers = self.npc_manager.get_power_workers()

        for worker_npc in power_workers:
            worker_id = f"power_worker_{worker_npc.id}"
            worker_info = {
                "npc": worker_npc,
                "skill_level": 1,  # 預設技能等級
            }

            # 註冊到電力管理系統
            self.power_manager.register_power_worker(worker_id, worker_info)

            # 為 NPC 建立與電力系統的連結
            worker_npc.power_manager = self.power_manager
            worker_npc.worker_id = worker_id

        print(f"已註冊 {len(power_workers)} 個電力工人到電力系統")

    def _draw_road_system(self, screen, visible_rect):
        """
        繪製道路系統（人行道、斑馬線、交通號誌）\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        visible_rect (pygame.Rect): 可見區域\n
        """
        # 創建一個臨時表面來繪製道路系統
        temp_surface = pygame.Surface((TOWN_TOTAL_WIDTH, TOWN_TOTAL_HEIGHT))
        temp_surface.fill((0, 255, 0))  # 綠色背景（透明色鍵）
        temp_surface.set_colorkey((0, 255, 0))  # 設定透明色鍵

        # 在臨時表面上繪製道路網絡
        self.road_manager.draw_road_network(temp_surface)

        # 計算要繪製的區域
        source_rect = pygame.Rect(
            visible_rect.x,
            visible_rect.y,
            min(visible_rect.width, TOWN_TOTAL_WIDTH - visible_rect.x),
            min(visible_rect.height, TOWN_TOTAL_HEIGHT - visible_rect.y),
        )

        # 確保座標不超出邊界
        if source_rect.x < TOWN_TOTAL_WIDTH and source_rect.y < TOWN_TOTAL_HEIGHT:
            screen.blit(temp_surface, (0, 0), source_rect)

    def _draw_vehicles(self, screen, visible_rect):
        """
        繪製載具系統\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        visible_rect (pygame.Rect): 可見區域\n
        """
        # 繪製所有載具
        for vehicle in self.vehicle_manager.vehicles:
            # 檢查載具是否在可見範圍內
            vehicle_screen_x = vehicle.x - self.camera_x
            vehicle_screen_y = vehicle.y - self.camera_y

            # 只繪製在螢幕範圍內的載具
            if (
                -50 <= vehicle_screen_x <= SCREEN_WIDTH + 50
                and -50 <= vehicle_screen_y <= SCREEN_HEIGHT + 50
            ):

                # 暫時調整載具位置來繪製
                original_rect = vehicle.rect.copy()
                vehicle.rect.x = vehicle_screen_x
                vehicle.rect.y = vehicle_screen_y
                vehicle.x = vehicle_screen_x
                vehicle.y = vehicle_screen_y

                # 繪製載具
                vehicle.draw(screen)

                # 恢復原始位置
                vehicle.rect = original_rect
                vehicle.x = original_rect.x
                vehicle.y = original_rect.y

    def _handle_vehicle_interaction(self):
        """
        處理載具互動\n
        \n
        回傳:\n
        bool: True 表示事件已處理\n
        """
        player_position = (self.player.x, self.player.y)

        # 檢查玩家是否已經在載具中
        current_vehicle = self.vehicle_manager.get_player_vehicle(self.player)

        if current_vehicle:
            # 玩家已經在載具中，執行下車
            exit_position = current_vehicle.get_off()
            self.player.set_position(exit_position)
            print(f"從 {current_vehicle.name} 下車")
            return True
        else:
            # 玩家不在載具中，尋找附近的載具
            nearby_vehicle = self.vehicle_manager.get_nearby_vehicle(player_position)

            if nearby_vehicle and nearby_vehicle.can_interact(player_position):
                # 嘗試上車
                if nearby_vehicle.get_on(self.player):
                    print(f"上了 {nearby_vehicle.name}")
                    return True
                else:
                    print(f"{nearby_vehicle.name} 已被占用")
                    return True
            else:
                print("附近沒有可用的載具")
                return False
