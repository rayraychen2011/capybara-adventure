# Capybara Adventure - AI Coding Agent Instructions

## Project Overview

This is a cozy life simulation game featuring a capybara exploring a peaceful town, built with Python/Pygame. The codebase follows strict Traditional Chinese documentation standards with specific naming conventions and architectural patterns.

## 🚨 Critical Recent Changes (2025-01-09)

⚠️ **Major Terrain-Based System Overhaul**:

- **Portal System REMOVED**: All portal-based scene transitions deleted; replaced with terrain-based ecology zones
- **Unified World Map**: Single continuous world using CSV terrain data instead of separate forest/lake scenes
- **Screen Resolution**: Changed from 1728x1728 to 1024x768 for standard display compatibility
- **Terrain Ecology**: Players trigger forest/lake experiences by walking on terrain codes 1 (forest) and 2 (water)
- **Camera System**: Full follow-camera implementation with world bounds constraints
- **UI Repositioning**: Time display moved to `top_center`, all UI adapted for new resolution

## Architecture & Core Systems

### 🏗️ Multi-Layer Architecture

```
GameEngine -> [StateManager + SceneManager + TimeManager + PowerManager] -> TownScene -> [Player + Systems]
```

- **GameEngine** (`src/core/game_engine.py`): Central coordinator with frame-optimized update sequences
- **StateManager** (`src/core/state_manager.py`): Enum-based state machine (9 states: MENU, PLAYING, PAUSED, INVENTORY, SHOPPING, FISHING, HUNTING, DRIVING, QUIT)
- **SceneManager** (`src/core/scene_manager.py`): Scene lifecycle with base `Scene` class inheritance
- **TownScene** (`src/scenes/town/town_scene_refactored.py`): Main game scene with modular sub-managers
- **TimeManager** (`src/systems/time_system.py`): **Saturday/Sunday are WORKDAYS** (opposite of real world)
- **PowerManager** (`src/systems/power_system.py`): 30-district electrical grid with worker injury system

### 🗺️ **NEW: Terrain-Based World System** (CRITICAL)

**The biggest architectural change**: Everything now uses CSV terrain data instead of separate scenes:

```python
# Core terrain ecology detection pattern
terrain_type = self.terrain_system.get_terrain_at_position(player_x, player_y)
if terrain_type == 1:  # Forest ecology zone
    print("🌲 進入森林生態區域 - Stevens Creek County Park 森林區")
elif terrain_type == 2:  # Lake ecology zone
    print("🏞️ 進入湖泊生態區域 - Stevens Creek 溪流")
```

- **TerrainBasedSystem** (`src/systems/terrain_based_system.py`): Loads `config/cupertino_map_edited.csv` and auto-generates everything
- **Terrain Codes**: 0=grass, 1=forest, 2=water, 3=road, 4=highway, 5=residential, 6=commercial, 7=park, 8=parking, 9=hills
- **Building Generation**: Residential areas (code 5) get 4 houses per grid; Commercial areas (code 6) get 4 buildings per grid
- **Ecology Zones**: Walking on terrain triggers ecology messages without scene changes
- **No Scene Boundaries**: Seamless world exploration with camera follow

### 🎮 Scene Architecture Pattern

All scenes inherit from `Scene` base class with required methods:

- `enter()` / `exit()` - lifecycle hooks
- `update(dt)` / `draw(screen)` - frame updates
- `handle_event(event)` - input processing
- `request_scene_change(target_scene)` - scene transitions

**Available Scenes**: town (main), home, menu, inventory

### 🏢 NPC & Time Systems Integration

## Recent Architecture Changes (Critical - 2025-01-09)

⚠️ **Major Game Design Overhaul**:

- **Portal System Removed**: Scene transitions via portals (`_create_scene_transitions()`) completely removed
- **Terrain-Based Ecology**: Players now experience forest/lake ecology by walking directly on terrain types in unified world map
- **Screen Resolution**: Changed from 1728x1728 to 1024x768 for standard display compatibility
- **Camera System**: Full camera follow implementation with seamless world exploration
- **UI Reorganization**: Time display moved to `top_center`, minimap remains `top_right`
- **Terrain Integration**: `TerrainBasedSystem` now handles ecology zones via `get_terrain_at_position()`

⚠️ **Road System Visual Removal**: All road, sidewalk, and traffic light visuals have been removed while preserving logic:

- `RoadSegment.draw()`, `Intersection.draw()`, `TrafficLight.draw()` now contain only `pass` statements
- All collision detection, pathfinding, and traffic logic remains functional for NPCs/vehicles

## Architecture & Core Systems

### 🏗️ Multi-Layer Architecture

```
GameEngine -> [StateManager + SceneManager + TimeManager + PowerManager] -> Scenes -> [Player + NPCs + Systems]
```

- **GameEngine** (`src/core/game_engine.py`): Central coordinator managing main loop, input handling, and system integration with frame-optimized update sequences
- **StateManager** (`src/core/state_manager.py`): Enum-based state machine with callback system and transition validation (9 states: MENU, PLAYING, PAUSED, INVENTORY, SHOPPING, FISHING, HUNTING, DRIVING, QUIT)
- **SceneManager** (`src/core/scene_manager.py`): Scene lifecycle management with base `Scene` class inheritance pattern
- **TimeManager** (`src/systems/time_system.py`): Game time, day/night cycles, work schedules (unique rule: weekends are workdays, Monday-Friday rest days)
- **PowerManager** (`src/systems/power_system.py`): Electrical grid simulation affecting 30 town districts with worker injury system

### 🗺️ **NEW: Unified Terrain-Based World System**

**Critical Change**: Instead of separate forest/lake scenes, everything exists in one continuous world map:

- **TerrainBasedSystem** (`src/systems/terrain_based_system.py`): Loads real Cupertino CSV data and auto-generates buildings, ecology zones
- **Terrain Codes**: 0=grass, 1=forest, 2=water, 3=road, 4=highway, 5=residential, 6=commercial, 7=park, 8=parking, 9=hills
- **Ecology Integration**: Walking on terrain code 1 triggers forest ecology, terrain code 2 triggers lake ecology
- **Camera Follow**: `_update_camera()` keeps player centered, constrained to map boundaries
- **No Scene Transitions**: Players explore seamlessly without loading screens

```python
# New terrain ecology detection pattern
terrain_type = self.terrain_system.get_terrain_at_position(player_x, player_y)
if terrain_type == 1:  # Forest ecology zone
    print("🌲 進入森林生態區域 - Stevens Creek County Park 森林區")
elif terrain_type == 2:  # Lake ecology zone
    print("🏞️ 進入湖泊生態區域 - Stevens Creek 溪流")
```

### 🎮 Scene System Pattern

All scenes inherit from `Scene` base class with required methods:

- `enter()` / `exit()` - lifecycle hooks
- `update(dt)` / `draw(screen)` - frame updates
- `handle_event(event)` - input processing
- `request_scene_change(target_scene)` - scene transitions (now only for menu/inventory/home)

Scene registration pattern in GameEngine:

```python
town_scene = TownScene(self.state_manager, self.time_manager, self.power_manager)
self.scene_manager.register_scene(SCENE_TOWN, town_scene)
```

**Available Scenes**: town (main world), home, menu, inventory

### 🗺️ Map & Terrain System

- **Cupertino Map**: Real-world CSV-based terrain data (`config/cupertino_map_edited.csv`) with 10 terrain types (0-9)
- **TerrainBasedSystem** (`src/systems/terrain_based_system.py`): Unified world system that loads CSV data and generates ecology zones
- **TileMapManager** (`src/systems/tile_system.py`): 30x30 town grid with streets, crosswalks, and building placement
- **Coordinate System**: Large world coordinates with camera offset for viewport rendering

### 👤 Player System Architecture

- **Player** class with 10-slot item bar (replaces traditional inventory), position tracking, health/money
- **InputController** handles WASD/arrow keys + action mapping (E for interact, I for inventory)
- **Movement Speed**: Currently `PLAYER_SPEED = 0.05` (very slow, may need adjustment)
- **World Coordinates**: Large world with camera offset for viewport rendering

- **NPCManager** (`src/systems/npc/npc_manager.py`): Manages 330+ town NPCs with behavior modules
- **TimeManager**: **INVERTED SCHEDULE** - Saturday/Sunday are WORKDAYS, Monday-Friday are rest days
- **PowerManager**: 30-district electrical grid; power outages when electrical workers get injured
- **NPC Behaviors**: Modular system with `MovementBehavior` and `WorkBehavior` classes

## � Development Workflows & Patterns

### ⚡ Recent Development Patterns (Follow These)

1. **New Systems**: Use terrain-based approach instead of scene-based
2. **Fishing System**: Complete interaction flow with choice UI (release vs sell fish)
3. **Building Generation**: Automated via terrain codes, not manual placement
4. **NPC Behaviors**: Split into separate behavior classes for modularity
5. **UI Components**: All support Traditional Chinese with `FontManager`

### 📊 Adding New Game Features

```python
# 1. Add to terrain system if location-based
def _setup_new_area_type(self):
    for y in range(self.map_height):
        for x in range(self.map_width):
            if self.map_data[y][x] == NEW_TERRAIN_CODE:
                # Setup area in this grid

# 2. Add to scene if gameplay mechanic
def _handle_new_interaction(self, player):
    # Handle interaction logic

# 3. Add UI component in src/utils/
class NewFeatureUI:
    def __init__(self):
        self.font_manager = get_font_manager()
```

### 🏃 Critical Debug/Testing Commands

```bash
# Main game execution
python main.py

# Terrain debugging
python debug_terrain.py

# Functionality testing
python test_functionality.py
```

### 🎯 State Management Integration

- Use `self.state_manager.change_state(GameState.X)` for transitions
- Register callbacks via `state_manager.register_state_change_callback()`
- All state changes trigger system coordination callbacks

## Critical Coding Conventions (MANDATORY)

### 📝 Traditional Chinese Documentation Pattern

**ALL code must follow this exact pattern**:

```python
######################載入套件######################
######################物件類別######################
class ExampleClass:
    """
    類別功能描述 - 用簡單的話說明這個類別做什麼\n
    \n
    詳細說明職責和主要功能\n
    用日常用語解釋，避免過於技術性術語\n
    """

def example_function(param1, param2):
    """
    函數功能描述 - 用簡單的話說明這個函數做什麼\n
    \n
    參數:\n
    param1 (type): 參數說明，包含類型和有效範圍\n
    param2 (type): 參數說明\n
    \n
    回傳:\n
    type: 回傳值說明\n
    """
    # 用簡單的話說明每個重要步驟在做什麼
    # 條件判斷用「如果...就...」的方式說明
```

### 🏷️ Naming Rules

- **Variables**: `snake_case` - `terrain_system`, `player_position`
- **Classes**: `PascalCase` - `TerrainBasedSystem`, `NPCManager`
- **Functions**: `snake_case` - `get_terrain_at_position`, `check_collision`
- **Constants**: `UPPER_CASE` - `SCREEN_WIDTH`, `TOTAL_TOWN_NPCS`

### �️ File Organization

```
src/
  core/          # Engine (GameEngine, StateManager, SceneManager)
  scenes/        # Game scenes (inherit from Scene)
  player/        # Player and input systems
  systems/       # Game simulation (terrain, NPCs, time, power)
  utils/         # UI components and helpers
config/          # Settings with detailed Traditional Chinese comments
```

## Project-Specific Implementation Patterns

### 🌍 **Terrain Ecology System** (New Core Pattern)

```python
# Core pattern for terrain-based features
def _check_terrain_ecology_zones(self):
    player_pos = self.player.get_center_position()
    terrain_type = self.terrain_system.get_terrain_at_position(player_pos[0], player_pos[1])

    if terrain_type != self.last_terrain_type:
        if terrain_type == 1:  # Forest ecology
            print("🌲 進入森林生態區域")
        elif terrain_type == 2:  # Lake ecology
            print("🏞️ 進入湖泊生態區域")
        self.last_terrain_type = terrain_type
```

### 🎣 Complex Interaction Systems (Fishing Example)

```python
# Multi-stage interaction with choice UI
class FishingSystem:
    def try_catch_fish(self, player):
        # Timing-based interaction
        if self.has_bite and within_time_window:
            fish = self._select_random_fish()
            # Show choice UI: release (health) vs sell (money)
            self.show_fish_choice = True
            return {"success": True, "fish": fish}
```

### 🏗️ Building Generation via Terrain

```python
# Auto-generation from CSV terrain data
def _setup_residential_areas(self):
    for y in range(self.map_height):
        for x in range(self.map_width):
            if self.map_data[y][x] == 5:  # Residential code
                # Place 4 houses per grid in 2x2 pattern
                for row in range(2):
                    for col in range(2):
                        house = ResidentialHouse(position, size)
```

### 🤖 Modular NPC Behavior

```python
# Behavior composition pattern
class NPC:
    def __init__(self):
        self.movement_behavior = NPCMovementBehavior(self)
        self.work_behavior = NPCWorkBehavior(self)

    def update(self, dt):
        self.movement_behavior.update(dt)
        self.work_behavior.update(dt, time_manager)
```

## Key Integration Points & Dependencies

### 🔧 Configuration System (`config/settings.py`)

**All constants use Traditional Chinese comments**:

- Game dimensions: `SCREEN_WIDTH = 1024`, `SCREEN_HEIGHT = 768`
- NPC population: `TOTAL_TOWN_NPCS = 330+`
- Terrain mapping: CSV codes 0-9 for different areas
- Time system: **INVERTED WORK SCHEDULE** (weekends = work days)

### 🛠️ Essential Utilities (`src/utils/helpers.py`)

**Always use existing functions**:

- `calculate_distance()`, `check_rect_collision()`
- `safe_load_image()`, `draw_text()`
- `FontManager` for Traditional Chinese text

### 📱 Input Pattern

```python
# Standard input handling in scenes
if event.type == pygame.KEYDOWN:
    if event.key == pygame.K_e:  # Interact
        # Handle interaction
    elif event.key == pygame.K_i:  # Inventory
        self.state_manager.change_state(GameState.INVENTORY)
```

## Critical Rules & Gotchas

- ⚠️ **Saturday/Sunday = WORKDAYS** (opposite of real world)
- ⚠️ **ALL comments in Traditional Chinese** with specific format
- ⚠️ **No `if __name__ == "__main__"`** - call `main()` directly
- ⚠️ **Section headers required**: `######################載入套件######################`
- ⚠️ **Terrain-based not portal-based**: Use ecology zones instead of scene transitions
- ⚠️ **1024x768 resolution**: Update all UI positioning for new dimensions
- ⚠️ **Camera follow system**: All world coordinates need camera offset calculations
