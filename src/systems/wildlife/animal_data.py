######################載入套件######################
from enum import Enum
import random


######################動物類型列舉######################
class AnimalType(Enum):
    """
    動物類型列舉\n
    \n
    定義遊戲中所有的動物種類\n
    區分一般動物、保育類動物和水生動物\n
    """

    # 森林一般動物
    RABBIT = "兔子"  # 無害小動物
    SQUIRREL = "松鼠"  # 無害小動物
    PHEASANT = "雉雞"  # 低威脅鳥類
    FOX = "狐狸"  # 低威脅肉食動物
    DEER = "鹿"  # 溫和草食動物
    SHEEP = "羊"  # 溫和草食動物
    WILD_BOAR = "野豬"  # 中等威脅雜食動物
    WOLF = "野狼"  # 高威脅肉食動物
    BEAR = "熊"  # 高威脅大型雜食動物
    MOUNTAIN_LION = "山獅"  # 高威脅大型肉食動物

    # 森林保育類動物 (受法律保護)
    PANGOLIN = "穿山甲"  # 保育類 - 獵殺違法
    LEOPARD_CAT = "石虎"  # 保育類 - 獵殺違法
    CLOUDED_LEOPARD = "雲豹"  # 保育類 - 獵殺違法

    # 沼澤動物
    FROG = "青蛙"  # 無害小動物
    CROCODILE = "鱷魚"  # 極度危險水中掠食者
    TURTLE = "烏龜"  # 溫和水陸動物

    # 湖泊魚類
    BASS = "鱸魚"  # 常見魚類
    CARP = "鯉魚"  # 常見魚類
    TROUT = "鱒魚"  # 普通魚類
    CATFISH = "鯰魚"  # 普通魚類
    SALMON = "鮭魚"  # 稀有魚類
    PIRANHA = "食人魚"  # 危險魚類
    GROUPER = "石斑魚"  # 常見魚類
    WHALE = "鯨魚"  # 稀有大型魚類
    PENGUIN = "企鵝"  # 稀有鳥類


######################動物威脅等級######################
class ThreatLevel(Enum):
    """
    動物威脅等級\n
    \n
    定義動物對玩家的威脅程度\n
    影響動物的攻擊性和逃跑機率\n
    """

    HARMLESS = "無害"  # 完全無害，不會攻擊
    LOW = "低威脅"  # 很少攻擊，容易逃跑
    MEDIUM = "中等威脅"  # 可能攻擊，有逃跑機率
    HIGH = "高威脅"  # 經常攻擊，較少逃跑
    EXTREME = "極度危險"  # 主動攻擊，很難逃脫


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
        # 森林小型動物
        AnimalType.RABBIT: {
            "size": 12,
            "speed": 4.0,
            "health": 25,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (139, 69, 19),  # 棕色
            "is_protected": False,
            "habitat": ["森林"],
            "drop_items": ["兔肉", "兔毛"],
            "market_value": 40,
            "spawn_weight": 0.4,  # 高生成權重 - 常見
        },
        AnimalType.SQUIRREL: {
            "size": 8,
            "speed": 3.5,
            "health": 15,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (160, 82, 45),  # 淺棕色
            "is_protected": False,
            "habitat": ["森林"],
            "drop_items": ["松鼠肉", "松鼠尾"],
            "market_value": 20,
            "spawn_weight": 0.35,  # 很常見
        },
        AnimalType.PHEASANT: {
            "size": 14,
            "speed": 3.0,
            "health": 30,
            "threat_level": ThreatLevel.LOW,
            "behavior": BehaviorType.PEACEFUL,
            "color": (128, 64, 0),  # 深棕色
            "is_protected": False,
            "habitat": ["森林"],
            "drop_items": ["雉雞肉", "雉雞羽毛"],
            "market_value": 60,
            "spawn_weight": 0.3,
        },
        AnimalType.FOX: {
            "size": 18,
            "speed": 4.0,
            "health": 50,
            "threat_level": ThreatLevel.LOW,
            "behavior": BehaviorType.DEFENSIVE,
            "color": (255, 140, 0),  # 橙色
            "is_protected": False,
            "habitat": ["森林"],
            "drop_items": ["狐狸肉", "狐狸皮"],
            "market_value": 100,
            "spawn_weight": 0.15,  # 較少見
        },
        AnimalType.BEAR: {
            "size": 32,
            "speed": 2.5,
            "health": 150,
            "threat_level": ThreatLevel.HIGH,
            "behavior": BehaviorType.AGGRESSIVE,
            "color": (101, 67, 33),  # 深棕色
            "is_protected": False,
            "habitat": ["森林"],
            "drop_items": ["熊肉", "熊皮", "熊膽"],
            "market_value": 500,
            "spawn_weight": 0.05,  # 稀有
        },
        # 森林一般動物
        AnimalType.DEER: {
            "size": 24,
            "speed": 3.5,
            "health": 60,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (139, 69, 19),  # 棕色
            "is_protected": False,
            "habitat": ["森林"],
            "drop_items": ["鹿肉", "鹿皮"],
            "market_value": 150,
            "spawn_weight": 0.3,  # 生成權重
        },
        AnimalType.SHEEP: {
            "size": 20,
            "speed": 2.5,
            "health": 45,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (255, 255, 255),  # 白色
            "is_protected": False,
            "habitat": ["森林", "草地"],
            "drop_items": ["羊肉", "羊毛"],
            "market_value": 120,
            "spawn_weight": 0.25,
        },
        AnimalType.WILD_BOAR: {
            "size": 22,
            "speed": 3.0,
            "health": 80,
            "threat_level": ThreatLevel.MEDIUM,
            "behavior": BehaviorType.DEFENSIVE,
            "color": (64, 64, 64),  # 暗灰色
            "is_protected": False,
            "habitat": ["森林"],
            "drop_items": ["豬肉", "豬皮"],
            "market_value": 180,
            "spawn_weight": 0.2,
        },
        AnimalType.WOLF: {
            "size": 26,
            "speed": 4.5,
            "health": 100,
            "threat_level": ThreatLevel.HIGH,
            "behavior": BehaviorType.AGGRESSIVE,
            "color": (105, 105, 105),  # 灰色
            "is_protected": False,
            "habitat": ["森林"],
            "drop_items": ["狼肉", "狼皮"],
            "market_value": 250,
            "spawn_weight": 0.15,
        },
        AnimalType.MOUNTAIN_LION: {
            "size": 28,
            "speed": 5.0,
            "health": 120,
            "threat_level": ThreatLevel.HIGH,
            "behavior": BehaviorType.PREDATOR,
            "color": (160, 82, 45),  # 棕褐色
            "is_protected": False,
            "habitat": ["森林"],
            "drop_items": ["獅肉", "獅皮"],
            "market_value": 300,
            "spawn_weight": 0.1,
        },
        # 保育類動物
        AnimalType.PANGOLIN: {
            "size": 18,
            "speed": 1.5,
            "health": 40,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.DEFENSIVE,
            "color": (139, 69, 19),  # 棕色
            "is_protected": True,  # 保育類！
            "habitat": ["森林"],
            "drop_items": ["穿山甲鱗片"],  # 違法物品
            "market_value": 0,  # 不能合法販售
            "spawn_weight": 0.05,  # 稀有
        },
        AnimalType.LEOPARD_CAT: {
            "size": 16,
            "speed": 6.0,
            "health": 50,
            "threat_level": ThreatLevel.LOW,
            "behavior": BehaviorType.TERRITORIAL,
            "color": (255, 215, 0),  # 金色
            "is_protected": True,  # 保育類！
            "habitat": ["森林"],
            "drop_items": ["石虎皮"],  # 違法物品
            "market_value": 0,
            "spawn_weight": 0.03,  # 非常稀有
        },
        AnimalType.CLOUDED_LEOPARD: {
            "size": 30,
            "speed": 5.5,
            "health": 90,
            "threat_level": ThreatLevel.MEDIUM,
            "behavior": BehaviorType.PREDATOR,
            "color": (192, 192, 192),  # 銀色
            "is_protected": True,  # 保育類！
            "habitat": ["森林"],
            "drop_items": ["雲豹皮"],  # 違法物品
            "market_value": 0,
            "spawn_weight": 0.02,  # 極度稀有
        },
        # 沼澤動物
        AnimalType.FROG: {
            "size": 8,
            "speed": 2.0,
            "health": 15,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (0, 128, 0),  # 綠色
            "is_protected": False,
            "habitat": ["沼澤"],
            "drop_items": ["青蛙腿"],
            "market_value": 20,
            "spawn_weight": 0.4,
        },
        AnimalType.CROCODILE: {
            "size": 40,
            "speed": 3.0,
            "health": 200,
            "threat_level": ThreatLevel.EXTREME,
            "behavior": BehaviorType.PREDATOR,
            "color": (34, 139, 34),  # 森林綠
            "is_protected": False,
            "habitat": ["沼澤", "湖泊"],
            "drop_items": ["鱷魚肉", "鱷魚皮"],
            "market_value": 500,
            "spawn_weight": 0.05,
        },
        AnimalType.TURTLE: {
            "size": 14,
            "speed": 1.0,
            "health": 80,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (107, 142, 35),  # 橄欖綠
            "is_protected": False,
            "habitat": ["沼澤", "湖泊"],
            "drop_items": ["龜肉", "龜殼"],
            "market_value": 100,
            "spawn_weight": 0.15,
        },
        # 湖泊魚類
        AnimalType.BASS: {
            "size": 16,
            "speed": 3.0,
            "health": 35,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (128, 128, 128),  # 灰色
            "is_protected": False,
            "habitat": ["湖泊"],
            "drop_items": ["鱸魚肉"],
            "market_value": 60,
            "spawn_weight": 0.35,
        },
        AnimalType.CARP: {
            "size": 18,
            "speed": 2.0,
            "health": 40,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (255, 215, 0),  # 金色
            "is_protected": False,
            "habitat": ["湖泊"],
            "drop_items": ["鯉魚肉"],
            "market_value": 50,
            "spawn_weight": 0.4,  # 很常見
        },
        AnimalType.TROUT: {
            "size": 14,
            "speed": 3.5,
            "health": 30,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (255, 20, 147),  # 深粉紅色
            "is_protected": False,
            "habitat": ["湖泊"],
            "drop_items": ["鱒魚肉"],
            "market_value": 80,
            "spawn_weight": 0.25,
        },
        AnimalType.CATFISH: {
            "size": 20,
            "speed": 2.5,
            "health": 45,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (139, 69, 19),  # 棕色
            "is_protected": False,
            "habitat": ["湖泊"],
            "drop_items": ["鯰魚肉"],
            "market_value": 70,
            "spawn_weight": 0.3,
        },
        AnimalType.SALMON: {
            "size": 22,
            "speed": 4.0,
            "health": 50,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (255, 160, 122),  # 淺鮭魚色
            "is_protected": False,
            "habitat": ["湖泊"],
            "drop_items": ["鮭魚肉", "魚卵"],
            "market_value": 150,
            "spawn_weight": 0.15,  # 較稀有
        },
        AnimalType.PIRANHA: {
            "size": 12,
            "speed": 4.0,
            "health": 30,
            "threat_level": ThreatLevel.HIGH,
            "behavior": BehaviorType.AGGRESSIVE,
            "color": (255, 0, 0),  # 紅色
            "is_protected": False,
            "habitat": ["湖泊"],
            "drop_items": ["食人魚肉"],
            "market_value": 80,
            "spawn_weight": 0.3,
            "water_attack_time": 60,  # 在水中1分鐘後攻擊
        },
        AnimalType.GROUPER: {
            "size": 18,
            "speed": 2.5,
            "health": 40,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (70, 130, 180),  # 鋼藍色
            "is_protected": False,
            "habitat": ["湖泊"],
            "drop_items": ["石斑魚肉"],
            "market_value": 120,
            "spawn_weight": 0.4,
        },
        AnimalType.WHALE: {
            "size": 80,
            "speed": 2.0,
            "health": 500,
            "threat_level": ThreatLevel.LOW,
            "behavior": BehaviorType.PEACEFUL,
            "color": (25, 25, 112),  # 午夜藍
            "is_protected": False,
            "habitat": ["湖泊"],
            "drop_items": ["鯨魚肉", "鯨脂"],
            "market_value": 1000,
            "spawn_weight": 0.01,  # 極度稀有
            "is_rare": True,
        },
        AnimalType.PENGUIN: {
            "size": 16,
            "speed": 2.5,
            "health": 35,
            "threat_level": ThreatLevel.HARMLESS,
            "behavior": BehaviorType.PEACEFUL,
            "color": (0, 0, 0),  # 黑色
            "is_protected": False,
            "habitat": ["湖泊"],
            "drop_items": ["企鵝肉"],
            "market_value": 800,
            "spawn_weight": 0.01,  # 極度稀有
            "is_rare": True,
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
    def get_protected_animals(cls):
        """
        獲取所有保育類動物\n
        \n
        回傳:\n
        list: 保育類動物列表\n
        """
        protected = []
        for animal_type, properties in cls.ANIMAL_PROPERTIES.items():
            if properties.get("is_protected", False):
                protected.append(animal_type)
        return protected

    @classmethod
    def is_animal_protected(cls, animal_type):
        """
        檢查動物是否為保育類\n
        \n
        參數:\n
        animal_type (AnimalType): 動物類型\n
        \n
        回傳:\n
        bool: True 表示是保育類動物\n
        """
        return cls.get_animal_property(animal_type, "is_protected") or False

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
        int: 市場價值，保育類動物返回 0\n
        """
        if cls.is_animal_protected(animal_type):
            return 0  # 保育類動物不能合法販售

        return cls.get_animal_property(animal_type, "market_value") or 0

    @classmethod
    def get_animal_statistics(cls):
        """
        獲取動物系統統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊\n
        """
        total_animals = len(cls.ANIMAL_PROPERTIES)
        protected_count = len(cls.get_protected_animals())

        habitats = {}
        for animal_type, properties in cls.ANIMAL_PROPERTIES.items():
            for habitat in properties.get("habitat", []):
                if habitat not in habitats:
                    habitats[habitat] = 0
                habitats[habitat] += 1

        return {
            "total_species": total_animals,
            "protected_species": protected_count,
            "regular_species": total_animals - protected_count,
            "habitats": habitats,
        }
