######################載入套件######################
import random
from enum import Enum


######################性格類型######################
class PersonalityType(Enum):
    """
    性格類型列舉\n
    \n
    定義不同的性格特徵，每種性格會影響NPC的對話風格和行為模式\n
    """
    FRIENDLY = "友善"      # 友善親切，喜歡聊天
    SHY = "害羞"          # 內向害羞，話不多
    GRUMPY = "暴躁"       # 脾氣暴躁，容易生氣
    CHEERFUL = "開朗"     # 開朗樂觀，總是很開心
    SERIOUS = "嚴肅"      # 嚴肅認真，很少開玩笑
    HUMOROUS = "幽默"     # 幽默風趣，喜歡開玩笑
    WISE = "睿智"         # 智慧老成，喜歡分享人生智慧
    ENERGETIC = "活潑"    # 活潑好動，充滿活力
    CALM = "冷靜"         # 冷靜沉著，不容易激動
    MYSTERIOUS = "神秘"   # 神秘莫測，話中有話


######################性格資料庫######################
class PersonalityDatabase:
    """
    性格資料庫 - 管理不同性格的對話和行為模式\n
    \n
    為每種性格類型提供專屬的對話內容、問候語和反應\n
    確保每個NPC都有獨特的個性表現\n
    """

    # 基礎問候語
    GREETINGS = {
        PersonalityType.FRIENDLY: [
            "你好！很高興見到你！",
            "嗨！今天過得怎麼樣？",
            "歡迎！有什麼我可以幫忙的嗎？",
            "你好呀！天氣真不錯呢！",
            "hi！很開心能跟你聊天！"
        ],
        PersonalityType.SHY: [
            "嗯...你好...",
            "啊，你好...",
            "哦，嗨...",
            "呃...hi...",
            "你...你好..."
        ],
        PersonalityType.GRUMPY: [
            "嗯，什麼事？",
            "又怎麼了？",
            "有事說事。",
            "別浪費我時間。",
            "哼，什麼風把你吹來了？"
        ],
        PersonalityType.CHEERFUL: [
            "哈囉！今天真是美好的一天！",
            "你好！我心情超好的！",
            "嗨嗨！生活真是太棒了！",
            "哈哈，你好呀！",
            "太好了！又遇到新朋友了！"
        ],
        PersonalityType.SERIOUS: [
            "你好。",
            "請問有什麼事嗎？",
            "嗯，你好。",
            "有何貴幹？",
            "你好，請說。"
        ],
        PersonalityType.HUMOROUS: [
            "哈哈，看誰來了！",
            "嘿，帥哥/美女！",
            "哇，稀客啊！",
            "yo～有人需要笑話嗎？",
            "嘿嘿，又見面了！"
        ],
        PersonalityType.WISE: [
            "年輕人，你好。",
            "你好，孩子。",
            "嗯，我們又見面了。",
            "歲月如流水，你好。",
            "時光荏苒，你好啊。"
        ],
        PersonalityType.ENERGETIC: [
            "哇！你好你好！",
            "嘿！超開心見到你！",
            "太棒了！新朋友！",
            "哇嗚！你來啦！",
            "讚讚讚！你好！"
        ],
        PersonalityType.CALM: [
            "你好。",
            "嗯，你來了。",
            "你好，一切都好嗎？",
            "安好。",
            "你好，很平靜的一天。"
        ],
        PersonalityType.MYSTERIOUS: [
            "呵呵...我們又見面了...",
            "命運讓我們相遇...",
            "有緣千里來相會...",
            "一切都是註定的...",
            "果然...你還是來了..."
        ]
    }

    # 日常對話
    DAILY_CONVERSATIONS = {
        PersonalityType.FRIENDLY: [
            "今天的天氣真不錯呢！",
            "小鎮最近變得越來越熱鬧了。",
            "你知道嗎？我今天心情特別好！",
            "希望每天都像今天一樣美好。",
            "有空常來聊天哦！",
            "這裡的人都很友善呢。"
        ],
        PersonalityType.SHY: [
            "呃...天氣還不錯...",
            "我...我不太會聊天...",
            "對不起，我有點緊張...",
            "其實...我挺喜歡這裡的...",
            "你...你是好人...",
            "謝謝你願意聽我說話..."
        ],
        PersonalityType.GRUMPY: [
            "這鬼天氣真是受不了。",
            "現在的年輕人啊...",
            "什麼世道，一天比一天糟。",
            "別煩我，我心情不好。",
            "哼，又是無聊的一天。",
            "這小鎮越來越吵鬧了。"
        ],
        PersonalityType.CHEERFUL: [
            "哈哈，每天都充滿希望！",
            "生活真是太美好了！",
            "我今天又學到新東西了！",
            "笑一笑，十年少！",
            "每天都要保持好心情哦！",
            "樂觀面對每一天！"
        ],
        PersonalityType.SERIOUS: [
            "工作要認真對待。",
            "時間就是金錢。",
            "做事要有條理。",
            "責任重於泰山。",
            "凡事都要三思而後行。",
            "效率很重要。"
        ],
        PersonalityType.HUMOROUS: [
            "你知道為什麼雞要過馬路嗎？因為牠想到對面去！",
            "我今天又想到一個笑話！",
            "生活需要一點幽默感。",
            "哈哈，你的表情好有趣！",
            "笑話能讓人忘記煩惱。",
            "幽默是生活的調味料。"
        ],
        PersonalityType.WISE: [
            "年輕人，記住要珍惜時間。",
            "人生如夢，歲月如歌。",
            "智慧來自於經驗。",
            "做人要誠實，做事要踏實。",
            "老了才知道健康的重要。",
            "人生最重要的是知足常樂。"
        ],
        PersonalityType.ENERGETIC: [
            "今天也要全力以赴！",
            "活力滿滿的一天開始了！",
            "運動讓我充滿活力！",
            "每天都要積極向上！",
            "年輕就是要有衝劲！",
            "讓我們一起加油吧！"
        ],
        PersonalityType.CALM: [
            "內心平靜最重要。",
            "急躁解決不了問題。",
            "慢慢來，比較快。",
            "心如止水，風平浪靜。",
            "冷靜思考，理性行動。",
            "寧靜致遠，淡泊明志。"
        ],
        PersonalityType.MYSTERIOUS: [
            "有些事情...不能說得太明白...",
            "命運的齒輪正在轉動...",
            "一切都有它的原因...",
            "有緣分的話，我們還會再見面...",
            "真相往往隱藏在表象之下...",
            "時機到了，你就會明白的..."
        ]
    }

    # 職業相關對話（會根據性格調整語調）
    PROFESSION_TALKS = {
        "farmer": {
            PersonalityType.FRIENDLY: [
                "農作物長得真好！想嚐嚐新鮮蔬菜嗎？",
                "種田雖然辛苦，但看到豐收就很開心！",
                "歡迎來我的農田參觀！"
            ],
            PersonalityType.GRUMPY: [
                "種田不容易，別以為很輕鬆。",
                "這些菜都是我辛苦種的，不便宜。",
                "天氣不好，收成就差。"
            ],
            PersonalityType.WISE: [
                "種田教會我耐心和毅力。",
                "土地是我們的根，要好好珍惜。",
                "農夫的智慧來自於大自然。"
            ]
        },
        "doctor": {
            PersonalityType.SERIOUS: [
                "健康是最重要的財富。",
                "請記得定期健康檢查。",
                "有任何身體不適請及時就醫。"
            ],
            PersonalityType.FRIENDLY: [
                "保持健康的生活習慣很重要哦！",
                "有什麼健康問題都可以來找我！",
                "預防勝於治療，要好好照顧自己！"
            ]
        },
        "hunter": {
            PersonalityType.SERIOUS: [
                "狩獵需要技巧和耐心。",
                "安全第一，使用武器要小心。",
                "保護環境是獵人的責任。"
            ],
            PersonalityType.MYSTERIOUS: [
                "森林裡有很多秘密...",
                "真正的獵人懂得與自然和諧相處...",
                "有些獵物...不是用眼睛看到的..."
            ]
        }
    }

    @classmethod
    def get_random_greeting(cls, personality_type):
        """
        根據性格類型獲取隨機問候語\n
        \n
        參數:\n
        personality_type (PersonalityType): 性格類型\n
        \n
        回傳:\n
        str: 隨機問候語\n
        """
        return random.choice(cls.GREETINGS.get(personality_type, ["你好。"]))

    @classmethod
    def get_random_daily_talk(cls, personality_type):
        """
        根據性格類型獲取隨機日常對話\n
        \n
        參數:\n
        personality_type (PersonalityType): 性格類型\n
        \n
        回傳:\n
        str: 隨機日常對話\n
        """
        return random.choice(cls.DAILY_CONVERSATIONS.get(personality_type, ["..."]))

    @classmethod
    def get_profession_talk(cls, profession_name, personality_type):
        """
        根據職業和性格獲取專業對話\n
        \n
        參數:\n
        profession_name (str): 職業名稱\n
        personality_type (PersonalityType): 性格類型\n
        \n
        回傳:\n
        str: 專業對話，如果沒有則返回日常對話\n
        """
        profession_talks = cls.PROFESSION_TALKS.get(profession_name.lower(), {})
        if personality_type in profession_talks:
            return random.choice(profession_talks[personality_type])
        else:
            # 如果沒有特定的職業對話，返回日常對話
            return cls.get_random_daily_talk(personality_type)


######################姓名生成器######################
class NameGenerator:
    """
    姓名生成器 - 為NPC生成具有性格特色的姓名\n
    \n
    根據性格類型為NPC分配合適的姓名\n
    確保每個NPC都有獨特且符合性格的名字\n
    """

    # 常見姓氏
    SURNAMES = [
        "王", "李", "張", "劉", "陳", "楊", "趙", "黃", "周", "吳",
        "徐", "孫", "胡", "朱", "高", "林", "何", "郭", "馬", "羅",
        "梁", "宋", "鄭", "謝", "韓", "唐", "馮", "于", "董", "蕭",
        "程", "曹", "袁", "鄧", "許", "傅", "沈", "曾", "彭", "呂"
    ]

    # 根據性格分類的名字
    PERSONALITY_NAMES = {
        PersonalityType.FRIENDLY: {
            "male": ["友善", "和藹", "親切", "溫和", "和睦", "友好", "和諧", "善良", "溫暖", "友愛"],
            "female": ["友萍", "和美", "親兒", "溫柔", "和香", "友芳", "和花", "善美", "溫心", "友蓮"]
        },
        PersonalityType.SHY: {
            "male": ["文靜", "安靜", "靜默", "寧靜", "幽靜", "靜心", "文雅", "內斂", "謙和", "靜思"],
            "female": ["靜怡", "文靜", "安妮", "靜心", "幽蘭", "靜美", "文雅", "內秀", "謙婉", "靜雯"]
        },
        PersonalityType.GRUMPY: {
            "male": ["剛強", "剛毅", "威武", "雄威", "強勇", "剛正", "威嚴", "堅毅", "剛烈", "威猛"],
            "female": ["剛花", "毅美", "威鳳", "雄英", "強美", "剛玉", "威華", "堅美", "烈美", "威鳳"]
        },
        PersonalityType.CHEERFUL: {
            "male": ["樂天", "歡喜", "快樂", "喜悅", "歡樂", "樂觀", "開心", "愉快", "喜樂", "歡欣"],
            "female": ["樂美", "歡喜", "快樂", "喜悅", "歡欣", "樂怡", "開心", "愉美", "喜美", "歡美"]
        },
        PersonalityType.SERIOUS: {
            "male": ["正直", "嚴謹", "莊重", "端正", "正義", "嚴肅", "莊嚴", "正氣", "嚴正", "端莊"],
            "female": ["正美", "嚴慧", "莊雅", "端秀", "正義", "嚴美", "莊美", "正心", "嚴雯", "端美"]
        },
        PersonalityType.HUMOROUS: {
            "male": ["風趣", "幽默", "詼諧", "機智", "風雅", "趣味", "幽雅", "機靈", "風采", "趣智"],
            "female": ["風美", "幽蘭", "詼美", "機慧", "風雅", "趣美", "幽雅", "機美", "風華", "趣雯"]
        },
        PersonalityType.WISE: {
            "male": ["智慧", "睿智", "博學", "聰明", "明智", "智仁", "睿明", "博雅", "聰慧", "明理"],
            "female": ["智美", "睿慧", "博雅", "聰美", "明慧", "智蘭", "睿美", "博美", "聰慧", "明美"]
        },
        PersonalityType.ENERGETIC: {
            "male": ["活力", "精神", "朝氣", "活躍", "生機", "精力", "活潑", "動力", "活躍", "精彩"],
            "female": ["活美", "精華", "朝美", "活蘭", "生美", "精美", "活花", "動美", "活雯", "精心"]
        },
        PersonalityType.CALM: {
            "male": ["冷靜", "沉著", "平靜", "安詳", "冷靜", "沉穩", "平和", "安寧", "冷峻", "沉默"],
            "female": ["冷美", "沉雅", "平美", "安詳", "冷雯", "沉美", "平心", "安美", "冷華", "沉慧"]
        },
        PersonalityType.MYSTERIOUS: {
            "male": ["神秘", "玄妙", "深邃", "神奇", "奧秘", "玄學", "深沉", "神韻", "玄機", "深謀"],
            "female": ["神美", "玄蘭", "深雅", "神華", "奧美", "玄美", "深美", "神雯", "玄慧", "深心"]
        }
    }

    @classmethod
    def generate_name(cls, personality_type):
        """
        根據性格類型生成姓名\n
        \n
        參數:\n
        personality_type (PersonalityType): 性格類型\n
        \n
        回傳:\n
        str: 生成的姓名\n
        """
        # 隨機選擇姓氏
        surname = random.choice(cls.SURNAMES)
        
        # 隨機選擇性別
        gender = random.choice(["male", "female"])
        
        # 根據性格和性別選擇名字
        if personality_type in cls.PERSONALITY_NAMES:
            given_name = random.choice(cls.PERSONALITY_NAMES[personality_type][gender])
        else:
            # 備用方案：使用通用名字
            default_names = {
                "male": ["志強", "建國", "世界", "明華", "國強", "志明", "建華", "世民", "明強", "國華"],
                "female": ["淑芬", "美玲", "雅雯", "淑華", "美華", "雅芳", "淑玲", "美芬", "雅華", "淑雯"]
            }
            given_name = random.choice(default_names[gender])
        
        return surname + given_name


######################NPC性格系統######################
class NPCPersonalitySystem:
    """
    NPC性格系統 - 為每個NPC分配獨特的性格和對話\n
    \n
    管理NPC的性格分配、姓名生成和對話系統\n
    確保每個NPC都有豐富的個性表現\n
    """

    def __init__(self):
        """
        初始化NPC性格系統\n
        """
        self.assigned_personalities = {}  # 記錄已分配的性格
        self.npc_profiles = {}  # 存儲每個NPC的完整檔案
        
        print("NPC性格系統初始化完成")

    def assign_personality_to_npc(self, npc):
        """
        為NPC分配性格和生成個人檔案\n
        \n
        參數:\n
        npc (NPC): NPC物件\n
        \n
        回傳:\n
        dict: NPC的性格檔案\n
        """
        # 隨機選擇性格類型
        personality_type = random.choice(list(PersonalityType))
        
        # 生成符合性格的姓名
        personality_name = NameGenerator.generate_name(personality_type)
        
        # 建立個人檔案
        profile = {
            "id": npc.id,
            "name": personality_name,
            "personality_type": personality_type,
            "profession": npc.profession,
            "greeting": PersonalityDatabase.get_random_greeting(personality_type),
            "conversation_history": [],
            "interaction_count": 0,
            "mood": 100,  # 心情指數 (0-100)
            "relationship_level": 0,  # 與玩家的關係等級
        }
        
        # 更新NPC的基本資訊
        npc.name = personality_name
        npc.personality_type = personality_type
        npc.personality_profile = profile
        
        # 生成性格化的對話內容
        self._generate_personality_dialogues(npc)
        
        # 記錄分配
        self.assigned_personalities[npc.id] = profile
        self.npc_profiles[npc.id] = profile
        
        print(f"為NPC {npc.id} 分配性格：{personality_name} ({personality_type.value})")
        return profile

    def _generate_personality_dialogues(self, npc):
        """
        根據性格生成個性化對話\n
        \n
        參數:\n
        npc (NPC): NPC物件\n
        """
        personality_type = npc.personality_type
        profession_name = npc.profession.value if hasattr(npc.profession, 'value') else str(npc.profession)
        
        # 生成多種類型的對話
        dialogues = []
        
        # 問候語
        dialogues.extend(PersonalityDatabase.GREETINGS.get(personality_type, ["你好。"]))
        
        # 日常對話
        dialogues.extend(PersonalityDatabase.DAILY_CONVERSATIONS.get(personality_type, ["..."]))
        
        # 職業相關對話
        profession_talks = PersonalityDatabase.PROFESSION_TALKS.get(profession_name.lower(), {})
        if personality_type in profession_talks:
            dialogues.extend(profession_talks[personality_type])
        
        # 更新NPC的對話列表
        npc.dialogue_lines = dialogues

    def get_npc_dialogue(self, npc, interaction_type="daily"):
        """
        根據NPC性格和互動類型獲取對話\n
        \n
        參數:\n
        npc (NPC): NPC物件\n
        interaction_type (str): 互動類型 ("greeting", "daily", "profession")\n
        \n
        回傳:\n
        str: 對話內容\n
        """
        if not hasattr(npc, 'personality_type'):
            return "你好。"  # 備用對話
        
        personality_type = npc.personality_type
        
        if interaction_type == "greeting":
            dialogue = PersonalityDatabase.get_random_greeting(personality_type)
        elif interaction_type == "profession":
            profession_name = npc.profession.value if hasattr(npc.profession, 'value') else str(npc.profession)
            dialogue = PersonalityDatabase.get_profession_talk(profession_name, personality_type)
        else:  # daily
            dialogue = PersonalityDatabase.get_random_daily_talk(personality_type)
        
        # 記錄對話歷史
        if npc.id in self.npc_profiles:
            profile = self.npc_profiles[npc.id]
            profile["conversation_history"].append({
                "dialogue": dialogue,
                "type": interaction_type,
                "timestamp": time.time()
            })
            profile["interaction_count"] += 1
            
            # 保持對話歷史在合理範圍內
            if len(profile["conversation_history"]) > 10:
                profile["conversation_history"].pop(0)
        
        return dialogue

    def update_npc_mood(self, npc_id, mood_change):
        """
        更新NPC的心情\n
        \n
        參數:\n
        npc_id (int): NPC ID\n
        mood_change (int): 心情變化值 (-100 到 100)\n
        """
        if npc_id in self.npc_profiles:
            profile = self.npc_profiles[npc_id]
            profile["mood"] = max(0, min(100, profile["mood"] + mood_change))

    def get_npc_profile(self, npc_id):
        """
        獲取NPC的完整檔案\n
        \n
        參數:\n
        npc_id (int): NPC ID\n
        \n
        回傳:\n
        dict: NPC檔案，如果不存在則返回None\n
        """
        return self.npc_profiles.get(npc_id)

    def get_personality_statistics(self):
        """
        獲取性格分佈統計\n
        \n
        回傳:\n
        dict: 性格分佈統計\n
        """
        stats = {}
        for personality_type in PersonalityType:
            count = sum(1 for profile in self.npc_profiles.values() 
                       if profile["personality_type"] == personality_type)
            stats[personality_type.value] = count
        
        return stats


# 導入時間模組用於對話歷史記錄
import time