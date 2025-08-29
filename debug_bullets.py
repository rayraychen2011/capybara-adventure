#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
子彈調試腳本 - 測試子彈顯示和音效\n
"""

import pygame
import sys
import os

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import *
from src.systems.shooting_system import ShootingSystem, Bullet
from src.player.player import Player

def main():
    """主測試函數"""
    pygame.init()
    
    # 定義顏色
    WHITE = (255, 255, 255)
    
    # 創建顯示窗口
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("子彈測試")
    clock = pygame.time.Clock()
    
    # 創建測試物件
    shooting_system = ShootingSystem()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    camera_offset = (0, 0)  # 無攝影機偏移
    
    print("開始子彈測試...")
    print("操作說明：")
    print("- 左鍵點擊：射擊")
    print("- ESC：退出")
    
    # 手動創建一些測試子彈
    test_bullets = [
        Bullet((100, 100), (5, 0)),   # 向右飛
        Bullet((200, 200), (0, -5)),  # 向上飛  
        Bullet((300, 300), (-3, 3)),  # 斜飛
    ]
    shooting_system.bullets.extend(test_bullets)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左鍵射擊
                    print(f"射擊位置: {event.pos}")
                    shooting_system.handle_mouse_shoot(player, event.pos, camera_offset)
        
        # 更新
        dt = clock.get_time() / 1000.0  # 轉換為秒
        shooting_system.update(dt)
        
        # 繪製
        screen.fill((50, 100, 50))  # 深綠背景
        
        # 繪製十字準線
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        pygame.draw.line(screen, WHITE, (center_x - 10, center_y), (center_x + 10, center_y), 2)
        pygame.draw.line(screen, WHITE, (center_x, center_y - 10), (center_x, center_y + 10), 2)
        
        # 繪製子彈（無攝影機偏移）
        bullet_count = len(shooting_system.bullets)
        shooting_system.draw_bullets(screen, camera_offset)
        
        # 顯示子彈數量
        font = pygame.font.Font(None, 36)
        text = font.render(f"子彈數量: {bullet_count}", True, WHITE)
        screen.blit(text, (10, 10))
        
        # 顯示玩家位置
        pos_text = font.render(f"玩家位置: ({player.x}, {player.y})", True, WHITE)
        screen.blit(pos_text, (10, 50))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("測試結束")

if __name__ == "__main__":
    main()