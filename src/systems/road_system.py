######################載入套件######################
import pygame
import math
import random
from config.settings import *


######################路段類別######################
class RoadSegment:
    """
    道路段落類別 - 表示一段道路\n
    \n
    每個道路段落包含起點、終點、寬度等資訊\n
    支援直線和彎曲道路的繪製\n
    可以設定車道數量和行人穿越點\n
    """

    def __init__(self, start_pos, end_pos, width=60, lanes=2):
        """
        初始化道路段落\n
        \n
        參數:\n
        start_pos (tuple): 起點座標 (x, y)\n
        end_pos (tuple): 終點座標 (x, y)\n
        width (int): 道路寬度\n
        lanes (int): 車道數量\n
        """
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = width
        self.lanes = lanes

        # 計算道路的幾何屬性
        self.length = math.sqrt(
            (end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2
        )

        # 道路方向角度
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        self.angle = math.atan2(dy, dx)

        # 道路類型
        self.road_type = "street"  # street, avenue, highway

        # 交通特性
        self.has_sidewalk = True
        self.has_crosswalk = False
        self.speed_limit = 30  # km/h

        # 視覺屬性
        self.surface_color = (80, 80, 80)  # 深灰色路面
        self.line_color = (255, 255, 255)  # 白色標線
        self.sidewalk_color = (160, 160, 160)  # 淺灰色人行道

    def get_perpendicular_vector(self):
        """
        獲取垂直於道路方向的單位向量\n
        \n
        回傳:\n
        tuple: 垂直向量 (x, y)\n
        """
        perp_x = -math.sin(self.angle)
        perp_y = math.cos(self.angle)
        return (perp_x, perp_y)

    def get_road_bounds(self):
        """
        計算道路的邊界點\n
        \n
        回傳:\n
        list: 道路四角的座標點\n
        """
        perp_x, perp_y = self.get_perpendicular_vector()
        half_width = self.width / 2

        # 計算四個角的座標
        corners = [
            (
                self.start_pos[0] + perp_x * half_width,
                self.start_pos[1] + perp_y * half_width,
            ),
            (
                self.start_pos[0] - perp_x * half_width,
                self.start_pos[1] - perp_y * half_width,
            ),
            (
                self.end_pos[0] - perp_x * half_width,
                self.end_pos[1] - perp_y * half_width,
            ),
            (
                self.end_pos[0] + perp_x * half_width,
                self.end_pos[1] + perp_y * half_width,
            ),
        ]

        return corners

    def draw(self, screen):
        """
        繪製道路段落 - 已移除視覺外觀但保留邏輯\n
        \n
        根據需求移除道路、人行道、紅綠燈的外觀\n
        但保留必要的碰撞或功能邏輯\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 不再繪製任何道路視覺元素
        # 道路的邏輯功能（碰撞檢測、導航等）仍然保留
        pass

    def _draw_sidewalks(self, screen):
        """
        繪製人行道\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        perp_x, perp_y = self.get_perpendicular_vector()
        sidewalk_width = 15
        total_width = self.width / 2 + sidewalk_width

        # 左側人行道
        left_points = [
            (
                self.start_pos[0] + perp_x * (self.width / 2),
                self.start_pos[1] + perp_y * (self.width / 2),
            ),
            (
                self.start_pos[0] + perp_x * total_width,
                self.start_pos[1] + perp_y * total_width,
            ),
            (
                self.end_pos[0] + perp_x * total_width,
                self.end_pos[1] + perp_y * total_width,
            ),
            (
                self.end_pos[0] + perp_x * (self.width / 2),
                self.end_pos[1] + perp_y * (self.width / 2),
            ),
        ]
        pygame.draw.polygon(screen, self.sidewalk_color, left_points)

        # 右側人行道
        right_points = [
            (
                self.start_pos[0] - perp_x * (self.width / 2),
                self.start_pos[1] - perp_y * (self.width / 2),
            ),
            (
                self.start_pos[0] - perp_x * total_width,
                self.start_pos[1] - perp_y * total_width,
            ),
            (
                self.end_pos[0] - perp_x * total_width,
                self.end_pos[1] - perp_y * total_width,
            ),
            (
                self.end_pos[0] - perp_x * (self.width / 2),
                self.end_pos[1] - perp_y * (self.width / 2),
            ),
        ]
        pygame.draw.polygon(screen, self.sidewalk_color, right_points)

    def _draw_lane_markings(self, screen):
        """
        繪製車道標線\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        if self.lanes <= 1:
            return

        # 計算車道分隔線的位置
        for i in range(1, self.lanes):
            # 車道分隔線相對於道路中心的偏移
            offset_ratio = (i / self.lanes) - 0.5
            if self.lanes == 2:
                offset_ratio = 0  # 雙車道時線在中間

            perp_x, perp_y = self.get_perpendicular_vector()
            offset_x = perp_x * offset_ratio * self.width
            offset_y = perp_y * offset_ratio * self.width

            # 虛線樣式
            dash_length = 10
            gap_length = 15
            total_dash = dash_length + gap_length

            # 計算需要多少段虛線
            num_dashes = int(self.length / total_dash)

            for j in range(num_dashes):
                # 計算虛線起點和終點
                progress_start = (j * total_dash) / self.length
                progress_end = min(((j * total_dash) + dash_length) / self.length, 1.0)

                start_x = (
                    self.start_pos[0]
                    + (self.end_pos[0] - self.start_pos[0]) * progress_start
                    + offset_x
                )
                start_y = (
                    self.start_pos[1]
                    + (self.end_pos[1] - self.start_pos[1]) * progress_start
                    + offset_y
                )
                end_x = (
                    self.start_pos[0]
                    + (self.end_pos[0] - self.start_pos[0]) * progress_end
                    + offset_x
                )
                end_y = (
                    self.start_pos[1]
                    + (self.end_pos[1] - self.start_pos[1]) * progress_end
                    + offset_y
                )

                pygame.draw.line(
                    screen, self.line_color, (start_x, start_y), (end_x, end_y), 2
                )

    def _draw_crosswalk(self, screen):
        """
        繪製斑馬線\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 在道路中點繪製斑馬線
        mid_x = (self.start_pos[0] + self.end_pos[0]) / 2
        mid_y = (self.start_pos[1] + self.end_pos[1]) / 2

        perp_x, perp_y = self.get_perpendicular_vector()

        # 斑馬線條紋
        stripe_width = 3
        stripe_spacing = 6
        num_stripes = int(self.width / stripe_spacing)

        for i in range(num_stripes):
            offset = (i - num_stripes / 2) * stripe_spacing
            stripe_start = (mid_x + perp_x * offset, mid_y + perp_y * offset)

            # 沿著道路方向畫條紋
            dir_x = math.cos(self.angle)
            dir_y = math.sin(self.angle)
            stripe_length = 8

            stripe_end = (
                stripe_start[0] + dir_x * stripe_length,
                stripe_start[1] + dir_y * stripe_length,
            )

            pygame.draw.line(
                screen, self.line_color, stripe_start, stripe_end, stripe_width
            )


######################路口類別######################
class Intersection:
    """
    路口類別 - 表示道路的交叉點\n
    \n
    管理多條道路的交會點\n
    控制交通號誌和行人穿越\n
    處理載具和行人的通行優先權\n
    """

    def __init__(self, position, intersection_type="cross"):
        """
        初始化路口\n
        \n
        參數:\n
        position (tuple): 路口中心位置 (x, y)\n
        intersection_type (str): 路口類型 ("cross", "t_junction", "roundabout")\n
        """
        self.position = position
        self.intersection_type = intersection_type
        self.connected_roads = []

        # 交通號誌
        self.has_traffic_light = True
        self.traffic_light = TrafficLight(position)

        # 路口尺寸
        self.size = 80
        self.rect = pygame.Rect(
            position[0] - self.size // 2,
            position[1] - self.size // 2,
            self.size,
            self.size,
        )

        # 行人穿越點
        self.crosswalks = []
        self._create_crosswalks()

    def _create_crosswalks(self):
        """
        創建行人穿越點\n
        """
        # 根據路口類型創建斑馬線
        if self.intersection_type == "cross":
            # 十字路口 - 四個方向都有斑馬線
            offsets = [
                (0, -self.size // 2),
                (self.size // 2, 0),
                (0, self.size // 2),
                (-self.size // 2, 0),
            ]

            for offset in offsets:
                crosswalk_pos = (
                    self.position[0] + offset[0],
                    self.position[1] + offset[1],
                )
                self.crosswalks.append(crosswalk_pos)

    def add_road(self, road_segment):
        """
        連接道路到路口\n
        \n
        參數:\n
        road_segment (RoadSegment): 道路段落\n
        """
        self.connected_roads.append(road_segment)
        # 在連接的道路上設置斑馬線
        road_segment.has_crosswalk = True

    def update(self, dt):
        """
        更新路口狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        if self.has_traffic_light:
            self.traffic_light.update(dt)

    def can_vehicle_pass(self, vehicle, approach_direction):
        """
        檢查載具是否可以通過路口\n
        \n
        參數:\n
        vehicle (Vehicle): 載具\n
        approach_direction (str): 接近方向 ("north", "south", "east", "west")\n
        \n
        回傳:\n
        bool: 是否可以通過\n
        """
        if not self.has_traffic_light:
            return True

        return self.traffic_light.can_vehicle_pass(approach_direction)

    def can_pedestrian_cross(self, pedestrian, crossing_direction):
        """
        檢查行人是否可以穿越\n
        \n
        參數:\n
        pedestrian (NPC): 行人\n
        crossing_direction (str): 穿越方向\n
        \n
        回傳:\n
        bool: 是否可以穿越\n
        """
        if not self.has_traffic_light:
            return True

        return self.traffic_light.can_pedestrian_cross(crossing_direction)

    def draw(self, screen):
        """
        繪製路口 - 已移除視覺外觀但保留邏輯\n
        \n
        根據需求移除道路、人行道、紅綠燈的外觀\n
        但保留必要的碰撞或功能邏輯\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 不再繪製任何路口視覺元素
        # 路口的邏輯功能（交通號誌判斷、通行權等）仍然保留
        pass

    def _draw_crosswalk_at_position(self, screen, position):
        """
        在指定位置繪製斑馬線\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        position (tuple): 斑馬線位置\n
        """
        # 簡化的斑馬線繪製
        stripe_width = 3
        stripe_length = 20
        num_stripes = 5

        for i in range(num_stripes):
            stripe_x = position[0] - stripe_length // 2 + i * 4
            stripe_y = position[1]

            pygame.draw.rect(
                screen, (255, 255, 255), (stripe_x, stripe_y - 2, stripe_width, 4)
            )


######################交通號誌類別######################
class TrafficLight:
    """
    交通號誌類別 - 控制路口通行\n
    \n
    管理紅綠燈的狀態轉換\n
    協調車輛和行人的通行時間\n
    提供視覺指示和邏輯判斷\n
    """

    def __init__(self, position):
        """
        初始化交通號誌\n
        \n
        參數:\n
        position (tuple): 號誌位置 (x, y)\n
        """
        self.position = position

        # 號誌狀態 - 包含四個方向的狀態
        self.states = {
            "north_south": "green",  # 南北向狀態
            "east_west": "red",  # 東西向狀態
        }

        # 行人穿越燈
        self.pedestrian_states = {
            "north_south": "red",
            "east_west": "green",
        }

        # 時間控制
        self.green_duration = 30.0  # 綠燈時間(秒)
        self.yellow_duration = 5.0  # 黃燈時間(秒)
        self.red_duration = 35.0  # 紅燈時間(秒)

        self.current_timer = 0.0
        self.current_phase = "north_south_green"  # 當前階段

        # 視覺屬性
        self.light_radius = 8
        self.pole_width = 4
        self.pole_height = 40

    def update(self, dt):
        """
        更新交通號誌狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        self.current_timer += dt

        # 狀態轉換邏輯
        if self.current_phase == "north_south_green":
            if self.current_timer >= self.green_duration:
                self._change_to_yellow("north_south")

        elif self.current_phase == "north_south_yellow":
            if self.current_timer >= self.yellow_duration:
                self._change_to_red("north_south")
                self._change_to_green("east_west")

        elif self.current_phase == "east_west_green":
            if self.current_timer >= self.green_duration:
                self._change_to_yellow("east_west")

        elif self.current_phase == "east_west_yellow":
            if self.current_timer >= self.yellow_duration:
                self._change_to_red("east_west")
                self._change_to_green("north_south")

    def _change_to_green(self, direction):
        """
        切換到綠燈\n
        \n
        參數:\n
        direction (str): 方向 ("north_south" 或 "east_west")\n
        """
        self.states[direction] = "green"
        self.pedestrian_states[direction] = "red"  # 車輛綠燈時行人紅燈
        self.current_phase = f"{direction}_green"
        self.current_timer = 0.0

    def _change_to_yellow(self, direction):
        """
        切換到黃燈\n
        \n
        參數:\n
        direction (str): 方向\n
        """
        self.states[direction] = "yellow"
        self.current_phase = f"{direction}_yellow"
        self.current_timer = 0.0

    def _change_to_red(self, direction):
        """
        切換到紅燈\n
        \n
        參數:\n
        direction (str): 方向\n
        """
        self.states[direction] = "red"
        self.pedestrian_states[direction] = "green"  # 車輛紅燈時行人綠燈

    def can_vehicle_pass(self, approach_direction):
        """
        檢查載具是否可以通過\n
        \n
        參數:\n
        approach_direction (str): 接近方向\n
        \n
        回傳:\n
        bool: 是否可以通過\n
        """
        if approach_direction in ["north", "south"]:
            return self.states["north_south"] == "green"
        elif approach_direction in ["east", "west"]:
            return self.states["east_west"] == "green"

        return False

    def can_pedestrian_cross(self, crossing_direction):
        """
        檢查行人是否可以穿越\n
        \n
        參數:\n
        crossing_direction (str): 穿越方向\n
        \n
        回傳:\n
        bool: 是否可以穿越\n
        """
        if crossing_direction in ["north_south", "south_north"]:
            return self.pedestrian_states["north_south"] == "green"
        elif crossing_direction in ["east_west", "west_east"]:
            return self.pedestrian_states["east_west"] == "green"

        return False

    def draw(self, screen):
        """
        繪製交通號誌 - 已移除視覺外觀但保留邏輯\n
        \n
        根據需求移除紅綠燈的外觀\n
        但保留必要的邏輯功能（狀態判斷等）\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 不再繪製任何交通號誌視覺元素
        # 交通號誌的邏輯功能（狀態轉換、通行判斷等）仍然保留
        pass

    def _draw_light_box(self, screen, position, state):
        """
        繪製燈箱\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        position (tuple): 燈箱位置\n
        state (str): 燈的狀態\n
        """
        box_width = 20
        box_height = 30

        # 繪製燈箱背景
        box_rect = pygame.Rect(
            position[0] - box_width // 2,
            position[1] - box_height // 2,
            box_width,
            box_height,
        )
        pygame.draw.rect(screen, (50, 50, 50), box_rect)
        pygame.draw.rect(screen, (0, 0, 0), box_rect, 2)

        # 根據狀態繪製燈
        if state == "red":
            pygame.draw.circle(
                screen, (255, 0, 0), (position[0], position[1] - 8), self.light_radius
            )
        elif state == "yellow":
            pygame.draw.circle(
                screen, (255, 255, 0), (position[0], position[1]), self.light_radius
            )
        elif state == "green":
            pygame.draw.circle(
                screen, (0, 255, 0), (position[0], position[1] + 8), self.light_radius
            )


######################道路管理器######################
class RoadManager:
    """
    道路管理器 - 統一管理道路系統\n
    \n
    負責道路網絡的創建、維護和渲染\n
    協調路口的交通號誌系統\n
    提供載具導航和行人穿越的支援\n
    """

    def __init__(self):
        """
        初始化道路管理器\n
        """
        self.road_segments = []
        self.intersections = []
        self.road_network = {}  # 道路網絡圖

        # 道路生成設定
        self.grid_size = 200  # 道路網格大小
        self.road_width = 60
        self.default_lanes = 2

        print("道路管理器初始化完成")

    def create_road_network_for_town(self, town_bounds):
        """
        為小鎮創建道路網絡\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界 (x, y, width, height)\n
        """
        tx, ty, tw, th = town_bounds

        # 清空現有道路
        self.road_segments.clear()
        self.intersections.clear()

        # 創建主要道路網格
        self._create_main_grid(town_bounds)

        # 創建彎曲的次要道路
        self._create_curved_roads(town_bounds)

        # 創建路口
        self._create_intersections(town_bounds)

        print(
            f"道路網絡創建完成: {len(self.road_segments)} 段道路, {len(self.intersections)} 個路口"
        )

    def _create_main_grid(self, town_bounds):
        """
        創建主要的道路網格\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界\n
        """
        tx, ty, tw, th = town_bounds

        # 計算網格數量
        cols = max(3, tw // self.grid_size)
        rows = max(3, th // self.grid_size)

        # 創建水平道路
        for row in range(rows + 1):
            y = ty + row * (th / rows)
            start_pos = (tx, y)
            end_pos = (tx + tw, y)

            road = RoadSegment(start_pos, end_pos, self.road_width, self.default_lanes)
            road.road_type = "avenue" if row % 2 == 0 else "street"
            self.road_segments.append(road)

        # 創建垂直道路
        for col in range(cols + 1):
            x = tx + col * (tw / cols)
            start_pos = (x, ty)
            end_pos = (x, ty + th)

            road = RoadSegment(start_pos, end_pos, self.road_width, self.default_lanes)
            road.road_type = "avenue" if col % 2 == 0 else "street"
            self.road_segments.append(road)

    def _create_curved_roads(self, town_bounds):
        """
        創建彎曲的次要道路\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界\n
        """
        tx, ty, tw, th = town_bounds

        # 創建幾條彎曲的對角線道路
        for i in range(3):
            # 隨機起點和終點
            start_x = tx + random.randint(0, tw // 3)
            start_y = ty + random.randint(0, th // 3)
            end_x = tx + tw - random.randint(0, tw // 3)
            end_y = ty + th - random.randint(0, th // 3)

            # 創建彎曲路徑（簡化版，使用多個直線段）
            self._create_curved_path((start_x, start_y), (end_x, end_y))

    def _create_curved_path(self, start_pos, end_pos, segments=5):
        """
        創建彎曲路徑\n
        \n
        參數:\n
        start_pos (tuple): 起點\n
        end_pos (tuple): 終點\n
        segments (int): 路段數量\n
        """
        points = [start_pos]

        # 在起點和終點之間創建控制點
        for i in range(1, segments):
            progress = i / segments

            # 線性插值基礎位置
            base_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
            base_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress

            # 添加隨機彎曲
            curve_offset = 50
            offset_x = random.randint(-curve_offset, curve_offset) * math.sin(
                progress * math.pi
            )
            offset_y = random.randint(-curve_offset, curve_offset) * math.sin(
                progress * math.pi
            )

            curved_point = (base_x + offset_x, base_y + offset_y)
            points.append(curved_point)

        points.append(end_pos)

        # 創建連接這些點的道路段
        for i in range(len(points) - 1):
            road = RoadSegment(
                points[i], points[i + 1], self.road_width * 0.8, 1
            )  # 彎曲道路較窄，單車道
            road.road_type = "curved_street"
            self.road_segments.append(road)

    def _create_intersections(self, town_bounds):
        """
        創建路口\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界\n
        """
        tx, ty, tw, th = town_bounds

        # 在主要網格交點創建路口
        cols = max(3, tw // self.grid_size)
        rows = max(3, th // self.grid_size)

        for row in range(1, rows):  # 不包括邊界
            for col in range(1, cols):
                x = tx + col * (tw / cols)
                y = ty + row * (th / rows)

                intersection = Intersection((x, y), "cross")

                # 為主要路口添加交通號誌
                if row % 2 == 0 or col % 2 == 0:
                    intersection.has_traffic_light = True
                else:
                    intersection.has_traffic_light = False

                self.intersections.append(intersection)

    def update(self, dt):
        """
        更新道路系統\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新所有路口的交通號誌
        for intersection in self.intersections:
            intersection.update(dt)

    def get_nearest_road(self, position):
        """
        獲取最近的道路\n
        \n
        參數:\n
        position (tuple): 位置\n
        \n
        回傳:\n
        RoadSegment: 最近的道路段，如果沒有則返回 None\n
        """
        if not self.road_segments:
            return None

        px, py = position
        nearest_road = None
        min_distance = float("inf")

        for road in self.road_segments:
            # 計算點到線段的距離
            distance = self._point_to_line_distance(
                position, road.start_pos, road.end_pos
            )

            if distance < min_distance:
                min_distance = distance
                nearest_road = road

        return nearest_road

    def _point_to_line_distance(self, point, line_start, line_end):
        """
        計算點到線段的最短距離\n
        \n
        參數:\n
        point (tuple): 點座標\n
        line_start (tuple): 線段起點\n
        line_end (tuple): 線段終點\n
        \n
        回傳:\n
        float: 最短距離\n
        """
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end

        # 線段長度的平方
        line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2

        if line_length_sq == 0:
            # 線段退化為點
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

        # 計算投影參數
        t = max(
            0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_length_sq)
        )

        # 投影點
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)

        # 返回距離
        return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)

    def get_intersections_near(self, position, radius=100):
        """
        獲取附近的路口\n
        \n
        參數:\n
        position (tuple): 位置\n
        radius (float): 搜索半徑\n
        \n
        回傳:\n
        list: 附近的路口列表\n
        """
        px, py = position
        nearby_intersections = []

        for intersection in self.intersections:
            ix, iy = intersection.position
            distance = math.sqrt((px - ix) ** 2 + (py - iy) ** 2)

            if distance <= radius:
                nearby_intersections.append(intersection)

        return nearby_intersections

    def can_vehicle_move_to(self, vehicle, target_position):
        """
        檢查載具是否可以移動到目標位置\n
        \n
        參數:\n
        vehicle (Vehicle): 載具\n
        target_position (tuple): 目標位置\n
        \n
        回傳:\n
        bool: 是否可以移動\n
        """
        # 檢查是否在道路上
        nearest_road = self.get_nearest_road(target_position)
        if not nearest_road:
            return False  # 不在道路上

        # 檢查交通號誌
        nearby_intersections = self.get_intersections_near(target_position, 50)
        for intersection in nearby_intersections:
            if intersection.has_traffic_light:
                # 簡化的方向判斷
                approach_direction = self._get_approach_direction(vehicle, intersection)
                if not intersection.can_vehicle_pass(approach_direction):
                    return False

        return True

    def _get_approach_direction(self, vehicle, intersection):
        """
        獲取載具接近路口的方向\n
        \n
        參數:\n
        vehicle (Vehicle): 載具\n
        intersection (Intersection): 路口\n
        \n
        回傳:\n
        str: 接近方向\n
        """
        vx, vy = vehicle.x, vehicle.y
        ix, iy = intersection.position

        dx = vx - ix
        dy = vy - iy

        # 根據相對位置判斷方向
        if abs(dx) > abs(dy):
            return "west" if dx < 0 else "east"
        else:
            return "north" if dy < 0 else "south"

    def draw_road_network(self, screen):
        """
        繪製整個道路網絡\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 先繪製道路段落
        for road in self.road_segments:
            road.draw(screen)

        # 再繪製路口（覆蓋在道路上）
        for intersection in self.intersections:
            intersection.draw(screen)

    def draw_debug_info(self, screen, font):
        """
        繪製除錯資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體\n
        """
        y_offset = 160

        # 顯示道路統計
        road_text = font.render(
            f"道路段數: {len(self.road_segments)}", True, (255, 255, 255)
        )
        screen.blit(road_text, (10, y_offset))

        intersection_text = font.render(
            f"路口數: {len(self.intersections)}", True, (255, 255, 255)
        )
        screen.blit(intersection_text, (10, y_offset + 20))

        # 顯示交通號誌狀態
        active_lights = sum(1 for i in self.intersections if i.has_traffic_light)
        light_text = font.render(f"交通號誌: {active_lights}", True, (255, 255, 255))
        screen.blit(light_text, (10, y_offset + 40))
