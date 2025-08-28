######################載入套件######################
import pygame
from src.player.player import Player


######################輸入控制器######################
class InputController:
    """
    輸入控制器 - 處理玩家輸入並控制角色行為\n
    \n
    負責將鍵盤和滑鼠輸入轉換為遊戲中的角色動作\n
    支援多種輸入方式和可自訂的按鍵配置\n
    提供平滑的移動控制和即時響應\n
    """

    def __init__(self, player):
        """
        初始化輸入控制器\n
        \n
        設定按鍵映射和綁定玩家角色\n
        \n
        參數:\n
        player (Player): 要控制的玩家角色實例\n
        """
        self.player = player

        # 按鍵狀態追蹤
        self.keys_pressed = set()
        self.keys_just_pressed = set()  # 本幀剛按下的按鍵

        # 移動按鍵映射
        self.movement_keys = {
            # WASD 移動
            pygame.K_w: (0, -1),  # 上
            pygame.K_s: (0, 1),  # 下
            pygame.K_a: (-1, 0),  # 左
            pygame.K_d: (1, 0),  # 右
            # 方向鍵移動
            pygame.K_UP: (0, -1),  # 上
            pygame.K_DOWN: (0, 1),  # 下
            pygame.K_LEFT: (-1, 0),  # 左
            pygame.K_RIGHT: (1, 0),  # 右
        }

        # 功能按鍵映射
        self.action_keys = {
            pygame.K_SPACE: "interact",  # 互動
            pygame.K_e: "equipment_wheel",  # 裝備圓盤（修改）
            pygame.K_q: "chop_tree",     # 砍伐樹木（新增）
            pygame.K_c: "talk",          # 對話（新增）
            pygame.K_i: "inventory",  # 背包
            pygame.K_TAB: "inventory",  # 背包（備用）
            pygame.K_m: "map",  # 地圖
            pygame.K_RETURN: "confirm",  # 確認
            pygame.K_BACKSPACE: "cancel",  # 取消
            pygame.K_f: "fishing",  # 釣魚
            pygame.K_g: "hunting",  # 狩獵
            pygame.K_v: "vehicle",  # 載具
            pygame.K_LSHIFT: "run",  # 跑步（預留）
            # 裝備選擇快捷鍵（新增）
            pygame.K_1: "equip_1",  # 槍
            pygame.K_2: "equip_2",  # 釣竿
            pygame.K_3: "equip_3",  # 小刀
            pygame.K_4: "equip_4",  # 車鑰匙
            pygame.K_5: "equip_5",  # 手電筒
        }

        # 滑鼠按鍵映射
        self.mouse_action_keys = {
            1: "left_click",    # 左鍵點擊
            2: "middle_click",  # 中鍵點擊 - 開啟小地圖
            3: "right_click",   # 右鍵點擊
        }

        # 當前移動向量
        self.movement_vector = [0, 0]

        print("輸入控制器已初始化")

    def handle_event(self, event):
        """
        處理單個輸入事件\n
        \n
        處理按鍵按下和釋放事件以及滑鼠事件\n
        觸發對應的遊戲動作\n
        \n
        參數:\n
        event (pygame.event.Event): Pygame 事件物件\n
        \n
        回傳:\n
        str: 觸發的動作名稱，如果沒有動作則回傳 None\n
        """
        action_triggered = None

        if event.type == pygame.KEYDOWN:
            # 按鍵按下
            self.keys_pressed.add(event.key)
            self.keys_just_pressed.add(event.key)  # 標記為剛按下

            # 檢查是否為功能按鍵
            if event.key in self.action_keys:
                action_triggered = self.action_keys[event.key]
                print(f"觸發動作: {action_triggered}")

            # 只有移動鍵才需要更新移動向量
            if event.key in self.movement_keys:
                self._update_movement()

        elif event.type == pygame.KEYUP:
            # 按鍵釋放
            if event.key in self.keys_pressed:
                self.keys_pressed.remove(event.key)

            # 只有移動鍵才需要更新移動向量
            if event.key in self.movement_keys:
                self._update_movement()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 滑鼠按鍵按下
            if event.button in self.mouse_action_keys:
                action_triggered = self.mouse_action_keys[event.button]
                print(f"觸發滑鼠動作: {action_triggered}")

        elif event.type == pygame.MOUSEWHEEL:
            # 滑鼠滾輪事件
            if event.y > 0:
                action_triggered = "scroll_up"
            elif event.y < 0:
                action_triggered = "scroll_down"

        return action_triggered

    def _update_movement(self):
        """
        更新移動向量\n
        \n
        根據當前按下的移動按鍵計算移動方向\n
        支援同時按下多個方向鍵的組合移動\n
        """
        # 重置移動向量
        self.movement_vector = [0, 0]

        # 遍歷所有按下的按鍵
        for key in self.keys_pressed:
            if key in self.movement_keys:
                # 累加移動向量
                dx, dy = self.movement_keys[key]
                self.movement_vector[0] += dx
                self.movement_vector[1] += dy

        # 設定玩家移動方向
        self.player.set_movement_direction(
            self.movement_vector[0], self.movement_vector[1]
        )

    def update(self, dt):
        """
        更新輸入控制器狀態 - 超高響應版本，支援奔跑功能\n
        \n
        每幀調用一次，使用最快速的按鍵檢測實現最低延遲控制\n
        目標延遲：不超過 0.03 秒 (約2幀的時間)\n
        支援 Shift 鍵奔跑功能\n
        \n
        參數:\n
        dt (float): 與上一幀的時間差，單位為秒\n
        """
        # 使用 Pygame 最快的按鍵檢測方法
        current_keys = pygame.key.get_pressed()

        # 檢查奔跑狀態（Shift 鍵）
        if current_keys[pygame.K_LSHIFT] or current_keys[pygame.K_RSHIFT]:
            self.player.start_running()
        else:
            self.player.stop_running()

        # 立即計算新的移動向量（零延遲處理）
        new_movement = [0, 0]

        # 垂直移動檢測 - 直接檢查最常用的按鍵
        if current_keys[pygame.K_w] or current_keys[pygame.K_UP]:
            new_movement[1] = -1
        if current_keys[pygame.K_s] or current_keys[pygame.K_DOWN]:
            new_movement[1] += 1

        # 水平移動檢測
        if current_keys[pygame.K_a] or current_keys[pygame.K_LEFT]:
            new_movement[0] = -1
        if current_keys[pygame.K_d] or current_keys[pygame.K_RIGHT]:
            new_movement[0] += 1

        # 調試輸出：檢查按鍵檢測
        if hasattr(self, '_debug_counter'):
            self._debug_counter += 1
        else:
            self._debug_counter = 0
        
        # 只有當有移動輸入時才輸出調試信息（頻率降低）
        if (new_movement[0] != 0 or new_movement[1] != 0) and self._debug_counter % 120 == 0:
            pressed_keys = []
            if current_keys[pygame.K_w]: pressed_keys.append("W")
            if current_keys[pygame.K_a]: pressed_keys.append("A")
            if current_keys[pygame.K_s]: pressed_keys.append("S")
            if current_keys[pygame.K_d]: pressed_keys.append("D")
            print(f"輸入控制器調試 - 按鍵: {', '.join(pressed_keys)}, 移動向量: {new_movement}")

        # 立即更新玩家移動（移除所有不必要的檢查）
        self.movement_vector = new_movement
        self.player.set_movement_direction(
            self.movement_vector[0], self.movement_vector[1]
        )

        # 清除本幀剛按下的按鍵記錄
        self.keys_just_pressed.clear()

    def _handle_continuous_actions(self, dt):
        """
        處理持續性動作\n
        \n
        處理需要長按才生效的動作\n
        例如跑步、蹲下等狀態性動作\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        # 檢查跑步按鍵
        if pygame.K_LSHIFT in self.keys_pressed:
            # 跑步狀態 - 目前暫時不實作
            pass

        # 檢查蹲下按鍵
        if pygame.K_c in self.keys_pressed:
            # 蹲下狀態 - 目前暫時不實作
            pass

    def is_key_pressed(self, key):
        """
        檢查指定按鍵是否正在被按住\n
        \n
        參數:\n
        key (int): Pygame 按鍵常數\n
        \n
        回傳:\n
        bool: True 表示按鍵正在被按住，False 表示沒有\n
        """
        return key in self.keys_pressed

    def is_action_key_pressed(self, action):
        """
        檢查指定動作的按鍵是否正在被按住\n
        \n
        參數:\n
        action (str): 動作名稱\n
        \n
        回傳:\n
        bool: True 表示動作按鍵正在被按住，False 表示沒有\n
        """
        for key, mapped_action in self.action_keys.items():
            if mapped_action == action and key in self.keys_pressed:
                return True
        return False

    def is_action_key_just_pressed(self, action):
        """
        檢查指定動作的按鍵是否剛剛被按下（本幀）\n
        \n
        參數:\n
        action (str): 動作名稱\n
        \n
        回傳:\n
        bool: True 表示動作按鍵剛剛被按下，False 表示沒有\n
        """
        for key, mapped_action in self.action_keys.items():
            if mapped_action == action and key in self.keys_just_pressed:
                return True
        return False

    def is_moving(self):
        """
        檢查玩家是否正在移動\n
        \n
        回傳:\n
        bool: True 表示有移動輸入，False 表示沒有\n
        """
        return self.movement_vector[0] != 0 or self.movement_vector[1] != 0

    def get_movement_vector(self):
        """
        獲取當前移動向量\n
        \n
        回傳:\n
        tuple: (x, y) 移動方向向量\n
        """
        return tuple(self.movement_vector)

    def stop_all_input(self):
        """
        停止所有輸入\n
        \n
        清除所有按鍵狀態，讓角色停止移動\n
        用於場景切換或特殊狀態時暫停玩家控制\n
        """
        self.keys_pressed.clear()
        self.movement_vector = [0, 0]
        self.player.stop_movement()
        print("所有輸入已停止")

    def set_key_mapping(self, key, action):
        """
        自訂按鍵映射\n
        \n
        允許玩家自訂按鍵配置\n
        \n
        參數:\n
        key (int): Pygame 按鍵常數\n
        action (str): 要映射的動作名稱\n
        """
        if action in ["up", "down", "left", "right"]:
            # 移動按鍵映射
            direction_map = {
                "up": (0, -1),
                "down": (0, 1),
                "left": (-1, 0),
                "right": (1, 0),
            }
            self.movement_keys[key] = direction_map[action]
        else:
            # 功能按鍵映射
            self.action_keys[key] = action

        print(f"按鍵映射已更新: {pygame.key.name(key)} -> {action}")

    def get_key_name(self, key):
        """
        獲取按鍵的名稱\n
        \n
        參數:\n
        key (int): Pygame 按鍵常數\n
        \n
        回傳:\n
        str: 按鍵名稱\n
        """
        return pygame.key.name(key)

    def get_current_mappings(self):
        """
        獲取當前的按鍵映射配置\n
        \n
        回傳:\n
        dict: 包含移動和功能按鍵映射的字典\n
        """
        return {
            "movement": self.movement_keys.copy(),
            "actions": self.action_keys.copy(),
        }

    def reset_to_default(self):
        """
        重置按鍵映射為預設配置\n
        \n
        恢復所有按鍵為初始設定\n
        """
        self.__init__(self.player)
        print("按鍵映射已重置為預設配置")


######################滑鼠控制器######################
class MouseController:
    """
    滑鼠控制器 - 處理滑鼠輸入和游標互動\n
    \n
    處理滑鼠點擊、移動、滾輪等輸入\n
    提供游標位置追蹤和點擊檢測功能\n
    """

    def __init__(self):
        """
        初始化滑鼠控制器\n
        """
        # 滑鼠位置
        self.mouse_x = 0
        self.mouse_y = 0

        # 滑鼠按鍵狀態
        self.left_button_pressed = False
        self.right_button_pressed = False
        self.middle_button_pressed = False

        print("滑鼠控制器已初始化")

    def handle_event(self, event):
        """
        處理滑鼠事件\n
        \n
        參數:\n
        event (pygame.event.Event): Pygame 事件物件\n
        \n
        回傳:\n
        str: 觸發的動作名稱，如果沒有動作則回傳 None\n
        """
        action_triggered = None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵
                self.left_button_pressed = True
                action_triggered = "left_click"
            elif event.button == 2:  # 中鍵
                self.middle_button_pressed = True
                action_triggered = "middle_click"
            elif event.button == 3:  # 右鍵
                self.right_button_pressed = True
                action_triggered = "right_click"

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左鍵
                self.left_button_pressed = False
            elif event.button == 2:  # 中鍵
                self.middle_button_pressed = False
            elif event.button == 3:  # 右鍵
                self.right_button_pressed = False

        elif event.type == pygame.MOUSEMOTION:
            self.mouse_x, self.mouse_y = event.pos
            action_triggered = "mouse_move"

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                action_triggered = "scroll_up"
            elif event.y < 0:
                action_triggered = "scroll_down"

        return action_triggered

    def get_mouse_position(self):
        """
        獲取滑鼠位置\n
        \n
        回傳:\n
        tuple: (x, y) 滑鼠座標\n
        """
        return (self.mouse_x, self.mouse_y)

    def is_left_button_pressed(self):
        """
        檢查左鍵是否被按住\n
        \n
        回傳:\n
        bool: True 表示左鍵被按住\n
        """
        return self.left_button_pressed

    def is_right_button_pressed(self):
        """
        檢查右鍵是否被按住\n
        \n
        回傳:\n
        bool: True 表示右鍵被按住\n
        """
        return self.right_button_pressed
