######################載入套件######################
import pygame
import random
import math
from config.settings import *


######################建築類別######################
class Building:
    """
    建築基礎類別 - 表示遊戲中的各種建築物\n
    \n
    所有建築物的共同基礎，包含位置、尺寸、類型等基本屬性\n
    支援不同類型的建築，如商店、醫院、教堂等\n
    提供統一的互動介面和渲染系統\n
    """

    def __init__(self, building_type, position, size):
        """
        初始化建築\n
        \n
        參數:\n
        building_type (str): 建築類型\n
        position (tuple): 位置 (x, y)\n
        size (tuple): 尺寸 (width, height)\n
        """
        self.building_type = building_type
        self.x, self.y = position
        self.width, self.height = size
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # 根據建築類型設定屬性
        self._setup_building_properties()

        # 建築狀態
        self.is_open = True
        self.staff_count = 0
        self.customers = []
        self.services = []

        # 互動相關
        self.interaction_points = []
        self._create_interaction_points()

    def _setup_building_properties(self):
        """
        根據建築類型設定屬性\n
        """
        if self.building_type == "gun_shop":
            self.name = "槍械店"
            self.color = (139, 69, 19)  # 棕色
            self.services = ["買槍", "買彈藥", "武器升級"]
            self.staff_count = 2

        elif self.building_type == "hospital":
            self.name = "醫院"
            self.color = (255, 255, 255)  # 白色
            self.services = ["治療", "重生點"]
            self.staff_count = 10  # 1醫生 + 8護士 + 1管理員

        elif self.building_type == "convenience_store":
            self.name = "便利商店"
            self.color = (255, 215, 0)  # 金色
            self.services = ["買食物", "買日用品"]
            self.staff_count = 2

        elif self.building_type == "church":
            self.name = "教堂"
            self.color = (128, 0, 128)  # 紫色
            self.services = ["祈禱", "懺悔"]
            self.staff_count = 15  # 1牧師 + 14修女

        elif self.building_type == "fishing_shop":
            self.name = "釣魚店"
            self.color = (0, 191, 255)  # 藍色
            self.services = ["買釣具", "賣魚"]
            self.staff_count = 20

        elif self.building_type == "market":
            self.name = "市場"
            self.color = (255, 165, 0)  # 橘色
            self.services = ["買賣物品", "交易"]
            self.staff_count = 10

        elif self.building_type == "street_vendor":
            self.name = "路邊小販"
            self.color = (255, 192, 203)  # 粉色
            self.services = ["特色商品"]
            self.staff_count = 1

        elif self.building_type == "power_plant":
            self.name = "電力場"
            self.color = (255, 255, 0)  # 黃色
            self.services = ["電力供應"]
            self.staff_count = 30

        else:
            self.name = "建築物"
            self.color = BUILDING_COLOR
            self.services = []
            self.staff_count = 1

    def _create_interaction_points(self):
        """
        創建互動點\n
        """
        # 在建築物四周創建互動點
        # 正門 (下方中央)
        main_entrance = (self.x + self.width // 2, self.y + self.height + 10)
        self.interaction_points.append(
            {"name": "正門", "position": main_entrance, "type": "entrance"}
        )

    def can_interact(self, player_position, max_distance=50):
        """
        檢查玩家是否可以與建築互動\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        max_distance (float): 最大互動距離\n
        \n
        回傳:\n
        bool: 是否可以互動\n
        """
        px, py = player_position

        for interaction_point in self.interaction_points:
            ix, iy = interaction_point["position"]
            distance = math.sqrt((px - ix) ** 2 + (py - iy) ** 2)

            if distance <= max_distance:
                return True

        return False

    def interact(self, player):
        """
        與建築互動\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 互動結果\n
        """
        if not self.is_open:
            return {"success": False, "message": f"{self.name}已關閉"}

        return {
            "success": True,
            "building": self,
            "services": self.services,
            "message": f"歡迎來到{self.name}！",
        }

    def draw(self, screen):
        """
        繪製建築\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 繪製建築主體
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        # 繪製建築名稱
        font = pygame.font.Font(None, 20)
        text = font.render(self.name, True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

        # 繪製互動點
        for point in self.interaction_points:
            pygame.draw.circle(screen, (255, 255, 0), point["position"], 3)

    def draw_info(self, screen, font):
        """
        繪製建築資訊\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        font (pygame.font.Font): 字體\n
        """
        # 顯示服務列表
        y_offset = 10
        for service in self.services:
            service_text = font.render(f"- {service}", True, (255, 255, 255))
            screen.blit(service_text, (self.rect.right + 10, self.rect.top + y_offset))
            y_offset += 20


######################槍械店######################
class GunShop(Building):
    """
    槍械店 - 專門販售武器和彈藥\n
    \n
    提供各種武器的購買、升級和彈藥補給服務\n
    根據規格書要求，小鎮內外共有10座槍械店\n
    """

    def __init__(self, position, size=(120, 80)):
        """
        初始化槍械店\n
        \n
        參數:\n
        position (tuple): 位置 (x, y)\n
        size (tuple): 尺寸 (width, height)\n
        """
        super().__init__("gun_shop", position, size)

        # 槍械店庫存
        self.weapon_inventory = {
            "pistol": {"price": 500, "stock": 5, "name": "手槍"},
            "rifle": {"price": 1500, "stock": 3, "name": "步槍"},
            "shotgun": {"price": 800, "stock": 4, "name": "霰彈槍"},
            "sniper": {"price": 3000, "stock": 1, "name": "狙擊槍"},
        }

        self.ammo_inventory = {
            "9mm": {"price": 2, "stock": 1000, "name": "9mm子彈"},
            "7.62mm": {"price": 5, "stock": 500, "name": "7.62mm子彈"},
            "12gauge": {"price": 8, "stock": 200, "name": "12號霰彈"},
            ".308": {"price": 15, "stock": 100, "name": ".308子彈"},
        }

    def interact(self, player):
        """
        槍械店互動\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 互動結果\n
        """
        base_result = super().interact(player)
        if not base_result["success"]:
            return base_result

        # 顯示槍械店菜單
        print(f"\n=== {self.name} ===")
        print("1. 購買武器")
        print("2. 購買彈藥")
        print("3. 查看庫存")
        print("0. 離開")

        return base_result

    def buy_weapon(self, weapon_type, player):
        """
        購買武器\n
        \n
        參數:\n
        weapon_type (str): 武器類型\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 購買結果\n
        """
        if weapon_type not in self.weapon_inventory:
            return {"success": False, "message": "沒有這種武器"}

        weapon_info = self.weapon_inventory[weapon_type]

        if weapon_info["stock"] <= 0:
            return {"success": False, "message": f"{weapon_info['name']}已售完"}

        if player.get_money() < weapon_info["price"]:
            return {"success": False, "message": "金錢不足"}

        # 扣除金錢和庫存
        player.spend_money(weapon_info["price"])
        weapon_info["stock"] -= 1

        return {
            "success": True,
            "weapon_type": weapon_type,
            "message": f"購買了 {weapon_info['name']}！",
        }

    def buy_ammo(self, ammo_type, quantity, player):
        """
        購買彈藥\n
        \n
        參數:\n
        ammo_type (str): 彈藥類型\n
        quantity (int): 數量\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 購買結果\n
        """
        if ammo_type not in self.ammo_inventory:
            return {"success": False, "message": "沒有這種彈藥"}

        ammo_info = self.ammo_inventory[ammo_type]

        if ammo_info["stock"] < quantity:
            return {"success": False, "message": f"{ammo_info['name']}庫存不足"}

        total_cost = ammo_info["price"] * quantity
        if player.get_money() < total_cost:
            return {"success": False, "message": "金錢不足"}

        # 扣除金錢和庫存
        player.spend_money(total_cost)
        ammo_info["stock"] -= quantity

        return {
            "success": True,
            "ammo_type": ammo_type,
            "quantity": quantity,
            "message": f"購買了 {quantity} 發 {ammo_info['name']}！",
        }


######################醫院######################
class Hospital(Building):
    """
    醫院 - 治療和重生點\n
    \n
    玩家死亡後的重生地點\n
    提供治療服務和NPC住院功能\n
    根據規格書要求，共有5座醫院\n
    """

    def __init__(self, position, size=(150, 100)):
        """
        初始化醫院\n
        \n
        參數:\n
        position (tuple): 位置 (x, y)\n
        size (tuple): 尺寸 (width, height)\n
        """
        super().__init__("hospital", position, size)

        # 醫院設施
        self.beds = 20  # 病床數量
        self.patients = []  # 住院患者
        self.is_respawn_point = True

    def admit_patient(self, patient, cause="疾病"):
        """
        收治患者\n
        \n
        參數:\n
        patient (NPC): 患者\n
        cause (str): 住院原因\n
        \n
        回傳:\n
        bool: 是否成功收治\n
        """
        if len(self.patients) >= self.beds:
            return False

        patient_record = {
            "patient": patient,
            "admission_time": pygame.time.get_ticks(),
            "cause": cause,
            "treatment_duration": 24,  # 住院24小時 (遊戲時間)
        }

        self.patients.append(patient_record)
        patient.hospitalize(self)

        print(f"{patient.name} 因 {cause} 住院治療")
        return True

    def discharge_patient(self, patient):
        """
        出院\n
        \n
        參數:\n
        patient (NPC): 出院患者\n
        """
        for record in self.patients[:]:
            if record["patient"] == patient:
                self.patients.remove(record)
                patient.discharge()
                print(f"{patient.name} 出院了")
                break

    def respawn_player(self, player):
        """
        玩家重生\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        # 重置玩家狀態
        player.health = PLAYER_MAX_HEALTH
        player.set_position((self.x + self.width // 2, self.y + self.height + 20))

        print(f"玩家在 {self.name} 重生")

        return {"success": True, "message": "您已在醫院重生"}


######################建築管理器######################
class BuildingManager:
    """
    建築管理器 - 統一管理所有建築物\n
    \n
    負責建築物的創建、更新、互動檢測等功能\n
    根據規格書要求配置正確數量的各類建築\n
    """

    def __init__(self):
        """
        初始化建築管理器\n
        """
        self.buildings = []
        self.buildings_by_type = {}

        # 建築統計
        self.building_counts = {
            "gun_shop": 0,
            "hospital": 0,
            "convenience_store": 0,
            "church": 0,
            "fishing_shop": 0,
            "market": 0,
            "street_vendor": 0,
            "power_plant": 0,
        }

        print("建築管理器初始化完成")

    def create_buildings_for_town(self, town_bounds):
        """
        為小鎮創建所有建築\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界 (x, y, width, height)\n
        """
        tx, ty, tw, th = town_bounds

        # 創建醫院 (5座)
        self._create_hospitals(town_bounds)

        # 創建槍械店 (10座)
        self._create_gun_shops(town_bounds)

        # 創建便利商店 (15座)
        self._create_convenience_stores(town_bounds)

        # 創建教堂 (2座)
        self._create_churches(town_bounds)

        # 創建其他建築
        self._create_other_buildings(town_bounds)

        print(f"建築創建完成，總計 {len(self.buildings)} 座建築")

    def _create_hospitals(self, town_bounds):
        """
        創建醫院\n
        """
        tx, ty, tw, th = town_bounds

        for i in range(HOSPITAL_COUNT):
            # 分散在小鎮各處
            x = tx + (i % 3) * (tw // 3) + random.randint(50, 100)
            y = ty + (i // 3) * (th // 2) + random.randint(50, 100)

            hospital = Hospital((x, y))
            self._add_building(hospital)

    def _create_gun_shops(self, town_bounds):
        """
        創建槍械店\n
        """
        tx, ty, tw, th = town_bounds

        for i in range(GUN_SHOP_COUNT):
            x = tx + random.randint(50, tw - 150)
            y = ty + random.randint(50, th - 100)

            gun_shop = GunShop((x, y))
            self._add_building(gun_shop)

    def _create_convenience_stores(self, town_bounds):
        """
        創建便利商店\n
        """
        tx, ty, tw, th = town_bounds

        for i in range(CONVENIENCE_STORE_COUNT):
            x = tx + random.randint(30, tw - 120)
            y = ty + random.randint(30, th - 80)

            store = Building("convenience_store", (x, y), (100, 60))
            self._add_building(store)

    def _create_churches(self, town_bounds):
        """
        創建教堂\n
        """
        tx, ty, tw, th = town_bounds

        for i in range(CHURCH_COUNT):
            x = tx + (i * tw // 2) + tw // 4 - 75
            y = ty + th // 4

            church = Building("church", (x, y), (150, 120))
            self._add_building(church)

    def _create_other_buildings(self, town_bounds):
        """
        創建其他建築\n
        """
        tx, ty, tw, th = town_bounds

        # 市場 (1座)
        market = Building("market", (tx + tw // 2 - 100, ty + th // 2 - 75), (200, 150))
        self._add_building(market)

        # 電力場 (1座)
        power_plant = Building("power_plant", (tx + tw - 200, ty + 50), (150, 100))
        self._add_building(power_plant)

        # 路邊小販 (10個)
        for i in range(STREET_VENDOR_COUNT):
            x = tx + random.randint(100, tw - 100)
            y = ty + random.randint(100, th - 100)

            vendor = Building("street_vendor", (x, y), (40, 40))
            self._add_building(vendor)

    def _add_building(self, building):
        """
        添加建築到管理器\n
        \n
        參數:\n
        building (Building): 建築物件\n
        """
        self.buildings.append(building)

        # 按類型分類
        building_type = building.building_type
        if building_type not in self.buildings_by_type:
            self.buildings_by_type[building_type] = []
        self.buildings_by_type[building_type].append(building)

        # 更新統計
        if building_type in self.building_counts:
            self.building_counts[building_type] += 1

    def get_nearby_building(self, position, max_distance=50):
        """
        獲取附近的建築\n
        \n
        參數:\n
        position (tuple): 位置\n
        max_distance (float): 最大距離\n
        \n
        回傳:\n
        Building: 最近的建築，如果沒有則返回 None\n
        """
        closest_building = None
        closest_distance = float("inf")

        px, py = position

        for building in self.buildings:
            if building.can_interact(position, max_distance):
                # 計算到建築中心的距離
                bx = building.x + building.width // 2
                by = building.y + building.height // 2
                distance = math.sqrt((px - bx) ** 2 + (py - by) ** 2)

                if distance < closest_distance:
                    closest_distance = distance
                    closest_building = building

        return closest_building

    def get_buildings_by_type(self, building_type):
        """
        獲取指定類型的建築列表\n
        \n
        參數:\n
        building_type (str): 建築類型\n
        \n
        回傳:\n
        list: 建築列表\n
        """
        return self.buildings_by_type.get(building_type, [])

    def get_nearest_hospital(self, position):
        """
        獲取最近的醫院\n
        \n
        參數:\n
        position (tuple): 位置\n
        \n
        回傳:\n
        Hospital: 最近的醫院\n
        """
        hospitals = self.get_buildings_by_type("hospital")
        if not hospitals:
            return None

        px, py = position
        nearest_hospital = min(
            hospitals, key=lambda h: math.sqrt((h.x - px) ** 2 + (h.y - py) ** 2)
        )

        return nearest_hospital

    def draw_all_buildings(self, screen):
        """
        繪製所有建築\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for building in self.buildings:
            building.draw(screen)

    def get_statistics(self):
        """
        獲取建築統計\n
        \n
        回傳:\n
        dict: 統計資訊\n
        """
        return {
            "total_buildings": len(self.buildings),
            "building_counts": self.building_counts.copy(),
        }
