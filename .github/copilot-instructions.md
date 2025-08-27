# Capybara Adventure - AI Coding Agent Instructions

## Project Overview

This is a cozy life simulation game featuring a capybara exploring a peaceful town, built with Python/Pygame. The codebase follows strict Traditional Chinese documentation standards wi## Project-Specific Patterns

### 🌍 **NEW: Terrain-Based Ecology System**

```python
# Ecology zone detection (replaces scene transitions)
def _check_terrain_ecology_zones(self):
    player_pos = self.player.get_center_position()
    terrain_type = self.terrain_system.get_terrain_at_position(player_pos[0], player_pos[1])

    # Avoid repeated messages
    if terrain_type != self.last_terrain_type:
        if terrain_type == 1:  # Forest ecology
            print("🌲 進入森林生態區域 - Stevens Creek County Park 森林區")
        elif terrain_type == 2:  # Lake ecology
            print("🏞️ 進入湖泊生態區域 - Stevens Creek 溪流")
        self.last_terrain_type = terrain_type
```

### 📱 NPC Management Patternspecific naming conventions and architectural patterns.

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

### 🏢 NPC & Time Systems Integration

- **NPCManager** (`src/systems/npc/npc_manager.py`): Manages 330 town NPCs + 100 forest tribe members with job assignments
- **TimeManager**: Unique game rules - **Saturday/Sunday are WORKDAYS**, Monday-Friday are rest days
- **PowerManager**: 30 electrical districts, power outages when electrical workers are injured
- **Profession system**: 8 professions with specific workplace assignments and daily schedules

### 🗂️ Systems Architecture

```
src/systems/
  terrain_based_system.py # NEW: Unified world system with CSV terrain loading
  time_system.py          # Day/night cycles, work schedules
  power_system.py         # Electrical grid simulation
  npc/                   # NPC management with professions
    npc_manager.py       # Bulk NPC operations
    npc.py              # Individual NPC behavior
    profession.py       # Job roles and assignments
  wildlife/              # Forest animal simulation
  vehicle_system.py      # Transportation mechanics
```

## Critical Coding Conventions

### 📝 Documentation Standards (MANDATORY)

All code MUST follow the existing Traditional Chinese documentation pattern with section headers:

```python
######################載入套件######################
######################物件類別######################
class ExampleClass:
    """
    類別功能描述 - 用簡單的話說明這個類別做什麼\n
    \n
    詳細說明職責和主要功能\n
    列出重要的屬性和方法\n
    """

def example_function(param1, param2):
    """
    函數功能描述 - 用簡單的話說明這個函數做什麼\n
    \n
    詳細說明這個函數的用途和工作原理\n
    用日常用語解釋，避免過於技術性的術語\n
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
    # 數字計算用日常用語解釋為什麼要這樣算
```

### 🏷️ Naming Conventions

- **Variables**: `snake_case` (e.g., `npc_manager`, `time_scale`)
- **Classes**: `PascalCase` (e.g., `NPCManager`, `TimeManager`)
- **Functions**: `snake_case` (e.g., `update_time_state`, `get_npcs_in_range`)
- **Constants**: `UPPER_CASE` (e.g., `TOTAL_TOWN_NPCS`, `POWER_PLANT_COUNT`)

### 📁 File Organization Patterns

```
src/
  core/          # Core engine systems (GameEngine, StateManager, SceneManager)
  scenes/        # Game scenes (inherit from Scene base class)
  player/        # Player and input systems
  systems/       # Game simulation systems (time, power, NPCs, wildlife)
  utils/         # Helper functions and UI components
config/          # Centralized settings with detailed comments
```

## Development Workflows

### �️ Adding Terrain-Based Features

1. Check terrain at player position: `terrain_system.get_terrain_at_position(x, y)`
2. Use terrain codes for feature detection (1=forest, 2=water, etc.)
3. Implement ecology responses in `_check_terrain_ecology_zones()`
4. Add terrain-specific buildings/resources to `TerrainBasedSystem`

### �🔧 Adding New Systems

1. Create system class in `src/systems/` with Traditional Chinese documentation
2. Initialize in `GameEngine.__init__()` with proper dependency injection
3. Register update/draw calls in `GameEngine.run()` main loop
4. Add system constants to `config/settings.py` with detailed comments

### 🎯 State Management Integration

- Use `self.state_manager.change_state(GameState.X)` for state transitions
- Register callbacks via `state_manager.register_state_change_callback()`
- Check states with `state_manager.is_state(GameState.X)`
- All state changes trigger callbacks for system coordination

### �️ Scene Creation Pattern

1. Inherit from `Scene` base class in `src/scenes/`
2. Implement required methods: `enter()`, `exit()`, `update(dt)`, `draw(screen)`, `handle_event(event)`
3. Register in `GameEngine._initialize_scenes()` with system dependencies:
   ```python
   scene = NewScene(self.state_manager, self.time_manager, self.power_manager)
   self.scene_manager.register_scene("scene_name", scene)
   ```
4. Add scene constant to `config/settings.py`

### 🎨 UI and Rendering Standards

- Use `FontManager` for Traditional Chinese text support via `get_font_manager()`
- All colors defined in `config/settings.py` with descriptive names
- UI components in `src/utils/` follow naming pattern: `*_ui.py`
- Coordinate system: (0,0) at top-left, positive Y downward
- **UI Positioning**: `TimeDisplayUI` supports `top_center` positioning for centered top displays
- **Screen Resolution**: Now 1024x768 instead of 1728x1728

## Key Dependencies & Integration Points

### 🔧 Configuration System

**Critical**: All constants in `config/settings.py` with extensive Traditional Chinese comments:

- Game dimensions: `SCREEN_WIDTH = 1024`, `SCREEN_HEIGHT = 768`, `FPS = 60`
- NPC counts: `TOTAL_TOWN_NPCS = 330`, `TOTAL_TRIBE_NPCS = 100`
- Map layout: 30x30 street grid with `TOWN_GRID_WIDTH/HEIGHT`
- System parameters: Power grid (30 districts), profession distributions
- **Terrain mapping**: Cupertino CSV data with codes 0-9 for different terrain types

### 🛠️ Utility Functions (`src/utils/helpers.py`)

**Always use these instead of reimplementing**:

- `calculate_distance()`, `normalize_vector()`, `clamp()`
- `check_rect_collision()`, `safe_load_image()`
- `draw_text()`, `create_surface_with_alpha()`

### 🗺️ Terrain & Map Integration

```python
# Loading terrain data from CSV
terrain_loader = TerrainMapLoader()
terrain_data = terrain_loader.load_map_from_csv("config/cupertino_map_edited.csv")

# Terrain code meanings (0-9)
# 0=grass, 1=forest, 2=water, 3=road, 4=highway,
# 5=residential, 6=commercial, 7=park, 8=parking, 9=hills
```

### 🎮 Input Handling Pattern

```python
# In scene's handle_event method
if event.type == pygame.KEYDOWN:
    if event.key == pygame.K_e:  # Interact key
        # Handle interaction
    elif event.key == pygame.K_i:  # Inventory key
        self.state_manager.change_state(GameState.INVENTORY)
```

### ⏰ Time System Integration

**Key concept**: Inverted work schedule (weekends = workdays)

```python
# Getting time information
if self.time_manager.is_work_time():  # Saturday/Sunday 9-17h
    # NPCs go to work
current_time = self.time_manager.get_time_string()
sky_color = self.time_manager.get_sky_color()
```

## Project-Specific Patterns

### � NPC Management Pattern

```python
# NPC creation with profession assignment
npc_manager = NPCManager(time_manager)
npc_manager.initialize_npcs(town_bounds, forest_bounds)

# Update with time integration
npc_manager.update(dt, player_position)
```

### ⚡ Power System Pattern

```python
# Power grid affects 30 districts
if electrical_worker.is_injured:
    power_manager.set_district_power(district_id, False)

# Check power status
if power_manager.has_power(district_id):
    # Buildings operate normally
```

### 💰 Player Inventory Pattern (10-slot item bar)

```python
# Item management
player.add_item("fish", 3)        # Add to first available slot
player.select_slot(0)             # Select slot by index
selected_item = player.get_selected_item()

# Money system
if player.spend_money(100):
    # Purchase successful
```

### 🔄 System Dependency Injection

Always pass managers to scenes requiring them:

```python
# Correct pattern
town_scene = TownScene(state_manager, time_manager, power_manager)

# Scene method signatures
def __init__(self, state_manager, time_manager=None, power_manager=None):
```

### 🎯 Performance Optimization Patterns

- **Spatial partitioning**: Only update NPCs within `update_distance` of player
- **Render culling**: Only draw entities within camera view + margin
- **State caching**: Cache expensive calculations in managers
- **Input optimization**: Direct movement updates per-frame for <0.03s latency
- **Frame staggering**: Time system updates every 2 frames, power system every 3 frames

## Common Gotchas & Critical Rules

- ⚠️ **Saturday/Sunday are WORKDAYS** - opposite of real world
- ⚠️ **Traditional Chinese required** in ALL comments and docstrings
- ⚠️ **No `if __name__ == "__main__"`** - call `main()` directly
- ⚠️ **Section headers required**: `######################載入套件######################`
- ⚠️ **System dependencies**: Always inject managers, never import globally
- ⚠️ **State transitions**: Use StateManager, never direct scene switching
- ⚠️ **No more portal transitions**: Use terrain ecology zones instead
- ⚠️ **Screen resolution**: Now 1024x768, update UI positioning accordingly
- ⚠️ **Player speed**: Currently very slow (0.05), may need adjustment for playability

## Testing & Debugging

### 🎮 Debug Controls (F1-F12)

Built-in debug hotkeys for time and power systems:

- `F1-F9`: Time manipulation (speed, skip hours/days)
- `F10/F12`: Power system visualization
- `H`: Show all hotkey help

### 🏃 Running the Game

```bash
python main.py  # Direct execution, GameEngine handles everything
```

Game flow: `main()` → `pygame.init()` → `GameEngine()` → `run()` → main loop with scene management

### 🔍 Common Debug Techniques

- Time system: Use `time_manager.get_debug_info()` for full state
- NPC behavior: `npc_manager.get_statistics()` for population overview
- Power grid: Visual debug via F12 hotkey shows district states
- Performance: Built-in FPS display and render distance controls
- **Terrain debugging**: Use `TerrainMapLoader` to visualize CSV terrain data
- **Ecology zones**: Check `get_terrain_at_position()` return values for terrain detection
- **Camera bounds**: Verify camera stays within `terrain_system.map_width/height * tile_size`

### 🏗️ Development Entry Points

- **Main entry**: `main.py` calls `GameEngine()` directly (no `if __name__ == "__main__"`)
- **Core loop**: GameEngine manages 60 FPS loop with optimized system updates
- **Scene creation**: All scenes require `(state_manager, time_manager=None, power_manager=None)` constructor pattern
- **Terrain integration**: Always use `TerrainBasedSystem` for world data instead of hardcoded scene boundaries
- **Recent changes**: Portal system removed (2025-01-09), terrain ecology system implemented, resolution changed to 1024x768
