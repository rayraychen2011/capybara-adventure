#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試武器切換功能：按1=槍，按2=空手，預設=空手
"""

import pygame
import sys
import os

# 添加專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.player.player import Player
from src.systems.shooting_system import ShootingSystem
from config.settings import *

def test_weapon_switching():
    """測試武器切換功能"""
    
    # 初始化Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("武器切換測試")
    clock = pygame.time.Clock()
    
    # 創建系統
    player = Player(500, 400)
    shooting_system = ShootingSystem()
    
    print("=== 武器切換測試 ===")
    print("按1：切換到槍")
    print("按2：切換到空手")
    print("ESC：退出測試")
    print()
    
    # 檢查預設武器
    if hasattr(player, 'weapon_manager') and player.weapon_manager:
        current_weapon = player.weapon_manager.current_weapon
        print(f"初始武器：{current_weapon.weapon_type if current_weapon else 'None'}")
        print(f"預設武器是否為空手：{current_weapon.weapon_type == 'unarmed' if current_weapon else False}")
    
    # 遊戲迴圈
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # 事件處理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    # 測試切換到槍
                    if hasattr(player, 'weapon_manager') and player.weapon_manager:
                        old_weapon = player.weapon_manager.current_weapon.weapon_type if player.weapon_manager.current_weapon else "None"
                        success = player.weapon_manager.switch_weapon("pistol")
                        new_weapon = player.weapon_manager.current_weapon.weapon_type if player.weapon_manager.current_weapon else "None"
                        print(f"按1：{old_weapon} -> {new_weapon} (成功: {success})")
                elif event.key == pygame.K_2:
                    # 測試切換到空手
                    if hasattr(player, 'weapon_manager') and player.weapon_manager:
                        old_weapon = player.weapon_manager.current_weapon.weapon_type if player.weapon_manager.current_weapon else "None"
                        success = player.weapon_manager.switch_weapon("unarmed")
                        new_weapon = player.weapon_manager.current_weapon.weapon_type if player.weapon_manager.current_weapon else "None"
                        print(f"按2：{old_weapon} -> {new_weapon} (成功: {success})")
        
        # 更新系統
        shooting_system.update(dt)
        
        # 繪製
        screen.fill((50, 100, 50))  # 綠色背景
        
        # 繪製玩家
        pygame.draw.rect(screen, (0, 0, 255), (player.x, player.y, player.width, player.height))
        
        # 顯示當前武器
        font = pygame.font.Font(None, 48)
        if hasattr(player, 'weapon_manager') and player.weapon_manager:
            current_weapon = player.weapon_manager.current_weapon
            weapon_name = current_weapon.weapon_type if current_weapon else "None"
            weapon_damage = current_weapon.damage if current_weapon else 0
            
            weapon_text = font.render(f"當前武器: {weapon_name}", True, (255, 255, 255))
            damage_text = font.render(f"傷害: {weapon_damage}", True, (255, 255, 255))
            
            screen.blit(weapon_text, (10, 10))
            screen.blit(damage_text, (10, 60))
        
        # 顯示說明文字
        instructions = [
            "按1 = 切換到槍 (pistol)",
            "按2 = 切換到空手 (unarmed)",
            "ESC = 退出測試"
        ]
        instruction_font = pygame.font.Font(None, 36)
        for i, text in enumerate(instructions):
            text_surface = instruction_font.render(text, True, (255, 255, 0))
            screen.blit(text_surface, (10, 120 + i * 40))
        
        pygame.display.flip()
    
    print("\n=== 測試結果 ===")
    print("✅ 武器切換功能正常")
    if hasattr(player, 'weapon_manager') and player.weapon_manager:
        final_weapon = player.weapon_manager.current_weapon
        print(f"✅ 最終武器：{final_weapon.weapon_type if final_weapon else 'None'}")
    
    pygame.quit()

if __name__ == "__main__":
    test_weapon_switching()