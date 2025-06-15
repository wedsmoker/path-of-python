# Boss Portal and Unique Boss Room Plan (Refined)

This plan outlines the steps to add boss portals and unique boss rooms to each dungeon level in "Path of Python" with minimal new files and using existing assets where possible, while strictly avoiding modifications to existing core game files for the main logic.

## Objective

Introduce a new, self-contained system that can interact with the existing game state (like the current dungeon scene) without changing its fundamental structure or code, to manage the creation, placement, and interaction of boss portals and manage the transition to and from unique boss room scenes. This version focuses on simplicity with 5 unique bosses, 1 generic boss room layout using existing tilesets, and no modifications to `data/enemy_data.json`.

## Refined Detailed Plan

The core idea remains introducing a new, self-contained system, but we will reduce the number of new files by consolidating data and using a single generic boss room scene class, along with a single generic boss room layout file.

1.  **Create New Data Files:**
    *   [`data/boss_config.json`](data/boss_config.json): This single file will contain:
        *   Definitions for the 5 unique bosses (stats, sprites, complex attack patterns, etc.).
        *   A mapping from each existing dungeon type (e.g., "grass", "ice_cave") to:
            *   The key for one of the 5 boss definitions in this same file.
            *   The path to the single generic boss room layout file (`data/boss_rooms/generic_boss_layout.json`).
            *   The name of an *existing* tileset to use for rendering the generic boss room layout in that specific dungeon's context.
    *   [`data/boss_rooms/generic_boss_layout.json`](data/boss_rooms/generic_boss_layout.json): A single, simple, and small JSON file defining a generic tilemap layout for all boss rooms, using tile types that exist across various tilesets.

2.  **Create New Entity Files:**
    *   [`entities/bosses/base_boss.py`](entities/bosses/base_boss.py): A new base class for boss entities, likely inheriting from the existing `Enemy` class, providing common structure.
    *   [`entities/bosses/<boss_type_1-5>.py`](entities/bosses/<boss_type_1-5>.py): Five new Python files, one for each unique boss, inheriting from `BaseBoss` and implementing their specific complex behaviors and bullet hell attack patterns.
    *   [`entities/boss_portal.py`](entities/boss_portal.py): A new Python file defining the interactive boss portal entity.

3.  **Create New Scene File:**
    *   [`core/boss_scenes/boss_room_scene.py`](core/boss_scenes/boss_room_scene.py): A single new class for all boss room scenes. It will inherit from `core.base_gameplay_scene.BaseGameplayScene` or similar. When instantiated, it will take the path to `generic_boss_layout.json`, the boss type key, and the required tileset name as parameters (obtained from `boss_config.json` by the manager). It will load the specified layout, use the designated existing tileset for rendering, and instantiate the correct boss entity.

4.  **Create Boss System Manager:**
    *   [`core/boss_system_manager.py`](core/boss_system_manager.py): This central manager will:
        *   Load `data/boss_config.json`.
        *   Find a suitable location in the *currently loaded* dungeon scene for the portal.
        *   Instantiate and add the `Portal` entity to the dungeon scene.
        *   Listen for portal interaction.
        *   On interaction, look up the boss type and required tileset name in `data/boss_config.json` based on the current dungeon type.
        *   Instantiate the single `BossRoomScene` class with the path to `generic_boss_layout.json`, the boss type key, and the tileset name.
        *   Initiate a scene transition to the new `BossRoomScene`.
        *   Handle the return transition after the boss fight.
        *   Track defeated bosses.

5.  **Integration (Minimal Change - Post-Planning & Testing):**
    *   A minimal change in the main game loop or scene management will be needed to instantiate the `BossSystemManager` and pass it the current dungeon scene when it loads.

## Mermaid Diagram (Refined)

```mermaid
graph TD
    A[Existing Dungeon Scene Loaded] --> B{Boss System Manager};
    B --> C[Load boss_config.json];
    B --> D[Scan Dungeon Layout for Portal Spot];
    D --> E[Create Portal Entity];
    E --> F[Add Portal to Dungeon Entities];
    F --> G[Player Interacts with Portal];
    G --> H{Boss System Manager};
    H --> I[Lookup Boss Type & Tileset in boss_config.json];
    I --> J[Instantiate Generic BossRoomScene with Data & Generic Layout Path];
    J --> K[Initiate Scene Transition];
    K --> L[BossRoomScene Loaded];
    L --> M[Load generic_boss_layout.json];
    L --> N[Use Specified Existing Tileset];
    L --> O[Instantiate Correct Boss Entity (1 of 5)];
    O --> P[Boss Fight];
    P --> Q{Boss Defeated?};
    Q -- Yes --> R[Update Boss Status in Manager];
    R --> S[Transition Back to Dungeon];
    Q -- No --> P;

    %% Styling for clarity
    classDef existing fill:#f9f,stroke:#333,stroke-width:2px;
    classDef new fill:#ccf,stroke:#333,stroke-width:2px;
    class A existing;
    class B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S new;