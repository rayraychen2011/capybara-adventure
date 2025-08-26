######################NPC 系統模組初始化######################
"""
NPC (非玩家角色) 系統\n
\n
此模組負責管理遊戲中的所有 NPC，包括：\n
- 330 個小鎮居民 (各種職業)\n
- 100 個森林部落成員\n
- 職業分配和工作排程\n
- 電力系統區域管理 (30個區域，30個電力工人)\n
- NPC 生活軌跡和行為 AI\n
- 受傷住院機制\n
"""

from .npc import NPC, NPCState
from .profession import Profession, ProfessionData
from .npc_manager import NPCManager

__all__ = ["NPC", "NPCState", "Profession", "ProfessionData", "NPCManager"]
