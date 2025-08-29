#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
射擊系統完整測試腳本\n
"""

import pygame
import sys
import os

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import *
from src.systems.shooting_system import ShootingSystem
from src.player.player import Player

def main():
    """主測試函數"""
    pygame.init()
    
    # 定義顏色
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
    # 創建顯示窗口
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("射擊系統完整測試")
    clock = pygame.time.Clock()
    
    # 創建測試物件
    shooting_system = ShootingSystem()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    camera_offset = (0, 0)  # 無攝影機偏移
    
    print("射擊系統完整測試開始...")
    print(f"玩家初始武器: {player.get_current_weapon()}")
    print(f"玩家可以射擊: {player.can_shoot()}")
    print("操作說明：")
    print("- 左鍵點擊：射擊")
    print("- 中鍵：切換武器")
    print("- 1-3數字鍵：直接選擇武器")
    print("- ESC：退出")
    
    running = True
    while running:
        dt = clock.get_time() / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    player.switch_weapon("unarmed")
                    print(f"切換到: {player.get_current_weapon()}")
                elif event.key == pygame.K_2:
                    player.switch_weapon("gun")
                    print(f"切換到: {player.get_current_weapon()}")
                elif event.key == pygame.K_3:
                    player.switch_weapon("axe")
                    print(f"切換到: {player.get_current_weapon()}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左鍵射擊
                    if player.can_shoot():
                        print(f"射擊位置: {event.pos}, 武器: {player.get_current_weapon()}")
                        shooting_system.handle_mouse_shoot(player, event.pos, camera_offset)
                    else:
                        print(f"無法射擊，當前武器: {player.get_current_weapon()}")
                elif event.button == 2:  # 中鍵切換武器
                    player.toggle_weapon_wheel()
        
        # 更新
        shooting_system.update(dt)
        
        # 繪製
        screen.fill((50, 50, 100))  # 深藍背景
        
        # 繪製玩家位置
        pygame.draw.circle(screen, GREEN, (int(player.x), int(player.y)), 15)
        
        # 繪製準星
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.line(screen, RED, (mouse_pos[0] - 10, mouse_pos[1]), (mouse_pos[0] + 10, mouse_pos[1]), 2)
        pygame.draw.line(screen, RED, (mouse_pos[0], mouse_pos[1] - 10), (mouse_pos[0], mouse_pos[1] + 10), 2)
        
        # 繪製子彈
        bullet_count = len(shooting_system.bullets)
        shooting_system.draw_bullets(screen, camera_offset)
        
        # 繪製UI信息
        font = pygame.font.Font(None, 36)
        info_texts = [
            f"當前武器: {player.get_current_weapon()}",
            f"可以射擊: {player.can_shoot()}",
            f"子彈數量: {bullet_count}",
            f"滑鼠位置: {mouse_pos}",
            f"玩家位置: ({int(player.x)}, {int(player.y)})"
        ]
        
        for i, text in enumerate(info_texts):
            surface = font.render(text, True, WHITE)
            screen.blit(surface, (10, 10 + i * 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("測試結束")

if __name__ == "__main__":
    main()