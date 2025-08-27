######################載入套件######################
import pygame
import math
from config.settings import *
from src.utils.helpers import clamp, fast_movement_calculate


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

    def __init__(self, x=PLAYER_START_X, y=PLAYER_START_Y):
        """
        初始化玩家角色\n
        \n
        設定角色的初始位置、外觀、屬性和狀態\n
        建立物品欄系統和各種遊戲數據\n
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
        self.is_injured = False  # 玩家是否處於受傷狀態
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

        # 物品欄系統（取代原背包系統）
        self.item_slots = [
            None
        ] * ITEM_BAR_SLOTS  # 10格物品欄，每格存放 {"name": str, "count": int}
        self.selected_slot = 0  # 當前選中的格子

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

        # 更新狀態效果（較低優先級）
        if self.status_effects:  # 只有在有狀態效果時才更新
            self._update_status_effects(dt)

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

    def _update_movement(self, dt):
        """
        更新角色移動邏輯 - 已優化效能\n
        \n
        根據當前方向和速度計算新位置\n
        使用快速的移動計算避免不必要的正規化\n
        優化常見移動情況的計算速度\n
        \n
        參數:\n
        dt (float): 時間間隔，用於幀率無關的移動計算\n
        """
        # 如果沒有移動方向，就不需要移動
        if self.direction_x == 0 and self.direction_y == 0:
            return

        # 根據是否在載具中調整速度
        current_speed = VEHICLE_SPEED if self.in_vehicle else self.speed

        # 使用優化的移動計算 - 避免不必要的平方根計算
        # 針對常見的8方向移動進行快速計算
        if self.direction_x == 0 or self.direction_y == 0:
            # 單軸移動（上下左右）- 最快的情況
            move_x = self.direction_x * current_speed * dt * 60
            move_y = self.direction_y * current_speed * dt * 60
        else:
            # 斜向移動 - 使用預計算的係數避免平方根運算
            diagonal_speed = current_speed * 0.7071067811865476  # 1/√2
            move_x = self.direction_x * diagonal_speed * dt * 60
            move_y = self.direction_y * diagonal_speed * dt * 60

        # 計算新位置（使用整數運算提升效能）
        self.x += move_x
        self.y += move_y

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
    def add_item(self, item_name, quantity=1):
        """
        將物品加入物品欄\n
        \n
        檢查是否有空格子或相同物品的格子\n
        如果有相同物品則增加數量，否則佔用新格子\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 要添加的數量，預設為 1\n
        \n
        回傳:\n
        bool: True 表示成功添加，False 表示物品欄已滿\n
        """
        # 先檢查是否有相同物品的格子
        for i, slot in enumerate(self.item_slots):
            if slot and slot["name"] == item_name:
                slot["count"] += quantity
                print(f"添加物品到格子 {i+1}: {item_name} x{quantity}")
                return True

        # 找空格子
        for i, slot in enumerate(self.item_slots):
            if slot is None:
                self.item_slots[i] = {"name": item_name, "count": quantity}
                print(f"新物品放入格子 {i+1}: {item_name} x{quantity}")
                return True

        print(f"物品欄已滿，無法添加 {item_name}")
        return False

    def remove_item(self, item_name, quantity=1):
        """
        從物品欄移除物品\n
        \n
        檢查物品數量並移除指定數量\n
        如果數量歸零則清空格子\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 要移除的數量，預設為 1\n
        \n
        回傳:\n
        bool: True 表示成功移除，False 表示物品不足\n
        """
        for i, slot in enumerate(self.item_slots):
            if slot and slot["name"] == item_name:
                if slot["count"] >= quantity:
                    slot["count"] -= quantity
                    if slot["count"] == 0:
                        self.item_slots[i] = None
                        print(f"格子 {i+1} 已清空")
                    else:
                        print(f"從格子 {i+1} 移除 {item_name} x{quantity}")
                    return True
                else:
                    print(
                        f"{item_name} 數量不足，現有 {slot['count']}，需要 {quantity}"
                    )
                    return False

        print(f"物品欄中沒有 {item_name}")
        return False

    def has_item(self, item_name, quantity=1):
        """
        檢查物品欄是否有指定物品\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        quantity (int): 需要的數量，預設為 1\n
        \n
        回傳:\n
        bool: True 表示有足夠物品，False 表示物品不足\n
        """
        total_count = 0
        for slot in self.item_slots:
            if slot and slot["name"] == item_name:
                total_count += slot["count"]
        return total_count >= quantity

    def get_item_count(self, item_name):
        """
        獲取物品欄中指定物品的總數量\n
        \n
        參數:\n
        item_name (str): 物品名稱\n
        \n
        回傳:\n
        int: 物品數量，如果沒有則回傳 0\n
        """
        total_count = 0
        for slot in self.item_slots:
            if slot and slot["name"] == item_name:
                total_count += slot["count"]
        return total_count

    def get_item_slots(self):
        """
        獲取物品欄狀態\n
        \n
        回傳:\n
        list: 包含所有格子狀態的列表\n
        """
        return self.item_slots.copy()

    def select_slot(self, slot_index):
        """
        選擇物品欄格子\n
        \n
        參數:\n
        slot_index (int): 格子索引（0-9）\n
        """
        if 0 <= slot_index < ITEM_BAR_SLOTS:
            self.selected_slot = slot_index

    def get_selected_item(self):
        """
        獲取當前選中格子的物品\n
        \n
        回傳:\n
        dict: 物品資訊 {"name": str, "count": int}，如果格子為空則回傳 None\n
        """
        return self.item_slots[self.selected_slot]

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
        if self.is_injured:
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

    def draw_item_bar(self, screen):
        """
        繪製畫面底下的物品欄\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        # 計算物品欄位置（畫面底下中央）
        bar_width = (
            ITEM_BAR_SLOTS * (ITEM_BAR_SLOT_SIZE + ITEM_BAR_PADDING) - ITEM_BAR_PADDING
        )
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - ITEM_BAR_HEIGHT - 10

        # 繪製物品欄背景
        background_rect = pygame.Rect(
            bar_x - 10, bar_y - 10, bar_width + 20, ITEM_BAR_HEIGHT + 20
        )
        pygame.draw.rect(screen, (50, 50, 50, 200), background_rect)
        pygame.draw.rect(screen, (200, 200, 200), background_rect, 2)

        # 繪製每個格子
        for i in range(ITEM_BAR_SLOTS):
            slot_x = bar_x + i * (ITEM_BAR_SLOT_SIZE + ITEM_BAR_PADDING)
            slot_y = bar_y
            slot_rect = pygame.Rect(
                slot_x, slot_y, ITEM_BAR_SLOT_SIZE, ITEM_BAR_SLOT_SIZE
            )

            # 格子背景顏色
            if i == self.selected_slot:
                # 選中的格子用亮色
                pygame.draw.rect(screen, (100, 150, 100), slot_rect)
            else:
                # 普通格子用暗色
                pygame.draw.rect(screen, (80, 80, 80), slot_rect)

            # 格子邊框
            pygame.draw.rect(screen, (200, 200, 200), slot_rect, 2)

            # 繪製物品（如果有的話）
            slot = self.item_slots[i]
            if slot:
                # 物品顏色（簡單的顏色映射）
                item_color = self._get_item_color(slot["name"])
                item_rect = pygame.Rect(
                    slot_x + 5,
                    slot_y + 5,
                    ITEM_BAR_SLOT_SIZE - 10,
                    ITEM_BAR_SLOT_SIZE - 10,
                )
                pygame.draw.rect(screen, item_color, item_rect)

                # 繪製物品數量
                if slot["count"] > 1:
                    font = pygame.font.Font(None, 20)
                    count_text = font.render(str(slot["count"]), True, (255, 255, 255))
                    screen.blit(
                        count_text,
                        (
                            slot_x + ITEM_BAR_SLOT_SIZE - 15,
                            slot_y + ITEM_BAR_SLOT_SIZE - 15,
                        ),
                    )

            # 繪製格子編號
            font = pygame.font.Font(None, 16)
            number_text = font.render(str(i + 1), True, (255, 255, 255))
            screen.blit(number_text, (slot_x + 2, slot_y + 2))

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
            "item_slots": self.item_slots.copy(),
            "selected_slot": self.selected_slot,
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

            # 載入物品欄
            if "item_slots" in save_data:
                self.item_slots = save_data["item_slots"].copy()
            if "selected_slot" in save_data:
                self.selected_slot = save_data["selected_slot"]

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
