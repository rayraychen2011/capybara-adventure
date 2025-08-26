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
PLAYER_SPEED = 3

# 玩家角色的尺寸 - 寬度
PLAYER_WIDTH = 32

# 玩家角色的尺寸 - 高度
PLAYER_HEIGHT = 32

# 玩家初始位置 X 座標
PLAYER_START_X = SCREEN_WIDTH // 2

# 玩家初始位置 Y 座標
PLAYER_START_Y = SCREEN_HEIGHT // 2

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
INITIAL_MONEY = 1000

# 背包初始容量
INVENTORY_CAPACITY = 20

# 自動存檔間隔時間，單位為秒
AUTO_SAVE_INTERVAL = 300

######################釣魚系統設定######################
# 釣魚成功的基礎機率 (0.0 到 1.0)
FISHING_BASE_SUCCESS_RATE = 0.3

# 釣魚動作需要的時間，單位為秒
FISHING_TIME = 3.0

######################狩獵系統設定######################
# 槍械射程，單位為像素
GUN_RANGE = 200

# 子彈速度，單位為像素/幀
BULLET_SPEED = 10

######################載具系統設定######################
# 載具移動速度，單位為像素/幀
VEHICLE_SPEED = 6

# 載具尺寸 - 寬度
VEHICLE_WIDTH = 64

# 載具尺寸 - 高度
VEHICLE_HEIGHT = 32

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
    "C:/Windows/Fonts/msjh.ttc",      # 微軟正黑體
    "C:/Windows/Fonts/kaiu.ttf",      # 標楷體  
    "C:/Windows/Fonts/mingliu.ttc",   # 細明體
    "C:/Windows/Fonts/simhei.ttf",    # 黑體
    None  # 預設字體 (Fallback)
]