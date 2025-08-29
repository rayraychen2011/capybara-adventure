######################載入套件######################
import pygame
import math
from config.settings import *


######################裝備圓盤UI######################
class EquipmentWheelUI:
    """
    裝備圓盤UI - 顯示5個裝備選項的圓形界面\n
    \n
    按下E鍵顯示，按1-5數字鍵選擇裝備\n
    提供視覺化的裝備選擇界面\n
    """

    def __init__(self):
        """
        初始化裝備圓盤UI\n
        """
        # UI設定
        self.wheel_radius = 80  # 圓盤半徑
        self.slot_radius = 25   # 裝備槽半徑
        self.center_radius = 15 # 中心圓半徑
        
        # 顏色設定
        self.bg_color = (0, 0, 0, 180)        # 半透明黑色背景
        self.wheel_color = (64, 64, 64, 200)   # 圓盤顏色
        self.slot_color = (128, 128, 128)      # 未選中槽顏色
        self.selected_color = (255, 255, 0)    # 選中槽顏色
        self.equipped_color = (0, 255, 0)      # 已裝備槽顏色
        self.text_color = (255, 255, 255)      # 文字顏色
        
        # 字體設定 - 使用字體管理器支援繁體中文
        from src.utils.font_manager import get_font_manager
        font_manager = get_font_manager()
        self.font = font_manager.get_font(20)
        self.small_font = font_manager.get_font(16)
        
        # 裝備槽位置（圓形排列）
        self.slot_positions = self._calculate_slot_positions()
        
        print("裝備圓盤UI初始化完成")

    def _calculate_slot_positions(self):
        """
        計算5個裝備槽的位置（圓形排列）\n
        \n
        回傳:\n
        dict: 槽位置字典 {slot_number: (x_offset, y_offset)}\n
        """
        positions = {}
        
        # 5個槽位，從上方開始，順時針排列
        angles = [
            -90,   # 1槽：上方
            -18,   # 2槽：右上
            54,    # 3槽：右下
            126,   # 4槽：左下
            -162   # 5槽：左上
        ]
        
        for i, angle in enumerate(angles):
            slot_number = i + 1
            radian = math.radians(angle)
            x_offset = math.cos(radian) * self.wheel_radius
            y_offset = math.sin(radian) * self.wheel_radius
            positions[slot_number] = (x_offset, y_offset)
        
        return positions

    def draw(self, screen, player):
        """
        繪製裝備圓盤\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        player (Player): 玩家物件\n
        """
        if not player.equipment_wheel_visible:
            return
        
        # 計算圓盤中心位置（螢幕中央）
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        
        # 繪製半透明背景
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 繪製圓盤背景
        wheel_surface = pygame.Surface((self.wheel_radius * 2 + 50, self.wheel_radius * 2 + 50), pygame.SRCALPHA)
        pygame.draw.circle(wheel_surface, self.wheel_color, 
                         (self.wheel_radius + 25, self.wheel_radius + 25), self.wheel_radius + 20)
        wheel_rect = wheel_surface.get_rect(center=(center_x, center_y))
        screen.blit(wheel_surface, wheel_rect)
        
        # 繪製中心圓
        pygame.draw.circle(screen, (100, 100, 100), (center_x, center_y), self.center_radius)
        
        # 繪製裝備槽
        for slot_number, equipment in player.equipment_slots.items():
            slot_x = center_x + self.slot_positions[slot_number][0]
            slot_y = center_y + self.slot_positions[slot_number][1]
            
            # 選擇槽顏色
            if equipment["equipped"]:
                color = self.equipped_color
            else:
                color = self.slot_color
            
            # 繪製槽圓圈
            pygame.draw.circle(screen, color, (int(slot_x), int(slot_y)), self.slot_radius)
            pygame.draw.circle(screen, (255, 255, 255), (int(slot_x), int(slot_y)), self.slot_radius, 2)
            
            # 繪製槽位編號
            number_text = self.font.render(str(slot_number), True, self.text_color)
            number_rect = number_text.get_rect(center=(slot_x, slot_y - 8))
            screen.blit(number_text, number_rect)
            
            # 繪製裝備名稱
            name_text = self.small_font.render(equipment["name"], True, self.text_color)
            name_rect = name_text.get_rect(center=(slot_x, slot_y + 8))
            screen.blit(name_text, name_rect)
        
        # 繪製說明文字
        instruction_text = self.font.render("按 1-5 選擇裝備，按 E 關閉", True, self.text_color)
        instruction_rect = instruction_text.get_rect(center=(center_x, center_y + self.wheel_radius + 60))
        screen.blit(instruction_text, instruction_rect)
        
        # 顯示當前裝備
        current_equipment = player.get_current_equipment()
        if current_equipment:
            current_text = self.font.render(f"當前裝備: {current_equipment['name']}", True, self.equipped_color)
            current_rect = current_text.get_rect(center=(center_x, center_y - self.wheel_radius - 40))
            screen.blit(current_text, current_rect)

    def handle_slot_selection(self, slot_number, player):
        """
        處理槽位選擇\n
        \n
        參數:\n
        slot_number (int): 選中的槽位編號\n
        player (Player): 玩家物件\n
        """
        if 1 <= slot_number <= 5:
            player.equip_item(slot_number)

    def is_visible(self, player):
        """
        檢查圓盤是否可見\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: 是否可見\n
        """
        return player.equipment_wheel_visible