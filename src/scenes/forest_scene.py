######################載入套件######################
import pygame
import random
from src.core.scene_manager import Scene
from src.core.state_manager import GameState
from src.player.player import Player
from src.player.input_controller import InputController
from src.utils.font_manager import get_font_manager
from config.settings import *

######################森林場景######################
class ForestScene(Scene):
    """
    森林場景 - 狩獵和資源收集的主要區域\n
    \n
    森林充滿各種野生動物和天然資源\n
    玩家可以在這裡狩獵、收集材料、探索隱藏的寶藏\n
    提供豐富的戶外活動體驗\n
    """
    
    def __init__(self, state_manager):
        """
        初始化森林場景\n
        \n
        參數:\n
        state_manager (StateManager): 遊戲狀態管理器\n
        """
        super().__init__("森林")
        self.state_manager = state_manager
        
        # 建立玩家角色
        self.player = Player(100, SCREEN_HEIGHT // 2)
        
        # 建立輸入控制器
        self.input_controller = InputController(self.player)
        
        # 建立場景元素
        self._create_trees()
        self._create_animals()
        self._create_resources()
        self._create_exit_area()
        
        # 狩獵系統狀態
        self.hunting_mode = False
        self.crosshair_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        print("森林場景已建立")
    
    def _create_trees(self):
        """
        建立森林中的樹木\n
        \n
        生成隨機分佈的樹木作為環境裝飾和障礙物\n
        """
        self.trees = []
        
        # 隨機生成 20-30 棵樹
        num_trees = random.randint(20, 30)
        
        for _ in range(num_trees):
            # 隨機位置，避免太靠近邊界
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            
            # 隨機樹木大小
            size = random.randint(20, 40)
            
            tree = {
                "position": (x, y),
                "size": size,
                "color": (34, 100, 34),  # 深綠色
                "rect": pygame.Rect(x - size//2, y - size//2, size, size)
            }
            
            self.trees.append(tree)
    
    def _create_animals(self):
        """
        建立森林中的動物\n
        \n
        生成可以狩獵的野生動物\n
        """
        self.animals = []
        
        # 定義動物類型
        animal_types = [
            {"name": "兔子", "color": (139, 69, 19), "size": 15, "speed": 2, "points": 10},
            {"name": "鹿", "color": (160, 82, 45), "size": 25, "speed": 1.5, "points": 25},
            {"name": "野豬", "color": (64, 64, 64), "size": 30, "speed": 1, "points": 40},
        ]
        
        # 隨機生成 8-12 隻動物
        num_animals = random.randint(8, 12)
        
        for _ in range(num_animals):
            animal_type = random.choice(animal_types)
            
            # 隨機位置
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            
            animal = {
                "name": animal_type["name"],
                "position": [x, y],  # 使用列表以便修改
                "color": animal_type["color"],
                "size": animal_type["size"],
                "speed": animal_type["speed"],
                "points": animal_type["points"],
                "direction": [random.uniform(-1, 1), random.uniform(-1, 1)],
                "alive": True,
                "move_timer": 0
            }
            
            self.animals.append(animal)
    
    def _create_resources(self):
        """
        建立可收集的資源\n
        \n
        生成木材、草藥等可收集物品\n
        """
        self.resources = []
        
        resource_types = [
            {"name": "木材", "color": (139, 69, 19), "value": 5},
            {"name": "草藥", "color": (0, 128, 0), "value": 8},
            {"name": "蘑菇", "color": (255, 228, 196), "value": 12},
            {"name": "石頭", "color": (128, 128, 128), "value": 3},
        ]
        
        # 隨機生成 15-25 個資源
        num_resources = random.randint(15, 25)
        
        for _ in range(num_resources):
            resource_type = random.choice(resource_types)
            
            # 隨機位置
            x = random.randint(30, SCREEN_WIDTH - 30)
            y = random.randint(30, SCREEN_HEIGHT - 30)
            
            resource = {
                "name": resource_type["name"],
                "position": (x, y),
                "color": resource_type["color"],
                "value": resource_type["value"],
                "collected": False,
                "rect": pygame.Rect(x - 8, y - 8, 16, 16)
            }
            
            self.resources.append(resource)
    
    def _create_exit_area(self):
        """
        建立返回小鎮的出口區域\n
        """
        self.exit_area = pygame.Rect(10, SCREEN_HEIGHT // 2 - 50, 50, 100)
    
    def enter(self):
        """
        進入森林場景\n
        """
        super().enter()
        print("玩家進入森林")
        # 重新生成一些動物，模擬生態系統
        self._respawn_some_animals()
    
    def _respawn_some_animals(self):
        """
        重新生成一些動物\n
        \n
        讓森林保持生機，避免動物被獵殺完畢\n
        """
        dead_animals = [animal for animal in self.animals if not animal["alive"]]
        
        # 有 30% 機率復活一些動物
        for animal in dead_animals:
            if random.random() < 0.3:
                animal["alive"] = True
                # 重新隨機位置
                animal["position"] = [
                    random.randint(100, SCREEN_WIDTH - 100),
                    random.randint(100, SCREEN_HEIGHT - 100)
                ]
                animal["direction"] = [random.uniform(-1, 1), random.uniform(-1, 1)]
    
    def update(self, dt):
        """
        更新森林場景邏輯\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新輸入控制器
        self.input_controller.update(dt)
        
        # 更新玩家角色
        self.player.update(dt)
        
        # 更新動物行為
        self._update_animals(dt)
        
        # 檢查場景切換
        self._check_exit()
        
        # 檢查資源收集
        self._check_resource_collection()
        
        # 檢查狩獵
        if self.hunting_mode:
            self._update_hunting_mode()
    
    def _update_animals(self, dt):
        """
        更新動物的移動和行為\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        for animal in self.animals:
            if not animal["alive"]:
                continue
            
            # 更新移動計時器
            animal["move_timer"] += dt
            
            # 每 2-4 秒改變一次移動方向
            if animal["move_timer"] > random.uniform(2, 4):
                animal["direction"] = [random.uniform(-1, 1), random.uniform(-1, 1)]
                animal["move_timer"] = 0
            
            # 移動動物
            speed = animal["speed"] * 20  # 調整速度比例
            animal["position"][0] += animal["direction"][0] * speed * dt
            animal["position"][1] += animal["direction"][1] * speed * dt
            
            # 限制動物在畫面內
            animal["position"][0] = max(animal["size"], 
                                      min(SCREEN_WIDTH - animal["size"], animal["position"][0]))
            animal["position"][1] = max(animal["size"], 
                                      min(SCREEN_HEIGHT - animal["size"], animal["position"][1]))
    
    def _check_exit(self):
        """
        檢查玩家是否要離開森林\n
        """
        if self.player.rect.colliderect(self.exit_area):
            self.request_scene_change(SCENE_TOWN)
    
    def _check_resource_collection(self):
        """
        檢查資源收集\n
        """
        if self.input_controller.is_action_key_pressed("interact"):
            player_rect = self.player.rect
            
            for resource in self.resources:
                if not resource["collected"] and player_rect.colliderect(resource["rect"]):
                    # 收集資源
                    self._collect_resource(resource)
                    break
    
    def _collect_resource(self, resource):
        """
        收集資源\n
        \n
        參數:\n
        resource (dict): 要收集的資源\n
        """
        resource_name = resource["name"]
        value = resource["value"]
        
        # 添加到玩家背包
        if self.player.add_item(resource_name, 1):
            resource["collected"] = True
            self.player.add_money(value)
            print(f"收集了 {resource_name}，獲得 ${value}")
        else:
            print("背包已滿，無法收集更多物品")
    
    def _update_hunting_mode(self):
        """
        更新狩獵模式\n
        """
        # 獲取滑鼠位置作為準星位置
        self.crosshair_pos = pygame.mouse.get_pos()
    
    def _shoot_at_target(self, target_pos):
        """
        向目標射擊\n
        \n
        參數:\n
        target_pos (tuple): 目標位置\n
        """
        player_pos = self.player.get_center_position()
        
        # 檢查射程
        distance = ((target_pos[0] - player_pos[0]) ** 2 + 
                   (target_pos[1] - player_pos[1]) ** 2) ** 0.5
        
        if distance > GUN_RANGE:
            print("目標太遠，無法射擊")
            return
        
        # 檢查是否擊中動物
        for animal in self.animals:
            if not animal["alive"]:
                continue
            
            animal_pos = animal["position"]
            hit_distance = ((target_pos[0] - animal_pos[0]) ** 2 + 
                           (target_pos[1] - animal_pos[1]) ** 2) ** 0.5
            
            if hit_distance < animal["size"]:
                # 擊中動物
                self._hunt_animal(animal)
                break
        else:
            print("射擊落空")
    
    def _hunt_animal(self, animal):
        """
        狩獵動物\n
        \n
        參數:\n
        animal (dict): 被獵殺的動物\n
        """
        animal["alive"] = False
        points = animal["points"]
        
        # 獲得金錢和物品
        self.player.add_money(points)
        meat_name = f"{animal['name']}肉"
        self.player.add_item(meat_name, 1)
        
        print(f"成功獵殺 {animal['name']}，獲得 ${points} 和 {meat_name}")
    
    def draw(self, screen):
        """
        繪製森林場景\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 清空背景為森林綠色
        screen.fill((34, 80, 34))
        
        # 繪製樹木
        self._draw_trees(screen)
        
        # 繪製資源
        self._draw_resources(screen)
        
        # 繪製動物
        self._draw_animals(screen)
        
        # 繪製出口區域
        self._draw_exit_area(screen)
        
        # 繪製玩家角色
        self.player.draw(screen)
        
        # 繪製狩獵介面
        if self.hunting_mode:
            self._draw_hunting_ui(screen)
        
        # 繪製 UI
        self._draw_ui(screen)
    
    def _draw_trees(self, screen):
        """
        繪製樹木\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for tree in self.trees:
            position = tree["position"]
            size = tree["size"]
            color = tree["color"]
            
            # 繪製樹冠（圓形）
            pygame.draw.circle(screen, color, position, size // 2)
            
            # 繪製樹幹（矩形）
            trunk_rect = pygame.Rect(position[0] - 3, position[1], 6, size // 3)
            pygame.draw.rect(screen, (101, 67, 33), trunk_rect)
    
    def _draw_resources(self, screen):
        """
        繪製資源\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for resource in self.resources:
            if resource["collected"]:
                continue
            
            # 繪製資源（小方塊）
            pygame.draw.rect(screen, resource["color"], resource["rect"])
            pygame.draw.rect(screen, (0, 0, 0), resource["rect"], 1)
    
    def _draw_animals(self, screen):
        """
        繪製動物\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        for animal in self.animals:
            if not animal["alive"]:
                continue
            
            position = animal["position"]
            size = animal["size"]
            color = animal["color"]
            
            # 繪製動物（橢圓形）
            animal_rect = pygame.Rect(position[0] - size//2, position[1] - size//2, size, size//2)
            pygame.draw.ellipse(screen, color, animal_rect)
            pygame.draw.ellipse(screen, (0, 0, 0), animal_rect, 1)
    
    def _draw_exit_area(self, screen):
        """
        繪製出口區域\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        pygame.draw.rect(screen, (255, 255, 0), self.exit_area)
        pygame.draw.rect(screen, (0, 0, 0), self.exit_area, 2)
        
        font = pygame.font.Font(None, 20)
        text = font.render("回小鎮", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.exit_area.center)
        screen.blit(text, text_rect)
    
    def _draw_hunting_ui(self, screen):
        """
        繪製狩獵模式的介面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        # 繪製準星
        crosshair_size = 20
        x, y = self.crosshair_pos
        
        # 十字準星
        pygame.draw.line(screen, (255, 0, 0), (x - crosshair_size, y), (x + crosshair_size, y), 2)
        pygame.draw.line(screen, (255, 0, 0), (x, y - crosshair_size), (x, y + crosshair_size), 2)
        
        # 準星圓圈
        pygame.draw.circle(screen, (255, 0, 0), (x, y), crosshair_size, 2)
        
        # 顯示狩獵模式提示
        font = pygame.font.Font(None, 24)
        hint_text = font.render("狩獵模式 - 左鍵射擊，G 退出", True, (255, 255, 0))
        screen.blit(hint_text, (10, SCREEN_HEIGHT - 60))
    
    def _draw_ui(self, screen):
        """
        繪製使用者介面\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        font = pygame.font.Font(None, 24)
        
        # 顯示金錢
        money_text = font.render(f"金錢: ${self.player.get_money()}", True, (255, 255, 255))
        screen.blit(money_text, (10, 10))
        
        # 顯示動物數量
        alive_animals = sum(1 for animal in self.animals if animal["alive"])
        animal_text = font.render(f"動物: {alive_animals}", True, (255, 255, 255))
        screen.blit(animal_text, (10, 35))
        
        # 顯示操作提示
        if not self.hunting_mode:
            hint_text = font.render("E: 收集 | G: 狩獵模式 | I: 背包", True, (255, 255, 255))
        else:
            hint_text = font.render("左鍵: 射擊 | G: 退出狩獵", True, (255, 255, 255))
        
        screen.blit(hint_text, (10, SCREEN_HEIGHT - 30))
    
    def handle_event(self, event):
        """
        處理森林場景的輸入事件\n
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
            if action == "hunting":
                # 切換狩獵模式
                self.hunting_mode = not self.hunting_mode
                if self.hunting_mode:
                    print("進入狩獵模式")
                else:
                    print("退出狩獵模式")
                return True
                
            elif action == "inventory":
                self.state_manager.change_state(GameState.INVENTORY)
                return True
        
        # 處理狩獵模式的滑鼠點擊
        if self.hunting_mode and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵
                self._shoot_at_target(event.pos)
                return True
        
        return False