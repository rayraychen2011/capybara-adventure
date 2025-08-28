######################載入套件######################
import pygame
from src.core.state_manager import GameState
from config.settings import *


######################世界控制器######################
class WorldController:
    """
    世界控制器 - 協調遊戲世界中各個系統的運作\n
    \n
    此控制器作為各個系統間的協調中心，負責：\n
    1. 系統間的通訊協調\n
    2. 全域事件處理\n
    3. 效能優化管理\n
    4. 系統生命週期管理\n
    \n
    設計目標：\n
    - 降低系統間的直接耦合\n
    - 提供統一的系統管理介面\n
    - 實現高效的系統協調\n
    """

    def __init__(self):
        """
        初始化世界控制器\n
        """
        # 註冊的系統
        self.systems = {}
        self.update_order = []  # 系統更新順序
        
        # 效能監控
        self.performance_stats = {
            "total_update_time": 0,
            "total_draw_time": 0,
            "frame_count": 0,
            "system_update_times": {}
        }
        
        # 事件系統
        self.event_listeners = {}
        
        print("世界控制器初始化完成")

    def register_system(self, name, system, update_priority=0):
        """
        註冊系統到控制器\n
        \n
        參數:\n
        name (str): 系統名稱\n
        system: 系統實例\n
        update_priority (int): 更新優先級（越低越先更新）\n
        """
        self.systems[name] = {
            "instance": system,
            "priority": update_priority,
            "enabled": True
        }
        
        # 重新排序更新順序
        self._update_system_order()
        
        print(f"註冊系統: {name} (優先級: {update_priority})")

    def _update_system_order(self):
        """
        根據優先級重新排序系統更新順序\n
        """
        sorted_systems = sorted(
            self.systems.items(),
            key=lambda x: x[1]["priority"]
        )
        self.update_order = [name for name, _ in sorted_systems]

    def update_all_systems(self, dt):
        """
        按優先級順序更新所有系統\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        import time
        
        total_start_time = time.time()
        
        for system_name in self.update_order:
            system_info = self.systems[system_name]
            
            if not system_info["enabled"]:
                continue
            
            system = system_info["instance"]
            
            # 效能監控
            start_time = time.time()
            
            try:
                # 嘗試調用系統的更新方法
                if hasattr(system, 'update'):
                    system.update(dt)
            except Exception as e:
                print(f"系統 {system_name} 更新時發生錯誤: {e}")
            
            # 記錄執行時間
            end_time = time.time()
            execution_time = end_time - start_time
            
            if system_name not in self.performance_stats["system_update_times"]:
                self.performance_stats["system_update_times"][system_name] = []
            
            self.performance_stats["system_update_times"][system_name].append(execution_time)
            
            # 只保留最近100次的記錄
            if len(self.performance_stats["system_update_times"][system_name]) > 100:
                self.performance_stats["system_update_times"][system_name].pop(0)
        
        # 記錄總執行時間
        total_end_time = time.time()
        self.performance_stats["total_update_time"] = total_end_time - total_start_time
        self.performance_stats["frame_count"] += 1

    def draw_all_systems(self, screen, camera_offset=(0, 0)):
        """
        繪製所有有繪製功能的系統\n
        \n
        參數:\n
        screen (Surface): 遊戲螢幕\n
        camera_offset (tuple): 攝影機偏移\n
        """
        import time
        
        start_time = time.time()
        
        for system_name in self.update_order:
            system_info = self.systems[system_name]
            
            if not system_info["enabled"]:
                continue
            
            system = system_info["instance"]
            
            try:
                # 嘗試調用系統的繪製方法
                if hasattr(system, 'draw'):
                    if len(camera_offset) == 2:
                        system.draw(screen, camera_offset[0], camera_offset[1])
                    else:
                        system.draw(screen)
            except Exception as e:
                print(f"系統 {system_name} 繪製時發生錯誤: {e}")
        
        # 記錄繪製時間
        end_time = time.time()
        self.performance_stats["total_draw_time"] = end_time - start_time

    def enable_system(self, name):
        """
        啟用系統\n
        \n
        參數:\n
        name (str): 系統名稱\n
        """
        if name in self.systems:
            self.systems[name]["enabled"] = True
            print(f"啟用系統: {name}")

    def disable_system(self, name):
        """
        停用系統\n
        \n
        參數:\n
        name (str): 系統名稱\n
        """
        if name in self.systems:
            self.systems[name]["enabled"] = False
            print(f"停用系統: {name}")

    def get_system(self, name):
        """
        獲取系統實例\n
        \n
        參數:\n
        name (str): 系統名稱\n
        \n
        回傳:\n
        系統實例或None\n
        """
        if name in self.systems:
            return self.systems[name]["instance"]
        return None

    def broadcast_event(self, event_type, event_data=None):
        """
        廣播事件給所有監聽者\n
        \n
        參數:\n
        event_type (str): 事件類型\n
        event_data: 事件數據\n
        """
        if event_type in self.event_listeners:
            for listener in self.event_listeners[event_type]:
                try:
                    listener(event_data)
                except Exception as e:
                    print(f"事件處理器發生錯誤: {e}")

    def register_event_listener(self, event_type, callback):
        """
        註冊事件監聽器\n
        \n
        參數:\n
        event_type (str): 事件類型\n
        callback: 回調函數\n
        """
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        
        self.event_listeners[event_type].append(callback)

    def unregister_event_listener(self, event_type, callback):
        """
        取消註冊事件監聽器\n
        \n
        參數:\n
        event_type (str): 事件類型\n
        callback: 回調函數\n
        """
        if event_type in self.event_listeners:
            try:
                self.event_listeners[event_type].remove(callback)
            except ValueError:
                pass

    def cleanup_all_systems(self):
        """
        清理所有系統\n
        """
        for system_name, system_info in self.systems.items():
            system = system_info["instance"]
            
            try:
                if hasattr(system, 'cleanup'):
                    system.cleanup()
            except Exception as e:
                print(f"系統 {system_name} 清理時發生錯誤: {e}")
        
        print("所有系統已清理完成")

    def get_performance_report(self):
        """
        獲取效能報告\n
        \n
        回傳:\n
        dict: 效能統計資訊\n
        """
        report = {
            "total_update_time": round(self.performance_stats["total_update_time"] * 1000, 2),  # 毫秒
            "total_draw_time": round(self.performance_stats["total_draw_time"] * 1000, 2),
            "frame_count": self.performance_stats["frame_count"],
            "systems_count": len(self.systems),
            "enabled_systems": sum(1 for s in self.systems.values() if s["enabled"])
        }
        
        # 計算各系統平均執行時間
        system_averages = {}
        for system_name, times in self.performance_stats["system_update_times"].items():
            if times:
                avg_time = sum(times) / len(times)
                system_averages[system_name] = round(avg_time * 1000, 2)  # 毫秒
        
        report["system_update_averages"] = system_averages
        
        return report

    def print_performance_report(self):
        """
        列印效能報告\n
        """
        report = self.get_performance_report()
        
        print("\n" + "=" * 50)
        print("🔧 世界控制器效能報告")
        print("=" * 50)
        
        print(f"總更新時間: {report['total_update_time']:.2f} ms")
        print(f"總繪製時間: {report['total_draw_time']:.2f} ms")
        print(f"已處理幀數: {report['frame_count']}")
        print(f"註冊系統數: {report['systems_count']}")
        print(f"啟用系統數: {report['enabled_systems']}")
        
        print("\n系統更新時間 (平均):")
        for system_name, avg_time in report["system_update_averages"].items():
            status = "✓" if self.systems[system_name]["enabled"] else "✗"
            print(f"  {status} {system_name}: {avg_time:.2f} ms")
        
        print("=" * 50 + "\n")

    def reset_performance_stats(self):
        """
        重置效能統計\n
        """
        self.performance_stats = {
            "total_update_time": 0,
            "total_draw_time": 0,
            "frame_count": 0,
            "system_update_times": {}
        }
        print("效能統計已重置")

    def get_debug_info(self):
        """
        獲取除錯資訊\n
        \n
        回傳:\n
        dict: 除錯資訊\n
        """
        return {
            "registered_systems": list(self.systems.keys()),
            "update_order": self.update_order,
            "enabled_systems": [name for name, info in self.systems.items() if info["enabled"]],
            "event_types": list(self.event_listeners.keys()),
            "performance": self.get_performance_report()
        }