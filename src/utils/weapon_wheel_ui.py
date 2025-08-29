######################載入套件######################
import pygame
import math
from config.settings import *


######################武器圓盤UI######################
class WeaponWheelUI:
    """
    武器圓盤UI - 顯示3個武器選項的圓形界面\n
    \n
    中鍵顯示，有三個槽位：槍、斧頭、空手\n
    預設選擇為空手\n
    """

    def __init__(self):
        """
        初始化武器圓盤UI\n
        """
        # UI設定
        self.wheel_radius = 100  # 圓盤半徑
        self.slot_radius = 30    # 武器槽半徑
        self.center_radius = 20  # 中心圓半徑
        
        # 顏色設定
        self.bg_color = (0, 0, 0, 150)        # 半透明黑色背景
        self.wheel_color = (64, 64, 64, 200)   # 圓盤顏色
        self.slot_color = (128, 128, 128)      # 未選中槽顏色
        self.selected_color = (255, 255, 0)    # 選中槽顏色
        self.equipped_color = (0, 255, 0)      # 已裝備槽顏色
        self.text_color = (255, 255, 255)      # 白色文字
        
        # 字體設定 - 使用字體管理器支援繁體中文
        from src.utils.font_manager import get_font_manager
        font_manager = get_font_manager()
        self.font = font_manager.get_font(24)
        self.small_font = font_manager.get_font(18)
        
        # 武器槽位置（圓形排列，3個槽位）
        self.weapon_slots = {
            "gun": {
                "name": "槍",
                "position": self._calculate_position(-90),  # 上方
                "key": "1"
            },
            "unarmed": {
                "name": "空手",
                "position": self._calculate_position(30),   # 右下
                "key": "2"
            },
            "axe": {
                "name": "斧頭", 
                "position": self._calculate_position(150),  # 左下
                "key": "3"
            }
        }
        
        # 當前選中的武器（預設空手）
        self.current_weapon = "unarmed"
        
        # 圓盤顯示狀態
        self.is_visible = False
        
        print("武器圓盤UI初始化完成")

    def _calculate_position(self, angle_degrees):
        """
        計算武器槽的位置\n
        \n
        參數:\n
        angle_degrees (float): 角度（度數）\n
        \n
        回傳:\n
        tuple: (x_offset, y_offset) 相對於中心的偏移\n
        """
        radian = math.radians(angle_degrees)
        x_offset = math.cos(radian) * self.wheel_radius
        y_offset = math.sin(radian) * self.wheel_radius
        return (x_offset, y_offset)

    def toggle_visibility(self):
        """
        切換武器圓盤的顯示狀態\n
        """
        self.is_visible = not self.is_visible
        if self.is_visible:
            print("武器圓盤已開啟")
        else:
            print("武器圓盤已關閉")

    def show(self):
        """
        顯示武器圓盤\n
        """
        self.is_visible = True

    def hide(self):
        """
        隱藏武器圓盤\n
        """
        self.is_visible = False

    def select_weapon(self, weapon_type):
        """
        選擇武器\n
        \n
        參數:\n
        weapon_type (str): 武器類型 ("gun", "axe", "unarmed")\n
        \n
        回傳:\n
        bool: 是否成功選擇\n
        """
        if weapon_type in self.weapon_slots:
            self.current_weapon = weapon_type
            print(f"選擇武器: {self.weapon_slots[weapon_type]['name']}")
            return True
        return False

    def select_weapon_by_key(self, key_number):
        """
        根據數字鍵選擇武器\n
        \n
        參數:\n
        key_number (str): 按鍵編號 ("1", "2", "3")\n
        \n
        回傳:\n
        bool: 是否成功選擇\n
        """
        for weapon_type, weapon_data in self.weapon_slots.items():
            if weapon_data["key"] == key_number:
                return self.select_weapon(weapon_type)
        return False

    def get_current_weapon(self):
        """
        獲取當前選中的武器\n
        \n
        回傳:\n
        str: 當前武器類型\n
        """
        return self.current_weapon

    def get_current_weapon_name(self):
        """
        獲取當前武器的中文名稱\n
        \n
        回傳:\n
        str: 當前武器名稱\n
        """
        return self.weapon_slots[self.current_weapon]["name"]

    def draw(self, screen):
        """
        繪製武器圓盤\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        if not self.is_visible:
            return
        
        # 計算圓盤中心位置（螢幕中央）
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        
        # 繪製半透明背景
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 繪製圓盤背景
        wheel_surface = pygame.Surface((self.wheel_radius * 2 + 80, self.wheel_radius * 2 + 80), pygame.SRCALPHA)
        pygame.draw.circle(wheel_surface, self.wheel_color, 
                         (self.wheel_radius + 40, self.wheel_radius + 40), self.wheel_radius + 30)
        wheel_rect = wheel_surface.get_rect(center=(center_x, center_y))
        screen.blit(wheel_surface, wheel_rect)
        
        # 繪製中心圓
        pygame.draw.circle(screen, (100, 100, 100), (center_x, center_y), self.center_radius)
        
        # 繪製武器槽
        for weapon_type, weapon_data in self.weapon_slots.items():
            slot_x = center_x + weapon_data["position"][0]
            slot_y = center_y + weapon_data["position"][1]
            
            # 選擇槽顏色
            if weapon_type == self.current_weapon:
                color = self.equipped_color
            else:
                color = self.slot_color
            
            # 繪製槽圓圈
            pygame.draw.circle(screen, color, (int(slot_x), int(slot_y)), self.slot_radius)
            pygame.draw.circle(screen, (255, 255, 255), (int(slot_x), int(slot_y)), self.slot_radius, 3)
            
            # 繪製武器圖標（簡單的形狀代替）
            self._draw_weapon_icon(screen, weapon_type, int(slot_x), int(slot_y))
            
            # 繪製武器名稱
            name_text = self.small_font.render(weapon_data["name"], True, self.text_color)
            name_rect = name_text.get_rect(center=(slot_x, slot_y + self.slot_radius + 20))
            screen.blit(name_text, name_rect)
            
            # 繪製按鍵提示
            key_text = self.small_font.render(f"[{weapon_data['key']}]", True, (200, 200, 200))
            key_rect = key_text.get_rect(center=(slot_x, slot_y + self.slot_radius + 40))
            screen.blit(key_text, key_rect)
        
        # 繪製說明文字
        instruction_text = self.font.render("按 1-3 選擇武器，按中鍵關閉", True, self.text_color)
        instruction_rect = instruction_text.get_rect(center=(center_x, center_y + self.wheel_radius + 80))
        screen.blit(instruction_text, instruction_rect)
        
        # 顯示當前武器
        current_text = self.font.render(f"當前武器: {self.get_current_weapon_name()}", True, self.equipped_color)
        current_rect = current_text.get_rect(center=(center_x, center_y - self.wheel_radius - 60))
        screen.blit(current_text, current_rect)

    def _draw_weapon_icon(self, screen, weapon_type, x, y):
        """
        繪製武器圖標\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        weapon_type (str): 武器類型\n
        x (int): X座標\n
        y (int): Y座標\n
        """
        if weapon_type == "gun":
            # 槍的圖標 - 簡單的L形
            pygame.draw.rect(screen, (64, 64, 64), (x-10, y-2, 15, 4))  # 槍管
            pygame.draw.rect(screen, (64, 64, 64), (x-5, y-8, 8, 10))   # 握把
            
        elif weapon_type == "axe":
            # 斧頭的圖標 - 三角形加手柄
            points = [(x-8, y-8), (x+8, y-8), (x, y+8)]
            pygame.draw.polygon(screen, (139, 69, 19), points)  # 斧頭
            pygame.draw.rect(screen, (101, 67, 33), (x-2, y, 4, 15))  # 手柄
            
        elif weapon_type == "unarmed":
            # 空手的圖標 - 拳頭
            pygame.draw.circle(screen, (255, 220, 177), (x, y), 8)  # 拳頭
            pygame.draw.rect(screen, (255, 220, 177), (x-3, y+5, 6, 10))  # 手腕

    def handle_key_input(self, key):
        """
        處理按鍵輸入\n
        \n
        參數:\n
        key (int): 按鍵代碼\n
        \n
        回傳:\n
        bool: 是否處理了輸入\n
        """
        if key == pygame.K_1:
            return self.select_weapon("gun")
        elif key == pygame.K_2:
            return self.select_weapon("unarmed")
        elif key == pygame.K_3:
            return self.select_weapon("axe")
        return False

    def handle_middle_click(self):
        """
        處理中鍵點擊\n
        """
        self.toggle_visibility()