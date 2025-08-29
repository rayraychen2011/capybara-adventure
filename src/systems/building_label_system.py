######################載入套件######################
import pygame
from config.settings import *
from src.utils.font_manager import get_font_manager


######################建築標示系統######################
class BuildingLabelSystem:
    """
    建築標示系統 - 顯示建築物上方的名稱標籤\n
    \n
    功能：\n
    - 商業區建築顯示建築名稱（中文）\n
    - 住宅區建築顯示「家」\n
    - 自動根據建築類型顯示適當標籤\n
    """

    def __init__(self):
        """
        初始化建築標示系統\n
        """
        self.font_manager = get_font_manager()
        
        # 標籤樣式設定
        self.font_size = 14
        self.text_color = (255, 255, 255)  # 白色文字
        self.background_color = (0, 0, 0, 128)  # 半透明黑色背景
        self.padding = 4  # 文字周圍的填充
        
        # 商業建築名稱映射
        self.commercial_names = {
            "convenience_store": "便利商店",
            "gun_shop": "槍械店",
            "clothing_store": "服裝店",
            "restaurant": "餐廳",
            "bank": "銀行",
            "hospital": "醫院",
            "school": "學校",
            "office": "辦公大樓",
            "shop": "商店",
            "market": "市場",
            "pharmacy": "藥局",
            "bookstore": "書店",
            "cafe": "咖啡廳",
            "bakery": "麵包店",
            "barber": "理髮店"
        }
        
        # 住宅標籤
        self.residential_label = "家"
        
        print("建築標示系統初始化完成")

    def get_building_label(self, building):
        """
        獲取建築的標籤文字\n
        \n
        只為住宅建築顯示「家」標籤，其他建築不顯示\n
        \n
        參數:\n
        building: 建築物件\n
        \n
        回傳:\n
        str: 標籤文字或None\n
        """
        # 只為住宅建築顯示「家」標籤
        if hasattr(building, 'building_type') and building.building_type == "house":
            return self.residential_label
        
        # 其他建築不顯示標籤
        return None

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製建築標籤（主繪製方法）\n
        \n
        這個方法被TownScene調用，需要與地形系統整合\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (int): 攝影機X偏移\n
        camera_y (int): 攝影機Y偏移\n
        """
        # 這個方法將由TownScene調用，並傳入建築列表
        # 目前先不做任何事，等待進一步整合
        pass

    def draw_building_label(self, screen, building, camera_x=0, camera_y=0):
        """
        繪製單個建築的標籤\n
        \n
        只為住宅建築繪製「家」標籤\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        building: 建築物件\n
        camera_x (int): 攝影機X偏移\n
        camera_y (int): 攝影機Y偏移\n
        """
        # 獲取建築標籤
        label = self.get_building_label(building)
        if not label:
            return
        
        # 計算標籤位置（建築物上方）
        label_x = building.x - camera_x + building.width // 2
        label_y = building.y - camera_y - 10  # 在建築物上方10像素
        
        # 獲取字體
        font = self.font_manager.get_font(self.font_size)
        
        # 渲染文字
        text_surface = font.render(label, True, self.text_color)
        text_rect = text_surface.get_rect()
        
        # 置中對齊
        text_rect.centerx = label_x
        text_rect.bottom = label_y
        
        # 檢查是否在螢幕範圍內
        screen_rect = screen.get_rect()
        if text_rect.colliderect(screen_rect):
            # 繪製半透明背景
            background_rect = text_rect.inflate(self.padding * 2, self.padding * 2)
            background_surface = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
            background_surface.fill(self.background_color)
            screen.blit(background_surface, background_rect)
            
            # 繪製文字
            screen.blit(text_surface, text_rect)

    def draw_all_building_labels(self, screen, buildings, camera_x=0, camera_y=0):
        """
        繪製所有建築的標籤\n
        \n
        只為住宅建築繪製「家」標籤\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        buildings (list): 建築物件列表\n
        camera_x (int): 攝影機X偏移\n
        camera_y (int): 攝影機Y偏移\n
        """
        for building in buildings:
            self.draw_building_label(screen, building, camera_x, camera_y)

    def add_commercial_name(self, shop_type, chinese_name):
        """
        添加商業建築名稱映射\n
        \n
        參數:\n
        shop_type (str): 商店類型\n
        chinese_name (str): 中文名稱\n
        """
        self.commercial_names[shop_type] = chinese_name

    def is_building_visible(self, building, camera_x, camera_y):
        """
        檢查建築是否在螢幕可見範圍內\n
        \n
        參數:\n
        building: 建築物件\n
        camera_x (int): 攝影機X偏移\n
        camera_y (int): 攝影機Y偏移\n
        \n
        回傳:\n
        bool: 是否可見\n
        """
        building_x = building.x - camera_x
        building_y = building.y - camera_y
        building_width = getattr(building, 'width', 60)
        building_height = getattr(building, 'height', 40)
        
        # 擴大檢測範圍，包含標籤區域
        margin = 50
        
        return not (building_x + building_width < -margin or 
                   building_x > SCREEN_WIDTH + margin or
                   building_y + building_height < -margin or 
                   building_y > SCREEN_HEIGHT + margin)

    def update_building_type(self, building, building_type):
        """
        更新建築類型\n
        \n
        參數:\n
        building: 建築物件\n
        building_type (str): 新的建築類型\n
        """
        building.building_type = building_type

    def set_custom_label(self, building, label):
        """
        為建築設定自定義標籤\n
        \n
        參數:\n
        building: 建築物件\n
        label (str): 自定義標籤\n
        """
        building.custom_label = label

    def get_custom_label(self, building):
        """
        獲取建築的自定義標籤\n
        \n
        參數:\n
        building: 建築物件\n
        \n
        回傳:\n
        str: 自定義標籤，如果沒有則返回None\n
        """
        return getattr(building, 'custom_label', None)


######################建築類型檢測器######################
class BuildingTypeDetector:
    """
    建築類型檢測器 - 自動識別建築類型\n
    \n
    根據建築的屬性和類別名稱自動判斷建築類型\n
    """

    def __init__(self):
        """
        初始化建築類型檢測器\n
        """
        # 住宅類型關鍵字
        self.residential_keywords = [
            'house', 'home', 'residential', 'apartment', 'condo'
        ]
        
        # 商業類型關鍵字
        self.commercial_keywords = [
            'shop', 'store', 'market', 'commercial', 'business',
            'office', 'restaurant', 'cafe', 'bank', 'hospital'
        ]

    def detect_building_type(self, building):
        """
        檢測建築類型\n
        \n
        參數:\n
        building: 建築物件\n
        \n
        回傳:\n
        str: 建築類型 ('residential', 'commercial', 'unknown')\n
        """
        # 首先檢查是否已經有明確的building_type屬性
        if hasattr(building, 'building_type'):
            return building.building_type
        
        # 檢查類別名稱
        class_name = building.__class__.__name__.lower()
        
        # 檢查是否是住宅
        for keyword in self.residential_keywords:
            if keyword in class_name:
                return 'residential'
        
        # 檢查是否是商業建築
        for keyword in self.commercial_keywords:
            if keyword in class_name:
                return 'commercial'
        
        # 檢查特殊屬性
        if hasattr(building, 'shop_type') or hasattr(building, 'shop_name'):
            return 'commercial'
        
        if hasattr(building, 'is_player_home'):
            return 'residential'
        
        return 'unknown'

    def auto_assign_building_types(self, buildings):
        """
        自動為建築列表分配類型\n
        \n
        參數:\n
        buildings (list): 建築物件列表\n
        """
        for building in buildings:
            if not hasattr(building, 'building_type'):
                detected_type = self.detect_building_type(building)
                building.building_type = detected_type