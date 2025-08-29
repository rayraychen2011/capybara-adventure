######################載入套件######################
import pygame
import random
from config.settings import *


######################斧頭工具######################
class Axe:
    """
    斧頭工具 - 用於砍樹的工具\n
    \n
    特性：\n
    - 可以裝備到裝備圓盤\n
    - 右鍵點擊樹木可以砍樹\n
    - 砍樹獲得1元金錢獎勵\n
    """

    def __init__(self):
        """
        初始化斧頭\n
        """
        self.name = "斧頭"
        self.tool_type = "axe"
        
        # 工具屬性
        self.damage = 50  # 對樹木的傷害
        self.durability = 100  # 耐久度
        self.max_durability = 100
        
        print(f"創建工具: {self.name}")

    def use(self, target):
        """
        使用斧頭\n
        \n
        參數:\n
        target: 目標物件（樹木）\n
        \n
        回傳:\n
        dict: 使用結果\n
        """
        if self.durability <= 0:
            return {"success": False, "message": "斧頭已損壞，需要修理"}
        
        # 消耗耐久度
        self.durability = max(0, self.durability - 1)
        
        # 對目標造成傷害
        if hasattr(target, 'take_damage'):
            damage_result = target.take_damage(self.damage)
            
            return {
                "success": True,
                "damage": self.damage,
                "target_destroyed": damage_result.get("destroyed", False),
                "durability": self.durability
            }
        
        return {"success": False, "message": "無效的目標"}

    def repair(self):
        """
        修理斧頭\n
        """
        self.durability = self.max_durability
        print(f"{self.name} 已修理完成")

    def get_durability_percentage(self):
        """
        獲取耐久度百分比\n
        \n
        回傳:\n
        float: 耐久度百分比 (0.0 到 1.0)\n
        """
        return self.durability / self.max_durability


######################樹木系統######################
class Tree:
    """
    樹木 - 可以被斧頭砍伐的環境物件\n
    \n
    被砍伐後會消失並給予玩家金錢獎勵\n
    """

    def __init__(self, x, y, tree_type="oak"):
        """
        初始化樹木\n
        \n
        參數:\n
        x (int): X座標\n
        y (int): Y座標\n
        tree_type (str): 樹木類型\n
        """
        self.x = x
        self.y = y
        self.tree_type = tree_type
        
        # 樹木屬性
        self.max_health = 100
        self.health = self.max_health
        self.is_alive = True
        
        # 視覺屬性 - 樹木比玩家高3倍
        from config.settings import PLAYER_HEIGHT
        self.width = PLAYER_HEIGHT * 3  # 24像素寬度
        self.height = PLAYER_HEIGHT * 3  # 24像素高度（玩家的3倍）
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # 樹木結構設定
        self.trunk_width = self.width // 4  # 樹幹寬度為樹木寬度的1/4
        self.trunk_height = self.height // 2  # 樹幹高度為樹木高度的1/2
        self.crown_radius = self.width // 2  # 樹冠半徑為樹木寬度的1/2
        
        # 獎勵設定
        self.money_reward = 1  # 砍伐獲得1元
        
        # 樹木顏色（根據類型）
        if tree_type == "oak":
            self.trunk_color = (139, 69, 19)  # 棕色樹幹
            self.leaves_color = (34, 139, 34)  # 綠色樹葉
        elif tree_type == "pine":
            self.trunk_color = (101, 67, 33)  # 深棕色樹幹
            self.leaves_color = (0, 100, 0)  # 深綠色樹葉
        else:
            self.trunk_color = (139, 69, 19)
            self.leaves_color = (34, 139, 34)

    def take_damage(self, damage):
        """
        受到傷害\n
        \n
        參數:\n
        damage (int): 傷害值\n
        \n
        回傳:\n
        dict: 傷害結果\n
        """
        if not self.is_alive:
            return {"success": False, "destroyed": False}
        
        self.health -= damage
        
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            
            print(f"樹木被砍倒了！獲得 {self.money_reward} 元")
            
            return {
                "success": True,
                "destroyed": True,
                "money_reward": self.money_reward
            }
        else:
            print(f"樹木受到 {damage} 點傷害，剩餘生命值: {self.health}")
            
            return {
                "success": True,
                "destroyed": False,
                "health_remaining": self.health
            }

    def is_near_position(self, x, y, max_distance=50):
        """
        檢查位置是否在樹木附近\n
        \n
        參數:\n
        x (int): X座標\n
        y (int): Y座標\n
        max_distance (float): 最大距離\n
        \n
        回傳:\n
        bool: 是否在範圍內\n
        """
        tree_center_x = self.x + self.width // 2
        tree_center_y = self.y + self.height // 2
        
        distance = ((x - tree_center_x) ** 2 + (y - tree_center_y) ** 2) ** 0.5
        return distance <= max_distance

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製樹木 - 改進版，樹木比玩家高3倍，有明顯的樹冠與樹幹區分\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (int): 攝影機X偏移\n
        camera_y (int): 攝影機Y偏移\n
        """
        if not self.is_alive:
            return  # 死亡的樹木不繪製
        
        # 計算螢幕座標
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # 檢查是否在螢幕範圍內
        if (screen_x + self.width < 0 or screen_x > SCREEN_WIDTH or
            screen_y + self.height < 0 or screen_y > SCREEN_HEIGHT):
            return
        
        # 計算根據健康狀態的顏色調整
        health_ratio = self.health / self.max_health
        
        # 繪製樹幹（底部居中）
        trunk_x = screen_x + (self.width - self.trunk_width) // 2
        trunk_y = screen_y + self.height - self.trunk_height
        trunk_rect = pygame.Rect(trunk_x, trunk_y, self.trunk_width, self.trunk_height)
        
        # 樹幹顏色隨健康度變化
        if health_ratio < 0.3:
            trunk_color = (80, 40, 20)  # 枯萎的樹幹
        else:
            trunk_color = self.trunk_color
            
        pygame.draw.rect(screen, trunk_color, trunk_rect)
        pygame.draw.rect(screen, (101, 67, 33), trunk_rect, 1)  # 樹幹邊框
        
        # 繪製樹冠（多層圓形，創造豐富的樹冠效果）
        crown_center_x = screen_x + self.width // 2
        crown_center_y = screen_y + self.crown_radius
        
        # 樹冠顏色隨健康度變化
        if health_ratio < 0.2:
            crown_color = (139, 69, 19)  # 枯萎成棕色
            outer_crown_color = (101, 67, 33)
        elif health_ratio < 0.4:
            crown_color = (218, 165, 32)  # 變黃
            outer_crown_color = (184, 134, 11)
        elif health_ratio < 0.6:
            crown_color = (154, 205, 50)  # 淺綠
            outer_crown_color = (124, 252, 0)
        else:
            crown_color = self.leaves_color
            # 外層樹冠顏色稍深
            r, g, b = self.leaves_color
            outer_crown_color = (max(0, r-20), max(0, g-20), max(0, b-20))
        
        # 繪製外層樹冠（較大，較深色）
        outer_radius = int(self.crown_radius * 1.1)
        pygame.draw.circle(screen, outer_crown_color, 
                         (int(crown_center_x), int(crown_center_y)), 
                         outer_radius)
        
        # 繪製主要樹冠
        pygame.draw.circle(screen, crown_color, 
                         (int(crown_center_x), int(crown_center_y)), 
                         self.crown_radius)
        
        # 繪製內層高光（健康樹木才有）
        if health_ratio > 0.6:
            highlight_radius = int(self.crown_radius * 0.6)
            highlight_color = (min(255, crown_color[0] + 30), 
                             min(255, crown_color[1] + 30), 
                             crown_color[2])
            highlight_x = crown_center_x - self.crown_radius // 3
            highlight_y = crown_center_y - self.crown_radius // 3
            pygame.draw.circle(screen, highlight_color, 
                             (int(highlight_x), int(highlight_y)), 
                             highlight_radius // 2)
        
        # 繪製樹冠邊框
        pygame.draw.circle(screen, (0, 100, 0), 
                         (int(crown_center_x), int(crown_center_y)), 
                         self.crown_radius, 2)
        
        # 如果樹木受傷，顯示健康條
        if health_ratio < 1.0:
            health_bar_width = self.width
            health_bar_height = 3
            health_bar_x = screen_x
            health_bar_y = screen_y - 8
            
            # 背景（紅色）
            pygame.draw.rect(screen, (200, 0, 0), 
                           (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
            
            # 前景（綠色，根據健康度調整）
            current_health_width = int(health_bar_width * health_ratio)
            if current_health_width > 0:
                health_color = (int(200 * (1 - health_ratio) + 0 * health_ratio),
                              int(0 * (1 - health_ratio) + 200 * health_ratio), 0)
                pygame.draw.rect(screen, health_color, 
                               (health_bar_x, health_bar_y, current_health_width, health_bar_height))


######################樹木管理器######################
class TreeManager:
    """
    樹木管理器 - 管理地圖上的所有樹木\n
    \n
    負責：\n
    - 創建和放置樹木\n
    - 處理樹木砍伐\n
    - 樹木重生系統\n
    """

    def __init__(self, terrain_system=None):
        """
        初始化樹木管理器\n
        \n
        參數:\n
        terrain_system: 地形系統引用\n
        """
        self.terrain_system = terrain_system
        self.trees = []
        self.chopped_trees = []  # 被砍伐的樹木位置記錄
        
        # 樹木重生設定
        self.respawn_time = 300  # 5分鐘後重生
        
        print("樹木管理器初始化完成")

    def generate_trees_on_terrain(self):
        """
        根據地形生成樹木\n
        \n
        在森林地形（地形代碼1）生成樹木\n
        """
        if not self.terrain_system:
            print("警告：沒有地形系統引用，無法生成樹木")
            return
        
        # 在地形代碼1的區域生成樹木
        tree_count = 0
        attempts = 0
        max_attempts = 1000
        
        while tree_count < 50 and attempts < max_attempts:  # 生成50棵樹
            attempts += 1
            
            # 隨機選擇位置
            x = random.randint(0, self.terrain_system.map_width - 1)
            y = random.randint(0, self.terrain_system.map_height - 1)
            
            # 檢查地形代碼
            if (0 <= y < len(self.terrain_system.map_data) and 
                0 <= x < len(self.terrain_system.map_data[y])):
                
                terrain_code = self.terrain_system.map_data[y][x]
                
                if terrain_code == 1:  # 森林地形
                    # 轉換為世界座標
                    world_x = x * self.terrain_system.tile_size
                    world_y = y * self.terrain_system.tile_size
                    
                    # 檢查是否與現有樹木重疊
                    if not self._is_position_occupied(world_x, world_y):
                        tree_type = random.choice(["oak", "pine"])
                        tree = Tree(world_x, world_y, tree_type)
                        self.trees.append(tree)
                        tree_count += 1
        
        print(f"生成了 {tree_count} 棵樹木")

    def _is_position_occupied(self, x, y, min_distance=60):
        """
        檢查位置是否被其他樹木佔據\n
        \n
        參數:\n
        x (int): X座標\n
        y (int): Y座標\n
        min_distance (float): 最小距離\n
        \n
        回傳:\n
        bool: 是否被佔據\n
        """
        for tree in self.trees:
            distance = ((tree.x - x) ** 2 + (tree.y - y) ** 2) ** 0.5
            if distance < min_distance:
                return True
        return False

    def find_tree_at_position(self, x, y, max_distance=50):
        """
        在指定位置尋找樹木\n
        \n
        參數:\n
        x (int): X座標\n
        y (int): Y座標\n
        max_distance (float): 最大距離\n
        \n
        回傳:\n
        Tree: 找到的樹木，如果沒有則返回None\n
        """
        for tree in self.trees:
            if tree.is_alive and tree.is_near_position(x, y, max_distance):
                return tree
        return None

    def chop_tree(self, tree, player):
        """
        砍伐樹木\n
        \n
        參數:\n
        tree (Tree): 要砍伐的樹木\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 砍伐結果\n
        """
        if not tree.is_alive:
            return {"success": False, "message": "樹木已經被砍伐"}
        
        # 使用斧頭砍樹
        axe = Axe()  # 簡化實作，直接創建斧頭
        result = axe.use(tree)
        
        if result["success"] and result.get("target_destroyed", False):
            # 樹木被砍倒
            # 給予玩家金錢獎勵
            player.money += tree.money_reward
            
            # 記錄砍伐時間用於重生
            import time
            chopped_info = {
                "position": (tree.x, tree.y),
                "tree_type": tree.tree_type,
                "chopped_time": time.time()
            }
            self.chopped_trees.append(chopped_info)
            
            # 從活樹列表中移除
            if tree in self.trees:
                self.trees.remove(tree)
            
            return {
                "success": True,
                "money_earned": tree.money_reward,
                "message": f"砍倒了樹木！獲得 {tree.money_reward} 元"
            }
        
        return result

    def update(self, dt):
        """
        更新樹木系統\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 檢查樹木重生
        self._check_tree_respawn()

    def _check_tree_respawn(self):
        """
        檢查樹木重生\n
        """
        import time
        current_time = time.time()
        respawned_trees = []
        
        for chopped_info in self.chopped_trees[:]:
            if current_time - chopped_info["chopped_time"] >= self.respawn_time:
                # 重生樹木
                x, y = chopped_info["position"]
                tree_type = chopped_info["tree_type"]
                
                new_tree = Tree(x, y, tree_type)
                self.trees.append(new_tree)
                respawned_trees.append(chopped_info)
                
                print(f"樹木在 ({x}, {y}) 重新生長")
        
        # 移除已重生的記錄
        for respawned in respawned_trees:
            self.chopped_trees.remove(respawned)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製所有樹木\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (int): 攝影機X偏移\n
        camera_y (int): 攝影機Y偏移\n
        """
        for tree in self.trees:
            tree.draw(screen, camera_x, camera_y)

    def get_tree_count(self):
        """
        獲取活樹數量\n
        \n
        回傳:\n
        int: 活樹數量\n
        """
        return len([tree for tree in self.trees if tree.is_alive])