"""
測試戰鬥系統 - 驗證所有新的戰鬥功能

測試項目:
1. 玩家射擊動物系統
2. 動物受傷和死亡機制
3. 不同稀有度動物的行為反應
4. 玩家受攻擊和血量系統
5. 玩家死亡傳送到醫院
"""

import sys
import os
import pygame
import random
import math

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.player.player import Player
from src.systems.weapon_system import Weapon, WeaponManager
from src.systems.wildlife.wildlife_manager import WildlifeManager
from src.systems.wildlife.animal import Animal, AnimalState
from src.systems.wildlife.animal_data import AnimalType, RarityLevel
from src.systems.terrain_based_system import TerrainBasedSystem

def test_combat_system():
    """測試戰鬥系統的各項功能"""
    print("=== 戰鬥系統測試開始 ===\n")
    
    # 初始化 Pygame（需要用於某些系統）
    pygame.init()
    
    # 1. 測試武器系統
    print("1. 測試武器系統")
    print("-" * 30)
    
    weapon_manager = WeaponManager()
    
    # 測試槍械
    weapon_manager.switch_weapon("pistol")
    gun = weapon_manager.current_weapon
    if gun:
        print(f"槍械: {gun.name}, 傷害: {gun.damage}, 射程: {gun.range}")
        
        # 測試射擊
        player_pos = (100, 100)
        target_pos = (150, 150)
        result = gun.shoot(target_pos, player_pos)
        print(f"射擊結果: 成功={result['success']}, 命中={result['hit']}, 傷害={result['damage']}")
    
    # 測試空手
    weapon_manager.switch_weapon("unarmed")
    unarmed = weapon_manager.current_weapon
    if unarmed:
        print(f"空手: {unarmed.name}, 傷害: {unarmed.damage}, 射程: {unarmed.range}")
    
    print()
    
    # 2. 測試玩家血量系統
    print("2. 測試玩家血量系統")
    print("-" * 30)
    
    player = Player(500, 500)
    print(f"玩家初始血量: {player.health}/{player.max_health}")
    
    # 測試受傷
    import time
    player.take_damage(50, None)
    print(f"受傷後血量: {player.health}/{player.max_health}")
    
    # 等待一下以避免無敵時間
    time.sleep(0.1)
    
    # 測試死亡和傳送到醫院
    player.take_damage(300, None)  # 致命傷害
    print(f"死亡後血量: {player.health}, 存活狀態: {player.is_alive}")
    print(f"玩家位置: ({player.x}, {player.y})")
    
    print()
    
    # 3. 測試動物戰鬥屬性
    print("3. 測試動物戰鬥屬性")
    print("-" * 30)
    
    # 創建不同稀有度的動物進行測試
    animals_to_test = [
        (AnimalType.RABBIT, "稀有動物 - 兔子"),
        (AnimalType.MOUNTAIN_LION, "超稀有動物 - 山獅"),
        (AnimalType.BEAR, "傳奇動物 - 熊")
    ]
    
    for animal_type, description in animals_to_test:
        print(f"\n{description}:")
        
        # 創建動物
        habitat_bounds = (0, 0, 1000, 1000)
        animal = Animal(animal_type, (300, 300), habitat_bounds, "forest")
        
        print(f"  血量: {animal.health}")
        print(f"  傷害: {animal.damage}")
        print(f"  敏捷: {animal.agility}")
        print(f"  攻擊範圍: {animal.attack_range}")
        print(f"  領地範圍: {animal.territory_range}")
        print(f"  稀有度: {animal.rarity.value if animal.rarity else 'None'}")
        
        # 測試受傷反應
        original_state = animal.state
        animal.take_damage(30, player)
        print(f"  受傷前狀態: {original_state.value}")
        print(f"  受傷後狀態: {animal.state.value}")
        print(f"  受傷後血量: {animal.health}")
        print(f"  存活狀態: {animal.is_alive}")
    
    print()
    
    # 4. 測試野生動物管理器的射擊系統
    print("4. 測試野生動物管理器射擊系統")
    print("-" * 30)
    
    # 創建野生動物管理器
    wildlife_manager = WildlifeManager()
    
    # 手動創建一些動物用於測試
    test_animals = []
    for i, animal_type in enumerate([AnimalType.RABBIT, AnimalType.MOUNTAIN_LION, AnimalType.BEAR]):
        animal = Animal(animal_type, (200 + i * 100, 200), habitat_bounds, "forest")
        test_animals.append(animal)
        wildlife_manager.all_animals.append(animal)
    
    print(f"創建了 {len(test_animals)} 隻測試動物")
    
    # 測試射擊
    player_pos = (100, 100)
    target_pos = (200, 200)  # 直接瞄準第一隻動物的位置
    weapon_damage = 50
    weapon_range = 300
    
    print(f"玩家位置: {player_pos}")
    print(f"射擊目標: {target_pos}")
    print(f"動物位置: {[(animal.x, animal.y) for animal in test_animals]}")
    
    result = wildlife_manager.handle_player_shoot(player_pos, target_pos, weapon_damage, weapon_range)
    
    if result['hit_animal']:
        animal = result['hit_animal']
        print(f"擊中了 {animal.animal_type.value}!")
        print(f"造成傷害: {result['damage_dealt']}")
        print(f"是否擊殺: {result['kill']}")
        print(f"動物當前血量: {animal.health}")
        print(f"動物狀態: {animal.state.value}")
    else:
        print("沒有擊中任何動物")
    
    print()
    
    # 5. 測試動物攻擊玩家
    print("5. 測試動物攻擊玩家")
    print("-" * 30)
    
    # 創建一隻熊進行攻擊測試（放置在玩家附近）
    bear = Animal(AnimalType.BEAR, (player.x + 20, player.y + 20), habitat_bounds, "forest")
    print(f"熊的攻擊傷害: {bear.damage}")
    print(f"熊的攻擊範圍: {bear.attack_range}")
    print(f"玩家位置: ({player.x}, {player.y})")
    print(f"熊的位置: ({bear.x}, {bear.y})")
    
    # 計算距離
    distance = math.sqrt((bear.x - player.x)**2 + (bear.y - player.y)**2)
    print(f"玩家與熊的距離: {distance}")
    
    # 重置玩家血量進行測試
    player.health = 200
    player.is_alive = True
    
    print(f"玩家測試前血量: {player.health}")
    
    # 讓熊攻擊玩家
    attack_success = bear.attack_player((player.x, player.y))
    
    if attack_success:
        print("熊攻擊成功!")
        print(f"熊攻擊標記: {bear.has_attacked_player}")
        print(f"預期傷害: {bear.damage}")
        
        # 模擬玩家受到攻擊
        player.take_damage(bear.damage, bear)
        print(f"玩家受攻擊後血量: {player.health}")
    else:
        print("熊攻擊失敗（可能距離太遠或冷卻中）")
    
    print()
    
    # 6. 測試不同稀有度動物的行為模式
    print("6. 測試動物行為模式")
    print("-" * 30)
    
    for animal in test_animals:
        print(f"\n{animal.animal_type.value} (稀有度: {animal.rarity.value if animal.rarity else 'None'}):")
        
        # 模擬玩家靠近
        original_state = animal.state
        animal.update(0.1, (animal.x + 50, animal.y + 50))  # 玩家在附近
        
        print(f"  玩家靠近前狀態: {original_state.value}")
        print(f"  玩家靠近後狀態: {animal.state.value}")
        
        # 測試受攻擊反應
        animal.take_damage(20, player)
        print(f"  受攻擊後狀態: {animal.state.value}")
    
    print("\n=== 戰鬥系統測試完成 ===")
    
    # 清理 Pygame
    pygame.quit()

if __name__ == "__main__":
    test_combat_system()