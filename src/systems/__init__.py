######################系統模組初始化######################
"""
遊戲系統模組\n
\n
此模組包含遊戲的各種系統實作：\n
- NPC 系統：非玩家角色管理\n
- 經濟系統：市場、商店、貨幣\n
- 環境系統：天氣、電力、建築\n
- 野生動物系統：動物、保育、狩獵\n
- 釣魚系統：魚類、釣魚機制\n
- 載具系統：車輛、道路\n
- 任務系統：任務管理\n
"""

# 導出主要類別供外部使用
from src.systems.npc.npc_manager import NPCManager
from src.systems.npc.npc import NPC
from src.systems.npc.profession import Profession, ProfessionData

__all__ = ["NPCManager", "NPC", "Profession", "ProfessionData"]
