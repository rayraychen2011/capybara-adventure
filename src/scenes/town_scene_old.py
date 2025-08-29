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
from src.utils.minimap_ui import MinimapUI
from src.utils.time_ui import TimeDisplayUI
from src.systems.npc.npc_manager import NPCManager
from src.systems.road_system import RoadManager
from src.systems.vehicle_system import VehicleManager
from src.systems.tile_system import TileMapManager
from src.systems.terrain_based_system import TerrainBasedSystem
from src.systems.building_label_system import BuildingLabelSystem
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

        # 建立基於地形的系統管理器
        self.terrain_system = TerrainBasedSystem(self.player)
        
        # 載入地形地圖並自動配置所有系統
        terrain_map_path = "config/cupertino_map_edited.csv"
        if not self.terrain_system.load_terrain_map(terrain_map_path):
            print("警告：地形地圖載入失敗，使用預設系統")
            self._setup_fallback_systems()
        else:
            print("地形地圖載入成功，系統自動配置完成")

        # 建立格子地圖系統 (保留用於 NPC 導航)
        self.tile_map = TileMapManager(TOWN_TOTAL_WIDTH, TOWN_TOTAL_HEIGHT, grid_size=20)

        # 建立 NPC 管理器，傳入時間管理器
        self.npc_manager = NPCManager(self.time_manager)

        # 建立道路管理器
        self.road_manager = RoadManager()

        # 建立載具管理器
        self.vehicle_manager = VehicleManager()

        # 建立野生動物管理器
        from src.systems.wildlife.wildlife_manager import WildlifeManager
        self.wildlife_manager = WildlifeManager()

        # 建立狩獵系統
        from src.systems.hunting_system import HuntingSystem
        self.hunting_system = HuntingSystem()

        # 建立射擊系統
        from src.systems.shooting_system import ShootingSystem
        self.shooting_system = ShootingSystem()

        # 定義小鎮邊界 (使用地圖尺寸)
        town_bounds = (
            0, 0, 
            self.terrain_system.map_width * self.terrain_system.tile_size, 
            self.terrain_system.map_height * self.terrain_system.tile_size
        )

        # 更新攝影機和玩家初始位置以符合新地圖
        self.camera_x = 0
        self.camera_y = 0
        self.player.set_position(town_bounds[2] // 2, town_bounds[3] // 2)

        # 創建格子地圖佈局（街道、人行道、斑馬線）- 保留用於 NPC 導航
        self.tile_map.create_town_layout(town_bounds)

        # 建立場景切換區域（移除 - 玩家可直接在地圖上進入不同生態區域）
        # self._create_scene_transitions(town_bounds)

        forest_bounds = (0, 0, SCREEN_WIDTH * 8, SCREEN_HEIGHT * 8)

        # 為 NPC 管理器設定建築物參考
        self.npc_manager.buildings = self.terrain_system.buildings

        # 初始化道路網絡
        self.road_manager.create_road_network_for_town(town_bounds)

        # 初始化載具生成點和車輛管理
        self._setup_vehicle_spawns(town_bounds)

        # 初始化電力網格（如果有電力管理器）
        if self.power_manager:
            self.power_manager.initialize_power_grid(town_bounds)

        # 初始化所有 NPC（建築物已經存在）
        self.npc_manager.initialize_npcs(town_bounds, forest_bounds)

        # 為 NPC 設定建築物參考，用於碰撞檢測
        self.npc_manager.set_buildings_reference(self.terrain_system.buildings)

        # 為 NPC 設定道路系統參考，用於智能路徑規劃
        self.npc_manager.set_road_system_reference(self.road_manager)

        # 為 NPC 設定格子地圖參考，用於路徑限制
        self.npc_manager.set_tile_map_reference(self.tile_map)

        # 將電力工人註冊到電力系統
        if self.power_manager:
            self._register_power_workers()

        # 設置野生動物系統
        self._setup_wildlife_system(town_bounds)

        # 生成初始載具
        self.vehicle_manager.spawn_initial_vehicles()

        # NPC 資訊顯示控制
        self.show_npc_info = False

        # NPC 資訊顯示器
        self.npc_info_ui = NPCInfoUI()

        # 小地圖系統
        self.minimap_ui = MinimapUI()

        # 時間顯示UI系統（頂部中央顯示）
        self.time_ui = TimeDisplayUI(position="top_center", style="compact")

        # 建築標籤系統
        self.building_label_system = BuildingLabelSystem()

        # 商店管理系統
        from src.systems.shop_system import ShopUI
        self.shop_manager = type('ShopManager', (), {'shop_ui': ShopUI()})()

        print("大型小鎮場景已建立 (基於地形系統)")

    def _setup_wildlife_system(self, town_bounds):
        """
        設置野生動物系統\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界\n
        """
        # 設置地形系統引用
        self.wildlife_manager.set_terrain_system(self.terrain_system)
        
        # 設置棲息地邊界（從地形系統獲取森林和湖泊區域）
        forest_areas = self.terrain_system.get_areas_by_terrain_type(1)  # 森林地形代碼1
        lake_areas = self.terrain_system.get_areas_by_terrain_type(2)    # 湖泊地形代碼2
        
        if forest_areas:
            # 使用第一個最大的森林區域
            largest_forest = max(forest_areas, key=lambda area: area[2] * area[3])
            self.wildlife_manager.set_habitat_bounds(largest_forest, lake_areas[0] if lake_areas else (0, 0, 100, 100))
        else:
            # 備用森林和湖泊區域
            forest_bounds = (100, 100, 800, 600)
            lake_bounds = (1000, 200, 400, 300)
            self.wildlife_manager.set_habitat_bounds(forest_bounds, lake_bounds)
        
        # 初始化野生動物群體
        self.wildlife_manager.initialize_animals("all")
        
        # 設置玩家攻擊回調
        self.wildlife_manager.set_player_attack_callback(self._handle_animal_attack_player)
        
        print("野生動物系統設置完成")

    def _handle_animal_attack_player(self, damage, animal):
        """
        處理動物攻擊玩家事件\n
        \n
        參數:\n
        damage (int): 傷害值\n
        animal (Animal): 攻擊的動物\n
        """
        # 讓玩家受到傷害
        self.player.take_damage(damage)
        print(f"🐾 {animal.animal_type.value} 攻擊了你！造成 {damage} 點傷害")
        
        # 動物攻擊後重置標記
        animal.has_attacked_player = False
        animal.attack_damage = 0

    def _handle_hunt_result(self, hunt_result):
        """
        處理狩獵結果\n
        \n
        參數:\n
        hunt_result (dict): 狩獵結果\n
        """
        if hunt_result["hit"] and hunt_result["kill"]:
            if hunt_result.get("protected", False):
                # 保育類動物懲罰
                penalty = hunt_result["penalty"]
                self.player.money += penalty["money"]  # 罰款（負數）
                print(f"💸 保育類動物罰款: ${abs(penalty['money'])}")
            else:
                # 正常狩獵獎勵
                rewards = hunt_result["rewards"]
                self.player.money += rewards["money"]
                print(f"💰 狩獵獎勵: ${rewards['money']}")

    def _handle_tree_chopping(self):
        """
        處理砍伐樹木（Q鍵）\n
        \n
        回傳:\n
        bool: True 表示事件已處理\n
        """
        # 檢查玩家是否裝備斧頭
        if not self.player.can_chop():
            print("❌ 砍伐樹木需要裝備斧頭！請按中鍵選擇武器")
            return True
        
        # 尋找玩家附近的樹木
        player_pos = self.player.get_center_position()
        player_rect = pygame.Rect(player_pos[0] - 40, player_pos[1] - 40, 80, 80)
        
        # 檢查森林區域中的樹木
        trees_to_chop = []
        for forest_area in self.terrain_system.forest_areas:
            for tree in forest_area['trees']:
                tree_rect = tree['collision_rect']
                if player_rect.colliderect(tree_rect):
                    trees_to_chop.append((forest_area, tree))
        
        if trees_to_chop:
            # 砍伐第一棵樹
            forest_area, tree = trees_to_chop[0]
            
            # 從森林區域中移除樹木
            forest_area['trees'].remove(tree)
            
            print("🪓 樹木被砍倒了！")
            # 可以添加木材獎勵
            self.player.money += 20  # 木材獎勵
            print("💰 獲得木材獎勵: $20")
        else:
            print("❌ 附近沒有樹木可以砍伐")
        
        return True

    def _handle_building_click(self, mouse_pos, camera_offset):
        """
        處理建築物點擊\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠位置\n
        camera_offset (tuple): 攝影機偏移量\n
        \n
        回傳:\n
        bool: True 表示事件已處理\n
        """
        # 將滑鼠位置轉換為世界座標
        world_x = mouse_pos[0] + camera_offset[0]
        world_y = mouse_pos[1] + camera_offset[1]
        
        # 檢查是否點擊了建築物
        clicked_building = None
        for building in self.terrain_system.buildings:
            if building.rect.collidepoint(world_x, world_y):
                clicked_building = building
                break
        
        if clicked_building:
            print(f"🏢 點擊建築物: {clicked_building.building_type}")
            # 處理建築物互動（已有的邏輯）
            # 這裡可以加入原有的商店界面等
            return True
        
        return False

    def _setup_fallback_systems(self):
        """
        設置備用系統（當地形地圖載入失敗時使用）\n
        """
        print("設置備用系統...")
        # 這裡可以保留原本的建築生成邏輯作為備用

    def _setup_vehicle_spawns(self, town_bounds):
        """
        設置載具生成點\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界\n
        """
        # 在地圖邊緣創建 AI 載具生成點
        self.vehicle_manager.create_map_edge_spawns(town_bounds)

        # 使用地形系統的停車場作為玩家載具停車點
        parking_spots = self.terrain_system.get_parking_spots_in_area(
            (town_bounds[2] // 2, town_bounds[3] // 2), 
            max(town_bounds[2], town_bounds[3]) // 2
        )

        # 從停車場中選擇一些位置作為玩家可用的載具停車點
        for i, spot in enumerate(parking_spots[:20]):  # 限制20個玩家載具停車點
            if not spot['occupied']:  # 只使用空的停車位
                vehicle_types = ["car", "bike", "motorcycle"]
                self.vehicle_manager.add_spawn_point(
                    spot['position'], vehicle_types, is_ai_spawn=False
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
                # 並且檢查格子地圖是否允許建造
                collision = False
                for existing_building in self.buildings:
                    if building_rect.colliderect(existing_building["area"]):
                        collision = True
                        break

                # 使用格子地圖檢查是否可以建造
                if not collision:
                    can_place, error_msg = self.tile_map.can_place_building(
                        building_rect.x, building_rect.y, 
                        building_rect.width, building_rect.height
                    )
                    if not can_place:
                        collision = True
                        print(f"建築放置被格子地圖拒絕: {error_msg}")

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

                # 在格子地圖上標記建築物
                self.tile_map.place_building(
                    building_rect.x, building_rect.y, 
                    building_rect.width, building_rect.height
                )

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

    def _create_scene_transitions(self, town_bounds):
        """
        建立場景切換區域 - 在地圖邊界\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界 (x, y, width, height)\n
        """
        tx, ty, tw, th = town_bounds
        
        self.scene_transitions = [
            {
                "name": "森林入口",
                "target_scene": SCENE_FOREST,
                "area": pygame.Rect(tx, th // 2 - 50, 50, 100),
                "color": (34, 139, 34),
                "description": "向西進入森林",
            },
            {
                "name": "湖泊入口", 
                "target_scene": SCENE_LAKE,
                "area": pygame.Rect(tx + tw - 50, th // 2 - 50, 50, 100),
                "color": (0, 191, 255),
                "description": "向東前往湖泊",
            },
            {
                "name": "家入口",
                "target_scene": SCENE_HOME,
                "area": pygame.Rect(tw // 2 - 50, ty + th - 50, 100, 50),
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
        # 計算地圖尺寸
        map_width = self.terrain_system.map_width * self.terrain_system.tile_size
        map_height = self.terrain_system.map_height * self.terrain_system.tile_size
        
        # 攝影機居中跟隨玩家
        target_camera_x = self.player.x - SCREEN_WIDTH // 2
        target_camera_y = self.player.y - SCREEN_HEIGHT // 2

        # 限制攝影機不超出地圖邊界
        self.camera_x = max(0, min(target_camera_x, map_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(target_camera_y, map_height - SCREEN_HEIGHT))

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

        # 更新時間UI
        if self.time_manager:
            self.time_ui.update(dt)

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

        # 更新狩獵和射擊系統
        self.shooting_system.update(dt)
        self.hunting_system.update_targeting(dt)
        
        # 更新狩獵目標選擇（如果在狩獵模式）
        if self.hunting_system.hunting_mode_active:
            mouse_pos = pygame.mouse.get_pos()
            camera_offset = (self.camera_x, self.camera_y)
            animals_in_range = self.hunting_system.find_animals_in_range(
                player_position, self.wildlife_manager
            )
            self.hunting_system.update_target_selection(mouse_pos, camera_offset, animals_in_range)

        # 更新野生動物系統
        if frame_count % 2 == 0:  # 每隔一幀更新野生動物
            self.wildlife_manager.update(dt, player_position, "town")
            
            # 檢查動物攻擊玩家
            for animal in self.wildlife_manager.animals:
                if animal.has_attacked_player:
                    self._handle_animal_attack_player(animal.attack_damage, animal)

        # 檢查子彈與動物的碰撞
        if self.shooting_system.get_bullet_count() > 0:
            bullet_hits = self.shooting_system.check_bullet_collisions(self.wildlife_manager.animals)
            for hit_info in bullet_hits:
                print(f"💥 子彈命中 {hit_info['target'].animal_type.value}！")

        # 最低優先級：互動檢查（移除場景切換檢查）
        if frame_count % 4 == 0:  # 每隔三幀檢查一次
            # 移除 self._check_scene_transitions() - 改由地形系統處理生態切換
            self._check_building_interactions()
            self._check_npc_interactions()
            self._check_terrain_ecology_zones()

    def _fast_collision_check(self, prev_x, prev_y):
        """
        快速碰撞檢測 - 使用地形系統進行建築碰撞檢測\n
        \n
        參數:\n
        prev_x (float): 玩家移動前的 X 座標\n
        prev_y (float): 玩家移動前的 Y 座標\n
        """
        # 建立玩家當前的碰撞矩形
        player_rect = pygame.Rect(
            self.player.x, self.player.y, self.player.width, self.player.height
        )

        # 使用地形系統獲取附近的建築物
        player_center = (self.player.x + self.player.width // 2, 
                        self.player.y + self.player.height // 2)
        nearby_buildings = self.terrain_system.get_buildings_in_area(player_center, 100)

        # 檢查建築物碰撞
        collision_detected = False
        for building in nearby_buildings:
            building_rect = pygame.Rect(building.x, building.y, building.width, building.height)
            if player_rect.colliderect(building_rect):
                collision_detected = True
                break

        # 如果發生碰撞，將玩家移回安全位置
        if collision_detected:
            # 嘗試只回退 X 座標
            self.player.x = prev_x
            player_rect.x = int(self.player.x)

            # 快速檢查只回退 X 是否還有碰撞
            x_collision = False
            for building in nearby_buildings:
                building_rect = pygame.Rect(building.x, building.y, building.width, building.height)
                if player_rect.colliderect(building_rect):
                    x_collision = True
                    break

            if x_collision:
                # 如果還有碰撞，也回退 Y 座標
                self.player.y = prev_y

            # 停止玩家移動方向，防止持續撞牆
            self.player.stop_movement()

        # 確保玩家不會超出地圖邊界
        map_width = self.terrain_system.map_width * self.terrain_system.tile_size
        map_height = self.terrain_system.map_height * self.terrain_system.tile_size
        
        if self.player.x < 0:
            self.player.x = 0
        elif self.player.x + self.player.width > map_width:
            self.player.x = map_width - self.player.width

        if self.player.y < 0:
            self.player.y = 0
        elif self.player.y + self.player.height > map_height:
            self.player.y = map_height - self.player.height

        # 更新玩家矩形位置
        self.player.rect.x = int(self.player.x)
        self.player.rect.y = int(self.player.y)

    def _check_terrain_ecology_zones(self):
        """
        檢查玩家是否進入特定地形的生態區域\n
        \n
        根據 target.prompt.md 要求：\n
        - 湖泊生態在 terrain code 2 (水體) 區域\n
        - 森林生態在 terrain code 1 (森林) 區域\n
        - 玩家直接踏入這些區域即可體驗對應生態\n
        """
        player_pos = self.player.get_center_position()
        
        # 獲取玩家當前位置的地形類型
        terrain_type = self.terrain_system.get_terrain_at_position(player_pos[0], player_pos[1])
        
        # 避免重複訊息，只在地形類型改變時顯示
        if not hasattr(self, 'last_terrain_type'):
            self.last_terrain_type = None
            
        if terrain_type != self.last_terrain_type:
            if terrain_type == 1:  # 森林區域
                # 玩家進入森林生態區域
                print("🌲 進入森林生態區域 - Stevens Creek County Park 森林區")
                # 這裡可以啟動森林相關的生態系統或效果
                # 例如：顯示森林動物、改變音效、調整光線等
                
            elif terrain_type == 2:  # 水體區域  
                # 玩家進入湖泊生態區域
                print("🏞️ 進入湖泊生態區域 - Stevens Creek 溪流")
                # 這裡可以啟動湖泊相關的生態系統或效果
                # 例如：顯示水生動物、釣魚功能、水聲效果等
                
            elif terrain_type == 0:  # 草地區域
                if self.last_terrain_type in [1, 2]:  # 從特殊生態區域離開
                    print("🌱 回到普通草地區域")
                    
            self.last_terrain_type = terrain_type

    def _check_scene_transitions(self):
        """
        檢查場景切換 - 已移除傳送門功能\n
        \n
        根據 target.prompt.md 要求，移除場景傳送門\n
        玩家現在通過直接踏入地形區域來體驗不同生態\n
        """
        # 移除原有的場景切換邏輯
        # 改由 _check_terrain_ecology_zones 處理生態區域體驗
        pass

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
        檢查建築物互動 - 使用地形系統\n
        """
        if self.input_controller.is_action_key_just_pressed("interact"):
            player_pos = self.player.get_center_position()

            # 使用地形系統獲取附近的建築
            nearby_buildings = self.terrain_system.get_buildings_in_area(player_pos, 60)

            for building in nearby_buildings:
                # 計算到建築中心的距離
                building_center = (building.x + building.width // 2, building.y + building.height // 2)
                distance = math.sqrt(
                    (player_pos[0] - building_center[0]) ** 2 +
                    (player_pos[1] - building_center[1]) ** 2
                )

                if distance < 60:  # 互動範圍
                    self._interact_with_terrain_building(building)
                    break

    def _interact_with_terrain_building(self, building):
        """
        與地形系統的建築物互動\n
        \n
        參數:\n
        building (Building): 建築物物件\n
        """
        building_type = building.building_type
        building_name = building.name

        print(f"與{building_name}互動")

        # 根據建築類型執行不同的互動邏輯
        if hasattr(building, 'interact'):
            # 如果建築有自定義互動方法
            result = building.interact(self.player)
            if result.get('success'):
                print(result.get('message', '互動成功'))
            else:
                print(result.get('message', '無法互動'))
        else:
            # 商店類型建築開啟商業界面
            if building_type in ["gun_shop", "convenience_store", "street_vendor", "clothing_store"]:
                print(f"調試: 偵測到商店類型建築 {building_type}，準備開啟商業界面")
                self._open_shop_interface(building_type, building_name)
            elif building_type == "church":
                # 教堂特殊處理 - 切換到教堂內部場景
                print(f"進入{building_name}")
                self.transition_target = "教堂內部"
            else:
                # 預設互動訊息
                interaction_messages = {
                    "hospital": f"{building_name}：醫院為您服務，需要治療嗎？", 
                    "fishing_shop": f"{building_name}：釣魚用品應有盡有！",
                    "market": f"{building_name}：新鮮商品，快來選購！",
                    "power_plant": f"{building_name}：電力供應中心，請勿靠近！",
                    "residential": f"{building_name}：這是私人住宅。"
                }

                message = interaction_messages.get(building_type, f"{building_name}：您好！")
                print(message)

    def _open_shop_interface(self, shop_type, shop_name):
        """
        開啟商店界面\n
        \n
        參數:\n
        shop_type (str): 商店類型\n
        shop_name (str): 商店名稱\n
        """
        print(f"調試: _open_shop_interface 被呼叫，shop_type={shop_type}, shop_name={shop_name}")
        
        # 根據商店類型獲取商品列表
        items = self._get_shop_items(shop_type)
        print(f"調試: 獲取到商品列表，數量={len(items)}")
        
        # 獲取玩家金錢（假設玩家有金錢屬性）
        player_money = getattr(self.player, 'money', 1000)  # 預設1000金錢
        print(f"調試: 玩家金錢={player_money}")
        
        # 顯示商店UI
        self.shop_manager.shop_ui.show(shop_name, items, player_money)
        print(f"開啟{shop_name}商業界面")

    def _get_shop_items(self, shop_type):
        """
        根據商店類型獲取商品列表\n
        \n
        參數:\n
        shop_type (str): 商店類型\n
        \n
        回傳:\n
        list: 商品列表\n
        """
        shop_items = {
            "gun_shop": [
                {"name": "手槍", "price": 500, "description": "可靠的近距離武器"},
                {"name": "步槍", "price": 1200, "description": "精準的遠距離武器"},
                {"name": "獵槍", "price": 800, "description": "適合狩獵的武器"},
                {"name": "子彈包", "price": 50, "description": "50發子彈"},
            ],
            "convenience_store": [
                {"name": "小型血量藥水", "price": 50, "description": "回復50點血量"},
                {"name": "中型血量藥水", "price": 150, "description": "回復150點血量"},
                {"name": "大型血量藥水", "price": 300, "description": "回復300點血量"},
                {"name": "能量飲料", "price": 25, "description": "短暫提升移動速度"},
            ],
            "street_vendor": [
                {"name": "路邊便當", "price": 30, "description": "便宜的填飽肚子選擇"},
                {"name": "小點心", "price": 15, "description": "解饞的小零食"},
                {"name": "涼飲", "price": 20, "description": "解渴的冰涼飲料"},
            ],
            "clothing_store": [
                {"name": "日常套裝", "price": 300, "description": "舒適的日常穿著"},
                {"name": "工作服", "price": 400, "description": "適合工作的耐用服裝"},
                {"name": "正式套裝", "price": 800, "description": "正式場合穿著"},
                {"name": "休閒服", "price": 250, "description": "輕鬆的休閒穿著"},
                {"name": "運動服", "price": 350, "description": "適合運動的服裝"},
            ]
        }
        
        return shop_items.get(shop_type, [])

    def _handle_purchase(self, purchase_result):
        """
        處理購買結果\n
        \n
        參數:\n
        purchase_result (dict): 購買結果，包含item和成功狀態\n
        """
        if purchase_result and purchase_result.get('action') == 'buy':
            item = purchase_result.get('item')
            
            # 使用玩家的 spend_money 方法
            if self.player.spend_money(item['price']):
                # 購買成功，更新商店UI中的金錢顯示
                self.shop_manager.shop_ui.update_player_money(self.player.money)
                
                # 根據物品類型處理
                if item['name'] in ["手槍", "步槍", "獵槍"]:
                    # 武器類物品，添加到玩家武器庫
                    print(f"獲得武器：{item['name']}")
                elif "血量藥水" in item['name']:
                    # 血量藥水，直接使用
                    heal_amount = item.get('heal_amount', 50)
                    if hasattr(self.player, 'health'):
                        self.player.health = min(self.player.max_health, self.player.health + heal_amount)
                    print(f"使用{item['name']}，回復{heal_amount}點血量")
                else:
                    # 其他物品
                    print(f"購買了：{item['name']}")
            else:
                print("購買失敗：金錢不足")
        else:
            print("購買失敗：無效的購買動作")

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
        繪製大型小鎮場景 - 使用地形系統\n
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

        # 繪製地形層（背景）
        self.terrain_system.draw_terrain_layer(screen, self.camera_x, self.camera_y)

        # 繪製森林元素
        self.terrain_system.draw_forest_elements(screen, self.camera_x, self.camera_y)

        # 繪製水體元素
        self.terrain_system.draw_water_elements(screen, self.camera_x, self.camera_y)

        # 繪製蔬果園（新增）
        self.terrain_system.draw_vegetable_gardens(screen, self.camera_x, self.camera_y)

        # 繪製建築物
        self.terrain_system.draw_buildings(screen, self.camera_x, self.camera_y)

        # 繪製建築標籤（只為住宅顯示「家」）
        buildings = getattr(self.terrain_system, 'buildings', [])
        self.building_label_system.draw_all_building_labels(screen, buildings, self.camera_x, self.camera_y)

        # 繪製停車場車輛
        self.terrain_system.draw_vehicles(screen, self.camera_x, self.camera_y)

        # 繪製道路系統（人行道、斑馬線、交通號誌）
        self._draw_road_system(screen, visible_rect)

        # 繪製載具系統（動態車輛）
        self._draw_vehicles(screen, visible_rect)

        # 移除場景切換區域繪製（已刪除傳送門功能）
        # self._draw_scene_transitions(screen, visible_rect)

        # 繪製 NPC（相對於攝影機位置）
        self.npc_manager.draw(
            screen, (self.camera_x, self.camera_y), self.show_npc_info
        )

        # 繪製野生動物
        if hasattr(self, 'wildlife_manager'):
            for animal in self.wildlife_manager.animals:
                animal.draw(screen, (self.camera_x, self.camera_y))

        # 繪製子彈
        if hasattr(self, 'shooting_system'):
            self.shooting_system.draw_bullets(screen, (self.camera_x, self.camera_y))

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

        # 繪製狩獵目標指示器（在狩獵模式時）
        if hasattr(self, 'hunting_system') and self.hunting_system.hunting_mode_active:
            player_position = self.player.get_center_position()
            animals_in_range = self.hunting_system.find_animals_in_range(
                player_position, self.wildlife_manager
            )
            self.hunting_system.draw_target_indicators(
                screen, (self.camera_x, self.camera_y), animals_in_range
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

        # 繪製時間顯示（螢幕頂部中央）
        if self.time_manager:
            self.time_ui.draw(screen, self.time_manager)

        # 繪製小地圖
        self._draw_minimap(screen)

    def _draw_minimap(self, screen):
        """
        繪製小地圖\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 獲取玩家位置和面朝方向
        player_x, player_y = self.player.get_position()
        facing_direction = self.player.facing_direction
        
        # 獲取建築物資料
        buildings = getattr(self.terrain_system, 'buildings', [])
        
        # 獲取地形資料（修正：使用map_data而不是terrain_data）
        terrain_data = getattr(self.terrain_system, 'map_data', None)
        
        # 小地圖調試訊息
        if terrain_data:
            print(f"小地圖調試 - 有地形資料, 建築數量: {len(buildings)}")
        else:
            print("小地圖調試 - 沒有地形資料")
        
        # 繪製小地圖
        self.minimap_ui.draw(screen, player_x, player_y, facing_direction, buildings, terrain_data)

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
        繪製小地圖顯示玩家在城市中的位置 - 使用地形系統\n
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
        map_width = self.terrain_system.map_width * self.terrain_system.tile_size
        map_height = self.terrain_system.map_height * self.terrain_system.tile_size
        scale_x = minimap_size / map_width
        scale_y = minimap_size / map_height

        # 繪製地形縮圖
        temp_minimap = pygame.Surface((minimap_size, minimap_size))
        temp_minimap.fill((0, 0, 0))
        
        # 使用地形載入器繪製小地圖
        scale = max(1, int(minimap_size / max(self.terrain_system.map_width, self.terrain_system.map_height)))
        self.terrain_system.terrain_loader.render_minimap(temp_minimap, scale)
        
        # 將小地圖貼到螢幕上
        screen.blit(temp_minimap, (minimap_x, minimap_y))

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
        from src.utils.font_manager import get_font_manager
        font_manager = get_font_manager()
        font = font_manager.get_font(20)
        self.npc_manager.draw_power_grid_status(screen, font)

        # 繪製物品欄（畫面底下）
        self.player.draw_item_bar(screen)

        # 操作提示已移除

        # 應用時間系統的視覺效果（天空顏色和光線遮罩）
        self._apply_time_visual_effects(screen)

        # 顯示 NPC 資訊清單（如果開啟）
        if self.show_npc_info:
            self.npc_info_ui.draw(screen)

        # 顯示商店UI（如果開啟）
        if self.shop_manager.shop_ui.is_visible:
            self.shop_manager.shop_ui.draw(screen)

        # 繪製狩獵UI（如果在狩獵模式）
        if hasattr(self, 'hunting_system'):
            font = self.font_manager.get_font(20)
            mouse_pos = pygame.mouse.get_pos()
            self.hunting_system.draw_hunting_ui(screen, font, mouse_pos)

        # 繪製射擊UI
        if hasattr(self, 'shooting_system'):
            self.shooting_system.draw_shooting_ui(screen, self.player)

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
        # 處理商店UI事件（優先處理）
        if self.shop_manager.shop_ui.is_visible:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左鍵點擊
                    purchase_result = self.shop_manager.shop_ui.handle_mouse_click(event.pos)
                    if purchase_result:
                        # 處理購買結果
                        self._handle_purchase(purchase_result)
                    return True
                elif event.button == 3:  # 右鍵關閉商店
                    self.shop_manager.shop_ui.hide()
                    return True
            elif event.type == pygame.MOUSEMOTION:
                self.shop_manager.shop_ui.handle_mouse_move(event.pos)
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC鍵關閉商店
                    self.shop_manager.shop_ui.hide()
                    return True

        # 讓輸入控制器處理事件
        action = self.input_controller.handle_event(event)

        # 處理狩獵和武器相關事件
        if action == "hunting":
            # G鍵切換狩獵模式
            self.hunting_system.toggle_hunting_mode(self.player)
            return True
        elif action == "chop_tree":
            # Q鍵砍伐樹木
            return self._handle_tree_chopping()
        elif action == "left_click":
            # 左鍵點擊處理
            mouse_pos = pygame.mouse.get_pos()
            camera_offset = (self.camera_x, self.camera_y)
            
            # 如果在狩獵模式，嘗試狩獵
            if self.hunting_system.hunting_mode_active:
                hunt_result = self.hunting_system.attempt_hunt(
                    self.player, self.shooting_system, mouse_pos, camera_offset
                )
                if hunt_result["success"]:
                    self._handle_hunt_result(hunt_result)
                return True
            else:
                # 檢查是否點擊了建築物（原有邏輯）
                return self._handle_building_click(mouse_pos, camera_offset)
        elif action == "weapon_wheel":
            # 中鍵切換武器圓盤
            self.player.weapon_wheel_visible = not self.player.weapon_wheel_visible
            return True

        # 處理小地圖事件
        if action == "middle_click":
            # 中鍵點擊切換小地圖顯示
            self.minimap_ui.toggle_visibility()
            return True
        elif action == "scroll_up" or action == "scroll_down":
            # 滑鼠滾輪縮放小地圖 (只有在小地圖顯示時才有效)
            if self.minimap_ui.is_visible:
                scroll_direction = 1 if action == "scroll_up" else -1
                self.minimap_ui.handle_scroll(scroll_direction)
                return True

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
