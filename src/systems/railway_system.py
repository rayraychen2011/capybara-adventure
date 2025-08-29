######################載入套件######################
import pygame
import random
import math
from config.settings import *
from src.utils.helpers import calculate_distance

######################物件類別######################
class TrainStation:
    """
    火車站建築物 - 提供快速旅行功能\n
    \n
    此類別負責：\n
    1. 火車站建築的渲染和管理\n
    2. 玩家互動處理（點擊選擇目的地）\n
    3. 快速旅行功能實現\n
    """
    
    def __init__(self, position, size, station_id, name):
        """
        初始化火車站\n
        \n
        參數:\n
        position (tuple): 火車站位置 (x, y)\n
        size (tuple): 火車站尺寸 (width, height)\n
        station_id (int): 火車站唯一ID\n
        name (str): 火車站名稱\n
        """
        self.x, self.y = position
        self.width, self.height = size
        self.station_id = station_id
        self.name = name
        self.color = TRAIN_STATION_COLOR
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # 月台設定
        self.platform_width = self.width
        self.platform_height = 10
        self.platform_rect = pygame.Rect(
            self.x, 
            self.y + self.height - self.platform_height,
            self.platform_width, 
            self.platform_height
        )
        
        # 互動區域（比建築稍大）
        self.interaction_rect = pygame.Rect(
            self.x - 20, self.y - 20,
            self.width + 40, self.height + 40
        )
        
        print(f"火車站 {self.name} 建立於位置 ({self.x}, {self.y})")

    def can_interact(self, player_position):
        """
        檢查玩家是否可以與火車站互動\n
        \n
        參數:\n
        player_position (tuple): 玩家位置 (x, y)\n
        \n
        回傳:\n
        bool: 如果可以互動則回傳True\n
        """
        px, py = player_position
        return self.interaction_rect.collidepoint(px, py)

    def draw(self, screen, camera_x, camera_y, font_manager):
        """
        繪製火車站\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        font_manager: 字體管理器\n
        """
        # 計算螢幕座標
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # 繪製火車站主建築
        station_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, self.color, station_rect)
        pygame.draw.rect(screen, (0, 0, 0), station_rect, 2)
        
        # 繪製月台
        platform_screen_rect = pygame.Rect(
            screen_x, 
            screen_y + self.height - self.platform_height,
            self.platform_width, 
            self.platform_height
        )
        pygame.draw.rect(screen, (100, 100, 100), platform_screen_rect)
        pygame.draw.rect(screen, (0, 0, 0), platform_screen_rect, 1)
        
        # 繪製火車站名稱（如果建築夠大）
        if self.width > 40 and self.height > 20:
            try:
                text_surface = font_manager.render_text(self.name, 14, (255, 255, 255))
                text_rect = text_surface.get_rect(center=station_rect.center)
                screen.blit(text_surface, text_rect)
            except:
                # 字體渲染失敗時使用預設字體
                font = pygame.font.Font(None, 14)
                text_surface = font.render(self.name, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=station_rect.center)
                screen.blit(text_surface, text_rect)

class Train:
    """
    火車物件 - 在鐵軌上移動的交通工具\n
    \n
    此類別負責：\n
    1. 火車的移動和動畫\n
    2. 火車在鐵軌上的路徑規劃\n
    3. 火車與交通號誌的互動\n
    """
    
    def __init__(self, position, route_points):
        """
        初始化火車\n
        \n
        參數:\n
        position (tuple): 火車起始位置 (x, y)\n
        route_points (list): 火車行駛路線點列表\n
        """
        self.x, self.y = position
        self.width = 24
        self.height = 12
        self.color = TRAIN_COLOR
        self.speed = TRAIN_SPEED / 60  # 轉換為每幀像素數
        
        # 路線相關
        self.route_points = route_points
        self.current_target_index = 0
        self.direction = 0  # 火車方向（角度）
        
        # 移動狀態
        self.is_moving = True
        self.wait_time = 0
        self.max_wait_time = 180  # 在車站停留3秒（60fps）
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt):
        """
        更新火車狀態\n
        \n
        參數:\n
        dt (float): 時間增量\n
        """
        if not self.route_points:
            return
        
        if self.is_moving:
            self._move_towards_target()
        else:
            # 在車站等待
            self.wait_time += 1
            if self.wait_time >= self.max_wait_time:
                self.is_moving = True
                self.wait_time = 0

    def _move_towards_target(self):
        """
        朝向目標點移動 - 支持平滑轉彎\n
        """
        if self.current_target_index >= len(self.route_points):
            self.current_target_index = 0  # 循環路線
        
        target_x, target_y = self.route_points[self.current_target_index]
        
        # 計算到目標的距離和方向
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.speed * 2:  # 提前準備轉向
            # 到達目標點附近，開始轉向下一個目標
            self.current_target_index = (self.current_target_index + 1) % len(self.route_points)
            
            # 如果是最後一個點，在車站停留
            if self.current_target_index == 0:
                self.is_moving = False
        else:
            # 計算移動方向
            move_x = (dx / distance) * self.speed
            move_y = (dy / distance) * self.speed
            
            # 添加轉彎平滑度 - 考慮下一個目標點
            if len(self.route_points) > 1:
                next_target_index = (self.current_target_index + 1) % len(self.route_points)
                next_target_x, next_target_y = self.route_points[next_target_index]
                
                # 計算轉彎預測
                if distance < 30:  # 接近目標時開始考慮轉彎
                    next_dx = next_target_x - target_x
                    next_dy = next_target_y - target_y
                    
                    # 平滑轉彎：混合當前方向和下一個方向
                    blend_factor = max(0, (30 - distance) / 30)  # 距離越近，轉彎影響越大
                    
                    move_x = move_x * (1 - blend_factor) + (next_dx / (math.sqrt(next_dx*next_dx + next_dy*next_dy) if next_dx*next_dx + next_dy*next_dy > 0 else 1)) * self.speed * blend_factor
                    move_y = move_y * (1 - blend_factor) + (next_dy / (math.sqrt(next_dx*next_dx + next_dy*next_dy) if next_dx*next_dx + next_dy*next_dy > 0 else 1)) * self.speed * blend_factor
            
            # 應用移動
            self.x += move_x
            self.y += move_y
            
            # 更新方向（用於視覺效果）
            self.direction = math.atan2(move_y, move_x)
        
        # 更新碰撞矩形
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen, camera_x, camera_y):
        """
        繪製火車 - 根據方向旋轉顯示\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # 繪製火車車身
        train_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, self.color, train_rect)
        pygame.draw.rect(screen, (0, 0, 0), train_rect, 1)
        
        # 根據移動方向繪製火車頭
        front_size = 4
        direction_x = math.cos(self.direction)
        direction_y = math.sin(self.direction)
        
        # 火車頭位置（在移動方向的前端）
        front_x = screen_x + self.width // 2 + direction_x * (self.width // 3)
        front_y = screen_y + self.height // 2 + direction_y * (self.height // 3)
        
        # 繪製火車頭（黃色，表示前進方向）
        pygame.draw.circle(screen, (255, 255, 0), (int(front_x), int(front_y)), front_size)
        
        # 繪製車身細節（窗戶）
        window_color = (135, 206, 235)  # 天空藍
        window_size = 2
        
        # 側面窗戶
        for i in range(0, self.width - 4, 6):
            window_x = screen_x + 2 + i
            window_y = screen_y + self.height // 2 - 1
            pygame.draw.rect(screen, window_color, 
                           pygame.Rect(window_x, window_y, window_size, window_size))
        
        # 如果火車停止，顯示停車標示
        if not self.is_moving:
            stop_color = (255, 0, 0)  # 紅色
            pygame.draw.circle(screen, stop_color, 
                             (int(screen_x + self.width // 2), int(screen_y - 5)), 3)

class RailwaySystem:
    """
    鐵路系統管理器 - 管理所有火車站、火車和鐵軌\n
    \n
    此系統負責：\n
    1. 火車站的建立和管理\n
    2. 火車的生成和路線規劃\n
    3. 快速旅行功能實現\n
    4. 鐵軌渲染和交通號誌\n
    """
    
    def __init__(self):
        """
        初始化鐵路系統\n
        """
        self.train_stations = []
        self.trains = []
        self.railway_tracks = []  # 鐵軌路段
        self.traffic_signals = []  # 交通號誌
        
        # 快速旅行相關
        self.show_destination_menu = False
        self.selected_station = None
        self.destination_options = []
        
        print("鐵路系統初始化完成")

    def setup_stations_from_terrain(self, terrain_system):
        """
        根據地形系統建立火車站\n
        \n
        參數:\n
        terrain_system: 地形系統物件\n
        """
        print("從地形系統建立火車站...")
        
        station_count = 0
        
        # 尋找火車站地形（代碼11）
        for y in range(terrain_system.map_height):
            for x in range(terrain_system.map_width):
                if terrain_system.map_data[y][x] == 11:  # 火車站
                    # 計算火車站位置（2格填滿1個建築）
                    station_x = x * terrain_system.tile_size
                    station_y = y * terrain_system.tile_size
                    
                    # 火車站大小為2個地形格子
                    station_width = terrain_system.tile_size * 2
                    station_height = terrain_system.tile_size
                    
                    # 創建火車站
                    station_name = f"火車站{station_count + 1}"
                    station = TrainStation(
                        (station_x, station_y),
                        (station_width, station_height),
                        station_count,
                        station_name
                    )
                    
                    self.train_stations.append(station)
                    station_count += 1
        
        print(f"建立了 {station_count} 個火車站")
        
        # 建立火車路線
        if len(self.train_stations) >= 2:
            self._create_train_routes()

    def setup_railway_tracks_from_terrain(self, terrain_system):
        """
        根據地形系統建立鐵軌\n
        \n
        參數:\n
        terrain_system: 地形系統物件\n
        """
        print("從地形系統建立鐵軌...")
        
        track_count = 0
        
        # 尋找鐵軌地形（代碼10）
        for y in range(terrain_system.map_height):
            for x in range(terrain_system.map_width):
                if terrain_system.map_data[y][x] == 10:  # 鐵軌
                    # 計算鐵軌位置
                    track_x = x * terrain_system.tile_size
                    track_y = y * terrain_system.tile_size
                    track_width = terrain_system.tile_size
                    track_height = terrain_system.tile_size
                    
                    # 創建鐵軌路段
                    track = {
                        'position': (track_x, track_y),
                        'size': (track_width, track_height),
                        'rect': pygame.Rect(track_x, track_y, track_width, track_height),
                        'grid_pos': (x, y),
                        'has_crosswalk': True,  # 所有鐵軌都有斑馬線
                        'traffic_signal': None
                    }
                    
                    # 每隔一定距離放置交通號誌
                    if track_count % 5 == 0:  # 每5個鐵軌格子放一個號誌
                        signal = {
                            'position': (track_x + track_width//2, track_y),
                            'state': 'red' if random.random() < 0.5 else 'green',
                            'timer': random.randint(180, 360),  # 3-6秒切換
                            'rect': pygame.Rect(track_x + track_width//2 - 5, track_y - 10, 10, 10)
                        }
                        track['traffic_signal'] = signal
                        self.traffic_signals.append(signal)
                    
                    self.railway_tracks.append(track)
                    track_count += 1
        
        print(f"建立了 {track_count} 個鐵軌路段和 {len(self.traffic_signals)} 個交通號誌")

    def _create_train_routes(self):
        """
        創建火車路線 - 基於鐵軌連接創建智能路徑\n
        """
        if len(self.train_stations) < 2:
            return
        
        # 基於鐵軌創建路線 - 火車只能在鐵軌上移動
        route_points = self._build_railway_path()
        
        # 創建一輛火車
        if route_points:
            train = Train(route_points[0], route_points)
            self.trains.append(train)
            print(f"創建火車路線，連接 {len(route_points)} 個路點")

    def _build_railway_path(self):
        """
        基於鐵軌網絡構建火車行駛路徑\n
        火車只能在鐵軌上移動，支持轉彎\n
        \n
        回傳:\n
        list: 火車行駛路徑點列表\n
        """
        if not self.railway_tracks:
            return []
        
        # 構建鐵軌網絡圖
        track_graph = self._build_track_graph()
        
        # 找到所有火車站的位置
        station_positions = []
        for station in self.train_stations:
            # 找到最接近車站的鐵軌點
            closest_track = self._find_closest_track_to_station(station)
            if closest_track:
                station_positions.append(closest_track['center'])
        
        if len(station_positions) < 2:
            # 如果站點不足，創建簡單的環形路線
            return self._create_simple_track_route()
        
        # 創建連接所有車站的路線
        route_points = []
        for i, station_pos in enumerate(station_positions):
            route_points.append(station_pos)
            
            # 添加車站間的中間路點（沿著鐵軌）
            if i < len(station_positions) - 1:
                next_station_pos = station_positions[i + 1]
                intermediate_points = self._find_path_between_stations(
                    station_pos, next_station_pos, track_graph
                )
                route_points.extend(intermediate_points)
        
        # 閉合路線 - 從最後一個車站回到第一個車站
        if len(station_positions) > 2:
            final_path = self._find_path_between_stations(
                station_positions[-1], station_positions[0], track_graph
            )
            route_points.extend(final_path)
        
        return route_points

    def _build_track_graph(self):
        """
        構建鐵軌網絡圖，用於路徑規劃\n
        \n
        回傳:\n
        dict: 鐵軌網絡圖\n
        """
        graph = {}
        
        # 為每個鐵軌創建節點
        for i, track in enumerate(self.railway_tracks):
            tx, ty = track['position']
            tw, th = track['size']
            
            # 鐵軌中心點
            center = (tx + tw // 2, ty + th // 2)
            
            # 鐵軌的四個連接點（上下左右）
            connections = {
                'north': (center[0], ty),
                'south': (center[0], ty + th),
                'west': (tx, center[1]),
                'east': (tx + tw, center[1]),
                'center': center
            }
            
            track['center'] = center
            track['connections'] = connections
            graph[i] = track
        
        return graph

    def _find_closest_track_to_station(self, station):
        """
        找到最接近車站的鐵軌\n
        \n
        參數:\n
        station (TrainStation): 火車站\n
        \n
        回傳:\n
        dict: 最接近的鐵軌資訊\n
        """
        station_center = (station.x + station.width // 2, station.y + station.height // 2)
        closest_track = None
        min_distance = float('inf')
        
        for track in self.railway_tracks:
            tx, ty = track['position']
            tw, th = track['size']
            track_center = (tx + tw // 2, ty + th // 2)
            
            distance = math.sqrt(
                (station_center[0] - track_center[0]) ** 2 + 
                (station_center[1] - track_center[1]) ** 2
            )
            
            if distance < min_distance:
                min_distance = distance
                closest_track = track
                closest_track['center'] = track_center
        
        return closest_track

    def _find_path_between_stations(self, start_pos, end_pos, track_graph):
        """
        在兩個車站之間找到沿鐵軌的路徑\n
        \n
        參數:\n
        start_pos (tuple): 起始位置\n
        end_pos (tuple): 結束位置\n
        track_graph (dict): 鐵軌網絡圖\n
        \n
        回傳:\n
        list: 中間路徑點列表\n
        """
        # 簡化版：直接連接起終點間的鐵軌中心點
        intermediate_points = []
        
        # 找到起點和終點間的所有鐵軌
        tracks_in_path = []
        for track_id, track in track_graph.items():
            track_center = track.get('center', (0, 0))
            
            # 檢查這個鐵軌是否在起終點的路徑上
            if self._is_track_on_path(start_pos, end_pos, track_center):
                tracks_in_path.append((track_center, self._distance_to_line(start_pos, end_pos, track_center)))
        
        # 按距離起點的順序排序
        tracks_in_path.sort(key=lambda x: x[1])
        
        # 添加中間點
        for track_center, _ in tracks_in_path[:5]:  # 限制最多5個中間點
            if track_center != start_pos and track_center != end_pos:
                intermediate_points.append(track_center)
        
        return intermediate_points

    def _is_track_on_path(self, start_pos, end_pos, track_pos):
        """
        檢查鐵軌是否在起終點路徑附近\n
        \n
        參數:\n
        start_pos (tuple): 起始位置\n
        end_pos (tuple): 結束位置\n
        track_pos (tuple): 鐵軌位置\n
        \n
        回傳:\n
        bool: 是否在路徑上\n
        """
        # 計算點到線段的距離
        distance_to_path = self._distance_to_line(start_pos, end_pos, track_pos)
        return distance_to_path < 50  # 50像素容差

    def _distance_to_line(self, start_pos, end_pos, point):
        """
        計算點到線段的距離\n
        \n
        參數:\n
        start_pos (tuple): 線段起點\n
        end_pos (tuple): 線段終點\n
        point (tuple): 測試點\n
        \n
        回傳:\n
        float: 距離\n
        """
        x1, y1 = start_pos
        x2, y2 = end_pos
        x0, y0 = point
        
        # 線段長度
        line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if line_length == 0:
            return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
        
        # 計算投影參數
        t = max(0, min(1, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / (line_length ** 2)))
        
        # 計算最近點
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        # 返回距離
        return math.sqrt((x0 - proj_x) ** 2 + (y0 - proj_y) ** 2)

    def _create_simple_track_route(self):
        """
        創建簡單的鐵軌循環路線\n
        \n
        回傳:\n
        list: 路線點列表\n
        """
        if not self.railway_tracks:
            return []
        
        # 選擇前8個鐵軌作為路線（如果有的話）
        route_points = []
        for i, track in enumerate(self.railway_tracks[:8]):
            tx, ty = track['position']
            tw, th = track['size']
            center = (tx + tw // 2, ty + th // 2)
            route_points.append(center)
        
        return route_points

    def check_player_near_station(self, player_position):
        """
        檢查玩家是否在火車站附近 - 自動顯示傳送選項\n
        \n
        參數:\n
        player_position (tuple): 玩家位置 (x, y)\n
        \n
        回傳:\n
        TrainStation: 如果在車站附近則回傳車站物件，否則回傳None\n
        """
        px, py = player_position
        
        for station in self.train_stations:
            # 擴大互動範圍，讓玩家更容易觸發
            expanded_rect = pygame.Rect(
                station.x - 30, station.y - 30,
                station.width + 60, station.height + 60
            )
            
            if expanded_rect.collidepoint(px, py):
                # 如果還沒有顯示目的地選單，則自動顯示
                if not self.show_destination_menu:
                    self.selected_station = station
                    # 建立目的地選項（除了當前車站外的所有車站）
                    self.destination_options = [s for s in self.train_stations if s.station_id != station.station_id]
                    
                    if self.destination_options:
                        self.show_destination_menu = True
                        print(f"🚂 進入 {station.name} 傳送範圍，按數字鍵選擇目的地")
                        return station
                
                return station
        
        # 如果玩家離開所有車站範圍，關閉選單
        if self.show_destination_menu:
            self.show_destination_menu = False
            self.selected_station = None
            self.destination_options = []
            print("🚂 離開火車站範圍，關閉傳送選單")
        
        return None

    def handle_station_click(self, click_position, player):
        """
        處理火車站點擊事件\n
        \n
        參數:\n
        click_position (tuple): 點擊位置 (x, y)\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 如果處理了點擊事件則回傳True\n
        """
        for station in self.train_stations:
            if station.can_interact(click_position):
                self.selected_station = station
                # 建立目的地選項（除了當前車站外的所有車站）
                self.destination_options = [s for s in self.train_stations if s.station_id != station.station_id]
                
                if self.destination_options:
                    self.show_destination_menu = True
                    print(f"開啟 {station.name} 的目的地選擇畫面")
                    return True
                else:
                    print("沒有其他可前往的車站")
        
        return False

    def handle_destination_selection(self, selection_index, player):
        """
        處理目的地選擇\n
        \n
        參數:\n
        selection_index (int): 選擇的目的地索引（0-8對應數字鍵1-9）\n
        player: 玩家物件\n
        \n
        回傳:\n
        bool: 如果成功傳送則回傳True\n
        """
        if (0 <= selection_index < len(self.destination_options) and selection_index < 9):
            destination = self.destination_options[selection_index]
            
            # 傳送玩家到目的地車站
            new_x = destination.x + destination.width // 2
            new_y = destination.y + destination.height + 15  # 車站前方稍遠一點
            
            # 使用玩家的 set_position 方法確保正確更新位置
            if hasattr(player, 'set_position'):
                player.set_position(new_x - player.width//2, new_y - player.height//2)
            else:
                player.x = new_x
                player.y = new_y
                # 確保更新玩家的矩形位置
                if hasattr(player, 'rect'):
                    player.rect.x = int(new_x)
                    player.rect.y = int(new_y)
            
            print(f"🚂 快速旅行：從 {self.selected_station.name} 前往 {destination.name}")
            print(f"🚂 玩家已傳送到 ({new_x}, {new_y})")
            
            # 關閉選擇畫面
            self.show_destination_menu = False
            self.selected_station = None
            self.destination_options = []
            
            return True
        
        return False

    def close_destination_menu(self):
        """
        關閉目的地選擇畫面\n
        """
        self.show_destination_menu = False
        self.selected_station = None
        self.destination_options = []

    def update(self, dt):
        """
        更新鐵路系統\n
        \n
        參數:\n
        dt (float): 時間增量\n
        """
        # 更新所有火車
        for train in self.trains:
            train.update(dt)
        
        # 更新交通號誌
        for signal in self.traffic_signals:
            signal['timer'] -= 1
            if signal['timer'] <= 0:
                # 切換號誌狀態
                signal['state'] = 'green' if signal['state'] == 'red' else 'red'
                signal['timer'] = random.randint(180, 360)  # 重置計時器

    def can_cross_railway(self, position):
        """
        檢查指定位置是否可以穿越鐵軌（斑馬線通行）\n
        根據新需求：NPC 只能從斑馬線處通過鐵軌，其他位置不可穿越\n
        \n
        參數:\n
        position (tuple): 檢查位置 (x, y)\n
        \n
        回傳:\n
        bool: 如果可以通行則回傳True\n
        """
        px, py = position
        
        for track in self.railway_tracks:
            if track['rect'].collidepoint(px, py):
                # 檢查是否有斑馬線 - 根據新需求，所有鐵軌都有斑馬線
                if track['has_crosswalk']:
                    # 檢查交通號誌 - 只有綠燈時可以通行
                    if track['traffic_signal']:
                        return track['traffic_signal']['state'] == 'green'
                    else:
                        return True  # 沒有號誌則可以通行
                else:
                    # 根據新需求：沒有斑馬線的位置不能通行
                    return False
        
        return True  # 不在鐵軌上可以通行

    def check_railway_collision_for_npc(self, entity_rect):
        """
        檢查 NPC 是否與鐵軌發生碰撞（新增，專門用於 NPC）\n
        根據新需求：NPC 不能到沒有斑馬線的鐵軌上\n
        \n
        參數:\n
        entity_rect (pygame.Rect): 實體的碰撞矩形\n
        \n
        回傳:\n
        bool: 如果發生碰撞且不能通行則回傳True\n
        """
        for track in self.railway_tracks:
            if entity_rect.colliderect(track['rect']):
                # 如果有斑馬線且是綠燈，允許通行
                if track['has_crosswalk']:
                    if track['traffic_signal']:
                        if track['traffic_signal']['state'] == 'red':
                            return True  # 紅燈不能通行
                    # 有斑馬線且綠燈（或無號誌）可以通行
                    return False
                else:
                    # 沒有斑馬線不能通行
                    return True
        return False  # 不在鐵軌上

    def check_railway_collision(self, entity_rect):
        """
        檢查實體是否與鐵軌發生碰撞（NPC不能到鐵軌上）\n
        \n
        參數:\n
        entity_rect (pygame.Rect): 實體的碰撞矩形\n
        \n
        回傳:\n
        bool: 如果發生碰撞則回傳True\n
        """
        for track in self.railway_tracks:
            if entity_rect.colliderect(track['rect']):
                return True
        return False

    def draw_railway_tracks(self, screen, camera_x, camera_y):
        """
        繪製鐵軌\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        for track in self.railway_tracks:
            tx, ty = track['position']
            tw, th = track['size']
            
            # 檢查是否在可見範圍內
            if (tx + tw < camera_x or tx > camera_x + screen.get_width() or
                ty + th < camera_y or ty > camera_y + screen.get_height()):
                continue
            
            screen_x = tx - camera_x
            screen_y = ty - camera_y
            
            # 繪製鐵軌底色
            track_rect = pygame.Rect(screen_x, screen_y, tw, th)
            pygame.draw.rect(screen, RAILWAY_COLOR, track_rect)
            
            # 繪製鐵軌線條
            rail_y1 = screen_y + th // 3
            rail_y2 = screen_y + 2 * th // 3
            pygame.draw.line(screen, (80, 50, 20), 
                           (screen_x, rail_y1), (screen_x + tw, rail_y1), 3)
            pygame.draw.line(screen, (80, 50, 20), 
                           (screen_x, rail_y2), (screen_x + tw, rail_y2), 3)
            
            # 繪製枕木
            for i in range(0, tw, 8):
                tie_x = screen_x + i
                pygame.draw.line(screen, (101, 67, 33),
                               (tie_x, screen_y), (tie_x, screen_y + th), 2)
            
            # 繪製斑馬線
            if track['has_crosswalk']:
                stripe_width = 4
                for i in range(0, tw, stripe_width * 2):
                    stripe_rect = pygame.Rect(screen_x + i, screen_y, stripe_width, th)
                    pygame.draw.rect(screen, (255, 255, 255), stripe_rect)
            
            # 繪製交通號誌
            if track['traffic_signal']:
                signal = track['traffic_signal']
                signal_x = signal['position'][0] - camera_x
                signal_y = signal['position'][1] - camera_y
                
                # 號誌燈顏色
                light_color = (0, 255, 0) if signal['state'] == 'green' else (255, 0, 0)
                pygame.draw.circle(screen, light_color, (int(signal_x), int(signal_y)), 5)
                pygame.draw.circle(screen, (0, 0, 0), (int(signal_x), int(signal_y)), 5, 2)

    def draw_stations(self, screen, camera_x, camera_y, font_manager):
        """
        繪製所有火車站\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        font_manager: 字體管理器\n
        """
        for station in self.train_stations:
            # 檢查是否在可見範圍內
            if (station.x + station.width < camera_x or station.x > camera_x + screen.get_width() or
                station.y + station.height < camera_y or station.y > camera_y + screen.get_height()):
                continue
            
            station.draw(screen, camera_x, camera_y, font_manager)
            
            # 如果是選中的車站且顯示目的地選單，繪製特殊標示
            if (self.selected_station and station.station_id == self.selected_station.station_id 
                and self.show_destination_menu):
                
                screen_x = station.x - camera_x
                screen_y = station.y - camera_y
                
                # 繪製閃爍的邊框
                current_time = pygame.time.get_ticks()
                if (current_time // 300) % 2:  # 每0.3秒閃爍一次
                    highlight_rect = pygame.Rect(screen_x - 5, screen_y - 5, 
                                               station.width + 10, station.height + 10)
                    pygame.draw.rect(screen, (255, 255, 0), highlight_rect, 3)
                
                # 繪製互動提示
                try:
                    hint_text = font_manager.render_text("按數字鍵選擇目的地", 12, (255, 255, 0))
                except:
                    font = pygame.font.Font(None, 12)
                    hint_text = font.render("Press number keys", True, (255, 255, 0))
                
                hint_rect = hint_text.get_rect(center=(screen_x + station.width//2, screen_y - 15))
                
                # 繪製提示背景
                bg_rect = pygame.Rect(hint_rect.x - 5, hint_rect.y - 2, 
                                    hint_rect.width + 10, hint_rect.height + 4)
                pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
                pygame.draw.rect(screen, (255, 255, 0), bg_rect, 1)
                
                screen.blit(hint_text, hint_rect)

    def draw_trains(self, screen, camera_x, camera_y):
        """
        繪製所有火車\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        for train in self.trains:
            # 檢查是否在可見範圍內
            if (train.x + train.width < camera_x or train.x > camera_x + screen.get_width() or
                train.y + train.height < camera_y or train.y > camera_y + screen.get_height()):
                continue
            
            train.draw(screen, camera_x, camera_y)

    def draw_destination_menu(self, screen, font_manager):
        """
        繪製火車站螢幕式的目的地選擇畫面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font_manager: 字體管理器\n
        """
        if not self.show_destination_menu or not self.destination_options:
            return
        
        # 火車站螢幕樣式設計
        screen_width = 400
        screen_height = 60 + len(self.destination_options) * 45 + 60
        screen_x = (screen.get_width() - screen_width) // 2
        screen_y = (screen.get_height() - screen_height) // 2
        
        # 繪製螢幕外框（類似LCD顯示器）
        border_rect = pygame.Rect(screen_x - 10, screen_y - 10, screen_width + 20, screen_height + 20)
        pygame.draw.rect(screen, (30, 30, 30), border_rect)  # 深灰色外框
        pygame.draw.rect(screen, (100, 100, 100), border_rect, 3)  # 邊框
        
        # 繪製螢幕背景（深藍色，類似火車站資訊螢幕）
        screen_rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        pygame.draw.rect(screen, (0, 20, 50), screen_rect)  # 深藍色背景
        pygame.draw.rect(screen, (0, 100, 200), screen_rect, 2)  # 藍色邊框
        
        # 繪製螢幕標題欄
        title_height = 40
        title_rect = pygame.Rect(screen_x, screen_y, screen_width, title_height)
        pygame.draw.rect(screen, (0, 50, 100), title_rect)  # 標題背景
        
        # 繪製車站名稱和標題
        try:
            station_name = self.selected_station.name if self.selected_station else "火車站"
            title_text = font_manager.render_text(f"{station_name} - 目的地選擇", 18, (255, 255, 255))
        except:
            font = pygame.font.Font(None, 18)
            title_text = font.render("Train Station - Destinations", True, (255, 255, 255))
        
        title_text_rect = title_text.get_rect(center=(screen_x + screen_width//2, screen_y + title_height//2))
        screen.blit(title_text, title_text_rect)
        
        # 繪製閃爍的"現在發車"指示
        current_time = pygame.time.get_ticks()
        if (current_time // 500) % 2:  # 每0.5秒閃爍一次
            try:
                departure_text = font_manager.render_text("● 現在發車 ●", 14, (0, 255, 0))
            except:
                font = pygame.font.Font(None, 14)
                departure_text = font.render("● NOW DEPARTING ●", True, (0, 255, 0))
            
            departure_rect = departure_text.get_rect(center=(screen_x + screen_width//2, screen_y + title_height + 15))
            screen.blit(departure_text, departure_rect)
        
        # 繪製目的地選項（像火車時刻表）
        options_start_y = screen_y + title_height + 30
        
        for i, station in enumerate(self.destination_options):
            option_y = options_start_y + i * 45
            option_rect = pygame.Rect(screen_x + 15, option_y, screen_width - 30, 40)
            
            # 繪製選項背景（交替顏色，像真實的時刻表）
            bg_color = (0, 30, 70) if i % 2 == 0 else (0, 40, 80)
            pygame.draw.rect(screen, bg_color, option_rect)
            pygame.draw.rect(screen, (0, 150, 255), option_rect, 1)
            
            # 繪製路線編號
            try:
                number_text = font_manager.render_text(f"{i+1}", 20, (255, 255, 0))
            except:
                font = pygame.font.Font(None, 20)
                number_text = font.render(f"{i+1}", True, (255, 255, 0))
            
            number_rect = pygame.Rect(screen_x + 25, option_y + 5, 30, 30)
            pygame.draw.rect(screen, (100, 100, 0), number_rect)
            pygame.draw.rect(screen, (255, 255, 0), number_rect, 2)
            
            number_text_rect = number_text.get_rect(center=number_rect.center)
            screen.blit(number_text, number_text_rect)
            
            # 繪製目的地名稱
            try:
                dest_text = font_manager.render_text(station.name, 16, (255, 255, 255))
            except:
                font = pygame.font.Font(None, 16)
                dest_text = font.render(station.name, True, (255, 255, 255))
            
            dest_text_rect = dest_text.get_rect(left=screen_x + 70, centery=option_y + 20)
            screen.blit(dest_text, dest_text_rect)
            
            # 繪製"發車中"狀態
            try:
                status_text = font_manager.render_text("發車中", 12, (0, 255, 100))
            except:
                font = pygame.font.Font(None, 12)
                status_text = font.render("DEPARTING", True, (0, 255, 100))
            
            status_text_rect = status_text.get_rect(right=screen_x + screen_width - 25, centery=option_y + 20)
            screen.blit(status_text, status_text_rect)
        
        # 繪製底部操作說明
        instruction_y = screen_y + screen_height - 45
        instruction_rect = pygame.Rect(screen_x, instruction_y, screen_width, 45)
        pygame.draw.rect(screen, (0, 60, 120), instruction_rect)
        
        try:
            help_text = font_manager.render_text("按對應數字鍵選擇目的地", 14, (255, 255, 255))
            esc_text = font_manager.render_text("ESC: 取消", 12, (200, 200, 200))
        except:
            font = pygame.font.Font(None, 14)
            help_text = font.render("Press number key to select destination", True, (255, 255, 255))
            font2 = pygame.font.Font(None, 12)
            esc_text = font2.render("ESC: Cancel", True, (200, 200, 200))
        
        help_rect = help_text.get_rect(center=(screen_x + screen_width//2, instruction_y + 15))
        screen.blit(help_text, help_rect)
        
        esc_rect = esc_text.get_rect(center=(screen_x + screen_width//2, instruction_y + 35))
        screen.blit(esc_text, esc_rect)

    def get_statistics(self):
        """
        獲取鐵路系統統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊\n
        """
        return {
            'train_stations': len(self.train_stations),
            'trains': len(self.trains),
            'railway_tracks': len(self.railway_tracks),
            'traffic_signals': len(self.traffic_signals)
        }