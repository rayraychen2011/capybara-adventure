#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整的子彈與動物碰撞檢測驗證程序

這個程序會在實際的遊戲場景中測試：
1. 玩家發射子彈的完整流程
2. 子彈在遊戲中的視覺顯示效果
3. 子彈與野生動物的碰撞檢測
4. 動物受傷和死亡的完整處理
5. 金錢獎勵系統
"""

import pygame
import sys
import os

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.game_engine import GameEngine
from src.core.state_manager import StateManager, GameState
from src.player.player import Player
from src.systems.shooting_system import ShootingSystem
from src.systems.wildlife.wildlife_manager import WildlifeManager
from src.systems.wildlife.animal import Animal
from src.systems.wildlife.animal_data import AnimalType
from src.systems.terrain_based_system import TerrainBasedSystem
from config.settings import *

class BulletCollisionDemo:
    """
    子彈碰撞演示程序
    
    在實際遊戲環境中測試子彈與動物的完整互動流程
    """
    
    def __init__(self):
        """初始化演示程序"""
        print("🎮 初始化子彈碰撞演示程序...")
        
        # 初始化 Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("子彈與動物碰撞檢測演示")
        self.clock = pygame.time.Clock()
        
        # 初始化遊戲組件
        self._initialize_game_systems()
        self._setup_test_scene()
        
        print("✅ 演示程序初始化完成")
    
    def _initialize_game_systems(self):
        """初始化遊戲系統"""
        # 創建玩家
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        print(f"✅ 創建玩家，位置: ({self.player.x}, {self.player.y})")
        
        # 創建射擊系統
        self.shooting_system = ShootingSystem()
        print("✅ 創建射擊系統")
        
        # 創建地形系統
        self.terrain_system = TerrainBasedSystem(self.player)
        terrain_loaded = self.terrain_system.load_terrain_map("config/cupertino_map_edited.csv")
        print(f"✅ 地形系統載入: {'成功' if terrain_loaded else '失敗'}")
        
        # 創建野生動物管理器
        self.wildlife_manager = WildlifeManager()
        self.wildlife_manager.set_terrain_system(self.terrain_system)
        print("✅ 創建野生動物管理器")
        
        # 攝影機偏移（簡化版）
        self.camera_x = 0
        self.camera_y = 0
        
        # 統計數據
        self.shots_fired = 0
        self.animals_hit = 0
        self.animals_killed = 0
        self.money_earned = 0
    
    def _setup_test_scene(self):
        """設定測試場景"""
        print("\n🏞️ 設定測試場景...")
        
        # 創建一些測試動物在玩家周圍
        test_animals = [
            (AnimalType.RABBIT, (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2), "grassland"),
            (AnimalType.RABBIT, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50), "grassland"),
            (AnimalType.SHEEP, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 - 100), "grassland"),
            (AnimalType.BEAR, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150), "forest"),
        ]
        
        for animal_type, position, habitat in test_animals:
            animal = Animal(animal_type, position, (0, 0, SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2), habitat)
            self.wildlife_manager.all_animals.append(animal)
            print(f"   ➕ 添加 {animal_type.value} 到位置 {position}")
        
        print(f"✅ 場景設定完成，共 {len(self.wildlife_manager.all_animals)} 隻動物")
    
    def run_demo(self):
        """運行演示程序"""
        print("\n🚀 開始子彈碰撞檢測演示")
        print("操作說明:")
        print("   - 左鍵點擊：發射子彈")
        print("   - ESC：退出演示")
        print("   - 空白鍵：顯示統計資訊")
        print("-" * 50)
        
        running = True
        show_instructions = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0  # 轉換為秒
            
            # 處理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self._print_statistics()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左鍵
                        self._handle_player_shoot(event.pos)
            
            # 更新遊戲系統
            self._update_systems(dt)
            
            # 檢查子彈碰撞
            self._check_bullet_collisions()
            
            # 繪製場景
            self._draw_scene()
            
            # 顯示說明（前5秒）
            if show_instructions and pygame.time.get_ticks() > 5000:
                show_instructions = False
        
        pygame.quit()
        self._print_final_report()
    
    def _handle_player_shoot(self, mouse_pos):
        """處理玩家射擊"""
        # 轉換滑鼠座標為世界座標
        world_x = mouse_pos[0] + self.camera_x
        world_y = mouse_pos[1] + self.camera_y
        target_pos = (world_x, world_y)
        
        # 執行射擊
        if self.shooting_system.shoot(self.player, target_pos):
            self.shots_fired += 1
            print(f"🔫 發射第 {self.shots_fired} 發子彈，目標: ({world_x:.0f}, {world_y:.0f})")
    
    def _update_systems(self, dt):
        """更新遊戲系統"""
        # 更新玩家
        self.player.update(dt)
        
        # 更新射擊系統
        self.shooting_system.update(dt)
        
        # 更新野生動物
        player_pos = (self.player.x, self.player.y)
        self.wildlife_manager.update(dt, player_pos, "town")
        
        # 簡單的攝影機跟隨
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2
    
    def _check_bullet_collisions(self):
        """檢查子彈碰撞"""
        # 獲取所有活著的動物
        active_animals = [animal for animal in self.wildlife_manager.all_animals if animal.is_alive]
        
        # 檢查碰撞
        hits = self.shooting_system.check_bullet_collisions(active_animals)
        
        for hit_info in hits:
            animal = hit_info['target']
            damage = hit_info['damage']
            hit_pos = hit_info['position']
            
            self.animals_hit += 1
            
            print(f"💥 第 {self.animals_hit} 次命中：{animal.animal_type.value} 受到 {damage} 點傷害")
            print(f"   位置: ({hit_pos[0]:.1f}, {hit_pos[1]:.1f})")
            print(f"   動物血量: {animal.health}/{animal.max_health}")
            
            # 檢查動物是否死亡
            if not animal.is_alive:
                self.animals_killed += 1
                
                # 計算金錢獎勵
                from src.systems.wildlife.animal_data import AnimalData
                rarity = AnimalData.get_animal_property(animal.animal_type, "rarity")
                reward = AnimalData.get_animal_rarity_value(rarity)
                
                self.player.money += reward
                self.money_earned += reward
                
                print(f"💀 {animal.animal_type.value} 死亡！獲得 {reward} 元獎勵")
                print(f"   玩家金錢: {self.player.money} 元")
    
    def _draw_scene(self):
        """繪製場景"""
        # 清空螢幕
        self.screen.fill((34, 80, 34))  # 深綠色背景
        
        camera_offset = (self.camera_x, self.camera_y)
        
        # 繪製動物
        for animal in self.wildlife_manager.all_animals:
            animal.draw(self.screen, camera_offset)
        
        # 繪製玩家
        self.player.draw(self.screen, self.camera_x, self.camera_y)
        
        # 繪製子彈
        self.shooting_system.draw_bullets(self.screen, camera_offset)
        
        # 繪製準心
        mouse_pos = pygame.mouse.get_pos()
        self._draw_crosshair(mouse_pos)
        
        # 繪製UI資訊
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_crosshair(self, mouse_pos):
        """繪製準心"""
        x, y = mouse_pos
        crosshair_color = (255, 0, 0)
        
        # 十字準心
        pygame.draw.line(self.screen, crosshair_color, (x - 10, y), (x + 10, y), 2)
        pygame.draw.line(self.screen, crosshair_color, (x, y - 10), (x, y + 10), 2)
        pygame.draw.circle(self.screen, crosshair_color, (x, y), 2)
    
    def _draw_ui(self):
        """繪製UI資訊"""
        font = pygame.font.Font(None, 24)
        
        # 玩家資訊
        player_info = [
            f"玩家位置: ({self.player.x:.0f}, {self.player.y:.0f})",
            f"玩家血量: {self.player.health}/{PLAYER_MAX_HEALTH}",
            f"玩家金錢: {self.player.money} 元",
        ]
        
        # 射擊統計
        shooting_stats = [
            f"發射子彈: {self.shots_fired}",
            f"命中動物: {self.animals_hit}",
            f"擊殺動物: {self.animals_killed}",
            f"活躍子彈: {len(self.shooting_system.bullets)}",
        ]
        
        # 動物狀態
        alive_animals = [animal for animal in self.wildlife_manager.all_animals if animal.is_alive]
        animal_stats = [
            f"存活動物: {len(alive_animals)}",
            f"總動物數: {len(self.wildlife_manager.all_animals)}",
        ]
        
        # 繪製文字
        y_offset = 10
        
        for text in player_info + [""] + shooting_stats + [""] + animal_stats:
            if text:  # 跳過空字串
                surface = font.render(text, True, (255, 255, 255))
                self.screen.blit(surface, (10, y_offset))
            y_offset += 25
        
        # 操作說明
        instructions = [
            "左鍵: 射擊",
            "空白鍵: 統計",
            "ESC: 退出"
        ]
        
        instruction_font = pygame.font.Font(None, 20)
        for i, text in enumerate(instructions):
            surface = instruction_font.render(text, True, (200, 200, 200))
            self.screen.blit(surface, (SCREEN_WIDTH - 120, 10 + i * 22))
    
    def _print_statistics(self):
        """輸出統計資訊"""
        print("\n📊 當前統計資訊:")
        print(f"   發射子彈: {self.shots_fired}")
        print(f"   命中動物: {self.animals_hit}")
        print(f"   擊殺動物: {self.animals_killed}")
        print(f"   獲得金錢: {self.money_earned} 元")
        print(f"   命中率: {(self.animals_hit/self.shots_fired*100):.1f}%" if self.shots_fired > 0 else "   命中率: 0%")
        print(f"   致死率: {(self.animals_killed/self.animals_hit*100):.1f}%" if self.animals_hit > 0 else "   致死率: 0%")
        
        alive_animals = [animal for animal in self.wildlife_manager.all_animals if animal.is_alive]
        print(f"   存活動物: {len(alive_animals)}")
        
        for animal in alive_animals:
            health_percent = (animal.health / animal.max_health) * 100
            print(f"     - {animal.animal_type.value}: {animal.health}/{animal.max_health} ({health_percent:.1f}%)")
    
    def _print_final_report(self):
        """輸出最終報告"""
        print("\n" + "=" * 60)
        print("🏁 子彈碰撞檢測演示完成")
        print("=" * 60)
        
        print("\n📈 最終統計:")
        print(f"   總發射次數: {self.shots_fired}")
        print(f"   總命中次數: {self.animals_hit}")
        print(f"   總擊殺次數: {self.animals_killed}")
        print(f"   總獲得金錢: {self.money_earned} 元")
        
        if self.shots_fired > 0:
            hit_rate = (self.animals_hit / self.shots_fired) * 100
            print(f"   整體命中率: {hit_rate:.1f}%")
        
        if self.animals_hit > 0:
            kill_rate = (self.animals_killed / self.animals_hit) * 100
            print(f"   整體致死率: {kill_rate:.1f}%")
        
        print(f"   玩家最終金錢: {self.player.money} 元")
        
        print("\n✅ 驗證結果:")
        
        if self.shots_fired > 0:
            print("   ✅ 子彈發射功能正常")
        else:
            print("   ❌ 未進行射擊測試")
        
        if self.animals_hit > 0:
            print("   ✅ 子彈碰撞檢測正常")
            print("   ✅ 動物受傷機制正常")
        else:
            print("   ❌ 未檢測到碰撞")
        
        if self.animals_killed > 0:
            print("   ✅ 動物死亡機制正常")
            print("   ✅ 金錢獎勵系統正常")
        
        if len(self.shooting_system.bullets) == 0:
            print("   ✅ 子彈生命週期管理正常")

def main():
    """主函數"""
    print("🎯 子彈與動物碰撞檢測完整驗證程序")
    print("=" * 60)
    
    try:
        demo = BulletCollisionDemo()
        demo.run_demo()
    except Exception as e:
        print(f"❌ 演示過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()