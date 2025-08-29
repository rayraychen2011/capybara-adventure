# Capybara Adventure - AI 開發指南# Capybara Adventure — AI 編碼代理指引

## 專案概述此文件提供精簡、可執行的指引，讓 AI 編碼代理（Copilot / LLM）能快速在本專案中做出安全、有用的修改。

Capybara Adventure 是一個基於 Python 和 Pygame 的開放世界農場模擬遊戲。玩家扮演水豚，在一個 100x100 網格的地圖上探索小鎮、與 NPC 互動、務農、釣魚、射擊等多種活動。## 核心技術棧

## 技術架構- **主要語言**：Python 3.x + Pygame

- **啟動檔**：`main.py`（專案慣例：直接呼叫 `main()`，不使用 `if __name__ == "__main__"`）

### 核心技術棧- **解析度**：1024x768 (16:12)，60 FPS

- **Python 3.x + Pygame**: 主要開發環境，負責遊戲迴圈、渲染、事件處理- **地圖系統**：100x100 格子地形，CSV 驅動

- **模組化架構**: src/ 目錄下分為核心、場景、系統、工具模組- **資產管理**：圖片素材在 `assets/images/`，音樂在 `assets/music/`

- **狀態管理**: StateManager + SceneManager 雙重架構- **存檔系統**：JSON 格式存檔在 `saves/game_save.json`，支援自動檢測和載入

- **地形系統**: CSV 驅動的 100x100 地圖系統，支援地形感知分配

- **存檔系統**: JSON 格式，支援自動載入/手動儲存## 架構概覽

### 核心系統架構**資料流**：CSV 地形 → TerrainBasedSystem → 自動建築配置 → NPC/Systems → 玩家互動

**引擎層次**：`GameEngine` → `StateManager`/`SceneManager` → `Scene` → `Player`/`Systems`

```**核心 API**：`terrain_system.get_terrain_at_position(x, y)` 回傳地形代碼 (0-11)

src/**狀態管理**：`GameState.MENU/PLAYING/PAUSED/INVENTORY` 等狀態機制

├── core/ # 遊戲核心引擎

│ ├── game_engine.py # 主遊戲引擎 - 統合所有系統## 必讀檔案（依重要性）

│ ├── state_manager.py # 狀態管理器 - PLAYING/PAUSED/QUIT

│ └── scene_manager.py # 場景管理器 - 場景切換與生命週期**核心引擎**：

├── scenes/ # 遊戲場景

│ ├── town/ # 小鎮場景 - 主要遊戲區域- `main.py` - 入口點與錯誤處理

│ │ ├── town_scene_refactored.py # 重構後的小鎮場景- `src/core/game_engine.py` - 主迴圈、場景與狀態整合、快捷鍵處理

│ │ └── town_interaction_handler.py # 互動處理器- `src/core/state_manager.py` - 遊戲狀態機（MENU/PLAYING/PAUSED/INVENTORY 等）

│ ├── home_scene.py # 家場景 - 玩家起始點- `src/core/scene_manager.py` - 場景切換與生命週期管理

│ ├── lake_scene.py # 湖泊場景 - 釣魚活動

│ └── church_interior_scene.py # 教堂內部場景**地形與世界**：

├── systems/ # 遊戲系統

│ ├── terrain_based_system.py # 地形系統 - CSV 驅動的地圖管理- `config/cupertino_map_edited.csv` - 100x100 地形數據（編碼 0-11）

│ ├── building_system.py # 建築系統 - 自動分配與管理- `config/terrain_codes.md` - 地形編碼對照表

│ ├── shop_system.py # 商店系統 - 商品管理與 UI- `src/systems/terrain_based_system.py` - 地形解析與建築自動配置

│ ├── shooting_system.py # 射擊系統 - 武器與彈道- `src/systems/tile_system.py` - 格子地圖與碰撞檢測

│ ├── weather_system.py # 天氣系統 - 動態天氣效果

│ ├── anti_overlap_system.py # 防重疊系統 - 碰撞處理**玩家與互動**：

│ └── npc/ # NPC 相關系統

│ ├── npc_manager.py # NPC 管理器 - 效能優化- `src/player/player.py` - 玩家物理、健康系統（最大血量 1000，初始 300）、物品欄、金錢

│ └── farmer_work_scheduler.py # 農夫工作調度- `src/player/input_controller.py` - WASD/滑鼠輸入處理

├── player/ # 玩家相關- `src/scenes/town/town_scene_refactored.py` - 主要遊戲場景（小鎮場景重構版）

│ ├── player.py # 玩家角色 - 移動、狀態、武器- `src/scenes/town/town_camera_controller.py` - 攝影機跟隨玩家

│ └── input_controller.py # 輸入控制器 - WASD 移動- `src/scenes/town/town_interaction_handler.py` - 互動邏輯處理

└── utils/ # 工具模組- `src/scenes/town/town_ui_manager.py` - UI 管理

    ├── phone_ui.py     # 手機UI - 存檔、時間、天氣

    ├── camera.py       # 攝影機系統**系統設定**：

    └── [各種UI工具]

```- `config/settings.py` - 全域常數與配置參數（玩家速度、建築數量等）

- `config/cupertino_map_edited.csv` - 實際使用的地形地圖

## 地形與建築系統- `config/terrain_codes.md` - 地形編碼（0-11）對照表

### 地形編碼系統 (重要)**UI 和工具**：

- **CSV 檔案**: `config/cupertino_map_100x100.csv` - 100x100 地圖定義

- **地形編碼**: - `src/utils/*.py` - 豐富的 UI 系統（小地圖、手機、武器輪盤、裝備輪盤等）

  - 0=平原 (可建造商業建築)- `src/utils/font_manager.py` - 繁體中文字體支援

  - 1=森林 (不可建造)

  - 2=山脈 (不可建造)## 專案慣例（重要）

  - 3=水域 (不可建造)

  - 5=道路 (可建造商業建築)- **註解/文件**：全部使用繁體中文。公有方法需要三引號 docstring，包含功能、參數、回傳。

  - 8=農地 (僅限農業建築)- **區塊註解**：使用 `######################` 作段落分隔。

- **座標系統**: 每格代表遊戲世界中的一個單位區域- **命名**：`snake_case`（函式/變數）、`PascalCase`（類別）、`UPPER_CASE`（常數）。

- **主程式執行**：不使用 `if __name__ == "__main__":` 慣例，直接呼叫 `main()`。

### 建築分配邏輯 (自動化)- **時間系統**：週末（Sat/Sun）為工作日（`src/systems/time_system.py`）。

- **商業區自動分配**: - **畫面解析度**：`SCREEN_WIDTH=1024`, `SCREEN_HEIGHT=768`（`config/settings.py`）。

  - 在平原(0)和道路(5)上分配服裝店、餐廳、銀行等- **存檔載入**：遊戲啟動時自動檢測 `saves/game_save.json` 並優先載入既有存檔。

  - 使用 `_assign_commercial_buildings()` 方法

  - 避開不合適地形，確保建築合理分布## 架構關鍵原則

- **住宅區分配**:

  - NPC 房屋自動分配在平原區域- **狀態驅動**：所有場景切換透過 `state_manager.change_state(GameState.XXX)`

  - 考慮與商業區的距離平衡- **地形為王**：99% 的遊戲內容由地形編碼驅動，避免硬編碼位置

- **農業建築**: - **系統依賴**：NPC/建築/野生動物都依賴 `terrain_system` 提供位置查詢

  - **嚴格限制**: 只能分配在農地(地形編碼 8)上- **玩家中心**：攝影機、小地圖、互動檢測都以玩家為中心計算

  - 包含穀倉、農舍、農具房等- **資源共享**：`time_manager`、`music_manager` 在 GameEngine 創建後傳遞給場景

  - 農夫工作地點與農業建築位置關聯

- **地形感知分配**: 建築系統會自動避開水域、森林等不適合地形## 建議開發工作流

### 重要的建築類型- **修改地形或區域行為**：先在 `config/cupertino_map_edited.csv` 做小規模更動並用地形檢視或 `python main.py` 測試。

- **服裝店**: - **新位置相關機制**：優先擴充 `terrain_based_system` / `tile_system`，避免新增場景。

  - **整合商品**: 包含所有服裝類商品 (原漫畫主題商品已整合)- **跨系統狀態變更**：使用 `state_manager.change_state(...)` 並註冊 callback 以避免 race condition。

  - **UI 功能**: 完整的購買介面，支援滑鼠與鍵盤操作- **UI 系統開發**：優先使用 `src/utils/` 中現有的 UI 組件（手機、小地圖、武器輪盤等）作為範例。

- **餐廳**: 提供各種食物和飲料- **存檔系統整合**：新數據需要在 `saves/game_save.json` 中保存，參考既有欄位格式。

- **銀行**: 提供金融服務 (未來擴展)

- **NPC 房屋**: NPC 居住與休息的地方## 常見整合模式

- **農業建築**: 穀倉、農舍等，與農夫工作系統緊密整合

**新建築類型**：在 `TerrainBasedSystem._setup_commercial_buildings()` 添加類型 → 在 `config/settings.py` 設定數量 → 創建對應系統類別

## 商店系統 (已重構)

**新 NPC 行為**：擴充 `src/systems/npc/npc_manager.py` → 使用 `terrain_system.get_terrain_at_position()` 查詢工作地點 → 註冊到時間系統回調

### ShopManager 核心功能

- **統一商品管理**: 所有商店商品資料集中管理**場景間資料傳遞**：使用 `scene_manager.change_scene()` 配合 `player` 物件狀態，避免全域變數

- **分類系統**:

  - 服裝類: 各種外觀裝備**系統間通信**：重要系統（time_manager、music_manager）在 GameEngine 創建後傳遞給場景，避免循環依賴

  - 食物類: 補充血量的食品

  - 飲料類: 各種飲品**存檔資料格式**：JSON 結構包含 `timestamp`, `player_position`, `player_health`, `player_money`, `game_time`, `weather` 等核心欄位

- **UI 介面系統**:

  - 商品網格顯示，支援滾動## 可複製範例（直接貼入場景或系統）

  - 滑鼠點擊選擇與購買

  - 右鍵退出功能**地形生態檢測**（放在場景的 `update`）：

  - 購買確認與金錢檢查

- **圖片資源管理**: ```python

  - 路徑: `assets/images/store/` def check_terrain_ecology_zones(player, terrain_system, last_terrain_type):

  - 支援商品圖片載入失敗的降級處理 """檢查玩家目前地形，地形變化時印出生態訊息並回傳當前地形代碼"""

    px, py = player.get_center_position()

### 商品系統設計 terrain_type = terrain_system.get_terrain_at_position(px, py)

- **資料結構**: if terrain_type != last_terrain_type:

  ````python if terrain_type == 1:

  {            print('🌲 進入森林生態區域')

      "name": "商品名稱",        elif terrain_type == 2:

      "price": 100,            print('🏞️ 進入湖泊生態區域')

      "description": "商品描述",     return terrain_type

      "image_path": "store/商品圖片.png",```

      "category": "clothing"

  }**簡單建築生成**（示範，呼叫於 terrain 系統初始化）：

  ````

- **價格系統**: ```python

  - 服裝類: 50-200 金幣 def setup_residential_areas(terrain_system, tile_system):

  - 食物類: 10-50 金幣 """把地形代碼 5 的格子在每格內放置 2x2 小房子（示範用）"""

  - 飲料類: 5-30 金幣 for y in range(terrain_system.map_height):

- **庫存設計**: 無限庫存，適合模擬遊戲體驗 for x in range(terrain_system.map_width):

            if terrain_system.map_data[y][x] == 5:

### 互動處理機制 for row in range(2):

- **建築類型映射**: `building_type_to_shop` 字典定義建築與商店的對應 for col in range(2):

- **右鍵退出**: 統一的退出機制 cell_x = x _ tile_system.tile_size + col _ (tile_system.tile_size // 2)

- **購買流程**: 選擇 → 確認 → 金錢檢查 → 購買成功/失敗 cell_y = y _ tile_system.tile_size + row _ (tile_system.tile_size // 2)

                        tile_system.place_house((cell_x, cell_y))

## NPC 系統 (效能優化)```

### NPC 管理架構**存檔系統整合**（在場景中調用）：

- **NPCManager**:

  - 統一管理所有 NPC 的生命週期```python

  - **效能優化**: 分層更新策略，根據距離調整更新頻率 def save_game_data(player, time_manager, weather_system=None):

  - 支援動態 NPC 生成與清理 """標準存檔格式，可在任何場景使用"""

- **個性系統**: save_data = {

  - 每個 NPC 有獨特的個性特徵 (友善度、工作習慣等) "timestamp": datetime.now().isoformat(),

  - 影響 NPC 的行為模式和對話反應 "player_position": [player.x, player.y],

- **狀態系統**: "player_health": player.health,

  - 健康、心情、工作狀態、社交關係等多維度屬性 "player_money": player.money,

  - 動態變化，影響 NPC 行為 "game_time": time_manager.get_formatted_time(),

        "weather": weather_system.current_weather if weather_system else "☀️ 晴天"

### 農夫工作系統 (自動化調度) }

- **FarmerWorkScheduler**: with open("saves/game_save.json", "w", encoding="utf-8") as f:

  - **時間驅動**: 根據遊戲內時間 (小時) 安排工作計畫 json.dump(save_data, f, indent=2, ensure_ascii=False)

  - **工作階段循環**: ```

    1. GATHERING (集合階段) - 農夫聚集準備

    2. WORKING (工作階段) - 前往農地工作 ## 常用命令

    3. RESTING (休息階段) - 休息與社交

  - **智能路徑導航**: 自動尋找最近的農地或工作地點- 執行遊戲：

  - **卡住檢測與處理**:

    - 檢測長時間未移動的農夫```

    - 自動傳送到安全位置 python main.py

    - 防止 AI 導航失敗影響遊戲體驗```

### NPC 效能優化策略- 執行測試：

- **分層更新系統**:

  - 近距離 (300 像素): 完整更新 - 每幀```

  - 中距離 (600 像素): 簡化更新 - 每 3 幀 python -m pytest -q

  - 遠距離: 最小更新 - 每 10 幀```

- **距離快速計算**: 避免昂貴的平方根運算

- **條件更新**: 只在必要時更新特定系統小結：如果要我幫你把其中一個範例整合到真實檔案（例如把 `check_terrain_ecology_zones` 加入 `src/scenes/town/town_scene_old.py` 或 `town_scene_refactored.py`），我可以替你修改並執行測試，請告訴我要改哪個檔案。

## 輸入控制系統 (已優化)

### 移動控制 (響應性優化)

- **WASD**: 基本 8 方向移動
- **Shift**: 奔跑功能 (速度提升)
- **方向平滑**: 支援對角線移動，流暢的移動體驗
- **碰撞檢測**: 快速矩形碰撞，防止穿越建築和水體

### 互動控制系統

- **E 鍵**: 通用互動鍵 (建築、NPC、物品)
- **右鍵**: 統一的退出/取消操作
- **L 鍵**: 切換射擊模式開關
- **數字鍵 1-3**: 武器快速切換
- **Tab 鍵**: 開關 NPC 狀態顯示面板
- **F1-F3**: 農夫工作系統調試快捷鍵
- **ESC**: 遊戲暫停/繼續

### 滑鼠控制

- **左鍵**: 射擊 (在射擊模式下)
- **右鍵**: 退出商店/介面
- **滑鼠移動**: 瞄準方向控制

## 射擊系統 (完整實作)

### 武器系統

- **多武器支援**:
  - 手槍: 單發精準射擊
  - 霰彈槍: 散彈攻擊
  - BB 槍: 全自動射擊模式
- **武器切換**: 數字鍵快速切換，即時切換武器類型
- **彈藥系統**: 無限彈藥設計，專注遊戲體驗

### 瞄準與射擊機制

- **滑鼠瞄準**: 滑鼠位置決定射擊方向
- **十字準心**: 動態十字準心顯示，提供視覺反饋
- **射擊模式**: L 鍵開關，防止誤射
- **全自動射擊**: BB 槍支援持續射擊

### 彈道系統

- **物理彈道**: 考慮重力影響的拋物線軌跡
- **碰撞檢測**: 精確的子彈與目標碰撞檢測
- **野生動物互動**: 子彈可以與野生動物產生互動 (驚嚇效果)
- **邊界處理**: 子彈超出地圖邊界自動清理

## 存檔系統 (穩定可靠)

### 存檔資料結構

```json
{
  "timestamp": "2025-08-29T22:55:56.287155",
  "player_position": [1810.56, 2695.77],
  "player_health": 100,
  "player_money": 2605,
  "game_time": "02:09",
  "weather": "☀️ 晴朗"
}
```

### 存檔機制設計

- **自動載入**:
  - 遊戲啟動時自動檢查並載入 `saves/game_save.json`
  - 載入失敗時使用預設值，不影響遊戲正常進行
- **手動儲存**:
  - 透過 PhoneUI 的手機介面進行手動儲存
  - 即時收集玩家狀態、時間、天氣等資料
- **資料完整性**:
  - 載入時驗證必要欄位存在
  - 使用臨時檔案機制防止存檔過程中斷導致損壞
- **備份與恢復**:
  - `.tmp` 臨時檔案機制
  - 原子性寫入，確保存檔完整性

### 儲存的遊戲狀態

- **玩家狀態**: 位置、血量、金錢、等級、經驗值
- **裝備狀態**: 當前服裝、擁有的服裝、當前工具
- **時間系統**: 遊戲內時間 (小時:分鐘)
- **環境狀態**: 當前天氣
- **位置資訊**: 玩家在地圖上的精確座標

## 效能優化策略 (已實施)

### 更新頻率優化

- **分時更新策略**:
  - 使用 `frame_count % N` 將系統更新分散到不同幀
  - 避免所有系統在同一幀進行昂貴計算
- **距離優化**:
  - 只對玩家視野範圍內的物件進行完整更新
  - 遠距離物件使用簡化更新邏輯
- **條件更新**:
  - 只在狀態改變時才觸發更新
  - 避免不必要的重複計算

### 碰撞檢測優化

- **範圍預篩選**:
  - 先用簡單的距離檢查過濾候選對象
  - 只對可能碰撞的物件進行精確檢測
- **快速矩形碰撞**:
  - 使用 `pygame.Rect.colliderect` 進行高效檢測
  - 避免複雜的幾何計算
- **分離軸測試**: 對複雜形狀使用更精確但較慢的演算法

### 記憶體管理

- **物件池技術**:
  - 子彈、粒子等頻繁創建的物件使用物件池
  - 重複使用物件，減少 GC 壓力
- **及時清理**:
  - 自動清除超出螢幕範圍的子彈和粒子
  - 定期清理不再需要的資源
- **資源快取**:
  - 圖片、音效等資源預載入並快取
  - 避免重複載入相同資源

### 渲染優化

- **視野裁剪**: 只渲染螢幕可見範圍內的物件
- **批次渲染**: 相同類型的物件一起渲染
- **降級處理**: 資源載入失敗時使用簡單圖形代替

## 程式碼風格指南 (嚴格遵循)

### 命名慣例

- **變數名稱**: snake_case
  - 例如: `player_position`, `game_time`, `bg_x`, `ball_radius`
- **類別名稱**: PascalCase
  - 例如: `GameEngine`, `NPCManager`, `Brick`, `Ball`
- **函數名稱**: snake_case
  - 例如: `update`, `handle_event`, `check_collision`, `draw`
- **常數**: UPPER_SNAKE_CASE
  - 例如: `SCREEN_WIDTH`, `FPS`, `BALL_COLOR`
- **布林變數**: 使用 `is_` 前綴
  - 例如: `is_moving`, `is_alive`, `is_visible`

### 註解規範 (重要)

#### 區塊註解

使用 `######################` 作為區塊分隔符:

```python
######################載入套件######################
import pygame
import sys

######################物件類別######################
class Player:
    # ...

######################定義函式區######################
def main():
    # ...

######################主程式######################
main()
```

#### 函數文檔字串 (必須)

```python
def check_collisions(self, screen_width, screen_height, paddle, bricks):
    """
    統一的碰撞偵測方法 - 處理球與各種物件的碰撞\n
    \n
    此方法按順序檢查：\n
    1. 牆壁碰撞（左右上邊界）\n
    2. 底板碰撞（包含角度調整算法）\n
    3. 磚塊碰撞（每次只處理一個，避免重複計分）\n
    \n
    參數:\n
    screen_width (int): 螢幕寬度，範圍 > 0\n
    screen_height (int): 螢幕高度，範圍 > 0\n
    paddle (Paddle): 底板物件，包含位置和尺寸資訊\n
    bricks (list): 磚塊陣列，包含所有未被擊中的磚塊\n
    \n
    回傳:\n
    dict: {\n
        'game_over': bool - 是否觸發遊戲結束（球掉到底部）\n
        'bricks_hit': int - 本次碰撞擊中的磚塊數量（0或1）\n
    }\n
    \n
    算法說明:\n
    - 底板碰撞角度調整：根據撞擊位置計算反彈角度\n
    - 磚塊碰撞方向判斷：比較 dx、dy 決定水平或垂直反彈\n
    - 速度限制：防止球速過快或過慢影響遊戲體驗\n
    """
```

#### 行內註解 (繁體中文)

```python
# 算出球打到底板的哪個位置（-1 是最左邊，1 是最右邊）
hit_pos = (self.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2)

# 根據撞到的位置改變球的左右速度，撞到邊邊會彈得比較斜
self.velocity_x += hit_pos * 3.5

# 不讓球跑太快，免得玩家跟不上
self.velocity_x = max(-10, min(10, self.velocity_x))
```

#### 異常處理註解

```python
try:
    # 試著載入球的圖片檔案
    ball_image = pygame.image.load(BALL_IMAGE_PATH).convert_alpha()
    ball_image = pygame.transform.scale(ball_image, BALL_IMAGE_SIZE)
    return ball_image
except pygame.error as e:
    # 如果圖片檔案壞了或找不到，就畫一個簡單的圓形代替
    print(f"載入球圖片失敗: {e}")
    # 創建一個圓形，這樣遊戲還是可以玩
    ball_surface = pygame.Surface(BALL_IMAGE_SIZE, pygame.SRCALPHA)
    pygame.draw.circle(ball_surface, BALL_COLOR, center, BALL_RADIUS)
    return ball_surface
```

### 程式結構規範

- **區塊組織**:
  1. 載入套件
  2. 物件類別
  3. 定義函式區
  4. 初始化設定
  5. 主程式
- **縮排**: 統一使用 4 個空格
- **空行**: 適當使用空行分隔不同功能區塊
- **主程式**: **不使用** `if __name__ == "__main__":` 慣例，直接呼叫 `main()`

### 錯誤處理規範

- **關鍵操作**: 必須使用 try-except 包裝
- **資源載入**: 提供降級處理機制
- **用戶操作**: 預期錯誤要有友善的錯誤訊息
- **除錯資訊**: 使用 `traceback.print_exc()` 提供完整錯誤追蹤

## 開發流程規範

### 檔案修改原則

1. **先讀取現有檔案**:
   - 使用 `read_file` 工具了解當前實作狀態
   - 分析現有程式碼的架構和設計模式
2. **小幅度修改**:
   - 避免大規模重構，降低引入錯誤的風險
   - 每次修改專注於單一功能或問題
3. **測試驗證**:
   - 每次修改後執行相關測試腳本
   - 確保修改不會破壞現有功能
4. **註解更新**:
   - 修改程式碼時同步更新相關註解
   - 保持文檔與實作的一致性

### 新功能開發流程

1. **需求分析**:
   - 明確功能需求和預期行為
   - 分析與現有系統的關聯性
2. **系統設計**:
   - 考慮與現有架構的整合點
   - 設計符合現有模式的 API
3. **漸進實作**:
   - 分階段實作，每階段都是可運行的
   - 逐步驗證功能正確性
4. **測試覆蓋**:
   - 編寫測試腳本驗證新功能
   - 確保邊界條件和錯誤情況都有處理

### 除錯流程

1. **問題重現**:
   - 先重現問題，了解觸發條件
   - 記錄重現步驟和環境條件
2. **日誌分析**:
   - 檢查 print 輸出和錯誤訊息
   - 分析錯誤發生的位置和原因
3. **逐步除錯**:
   - 使用 print 語句追蹤執行流程
   - 檢查變數狀態和數值變化
4. **修復驗證**:
   - 修復後執行完整測試
   - 確認問題已解決且無副作用

## 常見問題解決指南

### 建築分配問題

- **症狀**: 建築物沒有正確出現或位置不當
- **檢查點**:
  1. 驗證 `config/cupertino_map_100x100.csv` 中的地形編碼
  2. 檢查 `_assign_commercial_buildings()` 方法邏輯
  3. 確認建築數量設定 (`config/settings.py`)
  4. 測試建築分配邏輯 (`test_building_*.py`)

### NPC 行為異常

- **症狀**: NPC 不移動、卡住、或行為不符預期
- **檢查點**:
  1. 檢查 `FarmerWorkScheduler` 的工作階段狀態
  2. 驗證 NPC 路徑尋找邏輯
  3. 確認時間系統與 NPC 狀態同步
  4. 檢查是否觸發卡住檢測機制

### 商店系統問題

- **症狀**: 商店無法進入、商品顯示異常、購買失敗
- **檢查點**:
  1. 驗證建築類型到商店的映射 (`building_type_to_shop`)
  2. 檢查商品圖片路徑是否正確
  3. 確認玩家金錢狀態
  4. 測試滑鼠點擊事件處理

### 射擊系統問題

- **症狀**: 無法射擊、武器切換失敗、子彈行為異常
- **檢查點**:
  1. 確認 L 鍵 已開啟射擊模式
  2. 檢查武器管理器狀態
  3. 驗證子彈與目標的碰撞邏輯
  4. 檢查彈道物理參數設定

### 效能問題

- **症狀**: 遊戲卡頓、FPS 下降、記憶體使用過高
- **優化策略**:
  1. 檢查 NPC 更新頻率設定
  2. 驗證子彈和粒子清理機制
  3. 分析昂貴操作的執行頻率
  4. 使用性能分析工具找出瓶頸

## 重要檔案位置

### 核心系統檔案

- `main.py`: 遊戲入口點，初始化與錯誤處理
- `src/core/game_engine.py`: 主遊戲迴圈，系統整合
- `src/core/state_manager.py`: 遊戲狀態管理 (PLAYING/PAUSED/QUIT)
- `src/core/scene_manager.py`: 場景切換與管理
- `config/settings.py`: 全域設定檔案

### 主要系統實作

- `src/systems/terrain_based_system.py`: 地形解析與建築分配 ⭐
- `src/systems/building_system.py`: 建築物管理與創建
- `src/systems/shop_system.py`: 商店系統與 UI ⭐
- `src/systems/shooting_system.py`: 射擊系統與武器管理
- `src/systems/npc/npc_manager.py`: NPC 管理與效能優化 ⭐
- `src/systems/npc/farmer_work_scheduler.py`: 農夫工作調度 ⭐

### 場景檔案

- `src/scenes/town/town_scene_refactored.py`: 小鎮主場景 ⭐
- `src/scenes/town/town_interaction_handler.py`: 互動處理
- `src/scenes/home_scene.py`: 家場景
- `src/scenes/lake_scene.py`: 湖泊場景 (釣魚)

### 玩家系統

- `src/player/player.py`: 玩家角色邏輯 ⭐
- `src/player/input_controller.py`: 輸入控制

### 工具與 UI

- `src/utils/phone_ui.py`: 手機 UI 與存檔系統 ⭐
- `src/utils/camera.py`: 攝影機系統
- `src/utils/*_ui.py`: 各種 UI 工具

### 測試檔案

- `test_*.py`: 各種功能測試腳本
- `main.py`: 可直接執行進行完整測試

### 設定檔案

- `config/cupertino_map_100x100.csv`: 地圖定義 ⭐
- `config/settings.py`: 遊戲設定
- `saves/game_save.json`: 存檔檔案

## 開發注意事項 (重要)

### 程式慣例

1. **主程式啟動**:
   - **絕對不使用** `if __name__ == "__main__":` 慣例
   - 所有模組都直接呼叫 `main()` 函數
2. **中文支援**:
   - 所有使用者介面文字使用繁體中文
   - 確保字型檔案支援中文顯示
   - 檔案編碼統一使用 UTF-8
3. **路徑處理**:
   - 使用 `os.path.join` 確保跨平台相容性
   - 避免硬編碼的路徑分隔符
4. **異常處理**:
   - 重要操作 (檔案 I/O、資源載入) 必須包含 try-except
   - 提供有意義的錯誤訊息
   - 關鍵失敗時要有降級處理
5. **資源管理**:
   - 確保 Pygame 資源在遊戲結束時正確釋放
   - 避免記憶體洩漏

### 效能考量

1. **更新優化**:
   - 使用分時更新避免單幀負載過重
   - 距離優化: 遠距離物件使用簡化更新
2. **記憶體管理**:
   - 及時清理不需要的物件
   - 使用物件池技術重複利用物件
3. **渲染優化**:
   - 只渲染可見範圍內的物件
   - 批次處理相似的渲染操作

### 測試策略

1. **功能測試**:
   - 每個主要功能都有對應的測試腳本
   - 測試正常情況和邊界條件
2. **整合測試**:
   - 定期執行主程式進行完整測試
   - 確保各系統整合運作正常
3. **回歸測試**:
   - 修改後執行相關測試確保沒有破壞現有功能

## 實用程式碼範例

### 地形查詢範例

```python
def check_terrain_type(player, terrain_system):
    """檢查玩家當前所在地形類型"""
    px, py = player.get_center_position()
    terrain_type = terrain_system.get_terrain_at_position(px, py)

    terrain_names = {
        0: "平原", 1: "森林", 2: "山脈", 3: "水域",
        5: "道路", 8: "農地"
    }

    current_terrain = terrain_names.get(terrain_type, "未知地形")
    print(f"玩家位於: {current_terrain} (編碼: {terrain_type})")
    return terrain_type
```

### 建築分配檢查範例

```python
def verify_building_distribution(terrain_system):
    """驗證建築分配是否正確"""
    commercial_buildings = terrain_system.get_buildings_by_type("商業")
    farm_buildings = terrain_system.get_buildings_by_type("農業")

    print(f"商業建築數量: {len(commercial_buildings)}")
    print(f"農業建築數量: {len(farm_buildings)}")

    # 檢查農業建築是否都在農地上
    for building in farm_buildings:
        terrain_type = terrain_system.get_terrain_at_position(building.x, building.y)
        if terrain_type != 8:
            print(f"⚠️ 農業建築位於非農地: {building.name} at terrain {terrain_type}")
```

### 存檔系統範例

```python
def save_game_state(player, time_manager, weather="☀️ 晴朗"):
    """標準存檔功能"""
    save_data = {
        "timestamp": datetime.now().isoformat(),
        "player_position": [float(player.x), float(player.y)],
        "player_health": int(player.health),
        "player_money": int(player.money),
        "game_time": time_manager.get_time_string(),
        "weather": weather
    }

    try:
        save_dir = "saves"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        with open("saves/game_save.json", "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        print("遊戲存檔成功！")
        return True
    except Exception as e:
        print(f"存檔失敗: {e}")
        return False
```

## 結語

這個指南應該幫助 AI 開發代理更好地理解和維護 Capybara Adventure 專案。遵循這些指導原則將確保：

- **程式碼品質**: 統一的風格和結構
- **系統穩定性**: robust 的錯誤處理和測試
- **效能表現**: 優化的更新機制和資源管理
- **可維護性**: 清楚的文檔和模組化設計
- **功能完整性**: 全面的遊戲系統整合

專案的持續發展應該建立在這些已經驗證的架構和模式之上，確保每次修改都能改善遊戲體驗而不破壞現有功能。

## 快速參考

### 常用命令

- **執行遊戲**: `python main.py`
- **運行測試**: `python test_*.py`
- **查看地形編碼**: 參考 `config/terrain_codes.md`

### 重要常數 (config/settings.py)

- **螢幕解析度**: 1024 x 768
- **FPS**: 60
- **玩家初始金錢**: 500
- **玩家初始血量**: 100

### 緊急除錯檢查清單

1. 檢查 `main.py` 是否正常啟動
2. 確認 `saves/game_save.json` 存檔格式
3. 驗證地形編碼是否正確
4. 檢查建築分配邏輯
5. 確認 NPC 工作調度狀態
6. 測試商店系統互動
7. 驗證射擊系統功能
