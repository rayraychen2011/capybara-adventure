# Cupertino 地圖系統使用指南

## 📋 概述

此系統將真實的 Cupertino 地圖轉換為 CSV 格式，讓您可以使用數字編碼來編輯和自訂地形。系統包含三個主要組件：

1. **CSV 地圖檔案** (`config/cupertino_map.csv`) - 40x30 格的地形數據
2. **地圖載入器** (`src/utils/terrain_map_loader.py`) - 程式化載入和操作地圖
3. **視覺化編輯器** (`src/utils/terrain_map_editor.py`) - 圖形化編輯介面

## 🗺️ 地形編碼系統

| 編碼 | 地形類型 | 顏色   | 描述           | 對應真實地點                         |
| ---- | -------- | ------ | -------------- | ------------------------------------ |
| 0    | 草地     | 淺綠色 | 開放草地區域   | 公園周邊空地                         |
| 1    | 森林     | 深綠色 | 密集樹林       | Stevens Creek County Park 主要森林區 |
| 2    | 水體     | 藍色   | 河流、池塘     | Stevens Creek 溪流                   |
| 3    | 道路     | 灰色   | 一般街道       | 住宅區街道                           |
| 4    | 高速公路 | 深灰色 | 主要幹道       | 85 號、280 號高速公路                |
| 5    | 住宅區   | 淺黃色 | 居住區域       | Cupertino 住宅區                     |
| 6    | 商業區   | 橘色   | 商店、辦公樓   | 商業中心                             |
| 7    | 公園設施 | 綠色   | 遊樂設施、步道 | 公園內設施區                         |
| 8    | 停車場   | 淺灰色 | 停車區域       | 公園停車場                           |
| 9    | 山丘     | 棕色   | 地勢較高區域   | 丘陵地帶                             |

## 📁 檔案結構

```
config/
├── cupertino_map.csv          # 主要地圖檔案 (40x30)
├── terrain_codes.md           # 地形編碼說明
└── cupertino_map_edited.csv   # 編輯後的地圖（編輯器自動產生）

src/utils/
├── terrain_map_loader.py      # 地圖載入和操作類別
└── terrain_map_editor.py      # 視覺化編輯器
```

## 🛠️ 使用方法

### 1. 程式化操作地圖

```python
from src.utils.terrain_map_loader import TerrainMapLoader

# 載入地圖
map_loader = TerrainMapLoader()
map_loader.load_from_csv("config/cupertino_map.csv")

# 查詢地形
terrain_type = map_loader.get_terrain_at(10, 15)
terrain_name = map_loader.get_terrain_name(terrain_type)
print(f"座標(10,15)的地形：{terrain_name}")

# 修改地形
map_loader.set_terrain_at(10, 15, 1)  # 設為森林

# 儲存地圖
map_loader.save_to_csv("config/modified_map.csv")
```

### 2. 視覺化編輯

執行編輯器：

```bash
python src/utils/terrain_map_editor.py
```

編輯器操作：

- **左鍵點擊/拖拽**：繪製當前選擇的地形
- **數字鍵 0-9**：選擇不同地形類型
- **S 鍵**：儲存地圖到 `config/cupertino_map_edited.csv`
- **ESC 鍵**：離開編輯器

### 3. 整合到遊戲中

在遊戲場景中載入地圖：

```python
# 在場景初始化中
from src.utils.terrain_map_loader import TerrainMapLoader

class TownScene(Scene):
    def __init__(self, ...):
        # 載入地形地圖
        self.terrain_map = TerrainMapLoader()
        self.terrain_map.load_from_csv("config/cupertino_map.csv")

    def draw(self, screen):
        # 渲染地圖（縮圖方式）
        minimap_surface = pygame.Surface((200, 150))
        self.terrain_map.render_minimap(minimap_surface, scale=5)
        screen.blit(minimap_surface, (10, 10))

    def get_terrain_at_player(self, player_x, player_y):
        # 根據玩家位置獲取地形類型
        map_x = int(player_x // TILE_SIZE)
        map_y = int(player_y // TILE_SIZE)
        return self.terrain_map.get_terrain_at(map_x, map_y)
```

## 🎮 遊戲整合範例

### 地形影響遊戲機制

```python
def update_player_movement(self, player, dt):
    """根據地形類型調整玩家移動速度"""
    terrain_code = self.get_terrain_at_player(player.x, player.y)

    # 不同地形的移動速度修正
    speed_modifiers = {
        0: 1.0,    # 草地 - 正常速度
        1: 0.7,    # 森林 - 較慢
        2: 0.3,    # 水體 - 很慢（游泳）
        3: 1.2,    # 道路 - 較快
        4: 1.5,    # 高速公路 - 最快（但危險）
        5: 1.0,    # 住宅區 - 正常
        6: 1.0,    # 商業區 - 正常
        7: 0.9,    # 公園設施 - 略慢
        8: 1.1,    # 停車場 - 略快
        9: 0.6     # 山丘 - 較慢（爬坡）
    }

    modifier = speed_modifiers.get(terrain_code, 1.0)
    player.speed = player.base_speed * modifier
```

### 地形互動系統

```python
def handle_terrain_interaction(self, player, action_key_pressed):
    """處理玩家與地形的互動"""
    terrain_code = self.get_terrain_at_player(player.x, player.y)
    terrain_name = self.terrain_map.get_terrain_name(terrain_code)

    if action_key_pressed:
        if terrain_code == 2:  # 水體
            self.show_message("水豚跳進了溪流中游泳！")
            player.start_swimming()

        elif terrain_code == 1:  # 森林
            self.show_message("水豚在森林中發現了野果！")
            player.add_item("野果", 1)

        elif terrain_code == 6:  # 商業區
            self.show_message("水豚進入了商店")
            self.request_scene_change(SCENE_SHOP)

        elif terrain_code == 7:  # 公園設施
            self.show_message("水豚使用了公園設施休息")
            player.restore_energy(20)
```

## 🔧 自訂和擴展

### 添加新地形類型

1. 在 `TerrainMapLoader` 中添加新編碼：

```python
self.terrain_types = {
    # 現有地形...
    10: "沙灘",
    11: "岩石",
    12: "橋樑"
}

self.terrain_colors = {
    # 現有顏色...
    10: (194, 178, 128),  # 沙色
    11: (105, 105, 105),  # 岩石灰
    12: (139, 69, 19)     # 棕色
}
```

2. 在遊戲中處理新地形的邏輯

### 創建多層地圖

```python
# 載入多個地圖層
terrain_layer = TerrainMapLoader()
terrain_layer.load_from_csv("config/terrain_layer.csv")

building_layer = TerrainMapLoader()
building_layer.load_from_csv("config/building_layer.csv")

decoration_layer = TerrainMapLoader()
decoration_layer.load_from_csv("config/decoration_layer.csv")
```

## 📊 地圖統計與分析

使用內建的分析功能：

```python
# 獲取地圖統計資訊
map_info = map_loader.get_map_info()
print(f"地圖大小：{map_info['width']}x{map_info['height']}")
print(f"總格子數：{map_info['total_tiles']}")

for terrain_name, count in map_info['terrain_count'].items():
    percentage = (count / map_info['total_tiles']) * 100
    print(f"{terrain_name}: {count} 格 ({percentage:.1f}%)")
```

## 🐛 常見問題

### Q: 編輯器無法啟動

A: 確認已安裝 pygame：`pip install pygame`

### Q: 地圖載入失敗

A: 檢查 CSV 檔案路徑和格式是否正確

### Q: 想要更大的地圖

A: 可以手動編輯 CSV 檔案添加更多行和列，或使用編輯器重新設計

### Q: 如何匯出為其他格式

A: TerrainMapLoader 類別可以輕易擴展以支援 JSON、XML 等格式

## 🔜 未來擴展計劃

- [ ] 支援多層地圖
- [ ] 地形動畫效果
- [ ] 更多地形類型
- [ ] 地圖生成工具
- [ ] 與真實 GPS 數據整合

---

這個地圖系統為您的水豚冒險遊戲提供了強大而靈活的地形編輯能力。您可以根據遊戲需求自由調整和擴展！
