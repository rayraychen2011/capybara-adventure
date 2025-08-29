# Capybara Adventure — AI 編碼代理指引

此文件提供精簡、可執行的指引，讓 AI 編碼代理（Copilot / LLM）能快速在本專案中做出安全、有用的修改。

## 核心技術棧

- **主要語言**：Python 3.x + Pygame
- **啟動檔**：`main.py`（專案慣例：直接呼叫 `main()`，不使用 `if __name__ == "__main__"`）
- **解析度**：1024x768 (16:12)，60 FPS
- **地圖系統**：100x100 格子地形，CSV 驅動

## 架構概覽

**資料流**：CSV 地形 → TerrainBasedSystem → 自動建築配置 → NPC/Systems → 玩家互動
**引擎層次**：`GameEngine` → `StateManager`/`SceneManager` → `Scene` → `Player`/`Systems`
**核心 API**：`terrain_system.get_terrain_at_position(x, y)` 回傳地形代碼 (0-11)

## 必讀檔案（依重要性）

**核心引擎**：

- `main.py` - 入口點與錯誤處理
- `src/core/game_engine.py` - 主迴圈、場景與狀態整合、快捷鍵處理
- `src/core/state_manager.py` - 遊戲狀態機（MENU/PLAYING/PAUSED/INVENTORY 等）
- `src/core/scene_manager.py` - 場景切換與生命週期管理

**地形與世界**：

- `config/cupertino_map_edited.csv` - 100x100 地形數據（編碼 0-11）
- `config/terrain_codes.md` - 地形編碼對照表
- `src/systems/terrain_based_system.py` - 地形解析與建築自動配置
- `src/systems/tile_system.py` - 格子地圖與碰撞檢測

**玩家與互動**：

- `src/player/player.py` - 玩家物理、狀態、互動系統
- `src/player/input_controller.py` - WASD/滑鼠輸入處理
- `src/scenes/town/town_scene_refactored.py` - 主要遊戲場景

**系統設定**：

- `config/settings.py` - 全域常數與配置參數

## 專案慣例（重要）

- **註解/文件**：全部使用繁體中文。公有方法需要三引號 docstring，包含功能、參數、回傳。
- **區塊註解**：使用 `######################` 作段落分隔。
- **命名**：`snake_case`（函式/變數）、`PascalCase`（類別）、`UPPER_CASE`（常數）。
- **主程式執行**：不使用 `if __name__ == "__main__":` 慣例，直接呼叫 `main()`。
- **時間系統**：週末（Sat/Sun）為工作日（`src/systems/time_system.py`）。
- **畫面解析度**：`SCREEN_WIDTH=1024`, `SCREEN_HEIGHT=768`（`config/settings.py`）。

## 架構關鍵原則

- **狀態驅動**：所有場景切換透過 `state_manager.change_state(GameState.XXX)`
- **地形為王**：99% 的遊戲內容由地形編碼驅動，避免硬編碼位置
- **系統依賴**：NPC/建築/野生動物都依賴 `terrain_system` 提供位置查詢
- **玩家中心**：攝影機、小地圖、互動檢測都以玩家為中心計算
- **資源共享**：`time_manager`、`music_manager` 在 GameEngine 創建後傳遞給場景

## 建議開發工作流

- **修改地形或區域行為**：先在 `config/cupertino_map_edited.csv` 做小規模更動並用地形檢視或 `python main.py` 測試。
- **新位置相關機制**：優先擴充 `terrain_based_system` / `tile_system`，避免新增場景。
- **跨系統狀態變更**：使用 `state_manager.change_state(...)` 並註冊 callback 以避免 race condition。

## 常見整合模式

**新建築類型**：在 `TerrainBasedSystem._setup_commercial_buildings()` 添加類型 → 在 `config/settings.py` 設定數量 → 創建對應系統類別

**新 NPC 行為**：擴充 `src/systems/npc/npc_manager.py` → 使用 `terrain_system.get_terrain_at_position()` 查詢工作地點 → 註冊到時間系統回調

**場景間資料傳遞**：使用 `scene_manager.change_scene()` 配合 `player` 物件狀態，避免全域變數

## 可複製範例（直接貼入場景或系統）

**地形生態檢測**（放在場景的 `update`）：

```python
def check_terrain_ecology_zones(player, terrain_system, last_terrain_type):
    """檢查玩家目前地形，地形變化時印出生態訊息並回傳當前地形代碼"""
    px, py = player.get_center_position()
    terrain_type = terrain_system.get_terrain_at_position(px, py)
    if terrain_type != last_terrain_type:
        if terrain_type == 1:
            print('🌲 進入森林生態區域')
        elif terrain_type == 2:
            print('🏞️ 進入湖泊生態區域')
    return terrain_type
```

**簡單建築生成**（示範，呼叫於 terrain 系統初始化）：

```python
def setup_residential_areas(terrain_system, tile_system):
    """把地形代碼 5 的格子在每格內放置 2x2 小房子（示範用）"""
    for y in range(terrain_system.map_height):
        for x in range(terrain_system.map_width):
            if terrain_system.map_data[y][x] == 5:
                for row in range(2):
                    for col in range(2):
                        cell_x = x * tile_system.tile_size + col * (tile_system.tile_size // 2)
                        cell_y = y * tile_system.tile_size + row * (tile_system.tile_size // 2)
                        tile_system.place_house((cell_x, cell_y))
```

## 常用命令

- 執行遊戲：

```
python main.py
```

- 執行測試：

```
python -m pytest -q
```

小結：如果要我幫你把其中一個範例整合到真實檔案（例如把 `check_terrain_ecology_zones` 加入 `src/scenes/town/town_scene_old.py` 或 `town_scene_refactored.py`），我可以替你修改並執行測試，請告訴我要改哪個檔案。
