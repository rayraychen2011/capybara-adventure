# Capybara Adventure - AI Coding Agent Instructions

## Project Overview

This is a cozy life simulation game featuring a capybara exploring a peaceful town, built with Python/Pygame. The codebase follows strict Traditional Chinese documentation standards with specific naming conventions and architectural patterns.

## Architecture & Core Systems

### 🏗️ Three-Layer Architecture

```
GameEngine -> StateManager + SceneManager -> Individual Scenes
```

- **GameEngine** (`src/core/game_engine.py`): Central coordinator managing main loop, input handling, and system integration
- **StateManager** (`src/core/state_manager.py`): Enum-based state machine with callback system for transitions (MENU, PLAYING, PAUSED, INVENTORY, etc.)
- **SceneManager** (`src/core/scene_manager.py`): Scene lifecycle management with base `Scene` class inheritance pattern

### 🎮 Scene System Pattern

All scenes inherit from `Scene` base class with required methods:

- `enter()` / `exit()` - lifecycle hooks
- `update(dt)` / `draw(screen)` - frame updates
- `handle_event(event)` - input processing
- `request_scene_change(target_scene)` - scene transitions

Example scene registration in GameEngine:

```python
town_scene = TownScene(self.state_manager)
self.scene_manager.register_scene(SCENE_TOWN, town_scene)
```

### 👤 Player System Architecture

- **Player** class manages position, inventory, money, tools
- **InputController** handles WASD/arrow keys + action mapping (E for interact, I for inventory)
- Scene transitions triggered by collision detection with designated areas

## Critical Coding Conventions

### 📝 Documentation Standards (MANDATORY)

All code MUST follow the existing Traditional Chinese documentation pattern:

```python
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

- **Variables**: `snake_case` (e.g., `bg_x`, `ball_radius`)
- **Classes**: `PascalCase` (e.g., `Player`, `GameEngine`)
- **Functions**: `snake_case` (e.g., `check_collision`, `update_movement`)
- **Constants**: `UPPER_CASE` (e.g., `SCREEN_WIDTH`, `PLAYER_SPEED`)

### 📁 File Organization Patterns

```
src/
  core/          # Core engine systems
  scenes/        # Game scenes (inherit from Scene base class)
  player/        # Player and input systems
  utils/         # Helper functions and managers
config/          # Settings and configuration
```

## Development Workflows

### 🔧 Adding New Scenes

1. Create class inheriting from `Scene` in `src/scenes/`
2. Implement required methods: `enter()`, `exit()`, `update()`, `draw()`, `handle_event()`
3. Register in `GameEngine._initialize_scenes()`
4. Add scene constant to `config/settings.py`

### 🎯 State Management Integration

- Use `self.state_manager.change_state(GameState.X)` for state transitions
- Register callbacks via `state_manager.register_state_change_callback()`
- Check states with `state_manager.is_state(GameState.X)`

### 🎨 UI and Rendering

- Use `FontManager` for Traditional Chinese text support
- Access via `get_font_manager()` - handles system font detection
- All text rendering goes through font manager for proper Chinese display
- Color constants defined in `config/settings.py`

## Key Dependencies & Integration Points

### 🔧 Configuration System

All game constants in `config/settings.py`:

- Screen dimensions, colors, speeds
- Player stats, scene names
- Chinese font paths priority list

### 🛠️ Utility Functions

`src/utils/helpers.py` provides:

- `calculate_distance()`, `normalize_vector()`, `clamp()`
- `check_rect_collision()`, `safe_load_image()`
- Use these instead of reimplementing common math operations

### 🎮 Input Handling

- WASD + Arrow keys for movement
- E/Space for interaction
- I/Tab for inventory
- Input mapping defined in `InputController.action_keys`

## Project-Specific Patterns

### 💰 Player Data Management

```python
# Inventory system pattern
player.add_item("fish", 3)
player.has_item("fish", 1)
player.remove_item("fish", 1)

# Money system
player.add_money(100)
player.spend_money(50)
```

### 🔄 Scene Transition Pattern

```python
# In scene update method
if player_collides_with_transition_area:
    self.request_scene_change(SCENE_TARGET)
```

### 🎯 No `if __name__ == "__main__"`

Direct function calls at module level - project convention is to call `main()` directly without the Python idiom.

## Common Gotchas

- ⚠️ **Always use Traditional Chinese in comments and docstrings**
- ⚠️ **Scene state management requires proper enter/exit lifecycle**
- ⚠️ **Font system must be initialized before text rendering**
- ⚠️ **State changes should go through StateManager, not direct scene switching**
- ⚠️ **Use helper functions from `utils/helpers.py` for common operations**

## Testing & Running

```bash
python main.py  # Direct execution
```

The game initializes Pygame, creates the GameEngine, and starts the main loop. All scenes are registered during engine initialization.
