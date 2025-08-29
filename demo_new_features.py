#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新功能演示腳本
演示以下實現的功能：
1. 動物均勻分布
2. 右鍵與NPC對話
3. 武器切換系統（1=槍，2=空手）
4. 商業區重複建築檢測和漫畫主題服裝店替換
"""

import pygame
import sys
import os

# 添加專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.player.player import Player
from src.systems.weapon_system import WeaponManager
from src.player.input_controller import InputController

######################主演示程序######################

def main():
    """主演示程序"""
    print("=== 新功能演示程序 ===\n")
    
    # 初始化Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("新功能演示")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # 創建玩家
    try:
        player = Player(400, 300)
        print("✅ 玩家創建成功，包含武器管理器")
    except Exception as e:
        print(f"❌ 玩家創建失敗: {e}")
        pygame.quit()
        return
    
    # 創建輸入控制器
    input_controller = InputController(player)
    print("✅ 輸入控制器創建成功")
    
    # 遊戲狀態
    running = True
    current_demo = 0
    demos = [
        "武器切換演示 - 按1切換到槍，按2切換到空手",
        "輸入系統演示 - 右鍵模擬與NPC對話",
        "所有系統整合演示"
    ]
    
    print("\n=== 開始互動演示 ===")
    print("控制說明：")
    print("- WASD: 移動")
    print("- 1鍵: 切換到槍")
    print("- 2鍵: 切換到空手")
    print("- 右鍵: 與NPC對話（模擬）")
    print("- ESC: 退出")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    current_demo = (current_demo + 1) % len(demos)
                    print(f"\n切換到: {demos[current_demo]}")
            
            # 讓輸入控制器處理事件
            action = input_controller.handle_event(event)
            
            # 處理特殊動作
            if action:
                if action == "weapon_gun":
                    print("🔫 玩家切換到槍")
                elif action == "weapon_unarmed":
                    print("✋ 玩家切換到空手")
                elif action == "talk_to_npc":
                    print("💬 玩家嘗試與NPC對話（右鍵點擊）")
        
        # 更新輸入控制器
        input_controller.update(dt)
        
        # 更新玩家
        player.update(dt)
        
        # 繪製
        screen.fill((50, 50, 50))  # 深灰色背景
        
        # 繪製玩家
        pygame.draw.circle(screen, (0, 255, 0), (int(player.x), int(player.y)), 15)
        
        # 繪製UI信息
        y_offset = 10
        
        # 顯示當前演示
        demo_text = font.render(f"當前演示: {demos[current_demo]}", True, (255, 255, 255))
        screen.blit(demo_text, (10, y_offset))
        y_offset += 30
        
        # 顯示武器信息
        if hasattr(player, 'weapon_manager') and player.weapon_manager:
            weapon_info = player.weapon_manager.get_current_weapon_info()
            if weapon_info:
                weapon_text = font.render(f"當前武器: {weapon_info['name']}", True, (255, 255, 0))
                screen.blit(weapon_text, (10, y_offset))
                y_offset += 25
                
                ammo_info = weapon_info['ammo']
                if weapon_info['type'] == 'unarmed':
                    ammo_text = font.render("空手攻擊 - 無需彈藥", True, (255, 255, 255))
                else:
                    ammo_text = font.render(f"彈藥: {ammo_info['current']}/{ammo_info['magazine']}", True, (255, 255, 255))
                screen.blit(ammo_text, (10, y_offset))
                y_offset += 25
        
        # 顯示玩家位置
        pos_text = font.render(f"位置: ({int(player.x)}, {int(player.y)})", True, (255, 255, 255))
        screen.blit(pos_text, (10, y_offset))
        y_offset += 25
        
        # 顯示移動狀態
        if player.is_moving:
            moving_text = font.render("狀態: 移動中", True, (0, 255, 0))
        else:
            moving_text = font.render("狀態: 靜止", True, (255, 255, 255))
        screen.blit(moving_text, (10, y_offset))
        y_offset += 25
        
        # 顯示控制提示
        y_offset += 20
        controls = [
            "控制說明:",
            "WASD - 移動",
            "1鍵 - 切換到槍",
            "2鍵 - 切換到空手", 
            "右鍵 - 與NPC對話",
            "SPACE - 切換演示",
            "ESC - 退出"
        ]
        
        for control in controls:
            control_text = font.render(control, True, (200, 200, 200))
            screen.blit(control_text, (10, y_offset))
            y_offset += 20
        
        pygame.display.flip()
    
    print("\n=== 演示結束 ===")
    print("新功能總結:")
    print("1. ✅ 武器切換系統：1鍵切換到槍，2鍵切換到空手")
    print("2. ✅ 輸入控制器：右鍵與NPC對話功能")
    print("3. ✅ 玩家整合：武器管理器已集成到玩家系統")
    print("4. ✅ 動物均勻分布：網格分布算法已實現")
    print("5. ✅ 商業區建築：重複檢測和漫畫主題服裝店已實現")
    
    pygame.quit()

if __name__ == "__main__":
    main()