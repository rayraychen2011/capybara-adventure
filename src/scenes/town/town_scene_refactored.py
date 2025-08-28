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
from src.utils.npc_status_ui import NPCStatusDisplayUI  # 新增NPC狀態顯示
from src.utils.minimap_ui import MinimapUI
from src.utils.time_ui import TimeDisplayUI
from src.utils.equipment_wheel_ui import EquipmentWheelUI
from src.systems.npc.npc_manager import NPCManager
from src.systems.road_system import RoadManager
from src.systems.vehicle_system import VehicleManager
from src.systems.tile_system import TileMapManager
from src.systems.terrain_based_system import TerrainBasedSystem
from src.systems.wildlife.wildlife_manager import WildlifeManager  # 新增野生動物管理器
from src.systems.fishing_system import FishingSystem  # 新增釣魚系統
from src.systems.bait_shop_system import BaitShopManager  # 新增魚餌店系統
from src.systems.convenience_store_health_system import ConvenienceStoreHealthSystem  # 新增便利商店血量藥水
from src.systems.anti_overlap_system import AntiOverlapTeleportSystem  # 新增防重疊系統
from src.scenes.town.town_camera_controller import TownCameraController
from src.scenes.town.town_ui_manager import TownUIManager
from src.scenes.town.town_interaction_handler import TownInteractionHandler
from src.utils.house_interior_ui import HouseInteriorUI
from src.utils.fishing_ui import FishingUI  # 新增釣魚 UI
from src.utils.fishing_choice_ui import FishingChoiceUI  # 新增釣魚選擇 UI
from config.settings import *


######################小鎮場景（重構版）######################
class TownScene(Scene):
    """
    小鎮場景 - 重構後的簡化版本\n
    \n
    此場景作為協調器，將原本龐大的功能拆分到專門的管理器中：\n
    - TownCameraController: 攝影機控制\n
    - TownUIManager: UI 管理\n
    - TownInteractionHandler: 互動處理\n
    \n
    主要職責：\n
    1. 初始化所有子系統\n
    2. 協調系統間的通訊\n
    3. 處理場景級別的更新和繪製\n
    4. 管理場景狀態轉換\n
    """

    def __init__(self, state_manager, time_manager=None, power_manager=None):
        """
        初始化小鎮場景\n
        \n
        參數:\n
        state_manager (StateManager): 遊戲狀態管理器\n
        time_manager (TimeManager): 時間管理器\n
        power_manager (PowerManager): 電力管理器\n
        """
        print("=== TownScene.__init__ 開始 ===")
        super().__init__("小鎮")
        self.state_manager = state_manager
        self.time_manager = time_manager
        self.power_manager = power_manager

        print("開始初始化小鎮場景...")

        # 建立玩家角色
        self._initialize_player()

        # 建立核心系統
        self._initialize_core_systems()

        # 建立專門的管理器
        self._initialize_managers()

        # 設定系統間的依賴關係
        self._setup_system_dependencies()

        # 設定玩家的地形系統引用（用於碰撞檢測）
        self.player.set_terrain_system(self.terrain_system)

        # 初始化場景內容
        self._initialize_scene_content()

        print("小鎮場景初始化完成")

    def _initialize_player(self):
        """
        初始化玩家角色\n
        """
        # 創建玩家，初始位置稍後會設定為玩家之家
        self.player = Player()  # 不指定初始位置，稍後設定
        self.input_controller = InputController(self.player)

    def _initialize_core_systems(self):
        """
        初始化核心遊戲系統\n
        """
        print("開始初始化核心系統...")
        
        # 建立基於地形的系統管理器
        self.terrain_system = TerrainBasedSystem(self.player)
        print("TerrainBasedSystem 已創建")
        
        # 載入地形地圖
        terrain_map_path = "config/cupertino_map_edited.csv"
        print(f"嘗試載入地形地圖: {terrain_map_path}")
        
        if not self.terrain_system.load_terrain_map(terrain_map_path):
            print("警告：地形地圖載入失敗，使用預設系統")
            self._setup_fallback_systems()
        else:
            print("地形地圖載入成功！")

        # 建立格子地圖系統（保留用於 NPC 導航）
        self.tile_map = TileMapManager(TOWN_TOTAL_WIDTH, TOWN_TOTAL_HEIGHT, grid_size=20)
        print("TileMapManager 已創建")

        # 建立其他核心系統
        self.npc_manager = NPCManager(self.time_manager)
        self.road_manager = RoadManager()
        self.vehicle_manager = VehicleManager()
        
        # 建立野生動物管理器 - 管理地形代碼1區域的動物
        self.wildlife_manager = WildlifeManager()
        self.wildlife_manager.set_terrain_system(self.terrain_system)  # 連結地形系統
        self._setup_wildlife_bounds()
        
        # 建立釣魚系統 - 管理釣魚互動
        self.fishing_system = FishingSystem()
        
        # 建立魚餌店管理器 - 管理湖邊魚餌店
        self.bait_shop_manager = BaitShopManager(self.terrain_system)
        
        # 建立便利商店血量藥水系統
        self.convenience_health_system = ConvenienceStoreHealthSystem()
        
        # 建立防重疊傳送系統
        self.anti_overlap_system = AntiOverlapTeleportSystem(self.terrain_system)
        
        print("核心系統初始化完成")

    def _initialize_managers(self):
        """
        初始化專門的管理器\n
        """
        # 計算地圖尺寸
        map_width = self.terrain_system.map_width * self.terrain_system.tile_size
        map_height = self.terrain_system.map_height * self.terrain_system.tile_size

        # 攝影機控制器
        self.camera_controller = TownCameraController(map_width, map_height)
        self.camera_controller.center_on_player(self.player)

        # UI 子系統
        self.minimap_ui = MinimapUI()
        self.npc_info_ui = NPCInfoUI()
        self.npc_status_ui = NPCStatusDisplayUI()  # 新增NPC狀態顯示UI
        self.time_ui = TimeDisplayUI(position="top_center", style="compact")
        self.equipment_wheel_ui = EquipmentWheelUI()
        self.house_interior_ui = HouseInteriorUI()  # 住宅內部檢視 UI
        self.fishing_ui = FishingUI()  # 釣魚 UI
        self.fishing_choice_ui = FishingChoiceUI()  # 釣魚選擇 UI

        # UI 管理器
        self.ui_manager = TownUIManager(
            self.player, 
            self.minimap_ui, 
            self.npc_info_ui,
            self.terrain_system
        )

        # 互動處理器
        self.interaction_handler = TownInteractionHandler(
            self.player, 
            self.ui_manager
        )

    def _setup_system_dependencies(self):
        """
        設定系統間的依賴關係\n
        """
        # 為 NPC 設定各種參考
        self.npc_manager.set_buildings_reference(self.terrain_system.buildings)
        self.npc_manager.set_terrain_system_reference(self.terrain_system)
        self.npc_manager.set_road_system_reference(self.road_manager)
        self.npc_manager.set_tile_map_reference(self.tile_map)

        # 註冊電力工人到電力系統
        if self.power_manager:
            self._register_power_workers()

    def _initialize_scene_content(self):
        """
        初始化場景內容\n
        """
        # 定義邊界
        map_width = self.terrain_system.map_width * self.terrain_system.tile_size
        map_height = self.terrain_system.map_height * self.terrain_system.tile_size
        town_bounds = (0, 0, map_width, map_height)
        forest_bounds = (0, 0, SCREEN_WIDTH * 8, SCREEN_HEIGHT * 8)

        # 初始化系統內容
        self.tile_map.create_town_layout(town_bounds)
        self.road_manager.create_road_network_for_town(town_bounds)
        self.vehicle_manager.spawn_initial_vehicles()

        if self.power_manager:
            self.power_manager.initialize_power_grid(town_bounds)

        # 初始化 NPC
        self.npc_manager.initialize_npcs(town_bounds, forest_bounds)

        # 設定玩家初始位置為玩家之家
        self._setup_player_home()

        # 初始化野生動物 - 設定在地形代碼1的區域
        self.wildlife_manager.initialize_animals(scene_type="forest")

    def _setup_player_home(self):
        """
        設定玩家初始位置為玩家之家\n
        """
        # 找到玩家之家
        player_home = None
        for building in self.terrain_system.buildings:
            if hasattr(building, 'is_player_home') and building.is_player_home:
                player_home = building
                break
        
        if player_home:
            # 將玩家生成在玩家之家（傳遞建築物件）
            self.player.spawn_at_player_home(player_home)
            
            # 將攝影機移到玩家位置
            self.camera_controller.center_on_player(self.player)
            
            print(f"玩家已設定在玩家之家: {player_home.name}")
        else:
            # 如果找不到玩家之家，使用預設位置
            default_x = TOWN_TOTAL_WIDTH // 2
            default_y = TOWN_TOTAL_HEIGHT // 2
            self.player.set_position(default_x, default_y)
            self.camera_controller.center_on_player(self.player)
            print(f"警告：找不到玩家之家，使用預設位置: ({default_x}, {default_y})")

    def _handle_house_click(self, mouse_pos):
        """
        處理住宅點擊事件\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠點擊位置 (x, y)\n
        """
        # 轉換滑鼠座標為世界座標
        camera_x, camera_y = self.camera_controller.camera_x, self.camera_controller.camera_y
        world_x = mouse_pos[0] + camera_x
        world_y = mouse_pos[1] + camera_y
        
        # 檢查是否點擊了住宅
        for building in self.terrain_system.buildings:
            if hasattr(building, 'building_type') and building.building_type == "house":
                if building.rect.collidepoint(world_x, world_y):
                    # 檢查是否是玩家的住宅
                    if hasattr(building, 'is_player_home') and building.is_player_home:
                        # 進入室內場景
                        print(f"進入玩家住宅")
                        self.state_manager.change_state(GameState.HOME)
                        return True
                    else:
                        # 顯示其他住宅的內部檢視
                        self.house_interior_ui.show(building)
                        print(f"點擊了住宅: {building.name if hasattr(building, 'name') else '住宅'}")
                        return True
        return False

    def _handle_fishing_click(self, mouse_pos):
        """
        處理釣魚點擊事件\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠點擊位置 (x, y)\n
        \n
        回傳:\n
        bool: 是否處理了釣魚點擊\n
        """
        # 轉換滑鼠座標為世界座標
        camera_x, camera_y = self.camera_controller.camera_x, self.camera_controller.camera_y
        world_x = mouse_pos[0] + camera_x
        world_y = mouse_pos[1] + camera_y
        
        # 嘗試開始釣魚
        result = self.fishing_system.start_fishing(self.player, world_x, world_y, self.terrain_system)
        if result["success"]:
            # 釣魚開始成功，不顯示 console 訊息，UI 會處理
            return True
        else:
            # 只在特定情況下顯示錯誤訊息
            if "釣竿" in result["message"]:
                self.fishing_ui.show_message("需要裝備釣竿才能釣魚！", (255, 100, 100))
            elif "水邊" in result["message"] or "距離" in result["message"]:
                self.fishing_ui.show_message(result["message"], (255, 200, 100))
            return False

    def _setup_wildlife_bounds(self):
        """
        設定野生動物邊界 - 基於地形代碼1的森林區域\n
        """
        # 計算地圖尺寸
        map_width = self.terrain_system.map_width * self.terrain_system.tile_size
        map_height = self.terrain_system.map_height * self.terrain_system.tile_size
        
        # 野生動物可以在整個地圖範圍內活動，但主要在地形代碼1的區域生成
        forest_bounds = (0, 0, map_width, map_height)
        lake_bounds = (0, 0, map_width, map_height)  # 地形代碼2的水域
        
        self.wildlife_manager.set_habitat_bounds(forest_bounds, lake_bounds)

    def _setup_fallback_systems(self):
        """
        設定後備系統（當地形載入失敗時）\n
        """
        print("設定後備系統...")
        # 這裡可以設定基本的系統配置

    def _register_power_workers(self):
        """
        註冊電力工人到電力系統\n
        """
        power_workers = self.npc_manager.get_power_workers()
        for worker in power_workers:
            district_id = worker.assigned_area
            if district_id is not None:
                self.power_manager.register_worker(district_id, worker)

    def update(self, dt):
        """
        更新場景\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        # 更新玩家輸入和移動
        self.input_controller.update(dt)
        
        # 更新玩家狀態（處理移動、動畫等）
        self.player.update(dt)

        # 更新攝影機跟隨玩家
        self.camera_controller.update(self.player)

        # 檢查地形生態區域
        self._check_terrain_ecology_zones()

        # 更新核心系統
        player_pos = (self.player.x, self.player.y)
        self.npc_manager.update(dt, player_pos)
        self.vehicle_manager.update(dt, self.road_manager, self.npc_manager.all_npcs)
        
        # 更新野生動物系統 - 在小鎮場景中的森林區域
        self.wildlife_manager.update(dt, player_pos, "town")

        # 更新釣魚系統
        fishing_update = self.fishing_system.update(dt)
        if fishing_update:
            self.fishing_ui.handle_fishing_event(fishing_update)
            
            # 如果釣到魚，顯示選擇介面
            if fishing_update.get("event") == "catch_success":
                self.fishing_choice_ui.show_choice(fishing_update["fish"], fishing_update.get("choice_time_left", 3.0))
        
        # 更新釣魚選擇UI
        choice_update = self.fishing_choice_ui.update(dt)
        if choice_update == "time_up":
            # 時間到，自動放生
            result = self.fishing_system.release_fish_auto()
            self.fishing_choice_ui.hide()
            if result["success"]:
                print(f"⏰ {result['message']}")
        
        # 更新魚餌店管理器
        self.bait_shop_manager.update(dt, player_pos)
        
        # 更新防重疊傳送系統
        self.anti_overlap_system.update(dt, self.player, self.npc_manager)
        
        # 更新釣魚 UI 狀態
        self.fishing_ui.update_fishing_status(self.fishing_system)
        self.fishing_ui.update(dt)
        
        # 更新NPC狀態UI
        self.npc_status_ui.update(dt)

        # 更新管理器
        self.ui_manager.update(dt)
        self.interaction_handler.update(dt)

        # 檢查自動拾取
        self.interaction_handler.check_automatic_pickups(self.terrain_system)

    def _check_terrain_ecology_zones(self):
        """
        檢查玩家是否進入特殊生態區域\n
        """
        player_pos = self.player.get_center_position()
        terrain_type = self.terrain_system.get_terrain_at_position(player_pos[0], player_pos[1])

        # 避免重複訊息
        if not hasattr(self, 'last_terrain_type'):
            self.last_terrain_type = None

        if terrain_type != self.last_terrain_type:
            if terrain_type == 1:  # 森林區域
                print("🌲 進入森林生態區域 - Stevens Creek County Park 森林區")
            elif terrain_type == 2:  # 水體區域
                print("🏞️ 進入湖泊生態區域 - Stevens Creek 溪流")
            elif terrain_type == 0:  # 草地區域
                if self.last_terrain_type in [1, 2]:
                    print("🌱 回到普通草地區域")

            self.last_terrain_type = terrain_type

    def draw(self, screen):
        """
        繪製場景\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        """
        # 計算可見區域
        visible_rect = self.camera_controller.get_visible_rect()

        # 繪製地形和環境
        self._draw_terrain(screen, visible_rect)

        # 繪製遊戲實體
        self._draw_entities(screen, visible_rect)

        # 繪製 UI
        self.ui_manager.draw(screen, self.camera_controller, self.npc_manager, self.time_manager)
        
        # 繪製魚餌店
        camera_x = self.camera_controller.camera_x
        camera_y = self.camera_controller.camera_y
        self.bait_shop_manager.draw(screen, camera_x, camera_y)
        
        # 繪製裝備圓盤（在最上層）
        self.equipment_wheel_ui.draw(screen, self.player)
        
        # 繪製住宅內部檢視 UI（在最上層）
        self.house_interior_ui.draw(screen)
        
        # 繪製釣魚 UI（在最上層）
        self.fishing_ui.draw(screen)
        
        # 繪製釣魚選擇UI（在最上層）
        self.fishing_choice_ui.draw(screen)
        
        # 繪製NPC狀態顯示UI（在最上層）
        self.npc_status_ui.draw(screen, self.npc_manager)

    def _draw_terrain(self, screen, visible_rect):
        """
        繪製地形和環境\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        visible_rect (Rect): 可見區域\n
        """
        camera_x = self.camera_controller.camera_x
        camera_y = self.camera_controller.camera_y

        # 調試信息：每10幀打印一次
        if not hasattr(self, '_debug_frame_count'):
            self._debug_frame_count = 0
        self._debug_frame_count += 1
        
        if self._debug_frame_count % 10 == 0:
            print(f"繪製調試 - 攝影機位置: ({camera_x:.1f}, {camera_y:.1f})")
            print(f"地圖尺寸: {self.terrain_system.map_width}x{self.terrain_system.map_height}")
            print(f"建築物數量: {len(self.terrain_system.buildings)}")

        # 繪製地形基礎
        self.terrain_system.draw_terrain_layer(screen, camera_x, camera_y)

        # 繪製森林元素
        self.terrain_system.draw_forest_elements(screen, camera_x, camera_y)

        # 繪製水體元素
        self.terrain_system.draw_water_elements(screen, camera_x, camera_y)

        # 繪製建築物
        self.terrain_system.draw_buildings(screen, camera_x, camera_y)

        # 繪製停車場車輛
        self.terrain_system.draw_vehicles(screen, camera_x, camera_y)

    def _draw_entities(self, screen, visible_rect):
        """
        繪製遊戲實體\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        visible_rect (Rect): 可見區域\n
        """
        camera_x = self.camera_controller.camera_x
        camera_y = self.camera_controller.camera_y

        # 調試信息：每10幀打印一次
        if not hasattr(self, '_debug_entity_frame_count'):
            self._debug_entity_frame_count = 0
        self._debug_entity_frame_count += 1
        
        if self._debug_entity_frame_count % 10 == 0:
            print(f"實體調試 - 玩家位置: ({self.player.x:.1f}, {self.player.y:.1f})")
            print(f"NPC 數量: {len(self.npc_manager.all_npcs)}")
            print(f"載具數量: {len(self.vehicle_manager.vehicles)}")

        # 繪製 NPC
        self.npc_manager.draw(screen, (camera_x, camera_y))

        # 繪製野生動物
        self.wildlife_manager.draw_all_animals(screen, "town", (camera_x, camera_y))

        # 繪製載具
        self.vehicle_manager.draw_all_vehicles(screen)

        # 繪製玩家
        self.player.draw(screen, camera_x, camera_y)

    def handle_event(self, event):
        """
        處理輸入事件\n
        \n
        參數:\n
        event (pygame.Event): 輸入事件\n
        \n
        回傳:\n
        bool: 是否處理了事件\n
        """
        # 首先讓輸入控制器處理事件（這對移動很重要）
        action = self.input_controller.handle_event(event)
        
        # 處理滑鼠事件（小地圖互動、住宅點擊和釣魚）
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵點擊
                if self.house_interior_ui.is_visible():
                    # 如果住宅內部檢視已顯示，處理點擊事件
                    self.house_interior_ui.handle_click(event.pos)
                else:
                    # 嘗試處理住宅點擊
                    if not self._handle_house_click(event.pos):
                        # 如果不是住宅點擊，嘗試釣魚
                        self._handle_fishing_click(event.pos)
                return True
            elif event.button == 2:  # 中鍵點擊 - 切換小地圖顯示
                self.minimap_ui.toggle_visibility()
                return True
            elif event.button == 3:  # 右鍵點擊 - 嘗試釣魚
                if self.fishing_system.is_fishing_active():
                    result = self.fishing_system.try_catch_fish(self.player)
                    # UI 會自動處理釣魚結果顯示，不需要在 console 打印
                    return True
            elif self.ui_manager.handle_mouse_input(event):
                return True

        elif event.type == pygame.MOUSEWHEEL:
            # 中鍵滾輪 - 小地圖縮放
            if self.minimap_ui.is_visible:
                self.minimap_ui.handle_scroll(event.y)
                return True
            elif self.ui_manager.handle_mouse_input(event):
                return True

        # 處理鍵盤事件
        if event.type == pygame.KEYDOWN:
            # E鍵 - 裝備圓盤
            if event.key == pygame.K_e:
                self.player.toggle_equipment_wheel()
                return True
            
            # Q鍵 - 砍伐樹木
            elif event.key == pygame.K_q:
                self._handle_tree_chopping()
                return True
            
            # C鍵 - 對話（暫時用互動代替）
            elif event.key == pygame.K_c:
                self.interaction_handler.handle_interaction(
                    self.terrain_system, 
                    self.npc_manager, 
                    self.vehicle_manager
                )
                return True
            
            # 空白鍵 - 互動
            elif event.key == pygame.K_SPACE:
                self.interaction_handler.handle_interaction(
                    self.terrain_system, 
                    self.npc_manager, 
                    self.vehicle_manager
                )
                return True

            elif event.key == pygame.K_TAB:
                # 顯示所有NPC狀態資訊（按住TAB顯示，放開隱藏）
                self.npc_status_ui.show()
                return True

            elif event.key == pygame.K_i:
                # 打開物品欄
                self.state_manager.change_state(GameState.INVENTORY)
                return True

            # 裝備選擇快捷鍵 (1-5)
            elif pygame.K_1 <= event.key <= pygame.K_5:
                if self.player.equipment_wheel_visible:
                    # 如果裝備圓盤顯示，選擇裝備
                    slot_number = event.key - pygame.K_0
                    self.equipment_wheel_ui.handle_slot_selection(slot_number, self.player)
                else:
                    # 如果圓盤未顯示，選擇物品欄槽位
                    slot_index = (event.key - pygame.K_1) % 10
                    self.player.select_slot(slot_index)
                return True
            
            # 物品欄選擇快捷鍵 (6-0)
            elif pygame.K_6 <= event.key <= pygame.K_0:
                slot_index = (event.key - pygame.K_1) % 10
                self.player.select_slot(slot_index)
                return True
        
        elif event.type == pygame.KEYUP:
            # TAB鍵釋放 - 隱藏NPC狀態顯示
            if event.key == pygame.K_TAB:
                self.npc_status_ui.hide()
                return True
        
        # 處理釣魚選擇UI事件
        if self.fishing_choice_ui.is_visible:
            choice = self.fishing_choice_ui.handle_event(event)
            if choice == "release":
                result = self.fishing_system.release_fish(self.player)
                self.fishing_choice_ui.hide()
                if result["success"]:
                    print(f"🐟 {result['message']}")
                return True
            elif choice == "sell":
                result = self.fishing_system.sell_fish(self.player)
                self.fishing_choice_ui.hide()
                if result["success"]:
                    print(f"💰 {result['message']}")
                return True
        
        # 處理NPC狀態UI事件
        self.npc_status_ui.handle_event(event)

        return False

    def _handle_tree_chopping(self):
        """
        處理砍伐樹木\n
        """
        player_pos = (self.player.x, self.player.y)
        tree_info = self.terrain_system.get_nearby_tree(player_pos, max_distance=30)
        
        if tree_info:
            result = self.terrain_system.chop_tree(self.player, tree_info)
            if result['success']:
                print(f"💰 {result['message']}")
        else:
            print("附近沒有樹木可以砍伐")

    def enter(self):
        """
        進入場景\n
        """
        super().enter()  # 設定 is_active = True
        print("進入小鎮場景")
        # 確保攝影機跟隨玩家
        self.camera_controller.center_on_player(self.player)

    def exit(self):
        """
        離開場景\n
        """
        print("離開小鎮場景")

    def get_player(self):
        """
        獲取玩家物件\n
        \n
        回傳:\n
        Player: 玩家物件\n
        """
        return self.player

    def request_scene_change(self, target_scene):
        """
        請求場景切換\n
        \n
        參數:\n
        target_scene (str): 目標場景名稱\n
        """
        print(f"請求切換到場景: {target_scene}")
        # 這裡可以添加場景切換的邏輯

    def get_debug_info(self):
        """
        獲取場景除錯資訊\n
        \n
        回傳:\n
        dict: 除錯資訊\n
        """
        return {
            "scene_name": self.name,
            "player_position": (round(self.player.x, 2), round(self.player.y, 2)),
            "camera_info": self.camera_controller.get_debug_info(),
            "ui_info": self.ui_manager.get_debug_info(),
            "npc_count": len(self.npc_manager.all_npcs),
            "vehicle_count": len(self.vehicle_manager.vehicles)
        }