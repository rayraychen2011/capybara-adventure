######################載入套件######################
from enum import Enum
import random


######################職業類型列舉######################
class Profession(Enum):
    """
    NPC 職業類型列舉\n
    \n
    定義小鎮中所有可能的 NPC 職業類型\n
    每個職業都有特定的工作內容和分布數量\n
    """

    # 農業相關職業
    FARMER = "農夫"

    # 宗教人員
    PRIEST = "牧師"
    NUN = "修女"

    # 醫療人員
    DOCTOR = "醫生"
    NURSE = "護士"

    # 商業人員
    GUN_SHOP_WORKER = "槍械店員工"
    STREET_VENDOR = "路邊小販"
    FISHING_SHOP_WORKER = "釣魚店員工"
    CONVENIENCE_STORE_WORKER = "便利商店員工"

    # 其他專業
    POWER_WORKER = "電力系統員工"
    HUNTER = "獵人"
    RESIDENT = "一般居民"  # 新增：沒有特殊職業的一般居民

    # 森林部落
    TRIBE_MEMBER = "部落成員"


######################職業資料管理######################
class ProfessionData:
    """
    職業資料管理類別\n
    \n
    管理各種職業的基本資訊、數量分配和特殊屬性\n
    提供職業分配演算法和職業相關的資料查詢\n
    """

    # 各職業的預定數量 (根據規格書)
    PROFESSION_COUNTS = {
        Profession.FARMER: 100,
        Profession.PRIEST: 2,
        Profession.NUN: 48,
        Profession.DOCTOR: 10,
        Profession.NURSE: 40,
        Profession.GUN_SHOP_WORKER: 20,
        Profession.STREET_VENDOR: 10,
        Profession.FISHING_SHOP_WORKER: 20,
        Profession.CONVENIENCE_STORE_WORKER: 30,
        Profession.POWER_WORKER: 30,
        Profession.HUNTER: 20,
        Profession.RESIDENT: 150,  # 一般居民
        Profession.TRIBE_MEMBER: 100,  # 森林部落
    }

    # 職業工作場所對應
    PROFESSION_WORKPLACES = {
        Profession.FARMER: ["農田"],
        Profession.PRIEST: ["教堂"],
        Profession.NUN: ["教堂"],
        Profession.DOCTOR: ["醫院"],
        Profession.NURSE: ["醫院"],
        Profession.GUN_SHOP_WORKER: ["槍械店"],
        Profession.STREET_VENDOR: ["街道"],
        Profession.FISHING_SHOP_WORKER: ["釣魚店"],
        Profession.CONVENIENCE_STORE_WORKER: ["便利商店"],
        Profession.POWER_WORKER: ["電力場", "各區域"],
        Profession.HUNTER: ["森林"],
        Profession.RESIDENT: ["住宅區"],  # 一般居民主要在住宅區活動
        Profession.TRIBE_MEMBER: ["森林部落"],
    }

    # 職業的工作時間表 (小時制，24小時)
    PROFESSION_SCHEDULES = {
        Profession.FARMER: {
            "work_start": 6,
            "work_end": 18,
            "break_start": 12,
            "break_end": 13,
        },
        Profession.PRIEST: {
            "work_start": 8,
            "work_end": 20,
            "break_start": 14,
            "break_end": 15,
        },
        Profession.NUN: {
            "work_start": 6,
            "work_end": 22,
            "break_start": 12,
            "break_end": 13,
        },
        Profession.DOCTOR: {
            "work_start": 8,
            "work_end": 18,
            "break_start": 12,
            "break_end": 13,
        },
        Profession.NURSE: {
            "work_start": 0,  # 護士需要輪班
            "work_end": 24,
            "break_start": None,
            "break_end": None,
        },
        Profession.GUN_SHOP_WORKER: {
            "work_start": 9,
            "work_end": 21,
            "break_start": 12,
            "break_end": 13,
        },
        Profession.STREET_VENDOR: {
            "work_start": 7,
            "work_end": 19,
            "break_start": 12,
            "break_end": 13,
        },
        Profession.FISHING_SHOP_WORKER: {
            "work_start": 6,
            "work_end": 20,
            "break_start": 12,
            "break_end": 13,
        },
        Profession.CONVENIENCE_STORE_WORKER: {
            "work_start": 0,  # 便利商店24小時營業
            "work_end": 24,
            "break_start": None,
            "break_end": None,
        },
        Profession.POWER_WORKER: {
            "work_start": 8,
            "work_end": 17,
            "break_start": 12,
            "break_end": 13,
        },
        Profession.HUNTER: {
            "work_start": 5,
            "work_end": 17,
            "break_start": 11,
            "break_end": 12,
        },
        Profession.RESIDENT: {
            "work_start": 9,
            "work_end": 17,
            "break_start": 12,
            "break_end": 13,
        },
        Profession.TRIBE_MEMBER: {
            "work_start": 6,
            "work_end": 18,
            "break_start": 12,
            "break_end": 13,
        },
    }

    @classmethod
    def get_total_npc_count(cls):
        """
        獲取 NPC 總數量\n
        \n
        回傳:\n
        int: 所有 NPC 的總數量\n
        """
        return sum(cls.PROFESSION_COUNTS.values())

    @classmethod
    def get_town_npc_count(cls):
        """
        獲取小鎮內 NPC 數量 (不包含森林部落)\n
        \n
        回傳:\n
        int: 小鎮內 NPC 數量\n
        """
        total = sum(cls.PROFESSION_COUNTS.values())
        tribe_count = cls.PROFESSION_COUNTS[Profession.TRIBE_MEMBER]
        return total - tribe_count

    @classmethod
    def get_profession_count(cls, profession):
        """
        獲取特定職業的數量\n
        \n
        參數:\n
        profession (Profession): 職業類型\n
        \n
        回傳:\n
        int: 該職業的數量\n
        """
        return cls.PROFESSION_COUNTS.get(profession, 0)

    @classmethod
    def get_profession_workplaces(cls, profession):
        """
        獲取職業的工作場所列表\n
        \n
        參數:\n
        profession (Profession): 職業類型\n
        \n
        回傳:\n
        list: 工作場所名稱列表\n
        """
        return cls.PROFESSION_WORKPLACES.get(profession, [])

    @classmethod
    def get_profession_schedule(cls, profession):
        """
        獲取職業的工作時間表\n
        \n
        參數:\n
        profession (Profession): 職業類型\n
        \n
        回傳:\n
        dict: 包含工作時間的字典\n
        """
        return cls.PROFESSION_SCHEDULES.get(
            profession,
            {"work_start": 9, "work_end": 17, "break_start": 12, "break_end": 13},
        )

    @classmethod
    def is_profession_available_for_assignment(cls, profession, current_assignments):
        """
        檢查職業是否還有空缺可以分配\n
        \n
        參數:\n
        profession (Profession): 職業類型\n
        current_assignments (dict): 目前已分配的職業統計\n
        \n
        回傳:\n
        bool: True 表示還有空缺可分配\n
        """
        max_count = cls.get_profession_count(profession)
        current_count = current_assignments.get(profession, 0)
        return current_count < max_count

    @classmethod
    def get_random_profession_by_workplace(cls, workplace_type):
        """
        根據工作場所類型隨機獲取合適的職業\n
        \n
        參數:\n
        workplace_type (str): 工作場所類型\n
        \n
        回傳:\n
        Profession: 合適的職業類型，如果沒有則返回 None\n
        """
        suitable_professions = []

        for profession, workplaces in cls.PROFESSION_WORKPLACES.items():
            if workplace_type in workplaces:
                suitable_professions.append(profession)

        if suitable_professions:
            return random.choice(suitable_professions)
        return None

    @classmethod
    def get_profession_color(cls, profession):
        """
        獲取職業對應的顯示顏色\n
        \n
        參數:\n
        profession (Profession): 職業類型\n
        \n
        回傳:\n
        tuple: RGB 顏色值\n
        """
        color_map = {
            Profession.FARMER: (139, 69, 19),  # 棕色
            Profession.PRIEST: (255, 215, 0),  # 金色
            Profession.NUN: (128, 0, 128),  # 紫色
            Profession.DOCTOR: (255, 255, 255),  # 白色
            Profession.NURSE: (255, 192, 203),  # 粉紅色
            Profession.GUN_SHOP_WORKER: (105, 105, 105),  # 灰色
            Profession.STREET_VENDOR: (255, 165, 0),  # 橘色
            Profession.FISHING_SHOP_WORKER: (0, 191, 255),  # 淺藍色
            Profession.CONVENIENCE_STORE_WORKER: (0, 255, 0),  # 綠色
            Profession.POWER_WORKER: (255, 255, 0),  # 黃色
            Profession.HUNTER: (34, 139, 34),  # 森林綠
            Profession.RESIDENT: (169, 169, 169),  # 淺灰色
            Profession.TRIBE_MEMBER: (160, 82, 45),  # 深棕色
        }
        return color_map.get(profession, (128, 128, 128))  # 預設灰色

    @classmethod
    def generate_profession_list(cls):
        """
        生成完整的職業分配列表\n
        \n
        根據規格書的數量要求，生成所有 NPC 的職業分配\n
        \n
        回傳:\n
        list: 包含所有 NPC 職業的列表\n
        """
        profession_list = []

        for profession, count in cls.PROFESSION_COUNTS.items():
            profession_list.extend([profession] * count)

        # 隨機打亂順序，避免職業聚集
        random.shuffle(profession_list)

        return profession_list
