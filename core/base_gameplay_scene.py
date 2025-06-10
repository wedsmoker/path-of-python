import pygame
import json  # Import json to read zone_data.json
import os  # Import os to construct file paths
from ui.dialogue_manager import DialogueManager
from core.scene_manager import BaseScene
from entities.player import Player
from ui.hud import HUD
from config.constants import (
    KEY_INVENTORY, KEY_SKILL_TREE, KEY_INTERACT, KEY_OPTIONS_MENU,
    STATE_INVENTORY, STATE_SKILL_TREE, STATE_PAUSE_MENU, STATE_SETTINGS_MENU, TILE_SIZE,
    KEY_RIGHT_MOUSE, KEY_SKILL_1, KEY_SKILL_2, KEY_SKILL_3, KEY_SKILL_4, KEY_PAGE_UP, KEY_PAGE_DOWN
)
import math # Import math for distance calculation


class BaseGameplayScene(BaseScene):
    def __init__(self, game, player=None, hud=None):
        super().__init__(game)
        self.player = player  # Player is now passed in or remains None
        self.hud = hud  # HUD is now passed in or remains None
        self.projectiles = pygame.sprite.Group()

        # Camera settings
        self.camera_x = 0
        self.camera_y = 0
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.zoom_level = 1.0
        self.map_width = 50  # Placeholder, will be updated when the map is loaded
        self.map_height = 30  # Placeholder, will be updated when the map is loaded
        self.tile_size = TILE_SIZE  # Get from constants
        self.frame_count = 0

        self.tile_images = {}
        self._load_tile_images()

        # Placeholder NPC for testing dialogue
        # In a real game, this would be managed by an NPC system
        self.npcs = [
            {"name": "Old Scavenger", "tile_x": 10, "tile_y": 10, "dialogue_id": "old_scavenger_intro"}
        ]


    def _load_tile_images(self):
        """Loads tile images based on zone_data.json."""
        try:
            # Use os.path.join for cross-platform path compatibility
            zone_data_path = os.path.join(os.getcwd(), "data", "zone_data.json")
            with open(zone_data_path, "r") as f:
                zone_data = json.load(f)

            # Assuming 'default_tileset' is always used for now
            tileset_paths = zone_data["tile_sets"]["default_tileset"]
            for tile_type, path in tileset_paths.items():
                try:
                    full_path = os.path.join(os.getcwd(), path)
                    if not os.path.exists(full_path):
                        print(f"BaseGameplayScene: Error: Tile image file not found: {full_path}")
                        self.tile_images[tile_type] = pygame.Surface((self.tile_size, self.tile_size))
                        self.tile_images[tile_type].fill((255, 0, 255))  # Magenta placeholder
                        continue

                    image = pygame.image.load(full_path).convert_alpha()
                    self.tile_images[tile_type] = image
                    # print(f"BaseGameplayScene: Loaded tile image: {tile_type} from {full_path}")  # Added logging
                except pygame.error as e:
                    print(f"BaseGameplayScene: Warning: Could not load tile image {full_path}: {e}")
                    self.tile_images[tile_type] = pygame.Surface((self.tile_size, self.tile_size))
                    self.tile_images[tile_type].fill((255, 0, 255))  # Magenta placeholder
        except FileNotFoundError:
            print("BaseGameplayScene: Error: data/zone_data.json not found. Cannot load tile images.")
        except json.JSONDecodeError:
            print("BaseGameplayScene: Error: Could not decode data/zone_data.json. Check JSON format.")
        except KeyError as e:
            print(f"BaseGameplayScene: Error: Missing key in zone_data.json: {e}")

    def debug_log(self):
        if self.frame_count % 60 == 0:  # Log every second (assuming 60 FPS)
            # print(f"--- Debug Info (Frame {self.frame_count}) ---")
            # print(f"Camera X: {self.camera_x:.2f}, Camera Y: {self.camera_y:.2f}, Zoom: {self.zoom_level:.2f}")
            if self.player:
                # print(f"Player World X: {self.player.rect.x}, Player World Y: {self.player.rect.y}")
                pass
            else:
                # print("Player object is None in BaseGameplayScene.")
                pass
            # print(f"Map Width: {self.map_width}, Map Height: {self.tile_size}")
            # print(f"Visible Width: {self.game.settings.SCREEN_WIDTH / self.zoom_level:.2f}, Visible Height: {self.game.settings.SCREEN_HEIGHT / self.zoom_level:.2f}")
            # print(f"Max Camera X: {max(0, self.map_width * self.tile_size - (self.game.settings.SCREEN_WIDTH / self.zoom_level)):.2f}")
            # print(f"Max Camera Y: {max(0, self.map_height * self.tile_size - (self.game.settings.SCREEN_HEIGHT / self.zoom_level)):.2f}")
            if not self.tile_images:
                # print("WARNING: No tile images loaded!")
                pass
            else:
                # print(f"Loaded {len(self.tile_images)} tile images.")
                pass
            # print("------------------------------------")
            pass


    def handle_event(self, event):
        if self.game.dialogue_manager.is_dialogue_active():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.game.dialogue_manager.choose_option(0)
                elif event.key == pygame.K_2:
                    self.game.dialogue_manager.choose_option(1)
                elif event.key == pygame.K_3:
                    self.game.dialogue_manager.choose_option(2)
                elif event.key == pygame.K_4:
                    self.game.dialogue_manager.choose_option(3)
                elif event.key == pygame.K_ESCAPE: # Added to close dialogue
                    self.game.dialogue_manager.end_dialogue()
            return  # Consume event if dialogue is active

        if event.type == pygame.KEYDOWN:
            if event.key == KEY_INVENTORY:
                self.game.scene_manager.set_scene(STATE_INVENTORY, self.player)
            elif event.key == KEY_SKILL_TREE:
                self.game.scene_manager.set_scene(STATE_SKILL_TREE, self.player)
            elif event.key == pygame.K_ESCAPE:
                self.game.scene_manager.set_scene(STATE_PAUSE_MENU, player=self.player)
            elif event.key == KEY_OPTIONS_MENU:
                self.game.scene_manager.set_scene(STATE_SETTINGS_MENU, self.player)
            elif event.key == pygame.K_PLUS:
                self.zoom_level += 0.1
            elif event.key == pygame.K_MINUS:
                self.zoom_level -= 0.1
            elif event.key == pygame.K_LEFT:
                self.camera_offset_x -= 10
            elif event.key == pygame.K_RIGHT:
                self.camera_offset_x += 10
            elif event.key == pygame.K_UP:
                self.camera_offset_y -= 10
            elif event.key == pygame.K_DOWN:
                self.camera_offset_y += 10
            elif event.key == KEY_INTERACT: # Handle interaction key
                if self.player:
                    # Check for interaction with NPCs
                    for npc in self.npcs:
                        npc_world_x = npc["tile_x"] * TILE_SIZE + TILE_SIZE // 2
                        npc_world_y = npc["tile_y"] * TILE_SIZE + TILE_SIZE // 2
                        player_world_x = self.player.rect.centerx
                        player_world_y = self.player.rect.centery

                        distance = math.hypot(player_world_x - npc_world_x, player_world_y - npc_world_y)

                        # Define interaction distance (e.g., 1.5 tiles)
                        interaction_distance = TILE_SIZE * 1.5

                        if distance < interaction_distance:
                            # Start dialogue with this NPC
                            self.game.dialogue_manager.start_dialogue(npc["dialogue_id"])
                            break # Interact with only one NPC at a time

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left-click
            # Get the mouse position in world coordinates
            world_x = (event.pos[0] + self.camera_x * self.zoom_level) / self.zoom_level
            world_y = (event.pos[1] + self.camera_y * self.zoom_level) / self.zoom_level
            if self.player:
                self.player.set_target(world_x, world_y)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == KEY_RIGHT_MOUSE:
                if self.player:
                    self.player.activate_arc()

    def update(self, dt, entities=None):
        if self.player:  # Only update player if player exists
            self.player.update(dt)
        if self.hud:  # Only update HUD if HUD exists
            self.hud.update(dt, entities)

        self.debug_log()
        self.frame_count += 1

        # Get map dimensions and tile size from the current scene (e.g., SpawnTown)
        if hasattr(self.game, 'current_scene') and isinstance(self.game.current_scene, BaseGameplayScene):
            # Ensure we are getting the map dimensions from the actual scene instance, not the base class placeholder
            if hasattr(self.game.current_scene, 'map_width') and hasattr(self.game.current_scene, 'map_height'):
                self.map_width = self.game.current_scene.map_width
                self.map_height = self.game.current_scene.map_height
            else:
                # Fallback if map dimensions are not set in the current scene (shouldn't happen for gameplay scenes)
                # print("BaseGameplayScene: Warning: Current scene does not have map_width/height. Using defaults.")
                self.map_width = 50
                self.map_height = 30
        # Removed the else block that set map_width/height to 50/30,
        # as it was causing restricted movement when the actual map was larger.

        if hasattr(self, 'display_death_message') and self.display_death_message:
            current_time = pygame.time.get_ticks()
            if current_time - self.death_message_start_time > self.death_message_duration:
                self.display_death_message = False
                # Respawn the player in spawntown
                self.game.scene_manager.set_scene("spawn_town")
                if self.player:
                    self.player.current_life = self.player.max_life
                    self.player.current_mana = self.player.max_mana


        # Limit zoom level
        self.zoom_level = max(0.5, min(self.zoom_level, 2.0))

        # Limit camera offset
        self.camera_offset_x = max(-200, min(self.camera_offset_x, 200))
        self.camera_offset_y = max(-200, min(self.camera_offset_y, 200))

        # Calculate camera position
        if self.player:  # Only calculate camera if player exists
            self.camera_x = self.player.rect.centerx - (self.game.settings.SCREEN_WIDTH / 2) / self.zoom_level + self.camera_offset_x
            self.camera_y = self.player.rect.centery - (self.game.settings.SCREEN_HEIGHT / 2) / self.zoom_level + self.camera_offset_y
        else:
            self.camera_x = 0
            self.camera_y = 0
        # else:
        #     self.camera_x = 0
        #     self.camera_y = 0
        # else:
        #     pass

        # Clamp camera position to map boundaries
        min_x = 0
        min_y = 0
        visible_width = self.game.settings.SCREEN_WIDTH / self.zoom_level
        max_x = max(0, self.map_width * self.tile_size - visible_width)
        visible_height = self.game.settings.SCREEN_HEIGHT / self.zoom_level
        max_y = max(0, self.map_height * self.tile_size - visible_height)

        self.camera_x = max(min_x, min(self.camera_x, max_x))
        self.camera_y = max(min_y, min(self.camera_y, max_y))


    def draw(self, screen):
        hud_drawn = False
        if hasattr(self.game, 'current_scene'):
            # Draw the map (tiles)
            if hasattr(self.game.current_scene, 'tile_map'):
                # Add debug logging for tile map drawing
                if self.frame_count % 60 == 0:
                    # print(f"BaseGameplayScene: Drawing tile map. Map dimensions: {self.map_width}x{self.map_height}")
                    pass
                if not self.game.current_scene.tile_map:
                    # print("BaseGameplayScene: WARNING: tile_map is empty!")
                    pass # Added pass here
                else:
                    for y, row in enumerate(self.game.current_scene.tile_map):
                        for x, tile_type_value in enumerate(row):
                            # Calculate the tile's position relative to the camera
                            tile_x = (x * self.tile_size - self.camera_x) * self.zoom_level
                            tile_y = (y * self.tile_size - self.camera_y) * self.zoom_level

                            # Check if the tile is within the visible screen area
                            screen_width = self.game.settings.SCREEN_WIDTH
                            screen_height = self.game.settings.SCREEN_HEIGHT

                            if (tile_x + self.tile_size * self.zoom_level > 0 and
                                    tile_y + self.tile_size * self.zoom_level > 0 and
                                    tile_x < screen_width and
                                    tile_y < screen_height):

                                # Get the tile image
                                tile_image = self.tile_images.get(tile_type_value)
                                if tile_image:
                                    scaled_tile_image = pygame.transform.scale(tile_image, (int(self.tile_size * self.zoom_level), int(self.tile_size * self.zoom_level)))
                                    screen.blit(scaled_tile_image, (tile_x, tile_y))
                                else:
                                    # Fallback to drawing a colored rectangle if image not found
                                    color = (255, 0, 255)  # Magenta for missing textures
                                    pygame.draw.rect(screen, color, (tile_x, tile_y, self.tile_size * self.zoom_level, self.tile_size * self.zoom_level))
                                    if self.frame_count % 60 == 0:
                                        # print(f"BaseGameplayScene: WARNING: No image for tile type '{tile_type_value}' at ({x},{y}). Drawing magenta.")
                                        # print(f"BaseGameplayScene: tile_x: {tile_x}, tile_y: {tile_y}, screen_width: {screen_width}, screen_height: {screen_height}")  # Added logging
                                        pass
                            else:
                                if self.frame_count % 60 == 0:
                                    # print(f"BaseGameplayScene: Tile at ({{x}},{{y}}) is off-screen. Screen pos: ({{tile_x:.2f}}, {{tile_y:.2f}})") # Added logging
                                    pass

            # Draw the player (centered on screen)
            if self.player:  # Only draw player if player exists
                self.player.draw(screen)

            # Draw the HUD (unaffected by camera)
            if self.hud:  # Only draw HUD if HUD exists
                self.hud.draw(screen)
                hud_drawn = True

            # Draw dialogue if active
            if self.game.dialogue_manager.is_dialogue_active():
                self.game.dialogue_manager.draw(screen)

        else:
            hud_drawn = False

        if hasattr(self, 'display_death_message') and self.display_death_message:
            # Load the defeat window image
            try:
                defeat_image = pygame.image.load(os.path.join(os.getcwd(), "graphics", "gui", "window_defeat.png")).convert_alpha()
            except FileNotFoundError:
                print("Defeat window image not found!")
                defeat_image = None

            # Get the screen dimensions
            screen_width = self.game.settings.SCREEN_WIDTH
            screen_height = self.game.settings.SCREEN_HEIGHT

            # Calculate the center position
            center_x = screen_width // 2
            center_y = screen_height // 2

            # If the defeat image is loaded, blit it to the center of the screen
            if defeat_image:
                defeat_rect = defeat_image.get_rect(center=(center_x, center_y))
                screen.blit(defeat_image, defeat_rect)

            # Display "YOU DIED" message
            font = pygame.font.Font(None, 100)
            text_surface = font.render("YOU DIED", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(center_x, center_y))
            screen.blit(text_surface, text_rect)

            # Update the display
            pygame.display.flip()

            # Wait for a few seconds
            pygame.time.delay(3000)

            # Send the player to SpawnTown
            self.game.scene_manager.set_scene("spawn_town")
