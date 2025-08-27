######################載入套件######################
import pygame
import math
import random
from config.settings import *


######################載具類別######################
class Vehicle:
    """
    載具基礎類別 - 提供快速移動能力\n
    \n
    載具系統讓玩家可以更快速地在大地圖間移動\n
    支援不同類型的載具，每種都有不同的速度和特性\n
    載具可以在小鎮的特定地點獲得或租借\n
    新增交通規則遵守和道路導航功能\n
    """

    def __init__(self, vehicle_type, position, is_ai_controlled=False):
        """
        初始化載具\n
        \n
        參數:\n
        vehicle_type (str): 載具類型 ("car", "bike", "motorcycle", "truck", "bus")\n
        position (tuple): 初始位置 (x, y)\n
        is_ai_controlled (bool): 是否為 AI 控制的載具\n
        """
        self.vehicle_type = vehicle_type
        self.x, self.y = position
        self.rect = pygame.Rect(self.x, self.y, VEHICLE_WIDTH, VEHICLE_HEIGHT)

        # 根據載具類型設定屬性
        self._setup_vehicle_properties()

        # 載具狀態
        self.is_occupied = False  # 是否被玩家使用
        self.driver = None  # 當前駕駛員
        self.fuel = 100.0  # 燃料 (0-100)
        self.condition = 100.0  # 車況 (0-100)

        # 移動相關
        self.velocity_x = 0
        self.velocity_y = 0
        self.max_speed = self.base_speed
        self.acceleration = 0.5
        self.friction = 0.9

        # AI 控制相關
        self.is_ai_controlled = is_ai_controlled
        self.ai_destination = None
        self.ai_path = []
        self.ai_current_road = None
        self.ai_speed_factor = 1.0  # AI 速度調整因子

        # 交通規則遵守
        self.follows_traffic_rules = True
        self.stopped_at_light = False
        self.waiting_for_pedestrian = False
        self.current_lane = 0  # 當前車道 (0=右車道, 1=左車道)

        # 行為狀態
        self.behavior_state = "cruising"  # cruising, stopped, turning, parking
        self.target_speed = self.max_speed

        # 感知範圍
        self.sight_range = 100
        self.brake_distance = 50

        print(
            f"創建 {vehicle_type} 載具在位置 {position}{'(AI控制)' if is_ai_controlled else ''}"
        )

    def _setup_vehicle_properties(self):
        """
        根據載具類型設定屬性\n
        """
        if self.vehicle_type == "car":
            self.name = "汽車"
            self.base_speed = VEHICLE_SPEED * 1.5  # 汽車最快
            self.color = CAR_COLOR
            self.fuel_consumption = 0.1  # 每秒消耗燃料
            self.capacity = 4  # 可載人數
            self.size_multiplier = 1.0

        elif self.vehicle_type == "bike":
            self.name = "自行車"
            self.base_speed = VEHICLE_SPEED * 0.8  # 自行車較慢
            self.color = BIKE_COLOR
            self.fuel_consumption = 0  # 不消耗燃料
            self.capacity = 1
            self.size_multiplier = 0.7

        elif self.vehicle_type == "motorcycle":
            self.name = "機車"
            self.base_speed = VEHICLE_SPEED * 1.2
            self.color = (255, 255, 0)  # 黃色
            self.fuel_consumption = 0.05
            self.capacity = 2
            self.size_multiplier = 0.8

        elif self.vehicle_type == "truck":
            self.name = "卡車"
            self.base_speed = VEHICLE_SPEED * 0.9
            self.color = (139, 69, 19)  # 棕色
            self.fuel_consumption = 0.2
            self.capacity = 2
            self.size_multiplier = 1.5

        elif self.vehicle_type == "bus":
            self.name = "公車"
            self.base_speed = VEHICLE_SPEED * 0.7
            self.color = (0, 100, 200)  # 藍色
            self.fuel_consumption = 0.3
            self.capacity = 30
            self.size_multiplier = 2.0

        else:
            # 預設設定
            self.name = "未知載具"
            self.base_speed = VEHICLE_SPEED
            self.color = (128, 128, 128)
            self.fuel_consumption = 0.1
            self.capacity = 1
            self.size_multiplier = 1.0

        # 根據尺寸調整碰撞矩形
        width = int(VEHICLE_WIDTH * self.size_multiplier)
        height = int(VEHICLE_HEIGHT * self.size_multiplier)
        self.rect = pygame.Rect(self.x, self.y, width, height)

    def update(
        self,
        dt,
        input_controller=None,
        road_manager=None,
        other_vehicles=None,
        pedestrians=None,
    ):
        """
        更新載具狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        input_controller (InputController): 輸入控制器 (如果有駕駛員)\n
        road_manager (RoadManager): 道路管理器\n
        other_vehicles (list): 其他載具列表\n
        pedestrians (list): 行人列表\n
        """
        if self.is_ai_controlled:
            # AI 控制的載具
            self._update_ai_behavior(dt, road_manager, other_vehicles, pedestrians)
        elif self.is_occupied and input_controller:
            # 玩家控制的載具
            self._handle_driving_input(input_controller, dt, road_manager)

        # 更新載具物理
        self._update_physics(dt)

        # 更新燃料消耗
        if (self.is_occupied or self.is_ai_controlled) and (
            abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1
        ):
            self.fuel = max(0, self.fuel - self.fuel_consumption * dt)

        # 檢查燃料耗盡
        if self.fuel <= 0 and self.vehicle_type != "bike":
            self.max_speed = self.base_speed * 0.1  # 燃料耗盡時速度大幅降低
        else:
            self.max_speed = self.base_speed

    def _update_ai_behavior(self, dt, road_manager, other_vehicles, pedestrians):
        """
        更新 AI 載具行為\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        road_manager (RoadManager): 道路管理器\n
        other_vehicles (list): 其他載具列表\n
        pedestrians (list): 行人列表\n
        """
        if not road_manager:
            return

        # 檢查前方障礙物
        self._check_obstacles(other_vehicles, pedestrians)

        # 檢查交通號誌
        self._check_traffic_lights(road_manager)

        # 遵循道路行駛
        self._follow_road(road_manager, dt)

        # 調整速度
        self._adjust_speed(dt)

    def _check_obstacles(self, other_vehicles, pedestrians):
        """
        檢查前方障礙物\n
        \n
        參數:\n
        other_vehicles (list): 其他載具列表\n
        pedestrians (list): 行人列表\n
        """
        # 重置狀態
        self.waiting_for_pedestrian = False
        obstacle_detected = False

        # 檢查前方是否有行人
        if pedestrians:
            for pedestrian in pedestrians:
                distance = math.sqrt(
                    (self.x - pedestrian.x) ** 2 + (self.y - pedestrian.y) ** 2
                )
                if distance < self.brake_distance:
                    # 檢查行人是否在車輛前進路徑上
                    if self._is_in_path(pedestrian.x, pedestrian.y):
                        self.waiting_for_pedestrian = True
                        obstacle_detected = True
                        break

        # 檢查前方是否有其他載具
        if other_vehicles and not obstacle_detected:
            for other_vehicle in other_vehicles:
                if other_vehicle == self:
                    continue

                distance = math.sqrt(
                    (self.x - other_vehicle.x) ** 2 + (self.y - other_vehicle.y) ** 2
                )
                if distance < self.brake_distance:
                    if self._is_in_path(other_vehicle.x, other_vehicle.y):
                        obstacle_detected = True
                        break

        # 設定目標速度
        if obstacle_detected:
            self.target_speed = 0
            self.behavior_state = "stopped"
        else:
            self.target_speed = self.max_speed * self.ai_speed_factor
            self.behavior_state = "cruising"

    def _is_in_path(self, target_x, target_y):
        """
        檢查目標是否在載具的前進路徑上\n
        \n
        參數:\n
        target_x (float): 目標 x 座標\n
        target_y (float): 目標 y 座標\n
        \n
        回傳:\n
        bool: 是否在路徑上\n
        """
        # 計算載具的前進方向
        if abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
            return False  # 載具靜止

        # 正規化速度向量
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed == 0:
            return False

        dir_x = self.velocity_x / speed
        dir_y = self.velocity_y / speed

        # 計算到目標的向量
        to_target_x = target_x - self.x
        to_target_y = target_y - self.y

        # 計算投影長度
        projection = to_target_x * dir_x + to_target_y * dir_y

        # 如果投影為正且目標在合理距離內
        if projection > 0 and projection < self.sight_range:
            # 計算垂直距離
            perp_distance = abs(to_target_x * (-dir_y) + to_target_y * dir_x)
            return perp_distance < self.rect.width

        return False

    def _check_traffic_lights(self, road_manager):
        """
        檢查交通號誌\n
        \n
        參數:\n
        road_manager (RoadManager): 道路管理器\n
        """
        if not self.follows_traffic_rules:
            return

        # 獲取附近的路口
        nearby_intersections = road_manager.get_intersections_near(
            (self.x, self.y), self.brake_distance
        )

        self.stopped_at_light = False

        for intersection in nearby_intersections:
            if intersection.has_traffic_light:
                # 判斷接近方向
                approach_direction = self._get_approach_direction(intersection)

                # 檢查是否可以通過
                if not intersection.can_vehicle_pass(approach_direction):
                    # 計算到路口的距離
                    distance = math.sqrt(
                        (self.x - intersection.position[0]) ** 2
                        + (self.y - intersection.position[1]) ** 2
                    )

                    # 如果距離足夠近，需要停車
                    if distance < self.brake_distance:
                        self.stopped_at_light = True
                        self.target_speed = 0
                        self.behavior_state = "stopped"
                        break

    def _get_approach_direction(self, intersection):
        """
        獲取接近路口的方向\n
        \n
        參數:\n
        intersection (Intersection): 路口\n
        \n
        回傳:\n
        str: 接近方向\n
        """
        ix, iy = intersection.position
        dx = self.x - ix
        dy = self.y - iy

        # 根據相對位置判斷方向
        if abs(dx) > abs(dy):
            return "west" if dx < 0 else "east"
        else:
            return "north" if dy < 0 else "south"

    def _follow_road(self, road_manager, dt):
        """
        沿著道路行駛\n
        \n
        參數:\n
        road_manager (RoadManager): 道路管理器\n
        dt (float): 時間間隔\n
        """
        # 獲取當前最近的道路
        current_road = road_manager.get_nearest_road((self.x, self.y))

        if not current_road:
            return

        self.ai_current_road = current_road

        # 計算道路的方向向量
        road_dx = current_road.end_pos[0] - current_road.start_pos[0]
        road_dy = current_road.end_pos[1] - current_road.start_pos[1]
        road_length = math.sqrt(road_dx**2 + road_dy**2)

        if road_length == 0:
            return

        # 正規化道路方向
        road_dir_x = road_dx / road_length
        road_dir_y = road_dy / road_length

        # 判斷載具應該朝哪個方向行駛
        # 如果載具更接近起點，則向終點行駛，反之亦然
        to_start = math.sqrt(
            (self.x - current_road.start_pos[0]) ** 2
            + (self.y - current_road.start_pos[1]) ** 2
        )
        to_end = math.sqrt(
            (self.x - current_road.end_pos[0]) ** 2
            + (self.y - current_road.end_pos[1]) ** 2
        )

        if to_start > to_end:
            # 反向行駛
            road_dir_x = -road_dir_x
            road_dir_y = -road_dir_y

        # 設定 AI 目標方向
        if not self.stopped_at_light and not self.waiting_for_pedestrian:
            # 應用加速度朝道路方向
            self.velocity_x += road_dir_x * self.acceleration * dt * 10
            self.velocity_y += road_dir_y * self.acceleration * dt * 10

    def _adjust_speed(self, dt):
        """
        調整載具速度\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)

        # 根據目標速度調整
        if current_speed > self.target_speed:
            # 減速
            if current_speed > 0:
                brake_factor = max(0.1, self.target_speed / current_speed)
                self.velocity_x *= brake_factor
                self.velocity_y *= brake_factor

        # 限制最大速度
        if current_speed > self.max_speed:
            scale_factor = self.max_speed / current_speed
            self.velocity_x *= scale_factor
            self.velocity_y *= scale_factor

    def _handle_driving_input(self, input_controller, dt, road_manager=None):
        """
        處理駕駛輸入\n
        \n
        參數:\n
        input_controller (InputController): 輸入控制器\n
        dt (float): 時間間隔\n
        road_manager (RoadManager): 道路管理器\n
        """
        # 獲取輸入方向
        keys = pygame.key.get_pressed()

        # 加速度控制
        accel_x = 0
        accel_y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            accel_y = -self.acceleration
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            accel_y = self.acceleration
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            accel_x = -self.acceleration
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            accel_x = self.acceleration

        # 檢查道路限制（玩家也需要遵守一些基本交通規則）
        if road_manager and self.follows_traffic_rules:
            target_x = self.x + self.velocity_x + accel_x
            target_y = self.y + self.velocity_y + accel_y

            if not road_manager.can_vehicle_move_to(self, (target_x, target_y)):
                # 如果不能移動到目標位置，減少加速度
                accel_x *= 0.5
                accel_y *= 0.5

        # 應用加速度
        self.velocity_x += accel_x
        self.velocity_y += accel_y

        # 限制最大速度
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed > self.max_speed:
            self.velocity_x = (self.velocity_x / speed) * self.max_speed
            self.velocity_y = (self.velocity_y / speed) * self.max_speed

    def _update_physics(self, dt):
        """
        更新載具物理\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 應用摩擦力
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y

        # 更新碰撞矩形
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def get_on(self, driver):
        """
        上車\n
        \n
        參數:\n
        driver (Player): 駕駛員\n
        \n
        回傳:\n
        bool: 是否成功上車\n
        """
        if not self.is_occupied:
            self.is_occupied = True
            self.driver = driver
            print(
                f"{driver.name if hasattr(driver, 'name') else '玩家'} 開始駕駛 {self.name}"
            )
            return True
        return False

    def get_off(self):
        """
        下車\n
        \n
        回傳:\n
        tuple: 下車位置 (x, y)\n
        """
        if self.is_occupied:
            driver = self.driver
            self.is_occupied = False
            self.driver = None

            # 停止載具移動
            self.velocity_x = 0
            self.velocity_y = 0

            # 返回安全的下車位置
            exit_x = self.x + VEHICLE_WIDTH + 10
            exit_y = self.y

            print(
                f"{driver.name if hasattr(driver, 'name') else '玩家'} 停止駕駛 {self.name}"
            )
            return (exit_x, exit_y)

        return (self.x, self.y)

    def can_interact(self, player_position, max_distance=50):
        """
        檢查玩家是否可以與載具互動\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        max_distance (float): 最大互動距離\n
        \n
        回傳:\n
        bool: 是否可以互動\n
        """
        px, py = player_position
        distance = math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2)
        return distance <= max_distance and not self.is_occupied

    def draw(self, screen):
        """
        繪製載具\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 繪製載具主體
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        # 根據載具類型繪製特殊標識
        if self.vehicle_type == "car":
            # 繪製車輪
            wheel_color = (50, 50, 50)
            wheel_size = int(8 * self.size_multiplier)
            pygame.draw.circle(
                screen,
                wheel_color,
                (self.rect.left + 10, self.rect.bottom - 5),
                wheel_size,
            )
            pygame.draw.circle(
                screen,
                wheel_color,
                (self.rect.right - 10, self.rect.bottom - 5),
                wheel_size,
            )

        elif self.vehicle_type == "bike":
            # 繪製車輪 (較小)
            wheel_color = (100, 100, 100)
            wheel_size = int(6 * self.size_multiplier)
            pygame.draw.circle(
                screen,
                wheel_color,
                (self.rect.left + 8, self.rect.bottom - 3),
                wheel_size,
            )
            pygame.draw.circle(
                screen,
                wheel_color,
                (self.rect.right - 8, self.rect.bottom - 3),
                wheel_size,
            )

        elif self.vehicle_type == "truck":
            # 繪製卡車貨斗
            cargo_rect = pygame.Rect(
                self.rect.x + self.rect.width // 3,
                self.rect.y - 5,
                self.rect.width * 2 // 3,
                self.rect.height + 10,
            )
            pygame.draw.rect(screen, (101, 67, 33), cargo_rect)  # 深棕色貨斗
            pygame.draw.rect(screen, (0, 0, 0), cargo_rect, 1)

        elif self.vehicle_type == "bus":
            # 繪製公車窗戶
            window_color = (173, 216, 230)  # 淺藍色
            window_width = self.rect.width // 4
            window_height = self.rect.height // 3

            for i in range(3):  # 3個窗戶
                window_x = self.rect.x + 5 + i * (window_width + 5)
                window_y = self.rect.y + 5
                pygame.draw.rect(
                    screen,
                    window_color,
                    (window_x, window_y, window_width, window_height),
                )

        # 如果被佔用，繪製駕駛員指示
        if self.is_occupied:
            pygame.draw.circle(
                screen, (255, 255, 0), (self.rect.centerx, self.rect.centery - 10), 3
            )

        # 如果是 AI 控制且停車，顯示狀態指示
        if self.is_ai_controlled:
            if self.behavior_state == "stopped":
                # 繪製停車指示
                if self.stopped_at_light:
                    pygame.draw.circle(
                        screen, (255, 0, 0), (self.rect.centerx, self.rect.centery), 5
                    )
                elif self.waiting_for_pedestrian:
                    pygame.draw.circle(
                        screen, (255, 165, 0), (self.rect.centerx, self.rect.centery), 5
                    )

    def draw_info(self, screen, font):
        """
        繪製載具資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體\n
        """
        # 顯示載具名稱
        name_text = font.render(self.name, True, (255, 255, 255))
        screen.blit(name_text, (self.rect.x, self.rect.y - 40))

        # 顯示燃料 (如果需要)
        if self.fuel_consumption > 0:
            fuel_text = font.render(f"燃料: {int(self.fuel)}%", True, (255, 255, 255))
            screen.blit(fuel_text, (self.rect.x, self.rect.y - 20))


######################載具管理器######################
class VehicleManager:
    """
    載具管理器 - 統一管理所有載具\n
    \n
    負責載具的生成、更新、互動檢測等功能\n
    確保載具在合適的位置出現，並提供給玩家使用\n
    新增 AI 載具的自動生成和交通流量控制\n
    """

    def __init__(self):
        """
        初始化載具管理器\n
        """
        self.vehicles = []
        self.spawn_points = []  # 載具生成點
        self.ai_vehicles = []  # AI 控制的載具
        self.player_vehicles = []  # 玩家可用的載具

        # 交通流量控制
        self.max_ai_vehicles = 20  # 最大 AI 載具數量
        self.spawn_timer = 0.0
        self.spawn_interval = 5.0  # 每5秒嘗試生成新載具

        # 載具類型分佈
        self.vehicle_type_weights = {
            "car": 50,  # 50% 汽車
            "motorcycle": 20,  # 20% 機車
            "truck": 15,  # 15% 卡車
            "bus": 10,  # 10% 公車
            "bike": 5,  # 5% 自行車
        }

        print("載具管理器初始化完成")

    def add_spawn_point(self, position, vehicle_types=None, is_ai_spawn=True):
        """
        新增載具生成點\n
        \n
        參數:\n
        position (tuple): 生成位置 (x, y)\n
        vehicle_types (list): 可生成的載具類型，None表示所有類型\n
        is_ai_spawn (bool): 是否為 AI 載具生成點\n
        """
        if vehicle_types is None:
            vehicle_types = ["car", "bike", "motorcycle", "truck", "bus"]

        spawn_point = {
            "position": position,
            "vehicle_types": vehicle_types,
            "occupied": False,
            "vehicle": None,
            "is_ai_spawn": is_ai_spawn,
            "last_spawn_time": 0.0,
        }

        self.spawn_points.append(spawn_point)

    def create_map_edge_spawns(self, town_bounds):
        """
        在地圖邊緣創建載具生成點\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界 (x, y, width, height)\n
        """
        tx, ty, tw, th = town_bounds

        # 上邊界生成點
        for i in range(5):
            x = tx + (i + 1) * (tw / 6)
            spawn_point = (x, ty - 50)
            self.add_spawn_point(spawn_point, is_ai_spawn=True)

        # 下邊界生成點
        for i in range(5):
            x = tx + (i + 1) * (tw / 6)
            spawn_point = (x, ty + th + 50)
            self.add_spawn_point(spawn_point, is_ai_spawn=True)

        # 左邊界生成點
        for i in range(3):
            y = ty + (i + 1) * (th / 4)
            spawn_point = (tx - 50, y)
            self.add_spawn_point(spawn_point, is_ai_spawn=True)

        # 右邊界生成點
        for i in range(3):
            y = ty + (i + 1) * (th / 4)
            spawn_point = (tx + tw + 50, y)
            self.add_spawn_point(spawn_point, is_ai_spawn=True)

    def spawn_initial_vehicles(self):
        """
        在生成點生成初始載具\n
        """
        # 生成玩家可用的載具（停在特定位置）
        player_spawn_points = [sp for sp in self.spawn_points if not sp["is_ai_spawn"]]

        for spawn_point in player_spawn_points[:5]:  # 限制玩家載具數量
            if random.random() < 0.8:  # 80% 機率生成載具
                vehicle_type = random.choice(spawn_point["vehicle_types"])
                vehicle = Vehicle(
                    vehicle_type, spawn_point["position"], is_ai_controlled=False
                )

                self.vehicles.append(vehicle)
                self.player_vehicles.append(vehicle)
                spawn_point["occupied"] = True
                spawn_point["vehicle"] = vehicle

    def update(
        self,
        dt,
        input_controller=None,
        active_driver=None,
        road_manager=None,
        pedestrians=None,
    ):
        """
        更新所有載具\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        input_controller (InputController): 輸入控制器\n
        active_driver (Player): 當前駕駛的玩家\n
        road_manager (RoadManager): 道路管理器\n
        pedestrians (list): 行人列表\n
        """
        # 更新生成計時器
        self.spawn_timer += dt

        # 嘗試生成新的 AI 載具
        if self.spawn_timer >= self.spawn_interval:
            self._try_spawn_ai_vehicle(road_manager)
            self.spawn_timer = 0.0

        # 更新所有載具
        for vehicle in self.vehicles[:]:  # 使用切片避免修改列表時的問題
            # 只有當前駕駛的載具才接收輸入
            if vehicle.driver == active_driver:
                vehicle.update(
                    dt, input_controller, road_manager, self.vehicles, pedestrians
                )
            else:
                vehicle.update(dt, None, road_manager, self.vehicles, pedestrians)

            # 檢查 AI 載具是否需要移除（離開地圖邊界）
            if vehicle.is_ai_controlled:
                if self._should_remove_vehicle(vehicle):
                    self._remove_vehicle(vehicle)

    def _try_spawn_ai_vehicle(self, road_manager):
        """
        嘗試生成 AI 載具\n
        \n
        參數:\n
        road_manager (RoadManager): 道路管理器\n
        """
        # 檢查是否達到最大數量
        ai_vehicle_count = len(self.ai_vehicles)
        if ai_vehicle_count >= self.max_ai_vehicles:
            return

        # 選擇一個 AI 生成點
        ai_spawn_points = [
            sp for sp in self.spawn_points if sp["is_ai_spawn"] and not sp["occupied"]
        ]
        if not ai_spawn_points:
            return

        spawn_point = random.choice(ai_spawn_points)

        # 選擇載具類型（根據權重）
        vehicle_type = self._choose_vehicle_type()

        # 創建 AI 載具
        vehicle = Vehicle(vehicle_type, spawn_point["position"], is_ai_controlled=True)

        # 設定 AI 行為參數
        vehicle.ai_speed_factor = random.uniform(0.7, 1.2)  # 速度變化
        vehicle.follows_traffic_rules = random.random() < 0.9  # 90% 遵守交通規則

        # 設定目標（簡化：隨機選擇對面的生成點）
        self._set_ai_destination(vehicle, spawn_point)

        self.vehicles.append(vehicle)
        self.ai_vehicles.append(vehicle)
        spawn_point["occupied"] = True
        spawn_point["vehicle"] = vehicle

    def _choose_vehicle_type(self):
        """
        根據權重選擇載具類型\n
        \n
        回傳:\n
        str: 載具類型\n
        """
        total_weight = sum(self.vehicle_type_weights.values())
        random_value = random.randint(1, total_weight)

        current_weight = 0
        for vehicle_type, weight in self.vehicle_type_weights.items():
            current_weight += weight
            if random_value <= current_weight:
                return vehicle_type

        return "car"  # 預設回傳

    def _set_ai_destination(self, vehicle, spawn_point):
        """
        為 AI 載具設定目的地\n
        \n
        參數:\n
        vehicle (Vehicle): AI 載具\n
        spawn_point (dict): 生成點資訊\n
        """
        # 簡化版：選擇距離最遠的生成點作為目的地
        max_distance = 0
        best_destination = None

        for other_spawn in self.spawn_points:
            if other_spawn["is_ai_spawn"] and other_spawn != spawn_point:
                distance = math.sqrt(
                    (spawn_point["position"][0] - other_spawn["position"][0]) ** 2
                    + (spawn_point["position"][1] - other_spawn["position"][1]) ** 2
                )
                if distance > max_distance:
                    max_distance = distance
                    best_destination = other_spawn["position"]

        vehicle.ai_destination = best_destination

    def _should_remove_vehicle(self, vehicle):
        """
        檢查載具是否應該被移除\n
        \n
        參數:\n
        vehicle (Vehicle): 載具\n
        \n
        回傳:\n
        bool: 是否應該移除\n
        """
        # 檢查是否離開地圖邊界太遠
        for spawn_point in self.spawn_points:
            if spawn_point["is_ai_spawn"]:
                distance = math.sqrt(
                    (vehicle.x - spawn_point["position"][0]) ** 2
                    + (vehicle.y - spawn_point["position"][1]) ** 2
                )
                if distance < 100:  # 靠近邊界生成點
                    return True

        return False

    def _remove_vehicle(self, vehicle):
        """
        移除載具\n
        \n
        參數:\n
        vehicle (Vehicle): 要移除的載具\n
        """
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)

        if vehicle in self.ai_vehicles:
            self.ai_vehicles.remove(vehicle)

        # 釋放生成點
        for spawn_point in self.spawn_points:
            if spawn_point["vehicle"] == vehicle:
                spawn_point["occupied"] = False
                spawn_point["vehicle"] = None
                break

    def get_nearby_vehicle(self, player_position, max_distance=50):
        """
        獲取玩家附近的載具\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        max_distance (float): 最大距離\n
        \n
        回傳:\n
        Vehicle: 最近的可互動載具，如果沒有則返回 None\n
        """
        closest_vehicle = None
        closest_distance = float("inf")

        for vehicle in self.vehicles:
            if vehicle.can_interact(player_position, max_distance):
                px, py = player_position
                distance = math.sqrt((vehicle.x - px) ** 2 + (vehicle.y - py) ** 2)

                if distance < closest_distance:
                    closest_distance = distance
                    closest_vehicle = vehicle

        return closest_vehicle

    def get_player_vehicle(self, player):
        """
        獲取玩家當前駕駛的載具\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        Vehicle: 玩家駕駛的載具，如果沒有則返回 None\n
        """
        for vehicle in self.vehicles:
            if vehicle.driver == player:
                return vehicle
        return None

    def draw_all_vehicles(self, screen):
        """
        繪製所有載具\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for vehicle in self.vehicles:
            vehicle.draw(screen)

    def draw_debug_info(self, screen, font):
        """
        繪製除錯資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體\n
        """
        y_offset = 220

        # 顯示載具統計
        total_vehicles = len(self.vehicles)
        ai_vehicles = len(self.ai_vehicles)
        player_vehicles = len(self.player_vehicles)

        vehicle_text = font.render(f"總載具數: {total_vehicles}", True, (255, 255, 255))
        screen.blit(vehicle_text, (10, y_offset))

        ai_text = font.render(f"AI載具: {ai_vehicles}", True, (255, 255, 255))
        screen.blit(ai_text, (10, y_offset + 20))

        player_text = font.render(f"玩家載具: {player_vehicles}", True, (255, 255, 255))
        screen.blit(player_text, (10, y_offset + 40))

        occupied_count = sum(1 for v in self.vehicles if v.is_occupied)
        occupied_text = font.render(f"使用中: {occupied_count}", True, (255, 255, 255))
        screen.blit(occupied_text, (10, y_offset + 60))

        # 顯示生成點資訊
        spawn_text = font.render(
            f"生成點: {len(self.spawn_points)}", True, (255, 255, 255)
        )
        screen.blit(spawn_text, (10, y_offset + 80))

        # 顯示交通狀態
        stopped_vehicles = sum(
            1 for v in self.ai_vehicles if v.behavior_state == "stopped"
        )
        traffic_text = font.render(
            f"停車載具: {stopped_vehicles}", True, (255, 255, 255)
        )
        screen.blit(traffic_text, (10, y_offset + 100))
