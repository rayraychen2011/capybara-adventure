######################載入套件######################
import math
import pygame


######################數學工具函式######################
def calculate_distance(pos1, pos2):
    """
    計算兩點之間的直線距離 - 基於歐幾里得距離公式\n
    \n
    使用勾股定理計算兩個座標點之間的直線距離\n
    常用於碰撞檢測、移動計算、互動範圍判定等功能\n
    \n
    參數:\n
    pos1 (tuple): 第一個點的座標 (x, y)\n
    pos2 (tuple): 第二個點的座標 (x, y)\n
    \n
    回傳:\n
    float: 兩點間的直線距離，單位為像素\n
    \n
    數學公式:\n
    distance = √[(x2-x1)² + (y2-y1)²]\n
    """
    # 計算 X 軸方向的距離差
    dx = pos2[0] - pos1[0]

    # 計算 Y 軸方向的距離差
    dy = pos2[1] - pos1[1]

    # 用勾股定理算出直線距離
    return math.sqrt(dx * dx + dy * dy)


def normalize_vector(vector):
    """
    將向量正規化為單位向量 - 保持方向但長度變為 1（已優化效能）\n
    \n
    正規化向量在移動計算中很重要，可以確保不同方向的移動速度一致\n
    例如斜向移動不會比水平移動更快\n
    \n
    參數:\n
    vector (tuple): 要正規化的向量 (x, y)\n
    \n
    回傳:\n
    tuple: 正規化後的單位向量 (x, y)，如果輸入為零向量則回傳 (0, 0)\n
    \n
    數學原理:\n
    單位向量 = 原向量 / |原向量|\n
    """
    x, y = vector[0], vector[1]

    # 使用快速的長度平方檢查，避免不必要的平方根計算
    length_squared = x * x + y * y

    # 如果長度平方為零，就不能正規化，直接回傳零向量
    if length_squared == 0:
        return (0, 0)

    # 只在需要時計算平方根
    if length_squared == 1:
        # 已經是單位向量，直接回傳
        return (x, y)

    # 計算長度並正規化
    length = math.sqrt(length_squared)
    return (x / length, y / length)


def clamp(value, min_value, max_value):
    """
    將數值限制在指定範圍內 - 防止數值超出合理範圍\n
    \n
    這個函式確保數值不會小於最小值或大於最大值\n
    常用於限制玩家移動範圍、UI 元素位置、遊戲參數等\n
    \n
    參數:\n
    value (float): 要限制的數值\n
    min_value (float): 允許的最小值\n
    max_value (float): 允許的最大值\n
    \n
    回傳:\n
    float: 限制後的數值，保證在 [min_value, max_value] 範圍內\n
    """
    # 如果數值太小，就設定為最小值
    if value < min_value:
        return min_value

    # 如果數值太大，就設定為最大值
    elif value > max_value:
        return max_value

    # 如果數值在合理範圍內，就保持原樣
    else:
        return value


def fast_movement_calculate(direction_x, direction_y, speed, dt):
    """
    快速移動計算 - 優化的移動距離計算函數\n
    \n
    避免使用複雜的正規化計算，直接處理常見的移動情況\n
    針對遊戲中最常見的 8 方向移動進行優化\n
    \n
    參數:\n
    direction_x (int): X 軸方向（-1, 0, 1）\n
    direction_y (int): Y 軸方向（-1, 0, 1）\n
    speed (float): 移動速度\n
    dt (float): 時間間隔\n
    \n
    回傳:\n
    tuple: (move_x, move_y) 移動距離\n
    """
    # 如果沒有移動，直接回傳零
    if direction_x == 0 and direction_y == 0:
        return (0, 0)

    # 計算基礎移動距離
    base_distance = speed * dt * 60

    # 針對常見情況做快速計算
    if direction_x == 0 or direction_y == 0:
        # 單軸移動（上下左右）
        return (direction_x * base_distance, direction_y * base_distance)
    else:
        # 斜向移動，使用預計算的係數 0.707 (1/√2)
        diagonal_distance = base_distance * 0.707
        return (direction_x * diagonal_distance, direction_y * diagonal_distance)


######################碰撞檢測工具######################
def check_rect_collision(rect1, rect2):
    """
    檢查兩個矩形是否發生碰撞 - AABB 碰撞檢測算法\n
    \n
    使用軸對齊邊界框 (Axis-Aligned Bounding Box) 方法\n
    這是 2D 遊戲中最常用的碰撞檢測方式，計算快速且準確\n
    \n
    參數:\n
    rect1 (pygame.Rect): 第一個矩形物件\n
    rect2 (pygame.Rect): 第二個矩形物件\n
    \n
    回傳:\n
    bool: True 表示有碰撞，False 表示沒有碰撞\n
    \n
    算法原理:\n
    兩個矩形相撞的條件是在 X 軸和 Y 軸上都有重疊\n
    """
    # 直接使用 Pygame 內建的矩形碰撞檢測
    return rect1.colliderect(rect2)


def check_point_in_rect(point, rect):
    """
    檢查點是否在矩形內部 - 常用於滑鼠點擊檢測\n
    \n
    判斷一個座標點是否位於矩形範圍內\n
    常用於 UI 按鈕點擊、物件選取、區域觸發等功能\n
    \n
    參數:\n
    point (tuple): 要檢查的點座標 (x, y)\n
    rect (pygame.Rect): 矩形區域\n
    \n
    回傳:\n
    bool: True 表示點在矩形內，False 表示點在矩形外\n
    """
    # 使用 Pygame 矩形的內建方法檢查點是否在內部
    return rect.collidepoint(point)


######################繪圖工具函式######################
def draw_text(surface, text, font, color, x, y, center=False):
    """
    在指定位置繪製文字 - 遊戲文字顯示的標準方法\n
    \n
    提供靈活的文字繪製功能，支援置中對齊和自訂顏色\n
    常用於 UI 文字、遊戲訊息、數值顯示等\n
    \n
    參數:\n
    surface (pygame.Surface): 要繪製到的表面\n
    text (str): 要顯示的文字內容\n
    font (pygame.Font): 文字字型物件\n
    color (tuple): 文字顏色 RGB 值 (r, g, b)\n
    x (int): 文字 X 座標位置\n
    y (int): 文字 Y 座標位置\n
    center (bool): 是否將文字置中對齊，預設為 False\n
    \n
    回傳:\n
    pygame.Rect: 文字的邊界矩形，可用於後續的碰撞檢測或對齊\n
    """
    # 先把文字渲染成圖片
    text_surface = font.render(text, True, color)

    # 取得文字圖片的矩形範圍
    text_rect = text_surface.get_rect()

    if center:
        # 如果要置中，就調整文字位置到指定座標的中央
        text_rect.center = (x, y)
    else:
        # 如果不置中，就把文字左上角放在指定座標
        text_rect.x = x
        text_rect.y = y

    # 把文字圖片畫到目標表面上
    surface.blit(text_surface, text_rect)

    # 回傳文字的位置資訊，方便其他程式使用
    return text_rect


def create_surface_with_alpha(width, height, alpha=255):
    """
    建立具有透明度的表面 - 用於半透明 UI 和特效\n
    \n
    創建支援 Alpha 透明通道的 Surface 物件\n
    常用於製作半透明背景、淡入淡出效果、UI 遮罩等\n
    \n
    參數:\n
    width (int): 表面寬度，單位為像素\n
    height (int): 表面高度，單位為像素\n
    alpha (int): 透明度值，0-255，0 為完全透明，255 為完全不透明\n
    \n
    回傳:\n
    pygame.Surface: 支援透明度的表面物件\n
    """
    # 建立支援 Alpha 通道的表面
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # 設定整個表面的透明度
    surface.set_alpha(alpha)

    return surface


######################檔案處理工具######################
def safe_load_image(file_path, default_size=(32, 32), default_color=(255, 0, 255)):
    """
    安全載入圖片檔案 - 包含錯誤處理的圖片載入\n
    \n
    嘗試載入圖片檔案，如果失敗則創建預設的彩色方塊\n
    確保遊戲不會因為遺失圖片檔案而當機\n
    \n
    參數:\n
    file_path (str): 圖片檔案的路徑\n
    default_size (tuple): 預設尺寸 (width, height)，當圖片載入失敗時使用\n
    default_color (tuple): 預設顏色 (r, g, b)，當圖片載入失敗時使用\n
    \n
    回傳:\n
    pygame.Surface: 載入的圖片或預設彩色方塊\n
    """
    try:
        # 嘗試載入圖片檔案
        image = pygame.image.load(file_path).convert_alpha()
        return image
    except (pygame.error, FileNotFoundError) as e:
        # 如果載入失敗，就建立一個彩色方塊代替
        print(f"無法載入圖片 {file_path}: {e}")
        print(f"使用預設顏色方塊代替，尺寸: {default_size}，顏色: {default_color}")

        # 建立一個指定大小的彩色方塊
        surface = pygame.Surface(default_size, pygame.SRCALPHA)
        surface.fill(default_color)
        return surface
