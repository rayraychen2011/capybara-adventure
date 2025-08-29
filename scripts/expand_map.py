######################載入套件######################
import csv
import random

######################地圖擴展工具######################
def expand_map_to_100x100():
    """
    將現有的 40x30 地圖擴展為 100x100 地圖\n
    \n
    擴展策略:\n
    1. 將原始地圖置於新地圖的左上角\n
    2. 在右側和下方用相似的地形模式填充\n
    3. 保持原有的地形分佈比例\n
    """
    # 讀取原始地圖
    original_map = []
    with open('config/cupertino_map_edited.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            original_map.append([int(cell.strip()) for cell in row if cell.strip()])
    
    print(f"原始地圖尺寸: {len(original_map[0])}x{len(original_map)}")
    
    # 分析原始地圖的地形分佈
    terrain_stats = {}
    total_cells = 0
    for row in original_map:
        for cell in row:
            terrain_stats[cell] = terrain_stats.get(cell, 0) + 1
            total_cells += 1
    
    print("原始地圖地形分佈:")
    for terrain, count in sorted(terrain_stats.items()):
        percentage = (count / total_cells) * 100
        print(f"地形 {terrain}: {count} 個 ({percentage:.1f}%)")
    
    # 創建 100x100 的新地圖
    new_map = [[0 for _ in range(100)] for _ in range(100)]
    
    # 步驟1: 複製原始地圖到左上角
    for y in range(min(30, 100)):
        for x in range(min(40, 100)):
            if y < len(original_map) and x < len(original_map[0]):
                new_map[y][x] = original_map[y][x]
    
    # 步驟2: 擴展右側區域 (x: 40-99)
    for y in range(100):
        for x in range(40, 100):
            if y < 30:
                # 對於上方區域，基於鄰近的原始地圖進行擴展
                source_x = min(39, x - 40 + 20)  # 映射到原始地圖的右側部分
                source_y = y
                if source_y < len(original_map):
                    # 基於原始地形，加入一些隨機變化
                    base_terrain = original_map[source_y][source_x]
                    new_map[y][x] = _get_similar_terrain(base_terrain)
                else:
                    new_map[y][x] = _get_random_terrain_by_distribution(terrain_stats, total_cells)
            else:
                # 對於下方區域，使用分佈式隨機生成
                new_map[y][x] = _get_random_terrain_by_distribution(terrain_stats, total_cells)
    
    # 步驟3: 擴展下方區域 (y: 30-99)
    for y in range(30, 100):
        for x in range(40):
            # 基於上方對應位置的地形
            source_y = min(29, y - 30 + 15)  # 映射到原始地圖的下方部分
            source_x = x
            if source_x < len(original_map[0]):
                base_terrain = original_map[source_y][source_x]
                new_map[y][x] = _get_similar_terrain(base_terrain)
            else:
                new_map[y][x] = _get_random_terrain_by_distribution(terrain_stats, total_cells)
    
    # 步驟4: 添加一些大型區域以保持真實感
    _add_forest_areas(new_map)
    _add_water_areas(new_map)
    _add_residential_areas(new_map)
    _add_road_network(new_map)
    
    # 儲存新地圖
    with open('config/cupertino_map_100x100.csv', 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        for row in new_map:
            csv_writer.writerow(row)
    
    print(f"新地圖已儲存為 cupertino_map_100x100.csv")
    
    # 分析新地圖的地形分佈
    new_terrain_stats = {}
    new_total_cells = 0
    for row in new_map:
        for cell in row:
            new_terrain_stats[cell] = new_terrain_stats.get(cell, 0) + 1
            new_total_cells += 1
    
    print("\n新地圖地形分佈:")
    for terrain, count in sorted(new_terrain_stats.items()):
        percentage = (count / new_total_cells) * 100
        print(f"地形 {terrain}: {count} 個 ({percentage:.1f}%)")

def _get_similar_terrain(base_terrain):
    """
    根據基礎地形返回相似的地形類型\n
    """
    # 地形相似性對應表
    similar_terrains = {
        0: [0, 7],        # 草地 -> 草地、公園
        1: [1, 7],        # 森林 -> 森林、公園
        2: [2],           # 水體 -> 水體
        3: [3, 8],        # 道路 -> 道路、停車場
        4: [4, 3],        # 高速公路 -> 高速公路、道路
        5: [5, 0],        # 住宅區 -> 住宅區、草地
        6: [6, 5, 8],     # 商業區 -> 商業區、住宅區、停車場
        7: [7, 0, 1],     # 公園 -> 公園、草地、森林
        8: [8, 3],        # 停車場 -> 停車場、道路
        9: [9, 1],        # 山丘 -> 山丘、森林
        10: [10, 3],      # 鐵軌 -> 鐵軌、道路
        11: [11, 6, 8]    # 火車站 -> 火車站、商業區、停車場
    }
    
    possible_terrains = similar_terrains.get(base_terrain, [0])
    # 80% 機率保持原地形，20% 機率選擇相似地形
    if random.random() < 0.8:
        return base_terrain
    else:
        return random.choice(possible_terrains)

def _get_random_terrain_by_distribution(terrain_stats, total_cells):
    """
    根據原始地圖的地形分佈隨機選擇地形\n
    """
    rand_value = random.random()
    cumulative_prob = 0
    
    for terrain, count in terrain_stats.items():
        probability = count / total_cells
        cumulative_prob += probability
        if rand_value <= cumulative_prob:
            return terrain
    
    return 0  # 預設返回草地

def _add_forest_areas(map_data):
    """
    在新地圖中添加一些大型森林區域\n
    """
    # 在右下角添加一個大森林
    for y in range(70, 90):
        for x in range(70, 95):
            if random.random() < 0.8:
                map_data[y][x] = 1
    
    # 在中間區域添加一些小森林
    for y in range(40, 60):
        for x in range(50, 70):
            if random.random() < 0.3:
                map_data[y][x] = 1

def _add_water_areas(map_data):
    """
    在新地圖中添加一些水體區域\n
    """
    # 添加一條從左下到右下的河流
    for x in range(20, 80):
        y = int(80 + 10 * random.random())
        if 0 <= y < 100:
            map_data[y][x] = 2
            # 河流寬度變化
            if random.random() < 0.5 and y + 1 < 100:
                map_data[y + 1][x] = 2

def _add_residential_areas(map_data):
    """
    在新地圖中添加一些住宅區\n
    """
    # 在中右區域添加住宅區
    for y in range(10, 40):
        for x in range(60, 85):
            if random.random() < 0.4:
                map_data[y][x] = 5
    
    # 在下方添加住宅區
    for y in range(50, 80):
        for x in range(10, 40):
            if random.random() < 0.3:
                map_data[y][x] = 5

def _add_road_network(map_data):
    """
    在新地圖中添加道路網絡\n
    """
    # 添加主要的橫向道路
    for x in range(100):
        map_data[50][x] = 3  # 中央橫向道路
        map_data[25][x] = 3  # 上方橫向道路
        map_data[75][x] = 3  # 下方橫向道路
    
    # 添加主要的縱向道路
    for y in range(100):
        map_data[y][50] = 3  # 中央縱向道路
        map_data[y][25] = 3  # 左側縱向道路
        map_data[y][75] = 3  # 右側縱向道路

######################主程式######################
if __name__ == "__main__":
    expand_map_to_100x100()