######################載入套件######################
import pygame
import random
import math
from src.systems.npc.npc import NPC
from src.systems.npc.profession import Profession, ProfessionData
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


######################NPC 管理器######################
class NPCManager:
    """
    NPC 管理器 - 統一管理所有 NPC 的創建、更新和行為\n
    \n
    負責 NPC 系統的全面管理，包括：\n
    1. 根據規格書要求生成 330 個小鎮 NPC 和 100 個部落 NPC\n
    2. 職業分配和工作場所指派\n
    3. 電力系統的區域分配\n
    4. NPC 的集體行為更新和渲染\n
    5. NPC 與玩家的互動管理\n
    \n
    設計重點:\n
    - 效能優化：分區管理，只更新視野範圍內的 NPC\n
    - 智能分配：確保各職業人數符合規格要求\n
    - 生活軌跡：每個 NPC 都有合理的日常作息\n
    """

    def __init__(self, time_manager=None):
        """
        初始化 NPC 管理器\n
        \n
        參數:\n
        time_manager (TimeManager): 時間管理器實例，用於獲取當前時間和星期資訊\n
        """
        # NPC 容器
        self.town_npcs = []  # 小鎮 NPC (330個)
        self.tribe_npcs = []  # 森林部落 NPC (100個)
        self.all_npcs = []  # 所有 NPC 的統一列表

        # 職業分配統計
        self.profession_assignments = {profession: 0 for profession in Profession}

        # 電力系統管理
        self.power_areas = []  # 30個電力區域
        self.power_workers = []  # 30個電力工人

        # 建築物和工作場所
        self.workplaces = {
            "教堂": [],
            "醫院": [],
            "槍械店": [],
            "便利商店": [],
            "釣魚店": [],
            "農田": [],
            "電力場": None,
            "森林部落": None,
        }

        # 時間系統整合
        self.time_manager = time_manager

        # 渲染優化
        self.render_distance = 300  # 只渲染這個距離內的 NPC
        self.update_distance = 500  # 只更新這個距離內的 NPC

        print("NPC 管理器初始化完成")

    def initialize_npcs(self, town_bounds, forest_bounds):
        """
        初始化所有 NPC\n
        \n
        根據規格書要求創建所有 NPC 並分配職業\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界 (x, y, width, height)\n
        forest_bounds (tuple): 森林邊界 (x, y, width, height)\n
        """
        print("開始創建 NPC...")
        # 初始化電力區域
        self._initialize_power_areas(town_bounds)

        # 創建小鎮 NPC
        self._create_town_npcs(town_bounds)

        # 創建森林部落 NPC
        self._create_tribe_npcs(forest_bounds)

        # 合併所有 NPC
        self.all_npcs = self.town_npcs + self.tribe_npcs

        # 分配工作場所
        self._assign_workplaces()

        # 分配住所
        self._assign_homes(town_bounds, forest_bounds)

        # 驗證職業分配
        self._verify_profession_distribution()

        print(
            f"NPC 創建完成: 小鎮 {len(self.town_npcs)} 個, 部落 {len(self.tribe_npcs)} 個, 總計 {len(self.all_npcs)} 個"
        )

    def set_buildings_reference(self, buildings):
        """
        為所有 NPC 設定建築物參考，用於碰撞檢測\n
        \n
        參數:\n
        buildings (list): 建築物列表\n
        """
        for npc in self.all_npcs:
            npc.set_buildings_reference(buildings)
        print(f"已為 {len(self.all_npcs)} 個 NPC 設定建築物碰撞檢測")

    def set_road_system_reference(self, road_system):
        """
        為所有 NPC 設定道路系統參考，用於智能路徑規劃\n
        \n
        參數:\n
        road_system (RoadSystem): 道路系統實例\n
        """
        for npc in self.all_npcs:
            npc.road_system = road_system
        print(f"已為 {len(self.all_npcs)} 個 NPC 設定道路系統路徑規劃")

    def _initialize_power_areas(self, town_bounds):
        """
        初始化 30 個電力區域\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界 (x, y, width, height)\n
        """
        town_x, town_y, town_width, town_height = town_bounds

        # 將小鎮劃分為 6x5 的網格 (30個區域)
        area_width = town_width // 6
        area_height = town_height // 5

        for row in range(5):
            for col in range(6):
                area_center_x = town_x + col * area_width + area_width // 2
                area_center_y = town_y + row * area_height + area_height // 2

                area_info = {
                    "id": row * 6 + col + 1,
                    "center": (area_center_x, area_center_y),
                    "bounds": (
                        col * area_width + town_x,
                        row * area_height + town_y,
                        area_width,
                        area_height,
                    ),
                    "assigned_worker": None,
                    "has_power": True,
                }

                self.power_areas.append(area_info)

        print(f"創建了 {len(self.power_areas)} 個電力區域")

    def _create_town_npcs(self, town_bounds):
        """
        創建小鎮 NPC\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界\n
        """
        town_x, town_y, town_width, town_height = town_bounds

        # 生成職業分配列表 (不包含部落成員)
        town_professions = []
        for profession, count in ProfessionData.PROFESSION_COUNTS.items():
            if profession != Profession.TRIBE_MEMBER:
                town_professions.extend([profession] * count)

        # 隨機打亂職業順序
        random.shuffle(town_professions)

        # 創建 NPC
        for profession in town_professions:
            # 在小鎮範圍內隨機位置創建 NPC，避開建築物
            position = self._find_safe_spawn_position(town_bounds)

            npc = NPC(profession, position)
            self.town_npcs.append(npc)

            # 更新職業統計
            self.profession_assignments[profession] += 1

            # 特殊處理電力工人
            if profession == Profession.POWER_WORKER:
                self._assign_power_area_to_worker(npc)

    def _find_safe_spawn_position(self, town_bounds, max_attempts=50):
        """
        尋找安全的生成位置，避開建築物\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界\n
        max_attempts (int): 最大嘗試次數\n
        \n
        回傳:\n
        tuple: 安全的位置座標 (x, y)\n
        """
        town_x, town_y, town_width, town_height = town_bounds

        for attempt in range(max_attempts):
            # 在小鎮範圍內隨機選擇位置
            x = random.randint(town_x + 50, town_x + town_width - 50)
            y = random.randint(town_y + 50, town_y + town_height - 50)

            # 檢查該位置是否與建築物重疊
            if hasattr(self, "buildings") and self.buildings:
                # 建立測試矩形
                test_rect = pygame.Rect(x - 15, y - 15, 30, 30)  # NPC 大小約 30x30

                # 檢查是否與任何建築物重疊
                safe_position = True
                for building in self.buildings:
                    if test_rect.colliderect(building["area"]):
                        safe_position = False
                        break

                if safe_position:
                    return (x, y)
            else:
                # 如果還沒有建築物列表，直接返回隨機位置
                return (x, y)

        # 如果找不到安全位置，返回邊界內的隨機位置
        print("警告：找不到安全的 NPC 生成位置，使用隨機位置")
        return (
            random.randint(town_x + 50, town_x + town_width - 50),
            random.randint(town_y + 50, town_y + town_height - 50),
        )

    def _create_tribe_npcs(self, forest_bounds):
        """
        創建森林部落 NPC\n
        \n
        參數:\n
        forest_bounds (tuple): 森林邊界\n
        """
        forest_x, forest_y, forest_width, forest_height = forest_bounds

        # 部落位置 (森林中的一個區域)
        tribe_center_x = forest_x + forest_width // 2
        tribe_center_y = forest_y + forest_height // 2
        tribe_radius = 150

        # 創建 100 個部落成員
        for i in range(ProfessionData.get_profession_count(Profession.TRIBE_MEMBER)):
            # 在部落區域內隨機位置
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, tribe_radius)

            x = tribe_center_x + distance * math.cos(angle)
            y = tribe_center_y + distance * math.sin(angle)

            npc = NPC(Profession.TRIBE_MEMBER, (x, y))
            self.tribe_npcs.append(npc)

            # 更新職業統計
            self.profession_assignments[Profession.TRIBE_MEMBER] += 1

    def _assign_power_area_to_worker(self, power_worker):
        """
        為電力工人分配負責區域\n
        \n
        參數:\n
        power_worker (NPC): 電力工人 NPC\n
        """
        # 找到還沒有分配工人的區域
        for area in self.power_areas:
            if area["assigned_worker"] is None:
                area["assigned_worker"] = power_worker
                power_worker.assign_area(area["center"])
                self.power_workers.append(power_worker)
                break

    def _assign_workplaces(self):
        """
        為所有 NPC 分配工作場所\n
        """
        # 這裡需要根據建築物系統的完成情況來實作
        # 暫時使用隨機位置作為工作場所

        for npc in self.town_npcs:
            workplace_names = ProfessionData.get_profession_workplaces(npc.profession)

            if workplace_names:
                # 為現在先用隨機位置，之後會根據實際建築物位置調整
                workplace_x = random.randint(100, 900)
                workplace_y = random.randint(100, 600)
                npc.set_workplace((workplace_x, workplace_y))

    def _assign_homes(self, town_bounds, forest_bounds):
        """
        為所有 NPC 分配住所\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界\n
        forest_bounds (tuple): 森林邊界\n
        """
        town_x, town_y, town_width, town_height = town_bounds

        # 小鎮 NPC 的住所在小鎮內
        for npc in self.town_npcs:
            home_x = random.randint(town_x + 30, town_x + town_width - 30)
            home_y = random.randint(town_y + 30, town_y + town_height - 30)
            npc.set_home((home_x, home_y))

        # 部落 NPC 的住所在部落內
        forest_x, forest_y, forest_width, forest_height = forest_bounds
        tribe_center_x = forest_x + forest_width // 2
        tribe_center_y = forest_y + forest_height // 2

        for npc in self.tribe_npcs:
            # 部落成員住所在部落中心附近
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(20, 100)

            home_x = tribe_center_x + distance * math.cos(angle)
            home_y = tribe_center_y + distance * math.sin(angle)
            npc.set_home((home_x, home_y))

    def _verify_profession_distribution(self):
        """
        驗證職業分配是否符合規格要求\n
        """
        print("職業分配驗證:")

        for profession in Profession:
            expected = ProfessionData.get_profession_count(profession)
            actual = self.profession_assignments[profession]

            status = "✓" if expected == actual else "✗"
            print(f"  {status} {profession.value}: {actual}/{expected}")

            if expected != actual:
                print(f"    警告: {profession.value} 數量不符合規格要求！")

    def update_optimized(self, dt, player_position):
        """
        優化的 NPC 更新方法 - 顯著提升效能\n
        \n
        使用分時更新和距離優化，減少每幀的計算負擔\n
        只更新視野範圍內的 NPC，其他 NPC 使用簡化更新\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置\n
        """
        # 獲取當前時間資訊
        current_hour = 8
        current_day = 1
        is_workday = True

        if self.time_manager:
            current_hour = self.time_manager.hour
            day_mapping = {
                "monday": 1,
                "tuesday": 2,
                "wednesday": 3,
                "thursday": 4,
                "friday": 5,
                "saturday": 6,
                "sunday": 7,
            }
            current_day = day_mapping.get(self.time_manager.day_of_week.value, 1)
            is_workday = self.time_manager.is_work_day

        # 使用分層更新策略
        # 第一層：附近的 NPC 完整更新（高頻率）
        nearby_distance = 300
        nearby_npcs = self.get_nearby_npcs(player_position, nearby_distance)

        for npc in nearby_npcs:
            npc.update(dt, current_hour, current_day, is_workday)

        # 第二層：中距離的 NPC 簡化更新（中頻率）
        frame_count = int(pygame.time.get_ticks() / 16.67)
        if frame_count % 3 == 0:  # 每3幀更新一次
            medium_distance = 600
            medium_npcs = self.get_nearby_npcs(player_position, medium_distance)

            for npc in medium_npcs:
                if npc not in nearby_npcs:  # 避免重複更新
                    npc.simple_update(dt, current_hour, is_workday)

        # 第三層：遠距離的 NPC 最簡化更新（低頻率）
        if frame_count % 10 == 0:  # 每10幀更新一次
            for npc in self.all_npcs:
                if (
                    npc not in nearby_npcs
                    and self._calculate_distance_fast(
                        npc.get_position(), player_position
                    )
                    > 600
                ):
                    npc.minimal_update(current_hour, is_workday)

        # 電力系統更新（低頻率）
        if frame_count % 5 == 0:
            self._update_power_system()

    def get_nearby_npcs(self, center_position, max_distance):
        """
        獲取指定範圍內的 NPC - 使用快速距離計算\n
        \n
        參數:\n
        center_position (tuple): 中心位置\n
        max_distance (float): 最大距離\n
        \n
        回傳:\n
        list: 範圍內的 NPC 列表\n
        """
        center_x, center_y = center_position
        npcs_in_range = []
        max_distance_squared = max_distance * max_distance  # 避免平方根計算

        for npc in self.all_npcs:
            if npc.is_injured:
                continue  # 住院的 NPC 不需要更新位置

            npc_x, npc_y = npc.get_position()
            # 使用平方距離比較，避免平方根計算
            distance_squared = (npc_x - center_x) ** 2 + (npc_y - center_y) ** 2

            if distance_squared <= max_distance_squared:
                npcs_in_range.append(npc)

        return npcs_in_range

    def _calculate_distance_fast(self, pos1, pos2):
        """
        快速距離計算 - 使用曼哈頓距離\n
        \n
        參數:\n
        pos1 (tuple): 位置1\n
        pos2 (tuple): 位置2\n
        \n
        回傳:\n
        float: 曼哈頓距離\n
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def update(self, dt, player_position):
        """
        更新所有 NPC - 保留原有方法以維持兼容性\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player_position (tuple): 玩家位置 (用於優化更新範圍)\n
        """
        # 獲取當前時間資訊
        current_hour = 8  # 預設值
        current_day = 1  # 預設值
        is_workday = True  # 預設值

        if self.time_manager:
            current_hour = self.time_manager.hour
            # 將 DayOfWeek enum 轉換為數字 (1-7)
            day_mapping = {
                "monday": 1,
                "tuesday": 2,
                "wednesday": 3,
                "thursday": 4,
                "friday": 5,
                "saturday": 6,
                "sunday": 7,
            }
            current_day = day_mapping.get(self.time_manager.day_of_week.value, 1)
            is_workday = self.time_manager.is_work_day

        # 根據玩家位置決定更新哪些 NPC (效能優化)
        npcs_to_update = self._get_npcs_in_range(player_position, self.update_distance)

        # 更新 NPC，傳遞時間和星期資訊
        for npc in npcs_to_update:
            npc.update(dt, current_hour, current_day, is_workday)

        # 更新電力系統
        self._update_power_system()

    def _update_power_system(self):
        """
        更新電力系統狀態\n
        """
        for area in self.power_areas:
            worker = area["assigned_worker"]

            if worker and worker.is_injured:
                # 如果負責的電力工人住院，該區域停電
                area["has_power"] = False
            else:
                # 電力工人正常工作，區域有電
                area["has_power"] = True

    def _get_npcs_in_range(self, center_position, max_distance):
        """
        獲取指定範圍內的 NPC\n
        \n
        參數:\n
        center_position (tuple): 中心位置\n
        max_distance (float): 最大距離\n
        \n
        回傳:\n
        list: 範圍內的 NPC 列表\n
        """
        center_x, center_y = center_position
        npcs_in_range = []

        for npc in self.all_npcs:
            if npc.is_injured:
                continue  # 住院的 NPC 不需要更新位置

            npc_x, npc_y = npc.get_position()
            distance = math.sqrt((npc_x - center_x) ** 2 + (npc_y - center_y) ** 2)

            if distance <= max_distance:
                npcs_in_range.append(npc)

        return npcs_in_range

    def draw(self, screen, camera_position, show_info=False):
        """
        繪製 NPC\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_position (tuple): 攝影機位置 (camera_x, camera_y)\n
        show_info (bool): 是否顯示 NPC 資訊\n
        """
        # camera_position 現在直接是 (camera_x, camera_y)
        camera_x, camera_y = camera_position

        # 計算攝影機中心點用於範圍檢測
        camera_center_x = camera_x + SCREEN_WIDTH // 2
        camera_center_y = camera_y + SCREEN_HEIGHT // 2

        # 獲取需要渲染的 NPC
        npcs_to_render = self._get_npcs_in_range(
            (camera_center_x, camera_center_y), self.render_distance
        )

        # 繪製 NPC
        for npc in npcs_to_render:
            npc.draw(screen, camera_x, camera_y)

        # 繪製 NPC 資訊 (可選)
        if show_info:
            font = pygame.font.Font(None, 16)
            for npc in npcs_to_render:
                npc.draw_info(screen, font, camera_x, camera_y)

    def get_npc_status_list(self, player_position=None, max_distance=500):
        """
        獲取 NPC 狀態清單用於顯示\n
        \n
        參數:\n
        player_position (tuple): 玩家位置，用於距離篩選\n
        max_distance (float): 最大顯示距離\n
        \n
        回傳:\n
        list: NPC 狀態資訊清單\n
        """
        if player_position:
            # 獲取玩家附近的 NPC
            nearby_npcs = self._get_npcs_in_range(player_position, max_distance)
        else:
            # 顯示所有 NPC
            nearby_npcs = self.all_npcs

        # 獲取每個 NPC 的狀態資訊
        npc_status_list = []
        for npc in nearby_npcs:
            status_info = npc.get_status_info()
            # 計算與玩家的距離
            if player_position:
                distance = math.sqrt(
                    (npc.x - player_position[0]) ** 2
                    + (npc.y - player_position[1]) ** 2
                )
                status_info["distance"] = int(distance)
            npc_status_list.append(status_info)

        # 按距離排序（近的在前面）
        if player_position:
            npc_status_list.sort(key=lambda x: x["distance"])
        else:
            # 按姓名排序
            npc_status_list.sort(key=lambda x: x["name"])

        return npc_status_list

    def draw_power_grid_status(self, screen, font):
        """
        繪製電力系統狀態\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體物件\n
        """
        y_offset = 10

        # 顯示總體電力狀態
        powered_areas = sum(1 for area in self.power_areas if area["has_power"])
        total_areas = len(self.power_areas)

        power_text = f"電力狀況: {powered_areas}/{total_areas} 區域有電"
        power_color = (0, 255, 0) if powered_areas == total_areas else (255, 255, 0)

        if powered_areas < total_areas * 0.8:  # 少於80%區域有電時顯示紅色
            power_color = (255, 0, 0)

        power_surface = font.render(power_text, True, power_color)
        screen.blit(
            power_surface,
            (screen.get_width() - power_surface.get_width() - 10, y_offset),
        )

        # 顯示住院的電力工人數量
        injured_power_workers = sum(
            1 for worker in self.power_workers if worker.is_injured
        )
        if injured_power_workers > 0:
            injured_text = f"住院電力工人: {injured_power_workers} 人"
            injured_surface = font.render(injured_text, True, (255, 0, 0))
            screen.blit(
                injured_surface,
                (screen.get_width() - injured_surface.get_width() - 10, y_offset + 25),
            )

    def get_npc_at_position(self, position, max_distance=50):
        """
        獲取指定位置附近的 NPC\n
        \n
        參數:\n
        position (tuple): 查詢位置\n
        max_distance (float): 最大距離\n
        \n
        回傳:\n
        NPC: 最近的 NPC，如果沒有則返回 None\n
        """
        closest_npc = None
        closest_distance = float("inf")

        x, y = position

        for npc in self.all_npcs:
            if npc.is_injured:
                continue

            npc_x, npc_y = npc.get_position()
            distance = math.sqrt((npc_x - x) ** 2 + (npc_y - y) ** 2)

            if distance <= max_distance and distance < closest_distance:
                closest_distance = distance
                closest_npc = npc

        return closest_npc

    def interact_with_npc(self, npc):
        """
        與 NPC 互動\n
        \n
        參數:\n
        npc (NPC): 要互動的 NPC\n
        \n
        回傳:\n
        str: 對話內容\n
        """
        if npc:
            dialogue = npc.get_dialogue()
            print(f"{npc.name}: {dialogue}")
            return dialogue
        return None

    def injure_random_npc(self, cause="意外"):
        """
        隨機讓一個 NPC 受傷 (用於測試)\n
        \n
        參數:\n
        cause (str): 受傷原因\n
        """
        available_npcs = [npc for npc in self.all_npcs if not npc.is_injured]
        if available_npcs:
            npc = random.choice(available_npcs)
            npc.injure(cause)
            return npc
        return None

    def get_statistics(self):
        """
        獲取 NPC 系統統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊\n
        """
        stats = {
            "total_npcs": len(self.all_npcs),
            "town_npcs": len(self.town_npcs),
            "tribe_npcs": len(self.tribe_npcs),
            "injured_npcs": sum(1 for npc in self.all_npcs if npc.is_injured),
            "working_npcs": sum(
                1 for npc in self.all_npcs if npc.state.value == "工作中"
            ),
            "powered_areas": sum(1 for area in self.power_areas if area["has_power"]),
            "total_areas": len(self.power_areas),
            "current_hour": int(self.time_manager.hour) if self.time_manager else 8,
            "profession_counts": self.profession_assignments.copy(),
        }

        return stats

    def get_power_workers(self):
        """
        取得所有電力系統員工 NPC\n
        \n
        回傳:\n
        List[NPC]: 電力工人 NPC 列表\n
        """
        from .profession import Profession

        power_workers = [
            npc
            for npc in self.all_npcs
            if hasattr(npc, "profession") and npc.profession == Profession.POWER_WORKER
        ]

        return power_workers

    def get_all_npcs(self):
        """
        取得所有 NPC\n
        \n
        回傳:\n
        List[NPC]: 所有 NPC 列表\n
        """
        return self.all_npcs
