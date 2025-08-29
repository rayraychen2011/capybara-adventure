######################遊戲基本設定######################
"""
小鎮生活模擬器 - 遊戲設定檔\n
\n
此檔案包含遊戲的所有核心設定參數，包括：\n
- 視窗尺寸和顯示設定\n
- 遊戲效能參數\n
- 色彩定義\n
- 玩家角色基本參數\n
- 各系統的基礎設定\n
\n
修改此檔案可以調整遊戲的基本行為和外觀\n
"""

######################視窗與顯示設定######################
# 遊戲視窗的寬度，單位為像素
SCREEN_WIDTH = 1024

# 遊戲視窗的高度，單位為像素
SCREEN_HEIGHT = 768

# 遊戲標題，會顯示在視窗標題列
GAME_TITLE = "小鎮生活模擬器"

# 遊戲每秒幀數，控制遊戲更新和畫面刷新的速度
FPS = 60

# 全域縮放係數 - 根據需求將所有東西放大十倍顯示在螢幕上
GLOBAL_SCALE = 10.0

######################小鎮地圖設定######################
# 小鎮總尺寸設定 - 100x100 格子的超大型地圖（支援更豐富的遊戲內容）
TOWN_GRID_WIDTH = 100  # 橫向街區數量
TOWN_GRID_HEIGHT = 100  # 縱向街區數量 
STREET_WIDTH = 50  # 每條街道的寬度（像素）
BLOCK_SIZE = 150  # 每個街區的大小（像素）

# 街區內建築物設定
BUILDINGS_PER_BLOCK = 3  # 每個街區最少建築物數量
MAX_BUILDINGS_PER_BLOCK = 4  # 每個街區最多建築物數量
BUILDING_MARGIN = 12  # 建築物邊距

# 計算小鎮總尺寸
TOWN_TOTAL_WIDTH = TOWN_GRID_WIDTH * (BLOCK_SIZE + STREET_WIDTH)
TOWN_TOTAL_HEIGHT = TOWN_GRID_HEIGHT * (BLOCK_SIZE + STREET_WIDTH)

# 城牆設定
WALL_THICKNESS = 25  # 城牆厚度
WALL_COLOR = (101, 67, 33)  # 城牆顏色 - 深棕色

# 攝影機/視窗在小鎮中的起始位置
CAMERA_START_X = TOWN_TOTAL_WIDTH // 2 - SCREEN_WIDTH // 2
CAMERA_START_Y = TOWN_TOTAL_HEIGHT // 2 - SCREEN_HEIGHT // 2

######################世界座標系統設定######################
# 家的位置作為世界原點 (0, 0)
HOME_WORLD_X = TOWN_TOTAL_WIDTH // 2
HOME_WORLD_Y = TOWN_TOTAL_HEIGHT // 2

######################色彩定義######################
# 背景色彩 - 天空藍
BACKGROUND_COLOR = (135, 206, 235)

# 玩家角色顏色 - 橘色
PLAYER_COLOR = (255, 165, 0)

# 文字顏色 - 白色
TEXT_COLOR = (255, 255, 255)

# UI 背景色 - 半透明黑色
UI_BACKGROUND_COLOR = (0, 0, 0, 128)

# 建築物顏色 - 棕色
BUILDING_COLOR = (139, 69, 19)

# 道路顏色 - 深灰色
ROAD_COLOR = (105, 105, 105)

# 草地顏色 - 綠色
GRASS_COLOR = (34, 139, 34)

# 水面顏色 - 藍色
WATER_COLOR = (0, 191, 255)

######################玩家角色設定######################
# 玩家角色的移動速度，單位為像素/幀
PLAYER_SPEED = 200.0  # 調整為合適的移動速度（每秒移動像素數）

# 玩家奔跑速度（Shift 鍵加速）
PLAYER_RUN_SPEED = 300.0  # 奔跑時的移動速度

# 載具移動速度（玩家和 NPC 使用載具時的速度）
VEHICLE_SPEED = 400.0  # 載具移動速度（像素/秒）

# 玩家角色的尺寸 - 寬度（縮小為原來的1/4以配合建築系統）
PLAYER_WIDTH = 8

# 玩家角色的尺寸 - 高度（縮小為原來的1/4以配合建築系統）
PLAYER_HEIGHT = 8

# 玩家初始位置 X 座標
PLAYER_START_X = SCREEN_WIDTH // 2

# 玩家初始位置 Y 座標
PLAYER_START_Y = SCREEN_HEIGHT // 2

######################地圖格系統設定######################
# 一格大小為玩家的 216 倍（更新後為合理尺寸）
GRID_SIZE = PLAYER_WIDTH * 216  # 8 * 216 = 1728 像素

# 住宅建築規則 - 住宅為玩家的5倍長寬
RESIDENTIAL_MIN_SIZE = PLAYER_WIDTH * 5  # 住宅寬度 = 玩家的 5 倍 = 40 像素
RESIDENTIAL_HEIGHT = PLAYER_HEIGHT * 5  # 住宅高度 = 玩家的 5 倍 = 40 像素
RESIDENTIAL_MAX_PER_GRID = 6  # 每格最多 6 個住宅
RESIDENTIAL_SPACING = 5  # 住宅之間的通行間隙（調整為較小間距）

# 商業建築規則  
COMMERCIAL_MIN_SIZE = PLAYER_WIDTH * 7  # 玩家的 7 倍 = 56 像素
COMMERCIAL_MAX_PER_GRID = 4  # 每格最多 4 個商業建築
COMMERCIAL_SPACING = 8  # 商業建築之間的間隙（調整為較小間距）

######################小地圖設定######################
# 小地圖基本設定
MINIMAP_WIDTH = 300  # 小地圖寬度
MINIMAP_HEIGHT = 300  # 小地圖高度
MINIMAP_BACKGROUND_COLOR = (0, 0, 0, 180)  # 半透明黑色背景
MINIMAP_BORDER_COLOR = (255, 255, 255)  # 白色邊框

# 小地圖位置 (螢幕右上角，適應新螢幕尺寸 1024x768)
MINIMAP_X = SCREEN_WIDTH - MINIMAP_WIDTH - 20
MINIMAP_Y = 20

# 小地圖縮放設定
MINIMAP_MIN_ZOOM = 0.1  # 最小縮放比例 (10%)
MINIMAP_MAX_ZOOM = 2.0  # 最大縮放比例 (200%)
MINIMAP_DEFAULT_ZOOM = 0.5  # 預設縮放比例 (50%)
MINIMAP_ZOOM_STEP = 0.1  # 每次縮放步進

# 玩家在小地圖上的標示（配合縮小的玩家尺寸）
MINIMAP_PLAYER_SIZE = 4  # 玩家三角形的大小（縮小）
MINIMAP_PLAYER_COLOR = (255, 0, 0)  # 紅色玩家標示

######################效能優化設定######################
# 碰撞檢測優化距離（像素）
COLLISION_CHECK_DISTANCE = 100

# NPC 更新距離分級
NPC_NEAR_DISTANCE = 300  # 完整更新距離
NPC_MEDIUM_DISTANCE = 600  # 簡化更新距離
NPC_FAR_DISTANCE = 1000  # 最簡化更新距離

# 系統更新頻率優化
TIME_SYSTEM_UPDATE_INTERVAL = 2  # 每2幀更新一次時間系統
POWER_SYSTEM_UPDATE_INTERVAL = 3  # 每3幀更新一次電力系統
UI_UPDATE_INTERVAL = 4  # 每4幀更新一次UI

######################場景設定######################
# 場景切換區域的檢測範圍，單位為像素
SCENE_TRANSITION_DISTANCE = 50

# 場景類型列舉
SCENE_TOWN = "town"
SCENE_FOREST = "forest"
SCENE_LAKE = "lake"
SCENE_HOME = "home"


######################遊戲系統設定######################
# 初始金錢數量
INITIAL_MONEY = 500  # 根據新需求設定初始金錢為 500 元

# 物品欄設定（替代背包系統）
ITEM_BAR_SLOTS = 10  # 物品欄格子數量
ITEM_BAR_HEIGHT = 60  # 物品欄高度
ITEM_BAR_SLOT_SIZE = 50  # 每個格子的大小
ITEM_BAR_PADDING = 5  # 格子間的間距

# 自動存檔間隔時間，單位為秒
AUTO_SAVE_INTERVAL = 300

######################建築限制設定######################
# 住宅數量限制
MAX_RESIDENTIAL_BUILDINGS = 100  # 城鎮最多只能有 100 棟住宅

# 蔬果園設定
VEGETABLE_GARDEN_HARVEST_INCOME = 10  # 採摘 1 格蔬果園可獲得 10 元
VEGETABLE_GARDEN_DAILY_GROWTH = True  # 蔬果園每天成熟一次

# 服裝店設定
CLOTHING_STORE_OUTFIT_COUNT = 5  # 服裝店提供 5 套套裝
CLOTHING_OUTFIT_PRICE = 300  # 每套套裝價格為 300 元

# 路邊小販設定
STREET_VENDOR_COUNT = 1  # 地圖上有 1 位路邊小販 NPC

######################鐵路系統設定######################
# 火車站設定
TRAIN_STATION_COUNT = 10  # 火車站數量
TRAIN_SPEED = 400.0  # 火車移動速度（像素/秒）
TRAIN_CAPACITY = 50  # 火車載客容量

# 鐵軌設定
RAILWAY_TRACK_WIDTH = 8  # 鐵軌寬度
RAILWAY_SIGNAL_INTERVAL = 200  # 交通號誌間隔距離

# 火車顏色設定
TRAIN_COLOR = (139, 69, 19)  # 棕色火車
RAILWAY_COLOR = (101, 67, 33)  # 深棕色鐵軌
TRAIN_STATION_COLOR = (139, 0, 0)  # 深紅色火車站

# 血量藥水設定
HEALTH_POTIONS = {
    "小型血量藥水": {"price": 50, "heal_amount": 50},
    "中型血量藥水": {"price": 150, "heal_amount": 150},
    "大型血量藥水": {"price": 300, "heal_amount": 300}
}

######################槍械系統設定######################
# 槍械射程，單位為像素
GUN_RANGE = 200

# 子彈速度，單位為像素/幀
BULLET_SPEED = 10

# 初始武器設定
INITIAL_WEAPON = "手槍"
INITIAL_AMMO = 50

# 槍械商店設定
GUN_SHOP_COUNT = 10  # 槍械店數量

######################死亡和重生系統設定######################
# 醫院數量
HOSPITAL_COUNT = 5

# 玩家初始生命值（根據新需求）
PLAYER_MAX_HEALTH = 1000  # 最高血量
PLAYER_INITIAL_HEALTH = 300  # 預設血量

# 血量相關設定
HEALTH_LOW_THRESHOLD = 100  # 血量低於此值時播放心跳聲並自動回復
HEALTH_AUTO_RECOVERY_RATE = 1  # 自動回復速度（每秒回復1點）

######################建築物數量設定######################
# 住宅建築 (依據新需求：總共100個房子，25個住宅區)
HOUSES_PER_RESIDENTIAL_GRID = 4  # 每個住宅區格子放4個住宅單位
RESIDENTIAL_GRID_COUNT = 25  # 住宅區格子數量
TOTAL_HOUSES = 100  # 總住宅數量 - 固定為100個房子

# 宗教建築
CHURCH_COUNT = 2  # 教堂數量
PRIEST_COUNT = 2  # 牧師數量
NUN_COUNT = 8  # 修女數量

# 商業建築 (減少數量以配合較小地圖)
CONVENIENCE_STORE_COUNT = 8  # 便利商店數量
STREET_VENDOR_COUNT = 5  # 路邊小販數量
MARKET_COUNT = 1  # 市場數量

# 醫療建築
HOSPITAL_COUNT = 3  # 醫院數量

# 教育和娛樂建築
SCHOOL_COUNT = 2  # 學校數量
PARK_COUNT = 5  # 公園數量

# 金融建築
BANK_COUNT = 2  # 銀行數量

# 其他商業建築
CLOTHING_STORE_COUNT = 5  # 服裝店數量
GUN_SHOP_COUNT = 3  # 槍械店數量
OFFICE_BUILDING_COUNT = 8  # 辦公大樓數量

# 基礎設施
POWER_PLANT_COUNT = 1  # 電力場數量
FARM_AREA_COUNT = 5  # 農田區域數量

# 蔬果園設定（新增）
VEGETABLE_GARDEN_COUNT = 10  # 蔬果園數量
VEGETABLE_GARDEN_COLOR = (50, 205, 50)  # 蔬果園顏色 - 綠色

######################NPC職業分配設定######################
# 總NPC數量（依據新需求：99個NPC）
TOTAL_TOWN_NPCS = 99  # 固定為99個NPC
TOTAL_TRIBE_NPCS = 0  # 刪除部落NPC（依據需求）

# 小鎮NPC職業分配（根據農夫工作需求重新分配）
# 每個住宅最多3個NPC（家庭成員）
NPCS_PER_HOUSE = 3  # 每個住宅的NPC數量
FARMER_COUNT = 50  # 農夫（50名工作在火車站1旁農地）
DOCTOR_COUNT = 0  # 醫生（暫停其他職業）
NURSE_COUNT = 0  # 護士（暫停其他職業）
GUN_SHOP_STAFF_COUNT = 0  # 槍械店員工（暫停其他職業）
VENDOR_COUNT = 0  # 路邊小販（暫停其他職業）
STREET_VENDOR_COUNT = VENDOR_COUNT  # 為了相容性保留兩個名稱
CONVENIENCE_STAFF_COUNT = 0  # 便利商店員工（暫停其他職業）
CHEF_COUNT = 0  # 廚師（暫停其他職業）
TEACHER_COUNT = 0  # 教師（暫停其他職業）
HUNTER_COUNT = 0  # 獵人（暫停其他職業）
ARTIST_COUNT = 0  # 藝術家（暫停其他職業）
# 其他職業：49名無職業NPC在鎮上閒晃
OTHER_PROFESSIONS_COUNT = 49  # 無職業一般居民

######################NPC移動設定######################
# NPC 移動速度 - 與玩家移動速度相同
NPC_SPEED = PLAYER_SPEED  # NPC 和玩家使用相同的移動速度

# NPC 車輛使用設定
NPC_COMMUTE_DISTANCE_THRESHOLD = 200  # NPC 工作場所距離超過此值時會使用車輛




######################服裝系統設定######################
# 服裝類型數量
CLOTHING_TYPES = 5

# 服裝顏色變化
CLOTHING_COLORS = [
    (255, 165, 0),  # 橘色 (預設)
    (255, 0, 0),  # 紅色
    (0, 255, 0),  # 綠色
    (0, 0, 255),  # 藍色
    (255, 255, 0),  # 黃色
    (255, 0, 255),  # 紫色
    (0, 255, 255),  # 青色
    (128, 128, 128),  # 灰色
]



######################天氣系統設定######################
# 天氣類型和對應的特效設定
WEATHER_TYPES = {
    "☀️ 晴朗": {
        "sky_color_modifier": (1.0, 1.0, 1.0),  # 無色彩修正
        "light_modifier": 1.0,  # 正常光線
        "particles": None,  # 無粒子特效
        "sound": None,  # 無環境音效
        "visibility": 1.0,  # 正常能見度
    },
    "⛅ 多雲": {
        "sky_color_modifier": (0.9, 0.9, 0.95),  # 稍微偏灰
        "light_modifier": 0.8,  # 稍微暗一點
        "particles": None,  # 無粒子特效
        "sound": None,  # 無環境音效
        "visibility": 0.95,  # 稍微降低能見度
    },
    "☁️ 陰天": {
        "sky_color_modifier": (0.7, 0.7, 0.8),  # 灰藍色調
        "light_modifier": 0.6,  # 較暗
        "particles": None,  # 無粒子特效
        "sound": None,  # 無環境音效
        "visibility": 0.8,  # 降低能見度
    },
    "🌧️ 小雨": {
        "sky_color_modifier": (0.6, 0.6, 0.7),  # 深灰藍色
        "light_modifier": 0.5,  # 較暗
        "particles": "light_rain",  # 小雨粒子
        "sound": "light_rain",  # 小雨音效
        "visibility": 0.7,  # 明顯降低能見度
    },
    "⛈️ 雷雨": {
        "sky_color_modifier": (0.4, 0.4, 0.5),  # 很暗的灰色
        "light_modifier": 0.3,  # 很暗
        "particles": "heavy_rain",  # 大雨粒子
        "sound": "thunder_rain",  # 雷雨音效
        "visibility": 0.5,  # 大幅降低能見度
        "lightning": True,  # 閃電效果
    },
    "🌨️ 下雪": {
        "sky_color_modifier": (0.9, 0.9, 1.0),  # 冷色調白
        "light_modifier": 0.7,  # 稍暗但較亮
        "particles": "snow",  # 雪花粒子
        "sound": "wind",  # 風聲
        "visibility": 0.6,  # 降低能見度
    }
}

# 天氣特效粒子設定
RAIN_PARTICLE_COUNT = 200  # 雨滴數量
SNOW_PARTICLE_COUNT = 150  # 雪花數量
RAIN_PARTICLE_SPEED = 400  # 雨滴下落速度（像素/秒）
SNOW_PARTICLE_SPEED = 100  # 雪花下落速度（像素/秒）
RAIN_PARTICLE_COLOR = (200, 200, 255)  # 雨滴顏色（淺藍白）
SNOW_PARTICLE_COLOR = (255, 255, 255)  # 雪花顏色（白色）

# 閃電效果設定
LIGHTNING_DURATION = 0.2  # 閃電持續時間（秒）
LIGHTNING_INTERVAL_MIN = 3.0  # 最短閃電間隔（秒）
LIGHTNING_INTERVAL_MAX = 8.0  # 最長閃電間隔（秒）
LIGHTNING_BRIGHTNESS = 0.8  # 閃電亮度加成

# 霧效設定
FOG_ALPHA = 100  # 霧的透明度（0-255）
FOG_COLOR = (200, 200, 200)  # 霧的顏色（淺灰）

######################字體設定######################
# 預設字體大小
DEFAULT_FONT_SIZE = 24

# 小字體大小
SMALL_FONT_SIZE = 18

# 大字體大小
LARGE_FONT_SIZE = 32

# UI 字體大小
UI_FONT_SIZE = 20

# 標題字體大小
TITLE_FONT_SIZE = 36

# 繁體中文字體路徑清單 (按優先順序)
CHINESE_FONTS = [
    "C:/Windows/Fonts/msjh.ttc",  # 微軟正黑體
    "C:/Windows/Fonts/kaiu.ttf",  # 標楷體
    "C:/Windows/Fonts/mingliu.ttc",  # 細明體
    "C:/Windows/Fonts/simhei.ttf",  # 黑體
    None,  # 預設字體 (Fallback)
]
