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

######################小鎮地圖設定######################
# 小鎮總尺寸設定 - 30x30 街道的大型小鎮（足夠容納330個住宅）
TOWN_GRID_WIDTH = 30  # 橫向街區數量
TOWN_GRID_HEIGHT = 30  # 縱向街區數量 
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
# 玩家角色的移動速度，單位為像素/幀（已優化）
PLAYER_SPEED = 4  # 提升移動速度以改善操控感

# 玩家角色的尺寸 - 寬度
PLAYER_WIDTH = 32

# 玩家角色的尺寸 - 高度
PLAYER_HEIGHT = 32

# 玩家初始位置 X 座標
PLAYER_START_X = SCREEN_WIDTH // 2

# 玩家初始位置 Y 座標
PLAYER_START_Y = SCREEN_HEIGHT // 2

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

######################地圖尺寸設定######################
# 森林地圖尺寸（小鎮的8倍大）
FOREST_MAP_WIDTH = TOWN_TOTAL_WIDTH * 8
FOREST_MAP_HEIGHT = TOWN_TOTAL_HEIGHT * 8

# 湖泊地圖尺寸（小鎮的10倍大）
LAKE_MAP_WIDTH = TOWN_TOTAL_WIDTH * 10
LAKE_MAP_HEIGHT = TOWN_TOTAL_HEIGHT * 10

######################遊戲系統設定######################
# 初始金錢數量
INITIAL_MONEY = 1000

# 物品欄設定（替代背包系統）
ITEM_BAR_SLOTS = 10  # 物品欄格子數量
ITEM_BAR_HEIGHT = 60  # 物品欄高度
ITEM_BAR_SLOT_SIZE = 50  # 每個格子的大小
ITEM_BAR_PADDING = 5  # 格子間的間距

# 自動存檔間隔時間，單位為秒
AUTO_SAVE_INTERVAL = 300

######################釣魚系統設定######################
# 釣魚成功的基礎機率 (0.0 到 1.0)
FISHING_BASE_SUCCESS_RATE = 0.3

# 釣魚動作需要的時間，單位為秒
FISHING_TIME = 3.0

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

# 玩家初始生命值
PLAYER_MAX_HEALTH = 100
PLAYER_INITIAL_HEALTH = 100

######################建築物數量設定######################
# 住宅建築 (為330個NPC提供住所)
HOUSE_COUNT = 330  # 住宅數量 - 一個NPC一間房

# 宗教建築
CHURCH_COUNT = 5  # 教堂數量 (增加)
PRIEST_COUNT = 2  # 牧師數量
NUN_COUNT = 48  # 修女數量

# 商業建築 (增加數量以配合大地圖)
CONVENIENCE_STORE_COUNT = 25  # 便利商店數量 (增加)
STREET_VENDOR_COUNT = 15  # 路邊小販數量 (增加)
FISHING_SHOP_COUNT = 3  # 釣魚店數量 (增加)
MARKET_COUNT = 2  # 市場數量 (增加)

# 醫療建築
HOSPITAL_COUNT = 8  # 醫院數量 (增加)

# 教育和娛樂建築
SCHOOL_COUNT = 6  # 學校數量 (增加)
PARK_COUNT = 20  # 公園數量 (增加，避免空地)

# 金融建築
BANK_COUNT = 4  # 銀行數量 (增加)

# 其他商業建築
CLOTHING_STORE_COUNT = 15  # 服裝店數量 (增加)
TAVERN_COUNT = 12  # 酒館數量 (增加)
GUN_SHOP_COUNT = 10  # 槍械店數量
OFFICE_BUILDING_COUNT = 25  # 辦公大樓數量 (增加)

# 基礎設施
POWER_PLANT_COUNT = 1  # 電力場數量
FARM_AREA_COUNT = 5  # 農田區域數量

######################NPC職業分配設定######################
# 總NPC數量
TOTAL_TOWN_NPCS = 330
TOTAL_TRIBE_NPCS = 100

# 小鎮NPC職業分配
FARMER_COUNT = 100  # 農夫
DOCTOR_COUNT = 10  # 醫生
NURSE_COUNT = 40  # 護士
GUN_SHOP_STAFF_COUNT = 20  # 槍械店員工
VENDOR_COUNT = 10  # 路邊小販
FISHING_SHOP_STAFF_COUNT = 20  # 釣魚店員工
CONVENIENCE_STAFF_COUNT = 30  # 便利商店員工
POWER_WORKER_COUNT = 30  # 電力系統員工
HUNTER_COUNT = 20  # 獵人

######################載具系統設定######################
# 載具移動速度，單位為像素/幀
VEHICLE_SPEED = 6

# 載具尺寸 - 寬度
VEHICLE_WIDTH = 64

# 載具尺寸 - 高度
VEHICLE_HEIGHT = 32

# 載具顏色設定
CAR_COLOR = (255, 0, 0)  # 汽車 - 紅色
BIKE_COLOR = (0, 255, 0)  # 自行車 - 綠色

######################法律系統設定######################
# 危險區域設定
WATER_DANGER_TIME = 60.0  # 在水中停留多久會被食人魚攻擊 (秒)

######################服裝系統設定######################
# 服裝類型數量
CLOTHING_TYPES = 20

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

######################載具系統設定######################
# 載具移動速度，單位為像素/幀
VEHICLE_SPEED = 6

# 載具尺寸 - 寬度
VEHICLE_WIDTH = 64

# 載具尺寸 - 高度
VEHICLE_HEIGHT = 32

# 載具顏色
CAR_COLOR = (255, 0, 0)  # 紅色汽車
BIKE_COLOR = (0, 150, 0)  # 綠色自行車
TRUCK_COLOR = (139, 69, 19)  # 棕色卡車
BUS_COLOR = (0, 100, 200)  # 藍色公車

# AI 載具生成設定
MAX_AI_VEHICLES = 20  # 最大 AI 載具數量
AI_SPAWN_INTERVAL = 5.0  # AI 載具生成間隔（秒）
AI_DESPAWN_DISTANCE = 200  # AI 載具消失距離

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
