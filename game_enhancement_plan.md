# Game Enhancement Plan

This plan outlines the steps to address the user's requests for enhancing the game.

**Phase 1: Bug Fixing and Foundation**

1.  **Investigate Inventory/Settings Crash:**
    *   Goal: Identify the cause of the crashes in the inventory and settings screens when opened from spawntown or dungeons.
    *   Action: Use debugging techniques (print statements, Pygame debugger if available) to trace the code execution and pinpoint the error.
2.  **Larger Player Sprites:**
    *   Goal: Increase the size of player sprites while maintaining proportions.
    *   Action: Modify the player sprite drawing code to scale the sprites appropriately.
3.  **Basic Inventory Screen:**
    *   Goal: Create a functional inventory screen.
    *   Action: Implement a basic inventory screen using Pygame's UI elements.
4.  **Item List JSON:**
    *   Goal: Create a JSON file to store item definitions.
    *   Action: Design a JSON schema for items, including properties like name, description, graphics, stats, etc. Populate the JSON file with sample items.

**Phase 2: Skill Tree and Combat**

5.  **Skill Tree Implementation:**
    *   Goal: Implement a skill tree system.
    *   Action: Design a skill tree structure, create JSON templates for skills, and implement the logic for unlocking and activating skills.
6.  **Skill Activation and Effects:**
    *   Goal: Implement skill activation on **right click, page up, page down, and QWERTY keys** with appropriate effects and icons.
    *   Action: Modify the player's input handling to trigger skills on the specified keys and mouse button. Implement visual effects for skills using graphics from the `graphics` folder.
7.  **Enemy AI and Combat:**
    *   Goal: Implement basic enemy AI, including movement, attacking, and taking damage from skills.
    *   Action: Implement enemy movement patterns (bobbing, moving around). Implement enemy attack logic, including skill selection and visual effects.
8.  **Experience and Gold System:**
    *   Goal: Implement experience and gold systems.
    *   Action: Add experience gain on enemy kill. Display experience on the HUD. Implement a gold system where enemies drop gold.

**Phase 3: World and UI Enhancements**

9.  **Spawntown Shops:**
    *   Goal: Add shops to spawntown where players can buy items.
    *   Action: Implement shop NPCs and UI. Allow players to browse and purchase items using gold.
10. **Developer Cheat Tool:**
    *   Goal: Create a temporary cheat tool for developers.
    *   Action: Implement a cheat menu or console command to add items, skills, gold, and level up the player.
11. **HUD Redesign:**
    *   Goal: Redesign the HUD using the new graphics in the `graphics/gui` folder.
    *   Action: Analyze the new graphics format. Update the HUD code to use the new graphics while maintaining functionality.
12. **Control Mapping:**
    *   Goal: **Remove control mapping for skills, as they are now fixed to right click, page up, page down, and QWERTY keys.**
    *   Action: N/A
13. **Potion Usage:**
    *   Goal: Implement potion usage with number keys 1-5.
    *   Action: Add input handling for number keys to trigger potion usage.
14. **Title Screen Enhancements:**
    *   Goal: Add more content and functionality to the main title screen.
    *   Action: Enhance the title screen with new graphics and features, maintaining the game's style.
15. **Spawntown Complexity:**
    *   Goal: Add more town drawing complexity and tile variations in spawntown.
    *   Action: Expand the tile set and town generation logic to create more varied and interesting town layouts.
58a. **Currently Working On:** Expanding the tile set and town generation logic to create more varied and interesting town layouts.

**Phase 4: Content Expansion**

16. **JSON Content Expansion:**
    *   Goal: Add more content to all JSON files (dialog, items, skill tree, etc.).
    *   Action: Populate the JSON files with a large amount of content to provide a rich and engaging game experience.

**Mermaid Diagram:**

```mermaid
graph TD
    A[Phase 1: Bug Fixing and Foundation] --> B(Investigate Inventory/Settings Crash);
    A --> C(Larger Player Sprites);
    A --> D(Basic Inventory Screen);
    A --> E(Item List JSON);
    F[Phase 2: Skill Tree and Combat] --> G(Skill Tree Implementation);
    F --> H(Skill Activation and Effects - Right Click, QWERTY, Page Up/Down);
    F --> I(Enemy AI and Combat);
    F --> J(Experience and Gold System);
    K[Phase 3: World and UI Enhancements] --> L(Spawntown Shops);
    K --> M(Developer Cheat Tool);
    K --> N(HUD Redesign);
    K --> P(Potion Usage);
    K --> Q(Title Screen Enhancements);
    K --> R(Spawntown Complexity);
    S[Phase 4: Content Expansion] --> T(JSON Content Expansion);