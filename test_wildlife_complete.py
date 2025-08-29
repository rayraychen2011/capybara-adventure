#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
野生動物系統完整測試腳本\n
測試子彈軌跡、水陸限制、熊的領地、基於距離的稀有度分佈\n
"""

import pygame
import sys
import os

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import *
from src.systems.shooting_system import ShootingSystem
from src.systems.wildlife.wildlife_manager import WildlifeManager
from src.systems.wildlife.animal_data import AnimalType, RarityLevel
from src.player.player import Player

# 模擬地形系統
class MockTerrainSystem:
    def __init__(self):
        self.grid_width = 100
        self.grid_height = 100
        # 創建簡單的地形圖：中心是小鎮，周圍是森林、草地、水體
        self.terrain_grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # 設置地形
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # 小鎮中心區域（住宅）
                if 40 <= x <= 60 and 40 <= y <= 60:
                    self.terrain_grid[y][x] = 5  # 住宅區
                # 水體（湖泊）
                elif 20 <= x <= 35 and 30 <= y <= 50:
                    self.terrain_grid[y][x] = 2  # 水體
                # 森林
                elif x < 30 or x > 70 or y < 30 or y > 70:
                    self.terrain_grid[y][x] = 1  # 森林
                # 山丘
                elif (x < 20 and y < 20) or (x > 80 and y > 80):
                    self.terrain_grid[y][x] = 9  # 山丘
                # 其他是草地
                else:
                    self.terrain_grid[y][x] = 0  # 草地
    
    def get_terrain_at(self, x, y):
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            return self.terrain_grid[y][x]
        return 0

def main():
    """主測試函數"""
    pygame.init()
    
    # 創建顯示窗口
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("野生動物系統測試")
    clock = pygame.time.Clock()
    
    # 創建測試物件
    shooting_system = ShootingSystem()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    wildlife_manager = WildlifeManager()
    
    # 設置模擬地形系統
    terrain_system = MockTerrainSystem()
    wildlife_manager.set_terrain_system(terrain_system)
    wildlife_manager.set_world_bounds((0, 0, 2000, 2000))
    
    # 初始化動物
    wildlife_manager.initialize_animals()
    
    # 攝影機偏移
    camera_offset = [0, 0]
    
    print("野生動物系統測試開始...")
    print("操作說明：")
    print("- WASD：移動攝影機")
    print("- 左鍵：射擊（測試子彈軌跡）")
    print("- 空白鍵：切換熊的領地顯示")
    print("- R：重新生成動物")
    print("- ESC：退出")
    
    show_territory = True
    
    running = True
    while running:
        dt = clock.get_time() / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    show_territory = not show_territory
                    print(f"熊的領地顯示: {'開啟' if show_territory else '關閉'}")
                elif event.key == pygame.K_r:
                    print("重新生成動物...")
                    wildlife_manager.initialize_animals()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左鍵射擊
                    # 將螢幕座標轉換為世界座標
                    world_x = event.pos[0] + camera_offset[0]
                    world_y = event.pos[1] + camera_offset[1]
                    shooting_system.handle_mouse_shoot(player, event.pos, tuple(camera_offset))
        
        # 處理按鍵（攝影機移動）
        keys = pygame.key.get_pressed()
        camera_speed = 200 * dt
        if keys[pygame.K_w]:
            camera_offset[1] -= camera_speed
        if keys[pygame.K_s]:
            camera_offset[1] += camera_speed
        if keys[pygame.K_a]:
            camera_offset[0] -= camera_speed
        if keys[pygame.K_d]:
            camera_offset[0] += camera_speed
        
        # 更新系統
        shooting_system.update(dt)
        wildlife_manager.update(dt, (player.x, player.y), "town")
        
        # 繪製
        screen.fill((34, 139, 34))  # 森林綠背景
        
        # 繪製簡化的地形
        for y in range(0, terrain_system.grid_height, 5):  # 每5格繪製一次，提高性能
            for x in range(0, terrain_system.grid_width, 5):
                screen_x = x * 20 - camera_offset[0]
                screen_y = y * 20 - camera_offset[1]
                
                if -40 <= screen_x <= SCREEN_WIDTH + 40 and -40 <= screen_y <= SCREEN_HEIGHT + 40:
                    terrain_code = terrain_system.get_terrain_at(x, y)
                    color = {
                        0: (144, 238, 144),  # 草地 - 淺綠
                        1: (34, 139, 34),    # 森林 - 深綠
                        2: (0, 191, 255),    # 水體 - 藍色
                        5: (255, 228, 181),  # 住宅 - 淺橘
                        9: (160, 82, 45)     # 山丘 - 棕色
                    }.get(terrain_code, (128, 128, 128))
                    
                    pygame.draw.rect(screen, color, (screen_x, screen_y, 20, 20))
        
        # 繪製動物（包含熊的領地）
        for animal in wildlife_manager.animals:
            animal.draw(screen, tuple(camera_offset), show_territory=show_territory)
        
        # 繪製子彈軌跡
        shooting_system.draw_bullets(screen, tuple(camera_offset))
        
        # 繪製玩家
        player_screen_x = int(player.x - camera_offset[0])
        player_screen_y = int(player.y - camera_offset[1])
        pygame.draw.circle(screen, (255, 255, 0), (player_screen_x, player_screen_y), 15)
        
        # 顯示統計信息
        font = pygame.font.Font(None, 24)
        stats = wildlife_manager.get_wildlife_statistics()
        info_texts = [
            f"攝影機位置: ({camera_offset[0]:.0f}, {camera_offset[1]:.0f})",
            f"動物總數: {len(wildlife_manager.animals)}",
            f"稀有動物: {wildlife_manager.current_counts.get(RarityLevel.RARE, 0)}",
            f"超稀動物: {wildlife_manager.current_counts.get(RarityLevel.SUPER_RARE, 0)}",
            f"傳奇動物: {wildlife_manager.current_counts.get(RarityLevel.LEGENDARY, 0)}",
            f"子彈數: {len(shooting_system.bullets)}",
            f"領地顯示: {'開啟' if show_territory else '關閉'}"
        ]
        
        for i, text in enumerate(info_texts):
            surface = font.render(text, True, (255, 255, 255))
            screen.blit(surface, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("測試結束")

if __name__ == "__main__":
    main()