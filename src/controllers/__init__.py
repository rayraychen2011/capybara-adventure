######################控制器模組初始化######################
"""
控制器模組 - 系統協調和管理\n
\n
此模組包含遊戲的各種控制器，負責協調不同系統間的運作，\n
降低系統間的直接耦合，提供統一的管理介面。\n
\n
控制器類型：\n
- WorldController: 世界系統協調器\n
- InteractionController: 互動系統控制器\n
- UIController: UI 系統控制器\n
- InputController: 輸入系統控制器（已存在於 player 模組）\n
\n
設計原則：\n
- 中介者模式：控制器作為系統間的中介者\n
- 職責分離：每個控制器負責特定領域\n
- 事件驅動：通過事件系統進行通訊\n
- 效能監控：內建效能分析功能\n
"""

from .world_controller import WorldController

__all__ = [
    "WorldController"
]