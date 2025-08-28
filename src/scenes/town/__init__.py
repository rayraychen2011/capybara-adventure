######################小鎮場景模組初始化######################
"""
小鎮場景模組 - 重構後的模組化系統\n
\n
此模組將原本龐大的 TownScene 拆分為多個專門的管理器：\n
\n
核心組件：\n
- TownScene: 主場景協調器\n
- TownCameraController: 攝影機控制\n
- TownUIManager: UI 管理\n
- TownInteractionHandler: 互動處理\n
\n
設計原則：\n
- 單一職責：每個類別只負責一個主要功能\n
- 低耦合：管理器間通過明確的介面通訊\n
- 可擴展：容易添加新功能而不影響現有代碼\n
"""

from .town_scene_refactored import TownScene
from .town_camera_controller import TownCameraController
from .town_ui_manager import TownUIManager
from .town_interaction_handler import TownInteractionHandler

__all__ = [
    "TownScene",
    "TownCameraController", 
    "TownUIManager",
    "TownInteractionHandler"
]