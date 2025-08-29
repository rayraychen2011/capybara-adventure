#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試玩家射擊能力檢查

這個測試程序專門檢查為什麼玩家無法射擊
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.player.player import Player

def test_player_can_shoot():
    """測試玩家射擊能力"""
    print("🔫 測試玩家射擊能力檢查")
    
    # 創建玩家
    player = Player(100, 100)
    
    print(f"玩家初始狀態:")
    print(f"  fire_enabled: {player.fire_enabled}")
    print(f"  has weapon_manager: {hasattr(player, 'weapon_manager')}")
    
    if hasattr(player, 'weapon_manager') and player.weapon_manager:
        current_weapon = player.weapon_manager.current_weapon
        print(f"  current_weapon: {current_weapon}")
        if current_weapon:
            print(f"    weapon_type: {current_weapon.weapon_type}")
            print(f"    can_shoot: {current_weapon.can_shoot()}")
    
    print(f"  player.can_shoot(): {player.can_shoot()}")
    print(f"  player.get_weapon_damage(): {player.get_weapon_damage()}")
    
    # 測試切換武器
    print("\n🔄 測試切換武器...")
    if hasattr(player, 'weapon_manager') and player.weapon_manager:
        player.weapon_manager.switch_weapon("pistol")
        current_weapon = player.weapon_manager.current_weapon
        print(f"切換到手槍後:")
        print(f"  current_weapon: {current_weapon}")
        if current_weapon:
            print(f"    weapon_type: {current_weapon.weapon_type}")
            print(f"    can_shoot: {current_weapon.can_shoot()}")
        print(f"  player.can_shoot(): {player.can_shoot()}")

if __name__ == "__main__":
    test_player_can_shoot()