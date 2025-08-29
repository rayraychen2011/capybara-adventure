######################載入套件######################
import pygame
import math
from config.settings import *
from src.utils.helpers import clamp, fast_movement_calculate
from src.systems.weapon_system import WeaponManager


######################玩家角色類別######################
class Player:
    """
    玩家角色類別 - 代表遊戲中的主角\n
    \n
    管理玩家角色的所有屬性和行為，包括：\n
    - 位置和移動控制\n
    - 生命值和死亡重生系統\n
    - 外觀和動畫\n
    - 物品欄管理（10格物品欄取代背包）\n
    - 金錢和經驗值\n
    - 武器和載具系統\n
    - 各種遊戲狀態\n
    \n
    使用幾何形狀暫代圖片素材，提供完整的角色功能\n
    """

    def __init__(self, x=None, y=None):
        """
        初始化玩家角色\n
        \n
        設定角色的初始位置、外觀、屬性和狀態\n
        建立物品欄系統和各種遊戲數據\n
        \n
        參數:\n
        x (int): 初始 X 座標位置，None 表示待設定（會在玩家之家設定）\n
        y (int): 初始 Y 座標位置，None 表示待設定（會在玩家之家設定）\n
        """
        ######################位置和移動屬性######################
        # 玩家當前位置 - 初始設為螢幕中心，稍後會移動到玩家之家
        self.x = x if x is not None else SCREEN_WIDTH // 2
        self.y = y if y is not None else SCREEN_HEIGHT // 2
        self.needs_home_spawn = x is None and y is None  # 標記是否需要在玩家之家生成

        # 玩家尺寸
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        # 移動速度
        self.speed = PLAYER_SPEED
        self.run_speed = PLAYER_RUN_SPEED
        self.is_running = False  # 是否正在奔跑

        # 當前移動方向（單位向量）
        self.direction_x = 0
        self.direction_y = 0

        # 面朝方向（用於動畫和互動）
        self.facing_direction = "down"  # "up", "down", "left", "right"

        # 碰撞檢測相關
        self.terrain_system = None  # 地形系統引用，用於碰撞檢測

        ######################生命值系統######################
        # 生命值（根據新需求修改）
        self.max_health = PLAYER_MAX_HEALTH  # 最高血量 1000
        self.health = PLAYER_INITIAL_HEALTH  # 預設血量 300
        self.is_alive = True
        self.is_injured = False  # 玩家是否處於受傷狀態
        self.last_damage_time = 0
        self.invulnerable_time = 2.0  # 受傷後無敵時間 (秒)

        # 血量管理系統
        self.low_health_active = False  # 是否正在低血量狀態
        self.last_health_recovery_time = 0  # 上次自動回復時間
        self.heartbeat_sound_playing = False  # 心跳聲是否正在播放
        self.last_damage_time = -10.0  # 初始化為負值，確保遊戲開始時可以受傷

        # 重生系統
        self.spawn_position = None
        self.last_safe_position = (x, y)

        ######################外觀屬性######################
        # 角色顏色（暫代圖片）
        self.color = PLAYER_COLOR
        self.current_outfit = 0  # 服裝索引
        self.owned_outfits = [0]  # 擁有的服裝列表

        # 建立角色的碰撞矩形
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        ######################遊戲屬性######################
        # 金錢
        self.money = INITIAL_MONEY

        # 魚餌系統
        self.current_bait = "普通魚餌"  # 當前選用的魚餌
        self.bait_inventory = {
            "普通魚餌": -1,  # -1 表示無限
            "高級魚餌": 0,
            "頂級魚餌": 0
        }

        # 物品欄系統已刪除 - 根據需求移除所有物品撿取和掉落功能
        # self.item_slots = [None] * ITEM_BAR_SLOTS  # 已刪除
        # self.selected_slot = 0  # 已刪除

        ######################武器圓盤系統######################
        # 武器圓盤（3個槽位：槍、斧頭、空手）
        self.weapon_wheel_visible = False  # 武器圓盤是否顯示
        self.current_weapon = "unarmed"    # 當前武器（預設為空手）
        self.available_weapons = {
            "gun": {"name": "槍", "unlocked": True},     # 槍（初始擁有）
            "axe": {"name": "斧頭", "unlocked": True},   # 斧頭（初始擁有） 
            "unarmed": {"name": "空手", "unlocked": True}  # 空手（初始擁有）
        }

        # 移除背包系統（根據需求刪除）
        # 不再有物品欄、背包、物品撿取等功能

        # 經驗值和等級（預留功能）
        self.experience = 0
        self.level = 1

        # 體力值（預留功能）
        self.stamina = 100
        self.max_stamina = 100

        ######################狀態標誌######################
        # 是否正在移動
        self.is_moving = False

        # 載具系統
        self.current_vehicle = None
        self.is_driving = False
        self.in_vehicle = False  # 舊版載具系統相容性

        # 當前使用的工具
        self.current_tool = None

        # 武器系統
        self.equipped_weapon = None
        self.has_initial_weapon = True  # 根據規格書，開始時有手槍
        
        # 新的武器管理器（支援槍/空手切換）
        self.weapon_manager = WeaponManager()

        # 狀態效果
        self.status_effects = {}  # 狀態效果名稱 -> 剩餘時間

        print(f"玩家角色已建立，位置: ({self.x}, {self.y})")

    def update(self, dt):
        """
        更新玩家角色狀態 - 已優化效能\n
        \n
        每幀調用一次，更新角色的移動、動畫和其他狀態\n
        使用高效的更新順序提升響應速度\n
        \n
        參數:\n
        dt (float): 與上一幀的時間差，單位為秒\n
        """
        # 先處理移動（最高優先級）
        self._update_movement(dt)

        # 檢查是否正在移動（在移動更新後）
        self.is_moving = self.direction_x != 0 or self.direction_y != 0

        # 更新面朝方向（只在移動時）
        if self.is_moving:
            self._update_facing_direction()

        # 更新碰撞矩形位置（減少浮點數轉換）
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # 更新武器管理器
        if hasattr(self, 'weapon_manager') and self.weapon_manager:
            self.weapon_manager.update(dt)

        # 更新狀態效果（較低優先級）
        if self.status_effects:  # 只有在有狀態效果時才更新
            self._update_status_effects(dt)

        # 檢查和處理低血量狀態
        self._update_health_system(dt)

        # 檢查死亡狀態（最低優先級）
        if self.health <= 0 and self.is_alive:
            self._handle_death()

    def _update_status_effects(self, dt):
        """
        更新狀態效果\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 更新所有狀態效果的持續時間
        expired_effects = []

        for effect_name, remaining_time in self.status_effects.items():
            remaining_time -= dt

            if remaining_time <= 0:
                expired_effects.append(effect_name)
            else:
                self.status_effects[effect_name] = remaining_time

        # 移除過期的狀態效果
        for effect_name in expired_effects:
            self._remove_status_effect(effect_name)

    def _update_health_system(self, dt):
        """
        更新血量管理系統\n
        \n
        處理低血量時的心跳聲和自動回復\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        current_time = pygame.time.get_ticks() / 1000.0
        
        # 檢查是否血量低於閾值
        if self.health < HEALTH_LOW_THRESHOLD:
            if not self.low_health_active:
                print("🫀 血量過低，開始播放心跳聲並自動回復")
                self.low_health_active = True
                self.heartbeat_sound_playing = True
                # TODO: 實際播放心跳聲音檔案
            
            # 自動回復血量
            if current_time - self.last_health_recovery_time >= 1.0:  # 每秒回復一次
                old_health = self.health
                self.health = min(HEALTH_LOW_THRESHOLD, self.health + HEALTH_AUTO_RECOVERY_RATE)
                self.last_health_recovery_time = current_time
                
                if self.health > old_health:
                    print(f"💚 自動回復血量 +{self.health - old_health}，當前血量: {self.health}")
                
                # 如果回復到閾值以上，停止心跳聲
                if self.health >= HEALTH_LOW_THRESHOLD:
                    self.low_health_active = False
                    self.heartbeat_sound_playing = False
                    print("💚 血量已回復到安全水平，停止心跳聲")
        else:
            # 血量正常，確保停止心跳聲
            if self.low_health_active:
                self.low_health_active = False
                self.heartbeat_sound_playing = False

    def _remove_status_effect(self, effect_name):
        """
        移除狀態效果\n
        \n
        參數:\n
        effect_name (str): 狀態效果名稱\n
        """
        if effect_name in self.status_effects:
            del self.status_effects[effect_name]
            print(f"狀態效果 {effect_name} 已結束")

    def take_damage(self, damage, source=None):
        """
        受到傷害\n
        \n
        參數:\n
        damage (int): 傷害值\n
        source (object): 傷害來源\n
        \n
        回傳:\n
        bool: 是否成功造成傷害\n
        """
        # 檢查無敵時間
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_damage_time < self.invulnerable_time:
            return False

        # 扣除生命值
        self.health = max(0, self.health - damage)
        self.last_damage_time = current_time

        print(f"玩家受到 {damage} 點傷害！剩餘生命值: {self.health}")

        # 檢查死亡
        if self.health <= 0:
            self._handle_death(source)
            return True

        return True

    def heal(self, amount):
        """
        恢復生命值\n
        \n
        參數:\n
        amount (int): 恢復量\n
        """
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        healed = self.health - old_health

        if healed > 0:
            print(f"恢復了 {healed} 點生命值！當前生命值: {self.health}")

    def _handle_death(self, source=None):
        """
        處理玩家死亡\n
        \n
        參數:\n
        source (object): 死亡來源，如動物實例等\n
        """
        self.is_alive = False
        self.death_source = source  # 記錄死亡來源
        print("玩家死亡了...")
        
        # 根據新需求：玩家死亡後自動傳送到最近醫院並恢復生命值為100
        self._teleport_to_hospital()

    def _teleport_to_hospital(self):
        """
        傳送玩家到最近的醫院並恢復部分生命值\n
        """
        # 小鎮醫院位置（假設醫院在小鎮中心附近）
        hospital_positions = [
            (2000, 2900),  # 小鎮中心醫院
            (1800, 2800),  # 備用醫院位置
        ]
        
        # 選擇最近的醫院（這裡簡化為選第一個）
        hospital_x, hospital_y = hospital_positions[0]
        
        # 傳送到醫院
        self.x = hospital_x
        self.y = hospital_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # 恢復生命值為100
        self.health = 100
        self.is_alive = True
        
        print(f"玩家已被傳送到醫院 ({hospital_x}, {hospital_y})，生命值恢復至 {self.health}")
        
        # 重置受傷狀態
        self.is_injured = False
        self.last_damage_time = 0

    def respawn(self, position=None):
        """
        重生玩家\n
        \n
        參數:\n
        position (tuple): 重生位置，None表示使用預設重生點\n
        """
        if position:
            self.x, self.y = position
        elif self.spawn_position:
            self.x, self.y = self.spawn_position
        else:
            self.x, self.y = self.last_safe_position

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.health = self.max_health
        self.is_alive = True

        print(f"玩家在 ({self.x}, {self.y}) 重生")

    def set_spawn_position(self, position):
        """
        設定重生位置\n
        \n
        參數:\n
        position (tuple): 重生位置 (x, y)\n
        """
        self.spawn_position = position

    def set_terrain_system(self, terrain_system):
        """
        設定地形系統引用，用於碰撞檢測\n
        \n
        參數:\n
        terrain_system (TerrainBasedSystem): 地形系統實例\n
        """
        self.terrain_system = terrain_system

    def _update_movement(self, dt):
        """
        更新角色移動邏輯 - 已優化效能，支援奔跑功能和碰撞檢測\n
        \n
        根據當前方向和速度計算新位置\n
        使用快速的移動計算避免不必要的正規化\n
        優化常見移動情況的計算速度\n
        支援 Shift 鍵奔跑功能\n
        包含樹木和水域碰撞檢測\n
        \n
        參數:\n
        dt (float): 時間間隔，用於幀率無關的移動計算\n
        """
        # 如果沒有移動方向，就不需要移動
        if self.direction_x == 0 and self.direction_y == 0:
            return
        
        # 調試輸出：檢查移動參數（簡化版）
        if hasattr(self, '_debug_counter'):
            self._debug_counter += 1
        else:
            self._debug_counter = 0
        
        # 根據是否在載具中或奔跑狀態調整速度
        if self.in_vehicle:
            current_speed = VEHICLE_SPEED
        elif self.is_running:
            current_speed = self.run_speed  # 奔跑速度
        else:
            current_speed = self.speed  # 正常行走速度
        
        # 每180幀（約3秒）輸出一次調試信息，只在有移動時
        if self._debug_counter % 180 == 0 and (self.direction_x != 0 or self.direction_y != 0):
            print(f"玩家移動調試 - 方向: ({self.direction_x}, {self.direction_y}), 位置: ({self.x:.1f}, {self.y:.1f})")
            print(f"玩家當前速度: {current_speed}, 奔跑狀態: {self.is_running}")

        # 使用 dt 進行幀率無關的移動計算
        # current_speed 是像素/秒，dt 是秒，所以 move = speed * dt
        if self.direction_x == 0 or self.direction_y == 0:
            # 單軸移動（上下左右）- 最快的情況
            move_x = self.direction_x * current_speed * dt
            move_y = self.direction_y * current_speed * dt
        else:
            # 斜向移動 - 使用預計算的係數避免平方根運算
            diagonal_speed = current_speed * 0.7071067811865476  # 1/√2
            move_x = self.direction_x * diagonal_speed * dt
            move_y = self.direction_y * diagonal_speed * dt

        # 計算新位置
        new_x = self.x + move_x
        new_y = self.y + move_y

        # 碰撞檢測 - 檢查是否可以移動到新位置
        if self.terrain_system:
            # 分別檢查 X 和 Y 方向的移動，允許滑牆效果
            can_move_x = self.terrain_system.can_move_to_position(new_x, self.y, self.rect)
            can_move_y = self.terrain_system.can_move_to_position(self.x, new_y, self.rect)
            
            # 調試：碰撞檢測結果（簡化版）
            if self._debug_counter % 180 == 0:
                print(f"碰撞檢測 - 新位置: ({new_x:.1f}, {new_y:.1f}), 可移動X: {can_move_x}, 可移動Y: {can_move_y}")
            
            # 只有在不會發生碰撞時才移動
            old_x, old_y = self.x, self.y
            if can_move_x:
                self.x = new_x
            if can_move_y:
                self.y = new_y
                
            # 調試：實際移動結果（簡化版）
            if self._debug_counter % 180 == 0:
                moved_x = self.x - old_x
                moved_y = self.y - old_y
                if moved_x != 0 or moved_y != 0:  # 只在實際有移動時輸出
                    print(f"實際移動 - 移動量: ({moved_x:.3f}, {moved_y:.3f})")
        else:
            # 沒有地形系統時直接移動（後備方案）
            self.x = new_x
            self.y = new_y

        # 更新最後安全位置（只有當玩家不在水中或建築物內時）
        if self.terrain_system:
            if self.terrain_system.can_move_to_position(self.x, self.y, self.rect):
                self.last_safe_position = (self.x, self.y)

    def _update_facing_direction(self):
        """
        更新角色面朝方向\n
        \n
        根據移動方向決定角色朝向\n
        用於動畫播放和互動判定\n
        """
        # 只有在移動時才更新面朝方向
        if not self.is_moving:
            return

        # 根據移動方向決定面朝方向
        if abs(self.direction_x) > abs(self.direction_y):
            # 水平移動為主
            if self.direction_x > 0:
                self.facing_direction = "right"
            else:
                self.facing_direction = "left"
        else:
            # 垂直移動為主
            if self.direction_y > 0:
                self.facing_direction = "down"
            else:
                self.facing_direction = "up"

    def set_movement_direction(self, direction_x, direction_y):
        """
        設定角色移動方向\n
        \n
        由輸入系統調用，設定角色的移動方向\n
        方向值應該在 -1 到 1 之間\n
        \n
        參數:\n
        direction_x (float): X 軸移動方向，-1 左，1 右，0 不移動\n
        direction_y (float): Y 軸移動方向，-1 上，1 下，0 不移動\n
        """
        self.direction_x = clamp(direction_x, -1, 1)
        self.direction_y = clamp(direction_y, -1, 1)

    def stop_movement(self):
        """
        停止角色移動\n
        \n
        將移動方向設為零，讓角色停止移動\n
        """
        self.direction_x = 0
        self.direction_y = 0

    def set_running(self, is_running):
        """
        設定奔跑狀態\n
        \n
        參數:\n
        is_running (bool): True 表示開始奔跑，False 表示停止奔跑\n
        """
        self.is_running = is_running

    def start_running(self):
        """
        開始奔跑\n
        """
        self.is_running = True

    def stop_running(self):
        """
        停止奔跑\n
        """
        self.is_running = False

    def set_position(self, x, y):
        """
        直接設定角色位置\n
        \n
        用於場景切換、傳送等功能\n
        \n
        參數:\n
        x (int): 新的 X 座標\n
        y (int): 新的 Y 座標\n
        """
        self.x = x
        self.y = y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        print(f"玩家位置設定為: ({self.x}, {self.y})")

    def get_position(self):
        """
        獲取角色當前位置\n
        \n
        回傳:\n
        tuple: (x, y) 座標\n
        """
        return (self.x, self.y)

    def get_center_position(self):
        """
        獲取角色中心點位置\n
        \n
        回傳:\n
        tuple: (center_x, center_y) 中心座標\n
        """
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        return (center_x, center_y)

    def get_relative_position(self):
        """
        獲取相對於家的位置（以家為原點 0,0）\n
        \n
        回傳:\n
        tuple: (relative_x, relative_y) 相對座標\n
        """
        relative_x = int(self.x - HOME_WORLD_X)
        relative_y = int(self.y - HOME_WORLD_Y)
        return (relative_x, relative_y)

    ######################物品欄系統方法######################
    # 簡化的物品系統，支援狩獵和砍樹獎勵
    
    def add_item(self, item_name, quantity=1):
        """
        添加物品到玩家背包\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 物品數量，範圍 > 0\n
        \n
        回傳:\n
        bool: 成功添加返回 True，否則返回 False\n
        """
        if not hasattr(self, 'simple_inventory'):
            self.simple_inventory = {}
        
        if item_name in self.simple_inventory:
            self.simple_inventory[item_name] += quantity
        else:
            self.simple_inventory[item_name] = quantity
        
        print(f"📦 獲得物品: {item_name} x{quantity}")
        return True

    def remove_item(self, item_name, quantity=1):
        """
        從玩家背包移除物品\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 移除數量，範圍 > 0\n
        \n
        回傳:\n
        bool: 成功移除返回 True，否則返回 False\n
        """
        if not hasattr(self, 'simple_inventory'):
            self.simple_inventory = {}
            return False
        
        if item_name not in self.simple_inventory:
            return False
        
        if self.simple_inventory[item_name] >= quantity:
            self.simple_inventory[item_name] -= quantity
            if self.simple_inventory[item_name] == 0:
                del self.simple_inventory[item_name]
            return True
        return False

    def has_item(self, item_name, quantity=1):
        """檢查玩家是否擁有指定數量的物品"""
        if not hasattr(self, 'simple_inventory'):
            self.simple_inventory = {}
            return False
        return self.simple_inventory.get(item_name, 0) >= quantity

    def get_item_count(self, item_name):
        """獲取指定物品的數量"""
        if not hasattr(self, 'simple_inventory'):
            self.simple_inventory = {}
            return 0
        return self.simple_inventory.get(item_name, 0)

    def get_item_slots(self):
        """獲取物品格子列表，簡化版本返回字典"""
        if not hasattr(self, 'simple_inventory'):
            self.simple_inventory = {}
        return self.simple_inventory

    def get_inventory_list(self):
        """
        獲取物品清單\n
        \n
        回傳:\n
        list: 物品清單，每個元素是 (物品名稱, 數量) 的元組\n
        """
        if not hasattr(self, 'simple_inventory'):
            self.simple_inventory = {}
        return list(self.simple_inventory.items())

    def select_slot(self, slot_index):
        """簡化版本 - 不實作格子選擇功能"""
        pass

    def get_selected_item(self):
        """簡化版本 - 返回 None"""
        return None

    ######################魚餌系統方法######################
    def get_current_bait(self):
        """
        獲取當前使用的魚餌\n
        \n
        回傳:\n
        str: 當前魚餌名稱\n
        """
        return self.current_bait

    def set_current_bait(self, bait_name):
        """
        設定當前使用的魚餌\n
        \n
        參數:\n
        bait_name (str): 魚餌名稱\n
        \n
        回傳:\n
        bool: 是否成功設定\n
        """
        if bait_name in self.bait_inventory:
            if self.bait_inventory[bait_name] > 0 or self.bait_inventory[bait_name] == -1:
                self.current_bait = bait_name
                print(f"🎣 切換到 {bait_name}")
                return True
            else:
                print(f"❌ {bait_name} 數量不足")
                return False
        return False

    def add_bait(self, bait_name, quantity):
        """
        添加魚餌\n
        \n
        參數:\n
        bait_name (str): 魚餌名稱\n
        quantity (int): 數量\n
        """
        if bait_name in self.bait_inventory:
            if self.bait_inventory[bait_name] == -1:
                return  # 普通魚餌無限，不需要添加
            self.bait_inventory[bait_name] += quantity
            print(f"獲得 {bait_name} x{quantity}")

    def use_bait(self):
        """
        使用一個魚餌\n
        \n
        回傳:\n
        bool: 是否成功使用\n
        """
        if self.current_bait in self.bait_inventory:
            if self.bait_inventory[self.current_bait] == -1:
                return True  # 普通魚餌無限使用
            elif self.bait_inventory[self.current_bait] > 0:
                self.bait_inventory[self.current_bait] -= 1
                print(f"使用 {self.current_bait}，剩餘: {self.bait_inventory[self.current_bait]}")
                return True
        return False

    def get_bait_multiplier(self):
        """
        獲取當前魚餌的效果倍數\n
        \n
        回傳:\n
        float: 魚餌效果倍數\n
        """
        if self.current_bait in BAIT_TYPES:
            return BAIT_TYPES[self.current_bait]["multiplier"]
        return 1.0

    ######################血量藥水方法######################
    def use_health_potion(self, potion_type):
        """
        使用血量藥水\n
        \n
        參數:\n
        potion_type (str): 藥水類型\n
        \n
        回傳:\n
        bool: 是否成功使用\n
        """
        if potion_type in HEALTH_POTIONS:
            heal_amount = HEALTH_POTIONS[potion_type]["heal_amount"]
            old_health = self.health
            self.health = min(self.max_health, self.health + heal_amount)
            actual_heal = self.health - old_health
            
            if actual_heal > 0:
                print(f"🧪 使用 {potion_type}，回復 {actual_heal} 血量！當前血量: {self.health}")
                return True
            else:
                print("血量已滿，無需使用藥水")
                return False
        return False

    def release_fish_for_health(self):
        """
        放生魚類獲得血量加成\n
        \n
        回傳:\n
        int: 實際回復的血量\n
        """
        old_health = self.health
        new_health = min(self.max_health, int(self.health * FISH_RELEASE_HEALTH_MULTIPLIER))
        self.health = new_health
        actual_heal = new_health - old_health
        
        if actual_heal > 0:
            print(f"🐟 放生魚類，血量增加 {actual_heal}！當前血量: {self.health}")
        else:
            print("🐟 放生魚類，但血量已達上限")
        
        return actual_heal

    ######################金錢系統方法######################
    def add_money(self, amount):
        """
        增加金錢\n
        \n
        參數:\n
        amount (int): 要增加的金錢數量\n
        """
        if amount > 0:
            self.money += amount
            print(f"獲得金錢: ${amount}，總計: ${self.money}")

    def spend_money(self, amount):
        """
        花費金錢\n
        \n
        檢查金錢是否足夠並扣除\n
        \n
        參數:\n
        amount (int): 要花費的金錢數量\n
        \n
        回傳:\n
        bool: True 表示成功花費，False 表示金錢不足\n
        """
        if amount <= 0:
            return False

        if self.money >= amount:
            self.money -= amount
            print(f"花費金錢: ${amount}，剩餘: ${self.money}")
            return True
        else:
            print(f"金錢不足，需要 ${amount}，現有 ${self.money}")
            return False

    def get_money(self):
        """
        獲取當前金錢數量\n
        \n
        回傳:\n
        int: 當前金錢數量\n
        """
        return self.money

    def spawn_at_player_home(self, player_home):
        """
        將玩家生成在玩家之家門口（安全位置）\n
        \n
        參數:\n
        player_home (ResidentialHouse): 玩家之家建築物件\n
        """
        if self.needs_home_spawn and player_home:
            # 將玩家放在建築物下方（門口位置），而不是建築物內部
            home_x = player_home.x + player_home.width // 2  # 建築物中央 X 位置
            home_y = player_home.y + player_home.height + 20  # 建築物下方 20 像素（門口位置）
            self.set_position(home_x, home_y)
            
            # 設定重生點為離家最近的草原
            self._set_respawn_point_near_home(player_home)
            
            self.needs_home_spawn = False
            print(f"玩家已生成在玩家之家門口: ({home_x}, {home_y})")
            
            # 驗證位置是否安全（可移動）
            if self.terrain_system:
                can_move = self.terrain_system.can_move_to_position(home_x, home_y, self.rect)
                if not can_move:
                    # 如果門口位置也不安全，嘗試更遠的位置
                    alternative_y = player_home.y + player_home.height + 50
                    self.set_position(home_x, alternative_y)
                    print(f"門口位置不安全，移動到更遠位置: ({home_x}, {alternative_y})")
                else:
                    print("玩家位置驗證通過，可以正常移動")

    def _set_respawn_point_near_home(self, player_home):
        """
        設定離家最近的草原為重生點\n
        \n
        參數:\n
        player_home (ResidentialHouse): 玩家之家建築物件\n
        """
        if not self.terrain_system:
            # 沒有地形系統時使用預設重生點
            self.spawn_position = (player_home.x, player_home.y + player_home.height + 50)
            return
        
        home_center_x = player_home.x + player_home.width // 2
        home_center_y = player_home.y + player_home.height // 2
        
        # 在家周圍搜索最近的草原（地形編碼0）
        best_distance = float('inf')
        best_position = None
        search_radius = 200  # 搜索半徑
        
        for radius in range(50, search_radius, 20):
            for angle_step in range(0, 360, 30):
                angle = angle_step * 3.14159 / 180
                test_x = home_center_x + radius * math.cos(angle)
                test_y = home_center_y + radius * math.sin(angle)
                
                # 檢查是否為草原且可移動
                if self._is_grassland_position(test_x, test_y):
                    distance = ((test_x - home_center_x) ** 2 + (test_y - home_center_y) ** 2) ** 0.5
                    if distance < best_distance:
                        best_distance = distance
                        best_position = (test_x, test_y)
        
        if best_position:
            self.spawn_position = best_position
            print(f"🏠 重生點設定為離家最近的草原: ({best_position[0]:.1f}, {best_position[1]:.1f})")
        else:
            # 找不到草原時使用預設位置
            self.spawn_position = (home_center_x, home_center_y + 100)
            print(f"⚠️ 找不到草原，使用預設重生點: ({self.spawn_position[0]:.1f}, {self.spawn_position[1]:.1f})")

    def _is_grassland_position(self, x, y):
        """
        檢查位置是否為草原\n
        \n
        參數:\n
        x (float): X座標\n
        y (float): Y座標\n
        \n
        回傳:\n
        bool: 是否為草原且可移動\n
        """
        if not self.terrain_system:
            return True
        
        # 檢查地形類型是否為草原（編碼0）
        terrain_type = self.terrain_system.get_terrain_at_position(x, y)
        if terrain_type != 0:  # 不是草原
            return False
        
        # 檢查是否可移動
        dummy_rect = pygame.Rect(x-4, y-4, 8, 8)
        return self.terrain_system.can_move_to_position(x, y, dummy_rect)

    def get_health_percentage(self):
        """
        獲取生命值百分比\n
        \n
        回傳:\n
        float: 生命值百分比 (0.0 - 1.0)\n
        """
        return self.health / self.max_health if self.max_health > 0 else 0
    ######################載具系統方法######################
    def enter_vehicle(self):
        """
        進入載具\n
        \n
        改變玩家狀態為載具模式，提升移動速度\n
        """
        self.in_vehicle = True
        print("玩家進入載具")

    def exit_vehicle(self):
        """
        離開載具\n
        \n
        恢復玩家正常移動狀態\n
        """
        self.in_vehicle = False
        print("玩家離開載具")

    ######################工具系統方法######################
    def equip_tool(self, tool_name):
        """
        裝備工具\n
        \n
        設定當前使用的工具\n
        \n
        參數:\n
        tool_name (str): 工具名稱\n
        """
        self.current_tool = tool_name
        print(f"裝備工具: {tool_name}")

    def unequip_tool(self):
        """
        卸下工具\n
        \n
        清除當前使用的工具\n
        """
        if self.current_tool:
            print(f"卸下工具: {self.current_tool}")
            self.current_tool = None

    def get_current_tool(self):
        """
        獲取當前裝備的工具\n
        \n
        回傳:\n
        str: 當前工具名稱，如果沒有則回傳 None\n
        """
        return self.current_tool

    ######################繪製方法######################
    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製玩家角色\n
        \n
        在螢幕上繪製角色的視覺表現\n
        目前使用簡單的矩形代替圖片素材\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 X 偏移\n
        camera_y (int): 攝影機 Y 偏移\n
        """
        if not self.is_alive:
            return

        # 如果正在駕駛，不繪製玩家 (被載具遮擋)
        if self.is_driving:
            return

        # 計算螢幕座標
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        screen_rect = pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height)

        # 繪製角色主體（使用當前服裝顏色）
        pygame.draw.rect(screen, self.color, screen_rect)

        # 根據面朝方向繪製簡單的方向指示
        self._draw_direction_indicator(screen, camera_x, camera_y)

        # 繪製生命值條 (如果受傷)
        if self.is_injured:
            self._draw_health_bar(screen, camera_x, camera_y)

    def _draw_direction_indicator(self, screen, camera_x=0, camera_y=0):
        """
        繪製方向指示器\n
        \n
        在角色身上繪製等腰三角形表示面朝方向\n
        這與小地圖上的表示方式一致\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 X 偏移\n
        camera_y (int): 攝影機 Y 偏移\n
        """
        indicator_color = (255, 255, 255)  # 白色指示三角形
        size = 2  # 三角形大小（調整為配合縮小的玩家尺寸）

        # 計算角色螢幕中心位置
        center_x = self.rect.centerx - camera_x
        center_y = self.rect.centery - camera_y

        # 根據面朝方向計算三角形的三個頂點
        if self.facing_direction == "up":
            # 頂點朝上
            points = [
                (center_x, center_y - size),          # 頂點
                (center_x - size//2, center_y + size//2),  # 左下
                (center_x + size//2, center_y + size//2)   # 右下
            ]
        elif self.facing_direction == "down":
            # 頂點朝下
            points = [
                (center_x, center_y + size),          # 頂點
                (center_x - size//2, center_y - size//2),  # 左上
                (center_x + size//2, center_y - size//2)   # 右上
            ]
        elif self.facing_direction == "left":
            # 頂點朝左
            points = [
                (center_x - size, center_y),          # 頂點
                (center_x + size//2, center_y - size//2),  # 右上
                (center_x + size//2, center_y + size//2)   # 右下
            ]
        elif self.facing_direction == "right":
            # 頂點朝右
            points = [
                (center_x + size, center_y),          # 頂點
                (center_x - size//2, center_y - size//2),  # 左上
                (center_x - size//2, center_y + size//2)   # 左下
            ]
        else:
            # 預設朝下
            points = [
                (center_x, center_y + size),
                (center_x - size//2, center_y - size//2),
                (center_x + size//2, center_y - size//2)
            ]

        # 繪製方向指示三角形
        pygame.draw.polygon(screen, indicator_color, points)

    def _draw_health_bar(self, screen, camera_x=0, camera_y=0):
        """
        繪製生命值條\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        camera_x (int): 攝影機 X 偏移\n
        camera_y (int): 攝影機 Y 偏移\n
        """
        bar_width = self.rect.width
        bar_height = 4
        bar_x = self.rect.x - camera_x
        bar_y = self.rect.y - camera_y - 8

        # 背景條 (紅色)
        background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (255, 0, 0), background_rect)

        # 生命值條 (綠色)
        health_width = int(bar_width * self.get_health_percentage())
        if health_width > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            pygame.draw.rect(screen, (0, 255, 0), health_rect)

    def draw_item_bar(self, screen):
        """
        物品欄已刪除 - 此方法不再繪製任何內容\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        # 物品欄功能已完全移除，不再繪製
        pass

    def _get_item_color(self, item_name):
        """
        根據物品名稱返回對應的顏色\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        \n
        回傳:\n
        tuple: RGB 顏色值\n
        """
        # 簡單的物品顏色映射
        color_map = {
            "小魚": (0, 191, 255),  # 藍色
            "鯉魚": (255, 165, 0),  # 橘色
            "鱸魚": (50, 205, 50),  # 綠色
            "虹鱒": (255, 20, 147),  # 深粉色
            "金魚王": (255, 215, 0),  # 金色
            "兔肉": (139, 69, 19),  # 棕色
            "鹿肉": (160, 82, 45),  # 淺棕色
            "熊肉": (105, 105, 105),  # 灰色
            "鳥肉": (255, 255, 255),  # 白色
            "工具": (128, 128, 128),  # 灰色
            "材料": (34, 139, 34),  # 森林綠
        }

        # 檢查物品名稱中是否包含關鍵字
        for keyword, color in color_map.items():
            if keyword in item_name:
                return color

        # 預設顏色
        return (200, 200, 200)

    ######################資料序列化方法######################
    def get_save_data(self):
        """
        獲取存檔資料\n
        \n
        將玩家狀態轉換為可儲存的字典格式\n
        \n
        回傳:\n
        dict: 包含玩家所有狀態的字典\n
        """
        return {
            "position": (self.x, self.y),
            "health": self.health,
            "max_health": self.max_health,
            "money": self.money,
            # 物品欄相關已刪除
            # "item_slots": self.item_slots.copy(),
            # "selected_slot": self.selected_slot,
            "experience": self.experience,
            "level": self.level,
            "current_outfit": self.current_outfit,
            "owned_outfits": self.owned_outfits.copy(),
            "current_tool": self.current_tool,
            "last_safe_position": self.last_safe_position,
            "spawn_position": self.spawn_position,
        }

    def load_save_data(self, save_data):
        """
        載入存檔資料\n
        \n
        從字典格式的存檔資料恢復玩家狀態\n
        \n
        參數:\n
        save_data (dict): 包含玩家狀態的字典\n
        """
        try:
            # 載入位置
            if "position" in save_data:
                x, y = save_data["position"]
                self.set_position(x, y)

            # 載入生命值
            if "health" in save_data:
                self.health = save_data["health"]
            if "max_health" in save_data:
                self.max_health = save_data["max_health"]

            # 載入金錢
            if "money" in save_data:
                self.money = save_data["money"]

            # 物品欄相關已刪除
            # if "item_slots" in save_data:
            #     self.item_slots = save_data["item_slots"].copy()
            # if "selected_slot" in save_data:
            #     self.selected_slot = save_data["selected_slot"]

            # 載入經驗值和等級
            if "experience" in save_data:
                self.experience = save_data["experience"]
            if "level" in save_data:
                self.level = save_data["level"]

            # 載入服裝
            if "current_outfit" in save_data:
                self.current_outfit = save_data["current_outfit"]
            if "owned_outfits" in save_data:
                self.owned_outfits = save_data["owned_outfits"].copy()

            # 載入工具
            if "current_tool" in save_data:
                self.current_tool = save_data["current_tool"]

            # 載入位置資訊
            if "last_safe_position" in save_data:
                self.last_safe_position = save_data["last_safe_position"]
            if "spawn_position" in save_data:
                self.spawn_position = save_data["spawn_position"]

            # 確保玩家還活著
            self.is_alive = self.health > 0

            print("玩家存檔資料載入成功")

        except Exception as e:
            print(f"載入玩家存檔資料失敗: {e}")

    def _add_initial_items(self):
        """
        添加初始物品供測試\n
        """
        # 初始化簡化物品系統
        if not hasattr(self, 'simple_inventory'):
            self.simple_inventory = {}
        
        # 給玩家一些基本物品
        self.add_item("木材", 5)
        self.add_item("麵包", 3)
        print("✅ 物品系統已初始化，添加了基本物品")

    ######################裝備系統方法######################
    def toggle_equipment_wheel(self):
        """
        切換裝備圓盤顯示狀態\n
        """
        self.equipment_wheel_visible = not self.equipment_wheel_visible
        print(f"裝備圓盤 {'顯示' if self.equipment_wheel_visible else '隱藏'}")

    def equip_item(self, slot_number):
        """
        裝備指定槽位的物品\n
        \n
        參數:\n
        slot_number (int): 裝備槽位編號 (1-5)\n
        """
        if slot_number not in self.equipment_slots:
            return False
        
        # 先卸下當前裝備
        if self.current_equipment:
            self.equipment_slots[self.current_equipment]["equipped"] = False
        
        # 裝備新物品
        equipment = self.equipment_slots[slot_number]
        equipment["equipped"] = True
        self.current_equipment = slot_number
        
        print(f"🔧 裝備了 {equipment['name']}")
        
        # 隱藏裝備圓盤
        self.equipment_wheel_visible = False
        
        return True

    def get_current_equipment(self):
        """
        獲取當前裝備的物品\n
        \n
        回傳:\n
        dict: 當前裝備資訊，如果沒有裝備則回傳 None\n
        """
        if self.current_equipment is None:
            return None
        return self.equipment_slots[self.current_equipment]

    def has_equipment(self, equipment_name):
        """
        檢查是否擁有指定裝備\n
        \n
        參數:\n
        equipment_name (str): 裝備名稱\n
        \n
        回傳:\n
        bool: 是否擁有該裝備\n
        """
        for slot_data in self.equipment_slots.values():
            if slot_data["name"] == equipment_name:
                return True
        return False

    def is_equipment_equipped(self, equipment_name):
        """
        檢查指定裝備是否已裝備\n
        \n
        參數:\n
        equipment_name (str): 裝備名稱\n
        \n
        回傳:\n
        bool: 是否已裝備\n
        """
        current = self.get_current_equipment()
        return current is not None and current["name"] == equipment_name

    ######################武器圓盤系統方法######################
    def toggle_weapon_wheel(self):
        """
        切換武器圓盤顯示狀態\n
        """
        self.weapon_wheel_visible = not self.weapon_wheel_visible
        print(f"武器圓盤 {'顯示' if self.weapon_wheel_visible else '隱藏'}")

    def select_weapon(self, weapon_type):
        """
        選擇武器\n
        \n
        參數:\n
        weapon_type (str): 武器類型 ("gun", "axe", "unarmed")\n
        \n
        回傳:\n
        bool: 是否成功選擇\n
        """
        if weapon_type in self.available_weapons and self.available_weapons[weapon_type]["unlocked"]:
            self.current_weapon = weapon_type
            weapon_name = self.available_weapons[weapon_type]["name"]
            print(f"🔫 切換到武器: {weapon_name}")
            
            # 隱藏武器圓盤
            self.weapon_wheel_visible = False
            return True
        return False

    def get_current_weapon(self):
        """
        獲取當前武器類型\n
        \n
        回傳:\n
        str: 當前武器類型\n
        """
        return self.current_weapon

    def get_current_weapon_name(self):
        """
        獲取當前武器的中文名稱\n
        \n
        回傳:\n
        str: 當前武器名稱\n
        """
        return self.available_weapons[self.current_weapon]["name"]

    def can_shoot(self):
        """
        檢查是否可以射擊\n
        考慮新的武器管理器系統\n
        \n
        回傳:\n
        bool: 是否可以射擊\n
        """
        if hasattr(self, 'weapon_manager') and self.weapon_manager:
            current_weapon = self.weapon_manager.current_weapon
            if current_weapon and current_weapon.weapon_type in ["pistol", "rifle", "shotgun", "sniper"]:
                return current_weapon.can_shoot()
        # 回退到原有邏輯（BB槍永遠可以射擊）
        return True

    def can_chop(self):
        """
        檢查是否可以砍伐\n
        \n
        回傳:\n
        bool: 當前武器是否可以砍伐\n
        """
        return self.current_weapon == "axe"

    def get_weapon_damage(self):
        """
        獲取當前武器的傷害值\n
        \n
        回傳:\n
        int: 當前武器的傷害值\n
        """
        if hasattr(self, 'weapon_manager') and self.weapon_manager:
            current_weapon = self.weapon_manager.current_weapon
            if current_weapon:
                return current_weapon.damage
        # 回退到BB槍的預設傷害
        return BB_GUN_DAMAGE
