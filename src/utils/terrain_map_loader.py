######################載入套件######################
import csv
import pygame
import sys
import os
from typing import List, Tuple, Dict, Optional

# 添加專案根目錄到路徑以支援字體管理器
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

try:
    from src.utils.font_manager import get_font_manager, init_font_system
except ImportError:
    # 如果無法導入字體管理器，定義空函數避免錯誤
    def get_font_manager():
        return None
    def init_font_system():
        pass

######################物件類別######################
class TerrainMapLoader:
    """
    地形地圖載入器 - 從CSV檔案載入地形數據並轉換為遊戲可用的格式\n
    \n
    此類別負責：\n
    1. 讀取CSV格式的地形文件\n
    2. 將數字編碼轉換為地形類型\n
    3. 提供地形查詢和渲染支援\n
    4. 支援地形編輯和儲存功能\n
    """
    
    def __init__(self):
        """
        初始化地形地圖載入器\n
        \n
        設定地形編碼對應表和預設顏色\n
        """
        # 地形編碼對應表 - 數字對應地形類型
        self.terrain_types = {
            0: "草地",
            1: "森林",
            2: "水體", 
            3: "道路",
            4: "高速公路",
            5: "住宅區",
            6: "商業區",
            7: "公園設施",
            8: "農地",  # 新增農地地形
            9: "山丘",
            10: "鐵軌",
            11: "火車站"
        }
        
        # 地形顏色對應表 - 用於渲染顯示
        self.terrain_colors = {
            0: (144, 238, 144),  # 淺綠色 - 草地
            1: (34, 139, 34),    # 深綠色 - 森林
            2: (30, 144, 255),   # 藍色 - 水體
            3: (169, 169, 169),  # 灰色 - 道路
            4: (105, 105, 105),  # 深灰色 - 高速公路
            5: (255, 255, 224),  # 淺黃色 - 住宅區
            6: (255, 165, 0),    # 橘色 - 商業區
            7: (50, 205, 50),    # 綠色 - 公園設施
            8: (205, 133, 63),   # 土黃色 - 農地
            9: (160, 82, 45),    # 棕色 - 山丘
            10: (139, 69, 19),   # 深棕色 - 鐵軌
            11: (220, 20, 60)    # 深紅色 - 火車站
        }
        
        # 地圖數據儲存
        self.map_data: List[List[int]] = []
        self.map_width: int = 0
        self.map_height: int = 0
        
    def load_from_csv(self, file_path: str) -> bool:
        """
        從CSV檔案載入地形地圖數據\n
        \n
        參數:\n
        file_path (str): CSV檔案的完整路徑\n
        \n
        回傳:\n
        bool: 載入成功回傳True，失敗回傳False\n
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                self.map_data = []
                
                # 逐行讀取CSV數據
                for row in csv_reader:
                    # 將字串轉換為整數列表
                    terrain_row = [int(cell.strip()) for cell in row if cell.strip()]
                    if terrain_row:  # 只加入非空白行
                        self.map_data.append(terrain_row)
                
                # 更新地圖尺寸資訊
                if self.map_data:
                    self.map_height = len(self.map_data)
                    self.map_width = len(self.map_data[0]) if self.map_data[0] else 0
                    print(f"地圖載入成功：{self.map_width}x{self.map_height}")
                    return True
                else:
                    print("錯誤：CSV檔案為空或格式不正確")
                    return False
                    
        except FileNotFoundError:
            print(f"錯誤：找不到檔案 {file_path}")
            return False
        except ValueError as e:
            print(f"錯誤：CSV數據格式不正確 - {e}")
            return False
        except Exception as e:
            print(f"載入地圖時發生未知錯誤：{e}")
            return False
    
    def save_to_csv(self, file_path: str) -> bool:
        """
        將當前地圖數據儲存為CSV檔案\n
        \n
        參數:\n
        file_path (str): 要儲存的CSV檔案路徑\n
        \n
        回傳:\n
        bool: 儲存成功回傳True，失敗回傳False\n
        """
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file)
                for row in self.map_data:
                    csv_writer.writerow(row)
            print(f"地圖儲存成功：{file_path}")
            return True
        except Exception as e:
            print(f"儲存地圖時發生錯誤：{e}")
            return False
    
    def get_terrain_at(self, x: int, y: int) -> Optional[int]:
        """
        獲取指定座標的地形類型編碼\n
        \n
        參數:\n
        x (int): X座標（列），範圍 0 到 map_width-1\n
        y (int): Y座標（行），範圍 0 到 map_height-1\n
        \n
        回傳:\n
        Optional[int]: 地形編碼，超出範圍回傳None\n
        """
        # 檢查座標是否在有效範圍內
        if 0 <= y < self.map_height and 0 <= x < self.map_width:
            return self.map_data[y][x]
        return None
    
    def set_terrain_at(self, x: int, y: int, terrain_code: int) -> bool:
        """
        設定指定座標的地形類型\n
        \n
        參數:\n
        x (int): X座標（列）\n
        y (int): Y座標（行）\n
        terrain_code (int): 地形編碼，必須在有效範圍內\n
        \n
        回傳:\n
        bool: 設定成功回傳True，失敗回傳False\n
        """
        # 檢查座標和編碼是否有效
        if (0 <= y < self.map_height and 0 <= x < self.map_width and 
            terrain_code in self.terrain_types):
            self.map_data[y][x] = terrain_code
            return True
        return False
    
    def get_terrain_name(self, terrain_code: int) -> str:
        """
        根據地形編碼獲取地形名稱\n
        \n
        參數:\n
        terrain_code (int): 地形編碼\n
        \n
        回傳:\n
        str: 地形名稱，未知編碼回傳"未知地形"\n
        """
        return self.terrain_types.get(terrain_code, "未知地形")
    
    def get_terrain_color(self, terrain_code: int) -> Tuple[int, int, int]:
        """
        根據地形編碼獲取對應顏色\n
        \n
        參數:\n
        terrain_code (int): 地形編碼\n
        \n
        回傳:\n
        Tuple[int, int, int]: RGB顏色值，未知編碼回傳白色\n
        """
        return self.terrain_colors.get(terrain_code, (255, 255, 255))
    
    def render_minimap(self, surface: pygame.Surface, scale: int = 2, show_labels: bool = False) -> None:
        """
        在指定表面上渲染地圖縮圖\n
        \n
        參數:\n
        surface (pygame.Surface): 要繪製的表面\n
        scale (int): 縮放比例，每個地形格子的像素大小\n
        show_labels (bool): 是否顯示地形類型標籤（需要初始化字體系統）\n
        """
        if not self.map_data:
            return
            
        # 如果需要顯示標籤，初始化字體系統
        font_manager = None
        if show_labels:
            try:
                font_manager = get_font_manager()
            except:
                print("字體系統未初始化，將不顯示標籤")
                show_labels = False
            
        # 逐格繪製地形
        for y in range(self.map_height):
            for x in range(self.map_width):
                terrain_code = self.map_data[y][x]
                color = self.get_terrain_color(terrain_code)
                
                # 計算繪製位置和大小
                rect = pygame.Rect(x * scale, y * scale, scale, scale)
                pygame.draw.rect(surface, color, rect)
                
                # 繪製格子邊框（當格子夠大時）
                if scale >= 8:
                    pygame.draw.rect(surface, (128, 128, 128), rect, 1)
                
                # 顯示地形編碼（當格子非常大時）
                if show_labels and font_manager and scale >= 20:
                    try:
                        text_surface = font_manager.render_text(str(terrain_code), 12, (255, 255, 255))
                        text_rect = text_surface.get_rect(center=rect.center)
                        surface.blit(text_surface, text_rect)
                    except:
                        pass  # 忽略文字渲染錯誤
    
    def render_legend(self, surface: pygame.Surface, x: int = 10, y: int = 10, 
                     item_height: int = 25, use_chinese_font: bool = True) -> None:
        """
        在指定位置渲染地形圖例\n
        \n
        參數:\n
        surface (pygame.Surface): 要繪製的表面\n
        x (int): 圖例起始X座標\n
        y (int): 圖例起始Y座標\n
        item_height (int): 每個圖例項目的高度\n
        use_chinese_font (bool): 是否使用繁體中文字體\n
        """
        try:
            if use_chinese_font:
                # 嘗試使用字體管理器
                font_manager = get_font_manager()
                font = font_manager.get_font(18)
            else:
                # 也使用字體管理器確保繁體中文支援
                font_manager = get_font_manager()
                font = font_manager.get_font(18)
        except:
            # 字體載入失敗，使用預設字體
            font = pygame.font.Font(None, 18)
            
        current_y = y
        
        # 繪製圖例標題
        try:
            if use_chinese_font:
                title_text = font_manager.render_text("地形圖例", 20, (255, 255, 255))
            else:
                title_text = font.render("Terrain Legend", True, (255, 255, 255))
        except:
            title_text = font.render("Terrain Legend", True, (255, 255, 255))
            
        surface.blit(title_text, (x, current_y))
        current_y += item_height + 5
        
        # 繪製每種地形的圖例
        for terrain_code, terrain_name in self.terrain_types.items():
            color = self.get_terrain_color(terrain_code)
            
            # 繪製顏色方塊
            color_rect = pygame.Rect(x, current_y + 3, 18, 18)
            pygame.draw.rect(surface, color, color_rect)
            pygame.draw.rect(surface, (255, 255, 255), color_rect, 1)
            
            # 繪製地形名稱
            try:
                if use_chinese_font:
                    text_surface = font_manager.render_text(f"{terrain_code}: {terrain_name}", 16, (255, 255, 255))
                else:
                    text_surface = font.render(f"{terrain_code}: {terrain_name}", True, (255, 255, 255))
            except:
                text_surface = font.render(f"{terrain_code}: {terrain_name}", True, (255, 255, 255))
                
            surface.blit(text_surface, (x + 25, current_y))
            current_y += item_height
    
    def get_map_info(self) -> Dict:
        """
        獲取地圖基本資訊\n
        \n
        回傳:\n
        Dict: 包含地圖尺寸和地形統計的字典\n
        """
        if not self.map_data:
            return {"width": 0, "height": 0, "terrain_count": {}}
        
        # 統計各種地形的數量
        terrain_count = {}
        for row in self.map_data:
            for terrain_code in row:
                terrain_name = self.get_terrain_name(terrain_code)
                terrain_count[terrain_name] = terrain_count.get(terrain_name, 0) + 1
        
        return {
            "width": self.map_width,
            "height": self.map_height,
            "total_tiles": self.map_width * self.map_height,
            "terrain_count": terrain_count
        }

######################定義函式區######################
def create_sample_map(width: int = 20, height: int = 15) -> List[List[int]]:
    """
    創建一個範例地圖用於測試\n
    \n
    參數:\n
    width (int): 地圖寬度，預設20格\n
    height (int): 地圖高度，預設15格\n
    \n
    回傳:\n
    List[List[int]]: 2D地形數據陣列\n
    """
    # 創建基礎草地地圖
    sample_map = [[0 for _ in range(width)] for _ in range(height)]
    
    # 添加一些道路
    for x in range(width):
        sample_map[height//2][x] = 3  # 水平道路
    for y in range(height):
        sample_map[y][width//2] = 3   # 垂直道路
    
    # 添加一些森林區域
    for y in range(2, 5):
        for x in range(2, 8):
            sample_map[y][x] = 1
    
    # 添加水體
    for y in range(height-3, height):
        for x in range(width-8, width-2):
            sample_map[y][x] = 2
    
    return sample_map

def main():
    """
    測試地形地圖載入器的主要函式\n
    """
    # 初始化地圖載入器
    map_loader = TerrainMapLoader()
    
    # 載入Cupertino地圖 - 使用編輯版本
    if map_loader.load_from_csv("config/cupertino_map_edited.csv"):
        # 顯示地圖資訊
        map_info = map_loader.get_map_info()
        print("\n=== 地圖資訊 ===")
        print(f"地圖大小：{map_info['width']} x {map_info['height']}")
        print(f"總格子數：{map_info['total_tiles']}")
        print("\n地形分佈：")
        for terrain_name, count in map_info['terrain_count'].items():
            percentage = (count / map_info['total_tiles']) * 100
            print(f"{terrain_name}: {count} 格 ({percentage:.1f}%)")
        
        # 測試獲取特定位置的地形
        print(f"\n座標(10,10)的地形：{map_loader.get_terrain_name(map_loader.get_terrain_at(10, 10))}")
        print(f"座標(25,15)的地形：{map_loader.get_terrain_name(map_loader.get_terrain_at(25, 15))}")
    else:
        print("地圖載入失敗")

# 只在直接執行此檔案時才運行測試
if __name__ == "__main__":
    main()