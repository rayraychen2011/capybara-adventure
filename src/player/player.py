######################載入套件######################
import pygame
import math
from config.settings import *
from src.utils.helpers import clamp, normalize_vector


######################玩家角色類別######################
class Player:
    """
    玩家角色類別 - 代表遊戲中的主角\n
    \n
    管理玩家角色的所有屬性和行為，包括：\n
    - 位置和移動控制\n
    - 生命值和死亡重生系統\n
    - 外觀和動畫\n
    - 物品背包管理\n
    - 金錢和經驗值\n
    - 武器和載具系統\n
    - 各種遊戲狀態\n
    \n
    使用幾何形狀暫代圖片素材，提供完整的角色功能\n
    """

    def __init__(self, x=PLAYER_START_X, y=PLAYER_START_Y):
        """
        初始化玩家角色\n
        \n
        設定角色的初始位置、外觀、屬性和狀態\n
        建立背包系統和各種遊戲數據\n
        \n
        參數:\n
        x (int): 初始 X 座標位置，預設為螢幕中央\n
        y (int): 初始 Y 座標位置，預設為螢幕中央\n
        """
        ######################位置和移動屬性######################
        # 玩家當前位置
        self.x = x
        self.y = y

        # 玩家尺寸
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        # 移動速度
        self.speed = PLAYER_SPEED

        # 當前移動方向（單位向量）
        self.direction_x = 0
        self.direction_y = 0

        # 面朝方向（用於動畫和互動）
        self.facing_direction = "down"  # "up", "down", "left", "right"

        ######################生命值系統######################
        # 生命值
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_INITIAL_HEALTH
        self.is_alive = True
        self.last_damage_time = 0
        self.invulnerable_time = 2.0  # 受傷後無敵時間 (秒)

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

        # 背包系統
        self.inventory = {}  # {物品名稱: 數量}
        self.inventory_capacity = INVENTORY_CAPACITY

        # 添加一些初始物品供測試
        self._add_initial_items()

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

        # 狀態效果
        self.status_effects = {}  # 狀態效果名稱 -> 剩餘時間

        print(f"玩家角色已建立，位置: ({self.x}, {self.y})")

    def update(self, dt):
        """
        更新玩家角色狀態\n
        \n
        每幀調用一次，更新角色的移動、動畫和其他狀態\n
        \n
        參數:\n
        dt (float): 與上一幀的時間差，單位為秒\n
        """
        # 處理移動
        self._update_movement(dt)

        # 更新碰撞矩形位置
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # 更新面朝方向
        self._update_facing_direction()

        # 檢查是否正在移動
        self.is_moving = self.direction_x != 0 or self.direction_y != 0

        # 更新狀態效果
        self._update_status_effects(dt)

        # 檢查死亡狀態
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
            self._handle_death()
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

    def _handle_death(self):
        """
        處理玩家死亡\n
        """
        self.is_alive = False
        print("玩家死亡了...")

        # 這裡會觸發死亡重生機制
        # 實際的重生邏輯會在遊戲管理器中處理

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

    def start_driving(self, vehicle):
        """
        開始駕駛載具\n
        \n
        參數:\n
        vehicle (Vehicle): 載具物件\n
        \n
        回傳:\n
        bool: 是否成功開始駕駛\n
        """
        if vehicle.get_on(self):
            self.current_vehicle = vehicle
            self.is_driving = True
            print(f"開始駕駛 {vehicle.name}")
            return True
        return False

    def stop_driving(self):
        """
        停止駕駛載具\n
        \n
        回傳:\n
        tuple: 下車位置 (x, y)\n
        """
        if self.current_vehicle:
            exit_position = self.current_vehicle.get_off()
            self.current_vehicle = None
            self.is_driving = False

            # 設定玩家到下車位置
            self.x, self.y = exit_position
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

            print("停止駕駛")
            return exit_position
        return (self.x, self.y)

    def clear_inventory(self):
        """
        清空背包 (死亡時使用)\n
        \n
        回傳:\n
        dict: 清空前的物品列表\n
        """
        old_inventory = self.inventory.copy()
        self.inventory.clear()
        return old_inventory

    def equip_weapon(self, weapon):
        """
        裝備武器\n
        \n
        參數:\n
        weapon (Weapon): 武器物件\n
        """
        self.equipped_weapon = weapon
        print(f"裝備了 {weapon.name}")

    def get_equipped_weapon(self):
        """
        獲取當前裝備的武器\n
        \n
        回傳:\n
        Weapon: 武器物件，如果沒有則返回 None\n
        """
        return self.equipped_weapon

    def change_outfit(self, outfit_index):
        """
        更換服裝\n
        \n
        參數:\n
        outfit_index (int): 服裝索引\n
        \n
        回傳:\n
        bool: 是否成功更換\n
        """
        if outfit_index in self.owned_outfits:
            self.current_outfit = outfit_index

            # 更新服裝顏色
            if outfit_index < len(CLOTHING_COLORS):
                self.color = CLOTHING_COLORS[outfit_index]
            else:
                self.color = PLAYER_COLOR

            print(f"更換為服裝 {outfit_index}")
            return True
        return False

    def unlock_outfit(self, outfit_index):
        """
        解鎖新服裝\n
        \n
        參數:\n
        outfit_index (int): 服裝索引\n
        """
        if outfit_index not in self.owned_outfits:
            self.owned_outfits.append(outfit_index)
            print(f"解鎖了新服裝 {outfit_index}")

    def get_health_percentage(self):
        """
        獲取生命值百分比\n
        \n
        回傳:\n
        float: 生命值百分比 (0.0 到 1.0)\n
        """
        return self.health / self.max_health

    def is_injured(self):
        """
        檢查是否受傷\n
        \n
        回傳:\n
        bool: 是否受傷 (生命值小於最大值)\n
        """
        return self.health < self.max_health

    def _update_movement(self, dt):
        """
        更新角色移動邏輯\n
        \n
        根據當前方向和速度計算新位置\n
        確保移動速度在各個方向保持一致\n
        \n
        參數:\n
        dt (float): 時間間隔，用於幀率無關的移動計算\n
        """
        # 如果沒有移動方向，就不需要移動
        if self.direction_x == 0 and self.direction_y == 0:
            return

        # 正規化移動向量，確保斜向移動速度正確
        direction = normalize_vector((self.direction_x, self.direction_y))

        # 根據是否在載具中調整速度
        if self.is_driving and self.current_vehicle:
            current_speed = self.current_vehicle.max_speed
        else:
            current_speed = self.speed

        # 計算這一幀要移動的距離
        move_distance = current_speed * dt * 60  # 乘以 60 是為了配合 60 FPS

        # 計算新位置
        new_x = self.x + direction[0] * move_distance
        new_y = self.y + direction[1] * move_distance

        if self.is_driving and self.current_vehicle:
            # 如果正在駕駛，移動載具
            self.current_vehicle.x = new_x
            self.current_vehicle.y = new_y
            # 玩家位置跟隨載具
            self.x = new_x + self.current_vehicle.width // 2 - self.width // 2
            self.y = new_y + self.current_vehicle.height // 2 - self.height // 2
        else:
            # 正常移動，限制角色不能移出螢幕邊界
            self.x = clamp(new_x, 0, SCREEN_WIDTH - self.width)
            self.y = clamp(new_y, 0, SCREEN_HEIGHT - self.height)

        # 更新安全位置 (如果沒有危險)
        if self.is_alive:
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
        self.x = clamp(x, 0, SCREEN_WIDTH - self.width)
        self.y = clamp(y, 0, SCREEN_HEIGHT - self.height)
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

    ######################背包系統方法######################
    def add_item(self, item_name, quantity=1):
        """
        將物品加入背包\n
        \n
        檢查背包容量並添加物品\n
        如果物品已存在則增加數量\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 要添加的數量，預設為 1\n
        \n
        回傳:\n
        bool: True 表示成功添加，False 表示背包已滿\n
        """
        # 檢查背包是否還有空間
        current_items = sum(self.inventory.values())
        if current_items + quantity > self.inventory_capacity:
            print(f"背包已滿，無法添加 {item_name}")
            return False

        # 添加物品到背包
        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity

        print(f"添加物品: {item_name} x{quantity}")
        return True

    def remove_item(self, item_name, quantity=1):
        """
        從背包移除物品\n
        \n
        檢查物品數量並移除指定數量\n
        如果數量歸零則從背包中刪除\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 要移除的數量，預設為 1\n
        \n
        回傳:\n
        bool: True 表示成功移除，False 表示物品不足\n
        """
        if item_name not in self.inventory:
            print(f"背包中沒有 {item_name}")
            return False

        if self.inventory[item_name] < quantity:
            print(
                f"{item_name} 數量不足，現有 {self.inventory[item_name]}，需要 {quantity}"
            )
            return False

        # 移除物品
        self.inventory[item_name] -= quantity

        # 如果數量歸零，從背包刪除
        if self.inventory[item_name] == 0:
            del self.inventory[item_name]

        print(f"移除物品: {item_name} x{quantity}")
        return True

    def has_item(self, item_name, quantity=1):
        """
        檢查背包是否有指定物品\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 需要的數量，預設為 1\n
        \n
        回傳:\n
        bool: True 表示有足夠物品，False 表示物品不足\n
        """
        return self.inventory.get(item_name, 0) >= quantity

    def get_item_count(self, item_name):
        """
        獲取背包中指定物品的數量\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        \n
        回傳:\n
        int: 物品數量，如果沒有則回傳 0\n
        """
        return self.inventory.get(item_name, 0)

    def get_inventory_list(self):
        """
        獲取背包物品清單\n
        \n
        回傳:\n
        dict: 包含所有物品名稱和數量的字典\n
        """
        return self.inventory.copy()

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
    def draw(self, screen):
        """
        繪製玩家角色\n
        \n
        在螢幕上繪製角色的視覺表現\n
        目前使用簡單的矩形代替圖片素材\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        if not self.is_alive:
            return

        # 如果正在駕駛，不繪製玩家 (被載具遮擋)
        if self.is_driving:
            return

        # 繪製角色主體（使用當前服裝顏色）
        pygame.draw.rect(screen, self.color, self.rect)

        # 根據面朝方向繪製簡單的方向指示
        self._draw_direction_indicator(screen)

        # 繪製生命值條 (如果受傷)
        if self.is_injured():
            self._draw_health_bar(screen)

    def _draw_direction_indicator(self, screen):
        """
        繪製方向指示器\n
        \n
        在角色身上繪製小圓點表示面朝方向\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        indicator_color = (255, 255, 255)  # 白色指示點
        indicator_size = 3

        # 根據面朝方向計算指示點位置
        center_x = self.rect.centerx
        center_y = self.rect.centery

        if self.facing_direction == "up":
            indicator_pos = (center_x, center_y - 8)
        elif self.facing_direction == "down":
            indicator_pos = (center_x, center_y + 8)
        elif self.facing_direction == "left":
            indicator_pos = (center_x - 8, center_y)
        elif self.facing_direction == "right":
            indicator_pos = (center_x + 8, center_y)
        else:
            indicator_pos = (center_x, center_y)

        # 繪製方向指示點
        pygame.draw.circle(screen, indicator_color, indicator_pos, indicator_size)

    def _draw_health_bar(self, screen):
        """
        繪製生命值條\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        bar_width = self.rect.width
        bar_height = 4
        bar_x = self.rect.x
        bar_y = self.rect.y - 8

        # 背景條 (紅色)
        background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (255, 0, 0), background_rect)

        # 生命值條 (綠色)
        health_width = int(bar_width * self.get_health_percentage())
        if health_width > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            pygame.draw.rect(screen, (0, 255, 0), health_rect)

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
            "inventory": self.inventory.copy(),
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

            # 載入背包
            if "inventory" in save_data:
                self.inventory = save_data["inventory"].copy()

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
        # 添加一些測試物品
        self.add_item("小魚", 3)
        self.add_item("鯉魚", 1)
        self.add_item("兔肉", 2)
        self.add_item("工具", 1)
        print("已添加初始測試物品")

    def _update_movement(self, dt):
        """
        更新角色移動邏輯\n
        \n
        根據當前方向和速度計算新位置\n
        確保移動速度在各個方向保持一致\n
        \n
        參數:\n
        dt (float): 時間間隔，用於幀率無關的移動計算\n
        """
        # 如果沒有移動方向，就不需要移動
        if self.direction_x == 0 and self.direction_y == 0:
            return

        # 正規化移動向量，確保斜向移動速度正確
        direction = normalize_vector((self.direction_x, self.direction_y))

        # 根據是否在載具中調整速度
        current_speed = VEHICLE_SPEED if self.in_vehicle else self.speed

        # 計算這一幀要移動的距離
        move_distance = current_speed * dt * 60  # 乘以 60 是為了配合 60 FPS

        # 計算新位置
        new_x = self.x + direction[0] * move_distance
        new_y = self.y + direction[1] * move_distance

        # 限制角色不能移出螢幕邊界
        self.x = clamp(new_x, 0, SCREEN_WIDTH - self.width)
        self.y = clamp(new_y, 0, SCREEN_HEIGHT - self.height)

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
        self.x = clamp(x, 0, SCREEN_WIDTH - self.width)
        self.y = clamp(y, 0, SCREEN_HEIGHT - self.height)
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

    ######################背包系統方法######################
    def add_item(self, item_name, quantity=1):
        """
        將物品加入背包\n
        \n
        檢查背包容量並添加物品\n
        如果物品已存在則增加數量\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 要添加的數量，預設為 1\n
        \n
        回傳:\n
        bool: True 表示成功添加，False 表示背包已滿\n
        """
        # 檢查背包是否還有空間
        current_items = sum(self.inventory.values())
        if current_items + quantity > self.inventory_capacity:
            print(f"背包已滿，無法添加 {item_name}")
            return False

        # 添加物品到背包
        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity

        print(f"添加物品: {item_name} x{quantity}")
        return True

    def remove_item(self, item_name, quantity=1):
        """
        從背包移除物品\n
        \n
        檢查物品數量並移除指定數量\n
        如果數量歸零則從背包中刪除\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 要移除的數量，預設為 1\n
        \n
        回傳:\n
        bool: True 表示成功移除，False 表示物品不足\n
        """
        if item_name not in self.inventory:
            print(f"背包中沒有 {item_name}")
            return False

        if self.inventory[item_name] < quantity:
            print(
                f"{item_name} 數量不足，現有 {self.inventory[item_name]}，需要 {quantity}"
            )
            return False

        # 移除物品
        self.inventory[item_name] -= quantity

        # 如果數量歸零，從背包刪除
        if self.inventory[item_name] == 0:
            del self.inventory[item_name]

        print(f"移除物品: {item_name} x{quantity}")
        return True

    def has_item(self, item_name, quantity=1):
        """
        檢查背包是否有指定物品\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 需要的數量，預設為 1\n
        \n
        回傳:\n
        bool: True 表示有足夠物品，False 表示物品不足\n
        """
        return self.inventory.get(item_name, 0) >= quantity

    def get_item_count(self, item_name):
        """
        獲取背包中指定物品的數量\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        \n
        回傳:\n
        int: 物品數量，如果沒有則回傳 0\n
        """
        return self.inventory.get(item_name, 0)

    def get_inventory_list(self):
        """
        獲取背包物品清單\n
        \n
        回傳:\n
        dict: 包含所有物品名稱和數量的字典\n
        """
        return self.inventory.copy()

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
    def draw(self, screen):
        """
        繪製玩家角色\n
        \n
        在螢幕上繪製角色的視覺表現\n
        目前使用簡單的矩形代替圖片素材\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        # 繪製角色主體（橘色矩形）
        pygame.draw.rect(screen, self.color, self.rect)

        # 根據面朝方向繪製簡單的方向指示
        self._draw_direction_indicator(screen)

        # 如果在載具中，繪製載具外框
        if self.in_vehicle:
            self._draw_vehicle_indicator(screen)

    def _draw_direction_indicator(self, screen):
        """
        繪製方向指示器\n
        \n
        在角色身上繪製小圓點表示面朝方向\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        indicator_color = (255, 255, 255)  # 白色指示點
        indicator_size = 3

        # 根據面朝方向計算指示點位置
        center_x = self.rect.centerx
        center_y = self.rect.centery

        if self.facing_direction == "up":
            indicator_pos = (center_x, center_y - 8)
        elif self.facing_direction == "down":
            indicator_pos = (center_x, center_y + 8)
        elif self.facing_direction == "left":
            indicator_pos = (center_x - 8, center_y)
        elif self.facing_direction == "right":
            indicator_pos = (center_x + 8, center_y)
        else:
            indicator_pos = (center_x, center_y)

        # 繪製方向指示點
        pygame.draw.circle(screen, indicator_color, indicator_pos, indicator_size)

    def _draw_vehicle_indicator(self, screen):
        """
        繪製載具指示器\n
        \n
        當玩家在載具中時，在角色周圍繪製載具外框\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        vehicle_color = (100, 100, 100)  # 灰色載具框
        vehicle_rect = pygame.Rect(
            self.rect.x - 16,
            self.rect.y - 8,
            self.rect.width + 32,
            self.rect.height + 16,
        )

        # 繪製載具外框
        pygame.draw.rect(screen, vehicle_color, vehicle_rect, 3)

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
            "money": self.money,
            "inventory": self.inventory.copy(),
            "experience": self.experience,
            "level": self.level,
            "current_outfit": self.current_outfit,
            "current_tool": self.current_tool,
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

            # 載入金錢
            if "money" in save_data:
                self.money = save_data["money"]

            # 載入背包
            if "inventory" in save_data:
                self.inventory = save_data["inventory"].copy()

            # 載入經驗值和等級
            if "experience" in save_data:
                self.experience = save_data["experience"]
            if "level" in save_data:
                self.level = save_data["level"]

            # 載入服裝和工具
            if "current_outfit" in save_data:
                self.current_outfit = save_data["current_outfit"]
            if "current_tool" in save_data:
                self.current_tool = save_data["current_tool"]

            print("玩家存檔資料載入成功")

        except Exception as e:
            print(f"載入玩家存檔資料失敗: {e}")

    def _add_initial_items(self):
        """
        添加初始物品供測試\n
        """
        # 添加一些測試物品
        self.add_item("小魚", 3)
        self.add_item("鯉魚", 1)
        self.add_item("兔肉", 2)
        self.add_item("工具", 1)
        print("已添加初始測試物品")
