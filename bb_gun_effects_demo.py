######################BB槍特效演示######################
import pygame
import sys
import os
import math
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import *

def main():
    """
    BB槍特效演示 - 展示增強的子彈效果和文字邊框\n
    """
    print("=== BB槍特效演示 ===")
    
    # 初始化 pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("BB槍特效演示")
    clock = pygame.time.Clock()
    
    # 模擬子彈類別（簡化版）
    class DemoBullet:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.radius = 6
            self.color = (255, 255, 100)
            self.glow_intensity = 1.0
            self.sparkle_timer = 0
            self.trail_positions = [(x, y)]
            
        def update(self, dt):
            # 更新閃爍效果
            self.sparkle_timer += dt
            self.glow_intensity = 0.8 + 0.4 * math.sin(self.sparkle_timer * 15)
            
            # 模擬移動
            self.x += 200 * dt  # 向右移動
            
            # 更新拖尾
            self.trail_positions.append((self.x, self.y))
            if len(self.trail_positions) > 12:
                self.trail_positions.pop(0)
        
        def draw(self, screen):
            # 繪製拖尾效果（增強版）
            for i, (trail_x, trail_y) in enumerate(self.trail_positions):
                trail_screen_x = int(trail_x)
                trail_screen_y = int(trail_y)
                
                # 拖尾透明度和大小遞減
                alpha = int(255 * (i + 1) / len(self.trail_positions) * 0.7)
                trail_radius = max(1, self.radius - (len(self.trail_positions) - i - 1))
                
                # 創建拖尾表面
                trail_surface = pygame.Surface((trail_radius * 4, trail_radius * 4), pygame.SRCALPHA)
                
                # 繪製拖尾的外光暈（橘色）
                pygame.draw.circle(trail_surface, (255, 165, 0, alpha // 2), 
                                 (trail_radius * 2, trail_radius * 2), trail_radius + 1)
                
                # 繪製拖尾本體（黃色）
                pygame.draw.circle(trail_surface, (*self.color, alpha), 
                                 (trail_radius * 2, trail_radius * 2), trail_radius)
                
                screen.blit(trail_surface, (trail_screen_x - trail_radius * 2, trail_screen_y - trail_radius * 2))

            # 繪製子彈本體（增強版 - 帶閃爍效果）
            screen_x = int(self.x)
            screen_y = int(self.y)
            
            # 動態光暈強度
            glow_alpha = int(80 * self.glow_intensity)
            
            # 外光暈效果（動態）
            glow_surface = pygame.Surface((self.radius * 8, self.radius * 8), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 100, glow_alpha), 
                             (self.radius * 4, self.radius * 4), int(self.radius * 3 * self.glow_intensity))
            screen.blit(glow_surface, (screen_x - self.radius * 4, screen_y - self.radius * 4))
            
            # 中層光環（橘黃色）
            mid_alpha = int(150 * self.glow_intensity)
            mid_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(mid_surface, (255, 200, 0, mid_alpha), 
                             (self.radius * 2, self.radius * 2), self.radius + 2)
            screen.blit(mid_surface, (screen_x - self.radius * 2, screen_y - self.radius * 2))
            
            # 子彈核心（亮黃色）
            core_color = (min(255, int(255 * self.glow_intensity)), 
                         min(255, int(255 * self.glow_intensity)), 
                         min(255, int(150 * self.glow_intensity)))
            pygame.draw.circle(screen, core_color, (screen_x, screen_y), self.radius)
            
            # 子彈中心高亮點（閃爍）
            if self.glow_intensity > 0.9:
                pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), max(1, self.radius - 3))
    
    # 簡化的字體渲染（帶邊框）
    def render_text_with_outline(text, font, color, outline_color, outline_width=2):
        # 創建表面
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        # 創建帶邊框的表面
        surface_width = text_rect.width + outline_width * 2
        surface_height = text_rect.height + outline_width * 2
        surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
        
        # 渲染邊框
        outline_offsets = [
            (-outline_width, -outline_width), (0, -outline_width), (outline_width, -outline_width),
            (-outline_width, 0), (outline_width, 0),
            (-outline_width, outline_width), (0, outline_width), (outline_width, outline_width)
        ]
        
        outline_surface = font.render(text, True, outline_color)
        for offset_x, offset_y in outline_offsets:
            surface.blit(outline_surface, (outline_width + offset_x, outline_width + offset_y))
        
        # 渲染主文字
        surface.blit(text_surface, (outline_width, outline_width))
        
        return surface
    
    # 創建字體
    font_large = pygame.font.Font(None, 36)
    font_medium = pygame.font.Font(None, 24)
    
    # 創建測試子彈
    bullets = []
    bullet_spawn_timer = 0
    
    running = True
    last_time = pygame.time.get_ticks()
    
    print("BB槍特效演示運行中...")
    print("功能展示：")
    print("✅ 增強的子彈視覺特效（光暈、閃爍、拖尾）")
    print("✅ 白色文字配黑色邊框")
    print("✅ 每秒自動生成子彈演示")
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
        
        # 自動生成子彈（模擬每秒10發）
        bullet_spawn_timer += dt
        if bullet_spawn_timer >= 0.1:  # 0.1秒間隔
            # 在不同高度生成子彈
            y_positions = [200, 250, 300, 350, 400, 450, 500]
            y = y_positions[len(bullets) % len(y_positions)]
            bullets.append(DemoBullet(50, y))
            bullet_spawn_timer = 0
        
        # 更新子彈
        for bullet in bullets[:]:
            bullet.update(dt)
            # 移除超出螢幕的子彈
            if bullet.x > SCREEN_WIDTH + 50:
                bullets.remove(bullet)
        
        # 繪製
        screen.fill((50, 50, 100))  # 深藍色背景
        
        # 繪製子彈
        for bullet in bullets:
            bullet.draw(screen)
        
        # 繪製標題
        title_text = render_text_with_outline("BB槍特效演示", font_large, (255, 255, 255), (0, 0, 0))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        
        # 繪製說明文字
        info_texts = [
            "✨ 增強子彈特效：光暈、閃爍、拖尾",
            "🎯 每秒10發自動射擊速度",
            "📝 白色文字配黑色邊框",
            "按 ESC 鍵退出演示"
        ]
        
        for i, text in enumerate(info_texts):
            info_surface = render_text_with_outline(text, font_medium, (255, 255, 255), (0, 0, 0))
            screen.blit(info_surface, (50, 100 + i * 30))
        
        # 顯示當前子彈數量
        bullet_count_text = render_text_with_outline(f"畫面子彈數量: {len(bullets)}", font_medium, (255, 255, 0), (0, 0, 0))
        screen.blit(bullet_count_text, (50, SCREEN_HEIGHT - 80))
        
        # 顯示射擊模式
        mode_text = render_text_with_outline("🔥 BB槍全自動模式", font_medium, (255, 100, 100), (0, 0, 0))
        screen.blit(mode_text, (50, SCREEN_HEIGHT - 50))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    print("演示結束")

if __name__ == "__main__":
    main()