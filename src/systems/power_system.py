######################載入套件######################
from enum import Enum
from typing import Dict, List, Tuple, Optional, Callable
import pygame

from ..utils.helpers import calculate_distance

######################電力相關常數######################
from config.settings import (
    POWER_PLANT_COUNT,
    POWER_WORKER_COUNT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)


######################電力狀態列舉######################
class PowerStatus(Enum):
    """
    電力狀態列舉 - 定義電力系統的各種狀態\n
    """

    NORMAL = "正常供電"
    OUTAGE = "停電"
    MAINTENANCE = "維修中"
    OVERLOAD = "超載"


######################電力管理器######################
class PowerManager:
    """
    電力系統管理器 - 統一管理全市電力供應與分配\n
    \n
    功能說明:\n
    1. 管理 30 個電力區域的電力狀態\n
    2. 追蹤電力工人的工作狀態與區域分配\n
    3. 處理停電機制與影響範圍\n
    4. 提供電力狀態查詢與更新介面\n
    5. 整合時間系統，影響電力需求與供應\n
    \n
    設計原則:\n
    - 每個區域分配一名電力工人\n
    - 工人住院或離線時該區域停電\n
    - 支援回調機制通知電力狀態變化\n
    - 與建築系統整合，影響設施運作\n
    """

    def __init__(self, time_manager=None):
        """
        初始化電力管理器\n
        \n
        參數:\n
        time_manager (TimeManager): 時間管理器，用於同步電力系統與遊戲時間\n
        """
        # 時間系統整合
        self.time_manager = time_manager

        # 電力區域管理
        self.power_areas = {}  # {area_id: area_info}
        self.total_areas = 30  # 總共 30 個電力區域

        # 電力工人管理
        self.power_workers = {}  # {worker_id: worker_info}
        self.worker_to_area = {}  # {worker_id: area_id} 工人與區域對應
        self.area_to_worker = {}  # {area_id: worker_id} 區域與工人對應

        # 電力狀態追蹤
        self.global_power_status = PowerStatus.NORMAL
        self.power_demand = 0.0  # 當前電力需求 (0.0-1.0)
        self.power_supply = 1.0  # 當前電力供應 (0.0-1.0)

        # 回調機制
        self.power_change_callbacks = []  # 電力狀態變化回調
        self.outage_callbacks = []  # 停電事件回調

        # 統計資料
        self.stats = {
            "total_outages": 0,
            "areas_with_power": 30,
            "workers_on_duty": 0,
            "power_efficiency": 1.0,
        }

        print("電力管理器初始化完成")

    def initialize_power_grid(self, town_bounds: Tuple[int, int, int, int]):
        """
        初始化電力網格系統 - 劃分 30 個電力區域\n
        \n
        將小鎮劃分為 6x5 的網格，每個區域分配唯一 ID\n
        建立區域邊界、中心點、電力狀態等基礎資訊\n
        \n
        參數:\n
        town_bounds (tuple): 小鎮邊界 (x, y, width, height)\n
        """
        town_x, town_y, town_width, town_height = town_bounds

        # 計算每個區域的尺寸
        area_width = town_width // 6  # 6列
        area_height = town_height // 5  # 5行

        area_count = 0

        # 創建 6x5 的電力區域網格
        for row in range(5):
            for col in range(6):
                area_id = row * 6 + col + 1  # 區域 ID 從 1 開始

                # 計算區域中心點
                center_x = town_x + col * area_width + area_width // 2
                center_y = town_y + row * area_height + area_height // 2

                # 計算區域邊界
                bounds = (
                    town_x + col * area_width,
                    town_y + row * area_height,
                    area_width,
                    area_height,
                )

                # 建立區域資訊
                area_info = {
                    "id": area_id,
                    "row": row,
                    "col": col,
                    "center": (center_x, center_y),
                    "bounds": bounds,
                    "status": PowerStatus.NORMAL,
                    "assigned_worker": None,
                    "buildings": [],  # 該區域內的建築物列表
                    "power_demand": 0.0,  # 區域電力需求
                    "last_outage": None,  # 上次停電時間
                    "outage_duration": 0,  # 停電持續時間
                }

                self.power_areas[area_id] = area_info
                area_count += 1

        print(f"電力網格初始化完成：創建了 {area_count} 個電力區域")
        self._update_stats()

    def register_power_worker(self, worker_id: str, worker_info: dict):
        """
        註冊電力工人到電力系統\n
        \n
        將電力工人加入系統管理，分配負責區域\n
        建立工人與區域的雙向對應關係\n
        \n
        參數:\n
        worker_id (str): 工人唯一識別碼\n
        worker_info (dict): 工人資訊 (包含 NPC 物件、技能等級等)\n
        """
        if worker_id in self.power_workers:
            print(f"警告：電力工人 {worker_id} 已經註冊過")
            return

        # 註冊工人資訊
        self.power_workers[worker_id] = {
            "id": worker_id,
            "npc": worker_info.get("npc"),
            "skill_level": worker_info.get("skill_level", 1),
            "on_duty": True,
            "assigned_area": None,
            "work_efficiency": 1.0,
        }

        # 自動分配可用區域
        assigned_area = self._assign_area_to_worker(worker_id)

        if assigned_area:
            print(f"電力工人 {worker_id} 已註冊並分配到區域 {assigned_area}")
        else:
            print(f"電力工人 {worker_id} 已註冊，但無可用區域分配")

        self._update_stats()

    def _assign_area_to_worker(self, worker_id: str) -> Optional[int]:
        """
        為電力工人分配負責區域\n
        \n
        找到尚未分配工人的區域，建立工人與區域的對應關係\n
        優先分配給電力需求高或曾經停電的區域\n
        \n
        參數:\n
        worker_id (str): 工人 ID\n
        \n
        回傳:\n
        int: 分配的區域 ID，如果無可用區域則回傳 None\n
        """
        # 找出未分配工人的區域
        available_areas = [
            area_id
            for area_id, area_info in self.power_areas.items()
            if area_info["assigned_worker"] is None
        ]

        if not available_areas:
            return None

        # 優先分配給停電的區域
        priority_areas = [
            area_id
            for area_id in available_areas
            if self.power_areas[area_id]["status"] == PowerStatus.OUTAGE
        ]

        if priority_areas:
            selected_area = priority_areas[0]
        else:
            # 按 ID 順序分配
            selected_area = min(available_areas)

        # 建立雙向對應關係
        self.worker_to_area[worker_id] = selected_area
        self.area_to_worker[selected_area] = worker_id

        # 更新區域和工人資訊
        self.power_areas[selected_area]["assigned_worker"] = worker_id
        self.power_workers[worker_id]["assigned_area"] = selected_area

        # 如果區域原本停電，現在有工人了就恢復供電
        if self.power_areas[selected_area]["status"] == PowerStatus.OUTAGE:
            self._restore_power_to_area(selected_area)

        return selected_area

    def update_worker_status(self, worker_id: str, is_available: bool):
        """
        更新電力工人的工作狀態\n
        \n
        當工人住院、休假或重返工作時更新狀態\n
        自動處理因工人狀態變化導致的停電或復電\n
        \n
        參數:\n
        worker_id (str): 工人 ID\n
        is_available (bool): 是否可以工作 (False 表示住院、休假等)\n
        """
        if worker_id not in self.power_workers:
            print(f"警告：找不到電力工人 {worker_id}")
            return

        worker_info = self.power_workers[worker_id]
        old_status = worker_info["on_duty"]
        worker_info["on_duty"] = is_available

        assigned_area = worker_info["assigned_area"]

        if assigned_area:
            if is_available and not old_status:
                # 工人復工，恢復供電
                print(f"電力工人 {worker_id} 復工，區域 {assigned_area} 恢復供電")
                self._restore_power_to_area(assigned_area)

            elif not is_available and old_status:
                # 工人離線，該區域停電
                print(f"電力工人 {worker_id} 離線，區域 {assigned_area} 停電")
                self._trigger_power_outage(assigned_area, f"工人 {worker_id} 住院")

        self._update_stats()

    def _trigger_power_outage(self, area_id: int, reason: str = ""):
        """
        觸發區域停電\n
        \n
        將指定區域設為停電狀態，通知相關系統\n
        更新統計資料，觸發停電回調\n
        \n
        參數:\n
        area_id (int): 區域 ID\n
        reason (str): 停電原因\n
        """
        if area_id not in self.power_areas:
            return

        area_info = self.power_areas[area_id]

        if area_info["status"] != PowerStatus.OUTAGE:
            area_info["status"] = PowerStatus.OUTAGE
            area_info["last_outage"] = (
                self.time_manager.get_time_string() if self.time_manager else "未知時間"
            )
            area_info["outage_duration"] = 0

            self.stats["total_outages"] += 1

            print(f"區域 {area_id} 停電 - 原因：{reason}")

            # 觸發停電回調
            for callback in self.outage_callbacks:
                try:
                    callback(area_id, PowerStatus.OUTAGE, reason)
                except Exception as e:
                    print(f"停電回調執行失敗：{e}")

            self._update_stats()

    def _restore_power_to_area(self, area_id: int):
        """
        恢復區域供電\n
        \n
        將指定區域電力狀態恢復正常\n
        更新統計資料，觸發供電恢復回調\n
        \n
        參數:\n
        area_id (int): 區域 ID\n
        """
        if area_id not in self.power_areas:
            return

        area_info = self.power_areas[area_id]

        if area_info["status"] == PowerStatus.OUTAGE:
            area_info["status"] = PowerStatus.NORMAL

            print(f"區域 {area_id} 供電恢復")

            # 觸發供電恢復回調
            for callback in self.power_change_callbacks:
                try:
                    callback(area_id, PowerStatus.NORMAL, "供電恢復")
                except Exception as e:
                    print(f"供電恢復回調執行失敗：{e}")

            self._update_stats()

    def get_area_power_status(self, position: Tuple[int, int]) -> PowerStatus:
        """
        查詢指定位置的電力狀態\n
        \n
        根據座標位置查詢對應電力區域的供電狀態\n
        \n
        參數:\n
        position (tuple): 查詢位置 (x, y)\n
        \n
        回傳:\n
        PowerStatus: 該位置的電力狀態\n
        """
        area_id = self._get_area_by_position(position)

        if area_id and area_id in self.power_areas:
            return self.power_areas[area_id]["status"]

        return PowerStatus.NORMAL  # 預設有電

    def _get_area_by_position(self, position: Tuple[int, int]) -> Optional[int]:
        """
        根據位置座標找出對應的電力區域 ID\n
        \n
        參數:\n
        position (tuple): 查詢位置 (x, y)\n
        \n
        回傳:\n
        int: 區域 ID，如果位置不在任何區域內則回傳 None\n
        """
        x, y = position

        for area_id, area_info in self.power_areas.items():
            area_x, area_y, area_width, area_height = area_info["bounds"]

            # 檢查位置是否在區域範圍內
            if area_x <= x < area_x + area_width and area_y <= y < area_y + area_height:
                return area_id

        return None

    def register_power_change_callback(self, callback: Callable):
        """
        註冊電力狀態變化回調函數\n
        \n
        參數:\n
        callback (function): 回調函數，簽名為 callback(area_id, status, reason)\n
        """
        if callback not in self.power_change_callbacks:
            self.power_change_callbacks.append(callback)

    def register_outage_callback(self, callback: Callable):
        """
        註冊停電事件回調函數\n
        \n
        參數:\n
        callback (function): 回調函數，簽名為 callback(area_id, status, reason)\n
        """
        if callback not in self.outage_callbacks:
            self.outage_callbacks.append(callback)

    def update(self, dt: float):
        """
        更新電力系統狀態\n
        \n
        每幀調用，處理電力需求變化、維修進度等\n
        \n
        參數:\n
        dt (float): 距離上次更新的時間間隔（秒）\n
        """
        # 更新停電區域的停電時間
        for area_id, area_info in self.power_areas.items():
            if area_info["status"] == PowerStatus.OUTAGE:
                area_info["outage_duration"] += dt

        # 更新全域電力狀態
        self._update_global_power_status()

    def _update_global_power_status(self):
        """
        更新全域電力狀態\n
        \n
        根據各區域狀態計算整體電力系統健康度\n
        """
        total_areas = len(self.power_areas)

        if total_areas == 0:
            return

        # 計算有電的區域數量
        powered_areas = sum(
            1
            for area in self.power_areas.values()
            if area["status"] == PowerStatus.NORMAL
        )

        # 更新統計資料
        self.stats["areas_with_power"] = powered_areas
        self.stats["workers_on_duty"] = sum(
            1 for worker in self.power_workers.values() if worker["on_duty"]
        )

        # 計算電力效率
        self.stats["power_efficiency"] = powered_areas / total_areas

        # 決定全域電力狀態
        if powered_areas == total_areas:
            self.global_power_status = PowerStatus.NORMAL
        elif powered_areas > total_areas * 0.8:
            self.global_power_status = PowerStatus.NORMAL  # 80% 以上算正常
        elif powered_areas > total_areas * 0.5:
            self.global_power_status = PowerStatus.OVERLOAD  # 50-80% 算超載
        else:
            self.global_power_status = PowerStatus.OUTAGE  # 50% 以下算大停電

    def _update_stats(self):
        """
        更新統計資料\n
        """
        self._update_global_power_status()

    def get_power_stats(self) -> dict:
        """
        取得電力系統統計資料\n
        \n
        回傳:\n
        dict: 包含各種統計數據的字典\n
        """
        return self.stats.copy()

    def get_all_areas_info(self) -> dict:
        """
        取得所有電力區域的詳細資訊\n
        \n
        回傳:\n
        dict: 包含所有區域資訊的字典\n
        """
        return self.power_areas.copy()

    def get_area_info(self, area_id: int) -> Optional[dict]:
        """
        取得指定區域的詳細資訊\n
        \n
        參數:\n
        area_id (int): 區域 ID\n
        \n
        回傳:\n
        dict: 區域資訊，如果區域不存在則回傳 None\n
        """
        return self.power_areas.get(area_id)

    def is_position_powered(self, position: Tuple[int, int]) -> bool:
        """
        檢查指定位置是否有電力供應\n
        \n
        參數:\n
        position (tuple): 查詢位置 (x, y)\n
        \n
        回傳:\n
        bool: True 表示有電，False 表示停電\n
        """
        status = self.get_area_power_status(position)
        return status == PowerStatus.NORMAL

    def debug_print_power_grid(self):
        """
        除錯用：印出電力網格狀態\n
        """
        print("\n=== 電力網格狀態 ===")
        print(f"全域狀態：{self.global_power_status.value}")
        print(f"統計資料：{self.stats}")

        for row in range(5):
            for col in range(6):
                area_id = row * 6 + col + 1
                if area_id in self.power_areas:
                    area = self.power_areas[area_id]
                    status_symbol = "✓" if area["status"] == PowerStatus.NORMAL else "✗"
                    worker_id = area["assigned_worker"] or "無"
                    print(f"區域{area_id:2d}[{status_symbol}]{worker_id:8s}", end=" ")
            print()  # 換行
        print("========================\n")
