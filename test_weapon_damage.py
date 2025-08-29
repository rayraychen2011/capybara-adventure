#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試武器傷害系統 - 驗證子彈傷害是否從武器獲取
"""

import pygame
import sys
import os

# 添加專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.player.player import Player
from src.systems.shooting_system import ShootingSystem
from config.settings import *

def test_weapon_damage():
    """測試武器傷害是否正確傳遞給子彈"""
    
    # 初始化Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # 創建玩家
    player = Player()
    
    # 創建射擊系統
    shooting_system = ShootingSystem()
    
    print("=== 武器傷害測試 ===")
    
    # 測試預設武器傷害
    default_damage = player.get_weapon_damage()
    print(f"玩家當前武器傷害: {default_damage}")
    
    # 測試射擊（創建子彈）
    target_pos = (500, 500)
    success = shooting_system.shoot(player, target_pos)
    
    if success and shooting_system.bullets:
        bullet = shooting_system.bullets[-1]  # 獲取最新的子彈
        print(f"子彈傷害: {bullet.damage}")
        print(f"子彈傷害是否匹配武器傷害: {bullet.damage == default_damage}")
        
        if bullet.damage == default_damage:
            print("✅ 子彈正確使用了武器的傷害值！")
        else:
            print("❌ 子彈傷害與武器傷害不匹配！")
    else:
        print("❌ 射擊失敗或沒有創建子彈")
    
    # 測試不同武器
    if hasattr(player, 'weapon_manager') and player.weapon_manager:
        print("\n=== 測試不同武器類型 ===")
        
        # 獲取所有可用武器
        available_weapons = player.weapon_manager.get_available_weapons()
        print(f"可用武器: {available_weapons}")
        
        for weapon_type in available_weapons:
            # 切換武器
            if player.weapon_manager.switch_weapon(weapon_type):
                weapon_damage = player.get_weapon_damage()
                print(f"\n{weapon_type} 武器傷害: {weapon_damage}")
                
                # 測試射擊
                success = shooting_system.shoot(player, target_pos)
                if success and shooting_system.bullets:
                    bullet = shooting_system.bullets[-1]
                    print(f"  子彈傷害: {bullet.damage}")
                    print(f"  傷害匹配: {bullet.damage == weapon_damage}")
    
    print("\n=== 測試完成 ===")
    pygame.quit()

if __name__ == "__main__":
    test_weapon_damage()