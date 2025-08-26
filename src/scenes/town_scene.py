######################載入套件######################
import pygame
from src.core.scene_manager import Scene
from src.core.state_manager import GameState
from src.player.player import Player
from src.player.input_controller import InputController
from src.utils.font_manager import get_font_manager
from config.settings import *

######################小鎮場景######################
class TownScene(Scene):
    """
    小鎮場景 - 遊戲的主要活動區域\n
    \n
    小鎮是遊戲的中心樞紐，包含各種商業設施和居民\n
    玩家可以在這裡購物、接受任務、與 NPC 互動\n
    提供通往其他場景的入口\n
    """
    
    def __init__(self, state_manager):
        """
        初始化小鎮場景\n
        \n
        參數:\n
        state_manager (StateManager): 遊戲狀態管理器\n
        """
        super().__init__("小鎮")
        self.state_manager = state_manager
        
        # 取得字體管理器
        self.font_manager = get_font_manager()
        
        # 建立玩家角色
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # 建立輸入控制器
        self.input_controller = InputController(self.player)
        
        # 建立場景切換區域
        self._create_scene_transitions()
        
        # 建立建築物
        self._create_buildings()
        
        # 建立 NPC
        self._create_npcs()
        
        print("小鎮場景已建立")
    
    def _create_scene_transitions(self):
        """
        建立場景切換區域\n
        """
        self.scene_transitions = [
            {
                "name": "森林入口",
                "target_scene": SCENE_FOREST,
                "area": pygame.Rect(50, 50, 100, 50),
                "color": (34, 139, 34)  # 綠色
            },
            {
                "name": "湖泊碼頭",
                "target_scene": SCENE_LAKE,
                "area": pygame.Rect(SCREEN_WIDTH - 150, 50, 100, 50),
                "color": (0, 191, 255)  # 藍色
            },
            {
                "name": "回家",
                "target_scene": SCENE_HOME,
                "area": pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100, 100, 50),
                "color": (255, 215, 0)  # 金色
            }
        ]
    
    def _create_buildings(self):
        """
        建立建築物\n
        """
        self.buildings = [
            {
                "name": "便利商店",
                "type": "shop",
                "area": pygame.Rect(200, 150, 120, 80),
                "color": BUILDING_COLOR,
                "interaction_point": (260, 250)
            },
            {
                "name": "服裝店",
                "type": "clothing_store",
                "area": pygame.Rect(400, 150, 120, 80),
                "color": BUILDING_COLOR,
                "interaction_point": (460, 250)
            },
            {
                "name": "酒館",
                "type": "tavern",
                "area": pygame.Rect(600, 150, 120, 80),
                "color": BUILDING_COLOR,
                "interaction_point": (660, 250)
            }
        ]
    
    def _create_npcs(self):
        """
        建立 NPC 角色\n
        """
        self.npcs = [
            {
                "name": "商店老闆",
                "position": (260, 200),
                "color": (255, 0, 255),  # 紫色
                "dialogue": ["歡迎光臨！", "今天想買什麼呢？"]
            },
            {
                "name": "路人甲",
                "position": (500, 350),
                "color": (0, 255, 255),  # 青色
                "dialogue": ["天氣真好呢！", "小鎮最近很熱鬧。"]
            }
        ]
    
    def enter(self):
        """
        進入小鎮場景\n
        """
        super().enter()
        print("歡迎來到小鎮！")
    
    def update(self, dt):
        """
        更新小鎮場景邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新輸入控制器
        self.input_controller.update(dt)
        
        # 更新玩家角色
        self.player.update(dt)
        
        # 檢查場景切換
        self._check_scene_transitions()
        
        # 檢查建築物互動
        self._check_building_interactions()
        
        # 檢查 NPC 互動
        self._check_npc_interactions()
    
    def _check_scene_transitions(self):
        """
        檢查場景切換\n
        """
        player_rect = self.player.rect
        
        for transition in self.scene_transitions:
            if player_rect.colliderect(transition["area"]):
                target_scene = transition["target_scene"]
                print(f"切換到場景: {transition['name']}")
                self.request_scene_change(target_scene)
                break
    
    def _check_building_interactions(self):
        """
        檢查建築物互動\n
        """
        if self.input_controller.is_action_key_just_pressed("interact"):
            player_pos = self.player.get_center_position()
            
            for building in self.buildings:
                interaction_point = building["interaction_point"]
                distance = ((player_pos[0] - interaction_point[0]) ** 2 + 
                           (player_pos[1] - interaction_point[1]) ** 2) ** 0.5
                
                if distance < 50:  # 互動範圍
                    self._interact_with_building(building)
                    break
    
    def _interact_with_building(self, building):
        """
        與建築物互動\n
        \n
        參數:\n
        building (dict): 建築物資料\n
        """
        building_type = building["type"]
        building_name = building["name"]
        
        print(f"與{building_name}互動")
        
        if building_type == "shop":
            print("便利商店：歡迎光臨！想買些什麼嗎？")
            # 這裡可以實作商店系統
        elif building_type == "clothing_store":
            print("服裝店：我們有最時尚的服裝！")
            # 這裡可以實作服裝系統
        elif building_type == "tavern":
            print("酒館：來杯飲料休息一下吧！")
            # 這裡可以實作休息系統
    
    def _check_npc_interactions(self):
        """
        檢查 NPC 互動\n
        """
        if self.input_controller.is_action_key_just_pressed("interact"):
            player_pos = self.player.get_center_position()
            
            for npc in self.npcs:
                npc_pos = npc["position"]
                distance = ((player_pos[0] - npc_pos[0]) ** 2 + 
                           (player_pos[1] - npc_pos[1]) ** 2) ** 0.5
                
                if distance < 50:  # 互動範圍
                    self._talk_to_npc(npc)
                    break
    
    def _talk_to_npc(self, npc):
        """
        與 NPC 對話\n
        \n
        參數:\n
        npc (dict): NPC 資料\n
        """
        import random
        npc_name = npc["name"]
        dialogue = random.choice(npc["dialogue"])
        print(f"{npc_name}: {dialogue}")
    
    def draw(self, screen):
        """
        繪製小鎮場景\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 清空背景為草地綠色
        screen.fill(GRASS_COLOR)
        
        # 繪製道路
        self._draw_roads(screen)
        
        # 繪製建築物
        self._draw_buildings(screen)
        
        # 繪製場景切換區域
        self._draw_scene_transitions(screen)
        
        # 繪製 NPC
        self._draw_npcs(screen)
        
        # 繪製玩家角色
        self.player.draw(screen)
        
        # 繪製 UI
        self._draw_ui(screen)
    
    def _draw_roads(self, screen):
        """
        繪製道路\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 主要道路 - 水平
        pygame.draw.rect(screen, ROAD_COLOR,
                        (0, SCREEN_HEIGHT // 2 - 25, SCREEN_WIDTH, 50))
        
        # 主要道路 - 垂直
        pygame.draw.rect(screen, ROAD_COLOR,
                        (SCREEN_WIDTH // 2 - 25, 0, 50, SCREEN_HEIGHT))
    
    def _draw_buildings(self, screen):
        """
        繪製建築物\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for building in self.buildings:
            # 繪製建築物本體
            pygame.draw.rect(screen, building["color"], building["area"])
            pygame.draw.rect(screen, (0, 0, 0), building["area"], 2)
            
            # 繪製建築物名稱
            text = self.font_manager.render_text(building["name"], UI_FONT_SIZE, (255, 255, 255))
            text_rect = text.get_rect(center=building["area"].center)
            screen.blit(text, text_rect)
            
            # 繪製互動點
            interaction_point = building["interaction_point"]
            pygame.draw.circle(screen, (255, 255, 0), interaction_point, 5)
    
    def _draw_scene_transitions(self, screen):
        """
        繪製場景切換區域\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for transition in self.scene_transitions:
            # 繪製傳送點區域
            pygame.draw.rect(screen, transition["color"], transition["area"])
            pygame.draw.rect(screen, (0, 0, 0), transition["area"], 2)
            
            # 繪製標籤文字
            text = self.font_manager.render_text(transition["name"], DEFAULT_FONT_SIZE, (0, 0, 0))
            text_rect = text.get_rect(center=transition["area"].center)
            screen.blit(text, text_rect)
    
    def _draw_npcs(self, screen):
        """
        繪製 NPC\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for npc in self.npcs:
            # 繪製 NPC 圓形
            pygame.draw.circle(screen, npc["color"], npc["position"], 15)
            pygame.draw.circle(screen, (0, 0, 0), npc["position"], 15, 2)
            
            # 繪製 NPC 名稱
            text = self.font_manager.render_text(npc["name"], SMALL_FONT_SIZE, (0, 0, 0))
            text_rect = text.get_rect(center=(npc["position"][0], npc["position"][1] - 25))
            screen.blit(text, text_rect)
    
    def _draw_ui(self, screen):
        """
        繪製使用者介面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 顯示金錢
        money_text = self.font_manager.render_text(f"金錢: ${self.player.get_money()}", DEFAULT_FONT_SIZE, (0, 0, 0))
        screen.blit(money_text, (10, 10))
        
        # 顯示背包使用情況
        inventory = self.player.get_inventory_list()
        item_count = sum(inventory.values())
        capacity = self.player.inventory_capacity
        inventory_text = self.font_manager.render_text(f"背包: {item_count}/{capacity}", DEFAULT_FONT_SIZE, (0, 0, 0))
        screen.blit(inventory_text, (10, 35))
        
        # 顯示操作提示
        hint_text = self.font_manager.render_text("E: 互動 | I: 背包 | 走向不同區域切換場景", DEFAULT_FONT_SIZE, (0, 0, 0))
        screen.blit(hint_text, (10, SCREEN_HEIGHT - 30))
    
    def handle_event(self, event):
        """
        處理小鎮場景輸入事件\n
        \n
        參數:\n
        event (pygame.event.Event): 輸入事件\n
        \n
        回傳:\n
        bool: True 表示事件已處理\n
        """
        # 讓輸入控制器處理事件
        action = self.input_controller.handle_event(event)
        
        if action:
            if action == "inventory":
                self.state_manager.change_state(GameState.INVENTORY)
                return True
        
        return False
    
    def get_player(self):
        """
        獲取玩家角色實例\n
        \n
        回傳:\n
        Player: 玩家角色物件\n
        """
        return self.player