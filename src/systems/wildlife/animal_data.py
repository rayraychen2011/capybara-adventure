######################載入套件######################
from enum import Enum
import random


######################動物類型列舉######################
class AnimalType(Enum):
    """
    動物類型列舉\n
    \n
    定義遊戲中所有的動物種類\n
    按稀有度分類：稀有（30元）、超稀有（50元）、傳奇（100元）\n
    """

    # 稀有動物（獵殺獲得 30 元）
    RABBIT = "兔子"        # 生活在草地和森林區域，體型小、行動迅速、容易被忽視
    TURTLE = "烏龜"        # 棲息在水邊和濕地，行動緩慢但防禦力強
    SHEEP = "羊"           # 出沒於農田和丘陵地帶，群居性強、容易被發現

    # 超稀有動物（獵殺獲得 50 元）
    MOUNTAIN_LION = "山獅"  # 棲息在山區和森林深處，行動敏捷且具攻擊性
    BLACK_PANTHER = "黑豹"  # 出沒於密林並於夜間活動，行動隱秘且危險

    # 傳奇動物（獵殺獲得 100 元）
    BEAR = "熊"           # 棲息於山區和森林，體型巨大且力量強大，具有高度攻擊性


######################動物稀有度等級######################
class RarityLevel(Enum):
    """
    動物稀有度等級\n
    \n
    定義動物的稀有程度，影響獵殺獎勵和生成機率\n
    """

    RARE = "稀有"          # 獵殺獲得 30 元
    SUPER_RARE = "超稀有"   # 獵殺獲得 50 元
    LEGENDARY = "傳奇"      # 獵殺獲得 100 元


######################動物行為類型######################
class BehaviorType(Enum):
    """
    動物行為類型\n
    \n
    定義動物的基本行為模式\n
    """

    PEACEFUL = "和平"  # 不會主動攻擊
    DEFENSIVE = "防禦性"  # 被攻擊時反擊
    TERRITORIAL = "領域性"  # 保護領域，主動警告


######################威脅等級######################
class ThreatLevel(Enum):
    """
    動物威脅等級\n
    \n
    定義動物對玩家的威脅程度\n
    """

    HARMLESS = "無害"     # 完全無害
    LOW = "低威脅"        # 低威脅
    MEDIUM = "中威脅"     # 中等威脅
    HIGH = "高威脅"       # 高威脅
    EXTREME = "極度威脅"  # 極度威脅
    AGGRESSIVE = "攻擊性"  # 主動攻擊入侵者
    PREDATOR = "掠食性"  # 主動獵食其他生物


######################動物資料管理######################
class AnimalData:
    """
    動物資料管理類別\n
    \n
    管理所有動物種類的屬性、行為和生態資訊\n
    提供動物創建和行為決策所需的資料\n
    """

    # 動物基本屬性資料
    ANIMAL_PROPERTIES = {
        # 稀有動物（30元）
        AnimalType.RABBIT: {
            "size": 8,
            "speed": 4.0,
            "health": 50,
            "rarity": RarityLevel.RARE,
            "behavior": BehaviorType.PEACEFUL,
            "threat_level": ThreatLevel.HARMLESS,
            "color": (139, 69, 19),  # 棕色
            "habitat": ["草地", "森林"],
            "drop_items": ["兔肉", "兔毛"],
            "market_value": 30,
            "spawn_weight": 0.3,
            "description": "生活在草地和森林區域，體型小、行動迅速、容易被忽視",
        },
        AnimalType.TURTLE: {
            "size": 12,
            "speed": 1.0,
            "health": 50,
            "rarity": RarityLevel.RARE,
            "behavior": BehaviorType.DEFENSIVE,
            "threat_level": ThreatLevel.LOW,
            "color": (107, 142, 35),  # 橄欖綠
            "habitat": ["水邊", "濕地"],
            "drop_items": ["龜肉", "龜殼"],
            "market_value": 30,
            "spawn_weight": 0.25,
            "description": "棲息在水邊和濕地，行動緩慢但防禦力強",
        },
        AnimalType.SHEEP: {
            "size": 10,
            "speed": 2.5,
            "health": 50,
            "rarity": RarityLevel.RARE,
            "behavior": BehaviorType.PEACEFUL,
            "threat_level": ThreatLevel.HARMLESS,
            "color": (255, 255, 255),  # 白色
            "habitat": ["農田", "丘陵"],
            "drop_items": ["羊肉", "羊毛"],
            "market_value": 30,
            "spawn_weight": 0.35,
            "description": "出沒於農田和丘陵地帶，群居性強、容易被發現",
        },
        
        # 超稀有動物（50元）
        AnimalType.MOUNTAIN_LION: {
            "size": 14,
            "speed": 5.0,
            "health": 100,
            "rarity": RarityLevel.SUPER_RARE,
            "behavior": BehaviorType.TERRITORIAL,
            "threat_level": ThreatLevel.HIGH,
            "color": (160, 82, 45),  # 棕褐色
            "habitat": ["山區", "森林深處"],
            "drop_items": ["獅肉", "獅皮"],
            "market_value": 50,
            "spawn_weight": 0.15,
            "description": "棲息在山區和森林深處，行動敏捷且具攻擊性",
        },
        AnimalType.BLACK_PANTHER: {
            "size": 13,
            "speed": 5.0,
            "health": 100,
            "rarity": RarityLevel.SUPER_RARE,
            "behavior": BehaviorType.TERRITORIAL,
            "threat_level": ThreatLevel.HIGH,
            "color": (25, 25, 25),  # 黑色
            "habitat": ["密林"],
            "drop_items": ["豹肉", "豹皮"],
            "market_value": 50,
            "spawn_weight": 0.12,
            "description": "出沒於密林並於夜間活動，行動隱秘且危險",
        },
        
        # 傳奇動物（100元）
        AnimalType.BEAR: {
            "size": 18,
            "speed": 2.5,
            "health": 300,
            "rarity": RarityLevel.LEGENDARY,
            "behavior": BehaviorType.TERRITORIAL,
            "threat_level": ThreatLevel.EXTREME,
            "color": (101, 67, 33),  # 深棕色
            "habitat": ["山區", "森林"],
            "drop_items": ["熊肉", "熊皮", "熊膽"],
            "market_value": 100,
            "spawn_weight": 0.05,
            "description": "棲息於山區和森林，體型巨大且力量強大，具有高度攻擊性，玩家需謹慎接近",
        },
    }

    @classmethod
    def get_animal_property(cls, animal_type, property_name):
        """
        獲取動物的特定屬性\n
        \n
        參數:\n
        animal_type (AnimalType): 動物類型\n
        property_name (str): 屬性名稱\n
        \n
        回傳:\n
        any: 屬性值，如果不存在則返回 None\n
        """
        return cls.ANIMAL_PROPERTIES.get(animal_type, {}).get(property_name)

    @classmethod
    def get_animals_by_habitat(cls, habitat):
        """
        根據棲息地獲取動物列表\n
        \n
        參數:\n
        habitat (str): 棲息地名稱\n
        \n
        回傳:\n
        list: 在該棲息地的動物類型列表\n
        """
        animals = []
        for animal_type, properties in cls.ANIMAL_PROPERTIES.items():
            if habitat in properties.get("habitat", []):
                animals.append(animal_type)
        return animals

    @classmethod
    def get_animals_by_rarity(cls, rarity):
        """
        根據稀有度獲取動物列表\n
        \n
        參數:\n
        rarity (RarityLevel): 稀有度等級\n
        \n
        回傳:\n
        list: 該稀有度的動物類型列表\n
        """
        animals = []
        for animal_type, properties in cls.ANIMAL_PROPERTIES.items():
            if properties.get("rarity") == rarity:
                animals.append(animal_type)
        return animals

    @classmethod
    def get_spawn_weights_for_habitat(cls, habitat):
        """
        獲取特定棲息地的動物生成權重\n
        \n
        參數:\n
        habitat (str): 棲息地名稱\n
        \n
        回傳:\n
        dict: {動物類型: 生成權重}\n
        """
        weights = {}
        animals = cls.get_animals_by_habitat(habitat)

        for animal_type in animals:
            weight = cls.get_animal_property(animal_type, "spawn_weight")
            if weight:
                weights[animal_type] = weight

        return weights

    @classmethod
    def get_random_animal_for_habitat(cls, habitat):
        """
        根據生成權重隨機選擇該棲息地的動物\n
        \n
        參數:\n
        habitat (str): 棲息地名稱\n
        \n
        回傳:\n
        AnimalType: 隨機選中的動物類型，如果沒有則返回 None\n
        """
        weights = cls.get_spawn_weights_for_habitat(habitat)

        if not weights:
            return None

        # 根據權重進行隨機選擇
        animals = list(weights.keys())
        probabilities = list(weights.values())

        # 正規化機率
        total_weight = sum(probabilities)
        normalized_probs = [p / total_weight for p in probabilities]

        # 隨機選擇
        return random.choices(animals, weights=normalized_probs, k=1)[0]

    @classmethod
    def get_animal_loot(cls, animal_type):
        """
        獲取動物死亡時掉落的物品\n
        \n
        參數:\n
        animal_type (AnimalType): 動物類型\n
        \n
        回傳:\n
        list: 掉落物品列表\n
        """
        return cls.get_animal_property(animal_type, "drop_items") or []

    @classmethod
    def get_animal_market_value(cls, animal_type):
        """
        獲取動物的市場價值\n
        \n
        參數:\n
        animal_type (AnimalType): 動物類型\n
        \n
        回傳:\n
        int: 市場價值\n
        """
        return cls.get_animal_property(animal_type, "market_value") or 0

    @classmethod
    def get_animal_rarity_value(cls, rarity):
        """
        根據稀有度獲取獵殺獎勵金額\n
        \n
        參數:\n
        rarity (RarityLevel): 稀有度等級\n
        \n
        回傳:\n
        int: 獵殺獎勵金額\n
        """
        rarity_values = {
            RarityLevel.RARE: 30,
            RarityLevel.SUPER_RARE: 50,
            RarityLevel.LEGENDARY: 100,
        }
        return rarity_values.get(rarity, 0)

    @classmethod
    def get_animal_statistics(cls):
        """
        獲取動物系統統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊\n
        """
        total_animals = len(cls.ANIMAL_PROPERTIES)
        
        rarity_counts = {}
        for rarity in RarityLevel:
            rarity_counts[rarity.value] = len(cls.get_animals_by_rarity(rarity))

        habitats = {}
        for animal_type, properties in cls.ANIMAL_PROPERTIES.items():
            for habitat in properties.get("habitat", []):
                if habitat not in habitats:
                    habitats[habitat] = 0
                habitats[habitat] += 1

        return {
            "total_species": total_animals,
            "rarity_distribution": rarity_counts,
            "habitats": habitats,
        }
