######################載入套件######################
import pygame
import random
import time
from config.settings import *


######################釣魚系統######################
class FishingSystem:
    """
    釣魚系統 - 管理釣魚互動和魚類資源\n
    \n
    實現釣魚互動規則：\n
    1. 玩家站在水邊、裝備釣竿，對湖面按左鍵開始「釣魚動作」\n
    2. 開始後在 1.0 秒內顯示訊息：「釣到了！」\n
    3. 如果在 1.0 秒內接續於 0.5 秒內按右鍵，則判定為成功釣到魚\n
    4. 成功後顯示魚的品種、稀有度和金錢獎勵\n
    5. 若未在指定時間內按右鍵，則顯示「魚跑掉了！」\n
    6. 無論成功或失敗，釣魚流程結束後可立即開始下一輪\n
    """

    def __init__(self):
        """
        初始化釣魚系統\n
        """
        # 釣魚狀態
        self.is_fishing = False
        self.fishing_start_time = 0
        self.bite_start_time = 0
        self.has_bite = False
        self.fishing_complete = False
        
        # 釣到魚後的選擇系統
        self.caught_fish_data = None  # 當前釣到的魚的資料
        self.show_fish_choice = False  # 是否顯示選擇介面
        self.choice_start_time = 0  # 選擇介面開始時間
        self.choice_duration = 3.0  # 選擇介面持續時間（秒）
        
        # 釣魚計時設定
        self.bite_wait_time = 1.0  # 等待魚咬鉤的時間（秒）
        self.catch_window_time = 0.5  # 成功釣魚的時間窗口（秒）
        
        # 魚類資料庫
        self.fish_database = [
            {
                "name": "小丑魚",
                "rarity": "普通",
                "rarity_level": 1,
                "base_reward": 50,
                "color": (255, 165, 0)  # 橘色
            },
            {
                "name": "草魚",
                "rarity": "普通", 
                "rarity_level": 1,
                "base_reward": 60,
                "color": (34, 139, 34)  # 綠色
            },
            {
                "name": "鯉魚",
                "rarity": "常見",
                "rarity_level": 2,
                "base_reward": 120,
                "color": (255, 20, 147)  # 深粉色
            },
            {
                "name": "鱸魚",
                "rarity": "稀有",
                "rarity_level": 3,
                "base_reward": 250,
                "color": (0, 191, 255)  # 深藍色
            },
            {
                "name": "虹鱒",
                "rarity": "稀有",
                "rarity_level": 3,
                "base_reward": 280,
                "color": (138, 43, 226)  # 藍紫色
            },
            {
                "name": "金魚王",
                "rarity": "傳說",
                "rarity_level": 4,
                "base_reward": 500,
                "color": (255, 215, 0)  # 金色
            },
            {
                "name": "龍魚",
                "rarity": "神話",
                "rarity_level": 5,
                "base_reward": 1000,
                "color": (220, 20, 60)  # 深紅色
            }
        ]
        
        # 稀有度機率分配
        self.rarity_probabilities = {
            1: 0.50,  # 普通 - 50%
            2: 0.30,  # 常見 - 30%
            3: 0.15,  # 稀有 - 15%
            4: 0.04,  # 傳說 - 4%
            5: 0.01   # 神話 - 1%
        }
        
        print("釣魚系統初始化完成")

    def start_fishing(self, player, world_x, world_y, terrain_system):
        """
        開始釣魚動作\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        world_x (float): 點擊的世界座標 X\n
        world_y (float): 點擊的世界座標 Y\n
        terrain_system (TerrainBasedSystem): 地形系統\n
        \n
        回傳:\n
        dict: 釣魚開始結果\n
        """
        # 檢查是否已在釣魚中
        if self.is_fishing:
            return {"success": False, "message": "已經在釣魚中！"}
        
        # 檢查玩家是否裝備釣竿
        current_equipment = player.get_current_equipment()
        if not current_equipment or current_equipment["name"] != "釣竿":
            return {"success": False, "message": "需要裝備釣竿才能釣魚！"}
        
        # 檢查點擊位置是否為水域
        if not terrain_system.check_water_collision(world_x, world_y):
            return {"success": False, "message": "需要在水邊才能釣魚！"}
        
        # 檢查玩家是否在水邊（不能站在水裡）
        player_pos = player.get_center_position()
        if terrain_system.check_water_collision(player_pos[0], player_pos[1]):
            return {"success": False, "message": "不能站在水裡釣魚！"}
        
        # 檢查玩家與水域的距離
        distance = self._calculate_distance(player_pos, (world_x, world_y))
        if distance > 50:  # 最大釣魚距離
            return {"success": False, "message": "距離水域太遠，無法釣魚！"}
        
        # 開始釣魚
        self.is_fishing = True
        self.fishing_start_time = time.time()
        self.has_bite = False
        self.fishing_complete = False
        
        print("🎣 開始釣魚...")
        return {"success": True, "message": "開始釣魚..."}

    def update(self, dt):
        """
        更新釣魚狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        \n
        回傳:\n
        dict: 釣魚狀態更新資訊\n
        """
        if not self.is_fishing and not self.show_fish_choice:
            return None
        
        current_time = time.time()
        
        # 如果正在顯示選擇介面
        if self.show_fish_choice:
            elapsed_choice_time = current_time - self.choice_start_time
            if elapsed_choice_time >= self.choice_duration:
                # 選擇時間結束，自動選擇放生
                result = self.release_fish_auto()
                return result
            return {"event": "showing_choice", "fish": self.caught_fish_data}
        
        # 正常釣魚流程
        elapsed_time = current_time - self.fishing_start_time
        
        # 檢查是否到了魚咬鉤的時間
        if not self.has_bite and elapsed_time >= self.bite_wait_time:
            self.has_bite = True
            self.bite_start_time = current_time
            print("🐟 釣到了！快按右鍵！")
            return {"event": "bite", "message": "釣到了！"}
        
        # 檢查釣魚時間窗口是否結束
        if self.has_bite:
            bite_elapsed = current_time - self.bite_start_time
            if bite_elapsed >= self.catch_window_time and not self.fishing_complete:
                # 時間窗口結束，魚跑掉了
                result = self._fishing_failed()
                return result
        
        return None

    def try_catch_fish(self, player):
        """
        嘗試釣到魚（右鍵操作）\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 釣魚結果\n
        """
        if not self.is_fishing:
            return {"success": False, "message": "目前沒有在釣魚！"}
        
        if not self.has_bite:
            return {"success": False, "message": "魚還沒咬鉤，等等再試！"}
        
        if self.fishing_complete:
            return {"success": False, "message": "釣魚已結束！"}
        
        # 檢查是否在有效時間窗口內
        current_time = time.time()
        bite_elapsed = current_time - self.bite_start_time
        
        if bite_elapsed <= self.catch_window_time:
            # 成功釣到魚
            result = self._fishing_success(player)
            return result
        else:
            # 時間窗口已過，魚跑掉了
            result = self._fishing_failed()
            return result

    def _fishing_success(self, player):
        """
        釣魚成功處理 - 顯示選擇介面\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 成功結果\n
        """
        # 使用魚餌
        if not player.use_bait():
            print("⚠️ 魚餌不足！")
        
        # 隨機選擇魚類，考慮魚餌效果
        caught_fish = self._select_random_fish(player.get_bait_multiplier())
        
        # 儲存釣到的魚的資料
        self.caught_fish_data = caught_fish
        
        # 顯示選擇介面
        self.show_fish_choice = True
        self.choice_start_time = time.time()
        
        # 重置釣魚狀態
        self.is_fishing = False
        self.fishing_complete = True
        
        message = f"🎣 釣到了 {caught_fish['name']}！\n稀有度：{caught_fish['rarity']}\n請選擇：放生 或 賣掉"
        print(message)
        
        return {
            "success": True,
            "event": "catch_success",
            "message": "釣到了魚！請做選擇",
            "fish": caught_fish,
            "choice_time_left": self.choice_duration
        }

    def release_fish(self, player):
        """
        放生魚類 - 獲得血量加成\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 放生結果\n
        """
        if not self.show_fish_choice or not self.caught_fish_data:
            return {"success": False, "message": "沒有魚可以放生"}
        
        fish = self.caught_fish_data
        
        # 給予血量加成
        health_gained = player.release_fish_for_health()
        
        # 重置狀態
        self._reset_all_states()
        
        message = f"🐟 放生了 {fish['name']}\n血量增加: {health_gained}\n當前血量: {player.health}"
        print(message)
        
        return {
            "success": True,
            "action": "release",
            "fish": fish,
            "health_gained": health_gained,
            "message": message
        }

    def sell_fish(self, player):
        """
        賣掉魚類 - 獲得金錢\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        dict: 賣魚結果\n
        """
        if not self.show_fish_choice or not self.caught_fish_data:
            return {"success": False, "message": "沒有魚可以賣"}
        
        fish = self.caught_fish_data
        
        # 計算售價（使用魚餌倍數影響價格）
        base_reward = fish["base_reward"]
        bait_multiplier = player.get_bait_multiplier()
        final_price = int(base_reward * bait_multiplier)
        
        # 給予金錢
        player.add_money(final_price)
        
        # 重置狀態
        self._reset_all_states()
        
        message = f"💰 賣掉了 {fish['name']}\n獲得金錢: ${final_price}\n當前金錢: ${player.get_money()}"
        print(message)
        
        return {
            "success": True,
            "action": "sell",
            "fish": fish,
            "money_gained": final_price,
            "message": message
        }

    def release_fish_auto(self):
        """
        自動放生（時間到時）\n
        \n
        回傳:\n
        dict: 自動放生結果\n
        """
        if not self.show_fish_choice or not self.caught_fish_data:
            return {"success": False, "message": "沒有魚需要處理"}
        
        fish = self.caught_fish_data
        
        # 重置狀態
        self._reset_all_states()
        
        message = f"⏰ 時間到！自動放生了 {fish['name']}"
        print(message)
        
        return {
            "success": True,
            "action": "auto_release",
            "fish": fish,
            "message": message
        }

    def _reset_all_states(self):
        """
        重置所有釣魚相關狀態\n
        """
        self._reset_fishing_state()
        self.show_fish_choice = False
        self.caught_fish_data = None
        self.choice_start_time = 0

    def _fishing_failed(self):
        """
        釣魚失敗處理\n
        \n
        回傳:\n
        dict: 失敗結果\n
        """
        # 重置釣魚狀態
        self._reset_fishing_state()
        
        print("🐟 魚跑掉了！")
        
        return {
            "success": False,
            "event": "catch_failed", 
            "message": "魚跑掉了！"
        }

    def _reset_fishing_state(self):
        """
        重置釣魚狀態\n
        """
        self.is_fishing = False
        self.fishing_start_time = 0
        self.bite_start_time = 0
        self.has_bite = False
        self.fishing_complete = True

    def _select_random_fish(self, bait_multiplier=1.0):
        """
        隨機選擇魚類，考慮魚餌效果\n
        \n
        參數:\n
        bait_multiplier (float): 魚餌效果倍數\n
        \n
        回傳:\n
        dict: 選中的魚類資訊\n
        """
        # 根據魚餌倍數調整稀有度機率
        adjusted_probabilities = {}
        total_prob = 0
        
        for rarity_level, base_prob in self.rarity_probabilities.items():
            # 高級魚餌增加稀有魚類的機率
            if bait_multiplier > 1.0:
                if rarity_level >= 3:  # 稀有以上
                    adjusted_prob = base_prob * (1 + (bait_multiplier - 1) * 0.5)
                else:  # 普通和常見
                    adjusted_prob = base_prob * (1 - (bait_multiplier - 1) * 0.2)
            else:
                adjusted_prob = base_prob
            
            adjusted_probabilities[rarity_level] = max(0.01, adjusted_prob)  # 確保最小機率
            total_prob += adjusted_probabilities[rarity_level]
        
        # 正規化機率
        for rarity_level in adjusted_probabilities:
            adjusted_probabilities[rarity_level] /= total_prob
        
        # 根據調整後的機率選擇稀有度
        rand = random.random()
        cumulative_prob = 0
        selected_rarity = 1
        
        for rarity_level, prob in adjusted_probabilities.items():
            cumulative_prob += prob
            if rand <= cumulative_prob:
                selected_rarity = rarity_level
                break
        
        # 從選定稀有度中隨機選擇魚類
        available_fish = [fish for fish in self.fish_database if fish["rarity_level"] == selected_rarity]
        if available_fish:
            return random.choice(available_fish)
        
        # 後備選項：返回最普通的魚
        return self.fish_database[0]

    def _calculate_reward(self, fish):
        """
        計算釣魚獎勵金錢\n
        \n
        參數:\n
        fish (dict): 魚類資訊\n
        \n
        回傳:\n
        int: 獎勵金錢\n
        """
        base_reward = fish["base_reward"]
        rarity_multiplier = fish["rarity_level"]
        
        # 基礎獎勵 * 稀有度倍數 + 隨機波動
        random_bonus = random.randint(-10, 20)  # -10% 到 +20% 的隨機波動
        
        total_reward = int(base_reward * rarity_multiplier * (1 + random_bonus / 100))
        return max(total_reward, base_reward // 2)  # 確保最低獎勵

    def _calculate_distance(self, pos1, pos2):
        """
        計算兩點間距離\n
        \n
        參數:\n
        pos1 (tuple): 位置1 (x, y)\n
        pos2 (tuple): 位置2 (x, y)\n
        \n
        回傳:\n
        float: 距離\n
        """
        x1, y1 = pos1
        x2, y2 = pos2
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def cancel_fishing(self):
        """
        取消釣魚\n
        """
        if self.is_fishing:
            self._reset_fishing_state()
            print("取消釣魚")
            return {"success": True, "message": "取消釣魚"}
        return {"success": False, "message": "目前沒有在釣魚"}

    def is_fishing_active(self):
        """
        檢查是否正在釣魚\n
        \n
        回傳:\n
        bool: 是否正在釣魚\n
        """
        return self.is_fishing

    def get_fishing_status(self):
        """
        獲取釣魚狀態資訊\n
        \n
        回傳:\n
        dict: 釣魚狀態\n
        """
        if not self.is_fishing:
            return {"active": False}
        
        current_time = time.time()
        elapsed_time = current_time - self.fishing_start_time
        
        status = {
            "active": True,
            "elapsed_time": elapsed_time,
            "has_bite": self.has_bite,
            "waiting_for_bite": not self.has_bite and elapsed_time < self.bite_wait_time
        }
        
        if self.has_bite:
            bite_elapsed = current_time - self.bite_start_time
            status["bite_elapsed"] = bite_elapsed
            status["time_remaining"] = max(0, self.catch_window_time - bite_elapsed)
        
        return status