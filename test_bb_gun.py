######################測試BB槍系統######################
import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.systems.shooting_system import ShootingSystem, BBGun
from src.player.player import Player
from config.settings import *

def test_bb_gun():
    """
    測試BB槍系統 - 簡化版測試\n
    """
    print("=== BB槍系統測試 ===")
    
    # 初始化 pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("BB槍測試")
    clock = pygame.time.Clock()
    
    # 創建射擊系統和玩家
    shooting_system = ShootingSystem()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    # 創建BB槍
    bb_gun = BBGun()
    print(f"BB槍設定: {bb_gun.name}, 射速: {bb_gun.fire_rate} 發/秒")
    
    running = True
    last_time = pygame.time.get_ticks()
    
    print("按住滑鼠左鍵測試BB槍全自動射擊...")
    print("按 ESC 鍵退出")
    
    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0
        last_time = current_time
        
        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 檢查滑鼠按鍵狀態
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # 左鍵按住
            mouse_pos = pygame.mouse.get_pos()
            shooting_system.handle_mouse_shoot(player, mouse_pos, (0, 0))
        
        # 更新系統
        shooting_system.update(dt)
        
        # 繪製
        screen.fill((135, 206, 235))  # 天空藍背景
        
        # 繪製玩家（橘色方塊）
        pygame.draw.rect(screen, PLAYER_COLOR, 
                        (player.x - player.width//2, player.y - player.height//2, 
                         player.width, player.height))
        
        # 繪製子彈
        shooting_system.draw_bullets(screen, (0, 0))
        
        # 繪製射擊UI
        shooting_system.draw_shooting_ui(screen, player)
        
        # 顯示子彈數量
        from src.utils.font_manager import get_font_manager
        font_manager = get_font_manager()
        bullet_count_text = font_manager.render_text_with_outline(f"子彈數量: {len(shooting_system.bullets)}", 24, (255, 255, 255))
        screen.blit(bullet_count_text, (10, 10))
        
        # 顯示射擊統計
        stats = shooting_system.get_statistics()
        stats_text = font_manager.render_text_with_outline(f"已射擊: {stats['shots_fired']} 發", 24, (255, 255, 255))
        screen.blit(stats_text, (10, 50))
        
        # 顯示使用說明
        instruction_text = font_manager.render_text_with_outline("按住滑鼠左鍵射擊 | ESC退出", 20, (255, 255, 0))
        screen.blit(instruction_text, (10, SCREEN_HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    print("測試結束")

if __name__ == "__main__":
    test_bb_gun()