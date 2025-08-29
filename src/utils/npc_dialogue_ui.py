######################載入套件######################
import pygame
import random
from src.utils.font_manager import get_font_manager
from config.settings import *


######################NPC對話UI系統######################
class NPCDialogueUI:
    """
    NPC對話UI系統 - 處理與NPC的對話互動\n
    \n
    功能:\n
    1. 顯示NPC對話視窗\n
    2. 根據NPC性格產生不同對話內容\n
    3. 支援多選項對話\n
    4. 即時響應，左鍵點擊NPC立即顯示\n
    """

    def __init__(self):
        """
        初始化NPC對話UI\n
        """
        self.font_manager = get_font_manager()
        self.is_visible = False
        self.current_npc = None
        self.dialogue_lines = []
        self.current_line_index = 0
        
        # UI設定
        self.dialogue_width = 600
        self.dialogue_height = 200
        self.dialogue_x = (SCREEN_WIDTH - self.dialogue_width) // 2
        self.dialogue_y = SCREEN_HEIGHT - self.dialogue_height - 50
        
        # 顏色設定
        self.bg_color = (40, 40, 40, 240)  # 半透明深灰
        self.border_color = (200, 200, 200)
        self.text_color = (255, 255, 255)
        self.name_color = (100, 200, 255)
        self.button_color = (60, 60, 60)
        self.button_hover_color = (80, 80, 80)
        
        # 按鈕設定
        self.next_button_rect = None
        self.close_button_rect = None
        self.is_mouse_over_next = False
        self.is_mouse_over_close = False
        
        # 對話選項設定
        self.dialogue_options = []
        self.selected_option = 0
        
        print("NPC對話UI系統初始化完成")

    def show_dialogue(self, npc):
        """
        顯示與NPC的對話\n
        \n
        參數:\n
        npc (NPC): 要對話的NPC物件\n
        """
        self.current_npc = npc
        self.is_visible = True
        self.current_line_index = 0
        
        # 根據NPC性格和職業生成對話內容
        self.dialogue_lines = self._generate_dialogue_for_npc(npc)
        
        # 生成對話選項
        self.dialogue_options = self._generate_dialogue_options(npc)
        self.selected_option = 0
        
        print(f"開始與 {npc.name} 對話")

    def hide_dialogue(self):
        """
        隱藏對話視窗\n
        """
        self.is_visible = False
        self.current_npc = None
        self.dialogue_lines = []
        self.dialogue_options = []
        self.current_line_index = 0
        print("對話結束")

    def _generate_dialogue_for_npc(self, npc):
        """
        根據NPC特性生成對話內容\n
        \n
        參數:\n
        npc (NPC): NPC物件\n
        \n
        回傳:\n
        list: 對話內容列表\n
        """
        # 基礎問候語
        greetings = [
            f"你好！我是{npc.name}。",
            f"嗨！很高興見到你！",
            f"哈囉！我是這裡的{npc.profession.value}。"
        ]
        
        # 根據職業生成特定對話
        profession_dialogues = {
            "農夫": [
                "今年的收成還不錯呢！",
                "農田需要細心照料才能有好收成。",
                "你有興趣學習農業嗎？"
            ],
            "醫生": [
                "記得要保持身體健康喔！",
                "有任何身體不適都可以來醫院。",
                "預防勝於治療，這是我常說的話。"
            ],
            "牧師": [
                "願上帝保佑你平安。",
                "教堂隨時歡迎你來祈禱。",
                "內心的平靜比什麼都重要。"
            ],
            "獵人": [
                "森林裡要小心野生動物。",
                "狩獵需要技巧和耐心。",
                "我知道哪裡能找到最好的獵物。"
            ],
            "槍械店員工": [
                "需要什麼武器裝備嗎？",
                "安全使用武器很重要。",
                "我們有最好的狩獵裝備。"
            ],
            "便利商店員工": [
                "歡迎光臨！需要什麼嗎？",
                "我們有新鮮的食物和飲料。",
                "買點東西補充體力吧！"
            ],
            "電力工人": [
                "我負責維護這個區域的電力。",
                "電力系統需要定期檢查。",
                "停電的話記得通知我！"
            ]
        }
        
        # 根據當前狀態添加額外對話
        status_dialogues = []
        if hasattr(npc, 'is_workday') and not npc.is_workday:
            status_dialogues.extend([
                "今天是休息日，所以我在到處走走。",
                "平常工作很忙，難得可以放鬆一下。"
            ])
        
        if hasattr(npc, 'state'):
            if npc.state.value == "工作中":
                status_dialogues.extend([
                    "現在是工作時間，不能聊太久。",
                    "工作很充實，我很喜歡我的職業。"
                ])
            elif npc.state.value == "休息中":
                status_dialogues.extend([
                    "正在休息中，有什麼可以幫你的嗎？",
                    "休息時間總是過得特別快。"
                ])
        
        # 組合對話內容
        dialogue = []
        dialogue.append(random.choice(greetings))
        
        profession_name = npc.profession.value
        if profession_name in profession_dialogues:
            dialogue.extend(random.sample(profession_dialogues[profession_name], min(2, len(profession_dialogues[profession_name]))))
        
        if status_dialogues:
            dialogue.append(random.choice(status_dialogues))
        
        # 添加結尾
        endings = [
            "有什麼需要幫忙的嗎？",
            "希望你在小鎮玩得愉快！",
            "有時間再來聊聊吧！"
        ]
        dialogue.append(random.choice(endings))
        
        return dialogue

    def _generate_dialogue_options(self, npc):
        """
        生成對話選項\n
        \n
        參數:\n
        npc (NPC): NPC物件\n
        \n
        回傳:\n
        list: 對話選項列表\n
        """
        options = [
            {
                "text": "告訴我更多關於你的工作",
                "response": self._get_work_response(npc)
            },
            {
                "text": "小鎮有什麼有趣的地方嗎？",
                "response": "這個小鎮有很多有趣的地方！森林裡有野生動物，公園有新鮮蔬果，還有各種商店。"
            },
            {
                "text": "最近過得如何？",
                "response": self._get_personal_response(npc)
            },
            {
                "text": "再見",
                "response": "再見！祝你有美好的一天！",
                "action": "close"
            }
        ]
        
        return options

    def _get_work_response(self, npc):
        """
        獲取工作相關回應\n
        \n
        參數:\n
        npc (NPC): NPC物件\n
        \n
        回傳:\n
        str: 工作回應\n
        """
        work_responses = {
            "農夫": "我每天都在照顧農田，種植各種蔬菜水果。雖然辛苦，但看到作物成長很有成就感！",
            "醫生": "我的工作是照顧大家的健康。雖然有時候很忙，但能幫助別人康復讓我很滿足。",
            "牧師": "我在教堂主持禮拜，為信徒祈禱。宗教能給人們心靈上的慰藉和指導。",
            "獵人": "我在森林裡狩獵，也保護小鎮免受危險動物威脅。這需要很好的技巧和膽量。",
            "槍械店員工": "我在槍械店工作，為獵人和需要自衛的人提供武器。安全是我們最重視的。",
            "便利商店員工": "我在便利商店服務顧客，提供日常用品和食物。顧客的笑容是我最大的動力。",
            "電力工人": "我負責維護電力系統，確保大家都有電可用。雖然有時會發生意外，但這很重要。"
        }
        
        profession_name = npc.profession.value
        return work_responses.get(profession_name, "我的工作很有意義，每天都充滿挑戰！")

    def _get_personal_response(self, npc):
        """
        獲取個人狀況回應\n
        \n
        參數:\n
        npc (NPC): NPC物件\n
        \n
        回傳:\n
        str: 個人回應\n
        """
        if hasattr(npc, 'is_injured') and npc.is_injured:
            return "最近受了傷，正在康復中。謝謝你的關心！"
        
        personal_responses = [
            "最近過得很好！工作順利，生活也很充實。",
            "還不錯，雖然有時候會有點忙碌，但我很享受我的生活。",
            "很好！這個小鎮的人都很友善，我很喜歡這裡。",
            "過得很平靜，這就是我想要的生活方式。"
        ]
        
        return random.choice(personal_responses)

    def handle_click(self, mouse_pos):
        """
        處理滑鼠點擊事件\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠位置\n
        \n
        回傳:\n
        bool: 是否處理了點擊\n
        """
        if not self.is_visible:
            return False
        
        # 檢查是否點擊下一個按鈕
        if self.next_button_rect and self.next_button_rect.collidepoint(mouse_pos):
            self._next_dialogue_line()
            return True
        
        # 檢查是否點擊關閉按鈕
        if self.close_button_rect and self.close_button_rect.collidepoint(mouse_pos):
            self.hide_dialogue()
            return True
        
        # 檢查是否點擊對話選項
        option_y = self.dialogue_y + 120
        for i, option in enumerate(self.dialogue_options):
            option_rect = pygame.Rect(
                self.dialogue_x + 20,
                option_y + i * 20,
                self.dialogue_width - 40,
                18
            )
            
            if option_rect.collidepoint(mouse_pos):
                self._select_dialogue_option(i)
                return True
        
        # 檢查是否點擊在對話框外部
        dialogue_rect = pygame.Rect(
            self.dialogue_x, self.dialogue_y,
            self.dialogue_width, self.dialogue_height
        )
        
        if not dialogue_rect.collidepoint(mouse_pos):
            self.hide_dialogue()
            return True
        
        return True  # 阻止點擊穿透

    def handle_mouse_move(self, mouse_pos):
        """
        處理滑鼠移動事件\n
        \n
        參數:\n
        mouse_pos (tuple): 滑鼠位置\n
        """
        if not self.is_visible:
            return
        
        # 檢查滑鼠是否懸停在按鈕上
        self.is_mouse_over_next = (self.next_button_rect and 
                                  self.next_button_rect.collidepoint(mouse_pos))
        self.is_mouse_over_close = (self.close_button_rect and 
                                   self.close_button_rect.collidepoint(mouse_pos))

    def _next_dialogue_line(self):
        """
        顯示下一行對話\n
        """
        if self.current_line_index < len(self.dialogue_lines) - 1:
            self.current_line_index += 1
        else:
            # 對話結束，顯示選項
            pass

    def _select_dialogue_option(self, option_index):
        """
        選擇對話選項\n
        \n
        參數:\n
        option_index (int): 選項索引\n
        """
        if 0 <= option_index < len(self.dialogue_options):
            selected_option = self.dialogue_options[option_index]
            
            # 顯示回應
            self.dialogue_lines = [selected_option["response"]]
            self.current_line_index = 0
            
            # 檢查是否有特殊動作
            if selected_option.get("action") == "close":
                # 延遲關閉對話
                pygame.time.set_timer(pygame.USEREVENT + 1, 2000)  # 2秒後關閉

    def handle_key_input(self, event):
        """
        處理鍵盤輸入\n
        \n
        參數:\n
        event (pygame.event.Event): 鍵盤事件\n
        \n
        回傳:\n
        bool: 是否處理了輸入\n
        """
        if not self.is_visible:
            return False
        
        if event.key == pygame.K_ESCAPE:
            self.hide_dialogue()
            return True
        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            self._next_dialogue_line()
            return True
        elif event.key == pygame.K_UP:
            self.selected_option = max(0, self.selected_option - 1)
            return True
        elif event.key == pygame.K_DOWN:
            self.selected_option = min(len(self.dialogue_options) - 1, self.selected_option + 1)
            return True
        
        return False

    def draw(self, screen):
        """
        繪製對話UI\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        if not self.is_visible or not self.current_npc:
            return
        
        # 繪製半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 繪製對話框背景
        dialogue_surface = pygame.Surface(
            (self.dialogue_width, self.dialogue_height), 
            pygame.SRCALPHA
        )
        dialogue_surface.fill(self.bg_color)
        screen.blit(dialogue_surface, (self.dialogue_x, self.dialogue_y))
        
        # 繪製邊框
        pygame.draw.rect(
            screen, self.border_color,
            (self.dialogue_x, self.dialogue_y, self.dialogue_width, self.dialogue_height),
            3
        )
        
        # 繪製NPC名稱
        name_font = self.font_manager.get_font(20)
        name_text = f"{self.current_npc.name} ({self.current_npc.profession.value})"
        name_surface = name_font.render(name_text, True, self.name_color)
        screen.blit(name_surface, (self.dialogue_x + 20, self.dialogue_y + 15))
        
        # 繪製對話內容
        content_y = self.dialogue_y + 50
        if self.current_line_index < len(self.dialogue_lines):
            content_font = self.font_manager.get_font(16)
            current_line = self.dialogue_lines[self.current_line_index]
            
            # 自動換行處理
            words = current_line.split(' ')
            lines = []
            current_line_text = ""
            
            for word in words:
                test_line = current_line_text + word + " "
                text_width = content_font.size(test_line)[0]
                
                if text_width > self.dialogue_width - 40:
                    if current_line_text:
                        lines.append(current_line_text.strip())
                        current_line_text = word + " "
                    else:
                        lines.append(word)
                        current_line_text = ""
                else:
                    current_line_text = test_line
            
            if current_line_text:
                lines.append(current_line_text.strip())
            
            # 繪製文字行
            for i, line in enumerate(lines):
                line_surface = content_font.render(line, True, self.text_color)
                screen.blit(line_surface, (self.dialogue_x + 20, content_y + i * 20))
        
        # 繪製對話選項
        if self.current_line_index >= len(self.dialogue_lines) - 1:
            self._draw_dialogue_options(screen)
        
        # 繪製控制提示
        self._draw_controls_hint(screen)

    def _draw_dialogue_options(self, screen):
        """
        繪製對話選項\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        option_font = self.font_manager.get_font(14)
        option_y = self.dialogue_y + 120
        
        for i, option in enumerate(self.dialogue_options):
            # 選項背景
            if i == self.selected_option:
                option_bg = pygame.Surface(
                    (self.dialogue_width - 40, 18), 
                    pygame.SRCALPHA
                )
                option_bg.fill((100, 100, 100, 100))
                screen.blit(option_bg, (self.dialogue_x + 20, option_y + i * 20))
            
            # 選項文字
            option_text = f"► {option['text']}"
            option_surface = option_font.render(option_text, True, self.text_color)
            screen.blit(option_surface, (self.dialogue_x + 25, option_y + i * 20))

    def _draw_controls_hint(self, screen):
        """
        繪製控制提示\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製目標表面\n
        """
        hint_font = self.font_manager.get_font(12)
        hint_text = "點擊選項或按ESC關閉"
        hint_surface = hint_font.render(hint_text, True, (180, 180, 180))
        hint_x = self.dialogue_x + self.dialogue_width - hint_surface.get_width() - 10
        hint_y = self.dialogue_y + self.dialogue_height - 20
        screen.blit(hint_surface, (hint_x, hint_y))