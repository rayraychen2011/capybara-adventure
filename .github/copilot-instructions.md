# Capybara Adventure — AI 編碼代理指引

此文件提供精簡、可執行的指引，讓 AI 編碼代理（Copilot / LLM）能快速在本專案中做出安全、有用的修改。

- 主要語言 / 執行：Python 3.x、Pygame
- 啟動檔：`main.py`（專案慣例：直接呼叫 `main()`，不要加 `if __name__ == "__main__"`）

快速上手要點

- 世界由 CSV 地形驅動：`config/cupertino_map_edited.csv` → `src/systems/terrain_based_system.py`
- 引擎層次：`src/core/game_engine.py` -> `StateManager` / `SceneManager` -> 場景 -> 玩家/NPC/Systems
- 常用 API：`terrain_system.get_terrain_at_position(x, y)` 回傳地形 code（0-9）

必讀檔案（優先順序）

- `main.py`
- `src/core/game_engine.py`
- `src/core/state_manager.py`, `src/core/scene_manager.py`
- `src/systems/terrain_based_system.py`, `src/systems/tile_system.py`
- `src/systems/time_system.py`, `src/systems/power_system.py`
- `src/player/player.py`, `src/player/input_controller.py`
- `config/settings.py`, `config/cupertino_map_edited.csv`

專案慣例（重要）

- 註解/文件：全部使用繁體中文。公有方法需要三引號 docstring，包含功能、參數、回傳。
- 區塊註解：使用 `######################` 作段落分隔。
- 命名：`snake_case`（函式/變數）、`PascalCase`（類別）、`UPPER_CASE`（常數）。
- 時間系統：週末（Sat/Sun）為工作日（`src/systems/time_system.py`）。
- 畫面解析度：`SCREEN_WIDTH=1024`, `SCREEN_HEIGHT=768`（`config/settings.py`）。

建議開發工作流

- 修改地形或區域行為：先在 `config/cupertino_map_edited.csv` 做小規模更動並用地形檢視或 `python main.py` 測試。
- 新位置相關機制：優先擴充 `terrain_based_system` / `tile_system`，避免新增場景。
- 跨系統狀態變更：使用 `state_manager.change_state(...)` 並註冊 callback 以避免 race condition。

可複製範例（直接貼入場景或系統）

地形生態檢測（放在場景的 `update`）：

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

簡單建築生成（示範，呼叫於 terrain 系統初始化）：

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

常用命令

- 執行遊戲：

```
python main.py
```

- 執行測試：

```
python -m pytest -q
```

小結：如果要我幫你把其中一個範例整合到真實檔案（例如把 `check_terrain_ecology_zones` 加入 `src/scenes/town/town_scene_old.py` 或 `town_scene_refactored.py`），我可以替你修改並執行測試，請告訴我要改哪個檔案。
