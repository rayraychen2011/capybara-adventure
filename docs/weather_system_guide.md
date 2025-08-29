# 天氣特效系統 - 功能說明

## 系統概述

天氣特效系統為遊戲添加了豐富的視覺天氣效果，包括不同天氣類型的粒子特效、環境光線變化、天空顏色調整等功能。

## 支援的天氣類型

### 1. ☀️ 晴朗

- **天空顏色**：正常天空藍色
- **環境光**：100% 亮度
- **特效**：無粒子效果
- **能見度**：100%

### 2. ⛅ 多雲

- **天空顏色**：稍微偏灰 (90% 原色)
- **環境光**：80% 亮度
- **特效**：無粒子效果
- **能見度**：95%

### 3. ☁️ 陰天

- **天空顏色**：灰藍色調 (70% 原色)
- **環境光**：60% 亮度
- **特效**：輕微霧效
- **能見度**：80%

### 4. 🌧️ 小雨

- **天空顏色**：深灰藍色 (60% 原色)
- **環境光**：50% 亮度
- **特效**：雨滴粒子 (100 個)
- **能見度**：70%
- **風效**：隨機水平風力 (-30 到 30)

### 5. ⛈️ 雷雨

- **天空顏色**：很暗的灰色 (40% 原色)
- **環境光**：30% 亮度
- **特效**：大雨粒子 (200 個) + 閃電效果
- **能見度**：50%
- **風效**：較強隨機風力
- **閃電**：隨機間隔的全螢幕閃光效果

### 6. 🌨️ 下雪

- **天空顏色**：冷色調白 (90% 原色，增強藍色)
- **環境光**：70% 亮度
- **特效**：雪花粒子 (150 個) + 霧效
- **能見度**：60%
- **風效**：中等隨機風力

## 核心組件

### WeatherParticle (基礎粒子類別)

- 管理粒子的基本物理行為
- 處理位置更新和生命週期
- 支援風力影響

### RainDrop (雨滴粒子)

- 線條形狀模擬雨滴軌跡
- 垂直快速下降
- 受風力影響產生傾斜

### SnowFlake (雪花粒子)

- 圓形或多角形外觀
- 左右搖擺運動
- 緩慢飄落

### LightningFlash (閃電效果)

- 隨機時間間隔觸發
- 短暫全螢幕亮白效果
- 影響環境光強度

### WeatherEffectSystem (主要管理系統)

- 統一管理所有天氣特效
- 與手機 UI 同步天氣狀態
- 提供環境參數修正

## 系統整合

### 與時間系統整合

```python
# 時間系統可獲取天氣修正後的環境參數
modified_light = time_manager.get_ambient_light()  # 已包含天氣修正
modified_sky = time_manager.get_sky_color()       # 已包含天氣修正
```

### 與手機 UI 整合

```python
# 天氣系統會自動同步手機UI的天氣設定
weather_system.phone_ui = phone_ui
weather_system.set_weather(phone_ui.current_weather)
```

### 與遊戲場景整合

```python
# 在場景更新中
weather_system.update(dt)

# 在場景繪製中
weather_system.draw(screen, camera_x, camera_y)
```

## 設定參數

所有天氣相關的設定都在 `config/settings.py` 中：

```python
# 天氣類型設定
WEATHER_TYPES = {
    "☀️ 晴朗": {
        "sky_color_modifier": (1.0, 1.0, 1.0),
        "light_modifier": 1.0,
        "particles": None,
        "visibility": 1.0,
    },
    # ... 其他天氣類型
}

# 粒子特效設定
RAIN_PARTICLE_COUNT = 200
SNOW_PARTICLE_COUNT = 150
RAIN_PARTICLE_SPEED = 400
SNOW_PARTICLE_SPEED = 100

# 閃電效果設定
LIGHTNING_DURATION = 0.2
LIGHTNING_INTERVAL_MIN = 3.0
LIGHTNING_INTERVAL_MAX = 8.0
```

## 使用方法

### 玩家操作

1. 按 `P` 鍵開啟手機 UI
2. 點擊「🌤️ 切換天氣」按鈕
3. 天氣會按順序循環切換

### 程式控制

```python
# 直接設定天氣
weather_system.set_weather("🌧️ 小雨")

# 獲取當前天氣
current_weather = weather_system.get_current_weather()

# 獲取修正後的環境參數
modified_sky = weather_system.get_modified_sky_color(original_color)
modified_light = weather_system.get_modified_ambient_light(original_light)
```

## 除錯功能

天氣系統提供詳細的除錯資訊：

```python
debug_info = weather_system.get_debug_info()
# 回傳包含以下資訊的字典：
# - current_weather: 當前天氣
# - particles_count: 活躍粒子數量
# - light_modifier: 光線修正值
# - visibility: 能見度
# - wind_strength: 風力強度
# - fog_alpha: 霧效透明度
# - lightning_active: 閃電是否活躍
```

## 效能優化

- 粒子系統使用物件池管理
- 自動清理超出螢幕的粒子
- 按需生成新粒子
- 閃電效果使用計時器控制

## 未來擴展

系統設計具有良好的擴展性，可以輕鬆添加：

1. **新天氣類型**：在 `WEATHER_TYPES` 中添加新設定
2. **新粒子效果**：繼承 `WeatherParticle` 創建新類別
3. **音效支援**：在各天氣類型中添加音效設定
4. **季節系統**：結合時間系統實現季節變化
5. **地區天氣**：不同地形區域的特殊天氣

## 測試程式

專案包含兩個測試程式：

1. `test_weather_effects.py` - 基本功能測試
2. `test_weather_visual_demo.py` - 詳細視覺效果演示

執行測試：

```bash
python test_weather_effects.py
python test_weather_visual_demo.py
```

## 結論

天氣特效系統為遊戲增添了豐富的視覺層次和氛圍效果，透過粒子系統、光線調整和顏色修正，營造出不同天氣條件下的真實感受。系統設計模組化且易於擴展，可以根據遊戲需求持續添加新功能。
