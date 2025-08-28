######################載入套件######################
import pygame
import random
from config.settings import *


######################家具類別######################
class Furniture:
    """
    家具基礎類別 - 表示住宅內的各種家具\n
    \n
    所有家具的共同基礎，包含位置、尺寸、類型等基本屬性\n
    支援不同類型的家具，如床、桌子、椅子、廚具等\n
    提供統一的渲染系統和碰撞檢測\n
    """

    def __init__(self, furniture_type, position, size):
        """
        初始化家具\n
        \n
        參數:\n
        furniture_type (str): 家具類型\n
        position (tuple): 在住宅內的相對位置 (x, y)\n
        size (tuple): 尺寸 (width, height)\n
        """
        self.furniture_type = furniture_type
        self.x, self.y = position
        self.width, self.height = size
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # 根據家具類型設定屬性
        self._setup_furniture_properties()
        
        # 家具狀態
        self.is_interactive = False
        self.interaction_text = ""

    def _setup_furniture_properties(self):
        """
        根據家具類型設定屬性\n
        """
        if self.furniture_type == "bed":
            self.name = "床"
            self.color = (139, 69, 19)  # 棕色
            self.is_interactive = True
            self.interaction_text = "睡覺"

        elif self.furniture_type == "table":
            self.name = "桌子"
            self.color = (160, 82, 45)  # 淺棕色
            self.is_interactive = True
            self.interaction_text = "使用桌子"

        elif self.furniture_type == "chair":
            self.name = "椅子"
            self.color = (101, 67, 33)  # 深棕色
            self.is_interactive = True
            self.interaction_text = "坐下"

        elif self.furniture_type == "sofa":
            self.name = "沙發"
            self.color = (128, 0, 128)  # 紫色
            self.is_interactive = True
            self.interaction_text = "休息"

        elif self.furniture_type == "kitchen":
            self.name = "廚房"
            self.color = (192, 192, 192)  # 銀色
            self.is_interactive = True
            self.interaction_text = "烹飪"

        elif self.furniture_type == "wardrobe":
            self.name = "衣櫃"
            self.color = (139, 69, 19)  # 棕色
            self.is_interactive = True
            self.interaction_text = "換衣服"

        elif self.furniture_type == "tv":
            self.name = "電視"
            self.color = (0, 0, 0)  # 黑色
            self.is_interactive = True
            self.interaction_text = "看電視"

        elif self.furniture_type == "bookshelf":
            self.name = "書櫃"
            self.color = (160, 82, 45)  # 淺棕色
            self.is_interactive = True
            self.interaction_text = "讀書"

        else:
            self.name = "家具"
            self.color = (139, 69, 19)  # 預設棕色

    def can_interact(self, player_position, max_distance=20):
        """
        檢查玩家是否可以與家具互動\n
        \n
        參數:\n
        player_position (tuple): 玩家在住宅內的位置\n
        max_distance (float): 最大互動距離\n
        \n
        回傳:\n
        bool: 是否可以互動\n
        """
        if not self.is_interactive:
            return False
            
        px, py = player_position
        furniture_center_x = self.x + self.width // 2
        furniture_center_y = self.y + self.height // 2
        
        distance = ((px - furniture_center_x) ** 2 + (py - furniture_center_y) ** 2) ** 0.5
        return distance <= max_distance

    def interact(self, player):
        """
        與家具互動\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 互動結果\n
        """
        if not self.is_interactive:
            return {"success": False, "message": f"{self.name}無法互動"}

        # 根據家具類型執行不同的互動
        if self.furniture_type == "bed":
            return self._interact_bed(player)
        elif self.furniture_type == "kitchen":
            return self._interact_kitchen(player)
        elif self.furniture_type == "wardrobe":
            return self._interact_wardrobe(player)
        elif self.furniture_type == "tv":
            return self._interact_tv(player)
        else:
            return {
                "success": True,
                "message": f"使用了{self.name}",
                "furniture": self
            }

    def _interact_bed(self, player):
        """
        床的互動 - 恢復體力\n
        """
        if hasattr(player, 'health') and player.health < 100:
            player.health = min(100, player.health + 20)
            return {
                "success": True,
                "message": "在床上休息，恢復了一些體力",
                "health_recovered": 20
            }
        else:
            return {
                "success": True,
                "message": "在舒適的床上休息片刻"
            }

    def _interact_kitchen(self, player):
        """
        廚房的互動 - 烹飪食物\n
        """
        # 簡單的烹飪系統
        return {
            "success": True,
            "message": "在廚房準備了一些食物",
            "action": "cooking"
        }

    def _interact_wardrobe(self, player):
        """
        衣櫃的互動 - 換衣服\n
        """
        return {
            "success": True,
            "message": "打開衣櫃，查看衣服",
            "action": "change_clothes"
        }

    def _interact_tv(self, player):
        """
        電視的互動 - 看電視\n
        """
        return {
            "success": True,
            "message": "打開電視，正在播放新聞節目",
            "action": "watch_tv"
        }

    def draw(self, screen, house_world_x, house_world_y, camera_x, camera_y):
        """
        繪製家具\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        house_world_x (int): 住宅的世界X座標\n
        house_world_y (int): 住宅的世界Y座標\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        # 計算家具在世界座標系中的位置
        world_x = house_world_x + self.x
        world_y = house_world_y + self.y
        
        # 計算螢幕座標
        screen_x = world_x - camera_x
        screen_y = world_y - camera_y
        
        # 創建螢幕矩形
        screen_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        
        # 繪製家具
        pygame.draw.rect(screen, self.color, screen_rect)
        pygame.draw.rect(screen, (0, 0, 0), screen_rect, 1)
        
        # 繪製家具名稱（如果家具夠大）
        if self.width > 15 and self.height > 10:
            font = pygame.font.Font(None, 12)
            text = font.render(self.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=screen_rect.center)
            screen.blit(text, text_rect)


######################門類別######################
class Door:
    """
    門類別 - 住宅的進出口\n
    \n
    處理玩家在住宅內外的切換\n
    支援開關門的動畫和互動\n
    管理住宅的進入和離開邏輯\n
    """

    def __init__(self, position, door_type="entrance"):
        """
        初始化門\n
        \n
        參數:\n
        position (tuple): 門在住宅內的位置 (x, y)\n
        door_type (str): 門的類型 ("entrance" 為主要入口)\n
        """
        self.x, self.y = position
        self.door_type = door_type
        self.width = 8
        self.height = 12
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # 門的狀態
        self.is_open = False
        self.is_interactive = True
        
        # 門的外觀
        if door_type == "entrance":
            self.name = "大門"
            self.color = (139, 69, 19)  # 棕色
        else:
            self.name = "門"
            self.color = (160, 82, 45)  # 淺棕色

    def can_interact(self, player_position, max_distance=15):
        """
        檢查玩家是否可以與門互動\n
        \n
        參數:\n
        player_position (tuple): 玩家位置\n
        max_distance (float): 最大互動距離\n
        \n
        回傳:\n
        bool: 是否可以互動\n
        """
        px, py = player_position
        door_center_x = self.x + self.width // 2
        door_center_y = self.y + self.height // 2
        
        distance = ((px - door_center_x) ** 2 + (py - door_center_y) ** 2) ** 0.5
        return distance <= max_distance

    def interact(self, player):
        """
        與門互動 - 進出住宅\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 互動結果\n
        """
        if self.door_type == "entrance":
            # 主要入口的進出邏輯
            return {
                "success": True,
                "action": "toggle_interior_view",
                "message": "進出住宅",
                "door": self
            }
        else:
            # 其他門的開關邏輯
            self.is_open = not self.is_open
            state = "打開" if self.is_open else "關閉"
            return {
                "success": True,
                "message": f"{state}了{self.name}",
                "door_state": self.is_open
            }

    def draw(self, screen, house_world_x, house_world_y, camera_x, camera_y):
        """
        繪製門\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        house_world_x (int): 住宅的世界X座標\n
        house_world_y (int): 住宅的世界Y座標\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        # 計算門在世界座標系中的位置
        world_x = house_world_x + self.x
        world_y = house_world_y + self.y
        
        # 計算螢幕座標
        screen_x = world_x - camera_x
        screen_y = world_y - camera_y
        
        # 創建螢幕矩形
        screen_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        
        # 根據門的狀態選擇顏色
        if self.is_open:
            color = (101, 67, 33)  # 開門時較暗
        else:
            color = self.color
        
        # 繪製門
        pygame.draw.rect(screen, color, screen_rect)
        pygame.draw.rect(screen, (0, 0, 0), screen_rect, 1)
        
        # 繪製門把手
        handle_x = screen_x + self.width - 2
        handle_y = screen_y + self.height // 2
        pygame.draw.circle(screen, (255, 215, 0), (handle_x, handle_y), 1)


######################住宅內部管理器######################
class HouseInteriorManager:
    """
    住宅內部管理器 - 管理住宅內部的家具佈置和門系統\n
    \n
    負責：\n
    1. 自動生成家具佈置\n
    2. 管理門的位置和功能\n
    3. 處理住宅內部的互動\n
    4. 控制內部檢視的切換\n
    """

    def __init__(self):
        """
        初始化住宅內部管理器\n
        """
        # 家具佈置模板
        self.furniture_layouts = {
            "small_house": self._create_small_house_layout,
            "medium_house": self._create_medium_house_layout,
            "large_house": self._create_large_house_layout
        }
        
        print("住宅內部管理器初始化完成")

    def create_interior_for_house(self, house):
        """
        為住宅創建內部佈置\n
        \n
        參數:\n
        house (ResidentialHouse): 住宅建築物件\n
        \n
        回傳:\n
        dict: 包含家具和門的內部佈置\n
        """
        # 根據住宅大小選擇佈置模板
        house_area = house.width * house.height
        
        if house_area <= 40 * 40:  # 小住宅
            layout_type = "small_house"
        elif house_area <= 60 * 60:  # 中等住宅
            layout_type = "medium_house"
        else:  # 大住宅
            layout_type = "large_house"
        
        # 生成內部佈置
        interior = self.furniture_layouts[layout_type](house.width, house.height)
        
        # 為玩家之家添加特殊家具
        if hasattr(house, 'is_player_home') and house.is_player_home:
            interior = self._add_player_home_furniture(interior, house.width, house.height)
        
        return interior

    def _create_small_house_layout(self, width, height):
        """
        創建小住宅的內部佈置\n
        \n
        參數:\n
        width (int): 住宅寬度\n
        height (int): 住宅高度\n
        \n
        回傳:\n
        dict: 內部佈置\n
        """
        furniture_list = []
        door_list = []
        
        # 小住宅的基本家具（簡單佈置）
        # 床（放在右上角）
        bed = Furniture("bed", (width - 20, 5), (15, 10))
        furniture_list.append(bed)
        
        # 桌子（放在中央）
        table = Furniture("table", (width // 2 - 8, height // 2 - 5), (16, 10))
        furniture_list.append(table)
        
        # 椅子（放在桌子旁邊）
        chair = Furniture("chair", (width // 2 + 10, height // 2 - 3), (6, 6))
        furniture_list.append(chair)
        
        # 主要入口門（放在下方中央）
        entrance_door = Door((width // 2 - 4, height - 12), "entrance")
        door_list.append(entrance_door)
        
        return {
            "furniture": furniture_list,
            "doors": door_list,
            "layout_type": "small_house"
        }

    def _create_medium_house_layout(self, width, height):
        """
        創建中等住宅的內部佈置\n
        \n
        參數:\n
        width (int): 住宅寬度\n
        height (int): 住宅高度\n
        \n
        回傳:\n
        dict: 內部佈置\n
        """
        furniture_list = []
        door_list = []
        
        # 中等住宅的家具（較豐富的佈置）
        # 床（放在右上角）
        bed = Furniture("bed", (width - 25, 5), (20, 12))
        furniture_list.append(bed)
        
        # 沙發（放在左側）
        sofa = Furniture("sofa", (5, height // 2 - 8), (25, 12))
        furniture_list.append(sofa)
        
        # 桌子（放在中央）
        table = Furniture("table", (width // 2 - 10, height // 2 - 6), (20, 12))
        furniture_list.append(table)
        
        # 椅子（放在桌子周圍）
        chair1 = Furniture("chair", (width // 2 - 12, height // 2 + 8), (8, 6))
        chair2 = Furniture("chair", (width // 2 + 12, height // 2 + 8), (8, 6))
        furniture_list.extend([chair1, chair2])
        
        # 電視（放在左上角）
        tv = Furniture("tv", (5, 5), (15, 8))
        furniture_list.append(tv)
        
        # 主要入口門（放在下方中央）
        entrance_door = Door((width // 2 - 4, height - 12), "entrance")
        door_list.append(entrance_door)
        
        return {
            "furniture": furniture_list,
            "doors": door_list,
            "layout_type": "medium_house"
        }

    def _create_large_house_layout(self, width, height):
        """
        創建大住宅的內部佈置\n
        \n
        參數:\n
        width (int): 住宅寬度\n
        height (int): 住宅高度\n
        \n
        回傳:\n
        dict: 內部佈置\n
        """
        furniture_list = []
        door_list = []
        
        # 大住宅的家具（豪華佈置）
        # 臥室區域（右上角）
        bed = Furniture("bed", (width - 30, 5), (25, 15))
        wardrobe = Furniture("wardrobe", (width - 35, 25), (30, 12))
        furniture_list.extend([bed, wardrobe])
        
        # 客廳區域（左側）
        sofa = Furniture("sofa", (5, height // 2 - 10), (30, 15))
        tv = Furniture("tv", (40, height // 2 - 5), (20, 10))
        furniture_list.extend([sofa, tv])
        
        # 餐廳區域（中央）
        table = Furniture("table", (width // 2 - 12, height // 2 - 8), (24, 16))
        chair1 = Furniture("chair", (width // 2 - 15, height // 2 + 10), (8, 6))
        chair2 = Furniture("chair", (width // 2, height // 2 + 10), (8, 6))
        chair3 = Furniture("chair", (width // 2 + 15, height // 2 + 10), (8, 6))
        furniture_list.extend([table, chair1, chair2, chair3])
        
        # 廚房區域（左下角）
        kitchen = Furniture("kitchen", (5, height - 25), (25, 20))
        furniture_list.append(kitchen)
        
        # 書房區域（右下角）
        bookshelf = Furniture("bookshelf", (width - 25, height - 20), (20, 15))
        furniture_list.append(bookshelf)
        
        # 主要入口門（放在下方中央）
        entrance_door = Door((width // 2 - 4, height - 12), "entrance")
        door_list.append(entrance_door)
        
        return {
            "furniture": furniture_list,
            "doors": door_list,
            "layout_type": "large_house"
        }

    def _add_player_home_furniture(self, interior, width, height):
        """
        為玩家之家添加特殊家具\n
        \n
        參數:\n
        interior (dict): 基本內部佈置\n
        width (int): 住宅寬度\n
        height (int): 住宅高度\n
        \n
        回傳:\n
        dict: 增強的內部佈置\n
        """
        # 為玩家之家添加額外的特殊家具
        # 個人衣櫃（如果還沒有的話）
        has_wardrobe = any(f.furniture_type == "wardrobe" for f in interior["furniture"])
        if not has_wardrobe:
            wardrobe = Furniture("wardrobe", (width - 20, height - 30), (15, 25))
            interior["furniture"].append(wardrobe)
        
        # 個人書櫃（增加學習功能）
        has_bookshelf = any(f.furniture_type == "bookshelf" for f in interior["furniture"])
        if not has_bookshelf:
            bookshelf = Furniture("bookshelf", (5, height - 20), (15, 15))
            interior["furniture"].append(bookshelf)
        
        return interior

    def get_interactive_objects_near_player(self, interior, player_position, max_distance=20):
        """
        獲取玩家附近可互動的物件\n
        \n
        參數:\n
        interior (dict): 住宅內部佈置\n
        player_position (tuple): 玩家在住宅內的位置\n
        max_distance (float): 最大互動距離\n
        \n
        回傳:\n
        list: 可互動的物件列表\n
        """
        interactive_objects = []
        
        # 檢查家具
        for furniture in interior["furniture"]:
            if furniture.can_interact(player_position, max_distance):
                interactive_objects.append({
                    "type": "furniture",
                    "object": furniture,
                    "name": furniture.name,
                    "interaction_text": furniture.interaction_text
                })
        
        # 檢查門
        for door in interior["doors"]:
            if door.can_interact(player_position, max_distance):
                interactive_objects.append({
                    "type": "door",
                    "object": door,
                    "name": door.name,
                    "interaction_text": "進出"
                })
        
        return interactive_objects

    def draw_interior(self, screen, interior, house_world_x, house_world_y, camera_x, camera_y):
        """
        繪製住宅內部\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        interior (dict): 住宅內部佈置\n
        house_world_x (int): 住宅的世界X座標\n
        house_world_y (int): 住宅的世界Y座標\n
        camera_x (float): 攝影機X偏移\n
        camera_y (float): 攝影機Y偏移\n
        """
        # 繪製家具
        for furniture in interior["furniture"]:
            furniture.draw(screen, house_world_x, house_world_y, camera_x, camera_y)
        
        # 繪製門
        for door in interior["doors"]:
            door.draw(screen, house_world_x, house_world_y, camera_x, camera_y)