######################載入套件######################
import pygame
import sys
from src.core.game_engine import GameEngine


######################主程式######################
def main():
    """                                                                                             
    小鎮生活模擬器主程式入口\n
    \n
    初始化 Pygame 環境，啟動遊戲引擎，處理遊戲主迴圈\n                                      
    包含基本的錯誤處理機制，確保遊戲能夠正常啟動和關閉\n
    \n
    功能:\n
    1. 初始化 Pygame 核心模組\n
    2. 創建並啟動遊戲引擎實例\n
    3. 處理遊戲結束後的清理工作\n
    \n
    異常處理:\n
    - pygame.error: Pygame 初始化失敗\n
    - KeyboardInterrupt: 使用者中斷程式執行\n
    - SystemExit: 正常程式結束\n
    """
    try:
        # 初始化 Pygame，這是所有 Pygame 功能的基礎
        pygame.init()
        print("Pygame 初始化成功")

        # 建立遊戲引擎實例並啟動主迴圈
        game = GameEngine()
        print("遊戲引擎創建完成，準備開始遊戲")

        # 開始執行遊戲主迴圈，直到玩家退出
        game.run()

    except pygame.error as e:
        # Pygame 初始化或運行時發生錯誤
        print(f"Pygame 錯誤: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        # 玩家按 Ctrl+C 強制中斷程式
        print("\n遊戲被使用者中斷")

    except Exception as e:
        # 其他未預期的錯誤，顯示完整的堆疊追蹤
        import traceback

        print(f"遊戲運行時發生錯誤: {e}")
        print("完整錯誤資訊:")
        traceback.print_exc()
        sys.exit(1)

    finally:
        # 確保 Pygame 資源被正確釋放
        pygame.quit()
        print("遊戲已正常結束，Pygame 資源已清理")


# 直接呼叫主函式，不使用 if __name__ == "__main__" 慣例
main()
