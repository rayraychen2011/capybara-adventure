#!/usr/bin/env python3
"""
簡化射擊測試 - 直接模擬射擊和碰撞檢測
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import pygame
from src.systems.shooting_system import ShootingSystem
from src.systems.wildlife.animal import Animal, AnimalType
import math

def test_simple_shooting():
    """測試基本射擊和碰撞檢測"""
    
    # 初始化pygame（只為了必要的依賴）
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    print("🧪 開始射擊系統測試...")
    
    # 1. 創建射擊系統
    shooting_system = ShootingSystem()
    print("✅ 射擊系統已初始化")
    
    # 2. 創建測試動物
    animals = []
    # 在(100, 100)創建一隻兔子
    rabbit = Animal(
        animal_type=AnimalType.RABBIT,
        position=(100, 100),
        habitat_bounds=(0, 0, 800, 600)  # 整個螢幕作為棲息地
    )
    animals.append(rabbit)
    print(f"✅ 創建動物: {rabbit.animal_type.value} 在位置 ({rabbit.x}, {rabbit.y})")
    
    # 3. 直接創建子彈（跳過玩家物件）
    from src.systems.shooting_system import Bullet
    player_pos = (50, 50)
    target_pos = (100, 100)  # 動物位置
    
    print(f"🔫 從 {player_pos} 射擊，目標 {target_pos}")
    bullet = Bullet(player_pos, target_pos, damage=10)
    shooting_system.bullets.append(bullet)
    
    # 4. 檢查子彈狀態
    bullet_count = len(shooting_system.bullets)
    print(f"當前子彈數: {bullet_count}")
    
    if bullet_count > 0:
        bullet = shooting_system.bullets[0]
        print(f"子彈位置: ({bullet.x:.1f}, {bullet.y:.1f})")
        print(f"子彈速度: ({bullet.velocity_x:.1f}, {bullet.velocity_y:.1f})")
        print(f"子彈傷害: {bullet.damage}")
    
    # 5. 更新子彈位置（模擬多幀更新）
    print("\n🕐 模擬時間流逝...")
    for frame in range(30):  # 模擬30幀
        dt = 1/60  # 60 FPS
        shooting_system.update(dt)
        
        if len(shooting_system.bullets) > 0:
            bullet = shooting_system.bullets[0]
            
            # 檢查碰撞
            hit_results = shooting_system.check_bullet_collisions(animals)
            
            if hit_results:
                print(f"💥 第{frame+1}幀: 發生碰撞!")
                for hit in hit_results:
                    target = hit['target']
                    damage = hit['damage']
                    print(f"   命中 {target.animal_type.value}，造成 {damage} 傷害")
                    print(f"   {target.animal_type.value} 生命值: {target.health}/{target.max_health}")
                break
            elif frame % 10 == 0:  # 每10幀顯示一次位置
                print(f"第{frame+1}幀: 子彈位置 ({bullet.x:.1f}, {bullet.y:.1f})")
        else:
            print(f"第{frame+1}幀: 子彈已消失")
            break
    
    # 6. 檢查最終狀態
    print(f"\n📊 最終狀態:")
    print(f"剩餘子彈: {len(shooting_system.bullets)}")
    print(f"動物健康: {rabbit.health}/{rabbit.max_health}")
    print(f"動物存活: {'是' if rabbit.is_alive else '否'}")
    
    # 7. 統計信息
    stats = shooting_system.get_statistics()
    print(f"\n📈 射擊統計:")
    print(f"發射次數: {stats['shots_fired']}")
    print(f"命中次數: {stats['hits_count']}")
    print(f"命中率: {stats['accuracy']:.1f}%")
    
    pygame.quit()
    print("\n🎯 測試完成!")

if __name__ == "__main__":
    test_simple_shooting()