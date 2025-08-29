"""
戰鬥系統演示 - 展示所有新的戰鬥功能

演示項目:
1. 武器切換 (1=槍, 2=空手)
2. 射擊攻擊動物
3. 動物行為反應 (逃跑/攻擊)
4. 玩家血量和死亡機制
"""

import sys
import os
import pygame
import random
import math

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.player.player import Player
from src.systems.weapon_system import WeaponManager
from src.systems.wildlife.wildlife_manager import WildlifeManager
from src.systems.wildlife.animal import Animal, AnimalState
from src.systems.wildlife.animal_data import AnimalType, RarityLevel, AnimalData

def demo_combat_system():
    """演示戰鬥系統的所有功能"""
    print("=== 戰鬥系統演示 ===\n")
    
    # 初始化 Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("戰鬥系統演示")
    clock = pygame.time.Clock()
    
    # 創建系統
    player = Player(400, 300)
    wildlife_manager = WildlifeManager()
    
    # 設置攻擊回調
    def handle_animal_attack(damage, source_animal):
        """處理動物攻擊玩家的回調"""
        if player.take_damage(damage, source_animal):
            print(f"玩家被 {source_animal.animal_type.value} 攻擊，受到 {damage} 點傷害！")
            print(f"玩家剩餘血量: {player.health}")
            
            if not player.is_alive:
                print("玩家已死亡，正在傳送到醫院...")
    
    wildlife_manager.set_player_attack_callback(handle_animal_attack)
    
    # 創建測試動物
    habitat_bounds = (0, 0, 800, 600)
    test_animals = []
    
    # 在玩家周圍放置不同類型的動物
    animals_to_create = [
        (AnimalType.RABBIT, (200, 200), "稀有動物 - 會逃跑"),
        (AnimalType.MOUNTAIN_LION, (600, 300), "超稀有動物 - 會攻擊"),
        (AnimalType.BEAR, (400, 500), "傳奇動物 - 領地攻擊")
    ]
    
    for animal_type, position, description in animals_to_create:
        animal = Animal(animal_type, position, habitat_bounds, "forest")
        test_animals.append(animal)
        wildlife_manager.all_animals.append(animal)
        print(f"創建了 {description} 在位置 {position}")
    
    print(f"\n玩家初始位置: ({player.x}, {player.y})")
    print(f"玩家初始血量: {player.health}/{player.max_health}")
    print(f"當前武器: {player.weapon_manager.current_weapon.name if player.weapon_manager.current_weapon else '無'}")
    
    print("\n=== 控制說明 ===")
    print("1 - 切換到槍")
    print("2 - 切換到空手")
    print("滑鼠左鍵 - 射擊")
    print("WASD - 移動")
    print("ESC - 退出")
    print("H - 恢復血量")
    print("=================\n")
    
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    player.weapon_manager.switch_weapon("pistol")
                    print(f"切換到: {player.weapon_manager.current_weapon.name}")
                elif event.key == pygame.K_2:
                    player.weapon_manager.switch_weapon("unarmed")
                    print(f"切換到: {player.weapon_manager.current_weapon.name}")
                elif event.key == pygame.K_h:
                    player.heal(100)
                    print(f"恢復血量，當前: {player.health}/{player.max_health}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左鍵射擊
                    if player.weapon_manager.current_weapon:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        player_pos = (player.x, player.y)
                        target_pos = (mouse_x, mouse_y)
                        
                        weapon = player.weapon_manager.current_weapon
                        result = weapon.shoot(target_pos, player_pos)
                        
                        if result['success']:
                            print(f"使用 {weapon.name} 射擊！")
                            
                            if result['hit']:
                                # 檢查是否擊中動物
                                animal_result = wildlife_manager.handle_player_shoot(
                                    player_pos, target_pos, result['damage'], weapon.range
                                )
                                
                                if animal_result['hit_animal']:
                                    animal = animal_result['hit_animal']
                                    damage = animal_result['damage_dealt']
                                    is_kill = animal_result['kill']
                                    
                                    if is_kill:
                                        print(f"擊殺了 {animal.animal_type.value}！")
                                    else:
                                        print(f"擊中了 {animal.animal_type.value}，造成 {damage} 點傷害！")
                                        print(f"動物狀態: {animal.state.value}")
                                else:
                                    print("射擊命中但沒有擊中任何動物")
                            else:
                                print("射擊脫靶！")
                        else:
                            print("無法射擊")
        
        # 處理移動
        keys = pygame.key.get_pressed()
        move_x = move_y = 0
        if keys[pygame.K_a]:
            move_x = -1
        if keys[pygame.K_d]:
            move_x = 1
        if keys[pygame.K_w]:
            move_y = -1
        if keys[pygame.K_s]:
            move_y = 1
        
        if move_x != 0 or move_y != 0:
            # 標準化移動向量
            length = math.sqrt(move_x * move_x + move_y * move_y)
            move_x /= length
            move_y /= length
            
            # 移動玩家
            speed = 100  # 像素/秒
            new_x = player.x + move_x * speed * dt
            new_y = player.y + move_y * speed * dt
            
            # 邊界檢查
            new_x = max(20, min(780, new_x))
            new_y = max(20, min(580, new_y))
            
            player.x = new_x
            player.y = new_y
        
        # 更新動物
        for animal in wildlife_manager.all_animals[:]:
            if animal.is_alive:
                animal.update(dt, (player.x, player.y))
                
                # 檢查動物是否攻擊了玩家
                if hasattr(animal, 'has_attacked_player') and animal.has_attacked_player:
                    wildlife_manager._handle_animal_attack_player(animal, (player.x, player.y))
                    animal.has_attacked_player = False  # 重置攻擊標記
        
        # 繪製
        screen.fill((50, 100, 50))  # 綠色背景
        
        # 繪製動物
        for animal in wildlife_manager.all_animals:
            if animal.is_alive:
                # 動物顏色
                color = animal.color
                
                # 根據狀態調整顏色
                if animal.state == AnimalState.FLEEING:
                    color = (255, 255, 0)  # 黃色表示逃跑
                elif animal.state == AnimalState.ATTACKING:
                    color = (255, 0, 0)  # 紅色表示攻擊
                elif animal.state == AnimalState.ALERT:
                    color = (255, 165, 0)  # 橙色表示警戒
                
                # 繪製動物
                pygame.draw.circle(screen, color, (int(animal.x), int(animal.y)), animal.size)
                
                # 繪製血量條
                if animal.health < animal.max_health:
                    bar_width = 30
                    bar_height = 4
                    bar_x = int(animal.x - bar_width // 2)
                    bar_y = int(animal.y - animal.size - 10)
                    
                    # 背景條（紅色）
                    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                    
                    # 血量條（綠色）
                    health_ratio = animal.health / animal.max_health
                    health_width = int(bar_width * health_ratio)
                    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
                
                # 繪製名稱
                name_text = small_font.render(animal.animal_type.value, True, (255, 255, 255))
                name_rect = name_text.get_rect(center=(int(animal.x), int(animal.y - animal.size - 20)))
                screen.blit(name_text, name_rect)
                
                # 繪製領地範圍（僅對傳奇動物）
                if animal.rarity == RarityLevel.LEGENDARY and animal.territory_range > 0:
                    pygame.draw.circle(screen, (255, 255, 255), (int(animal.x), int(animal.y)), 
                                     int(animal.territory_range), 2)
        
        # 繪製玩家
        player_color = (0, 0, 255)  # 藍色
        if not player.is_alive:
            player_color = (128, 128, 128)  # 灰色表示死亡
        
        pygame.draw.circle(screen, player_color, (int(player.x), int(player.y)), 10)
        
        # 繪製準星
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.line(screen, (255, 255, 255), (mouse_x - 10, mouse_y), (mouse_x + 10, mouse_y), 2)
        pygame.draw.line(screen, (255, 255, 255), (mouse_x, mouse_y - 10), (mouse_x, mouse_y + 10), 2)
        
        # 繪製射程圓圈（如果有武器）
        if player.weapon_manager.current_weapon:
            weapon_range = player.weapon_manager.current_weapon.range
            pygame.draw.circle(screen, (255, 255, 255), (int(player.x), int(player.y)), 
                             int(weapon_range), 1)
        
        # 繪製UI
        y_offset = 10
        
        # 玩家血量
        health_text = font.render(f"血量: {player.health}/{player.max_health}", True, (255, 255, 255))
        screen.blit(health_text, (10, y_offset))
        y_offset += 30
        
        # 當前武器
        if player.weapon_manager.current_weapon:
            weapon = player.weapon_manager.current_weapon
            weapon_text = font.render(f"武器: {weapon.name} (傷害: {weapon.damage})", True, (255, 255, 255))
            screen.blit(weapon_text, (10, y_offset))
            y_offset += 25
            
            # 彈藥
            if weapon.weapon_type != "unarmed":
                ammo_text = small_font.render(f"彈藥: {weapon.current_ammo}/{weapon.magazine_size}", True, (255, 255, 255))
                screen.blit(ammo_text, (10, y_offset))
                y_offset += 20
        
        # 動物狀態
        y_offset += 10
        for i, animal in enumerate(wildlife_manager.all_animals):
            if animal.is_alive:
                status_text = small_font.render(
                    f"{animal.animal_type.value}: {animal.state.value} (血量: {animal.health})", 
                    True, (255, 255, 255)
                )
                screen.blit(status_text, (10, y_offset))
                y_offset += 20
        
        pygame.display.flip()
    
    pygame.quit()
    print("\n演示結束")

if __name__ == "__main__":
    demo_combat_system()