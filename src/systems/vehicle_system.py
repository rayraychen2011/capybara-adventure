######################載入套件######################
import pygame
import math
from config.settings import *


######################載具類別######################
class Vehicle:
    """
    載具基礎類別 - 提供快速移動能力\n
    \n
    載具系統讓玩家可以更快速地在大地圖間移動\n
    支援不同類型的載具，每種都有不同的速度和特性\n
    載具可以在小鎮的特定地點獲得或租借\n
    """

    def __init__(self, vehicle_type, position):
        """
        初始化載具\n
        \n
        參數:\n
        vehicle_type (str): 載具類型 ("car", "bike", "motorcycle")\n
        position (tuple): 初始位置 (x, y)\n
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

        print(f"創建 {vehicle_type} 載具在位置 {position}")

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

        elif self.vehicle_type == "bike":
            self.name = "自行車"
            self.base_speed = VEHICLE_SPEED * 0.8  # 自行車較慢
            self.color = BIKE_COLOR
            self.fuel_consumption = 0  # 不消耗燃料
            self.capacity = 1

        elif self.vehicle_type == "motorcycle":
            self.name = "機車"
            self.base_speed = VEHICLE_SPEED * 1.2
            self.color = (255, 255, 0)  # 黃色
            self.fuel_consumption = 0.05
            self.capacity = 2

        else:
            # 預設設定
            self.name = "未知載具"
            self.base_speed = VEHICLE_SPEED
            self.color = (128, 128, 128)
            self.fuel_consumption = 0.1
            self.capacity = 1

    def update(self, dt, input_controller=None):
        """
        更新載具狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        input_controller (InputController): 輸入控制器 (如果有駕駛員)\n
        """
        if self.is_occupied and input_controller:
            # 處理駕駛輸入
            self._handle_driving_input(input_controller, dt)

        # 更新載具物理
        self._update_physics(dt)

        # 更新燃料消耗
        if self.is_occupied and (
            abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1
        ):
            self.fuel = max(0, self.fuel - self.fuel_consumption * dt)

        # 檢查燃料耗盡
        if self.fuel <= 0 and self.vehicle_type != "bike":
            self.max_speed = self.base_speed * 0.1  # 燃料耗盡時速度大幅降低
        else:
            self.max_speed = self.base_speed

    def _handle_driving_input(self, input_controller, dt):
        """
        處理駕駛輸入\n
        \n
        參數:\n
        input_controller (InputController): 輸入控制器\n
        dt (float): 時間間隔\n
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

        # 繪製載具類型標識
        if self.vehicle_type == "car":
            # 繪製車輪
            wheel_color = (50, 50, 50)
            wheel_size = 8
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
            wheel_size = 6
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

        # 如果被佔用，繪製駕駛員指示
        if self.is_occupied:
            pygame.draw.circle(
                screen, (255, 255, 0), (self.rect.centerx, self.rect.centery - 10), 3
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
    """

    def __init__(self):
        """
        初始化載具管理器\n
        """
        self.vehicles = []
        self.spawn_points = []  # 載具生成點

        print("載具管理器初始化完成")

    def add_spawn_point(self, position, vehicle_types=None):
        """
        新增載具生成點\n
        \n
        參數:\n
        position (tuple): 生成位置 (x, y)\n
        vehicle_types (list): 可生成的載具類型，None表示所有類型\n
        """
        if vehicle_types is None:
            vehicle_types = ["car", "bike", "motorcycle"]

        spawn_point = {
            "position": position,
            "vehicle_types": vehicle_types,
            "occupied": False,
            "vehicle": None,
        }

        self.spawn_points.append(spawn_point)

    def spawn_initial_vehicles(self):
        """
        在生成點生成初始載具\n
        """
        import random

        for spawn_point in self.spawn_points:
            if random.random() < 0.7:  # 70% 機率生成載具
                vehicle_type = random.choice(spawn_point["vehicle_types"])
                vehicle = Vehicle(vehicle_type, spawn_point["position"])

                self.vehicles.append(vehicle)
                spawn_point["occupied"] = True
                spawn_point["vehicle"] = vehicle

    def update(self, dt, input_controller=None, active_driver=None):
        """
        更新所有載具\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        input_controller (InputController): 輸入控制器\n
        active_driver (Player): 當前駕駛的玩家\n
        """
        for vehicle in self.vehicles:
            # 只有當前駕駛的載具才接收輸入
            if vehicle.driver == active_driver:
                vehicle.update(dt, input_controller)
            else:
                vehicle.update(dt)

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
        y_offset = 100

        # 顯示載具統計
        vehicle_text = font.render(
            f"載具數量: {len(self.vehicles)}", True, (255, 255, 255)
        )
        screen.blit(vehicle_text, (10, y_offset))

        occupied_count = sum(1 for v in self.vehicles if v.is_occupied)
        occupied_text = font.render(f"使用中: {occupied_count}", True, (255, 255, 255))
        screen.blit(occupied_text, (10, y_offset + 20))

        # 顯示生成點資訊
        spawn_text = font.render(
            f"生成點: {len(self.spawn_points)}", True, (255, 255, 255)
        )
        screen.blit(spawn_text, (10, y_offset + 40))
