######################NPC 行為模組初始化######################
"""
NPC 行為系統模組\n
\n
此模組包含所有 NPC 行為的實作，將原本集中在 NPC 類別中的行為邏輯\n
拆分為專門的行為管理器，提升程式碼的可維護性和可擴展性。\n
\n
行為模組：\n
- MovementBehavior: 移動行為（路徑規劃、碰撞避免、移動動畫）\n
- WorkBehavior: 工作行為（工作時間、任務執行、職業特殊行為）\n
- SocialBehavior: 社交行為（對話、互動、群體行為）\n
- PathfindingBehavior: 路徑尋找（A*算法、道路系統整合）\n
\n
設計原則：\n
- 模組化：每個行為獨立管理\n
- 可組合：不同行為可以組合使用\n
- 可擴展：容易添加新的行為類型\n
- 低耦合：行為間通過明確介面通訊\n
"""

from .movement_behavior import NPCMovementBehavior
from .work_behavior import NPCWorkBehavior

__all__ = [
    "NPCMovementBehavior",
    "NPCWorkBehavior"
]