######################載入套件######################
import pygame
from config.settings import *


######################場景基底類別######################
class Scene:
    """
    場景基底類別 - 所有遊戲場景的共同基礎\n
    \n
    定義場景的基本結構和必須實作的方法\n
    每個具體場景都要繼承此類別並實作相關方法\n
    提供場景間切換的標準介面\n
    """

    def __init__(self, scene_name):
        """
        初始化場景基本屬性\n
        \n
        參數:\n
        scene_name (str): 場景名稱，用於識別和除錯\n
        """
        self.name = scene_name
        self.is_active = False
        self.transition_target = None  # 要切換到的目標場景

    def enter(self):
        """
        進入場景時的初始化作業\n
        \n
        當場景變為活躍狀態時調用\n
        子類別應該覆寫此方法來實作場景特定的初始化\n
        """
        self.is_active = True
        print(f"進入場景: {self.name}")

    def exit(self):
        """
        離開場景時的清理作業\n
        \n
        當場景變為非活躍狀態時調用\n
        子類別應該覆寫此方法來實作場景特定的清理\n
        """
        self.is_active = False
        print(f"離開場景: {self.name}")

    def update(self, dt):
        """
        更新場景邏輯\n
        \n
        每幀調用一次，用於更新場景的遊戲邏輯\n
        子類別必須實作此方法\n
        \n
        參數:\n
        dt (float): 與上一幀的時間差，單位為秒\n
        """
        raise NotImplementedError("子類別必須實作 update 方法")

    def draw(self, screen):
        """
        繪製場景畫面\n
        \n
        每幀調用一次，用於繪製場景的視覺內容\n
        子類別必須實作此方法\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        raise NotImplementedError("子類別必須實作 draw 方法")

    def handle_event(self, event):
        """
        處理輸入事件\n
        \n
        處理玩家的鍵盤、滑鼠等輸入\n
        子類別可以覆寫此方法來實作場景特定的輸入處理\n
        \n
        參數:\n
        event (pygame.event.Event): Pygame 事件物件\n
        \n
        回傳:\n
        bool: True 表示事件已處理，False 表示事件未處理\n
        """
        return False

    def request_scene_change(self, target_scene):
        """
        請求切換到其他場景\n
        \n
        場景可以透過此方法請求切換到其他場景\n
        實際的切換動作由場景管理器執行\n
        \n
        參數:\n
        target_scene (str): 目標場景的名稱\n
        """
        self.transition_target = target_scene
        print(f"場景 {self.name} 請求切換到 {target_scene}")


######################場景管理器######################
class SceneManager:
    """
    場景管理器 - 負責管理所有遊戲場景的切換和更新\n
    \n
    統一管理遊戲中的所有場景，提供場景註冊、切換、更新等功能\n
    確保在任何時候都只有一個場景處於活躍狀態\n
    處理場景間的平滑切換和資源管理\n
    """

    def __init__(self):
        """
        初始化場景管理器\n
        \n
        建立場景字典和設定初始狀態\n
        """
        # 儲存所有已註冊場景的字典
        self.scenes = {}

        # 目前活躍的場景
        self.current_scene = None

        # 前一個場景的名稱，用於設定入口位置
        self.previous_scene_name = None

        # 正在切換中的目標場景
        self.pending_scene_change = None

        # 場景切換是否正在進行
        self.transitioning = False

    def register_scene(self, scene_name, scene_instance):
        """
        註冊一個新場景到管理器中\n
        \n
        將場景實例加入管理器，讓它可以被切換和管理\n
        \n
        參數:\n
        scene_name (str): 場景的唯一識別名稱\n
        scene_instance (Scene): 場景的實例物件\n
        """
        if scene_name in self.scenes:
            print(f"警告: 場景 '{scene_name}' 已存在，將被覆蓋")

        self.scenes[scene_name] = scene_instance
        print(f"註冊場景: {scene_name}")

    def change_scene(self, scene_name):
        """
        切換到指定的場景\n
        \n
        安全地從當前場景切換到新場景\n
        處理場景的進入和離開邏輯\n
        \n
        參數:\n
        scene_name (str): 要切換到的場景名稱\n
        \n
        回傳:\n
        bool: True 表示切換成功，False 表示場景不存在\n
        """
        # 檢查目標場景是否存在
        if scene_name not in self.scenes:
            print(f"錯誤: 場景 '{scene_name}' 不存在")
            return False

        # 如果目標場景就是當前場景，不需要切換
        if self.current_scene and self.current_scene.name == scene_name:
            print(f"已經在場景 '{scene_name}' 中")
            return True

        # 記錄前一個場景的名稱
        if self.current_scene:
            self.previous_scene_name = self.current_scene.name
            self.current_scene.exit()
        else:
            self.previous_scene_name = None

        # 切換到新場景
        self.current_scene = self.scenes[scene_name]

        # 傳遞前一個場景信息給支援的場景
        if hasattr(self.current_scene, "set_entry_from_scene"):
            self.current_scene.set_entry_from_scene(self.previous_scene_name)

        self.current_scene.enter()

        print(f"場景切換完成: -> {scene_name}")
        return True

    def update(self, dt):
        """
        更新當前場景\n
        \n
        每幀調用一次，更新當前活躍場景的邏輯\n
        同時檢查是否有場景切換請求\n
        \n
        參數:\n
        dt (float): 與上一幀的時間差，單位為秒\n
        """
        # 如果有當前場景，就更新它
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.update(dt)

            # 檢查場景是否請求切換
            if self.current_scene.transition_target:
                target = self.current_scene.transition_target
                self.current_scene.transition_target = None  # 清除請求
                self.change_scene(target)

    def draw(self, screen):
        """
        繪製當前場景\n
        \n
        每幀調用一次，繪製當前活躍場景的畫面\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.draw(screen)

    def handle_event(self, event):
        """
        將事件傳遞給當前場景處理\n
        \n
        讓當前場景有機會處理玩家輸入\n
        \n
        參數:\n
        event (pygame.event.Event): Pygame 事件物件\n
        \n
        回傳:\n
        bool: True 表示事件已被處理，False 表示事件未被處理\n
        """
        if self.current_scene and self.current_scene.is_active:
            return self.current_scene.handle_event(event)
        return False

    def get_current_scene_name(self):
        """
        獲取當前場景的名稱\n
        \n
        回傳:\n
        str: 當前場景名稱，如果沒有當前場景則回傳 None\n
        """
        if self.current_scene:
            return self.current_scene.name
        return None

    def has_scene(self, scene_name):
        """
        檢查是否已註冊指定場景\n
        \n
        參數:\n
        scene_name (str): 要檢查的場景名稱\n
        \n
        回傳:\n
        bool: True 表示場景存在，False 表示場景不存在\n
        """
        return scene_name in self.scenes

    def get_scene_count(self):
        """
        獲取已註冊場景的數量\n
        \n
        回傳:\n
        int: 已註冊場景的總數\n
        """
        return len(self.scenes)

    def list_scenes(self):
        """
        列出所有已註冊的場景名稱\n
        \n
        回傳:\n
        list: 包含所有場景名稱的列表\n
        """
        return list(self.scenes.keys())

    def cleanup(self):
        """
        清理場景管理器\n
        \n
        遊戲結束時調用，確保所有場景都正確離開\n
        釋放相關資源\n
        """
        # 讓當前場景離開
        if self.current_scene:
            self.current_scene.exit()
            self.current_scene = None

        # 清空場景字典
        self.scenes.clear()
        print("場景管理器已清理")
