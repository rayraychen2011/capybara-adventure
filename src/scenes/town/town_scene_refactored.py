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
from src.utils.farmer_status_ui import FarmerStatusUI  # 新增農夫狀態顯示
from src.utils.time_ui import TimeDisplayUI
from src.utils.weapon_wheel_ui import WeaponWheelUI
from src.systems.npc.npc_manager import NPCManager
from src.systems.road_system import RoadManager
from src.systems.tile_system import TileMapManager
from src.systems.terrain_based_system import TerrainBasedSystem
from src.systems.wildlife.wildlife_manager import WildlifeManager  # 新增野生動物管理器
from src.systems.convenience_store_health_system import ConvenienceStoreHealthSystem  # 新增便利商店血量藥水
from src.systems.anti_overlap_system import AntiOverlapTeleportSystem  # 新增防重疊系統
from src.systems.street_light_system import StreetLightSystem  # 新增路燈系統
from src.systems.vegetable_garden_system import VegetableGardenSystem  # 新增蔬果園系統
from src.systems.shooting_system import ShootingSystem, CrosshairSystem, ShootingSoundManager  # 修改射擊系統導入
from src.systems.shop_system import ShopManager  # 新增商店系統
# from src.systems.shop_types import ShopManager, ConvenienceStore, StreetVendor, GunShop, ClothingStore  # 舊的商店類型，已停用
from src.systems.church_system import Church, BlessingSystem, ChurchScene  # 新增教堂系統
from src.systems.axe_system import TreeManager, Axe  # 新增斧頭系統
from src.systems.building_label_system import BuildingLabelSystem, BuildingTypeDetector  # 新增建築標示系統
from src.systems.weather_system import WeatherEffectSystem  # 新增天氣特效系統
from src.scenes.town.town_camera_controller import TownCameraController
from src.scenes.town.town_ui_manager import TownUIManager
from src.scenes.town.town_interaction_handler import TownInteractionHandler
from src.utils.house_interior_ui import HouseInteriorUI
from src.utils.operation_guide_ui import OperationGuideUI  # 新增操作指南UI
from src.utils.phone_ui import PhoneUI  # 新增手機UI
from src.utils.npc_dialogue_ui import NPCDialogueUI  # 新增NPC對話UI
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

    def __init__(self, state_manager, time_manager=None, music_manager=None):
        """
        初始化小鎮場景\n
        \n
        參數:\n
        state_manager (StateManager): 遊戲狀態管理器\n
        time_manager (TimeManager): 時間管理器\n
        music_manager (MusicManager): 音樂管理器\n
        """
        print("=== TownScene.__init__ 開始 ===")
        super().__init__("小鎮")
        self.state_manager = state_manager
        self.time_manager = time_manager
        self.music_manager = music_manager

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
        
        # 載入地形地圖 - 使用編輯版本
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
        
        # 建立野生動物管理器 - 管理地形代碼1區域的動物
        self.wildlife_manager = WildlifeManager()
        self.wildlife_manager.set_terrain_system(self.terrain_system)  # 連結地形系統
        self.wildlife_manager.set_player_attack_callback(self._handle_player_attacked_by_animal)  # 設置攻擊回調
        self._setup_wildlife_bounds()
        
        # 建立便利商店血量藥水系統
        self.convenience_health_system = ConvenienceStoreHealthSystem()
        
        # 建立防重疊傳送系統
        self.anti_overlap_system = AntiOverlapTeleportSystem(self.terrain_system)
        
        # 建立路燈系統
        self.street_light_system = StreetLightSystem(self.time_manager, self.terrain_system)
        
        # 建立蔬果園採集系統
        self.vegetable_garden_system = VegetableGardenSystem(self.terrain_system, self.time_manager)
        
        # 建立天氣特效系統
        self.weather_system = WeatherEffectSystem()
        
        # 建立新的遊戲系統
        self.shooting_system = ShootingSystem()  # 新的射擊系統
        self.crosshair_system = CrosshairSystem()  # 準心系統
        self.shooting_sound_manager = ShootingSoundManager()  # 射擊音效
        # 建立新的商店系統
        self.shop_manager = ShopManager()  # 新的商店管理器
        
        # 手動添加一些商店建築物用於測試
        self._add_test_shop_buildings()
        self.blessing_system = BlessingSystem()  # 祝福系統
        self.tree_manager = TreeManager(self.terrain_system)  # 樹木管理器
        self.building_label_system = BuildingLabelSystem()  # 建築標示系統
        self.building_type_detector = BuildingTypeDetector()  # 建築類型檢測器
        
        # 移除舊的BB槍系統（已被新射擊系統取代）
        # self.player_bb_gun = BBGun()  # 已刪除
        # self.player.equipped_weapon = None  # 已刪除
        
        # 移除舊的裝備系統（已被武器圓盤取代）
        # self.player.equipment_slots[1] = {...}  # 已刪除
        # self.player.current_equipment = 0  # 已刪除
        
        # 教堂場景（稍後初始化）
        self.church_scene = None
        self.in_church = False
        
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
        self.npc_info_ui = NPCInfoUI()
        self.npc_status_ui = NPCStatusDisplayUI()  # 新增NPC狀態顯示UI
        self.farmer_status_ui = FarmerStatusUI()  # 新增農夫狀態顯示UI
        self.npc_dialogue_ui = NPCDialogueUI()  # 新增NPC對話UI
        self.time_ui = TimeDisplayUI(position="top_center", style="compact")
        self.weapon_wheel_ui = WeaponWheelUI()
        self.house_interior_ui = HouseInteriorUI()  # 住宅內部檢視 UI
        self.operation_guide_ui = OperationGuideUI()  # 操作指南 UI
        self.phone_ui = PhoneUI()  # 手機 UI

        # UI 管理器
        self.ui_manager = TownUIManager(
            self.player, 
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
        
        # 連接天氣系統與手機UI
        self.weather_system.phone_ui = self.phone_ui
        # 設定初始天氣（與手機UI同步）
        self.weather_system.set_weather(self.phone_ui.current_weather)
        
        # 連接時間系統與天氣系統
        if self.time_manager:
            self.time_manager.set_weather_system(self.weather_system)

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

        # 初始化 NPC
        self.npc_manager.initialize_npcs(town_bounds, forest_bounds)

        # 設定玩家初始位置為玩家之家
        self._setup_player_home()

        # 初始化野生動物 - 設定在地形代碼1的區域
        self.wildlife_manager.initialize_animals(scene_type="all")  # 初始化所有類型動物（森林、湖泊、草原）
        
        # 初始化路燈系統
        self.street_light_system.initialize_street_lights()
        
        # 初始化蔬果園系統
        self.vegetable_garden_system.initialize_gardens()
        
        # 初始化樹木系統
        self.tree_manager.generate_trees_on_terrain()
        
        # 初始化商店系統
        self._initialize_shops()
        
        # 初始化教堂系統
        self._initialize_churches()
        
        # 自動檢測建築類型
        self.building_type_detector.auto_assign_building_types(self.terrain_system.buildings)
        
        # 設置戰鬥系統
        self._setup_combat_system()

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
        
        # 更新音樂和音效系統
        self._update_music_and_sfx()
        
        # 檢查玩家是否在火車站附近（自動顯示傳送選項）
        player_center = self.player.get_center_position()
        self.terrain_system.check_player_near_railway_station(player_center)

        # 更新核心系統
        player_pos = (self.player.x, self.player.y)
        self.npc_manager.update(dt, player_pos)
        
        # 更新野生動物系統 - 在小鎮場景中的森林區域
        self.wildlife_manager.update(dt, player_pos, "town")
        
        # 更新玩家商品效果
        self.shop_manager.update_player_effects(self.player)
        
        # 更新祝福系統
        self.blessing_system.update(dt)
        
        # 更新樹木系統
        self.tree_manager.update(dt)
        
        # 檢查教堂互動
        if hasattr(self, 'church'):
            self.church.is_near_player(player_pos)
        
        # 更新射擊系統
        self.shooting_system.update(dt)
        
        # 減少調試輸出頻率：每300幀（約5秒）輸出一次子彈狀態
        if not hasattr(self, '_bullet_debug_counter'):
            self._bullet_debug_counter = 0
        self._bullet_debug_counter += 1
        if self._bullet_debug_counter % 300 == 0 and len(self.shooting_system.bullets) > 0:
            print(f"🔸 當前場景中有 {len(self.shooting_system.bullets)} 發子彈")
        
        # 檢查子彈與野生動物碰撞
        if hasattr(self, 'wildlife_manager') and self.wildlife_manager:
            # 獲取所有活著的動物用於碰撞檢測
            active_animals = [animal for animal in self.wildlife_manager.all_animals if animal.is_alive]
            
            # 減少調試輸出：每300幀輸出一次動物狀態
            if self._bullet_debug_counter % 300 == 0:
                print(f"🦎 野生動物狀態: 總計 {len(self.wildlife_manager.all_animals)} 隻，活著 {len(active_animals)} 隻")
            
            # 子彈與動物共存檢測（減少輸出頻率）
            bullet_count = len(self.shooting_system.bullets)
            animal_count = len(active_animals)
            
            # 只在有子彈且每120幀時輸出調試信息
            if bullet_count > 0 and self._bullet_debug_counter % 120 == 0:
                print(f"⚡ 當前有 {bullet_count} 發子彈，{animal_count} 隻動物")
            
            # 只在實際進行碰撞檢測且每120幀時輸出
            if bullet_count > 0 and animal_count > 0 and self._bullet_debug_counter % 120 == 0:
                print(f"🔍 碰撞檢測: {bullet_count} 發子彈 vs {animal_count} 隻動物")
            
            # 檢查子彈碰撞
            bullet_hits = self.shooting_system.check_bullet_collisions(active_animals)
            
            # 處理命中結果
            for hit_info in bullet_hits:
                animal = hit_info['target']
                damage = hit_info['damage']
                hit_pos = hit_info['position']
                
                # 減少擊中調試輸出：只輸出死亡事件，傷害事件不輸出
                # print(f"💥 子彈擊中 {animal.animal_type.value}，造成 {damage} 點傷害！")
                
                # 檢查動物是否死亡
                if not animal.is_alive:
                    # 給玩家金錢獎勵
                    if hasattr(animal, 'animal_type'):
                        from src.systems.wildlife.animal_data import AnimalData
                        rarity = AnimalData.get_animal_property(animal.animal_type, "rarity")
                        reward_money = AnimalData.get_animal_rarity_value(rarity)
                        
                        if hasattr(self.player, 'money'):
                            self.player.money += reward_money
                            print(f"🏆 擊殺 {animal.animal_type.value}！獲得 {reward_money} 元")
        
        # 檢查持續按住滑鼠左鍵的全自動射擊（BB槍特性）
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and self.player.is_fire_enabled():  # 左鍵按住且開火功能啟用
            mouse_pos = pygame.mouse.get_pos()
            camera_offset = (self.camera_controller.camera_x, self.camera_controller.camera_y)
            self.shooting_system.handle_mouse_shoot(self.player, mouse_pos, camera_offset)
        
        # 更新準心位置
        mouse_pos = pygame.mouse.get_pos()
        self.crosshair_system.update(mouse_pos)
        
        # 檢查武器裝備狀態來顯示/隱藏準心
        # 只有當玩家裝備了槍時才顯示準心（空手時不顯示）
        if (hasattr(self.player, 'weapon_manager') and 
            self.player.weapon_manager and 
            self.player.weapon_manager.current_weapon and
            self.player.weapon_manager.current_weapon.weapon_type != "unarmed"):
            self.crosshair_system.show()
        else:
            self.crosshair_system.hide()

        # 更新地形系統（包含鐵路系統）
        self.terrain_system.update(dt)
        
        # 更新街燈系統
        self.street_light_system.update(dt)
        
        # 更新蔬菜花園系統
        self.vegetable_garden_system.update(dt)
        
        # 更新天氣特效系統
        self.weather_system.update(dt)
        
        # 檢查玩家是否進入蔬果園自動採收
        player_pos = (self.player.x, self.player.y)
        auto_harvest_result = self.vegetable_garden_system.check_auto_harvest(player_pos, self.player)
        if auto_harvest_result:
            print(f"🌱 自動採收: {auto_harvest_result['message']}")
            self.ui_manager.show_message(f"自動採收 {auto_harvest_result['vegetable']} (+{auto_harvest_result['money_earned']}元)")

        # 更新防重疊傳送系統
        self.anti_overlap_system.update(dt, self.player, self.npc_manager)
        
        # 更新操作指南UI
        self.operation_guide_ui.update(dt)
        
        # 更新手機UI
        self.phone_ui.update(dt)
        
        # 移除釣魚 UI 更新（已刪除釣魚系統）
        
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

    def _update_music_and_sfx(self):
        """
        根據玩家位置和狀態更新背景音樂和音效\n
        """
        if not self.music_manager:
            return
            
        player_pos = self.player.get_center_position()
        terrain_type = self.terrain_system.get_terrain_at_position(player_pos[0], player_pos[1])
        
        # 檢查是否在傳奇動物領地
        in_legendary_territory = False
        if hasattr(self, 'wildlife_manager'):
            in_legendary_territory = self.wildlife_manager.is_player_in_legendary_territory(player_pos)
        
        # 更新背景音樂
        self.music_manager.update_music_for_location(terrain_type, in_legendary_territory)
        
        # 更新環境音效（草原風聲）
        self.music_manager.play_grassland_ambient(terrain_type)

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
        
        # 繪製武器圓盤（在最上層）
        self.weapon_wheel_ui.draw(screen)
        
        # 繪製射擊系統UI（準星、子彈、武器資訊）
        self.shooting_system.draw_bullets(screen, (self.camera_controller.camera_x, self.camera_controller.camera_y))
        self.shooting_system.draw_shooting_ui(screen, self.player)
        
        # 繪製住宅內部檢視 UI（在最上層）
        self.house_interior_ui.draw(screen)
        
        # 繪製操作指南UI（在最上層）
        self.operation_guide_ui.draw(screen)
        
        # 繪製手機UI（在最上層）
        self.phone_ui.draw(screen, self.time_manager)
        
        # 繪製NPC對話UI（在最上層）
        self.npc_dialogue_ui.draw(screen)
        
        # 繪製火車站目的地選擇畫面（在最上層）
        self.terrain_system.railway_system.draw_destination_menu(screen, get_font_manager())
        
        # 繪製NPC狀態顯示UI（在最上層）
        self.npc_status_ui.draw(screen, self.npc_manager)
        
        # 繪製農夫狀態UI（在最上層）
        if hasattr(self.npc_manager, 'farmer_scheduler'):
            self.farmer_status_ui.draw(screen, self.npc_manager.farmer_scheduler, self.time_manager)
            # 在地圖上顯示農夫狀態標記
            camera_x = self.camera_controller.camera_x
            camera_y = self.camera_controller.camera_y
            self.farmer_status_ui.draw_farmer_info_on_map(screen, camera_x, camera_y, self.npc_manager.farmer_scheduler)

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

        # 繪製蔬果園（新增）
        self.terrain_system.draw_vegetable_gardens(screen, camera_x, camera_y)
        
        # 繪製街燈系統
        self.street_light_system.draw(screen, (camera_x, camera_y))
        
        # 繪製蔬菜花園系統
        self.vegetable_garden_system.draw(screen, (camera_x, camera_y))

        # 繪製鐵路系統（鐵軌、火車站、火車）
        self.terrain_system.draw_railway_elements(screen, camera_x, camera_y, get_font_manager())

        # 繪製建築物
        self.terrain_system.draw_buildings(screen, camera_x, camera_y, get_font_manager())
        
        # 繪製天氣特效（在建築物之後，實體之前）
        self.weather_system.draw(screen, camera_x, camera_y)

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

        # 繪製 NPC
        self.npc_manager.draw(screen, (camera_x, camera_y))

        # 繪製野生動物
        self.wildlife_manager.draw_all_animals(screen, "town", (camera_x, camera_y))

        # 繪製樹木
        self.tree_manager.draw(screen, camera_x, camera_y)

        # 繪製商店建築標籤
        if hasattr(self.terrain_system, 'commercial_buildings'):
            self.building_label_system.draw_all_building_labels(
                screen, self.terrain_system.commercial_buildings, camera_x, camera_y
            )

        # 繪製教堂
        if hasattr(self, 'church'):
            self.church.draw(screen, camera_x, camera_y)

        # 繪製商店界面
        self.shop_manager.draw(screen, self.player)

        # 繪製玩家
        self.player.draw(screen, camera_x, camera_y)

        # 繪製子彈（在玩家之後，UI之前）
        self.shooting_system.draw_bullets(screen, (camera_x, camera_y))

        # 繪製十字準星（如果有配備槍）
        if (hasattr(self.player, 'current_equipment') and 
            self.player.current_equipment == 1):  # 1號槽位是槍
            self.crosshair_system.draw(screen)

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
        
        # 處理新的動作
        if action:
            if action == "toggle_fire_mode":
                # L鍵 - 切換開火功能
                self.player.toggle_fire_mode()
                print(f"L鍵切換開火功能: {'開啟' if self.player.is_fire_enabled() else '關閉'}")
                return True
            elif action == "weapon_gun":
                # 切換到槍
                if hasattr(self.player, 'weapon_manager'):
                    self.player.weapon_manager.switch_weapon("pistol")
                print("切換到槍")
                return True
            elif action == "weapon_unarmed":
                # 切換到空手
                if hasattr(self.player, 'weapon_manager'):
                    self.player.weapon_manager.switch_weapon("unarmed")
                print("切換到空手")
                return True
            elif action == "talk_to_npc" or action == "right_click":
                # 右鍵點擊 - 與NPC對話或切換開火功能
                world_x = event.pos[0] + self.camera_controller.camera_x
                world_y = event.pos[1] + self.camera_controller.camera_y
                
                # 檢查是否點擊了玩家角色
                player_rect = pygame.Rect(
                    self.player.x - self.player.width//2,
                    self.player.y - self.player.height//2,
                    self.player.width,
                    self.player.height
                )
                if player_rect.collidepoint(world_x, world_y):
                    # 點擊玩家角色，切換開火功能
                    self.player.toggle_fire_mode()
                    return True
                
                # 檢查是否點擊了NPC
                clicked_npc = self._find_npc_at_position(world_x, world_y)
                if clicked_npc:
                    self.npc_dialogue_ui.show_dialogue(clicked_npc)
                    print(f"與NPC {clicked_npc.name} 對話")
                    return True
        
        # 處理滑鼠事件（武器圓盤、射擊、住宅點擊、火車站等）
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 優先處理NPC對話UI點擊
            if self.npc_dialogue_ui.handle_click(event.pos):
                return True
                
            # 優先處理手機UI點擊
            if self.phone_ui.handle_click(event.pos, self.player, self.time_manager):
                return True
                
            if event.button == 1:  # 左鍵點擊 - 射擊或其他互動
                if self.house_interior_ui.is_visible():
                    # 如果住宅內部檢視已顯示，處理點擊事件
                    self.house_interior_ui.handle_click(event.pos)
                elif self.shop_manager.is_shop_open():
                    # 商店已開啟時，左鍵不處理其他點擊（保留商店互動空間）
                    pass
                elif self.terrain_system.railway_system.show_destination_menu:
                    # 如果火車站選擇畫面已顯示，不處理其他點擊
                    pass
                else:
                    # 計算世界座標
                    world_x = event.pos[0] + self.camera_controller.camera_x
                    world_y = event.pos[1] + self.camera_controller.camera_y
                    
                    # 檢查玩家是否裝備槍械進行射擊
                    if self.player.can_shoot():  # 玩家裝備了槍
                        # 使用射擊系統發射可視子彈（新系統）
                        camera_offset = (self.camera_controller.camera_x, self.camera_controller.camera_y)
                        shoot_result = self.shooting_system.handle_mouse_shoot(self.player, event.pos, camera_offset)
                        print(f"🔫 左鍵射擊: can_shoot={self.player.can_shoot()}, shoot_result={shoot_result}")
                        print(f"   當前子彈數: {len(self.shooting_system.bullets)}")
                    else:
                        print(f"❌ 無法射擊: can_shoot={self.player.can_shoot()}")
                        # 嘗試處理火車站點擊
                        if not self.terrain_system.handle_railway_click((world_x, world_y), self.player):
                            # 如果不是火車站點擊，嘗試住宅點擊
                            self._handle_house_click(event.pos)
                return True
            elif event.button == 2:  # 中鍵點擊 - 武器圓盤
                self.player.toggle_weapon_wheel()
                return True
            elif event.button == 3:  # 右鍵點擊 - NPC對話、商店互動、砍樹、採摘蔬果園或關閉火車站選擇畫面
                if self.terrain_system.railway_system.show_destination_menu:
                    self.terrain_system.railway_system.close_destination_menu()
                    return True
                elif self.shop_manager.is_shop_open():
                    # 商店開啟時，右鍵可以購買商品或關閉商店
                    purchased = self.shop_manager.handle_mouse_click(event.pos, self.player)
                    if not purchased:
                        # 如果沒有購買商品，則關閉商店
                        self.shop_manager.close_shop()
                    return True
                else:
                    # 計算世界座標
                    world_x = event.pos[0] + self.camera_controller.camera_x
                    world_y = event.pos[1] + self.camera_controller.camera_y
                    
                    # 優先檢查NPC點擊（右鍵對話）
                    clicked_npc = self._find_npc_at_position(world_x, world_y)
                    if clicked_npc:
                        self.npc_dialogue_ui.show_dialogue(clicked_npc)
                        print(f"右鍵與NPC {clicked_npc.name} 對話")
                        return True
                    
                    # 優先嘗試建築物右鍵互動（商店系統）
                    building = self._find_building_at_position(world_x, world_y)
                    print(f"DEBUG: 建築物檢測結果={building}")
                    if building and hasattr(building, 'building_type'):
                        print(f"DEBUG: 右鍵點擊建築物，類型={building.building_type}, 名稱={getattr(building, 'name', 'N/A')}")
                        if building.building_type in ["gun_shop", "convenience_store", "clothing_store", "hospital"]:
                            print(f"DEBUG: 建築物類型符合商店條件")
                            result = building.interact(self.player)
                            print(f"DEBUG: 建築物互動結果={result}")
                            if result.get("success") and result.get("action") == "open_shop":
                                # 根據建築物類型開啟對應的商店
                                shop_type = self._get_shop_type_from_building(building.building_type)
                                print(f"DEBUG: 映射的商店類型={shop_type}")
                                if shop_type:
                                    print(f"DEBUG: 開啟商店={shop_type}")
                                    self.shop_manager.open_shop(shop_type)
                                    print(f"DEBUG: 商店開啟狀態確認={self.shop_manager.is_shop_open()}")
                                else:
                                    print(f"DEBUG: ❌ 商店類型映射失敗")
                                return True
                            else:
                                print(f"DEBUG: ❌ 建築物互動失敗或未返回open_shop")
                        else:
                            print(f"DEBUG: 建築物類型不符合商店條件，跳過商店處理")
                    
                    # 如果沒有找到新的互動建築物，繼續執行原有的右鍵互動邏輯
                    if not building:
                        print(f"DEBUG: 未找到建築物，繼續執行其他右鍵互動邏輯")
                        # 嘗試商店互動
                        if self._handle_shop_interaction((world_x, world_y)):
                            return True
                        return True
                    # 嘗試教堂互動
                    elif self._handle_church_interaction((world_x, world_y)):
                        return True
                    # 嘗試通用建築物互動
                    elif self._handle_building_interaction((world_x, world_y)):
                        return True
                    # 嘗試砍樹
                    elif self._handle_tree_chopping((world_x, world_y)):
                        return True
                    # 右鍵採摘蔬果園
                    else:
                        self._handle_vegetable_garden_harvest(event.pos)
                        return True
            elif self.ui_manager.handle_mouse_input(event):
                return True

        elif event.type == pygame.MOUSEWHEEL:
            # 操作指南滾動 - 最高優先級
            if self.operation_guide_ui.is_visible:
                self.operation_guide_ui.handle_scroll(event.y)
                return True
            elif self.ui_manager.handle_mouse_input(event):
                return True

        elif event.type == pygame.MOUSEMOTION:
            # 滑鼠移動 - NPC對話UI和商店按鈕高亮
            if self.npc_dialogue_ui.is_visible:
                self.npc_dialogue_ui.handle_mouse_move(event.pos)
                return True
            elif self.shop_manager.is_shop_open():
                # 新商店系統不需要處理滑鼠移動事件
                return True

        # 處理鍵盤事件
        if event.type == pygame.KEYDOWN:
            # 優先讓NPC對話UI處理鍵盤事件
            if self.npc_dialogue_ui.handle_key_input(event):
                return True
                
            # 讓商店管理器處理鍵盤事件
            if self.shop_manager.handle_key_input(event):
                return True
                
            # 先讓操作指南UI處理鍵盤事件（處理反斜線鍵）
            if self.operation_guide_ui.handle_key_press(event.key):
                return True
            
            # 0鍵 - 操作指南
            if event.key == pygame.K_0:
                self.operation_guide_ui.toggle_visibility()
                return True
            
            # ESC鍵 - 關閉UI或暫停
            elif event.key == pygame.K_ESCAPE:
                if self.terrain_system.railway_system.show_destination_menu:
                    self.terrain_system.railway_system.close_destination_menu()
                    return True
                elif self.operation_guide_ui.is_visible:
                    self.operation_guide_ui.hide()
                    return True
                elif self.shop_manager.is_shop_open():
                    self.shop_manager.close_shop()
                    return True
                else:
                    self.state_manager.change_state(GameState.PAUSED)
                    return True
            
            # 數字鍵1-2 - 武器選擇
            elif event.key == pygame.K_1:
                # 切換到手槍
                if hasattr(self.player, 'weapon_manager') and self.player.weapon_manager:
                    self.player.weapon_manager.switch_weapon("pistol")
                    print("切換到手槍")
                return True
            elif event.key == pygame.K_2:
                # 切換到空手
                if hasattr(self.player, 'weapon_manager') and self.player.weapon_manager:
                    self.player.weapon_manager.switch_weapon("unarmed")
                    print("切換到空手")
                return True
            
            # 數字鍵3-6 - 火車站目的地選擇
            elif pygame.K_3 <= event.key <= pygame.K_6:
                if self.terrain_system.railway_system.show_destination_menu:
                    selection_index = event.key - pygame.K_3  # 3鍵對應索引0
                    if self.terrain_system.railway_system.handle_destination_selection(selection_index, self.player):
                        print("🚂 快速旅行成功！")
                    return True
                elif self.player.weapon_wheel_visible:
                    # 如果武器圓盤顯示，處理舊的武器選擇邏輯
                    weapon_key = str(event.key - pygame.K_0)  # 轉換為字符串
                    self.weapon_wheel_ui.select_weapon_by_key(weapon_key)
                    return True
            
            # 數字鍵7-9 - 火車站目的地選擇（擴展）
            elif pygame.K_7 <= event.key <= pygame.K_9:
                if self.terrain_system.railway_system.show_destination_menu:
                    selection_index = event.key - pygame.K_3  # 保持與上面的邏輯一致
                    if self.terrain_system.railway_system.handle_destination_selection(selection_index, self.player):
                        print("🚂 快速旅行成功！")
                    return True
            
            # 0鍵 - 移除槽位選擇功能
            elif event.key == pygame.K_0:
                if not self.terrain_system.railway_system.show_destination_menu:
                    pass  # 不再支援物品欄槽位
                    return True
            
            # E鍵 - 移除舊的裝備圓盤（現在使用中鍵）
            # if event.key == pygame.K_e:
            #     self.player.toggle_equipment_wheel()
            #     return True
            
            # Q鍵 - 砍伐樹木
            elif event.key == pygame.K_q:
                self._handle_tree_chopping()
                return True
            
            # P鍵 - 開啟/關閉手機
            elif event.key == pygame.K_p:
                self.phone_ui.toggle_visibility()
                return True
            
            # G鍵 - 切換武器裝備狀態
            elif event.key == pygame.K_g:
                self._toggle_weapon()
                return True
            
            # C鍵 - 對話（暫時用互動代替）
            elif event.key == pygame.K_c:
                self.interaction_handler.handle_interaction(
                    self.terrain_system, 
                    self.npc_manager, 
                    None  # 移除vehicle_manager參數
                )
                return True
            
            # 空白鍵 - 互動
            elif event.key == pygame.K_SPACE:
                self.interaction_handler.handle_interaction(
                    self.terrain_system, 
                    self.npc_manager, 
                    None  # 移除vehicle_manager參數
                )
                return True

            elif event.key == pygame.K_TAB:
                # 顯示所有NPC狀態資訊（按住TAB顯示，放開隱藏）
                self.npc_status_ui.show()
                return True
        
        elif event.type == pygame.KEYUP:
            # TAB鍵釋放 - 隱藏NPC狀態顯示
            if event.key == pygame.K_TAB:
                self.npc_status_ui.hide()
                return True
        
        # 移除釣魚選擇UI事件處理（已刪除釣魚系統）
        
        # 處理NPC狀態UI事件
        self.npc_status_ui.handle_event(event)
        
        # 處理農夫狀態UI事件
        if hasattr(self.npc_manager, 'farmer_scheduler'):
            self.farmer_status_ui.handle_key_event(event, self.npc_manager.farmer_scheduler)

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

    def _toggle_weapon(self):
        """
        切換武器裝備狀態（G鍵）\n
        玩家可以裝備或卸下武器，只有裝備武器時才顯示準心\n
        """
        if hasattr(self.player, 'equipped_weapon'):
            if self.player.equipped_weapon is None:
                # 裝備武器
                if hasattr(self, 'player_bb_gun'):
                    self.player.equipped_weapon = self.player_bb_gun
                    print("🔫 已裝備 BB槍")
                else:
                    print("❌ 沒有可裝備的武器")
            else:
                # 卸下武器
                self.player.equipped_weapon = None
                print("🎒 已收起武器")
        else:
            print("❌ 武器系統未初始化")

    def _handle_vegetable_garden_harvest(self, mouse_pos):
        """
        處理蔬果園採摘\n
        根據新需求：玩家右鍵採摘蔬果園，獲得 10 元收益\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠點擊位置 (x, y)\n
        """
        # 轉換滑鼠座標為世界座標
        camera_x, camera_y = self.camera_controller.camera_x, self.camera_controller.camera_y
        world_x = mouse_pos[0] + camera_x
        world_y = mouse_pos[1] + camera_y
        
        # 嘗試採摘蔬果園
        result = self.terrain_system.harvest_vegetable_garden((world_x, world_y), self.player)
        
        if result['success']:
            print(f"🌱 {result['message']}")
        else:
            # 如果附近沒有蔬果園，不顯示錯誤消息（避免太多輸出）
            if "附近沒有蔬果園" not in result['message']:
                print(f"❌ {result['message']}")

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
            "railway_stations": len(self.railway_system.train_stations)
        }

    def _handle_player_attacked_by_animal(self, damage, animal):
        """
        處理玩家被動物攻擊\n
        \n
        參數:\n
        damage (int): 傷害值\n
        animal (Animal): 攻擊的動物\n
        """
        # 對玩家造成傷害
        self.player.take_damage(damage, animal)
        
        # 檢查玩家是否死亡
        if not self.player.is_alive:
            self._handle_player_death_by_animal(animal)

    def _handle_player_death_by_animal(self, animal):
        """
        處理玩家被動物擊殺\n
        \n
        參數:\n
        animal (Animal): 擊殺玩家的動物\n
        """
        print(f"💀 玩家被 {animal.animal_type.value} 擊殺了！")
        
        # 扣除財產的5%
        money_loss = round(self.player.money * 0.05)
        self.player.money = max(0, self.player.money - money_loss)
        
        if money_loss > 0:
            print(f"💰 損失了 {money_loss} 元（5%財產損失）")
        
        # 找到最近的醫院並傳送玩家
        hospital_position = self._find_nearest_hospital()
        if hospital_position:
            print(f"🏥 正在將玩家傳送到最近的醫院...")
            self.player.respawn(hospital_position)
            print(f"🏥 玩家已在醫院重生！")
        else:
            # 如果沒有醫院，使用默認重生點
            self.player.respawn()
            print("⚕️ 沒有找到醫院，使用默認重生點")

    def _find_nearest_hospital(self):
        """
        找到最近的醫院\n
        \n
        回傳:\n
        tuple: 最近醫院的位置，如果沒有醫院則返回 None\n
        """
        player_pos = (self.player.x, self.player.y)
        nearest_hospital = None
        nearest_distance = float('inf')
        
        # 搜尋所有建築物中的醫院
        for building in self.terrain_system.buildings:
            if hasattr(building, 'building_type') and building.building_type == "hospital":
                # 計算距離
                building_center = (building.x + building.width // 2, building.y + building.height // 2)
                distance = ((player_pos[0] - building_center[0]) ** 2 + (player_pos[1] - building_center[1]) ** 2) ** 0.5
                
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_hospital = building
        
        if nearest_hospital:
            # 返回醫院門口的位置
            return (
                nearest_hospital.x + nearest_hospital.width // 2,
                nearest_hospital.y + nearest_hospital.height + 10  # 門口位置
            )
        
        return None

    def _initialize_shops(self):
        """
        初始化商店系統 - 為建築物註冊商店\n
        """
        # 新的商店系統不需要註冊建築物，所有商店類型已在 ShopManager 初始化時設定
        print("初始化商店系統完成：使用新的統一商店管理器")

    def _initialize_churches(self):
        """
        初始化教堂系統\n
        """
        # 創建教堂
        map_width = self.terrain_system.map_width * self.terrain_system.tile_size
        map_height = self.terrain_system.map_height * self.terrain_system.tile_size
        
        church_x = int(map_width * 0.5)
        church_y = int(map_height * 0.2)
        
        self.church = Church(church_x, church_y)
        self.church_scene = ChurchScene(self.blessing_system)
        
        print("教堂系統初始化完成")

    def _handle_shooting(self, mouse_pos):
        """
        處理射擊事件\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠點擊位置\n
        """
        if not hasattr(self.player, 'equipped_weapon') or not self.player.equipped_weapon:
            return
        
        # 計算世界座標
        world_x = mouse_pos[0] + self.camera_controller.camera_x
        world_y = mouse_pos[1] + self.camera_controller.camera_y
        target_position = (world_x, world_y)
        
        # 玩家位置
        player_position = (self.player.x + self.player.width//2, 
                          self.player.y + self.player.height//2)
        
        # 射擊
        weapon = self.player.equipped_weapon
        if weapon.can_shoot():
            # 播放射擊音效
            self.shooting_sound_manager.play_shot_sound(weapon.weapon_type)
            
            # 執行射擊
            result = weapon.shoot(target_position, player_position)
            
            if result["success"]:
                print(f"射擊！距離: {result['distance']:.1f}")
                
                # 檢查是否擊中動物
                if result["hit"]:
                    self._check_animal_hit(target_position, result["damage"])
        
    def _check_animal_hit(self, target_position, damage):
        """
        檢查是否擊中動物\n
        \n
        參數:\n
        target_position (tuple): 射擊目標位置\n
        damage (int): 傷害值\n
        """
        # 獲取附近的動物
        nearby_animals = self.wildlife_manager.get_nearby_animals(
            target_position, 30, "town"  # 30像素範圍內
        )
        
        if nearby_animals:
            # 選擇最近的動物
            target_animal = min(
                nearby_animals,
                key=lambda a: ((a.x - target_position[0]) ** 2 + 
                              (a.y - target_position[1]) ** 2)
            )
            
            # 對動物造成傷害
            target_animal.take_damage(damage, self.player)
            
            # 檢查動物是否死亡
            if not target_animal.is_alive:
                # 獲得金錢獎勵
                from src.systems.wildlife.animal_data import AnimalData
                rarity = AnimalData.get_animal_property(target_animal.animal_type, "rarity")
                base_reward = AnimalData.get_animal_rarity_value(rarity)
                
                # 應用祝福效果
                final_reward = self.blessing_system.apply_blessing_effect(self.player, base_reward)
                
                # 給予獎勵
                self.player.money += final_reward
                
                print(f"擊殺 {target_animal.animal_type.value}！獲得 {final_reward} 元")

    def _handle_shop_interaction(self, world_pos):
        """
        處理商店互動\n
        \n
        參數:\n
        world_pos (tuple): 世界座標位置\n
        \n
        回傳:\n
        bool: 是否處理了商店互動\n
        """
        # 舊的商店處理邏輯，已被新商店系統取代
        return False

    def _handle_shop_purchase(self, purchase_result):
        """
        處理商店購買 - 舊方法，已被新商店系統取代
        """
        # 舊的購買處理邏輯，已被新商店系統取代
        pass

    def _handle_church_interaction(self, world_pos):
        """
        處理教堂互動\n
        \n
        參數:\n
        world_pos (tuple): 世界座標位置\n
        \n
        回傳:\n
        bool: 是否處理了教堂互動\n
        """
        if hasattr(self, 'church') and self.church.is_player_nearby:
            # 進入教堂場景
            print("進入教堂")
            self.in_church = True
            return True
        
        return False

    def _handle_building_interaction(self, world_pos):
        """
        處理通用建築物右鍵互動\n
        \n
        參數:\n
        world_pos (tuple): 世界座標位置\n
        \n
        回傳:\n
        bool: 是否處理了建築物互動\n
        """
        # 定義互動範圍
        interaction_range = 80
        
        # 檢查地形系統中的所有建築物
        for building in self.terrain_system.buildings:
            # 計算與建築物的距離
            building_x = getattr(building, 'x', 0)
            building_y = getattr(building, 'y', 0)
            distance = ((world_pos[0] - building_x) ** 2 + (world_pos[1] - building_y) ** 2) ** 0.5
            
            if distance <= interaction_range:
                # 檢查建築物類型並執行對應的互動
                building_type = getattr(building, 'type', 'unknown')
                building_name = getattr(building, 'name', '建築物')
                
                # 特殊商店類型：打開商店界面
                if building_type in ['gun_shop', 'convenience_store', 'street_vendor', 'clothing_store']:
                    return self._open_shop_by_building_type(building_type, (building_x, building_y))
                
                # 教堂：進入教堂
                elif building_type == 'church':
                    return self._enter_church_building()
                
                # 其他建築物：執行通用互動
                else:
                    self._interact_with_generic_building(building, building_type, building_name)
                    return True
        
        return False

    def _interact_with_generic_building(self, building, building_type, building_name):
        """
        與通用建築物互動\n
        \n
        參數:\n
        building: 建築物物件\n
        building_type (str): 建築物類型\n
        building_name (str): 建築物名稱\n
        """
        # 根據建築類型顯示不同的互動訊息
        interaction_messages = {
            "house": f"這是{building_name}的家",
            "residential": f"這是{building_name}的住宅",
            "hospital": f"歡迎來到{building_name}！需要治療嗎？",
            "bank": f"歡迎來到{building_name}！需要金融服務嗎？",
            "school": f"歡迎來到{building_name}！這是知識的殿堂",
            "office": f"這是{building_name}辦公大樓",
            "market": f"歡迎來到{building_name}！新鮮商品等你選購",
            "pharmacy": f"歡迎來到{building_name}！需要藥品嗎？",
            "bookstore": f"歡迎來到{building_name}！書香滿屋",
            "cafe": f"歡迎來到{building_name}！來杯咖啡吧",
            "bakery": f"歡迎來到{building_name}！麵包香氣撲鼻",
            "barber": f"歡迎來到{building_name}！需要理髮服務嗎？",
            "restaurant": f"歡迎來到{building_name}！美食等你品嚐",
            "tavern": f"歡迎來到{building_name}！來喝一杯放鬆一下",
            "unknown": f"與{building_name}互動"
        }
        
        # 顯示互動訊息
        message = interaction_messages.get(building_type, f"與{building_name}互動")
        self.ui_manager.show_message(message, 2.5)
        
        # 特殊建築物的額外功能
        if building_type == "hospital" and self.player.health < PLAYER_MAX_HEALTH:
            # 醫院可以治療
            self.player.health = PLAYER_MAX_HEALTH
            self.ui_manager.show_message("健康已完全恢復！", 2.0)
        
        elif building_type == "bank":
            # 銀行顯示餘額
            balance = self.player.get_money()
            self.ui_manager.show_message(f"您的帳戶餘額：${balance}", 2.0)
        
        elif building_type in ["house", "residential"]:
            # 住宅建築 - 顯示內部檢視（如果已實現）
            if hasattr(self, 'house_interior_ui'):
                self.house_interior_ui.show_for_building(building)

    def _open_shop_by_building_type(self, building_type, position):
        """
        根據建築物類型打開對應的商店界面
        
        參數:
        building_type (str): 建築物類型
        position (tuple): 建築物位置
        
        回傳:
        bool: 是否成功打開商店
        """
        # 使用新的商店系統
        shop_type = self._get_shop_type_from_building(building_type)
        if shop_type:
            self.shop_manager.open_shop(shop_type)
            return True
        
        return False

    def _enter_church_building(self):
        """
        進入教堂建築\n
        \n
        回傳:\n
        bool: 是否成功進入教堂\n
        """
        # 檢查是否有教堂系統
        if hasattr(self, 'church') and self.church:
            # 進入教堂場景
            print("進入教堂")
            self.in_church = True
            self.ui_manager.show_message("歡迎來到教堂！願神保佑你", 2.5)
            return True
        else:
            # 沒有教堂系統，顯示一般訊息
            self.ui_manager.show_message("歡迎來到教堂！願神保佑你", 2.5)
            return True

    def _handle_tree_chopping(self, world_pos):
        """
        處理砍樹互動\n
        \n
        參數:\n
        world_pos (tuple): 世界座標位置\n
        \n
        回傳:\n
        bool: 是否處理了砍樹互動\n
        """
        # 檢查玩家是否裝備斧頭（3號槽位）
        if (hasattr(self.player, 'current_equipment') and 
            self.player.current_equipment == 3):
            
            # 尋找附近的樹木
            tree = self.tree_manager.find_tree_at_position(world_pos[0], world_pos[1])
            
            if tree:
                # 砍樹
                result = self.tree_manager.chop_tree(tree, self.player)
                
                if result['success']:
                    print(result['message'])
                    return True
        
        return False

    def _find_npc_at_position(self, world_x, world_y):
        """
        尋找指定世界座標位置的 NPC\n
        \n
        參數:\n
        world_x (float): 世界座標 X\n
        world_y (float): 世界座標 Y\n
        \n
        回傳:\n
        NPC or None: 找到的 NPC 物件，沒有則回傳 None\n
        """
        if not hasattr(self, 'npc_manager') or not self.npc_manager:
            return None
        
        # 遍歷所有 NPC 檢查碰撞
        for npc in self.npc_manager.all_npcs:
            # 計算 NPC 的邊界框
            npc_rect = pygame.Rect(npc.x - 16, npc.y - 16, 32, 32)
            
            # 檢查點擊位置是否在 NPC 邊界內
            if npc_rect.collidepoint(world_x, world_y):
                return npc
        
        return None

    def _find_building_at_position(self, x, y):
        """
        在指定位置查找建築物\n
        \n
        參數:\n
        x (float): X座標\n
        y (float): Y座標\n
        \n
        回傳:\n
        Building: 找到的建築物，如果沒有則返回None\n
        """
        # 首先嘗試精確的邊界檢測
        for building in self.terrain_system.buildings:
            if hasattr(building, 'x') and hasattr(building, 'y') and hasattr(building, 'width') and hasattr(building, 'height'):
                # 檢查點是否在建築物的矩形範圍內
                if (building.x <= x <= building.x + building.width and 
                    building.y <= y <= building.y + building.height):
                    print(f"DEBUG: 精確檢測找到建築物: {getattr(building, 'name', 'N/A')} ({getattr(building, 'building_type', 'N/A')})")
                    return building
        
        # 如果精確檢測沒有找到，使用範圍檢測（向後兼容）
        interaction_range = 100  # 增加互動範圍
        closest_building = None
        closest_distance = float('inf')
        
        for building in self.terrain_system.buildings:
            if hasattr(building, 'x') and hasattr(building, 'y'):
                # 計算到建築物中心的距離
                building_center_x = building.x + getattr(building, 'width', 0) // 2
                building_center_y = building.y + getattr(building, 'height', 0) // 2
                distance = ((x - building_center_x) ** 2 + (y - building_center_y) ** 2) ** 0.5
                
                if distance <= interaction_range and distance < closest_distance:
                    closest_building = building
                    closest_distance = distance
        
        if closest_building:
            print(f"DEBUG: 範圍檢測找到建築物: {getattr(closest_building, 'name', 'N/A')} 距離: {closest_distance:.1f}")
        else:
            print(f"DEBUG: 未找到任何建築物在位置 ({x}, {y})")
            
        return closest_building
    
    def _handle_weapon_shoot(self, screen_pos, world_x, world_y):
        """
        處理武器射擊事件\n
        
        參數:\n
        screen_pos (tuple): 螢幕座標位置\n
        world_x (float): 世界座標 X\n
        world_y (float): 世界座標 Y\n
        """
        if not hasattr(self.player, 'weapon_manager') or not self.player.weapon_manager:
            return
            
        # 獲取當前武器
        current_weapon = self.player.weapon_manager.current_weapon
        if not current_weapon:
            return
            
        # 執行射擊
        player_pos = (self.player.x, self.player.y)
        target_pos = (world_x, world_y)
        
        shoot_result = current_weapon.shoot(target_pos, player_pos)
        
        if shoot_result['success']:
            print(f"使用 {current_weapon.name} 射擊！")
            
            # 如果命中，檢查是否擊中動物
            if shoot_result['hit']:
                # 調用野生動物管理器處理射擊
                animal_result = self.wildlife_manager.handle_player_shoot(
                    player_pos, 
                    target_pos, 
                    shoot_result['damage'], 
                    current_weapon.range
                )
                
                if animal_result['hit_animal']:
                    animal = animal_result['hit_animal']
                    damage = animal_result['damage_dealt']
                    is_kill = animal_result['kill']
                    
                    if is_kill:
                        print(f"擊殺了 {animal.animal_type.value}！獲得經驗值和金錢。")
                        # 這裡可以添加獎勵邏輯
                    else:
                        print(f"擊中了 {animal.animal_type.value}，造成 {damage} 點傷害！")
                else:
                    print("射擊命中但沒有擊中任何動物")
            else:
                print("射擊脫靶！")
        else:
            print("無法射擊（可能需要重新裝彈）")
    
    def _get_shop_type_from_building(self, building_type):
        """
        根據建築物類型返回對應的商店類型
        
        參數:
        building_type (str): 建築物類型
        
        回傳:
        ShopType: 對應的商店類型，如果沒有對應則返回 None
        """
        from src.systems.shop_system import ShopType
        
        mapping = {
            "convenience_store": ShopType.CONVENIENCE_STORE,
            "gun_shop": ShopType.GUN_STORE,
            "clothing_store": ShopType.CLOTHING_STORE,
            "hospital": ShopType.HOSPITAL
        }
        
        return mapping.get(building_type)
    
    def _setup_combat_system(self):
        """
        設置戰鬥系統，包括玩家受攻擊回調\n
        """
        # 設置動物攻擊玩家的回調
        def handle_animal_attack(damage, source_animal):
            """處理動物攻擊玩家的回調"""
            if self.player.take_damage(damage, source_animal):
                print(f"玩家被 {source_animal.animal_type.value} 攻擊，受到 {damage} 點傷害！")
                
                # 檢查玩家是否死亡
                if not self.player.is_alive:
                    print("玩家已死亡，正在傳送到醫院...")
        
        # 設置野生動物管理器的攻擊回調
        if hasattr(self, 'wildlife_manager'):
            self.wildlife_manager.set_player_attack_callback(handle_animal_attack)

    def _add_test_shop_buildings(self):
        """
        手動添加測試用的商店建築物到小鎮商業區
        按照新需求：刪除原有建築，新增5個一格一個的專門商店
        """
        from src.systems.building_system import Building
        
        # 清除原有的商業建築物
        print("🗑️ 清除原有商業建築物...")
        self.terrain_system.buildings = [
            building for building in self.terrain_system.buildings 
            if not hasattr(building, 'building_type') or building.building_type not in [
                "market", "bank", "office_building", "factory", "restaurant"
            ]
        ]
        
        # 商業區位置：地圖座標 (70-80, 40-50) 區域
        # 每個格子 32x32 像素，所以世界座標需要乘以 32
        
        # 槍械店 - 按照新需求重新配置
        gun_shop = Building(
            building_type="gun_shop",
            position=(70 * 32, 40 * 32),  # (2240, 1280)
            size=(32, 32)
        )
        gun_shop.name = "獵人武器店"
        self.terrain_system.buildings.append(gun_shop)
        
        # 服裝店 
        clothing_store = Building(
            building_type="clothing_store",
            position=(72 * 32, 40 * 32),  # (2304, 1280)
            size=(32, 32)
        )
        clothing_store.name = "時尚服飾店"
        self.terrain_system.buildings.append(clothing_store)
        
        # 便利商店
        convenience_store = Building(
            building_type="convenience_store",
            position=(74 * 32, 40 * 32),  # (2368, 1280)
            size=(32, 32)
        )
        convenience_store.name = "小鎮便利商店"
        self.terrain_system.buildings.append(convenience_store)
        
        # 醫院
        hospital = Building(
            building_type="hospital",
            position=(78 * 32, 40 * 32),  # (2496, 1280)
            size=(32, 32)
        )
        hospital.name = "小鎮醫院"
        self.terrain_system.buildings.append(hospital)
        
        print(f"✅ 已在商業區添加 5 個新商店建築物")
        print(f"📍 商店位置：槍械店(2240,1280), 服裝店(2304,1280), 便利商店(2368,1280), 漫畫商城(2432,1280), 醫院(2496,1280)")
        print(f"🏢 總建築物數量: {len(self.terrain_system.buildings)}")
        
        # 確保所有建築物都有 interact 方法
        for building in self.terrain_system.buildings:
            if not hasattr(building, 'interact'):
                building.interact = self._create_default_interact_method(building)

    def _create_default_interact_method(self, building):
        """
        為建築物創建預設的互動方法
        
        參數:
        building: 建築物實例
        
        回傳:
        function: 互動方法
        """
        def interact(player):
            """
            建築物的預設互動方法
            
            參數:
            player: 玩家實例
            
            回傳:
            dict: 互動結果
            """
            building_type = getattr(building, 'building_type', 'unknown')
            
            # 商店類型建築物可以開啟商店
            if building_type in ["convenience_store", "gun_shop", "clothing_store", "hospital"]:
                return {
                    "success": True,
                    "action": "open_shop",
                    "message": f"歡迎來到{getattr(building, 'name', '商店')}！"
                }
            
            # 其他建築物的預設互動
            return {
                "success": True,
                "action": "general_interact",
                "message": f"你與{getattr(building, 'name', '建築物')}進行了互動"
            }
        
        return interact