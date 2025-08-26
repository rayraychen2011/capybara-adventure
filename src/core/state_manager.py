######################載入套件######################
from enum import Enum

######################遊戲狀態定義######################
class GameState(Enum):
    """
    遊戲狀態列舉 - 定義遊戲的各種運行狀態\n
    \n
    使用狀態機模式管理遊戲的不同階段\n
    每個狀態代表遊戲的一種運行模式，控制遊戲的行為和畫面顯示\n
    \n
    狀態說明:\n
    - MENU: 主選單畫面，玩家可以開始新遊戲或載入存檔\n
    - PLAYING: 正常遊戲進行中，玩家可以自由活動和互動\n
    - PAUSED: 遊戲暫停狀態，暫停所有遊戲邏輯但保持畫面\n
    - INVENTORY: 背包管理畫面，玩家查看和管理物品\n
    - SHOPPING: 商店購物介面，與 NPC 進行交易\n
    - FISHING: 釣魚小遊戲進行中，特殊的互動模式\n
    - HUNTING: 狩獵模式，使用槍械狩獵動物\n
    - DRIVING: 駕駛載具中，改變移動方式和速度\n
    - QUIT: 準備退出遊戲，進行清理工作\n
    """
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    SHOPPING = "shopping"
    FISHING = "fishing"
    HUNTING = "hunting"
    DRIVING = "driving"
    QUIT = "quit"

######################狀態管理器######################
class StateManager:
    """
    遊戲狀態管理器 - 控制遊戲狀態的切換和維護\n
    \n
    負責管理遊戲的當前狀態和狀態歷史\n
    提供安全的狀態切換機制，支援狀態回退功能\n
    確保遊戲在不同狀態間平滑過渡\n
    """
    
    def __init__(self):
        """
        初始化狀態管理器\n
        \n
        設定初始狀態為主選單，並建立狀態歷史紀錄\n
        狀態歷史用於實現「返回上一個狀態」的功能\n
        """
        # 目前的遊戲狀態，預設從主選單開始
        self.current_state = GameState.MENU
        
        # 前一個狀態，用於返回功能
        self.previous_state = None
        
        # 狀態歷史紀錄，最多保留 10 個狀態
        self.state_history = []
        
        # 狀態切換時的回調函數字典
        self.state_change_callbacks = {}
    
    def change_state(self, new_state):
        """
        切換到新的遊戲狀態\n
        \n
        安全地切換遊戲狀態，記錄狀態歷史\n
        觸發狀態變更事件，讓其他系統能夠響應狀態改變\n
        \n
        參數:\n
        new_state (GameState): 要切換到的新狀態\n
        \n
        功能:\n
        1. 記錄當前狀態到歷史中\n
        2. 更新當前和前一個狀態\n
        3. 觸發狀態變更回調函數\n
        4. 輸出狀態變更日誌\n
        """
        # 如果新狀態和目前狀態相同，就不需要切換
        if new_state == self.current_state:
            return
        
        # 把目前狀態記錄為前一個狀態
        self.previous_state = self.current_state
        
        # 把目前狀態加入歷史紀錄
        self.state_history.append(self.current_state)
        
        # 限制歷史紀錄的長度，避免記憶體浪費
        if len(self.state_history) > 10:
            self.state_history.pop(0)  # 移除最舊的紀錄
        
        # 切換到新狀態
        old_state = self.current_state
        self.current_state = new_state
        
        # 輸出狀態變更的日誌
        print(f"遊戲狀態切換: {old_state.value} -> {new_state.value}")
        
        # 觸發狀態變更的回調函數
        self._trigger_state_change_callback(old_state, new_state)
    
    def go_back(self):
        """
        返回到前一個狀態\n
        \n
        如果有前一個狀態的紀錄，就返回到那個狀態\n
        常用於取消操作、關閉選單、退出子系統等情況\n
        \n
        回傳:\n
        bool: True 表示成功返回，False 表示沒有可返回的狀態\n
        """
        if self.previous_state is not None:
            # 暫存當前狀態
            temp_current = self.current_state
            
            # 切換回前一個狀態
            self.current_state = self.previous_state
            self.previous_state = None
            
            print(f"返回前一個狀態: {temp_current.value} -> {self.current_state.value}")
            return True
        else:
            print("沒有可返回的狀態")
            return False
    
    def is_state(self, state):
        """
        檢查當前是否為指定狀態\n
        \n
        提供便利的狀態檢查方法，讓其他系統能夠根據狀態決定行為\n
        \n
        參數:\n
        state (GameState): 要檢查的狀態\n
        \n
        回傳:\n
        bool: True 表示當前狀態符合，False 表示不符合\n
        """
        return self.current_state == state
    
    def get_state_name(self):
        """
        獲取當前狀態的名稱\n
        \n
        回傳當前狀態的字串名稱，用於顯示或記錄\n
        \n
        回傳:\n
        str: 當前狀態的名稱\n
        """
        return self.current_state.value
    
    def register_state_change_callback(self, callback_name, callback_function):
        """
        註冊狀態變更回調函數\n
        \n
        讓其他系統能夠在狀態改變時收到通知\n
        例如 UI 系統可以在狀態改變時更新介面\n
        \n
        參數:\n
        callback_name (str): 回調函數的識別名稱\n
        callback_function (function): 回調函數，接收 (old_state, new_state) 參數\n
        """
        self.state_change_callbacks[callback_name] = callback_function
        print(f"註冊狀態變更回調: {callback_name}")
    
    def unregister_state_change_callback(self, callback_name):
        """
        取消註冊狀態變更回調函數\n
        \n
        移除不再需要的回調函數，避免記憶體洩漏\n
        \n
        參數:\n
        callback_name (str): 要移除的回調函數名稱\n
        \n
        回傳:\n
        bool: True 表示成功移除，False 表示回調函數不存在\n
        """
        if callback_name in self.state_change_callbacks:
            del self.state_change_callbacks[callback_name]
            print(f"取消註冊狀態變更回調: {callback_name}")
            return True
        else:
            print(f"回調函數不存在: {callback_name}")
            return False
    
    def _trigger_state_change_callback(self, old_state, new_state):
        """
        觸發所有已註冊的狀態變更回調函數\n
        \n
        這是內部方法，在狀態切換時自動調用\n
        依序執行所有註冊的回調函數，並處理可能的錯誤\n
        \n
        參數:\n
        old_state (GameState): 切換前的狀態\n
        new_state (GameState): 切換後的狀態\n
        """
        for callback_name, callback_function in self.state_change_callbacks.items():
            try:
                # 執行回調函數
                callback_function(old_state, new_state)
            except Exception as e:
                # 如果回調函數發生錯誤，記錄但不影響遊戲繼續
                print(f"狀態變更回調函數錯誤 ({callback_name}): {e}")
    
    def can_transition_to(self, target_state):
        """
        檢查是否可以切換到指定狀態\n
        \n
        實現狀態切換的邏輯限制，防止無效的狀態轉換\n
        例如只有在 PLAYING 狀態才能進入 FISHING 狀態\n
        \n
        參數:\n
        target_state (GameState): 目標狀態\n
        \n
        回傳:\n
        bool: True 表示可以切換，False 表示不允許切換\n
        """
        current = self.current_state
        
        # 定義狀態轉換規則
        transition_rules = {
            GameState.MENU: [GameState.PLAYING, GameState.QUIT],
            GameState.PLAYING: [GameState.PAUSED, GameState.INVENTORY, GameState.FISHING, 
                              GameState.HUNTING, GameState.DRIVING, GameState.SHOPPING, GameState.MENU],
            GameState.PAUSED: [GameState.PLAYING, GameState.MENU],
            GameState.INVENTORY: [GameState.PLAYING],
            GameState.SHOPPING: [GameState.PLAYING],
            GameState.FISHING: [GameState.PLAYING],
            GameState.HUNTING: [GameState.PLAYING],
            GameState.DRIVING: [GameState.PLAYING],
            GameState.QUIT: []  # 退出狀態不能轉換到其他狀態
        }
        
        # 檢查是否允許這個狀態轉換
        allowed_states = transition_rules.get(current, [])
        return target_state in allowed_states