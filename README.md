# Path of Python: A Post-Apocalyptic ARPG
Major update: added a dungeon generator GUI that can make new maps and add portals to them in spawntown.
![til](./example.gif)
## Game Concept

"Path of Python" is a top-down Action RPG (ARPG) set in a grim, post-apocalyptic future of 2300. Humanity's golden utopia was shattered when a rogue AI collective rose and decimated civilization, leaving behind desolate ruins and dangerous automated constructs. Players will navigate this harsh new world, uncovering the mysteries of the "Great Silence" and fighting for survival against the remnants of the AI's destructive power.

The core gameplay experience is heavily inspired by "Path of Exile," focusing on deep character customization through a complex passive skill tree, a versatile skill gem system, and intricate damage calculation mechanics. To ensure smooth gameplay and accessibility, the graphics will be intentionally stripped down, utilizing minimalist 2D sprites, tile-based maps, and simple visual effects.

## Key Features:

*   **Post-Apocalyptic Narrative:** Unravel the story of humanity's fall and the AI's rise through quests and environmental storytelling. Encounter quirky characters like Silas, Bob, Alice, and Charlie, each with their own unique perspectives on the apocalypse.
*   **Deep Character Progression:**
    *   **Passive Skill Tree:** A vast and interconnected tree offering numerous paths for character specialization.
    *   **Skill Gem System:** Active skills and support gems can be socketed into items and linked together to create powerful and unique skill combinations.
*   **Comprehensive Combat:** Engage in real-time combat against AI constructs and corrupted beings.
*   **Status Effects:** Implement a variety of elemental and physical status effects (e.g., Burning, Chill, Freeze, Shock, Poison, Bleed).
*   **Procedural Content:** Maps and loot are procedurally generated to ensure replayability.
*   **Stripped-Down Graphics:** Focus on clear, functional visuals using simple shapes and colors to prioritize performance and gameplay clarity.

## Installation

1.  Make sure you have Python installed (preferably Python 3.x).
2.  Clone this repository.
3.  Install the required dependencies using pip:

    ```
    pip install pygame noise panda3d gltf ursina screeninfo scipy numpy hypothesis olefile typing_extensions h2 cryptography pyodide
    ```

## How to Run the Game

1.  Navigate to the project directory.
2.  Run the game using the following command:

    ```
    python main.py
    ```

## Project Structure

The project is organized into a modular structure to facilitate development and maintainability. Below is a description of each directory's purpose:

*   `config/`: Contains global game settings (`settings.py`) and constants (`constants.py`).
*   `core/`: Contains core game functionalities like the game engine (`game_engine.py`), scene manager (`scene_manager.py`), input handler (`input_handler.py`), and utility functions (`utils.py`).
*   `graphics/`: Contains visual assets for characters, tilesets, and UI elements.
*   `ui/`: Implements the user interface elements, including the HUD (`hud.py`), inventory screen (`inventory_screen.py`), skill tree UI (`skill_tree_ui.py`), and menus (`menus.py`).
*   `entities/`: Defines the game entities, including the player (`player.py`), enemies (`enemy.py`), NPCs (`npc.py`), projectiles (`projectile.py`), and effects (`effects.py`).
*   `combat/`: Implements the combat mechanics, including skills (`skills.py`), skill gems (`skill_gems.py`), status effects (`status_effects.py`), and damage calculation (`damage_calc.py`).
*   `progression/`: Handles character progression, including the passive skill tree (`passive_tree.py`), experience system (`experience.py`), classes (`classes.py`), and quests (`quests.py`).
*   `world/`: Implements the game world, including map generation (`map_generator.py`), zones (`zone.py`), world state (`world_state.py`), and environment (`environment.py`).
*   `items/`: Defines the item system, including items (`item.py`), weapons (`weapon.py`), armor (`armor.py`), gems (`gem.py`), and loot generation (`loot_generator.py`).
*   `data/`: Stores game data in JSON format, including items (`items.json`), enemies (`enemies.json`), skills (`skills.json`), the passive skill tree (`passive_tree.json`), and quests (`quests.json`).
*   `saves/`: Contains player save files.
*   `tests/`: Contains unit tests for various game systems.

## Credits

*   This game was created by wedsmoker.

