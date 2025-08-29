#!/usr/bin/env python3
"""
實際遊戲射擊測試 - 在真實遊戲中測試射擊
"""

import sys
import os
import pygame
sys.path.insert(0, os.path.abspath('.'))

from src.core.game_engine import GameEngine

def main():
    """運行遊戲並指導用戶進行射擊測試"""
    
    print("🎮 開始真實遊戲射擊測試...")
    print()
    print("📋 測試說明：")
    print("1. 遊戲啟動後，請用滑鼠左鍵點擊螢幕進行射擊")
    print("2. 嘗試瞄準動物（兔子、羊等）並射擊")
    print("3. 觀察終端輸出，檢查子彈和碰撞檢測訊息")
    print("4. 按ESC或關閉視窗結束測試")
    print()
    print("🔍 期待看到的調試訊息：")
    print("- '🔫 BB槍射擊!' - 表示射擊觸發")
    print("- '🔫 左鍵射擊: can_shoot=True, shoot_result=True' - 表示射擊成功")
    print("- '⚡ 當前有 X 發子彈，Y 隻動物' - 表示子彈和動物共存")
    print("- '🔍 碰撞檢測: X 發子彈 vs Y 隻動物' - 表示碰撞檢測執行")
    print("- '💥 命中目標! 傷害: X' - 表示成功擊中動物")
    print()
    
    input("按Enter開始遊戲...")
    
    # 初始化並運行遊戲
    engine = GameEngine()
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\n⛔ 遊戲被用戶中斷")
    except Exception as e:
        print(f"\n❌ 遊戲運行錯誤: {e}")
    finally:
        print("\n🏁 遊戲測試結束")

if __name__ == "__main__":
    main()