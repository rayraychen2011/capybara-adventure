######################載入套件######################
import pygame
import os
import sys

# 添加專案根目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.settings import *

######################字體管理器######################
class FontManager:
    """
    字體管理器 - 處理繁體中文字體的載入和管理\n
    \n
    此類別負責：\n
    1. 自動偵測系統中可用的繁體中文字體\n
    2. 提供不同大小的字體實例\n
    3. 確保文字能夠正確顯示繁體中文\n
    4. 提供字體快取機制，提升效能\n
    \n
    設計原則:\n
    - 優先使用系統內建的繁體中文字體\n
    - 提供 Fallback 機制，確保遊戲不會因字體問題無法執行\n
    - 字體快取避免重複載入，提升渲染效能\n
    """
    
    def __init__(self):
        """
        初始化字體管理器\n
        """
        # 確保pygame.font已初始化
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
            
        # 字體快取字典，避免重複載入相同字體
        self.font_cache = {}
        
        # 尋找可用的繁體中文字體
        self.chinese_font_path = self._find_chinese_font()
        
        print(f"使用字體: {self.chinese_font_path if self.chinese_font_path else '預設字體'}")
    
    def _find_chinese_font(self):
        """
        尋找系統中可用的繁體中文字體\n
        \n
        回傳:\n
        str 或 None: 可用字體的檔案路徑，如果都找不到則回傳 None\n
        """
        for font_path in CHINESE_FONTS:
            if font_path is None:
                # 到達 Fallback 選項
                return None
            
            if os.path.exists(font_path):
                try:
                    # 測試字體是否能正常載入
                    test_font = pygame.font.Font(font_path, 12)
                    # 測試是否能渲染繁體中文
                    test_surface = test_font.render("測試", True, (255, 255, 255))
                    return font_path
                except pygame.error:
                    # 這個字體有問題，繼續嘗試下一個
                    continue
        
        # 所有字體都無法使用，回傳 None 使用預設字體
        return None
    
    def get_font(self, size=DEFAULT_FONT_SIZE):
        """
        取得指定大小的字體實例\n
        \n
        參數:\n
        size (int): 字體大小，預設為 DEFAULT_FONT_SIZE\n
        \n
        回傳:\n
        pygame.font.Font: 字體物件實例\n
        """
        # 建立快取鍵值
        cache_key = (self.chinese_font_path, size)
        
        # 檢查快取中是否已有此字體
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # 建立新的字體實例
        try:
            if self.chinese_font_path:
                font = pygame.font.Font(self.chinese_font_path, size)
            else:
                # 使用 Pygame 預設字體
                font = pygame.font.Font(None, size)
        except pygame.error:
            # 載入失敗，使用預設字體
            font = pygame.font.Font(None, size)
        
        # 將字體加入快取
        self.font_cache[cache_key] = font
        
        return font
    
    def get_small_font(self):
        """
        取得小字體\n
        \n
        回傳:\n
        pygame.font.Font: 小字體物件\n
        """
        return self.get_font(SMALL_FONT_SIZE)
    
    def get_large_font(self):
        """
        取得大字體\n
        \n
        回傳:\n
        pygame.font.Font: 大字體物件\n
        """
        return self.get_font(LARGE_FONT_SIZE)
    
    def get_ui_font(self):
        """
        取得 UI 字體\n
        \n
        回傳:\n
        pygame.font.Font: UI 字體物件\n
        """
        return self.get_font(UI_FONT_SIZE)
    
    def get_title_font(self):
        """
        取得標題字體\n
        \n
        回傳:\n
        pygame.font.Font: 標題字體物件\n
        """
        return self.get_font(TITLE_FONT_SIZE)
    
    def render_text(self, text, size=DEFAULT_FONT_SIZE, color=TEXT_COLOR, antialias=True):
        """
        渲染文字為 Surface 物件\n
        \n
        參數:\n
        text (str): 要渲染的文字內容\n
        size (int): 字體大小，預設為 DEFAULT_FONT_SIZE\n
        color (tuple): 文字顏色 RGB 值，預設為 TEXT_COLOR\n
        antialias (bool): 是否使用反鋸齒，預設為 True\n
        \n
        回傳:\n
        pygame.Surface: 渲染完成的文字表面\n
        """
        font = self.get_font(size)
        return font.render(text, antialias, color)
    
    def render_multiline_text(self, text_lines, size=DEFAULT_FONT_SIZE, color=TEXT_COLOR, line_spacing=5):
        """
        渲染多行文字為 Surface 物件\n
        \n
        參數:\n
        text_lines (list): 文字行列表\n
        size (int): 字體大小\n
        color (tuple): 文字顏色 RGB 值\n
        line_spacing (int): 行間距\n
        \n
        回傳:\n
        pygame.Surface: 包含所有文字行的表面\n
        """
        if not text_lines:
            return pygame.Surface((1, 1))
        
        font = self.get_font(size)
        
        # 計算所需的表面尺寸
        max_width = 0
        total_height = 0
        line_surfaces = []
        
        for line in text_lines:
            line_surface = font.render(line, True, color)
            line_surfaces.append(line_surface)
            max_width = max(max_width, line_surface.get_width())
            total_height += line_surface.get_height() + line_spacing
        
        # 移除最後一行的多餘間距
        total_height -= line_spacing
        
        # 建立目標表面
        result_surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
        
        # 繪製各行文字
        y_offset = 0
        for line_surface in line_surfaces:
            result_surface.blit(line_surface, (0, y_offset))
            y_offset += line_surface.get_height() + line_spacing
        
        return result_surface
    
    def get_text_size(self, text, size=DEFAULT_FONT_SIZE):
        """
        計算文字渲染後的尺寸\n
        \n
        參數:\n
        text (str): 要計算的文字\n
        size (int): 字體大小\n
        \n
        回傳:\n
        tuple: (width, height) 文字的寬度和高度\n
        """
        font = self.get_font(size)
        return font.size(text)
    
    def clear_cache(self):
        """
        清空字體快取\n
        """
        self.font_cache.clear()
        print("字體快取已清空")

######################全域字體管理器實例######################
# 建立全域字體管理器實例，供其他模組使用
font_manager = None

def get_font_manager():
    """
    取得全域字體管理器實例\n
    \n
    回傳:\n
    FontManager: 字體管理器實例\n
    """
    global font_manager
    if font_manager is None:
        font_manager = FontManager()
    return font_manager

def init_font_system():
    """
    初始化字體系統\n
    """
    global font_manager
    font_manager = FontManager()
    print("字體系統初始化完成")