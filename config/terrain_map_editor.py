######################載入套件######################
import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.terrain_map_loader import TerrainMapLoader
from src.utils.font_manager import get_font_manager, init_font_system

######################物件類別######################
class TerrainMapEditor:
    """
    地形地圖編輯器 - 提供視覺化的地圖編輯功能\n
    \n
    此編輯器允許：\n
    1. 載入和顯示CSV地圖\n
    2. 使用滑鼠點擊修改地形\n
    3. 即時預覽地形變更\n
    4. 儲存修改後的地圖\n
    5. 自動載入最後編輯的版本\n
    """
    
    def __init__(self, window_width: int = 1200, window_height: int = 900):
        """
        初始化地圖編輯器\n
        \n
        參數:\n
        window_width (int): 視窗寬度，預設1200像素\n
        window_height (int): 視窗高度，預設900像素\n
        """
        pygame.init()
        
        # 初始化字體系統以支援繁體中文
        init_font_system()
        self.font_manager = get_font_manager()
        
        # 設定視窗
        self.window_width = window_width
        self.window_height = window_height
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("地形地圖編輯器 - Cupertino Map Editor")
        
        # 設定字體 - 使用字體管理器取得支援繁體中文的字體
        self.font = self.font_manager.get_font(24)
        self.small_font = self.font_manager.get_font(18)
        
        # 初始化地圖載入器
        self.map_loader = TerrainMapLoader()
        
        # 編輯器設定
        self.tile_size = 15  # 提高初始瓦片大小，讓地圖更清楚
        self.selected_terrain = 0  # 當前選擇的地形類型
        self.map_offset_x = 50  # 地圖顯示偏移
        self.map_offset_y = 50
        
        # 縮放和拖拽功能
        self.min_tile_size = 2  # 最小瓦片大小
        self.max_tile_size = 50  # 最大瓦片大小
        self.dragging = False  # 是否正在拖拽地圖
        self.last_mouse_pos = (0, 0)  # 上一次滑鼠位置
        
        # 工具面板設定
        self.panel_width = 200
        self.panel_x = window_width - self.panel_width
        
        # 編輯器狀態
        self.is_painting = False
        self.running = True
        self.current_file_info = "未載入檔案"  # 追蹤當前檔案狀態
        self.has_unsaved_changes = False  # 追蹤是否有未儲存的變更
        
    def load_map(self, file_path: str) -> bool:
        """
        載入地圖檔案\n
        \n
        參數:\n
        file_path (str): CSV地圖檔案路徑\n
        \n
        回傳:\n
        bool: 載入成功回傳True\n
        """
        success = self.map_loader.load_from_csv(file_path)
        if success:
            print(f"地圖載入成功：{file_path}")
            # 更新當前檔案資訊
            if "edited" in file_path:
                self.current_file_info = "編輯版本 (已修改)"
            else:
                self.current_file_info = "原始版本"
            # 調整顯示比例以適應視窗
            self._adjust_display_scale()
        return success
    
    def _adjust_display_scale(self):
        """
        根據地圖大小調整顯示比例\n
        讓整個地圖能夠顯示在視窗中\n
        """
        if self.map_loader.map_width == 0 or self.map_loader.map_height == 0:
            return
            
        # 計算可用的顯示區域（扣除工具面板）
        available_width = self.window_width - self.panel_width - self.map_offset_x * 2
        available_height = self.window_height - self.map_offset_y * 2
        
        # 計算適合的瓦片大小，但不要太小
        scale_x = available_width // self.map_loader.map_width
        scale_y = available_height // self.map_loader.map_height
        
        # 選擇較小的比例以確保地圖完整顯示，但設定最小值
        optimal_size = max(1, min(scale_x, scale_y, 25))
        self.tile_size = max(optimal_size, 8)  # 至少8像素，確保可見性
        
        print(f"顯示比例調整為：{self.tile_size}x{self.tile_size} 像素/格")
        print(f"提示：使用滑鼠滾輪可縮放，按住中鍵可拖拽地圖")
    
    def handle_events(self):
        """
        處理使用者輸入事件\n
        包含滑鼠點擊、鍵盤按鍵、縮放和拖拽等\n
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左鍵點擊
                    self.is_painting = True
                    self._handle_map_click(event.pos)
                elif event.button == 2:  # 中鍵，開始拖拽
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 左鍵放開
                    self.is_painting = False
                elif event.button == 2:  # 中鍵放開
                    self.dragging = False
                    
            elif event.type == pygame.MOUSEWHEEL:
                # 滑鼠滾輪縮放
                if event.y > 0:  # 向上滾，放大
                    self.tile_size = min(self.max_tile_size, self.tile_size + 2)
                elif event.y < 0:  # 向下滾，縮小
                    self.tile_size = max(self.min_tile_size, self.tile_size - 2)
                print(f"縮放：{self.tile_size}x{self.tile_size} 像素/格")
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.is_painting:
                    self._handle_map_click(event.pos)
                elif self.dragging:
                    # 拖拽地圖
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.map_offset_x += dx
                    self.map_offset_y += dy
                    self.last_mouse_pos = event.pos
                    
            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard(event.key)
    
    def _handle_map_click(self, mouse_pos: tuple):
        """
        處理地圖區域的滑鼠點擊\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠座標 (x, y)\n
        """
        mouse_x, mouse_y = mouse_pos
        
        # 檢查是否點擊在地圖區域內
        if (mouse_x < self.map_offset_x or 
            mouse_x >= self.panel_x or
            mouse_y < self.map_offset_y):
            return
            
        # 轉換螢幕座標為地圖格子座標
        map_x = (mouse_x - self.map_offset_x) // self.tile_size
        map_y = (mouse_y - self.map_offset_y) // self.tile_size
        
        # 檢查是否真的改變了地形
        current_terrain = self.map_loader.get_terrain_at(map_x, map_y)
        if current_terrain != self.selected_terrain:
            # 設定地形類型
            if self.map_loader.set_terrain_at(map_x, map_y, self.selected_terrain):
                print(f"設定座標({map_x},{map_y})為{self.map_loader.get_terrain_name(self.selected_terrain)}")
                self.has_unsaved_changes = True  # 標記有未儲存的變更
                self.current_file_info = "編輯版本 (有未儲存變更)"
    
    def _handle_keyboard(self, key):
        """
        處理鍵盤輸入\n
        \n
        參數:\n
        key: pygame鍵盤事件鍵值\n
        """
        # 數字鍵0-9選擇地形類型
        if pygame.K_0 <= key <= pygame.K_9:
            terrain_code = key - pygame.K_0
            if terrain_code in self.map_loader.terrain_types:
                self.selected_terrain = terrain_code
                print(f"選擇地形：{self.map_loader.get_terrain_name(terrain_code)}")
        
        # Q鍵選擇鐵軌(10)
        elif key == pygame.K_q:
            if 10 in self.map_loader.terrain_types:
                self.selected_terrain = 10
                print(f"選擇地形：{self.map_loader.get_terrain_name(10)}")
        
        # E鍵選擇火車站(11)
        elif key == pygame.K_e:
            if 11 in self.map_loader.terrain_types:
                self.selected_terrain = 11
                print(f"選擇地形：{self.map_loader.get_terrain_name(11)}")
                
        # S鍵儲存地圖
        elif key == pygame.K_s:
            self.save_map()
            
        # R鍵重置視圖
        elif key == pygame.K_r:
            self.map_offset_x = 50
            self.map_offset_y = 50
            self._adjust_display_scale()
            print("視圖已重置")
            
        # F鍵全螢幕適配
        elif key == pygame.K_f:
            self._adjust_display_scale()
            self.map_offset_x = 50
            self.map_offset_y = 50
            print("地圖已適配螢幕大小")
            
        # +/- 鍵縮放
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
            self.tile_size = min(self.max_tile_size, self.tile_size + 2)
            print(f"放大：{self.tile_size}x{self.tile_size} 像素/格")
        elif key == pygame.K_MINUS:
            self.tile_size = max(self.min_tile_size, self.tile_size - 2)
            print(f"縮小：{self.tile_size}x{self.tile_size} 像素/格")
            
        # ESC鍵離開
        elif key == pygame.K_ESCAPE:
            self.running = False
    
    def save_map(self):
        """
        儲存當前地圖到CSV檔案\n
        始終儲存至編輯版本檔案，保持編輯連續性\n
        """
        file_path = "config/cupertino_map_edited.csv"
        if self.map_loader.save_to_csv(file_path):
            print(f"地圖已儲存至：{file_path}")
            print("下次開啟編輯器時將自動載入此版本")
            self.has_unsaved_changes = False  # 清除未儲存變更標記
            self.current_file_info = "編輯版本 (已儲存)"
        else:
            print("地圖儲存失敗")
    
    def draw(self):
        """
        繪製編輯器介面\n
        包含地圖顯示和工具面板\n
        """
        # 清空螢幕
        self.screen.fill((64, 64, 64))
        
        # 繪製地圖
        self._draw_map()
        
        # 繪製工具面板
        self._draw_tool_panel()
        
        # 繪製滑鼠座標資訊
        self._draw_mouse_info()
        
        # 更新顯示
        pygame.display.flip()
    
    def _draw_mouse_info(self):
        """
        在螢幕上顯示當前滑鼠位置對應的地圖座標\n
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # 計算滑鼠對應的地圖座標
        if (mouse_x >= self.map_offset_x and 
            mouse_x < self.panel_x and
            mouse_y >= self.map_offset_y):
            
            map_x = (mouse_x - self.map_offset_x) // self.tile_size
            map_y = (mouse_y - self.map_offset_y) // self.tile_size
            
            # 檢查座標是否在地圖範圍內
            if (0 <= map_x < self.map_loader.map_width and 
                0 <= map_y < self.map_loader.map_height):
                
                current_terrain = self.map_loader.get_terrain_at(map_x, map_y)
                terrain_name = self.map_loader.get_terrain_name(current_terrain)
                
                # 在螢幕左下角顯示座標資訊
                coord_text = f"座標: ({map_x}, {map_y}) - {terrain_name}"
                coord_surface = self.font_manager.render_text(coord_text, 18, (255, 255, 0))
                self.screen.blit(coord_surface, (10, self.window_height - 30))
    
    def _draw_map(self):
        """
        繪製地圖網格\n
        """
        if not self.map_loader.map_data:
            return
            
        # 繪製每個地形格子
        for y in range(self.map_loader.map_height):
            for x in range(self.map_loader.map_width):
                terrain_code = self.map_loader.get_terrain_at(x, y)
                if terrain_code is not None:
                    color = self.map_loader.get_terrain_color(terrain_code)
                    
                    # 計算繪製位置
                    rect_x = self.map_offset_x + x * self.tile_size
                    rect_y = self.map_offset_y + y * self.tile_size
                    
                    # 繪製地形格子
                    rect = pygame.Rect(rect_x, rect_y, self.tile_size, self.tile_size)
                    pygame.draw.rect(self.screen, color, rect)
                    
                    # 繪製格子邊框（當瓦片夠大時）
                    if self.tile_size >= 10:
                        pygame.draw.rect(self.screen, (128, 128, 128), rect, 1)
    
    def _draw_tool_panel(self):
        """
        繪製右側工具面板\n
        """
        # 繪製面板背景
        panel_rect = pygame.Rect(self.panel_x, 0, self.panel_width, self.window_height)
        pygame.draw.rect(self.screen, (32, 32, 32), panel_rect)
        pygame.draw.line(self.screen, (128, 128, 128), (self.panel_x, 0), (self.panel_x, self.window_height), 2)
        
        y_offset = 20
        
        # 標題 - 使用字體管理器渲染繁體中文
        title_text = self.font_manager.render_text("地形地圖編輯器", 24, (255, 255, 255))
        self.screen.blit(title_text, (self.panel_x + 10, y_offset))
        y_offset += 40
        
        # 當前選擇的地形
        current_text = self.font_manager.render_text("當前地形:", 18, (255, 255, 255))
        self.screen.blit(current_text, (self.panel_x + 10, y_offset))
        y_offset += 20
        
        terrain_name = self.map_loader.get_terrain_name(self.selected_terrain)
        terrain_color = self.map_loader.get_terrain_color(self.selected_terrain)
        
        # 顯示當前地形顏色和名稱
        color_rect = pygame.Rect(self.panel_x + 10, y_offset, 20, 20)
        pygame.draw.rect(self.screen, terrain_color, color_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), color_rect, 1)
        
        name_text = self.font_manager.render_text(f"{self.selected_terrain}: {terrain_name}", 18, (255, 255, 255))
        self.screen.blit(name_text, (self.panel_x + 35, y_offset + 2))
        y_offset += 40
        
        # 地形選項
        options_text = self.font_manager.render_text("地形選項 (0-9, Q鐵軌, E火車站):", 18, (255, 255, 255))
        self.screen.blit(options_text, (self.panel_x + 10, y_offset))
        y_offset += 25
        
        # 顯示所有地形類型
        for code, name in self.map_loader.terrain_types.items():
            color = self.map_loader.get_terrain_color(code)
            
            # 地形顏色方塊
            color_rect = pygame.Rect(self.panel_x + 10, y_offset, 15, 15)
            pygame.draw.rect(self.screen, color, color_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), color_rect, 1)
            
            # 地形名稱 - 使用字體管理器渲染繁體中文，為鐵軌和火車站顯示特殊快捷鍵
            text_color = (255, 255, 0) if code == self.selected_terrain else (255, 255, 255)
            
            # 根據地形類型顯示不同的快捷鍵提示
            if code == 10:  # 鐵軌
                terrain_text = self.font_manager.render_text(f"Q: {name}", 18, text_color)
            elif code == 11:  # 火車站
                terrain_text = self.font_manager.render_text(f"E: {name}", 18, text_color)
            else:  # 其他地形顯示數字
                terrain_text = self.font_manager.render_text(f"{code}: {name}", 18, text_color)
            
            self.screen.blit(terrain_text, (self.panel_x + 30, y_offset))
            
            y_offset += 20
        
        # 操作說明
        y_offset += 20
        controls_text = self.font_manager.render_text("操作說明:", 18, (255, 255, 255))
        self.screen.blit(controls_text, (self.panel_x + 10, y_offset))
        y_offset += 20
        
        instructions = [
            "左鍵: 繪製地形",
            "中鍵拖拽: 移動地圖",
            "滑鼠滾輪: 縮放",
            "0-9: 選擇地形",
            "Q: 鐵軌 E: 火車站",
            "+/-: 縮放地圖",
            "R: 重置視圖",
            "F: 適配螢幕",
            "S: 儲存地圖",
            "ESC: 離開"
        ]
        
        for instruction in instructions:
            inst_text = self.font_manager.render_text(instruction, 18, (200, 200, 200))
            self.screen.blit(inst_text, (self.panel_x + 10, y_offset))
            y_offset += 18
        
        # 地圖資訊
        if self.map_loader.map_data:
            y_offset += 20
            info_text = self.font_manager.render_text("地圖資訊:", 18, (255, 255, 255))
            self.screen.blit(info_text, (self.panel_x + 10, y_offset))
            y_offset += 20
            
            # 當前檔案狀態 - 根據是否有未儲存變更改變顏色
            file_color = (255, 200, 100) if self.has_unsaved_changes else (200, 200, 200)
            file_text = self.font_manager.render_text(f"檔案: {self.current_file_info}", 18, file_color)
            self.screen.blit(file_text, (self.panel_x + 10, y_offset))
            y_offset += 18
            
            size_text = self.font_manager.render_text(f"大小: {self.map_loader.map_width}x{self.map_loader.map_height}", 18, (200, 200, 200))
            self.screen.blit(size_text, (self.panel_x + 10, y_offset))
            y_offset += 18
            
            scale_text = self.font_manager.render_text(f"縮放: {self.tile_size}px/格", 18, (200, 200, 200))
            self.screen.blit(scale_text, (self.panel_x + 10, y_offset))
            y_offset += 18
            
            # 自動儲存提示
            save_text = self.font_manager.render_text("儲存至: cupertino_map_edited.csv", 18, (150, 255, 150))
            self.screen.blit(save_text, (self.panel_x + 10, y_offset))
    
    def run(self):
        """
        執行編輯器主迴圈\n
        """
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            self.draw()
            clock.tick(60)  # 60 FPS
            
        pygame.quit()

######################主程式######################
def main():
    """
    地圖編輯器主程式\n
    自動載入最後編輯的版本，保持編輯連續性\n
    """
    print("=== 地形地圖編輯器 ===")
    
    # 創建編輯器
    editor = TerrainMapEditor()
    
    # 優先載入編輯版本，如果不存在則載入原始版本
    edited_map_path = "config/cupertino_map_edited.csv"
    original_map_path = "config/cupertino_map.csv"
    
    # 檢查編輯版本是否存在
    if os.path.exists(edited_map_path):
        print(f"載入最後編輯的地圖版本：{edited_map_path}")
        map_loaded = editor.load_map(edited_map_path)
        current_file = "編輯版本"
    else:
        print(f"編輯版本不存在，載入原始地圖：{original_map_path}")
        map_loaded = editor.load_map(original_map_path)
        current_file = "原始版本"
    
    if map_loaded:
        print(f"地圖載入成功！當前檔案：{current_file}")
        print(f"編輯結果將自動儲存到：{edited_map_path}")
        print("\n操作說明：")
        print("- 左鍵點擊或拖拽來繪製地形")
        print("- 按數字鍵 0-9 選擇不同的地形類型")
        print("- 按 S 鍵儲存地圖（自動儲存到編輯版本）")
        print("- 按 ESC 鍵離開編輯器")
        print("- 下次開啟將自動載入您的編輯結果")
        
        # 執行編輯器
        editor.run()
    else:
        print("錯誤：無法載入地圖檔案")
        print(f"請確認以下檔案之一存在：")
        print(f"- {edited_map_path}")
        print(f"- {original_map_path}")

# 直接執行編輯器
main()