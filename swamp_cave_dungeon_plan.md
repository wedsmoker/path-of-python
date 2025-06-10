# Swamp/Cave Dungeon Implementation Plan

This document outlines the plan to add a new Swamp/Cave themed dungeon to the game, accessible via portals from SpawnTown.

## Detailed Plan: Swamp/Cave Dungeon Implementation

**Goal 1: Define the Swamp/Cave Dungeon Scene**
*   Create a new Python file, e.g., [`core/swamp_cave_dungeon.py`](core/swamp_cave_dungeon.py), that inherits from `core.base_gameplay_scene.BaseGameplayScene`.
*   This class will represent the Swamp/Cave dungeon scene and manage its specific elements.

**Goal 2: Implement Swamp/Cave Map Generation**
*   Within the `SwampCaveDungeon` class, instantiate the `world.map_generator.MapGenerator` with parameters suitable for a dungeon (e.g., smaller size than SpawnTown, different generation settings if `MapGenerator` supports them).
*   If `MapGenerator` is not flexible enough for a distinct dungeon layout, we may need to explore creating a new map generation function or class specifically for dungeons.
*   Identify or create tile assets suitable for a swampy/cave environment from the `graphics` folder.

**Goal 3: Define Dungeon-Specific Data in JSON**
*   Create a new JSON file, e.g., [`data/dungeons.json`](data/dungeons.json), to store data for all dungeons.
*   Within `dungeons.json`, add an entry for the "swamp_cave" dungeon.
*   Include details such as:
    *   `name`: "Swampy Depths" or similar.
    *   `map_settings`: Parameters for map generation (if applicable).
    *   `allowed_enemies`: A list of enemy types that can spawn in this dungeon (e.g., ["leech", "giant_lizard", "grey_snake", "yellow_snake"]).
    *   `enemy_details`: A dictionary defining the properties of each enemy type (health, damage, speed, sprite asset path, abilities).
    *   `dialogue`: Any unique dialogue associated with the dungeon (e.g., lore snippets, warnings).
    *   `portals`: Information about exit portals within the dungeon.

**Goal 4: Implement Dungeon Enemies**
*   Modify the `entities.enemy.Enemy` class or create new enemy classes if needed to handle different enemy behaviors and properties defined in `data/dungeons.json`.
*   In the `SwampCaveDungeon` class, implement enemy spawning logic similar to `SpawnTown`, but using the `allowed_enemies` and `enemy_details` from the `dungeons.json` data for the Swamp/Cave dungeon.
*   Load the appropriate enemy sprites from `graphics/UNUSED/monsters` based on the `enemy_details` in the JSON.

**Goal 5: Implement Portals in SpawnTown**
*   In `core/spawn_town.py`, add a mechanism to place portal objects on the map. These could be simple interactive objects.
*   Identify or create a graphic asset for the portals using available assets (e.g., something from `graphics/UNUSED/other` like `demon_pentagram-large*.png` or `xom_sparkles_blue.png`, or potentially a new asset).
*   Implement interaction logic for the portals. When the player interacts with a portal, it should trigger a scene transition to the corresponding dungeon scene (`SwampCaveDungeon`).

**Goal 6: Implement Scene Transition Logic**
*   In `core.game_engine.GameEngine`, add functionality to switch between different `BaseGameplayScene` instances. This might involve a method like `change_scene(new_scene_instance)`.
*   Modify the portal interaction logic in `SpawnTown` to call this `change_scene` method, passing an instance of `SwampCaveDungeon`.
*   Implement a similar portal or exit mechanism within the `SwampCaveDungeon` to allow the player to return to SpawnTown.

**Visualizing Scene Transitions:**

```mermaid
graph TD
    A[Start Game] --> B(SpawnTown Scene);
    B --> C{Interact with Portal};
    C -- To Swamp/Cave --> D(SwampCaveDungeon Scene);
    D --> E{Find Exit Portal};
    E -- To SpawnTown --> B;