"""
野生動物系統模組\n
\n
提供完整的野生動物管理功能，包含：\n
- 動物種類和屬性定義\n
- 動物行為 AI 系統\n
- 野生動物管理器\n
- 狩獵和釣魚機制\n
- 保育系統\n
"""

from .animal_data import AnimalType, AnimalData, ThreatLevel, BehaviorType
from .animal import Animal, AnimalState
from .wildlife_manager import WildlifeManager

__all__ = [
    "AnimalType",
    "AnimalData",
    "ThreatLevel",
    "BehaviorType",
    "Animal",
    "AnimalState",
    "WildlifeManager",
]
