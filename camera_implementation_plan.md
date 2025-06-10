# Camera Implementation Plan

## Goal

Implement a fixed camera system with zoom and offset features to allow exploration of large, generated gameplay maps.

## Plan

**1. Modify `BaseGameplayScene.draw()`:**

*   Calculate the offset based on the player's position and the desired camera offset.
*   Apply the zoom level to the scaling of the game elements.
*   Draw the player at the center of the screen (or a fixed offset from the center).
*   Draw other game elements (tiles, enemies, decorations) at positions offset from the player's position, taking into account the zoom level and camera offset.

**2. Implement Zoom Controls:**

*   Add input handling for zoom in and zoom out actions (e.g., using the mouse wheel or keyboard keys).
*   Update the zoom level based on the input.
*   Limit the zoom level to a reasonable range to prevent excessive zooming in or out.

**3. Implement Camera Offset:**

*   Add variables to store the camera's x and y offset.
*   Allow the user to adjust the camera offset (e.g., using keyboard keys or mouse movement).
*   Clamp the camera offset to a reasonable range.

**4. Implement Map Boundary Checks:**

*   Get Map Dimensions:
    *   In `BaseGameplayScene`, retrieve the map width and height from the `MapGenerator` or from the loaded map data. Store these values as `self.map_width` and `self.map_height`.
    *   Also, get the tile size from `config/constants.py` and store it as `self.tile_size`.
*   Calculate Camera Boundaries:
    *   Calculate the minimum and maximum x and y coordinates for the camera based on the map dimensions, tile size, screen dimensions, zoom level, and camera offset.
        *   `min_x = 0`
        *   `min_y = 0`
        *   `max_x = self.map_width * self.tile_size - self.game.settings.SCREEN_WIDTH / self.zoom_level + self.camera_offset_x`
        *   `max_y = self.map_height * self.tile_size - self.game.settings.SCREEN_HEIGHT / self.zoom_level + self.camera_offset_y`
*   Clamp Camera Position:
    *   Before drawing any game elements, calculate the camera's x and y position based on the player's position and the camera offset.
    *   Clamp the camera's x and y position to the calculated boundaries:
        *   `camera_x = max(min_x, min(camera_x, max_x))`
        *   `camera_y = max(min_y, min(camera_y, max_y))`
*   Apply Camera Offset and Zoom:
    *   When drawing game elements, use the clamped `camera_x` and `camera_y` values to calculate the offset for each element's position.
    *   Apply the zoom level to the scaling of the game elements.

**5. Test and Refine:**

*   Test the camera system with different map sizes, player movement patterns, zoom levels, and camera offsets.
*   Pay close attention to the map boundaries to ensure the camera doesn't move beyond them.
*   Adjust the camera's behavior as needed to ensure a smooth and seamless experience.

## Progress

*   Implemented a fixed camera system with zoom and offset features.
*   Added input handling for zoom in and zoom out actions using the + and - keys.
*   Limited the zoom level to a range between 0.5 and 2.0.
*   Added input handling for adjusting the camera offset using the arrow keys.
*   Limited the camera offset to a range between -200 and 200 in both x and y directions.
*   Ensured that the map_width and map_height values in BaseGameplayScene are correctly initialized with the values from the SpawnTown scene.
*   The camera now follows the player correctly.

## Problems

*   Initially, the player was not visible and the UI was not drawing properly due to the draw calls being in the wrong place.
*   The background was not moving correctly with the camera.

## Fixes

*   Moved the player and HUD drawing code from `BaseGameplayScene.draw()` to `SpawnTown.draw()`.
*   Updated `SpawnTown.draw()` to offset the tile positions by the camera coordinates.
*   Corrected the player object initialization in `SpawnTown.py`
*   Updated `entities/player.py` to access the `current_scene` from the `SceneManager` instead of the `GameEngine`.

## Remaining Work

*   Implement zoom controls.
*   Implement camera offset controls.
*   Implement map boundary checks.

## Mermaid Diagram

```mermaid
graph LR
    A[Start] --> B{Modify BaseGameplayScene.draw()};
    B --> C[Calculate Camera Offset];
    C --> D[Apply Zoom Level];
    D --> E[Draw Player at Center];
    E --> F[Draw Other Elements with Offset and Zoom];
    F --> G{Implement Zoom Controls};
    G --> H[Add Input Handling for Zoom];
    H --> I[Update Zoom Level];
    I --> J[Limit Zoom Range];
    J --> K{Implement Camera Offset};
    K --> L[Add Offset Variables];
    L --> M[Allow User to Adjust Offset];
    M --> N[Clamp Offset Range];
    N --> O{Implement Map Boundary Checks};
    O --> P[Get Map Dimensions and Tile Size];
    P --> Q[Calculate Camera Boundaries];
    Q --> R[Clamp Camera Position];
    R --> S[Apply Camera Offset and Zoom];
    S --> T{Test and Refine};
    T --> U[Test with Different Settings];
    U --> V[Adjust Camera Behavior];
    V --> W[End];