######################載入套件######################
import pygame
import random
import math
from config.settings import *
from src.systems.furniture_system import HouseInteriorManager
from src.utils.font_manager import FontManager


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
        
        # 字體管理器
        self.font_manager = FontManager()

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

    def _setup_clothing_store_outfits(self):
        """
        設定服裝店的套裝選項\n
        根據新需求：提供 5 套可購買的套裝，每套價格為 300 元\n
        """
        if self.building_type == "clothing_store":
            self.available_outfits = [
                {"id": 1, "name": "休閒套裝", "price": CLOTHING_OUTFIT_PRICE, "color": (0, 100, 200)},
                {"id": 2, "name": "正式套裝", "price": CLOTHING_OUTFIT_PRICE, "color": (50, 50, 50)},
                {"id": 3, "name": "運動套裝", "price": CLOTHING_OUTFIT_PRICE, "color": (255, 100, 100)},
                {"id": 4, "name": "夏日套裝", "price": CLOTHING_OUTFIT_PRICE, "color": (255, 255, 100)},
                {"id": 5, "name": "冬季套裝", "price": CLOTHING_OUTFIT_PRICE, "color": (100, 50, 150)}
            ]

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

        elif self.building_type == "clothing_store":
            self.name = "服裝店"
            self.color = (255, 20, 147)  # 深粉色
            self.services = ["購買套裝"]
            self.staff_count = 2
            # 服裝店專用屬性
            self.available_outfits = []
            self._setup_clothing_store_outfits()

        elif self.building_type == "power_plant":
            self.name = "電力場"
            self.color = (255, 255, 0)  # 黃色
            self.services = ["電力供應"]
            self.staff_count = 30

        elif self.building_type == "park":
            self.name = "公園"
            self.color = (50, 205, 50)  # 綠色
            self.services = ["休閒娛樂"]
            self.staff_count = 3

        elif self.building_type == "clothing_store":
            self.name = "服裝店"
            self.color = (255, 20, 147)  # 粉色
            self.services = ["買衣服", "換裝"]
            self.staff_count = 3

        elif self.building_type == "office_building":
            self.name = "辦公大樓"
            self.color = (169, 169, 169)  # 灰色
            self.services = ["辦公服務"]
            self.staff_count = 15

        elif self.building_type == "factory":
            self.name = "工廠"
            self.color = (105, 105, 105)  # 深灰色
            self.services = ["生產製造"]
            self.staff_count = 20

        elif self.building_type == "house":
            self.name = "住宅"
            self.color = (160, 82, 45)  # 淺棕色
            self.services = ["居住"]
            self.staff_count = 0

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

        # 服裝店特殊互動
        if self.building_type == "clothing_store":
            return self._handle_clothing_store_interaction(player)
        
        # 其他建築的通用互動
        return {
            "success": True,
            "building": self,
            "services": self.services,
            "message": f"歡迎來到{self.name}！",
        }

    def _handle_clothing_store_interaction(self, player):
        """
        處理服裝店互動\n
        根據新需求：提供 5 套可購買的套裝，每套價格為 300 元\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 互動結果\n
        """
        message = f"歡迎來到{self.name}！\\n\\n可購買的套裝：\\n"
        
        for i, outfit in enumerate(self.available_outfits, 1):
            owned_status = "已擁有" if outfit['id'] in player.owned_outfits else f"${outfit['price']}"
            message += f"{i}. {outfit['name']} - {owned_status}\\n"
        
        message += f"\\n您目前有 ${player.get_money()}\\n"
        message += "按數字鍵 1-5 購買對應套裝"
        
        return {
            "success": True,
            "building": self,
            "building_type": "clothing_store",
            "message": message,
            "available_outfits": self.available_outfits
        }

    def purchase_outfit(self, player, outfit_id):
        """
        購買套裝\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        outfit_id (int): 套裝ID\n
        \n
        回傳:\n
        dict: 購買結果\n
        """
        if self.building_type != "clothing_store":
            return {"success": False, "message": "此建築不是服裝店"}
        
        # 尋找對應的套裝
        target_outfit = None
        for outfit in self.available_outfits:
            if outfit['id'] == outfit_id:
                target_outfit = outfit
                break
        
        if not target_outfit:
            return {"success": False, "message": "找不到指定的套裝"}
        
        # 檢查是否已擁有
        if outfit_id in player.owned_outfits:
            return {"success": False, "message": f"您已經擁有{target_outfit['name']}"}
        
        # 檢查金錢是否足夠
        if player.get_money() < target_outfit['price']:
            return {
                "success": False, 
                "message": f"金錢不足！需要 ${target_outfit['price']}，您有 ${player.get_money()}"
            }
        
        # 進行購買
        if player.spend_money(target_outfit['price']):
            player.owned_outfits.append(outfit_id)
            return {
                "success": True, 
                "message": f"成功購買 {target_outfit['name']}！",
                "outfit": target_outfit
            }
        else:
            return {"success": False, "message": "購買失敗"}

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

        # 建築物名稱標籤已移除（依據新需求）

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

    def __init__(self, position, size=(60, 40)):
        """
        初始化槍械店\n
        \n
        參數:\n
        position (tuple): 位置 (x, y)\n
        size (tuple): 尺寸 (width, height)（調整為配合新的玩家尺寸）\n
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

    def __init__(self, position, size=(75, 50)):
        """
        初始化醫院\n
        \n
        參數:\n
        position (tuple): 位置 (x, y)\n
        size (tuple): 尺寸 (width, height)（調整為配合新的玩家尺寸）\n
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


######################住宅建築######################
class ResidentialHouse(Building):
    """
    住宅建築 - 專門的住宅類別\n
    \n
    提供住宅的特殊功能：\n
    - 居民管理\n
    - 內部檢視\n
    - 正方形外觀\n
    - 玩家之家特殊標記\n
    - 家具佈置系統\n
    - 門系統\n
    """

    def __init__(self, building_type, position, size):
        """
        初始化住宅\n
        \n
        參數:\n
        building_type (str): 建築類型\n
        position (tuple): 位置 (x, y)\n
        size (tuple): 尺寸 (width, height)\n
        """
        super().__init__(building_type, position, size)
        
        # 字體管理器
        from src.utils.font_manager import get_font_manager
        self.font_manager = get_font_manager()
        
        # 住宅特殊屬性
        self.residents = []  # 居民列表
        self.max_residents = 3  # 最多3個居民
        self.is_player_home = False  # 是否為玩家之家
        self.interior_visible = False  # 是否顯示內部檢視
        
        # 住宅外觀設定為正方形
        self.color = (160, 82, 45)  # 住宅標準顏色
        
        # 內部佈置系統
        self.interior_manager = HouseInteriorManager()
        self.interior = None  # 住宅內部佈置
        self.has_interior = False  # 是否已生成內部佈置
        
        # 玩家在住宅內的位置（僅在內部檢視時使用）
        self.player_interior_position = None

    def initialize_interior(self):
        """
        初始化住宅內部佈置（延遲載入）\n
        """
        if not self.has_interior:
            self.interior = self.interior_manager.create_interior_for_house(self)
            self.has_interior = True
            print(f"為住宅 {self.name} 創建了內部佈置")

    def add_resident(self, npc):
        """
        添加居民到住宅\n
        \n
        參數:\n
        npc (NPC): 要添加的NPC\n
        \n
        回傳:\n
        bool: 是否成功添加\n
        """
        if len(self.residents) >= self.max_residents:
            return False
        
        self.residents.append(npc)
        npc.set_home((self.x + self.width // 2, self.y + self.height // 2))
        print(f"NPC {npc.name} 被分配到住宅 {self.name}")
        return True

    def remove_resident(self, npc):
        """
        從住宅移除居民\n
        \n
        參數:\n
        npc (NPC): 要移除的NPC\n
        """
        if npc in self.residents:
            self.residents.remove(npc)
            print(f"NPC {npc.name} 離開住宅 {self.name}")

    def get_resident_count(self):
        """
        獲取住宅內居民數量\n
        \n
        回傳:\n
        int: 居民數量\n
        """
        return len(self.residents)

    def is_full(self):
        """
        檢查住宅是否已滿\n
        \n
        回傳:\n
        bool: 是否已滿\n
        """
        return len(self.residents) >= self.max_residents

    def toggle_interior_view(self, player):
        """
        切換住宅內部檢視\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 切換結果\n
        """
        # 確保內部佈置已初始化
        if not self.has_interior:
            self.initialize_interior()
        
        self.interior_visible = not self.interior_visible
        
        if self.interior_visible:
            # 進入內部檢視 - 將玩家移至住宅內部的入口門附近
            entrance_door = None
            for door in self.interior["doors"]:
                if door.door_type == "entrance":
                    entrance_door = door
                    break
            
            if entrance_door:
                self.player_interior_position = (
                    entrance_door.x + entrance_door.width // 2,
                    entrance_door.y - 10  # 玩家位置稍微往上一點
                )
            else:
                # 如果沒有找到入口門，將玩家放在住宅中央
                self.player_interior_position = (self.width // 2, self.height // 2)
            
            return {
                "success": True,
                "action": "enter_interior",
                "message": f"進入{self.name}內部",
                "interior_position": self.player_interior_position
            }
        else:
            # 離開內部檢視 - 將玩家移至住宅外部
            self.player_interior_position = None
            return {
                "success": True,
                "action": "exit_interior",
                "message": f"離開{self.name}",
                "exterior_position": (self.x + self.width // 2, self.y + self.height + 15)
            }

    def get_nearby_interactive_objects(self, player_position, max_distance=20):
        """
        獲取玩家附近可互動的物件（僅在內部檢視時）\n
        \n
        參數:\n
        player_position (tuple): 玩家在住宅內的位置\n
        max_distance (float): 最大互動距離\n
        \n
        回傳:\n
        list: 可互動的物件列表\n
        """
        if not self.interior_visible or not self.has_interior:
            return []
        
        return self.interior_manager.get_interactive_objects_near_player(
            self.interior, player_position, max_distance
        )

    def interact_with_interior_object(self, object_type, obj, player):
        """
        與住宅內部物件互動\n
        \n
        參數:\n
        object_type (str): 物件類型 ("furniture" 或 "door")\n
        obj: 物件實例\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 互動結果\n
        """
        if object_type == "door" and obj.door_type == "entrance":
            # 與入口門互動 - 切換內外檢視
            return self.toggle_interior_view(player)
        else:
            # 與其他物件互動
            return obj.interact(player)

    def interact(self, player):
        """
        住宅互動 - 顯示內部狀況或進入內部檢視\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 互動結果\n
        """
        if self.is_player_home:
            # 玩家之家的特殊互動 - 直接進入內部檢視
            return self.toggle_interior_view(player)
        else:
            # 一般住宅的內部檢視
            return {
                "success": True,
                "building": self,
                "message": f"住宅內部 - 居民數量: {len(self.residents)}/{self.max_residents}",
                "action": "view_exterior",
                "residents": self.residents,
            }

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製住宅 - 正方形外觀和內部檢視\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        # 計算螢幕座標
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        screen_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        
        if self.interior_visible:
            # 內部檢視模式 - 繪製住宅內部
            self._draw_interior_view(screen, camera_x, camera_y)
        else:
            # 外部檢視模式 - 繪製住宅外觀
            self._draw_exterior_view(screen, screen_rect)

    def _draw_exterior_view(self, screen, screen_rect):
        """
        繪製住宅外觀\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        screen_rect (pygame.Rect): 螢幕矩形\n
        """
        # 繪製住宅主體（正方形）
        pygame.draw.rect(screen, self.color, screen_rect)
        pygame.draw.rect(screen, (0, 0, 0), screen_rect, 2)

        # 如果是玩家之家，添加特殊標記
        if self.is_player_home:
            # 繪製家的標記（小星星或特殊符號）
            center_x = screen_rect.centerx
            center_y = screen_rect.centery
            pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), 8)
            
            # 繪製家的標誌文字
            font = self.font_manager.get_font(16)
            text = font.render("家", True, (0, 0, 0))
            text_rect = text.get_rect(center=(center_x, center_y))
            screen.blit(text, text_rect)
        else:
            # 一般住宅顯示居民數量
            text = self.font_manager.render_text(f"{len(self.residents)}", 20, (255, 255, 255))
            text_rect = text.get_rect(center=screen_rect.center)
            screen.blit(text, text_rect)

    def _draw_interior_view(self, screen, camera_x, camera_y):
        """
        繪製住宅內部檢視\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        # 確保內部佈置已初始化
        if not self.has_interior:
            self.initialize_interior()
        
        # 繪製住宅內部背景
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        interior_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        
        # 內部地板（米色）
        pygame.draw.rect(screen, (245, 245, 220), interior_rect)
        # 內部牆壁邊框
        pygame.draw.rect(screen, (139, 69, 19), interior_rect, 3)
        
        # 繪製家具和門
        if self.interior:
            self.interior_manager.draw_interior(
                screen, self.interior, self.x, self.y, camera_x, camera_y
            )
        
        # 繪製內部檢視標記（已移除名稱顯示，依據新需求）
        # 保留房間內部檢視功能但不顯示標題

    def get_resident_info(self):
        """
        獲取住宅居民資訊\n
        \n
        回傳:\n
        list: 居民資訊列表\n
        """
        resident_info = []
        for resident in self.residents:
            info = {
                "name": resident.name,
                "profession": resident.profession.value if hasattr(resident, 'profession') else "無業",
                "status": "在家" if not resident.is_at_work else "工作中",
                "is_injured": resident.is_injured if hasattr(resident, 'is_injured') else False,
            }
            resident_info.append(info)
        return resident_info

    def get_interior_stats(self):
        """
        獲取住宅內部統計資訊\n
        \n
        回傳:\n
        dict: 內部統計\n
        """
        if not self.has_interior:
            return {"furniture_count": 0, "door_count": 0, "layout_type": "未初始化"}
        
        furniture_count = len(self.interior["furniture"])
        door_count = len(self.interior["doors"])
        layout_type = self.interior["layout_type"]
        
        return {
            "furniture_count": furniture_count,
            "door_count": door_count,
            "layout_type": layout_type,
            "is_interior_visible": self.interior_visible
        }


######################網格建築管理器######################
class GridBuildingManager:
    """
    網格建築管理器 - 基於網格系統管理建築物\n
    \n
    實現新的地圖格規則：\n
    - 一格大小為玩家的 216 倍\n
    - 住宅：長寬至少玩家的 5 倍，每格最多 6 個\n
    - 商業建築：長寬至少玩家的 7 倍，每格最多 4 個\n
    - 建築之間必須保有通行間隙\n
    """

    def __init__(self):
        """
        初始化網格建築管理器\n
        """
        # 建築物列表
        self.buildings = []
        self.buildings_by_type = {}
        
        # 網格系統 - 儲存每個網格的建築物
        self.grid_buildings = {}  # {(grid_x, grid_y): {"residential": [], "commercial": []}}
        
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

        print("網格建築管理器初始化完成")

    def get_grid_position(self, world_x, world_y):
        """
        獲取世界座標對應的網格位置\n
        \n
        參數:\n
        world_x (float): 世界座標 X\n
        world_y (float): 世界座標 Y\n
        \n
        回傳:\n
        tuple: (grid_x, grid_y) 網格座標\n
        """
        grid_x = int(world_x // GRID_SIZE)
        grid_y = int(world_y // GRID_SIZE)
        return (grid_x, grid_y)

    def get_grid_bounds(self, grid_x, grid_y):
        """
        獲取網格的邊界座標\n
        \n
        參數:\n
        grid_x (int): 網格 X 座標\n
        grid_y (int): 網格 Y 座標\n
        \n
        回傳:\n
        tuple: (min_x, min_y, max_x, max_y) 網格邊界\n
        """
        min_x = grid_x * GRID_SIZE
        min_y = grid_y * GRID_SIZE
        max_x = min_x + GRID_SIZE
        max_y = min_y + GRID_SIZE
        return (min_x, min_y, max_x, max_y)

    def can_place_building(self, grid_x, grid_y, building_type, building_width, building_height):
        """
        檢查是否可以在指定網格放置建築\n
        \n
        參數:\n
        grid_x (int): 網格 X 座標\n
        grid_y (int): 網格 Y 座標\n
        building_type (str): 建築類型 ("residential" 或 "commercial")\n
        building_width (int): 建築寬度\n
        building_height (int): 建築高度\n
        \n
        回傳:\n
        bool: 是否可以放置\n
        """
        # 檢查建築尺寸是否符合最小要求
        if building_type == "residential":
            min_size = RESIDENTIAL_MIN_SIZE
            max_buildings = RESIDENTIAL_MAX_PER_GRID
        elif building_type == "commercial":
            min_size = COMMERCIAL_MIN_SIZE
            max_buildings = COMMERCIAL_MAX_PER_GRID
        else:
            return False

        if building_width < min_size or building_height < min_size:
            return False

        # 檢查網格是否存在
        grid_key = (grid_x, grid_y)
        if grid_key not in self.grid_buildings:
            self.grid_buildings[grid_key] = {"residential": [], "commercial": []}

        # 檢查該類型建築數量是否已達上限
        current_count = len(self.grid_buildings[grid_key][building_type])
        if current_count >= max_buildings:
            return False

        return True

    def find_placement_position(self, grid_x, grid_y, building_type, building_width, building_height):
        """
        在網格內尋找合適的建築放置位置\n
        \n
        參數:\n
        grid_x (int): 網格 X 座標\n
        grid_y (int): 網格 Y 座標\n
        building_type (str): 建築類型\n
        building_width (int): 建築寬度\n
        building_height (int): 建築高度\n
        \n
        回傳:\n
        tuple: (x, y) 建築位置，如果找不到則回傳 None\n
        """
        min_x, min_y, max_x, max_y = self.get_grid_bounds(grid_x, grid_y)
        
        # 設定間隙
        spacing = RESIDENTIAL_SPACING if building_type == "residential" else COMMERCIAL_SPACING
        
        # 獲取網格內已有的建築
        grid_key = (grid_x, grid_y)
        if grid_key not in self.grid_buildings:
            self.grid_buildings[grid_key] = {"residential": [], "commercial": []}
        
        existing_buildings = []
        existing_buildings.extend(self.grid_buildings[grid_key]["residential"])
        existing_buildings.extend(self.grid_buildings[grid_key]["commercial"])
        
        # 嘗試多個位置
        attempts = 50  # 最多嘗試50次
        for _ in range(attempts):
            # 隨機選擇位置，但確保不超出網格邊界
            x = random.randint(min_x + spacing, max_x - building_width - spacing)
            y = random.randint(min_y + spacing, max_y - building_height - spacing)
            
            # 檢查與其他建築的衝突
            new_rect = pygame.Rect(x, y, building_width, building_height)
            collision = False
            
            for existing_building in existing_buildings:
                existing_rect = pygame.Rect(
                    existing_building["x"] - spacing,
                    existing_building["y"] - spacing,
                    existing_building["width"] + 2 * spacing,
                    existing_building["height"] + 2 * spacing
                )
                
                if new_rect.colliderect(existing_rect):
                    collision = True
                    break
            
            if not collision:
                return (x, y)
        
        # 如果隨機放置失敗，嘗試網格式放置
        return self._grid_placement(grid_x, grid_y, building_type, building_width, building_height)

    def _grid_placement(self, grid_x, grid_y, building_type, building_width, building_height):
        """
        使用網格式放置算法\n
        \n
        參數:\n
        grid_x (int): 網格 X 座標\n
        grid_y (int): 網格 Y 座標\n
        building_type (str): 建築類型\n
        building_width (int): 建築寬度\n
        building_height (int): 建築高度\n
        \n
        回傳:\n
        tuple: (x, y) 建築位置，如果找不到則回傳 None\n
        """
        min_x, min_y, max_x, max_y = self.get_grid_bounds(grid_x, grid_y)
        spacing = RESIDENTIAL_SPACING if building_type == "residential" else COMMERCIAL_SPACING
        
        # 計算可用空間
        available_width = GRID_SIZE - 2 * spacing
        available_height = GRID_SIZE - 2 * spacing
        
        # 計算可以放置的建築數量
        if building_type == "residential":
            # 住宅嘗試 2x3 或 3x2 排列
            cols = 3 if available_width >= 3 * (building_width + spacing) else 2
            rows = 2 if cols == 3 else 3
        else:  # commercial
            # 商業建築嘗試 2x2 排列
            cols = 2
            rows = 2
        
        # 計算每個建築的放置位置
        grid_key = (grid_x, grid_y)
        existing_count = len(self.grid_buildings[grid_key][building_type])
        
        if existing_count >= cols * rows:
            return None
        
        # 計算當前建築應該放在第幾個位置
        pos_index = existing_count
        col = pos_index % cols
        row = pos_index // cols
        
        # 計算實際座標
        cell_width = available_width // cols
        cell_height = available_height // rows
        
        x = min_x + spacing + col * cell_width + (cell_width - building_width) // 2
        y = min_y + spacing + row * cell_height + (cell_height - building_height) // 2
        
        # 確保建築不超出網格
        x = max(min_x + spacing, min(x, max_x - building_width - spacing))
        y = max(min_y + spacing, min(y, max_y - building_height - spacing))
        
        return (x, y)

    def place_building(self, building, grid_x, grid_y, building_type):
        """
        在網格中放置建築\n
        \n
        參數:\n
        building (Building): 建築物件\n
        grid_x (int): 網格 X 座標\n
        grid_y (int): 網格 Y 座標\n
        building_type (str): 建築類型\n
        \n
        回傳:\n
        bool: 是否成功放置\n
        """
        # 檢查是否可以放置
        if not self.can_place_building(grid_x, grid_y, building_type, building.width, building.height):
            return False
        
        # 尋找放置位置
        position = self.find_placement_position(grid_x, grid_y, building_type, building.width, building.height)
        if position is None:
            return False
        
        # 更新建築位置
        building.x, building.y = position
        building.rect.x = building.x
        building.rect.y = building.y
        
        # 添加到網格記錄
        grid_key = (grid_x, grid_y)
        building_info = {
            "building": building,
            "x": building.x,
            "y": building.y,
            "width": building.width,
            "height": building.height
        }
        self.grid_buildings[grid_key][building_type].append(building_info)
        
        # 添加到建築管理器
        self._add_building(building)
        
        return True

    def create_buildings_for_town(self, town_bounds):
        """
        為小鎮創建所有建築\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界 (x, y, width, height)\n
        """
        tx, ty, tw, th = town_bounds

        # 計算小鎮包含的網格範圍
        start_grid_x, start_grid_y = self.get_grid_position(tx, ty)
        end_grid_x, end_grid_y = self.get_grid_position(tx + tw, ty + th)

        # 創建住宅建築（使用網格系統）
        self._create_residential_buildings(start_grid_x, start_grid_y, end_grid_x, end_grid_y)

        # 創建商業建築（使用網格系統）
        self._create_commercial_buildings(start_grid_x, start_grid_y, end_grid_x, end_grid_y)

        print(f"建築創建完成，總計 {len(self.buildings)} 座建築")

    def _create_residential_buildings(self, start_grid_x, start_grid_y, end_grid_x, end_grid_y):
        """
        創建住宅建築 - 限制為4個住宅，外觀改為正方形\n
        """
        residential_created = 0
        target_count = 4  # 明確限制為4個住宅

        # 在住宅區網格範圍內只創建4個住宅
        for grid_y in range(start_grid_y, end_grid_y):
            for grid_x in range(start_grid_x, end_grid_x):
                if residential_created >= target_count:
                    break

                # 創建一個住宅
                # 住宅尺寸：正方形外觀，大小統一
                width = 60   # 正方形寬度
                height = 60  # 正方形高度
                
                # 創建住宅
                house = ResidentialHouse("house", (0, 0), (width, height))
                
                # 檢查是否為玩家之家（第一個住宅）
                if residential_created == 0:
                    house.is_player_home = True
                    house.name = "玩家之家"
                    house.color = (255, 215, 0)  # 金色標記玩家之家
                
                # 嘗試放置在網格中
                if self.place_building(house, grid_x, grid_y, "residential"):
                    residential_created += 1
                else:
                    # 如果無法放置，嘗試下一個網格
                    continue

            if residential_created >= target_count:
                break

        print(f"創建了 {residential_created} 座住宅建築（包含1座玩家之家）")

    def _create_commercial_buildings(self, start_grid_x, start_grid_y, end_grid_x, end_grid_y):
        """
        創建商業建築\n
        """
        # 要創建的商業建築類型和數量
        commercial_types = [
            ("hospital", HOSPITAL_COUNT),
            ("gun_shop", GUN_SHOP_COUNT),
            ("convenience_store", CONVENIENCE_STORE_COUNT),
            ("church", CHURCH_COUNT),
            ("market", 1),
            ("power_plant", 1),
        ]

        for building_type, count in commercial_types:
            created = 0
            
            for grid_y in range(start_grid_y, end_grid_y):
                for grid_x in range(start_grid_x, end_grid_x):
                    if created >= count:
                        break

                    # 商業建築尺寸：長寬至少為玩家的7倍（調整為更合理的尺寸）
                    if building_type == "hospital":
                        width, height = 80, 60  # 醫院較大
                    elif building_type == "church":
                        width, height = 90, 70  # 教堂較大
                    elif building_type == "market":
                        width, height = 100, 80  # 市場最大
                    elif building_type == "power_plant":
                        width, height = 95, 75  # 電力場較大
                    else:
                        # 其他商業建築
                        width = random.randint(COMMERCIAL_MIN_SIZE, COMMERCIAL_MIN_SIZE + 30)
                        height = random.randint(COMMERCIAL_MIN_SIZE, COMMERCIAL_MIN_SIZE + 25)

                    # 創建建築
                    if building_type == "hospital":
                        building = Hospital((0, 0), (width, height))
                    elif building_type == "gun_shop":
                        building = GunShop((0, 0), (width, height))
                    else:
                        building = Building(building_type, (0, 0), (width, height))

                    # 嘗試放置在網格中
                    if self.place_building(building, grid_x, grid_y, "commercial"):
                        created += 1

                if created >= count:
                    break

            print(f"創建了 {created} 座 {building_type} 建築")

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

    def get_player_home(self):
        """
        獲取玩家之家建築\n
        \n
        回傳:\n
        ResidentialHouse: 玩家之家建築物件，如果找不到則回傳 None\n
        """
        for building in self.buildings:
            if hasattr(building, 'is_player_home') and building.is_player_home:
                return building
        return None

    def get_player_home_position(self):
        """
        獲取玩家之家的中心位置\n
        \n
        回傳:\n
        tuple: 玩家之家的中心位置 (x, y)，如果找不到則回傳 None\n
        """
        player_home = self.get_player_home()
        if player_home:
            center_x = player_home.x + player_home.width // 2
            center_y = player_home.y + player_home.height // 2
            return (center_x, center_y)
        return None

    def get_residential_buildings(self):
        """
        獲取所有住宅建築\n
        \n
        回傳:\n
        list: 住宅建築列表\n
        """
        residential_buildings = []
        for building in self.buildings:
            if hasattr(building, 'building_type') and building.building_type == "house":
                residential_buildings.append(building)
        return residential_buildings

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
