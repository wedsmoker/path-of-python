import pygame
import json
import os
import random
import math
from core.base_gameplay_scene import BaseGameplayScene
from entities.player import Player
from entities.npc import NPC
from entities.enemy import Enemy
from ui.hud import HUD
from world.map_generator import MapGenerator
from core.pathfinding import Pathfinding
from config.constants import (
    ENEMY_SPAWN_DISTANCE, ENEMY_SPAWN_COOLDOWN, TILE_SIZE,
    KEY_SKILL_TREE, KEY_INVENTORY, KEY_PAUSE_MENU, KEY_SETTINGS_MENU
)

class SwampCaveDungeon(BaseGameplayScene):
    def __init__(self, game, player, hud):
        super().__init__(game, player, hud)
        self.name = "SwampCaveDungeon"

        # Load dungeon data from JSON
        self.dungeon_data = self.load_dungeon_data("swamp_cave")
        self.allowed_enemies = self.dungeon_data.get("allowed_enemies", [])
        self.enemy_details = self.dungeon_data.get("enemy_details", {})

        self.enemies = pygame.sprite.Group()
        self.effects = pygame.sprite.Group() # Add effects group
        self.last_enemy_spawn_time = pygame.time.get_ticks()

        # Map generation placeholder - use settings from JSON if available
        map_settings = self.dungeon_data.get("map_settings", {"width": 100, "height": 100})
        map_generator = MapGenerator(map_settings["width"], map_settings["height"])
        all_map_data = map_generator.generate_all()
        self.tile_map = all_map_data['map']
        self.map_width = len(self.tile_map[0])
        self.map_height = len(self.tile_map)

        # Translate tile types to swamp cave tileset keys
        self.tile_map = self._translate_tile_types(self.tile_map)

        # Pathfinding
        self.pathfinding = Pathfinding(game)

        # Placeholder for the exit portal
        # Use location from JSON if available, otherwise a default
        exit_portal_location = self.dungeon_data.get("portals", [{}])[0].get("location", [50, 50])
        self.exit_portal_rect = pygame.Rect(exit_portal_location[0], exit_portal_location[1], 64, 64) # Example size
        # self.exit_portal_color = (0, 0, 255) # Blue color for exit placeholder - No longer needed

        # Load assets
        self.assets = {}
        self._load_assets()

        # "NOT HERE" message
        self.display_message = False
        self.message_start_time = 0
        self.message_duration = 5000 # 5 seconds


    def _load_tile_images(self):
        """Loads tile images specifically for the swamp cave dungeon."""
        try:
            zone_data_path = os.path.join(os.getcwd(), "data", "zone_data.json")
            with open(zone_data_path, "r") as f:
                zone_data = json.load(f)

            # Load the swamp_cave_tileset
            tileset_paths = zone_data["tile_sets"]["swamp_cave_tileset"]
            for tile_type, path in tileset_paths.items():
                try:
                    full_path = os.path.join(os.getcwd(), path)
                    if not os.path.exists(full_path):
                        print(f"SwampCaveDungeon: Error: Tile image file not found: {full_path}")
                        self.tile_images[tile_type] = pygame.Surface((self.tile_size, self.tile_size))
                        self.tile_images[tile_type].fill((255, 0, 255))  # Magenta placeholder
                        continue

                    image = pygame.image.load(full_path).convert_alpha()
                    self.tile_images[tile_type] = image
                except pygame.error as e:
                    print(f"SwampCaveDungeon: Warning: Could not load tile image {full_path}: {e}")
                    self.tile_images[tile_type] = pygame.Surface((self.tile_size, self.tile_size))
                    self.tile_images[tile_type].fill((255, 0, 255))  # Magenta placeholder
        except FileNotFoundError:
            print("SwampCaveDungeon: Error: data/zone_data.json not found. Cannot load tile images.")
        except json.JSONDecodeError:
            print("SwampCaveDungeon: Error: Could not decode data/zone_data.json. Check JSON format.")
        except KeyError as e:
            print(f"SwampCaveDungeon: Error: Missing key in zone_data.json or swamp_cave_tileset: {e}")

    def _translate_tile_types(self, tile_map):
        """Translates default tile types to swamp cave tileset keys."""
        translation_map = {
            'grass': 'floor_swamp',
            'sand': 'floor_bog',
            'water': 'water_murky',
            'forest': 'wall_vines',
            'building': 'wall_stone_dark',
            'street': 'floor_swamp', # Using swamp floor for streets in dungeon
            'rubble': 'floor_bog'    # Using bog floor for rubble in dungeon
        }
        translated_map = []
        for row in tile_map:
            translated_row = [translation_map.get(tile_type, tile_type) for tile_type in row]
            translated_map.append(translated_row)
        return translated_map

    def _load_assets(self):
        """Loads general assets like portals from zone_data.json."""
        try:
            zone_data_path = os.path.join(os.getcwd(), "data", "zone_data.json")
            with open(zone_data_path, "r") as f:
                zone_data = json.load(f)

            # Load portal assets
            portal_assets = zone_data.get("assets", {}).get("portals", {})
            for asset_key, path in portal_assets.items():
                try:
                    full_path = os.path.join(os.getcwd(), path)
                    if not os.path.exists(full_path):
                        print(f"SwampCaveDungeon: Error: Asset file not found: {full_path}")
                        self.assets[asset_key] = None # Store None or a placeholder if file not found
                        continue

                    image = pygame.image.load(full_path).convert_alpha()
                    self.assets[asset_key] = image
                except pygame.error as e:
                    print(f"SwampCaveDungeon: Warning: Could not load asset image {full_path}: {e}")
                    self.assets[asset_key] = None # Store None or a placeholder on error
        except FileNotFoundError:
            print("SwampCaveDungeon: Error: data/zone_data.json not found. Cannot load assets.")
        except json.JSONDecodeError:
            print("SwampCaveDungeon: Error: Could not decode data/zone_data.json. Check JSON format.")
        except KeyError as e:
            print(f"SwampCaveDungeon: Error: Missing key in zone_data.json assets: {e}")


    def load_dungeon_data(self, dungeon_key):
        """Loads data for a specific dungeon from dungeons.json."""
        dungeons_data_path = os.path.join(os.getcwd(), "data", "dungeons.json")
        try:
            with open(dungeons_data_path, "r") as f:
                all_dungeons_data = json.load(f)
            return all_dungeons_data.get("dungeons", {}).get(dungeon_key, {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading dungeon data from {dungeons_data_path}: {e}")
            return {}

    def spawn_enemy(self):
        """Spawns a new enemy at a random location within a certain distance of the player."""
        if not self.allowed_enemies:
            return

        enemy_type_key = random.choice(self.allowed_enemies)
        enemy_data = self.enemy_details.get(enemy_type_key)

        if not enemy_data:
            print(f"Warning: No details found for enemy type '{enemy_type_key}' in dungeons.json")
            return

        angle = random.uniform(0, 2 * math.pi)
        player_pos = self.player.rect.center
        x = player_pos[0] + ENEMY_SPAWN_DISTANCE * math.cos(angle)
        y = player_pos[1] + ENEMY_SPAWN_DISTANCE * math.sin(angle)

        # Create enemy using data from JSON
        new_enemy = Enemy(self.game, x, y, enemy_data)
        self.enemies.add(new_enemy)
        # print(f"Spawned a {new_enemy.name} at ({int(x)}, {int(y)})!") # Uncomment for debugging

    def handle_event(self, event):
        super().handle_event(event)
        # Dungeon specific event handling here

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left-click
            # Check for exit portal interaction
            # Calculate portal's screen position
            portal_screen_x = (self.exit_portal_rect.x - self.camera_x) * self.zoom_level
            portal_screen_y = (self.exit_portal_rect.y - self.camera_x) * self.zoom_level

            # Create a rect for the portal at its screen position
            portal_screen_rect = pygame.Rect(portal_screen_x, portal_screen_y,
                                             self.exit_portal_rect.width * self.zoom_level,
                                             self.exit_portal_rect.height * self.zoom_level)

            if portal_screen_rect.collidepoint(event.pos):
                print("Interacted with exit portal! Changing scene...") # Debug print
                # Trigger scene change back to SpawnTown
                self.game.scene_manager.set_scene("spawn_town")

        # Disable menu keys in dungeon
        if event.type == pygame.KEYDOWN:
            if event.key in (KEY_SKILL_TREE, KEY_INVENTORY, KEY_PAUSE_MENU, KEY_SETTINGS_MENU):
                self.display_message = True
                self.message_start_time = pygame.time.get_ticks()
                return # Consume the event


    def update(self, dt):
        current_time = pygame.time.get_ticks()

        # Enemy Spawning Logic
        if current_time - self.last_enemy_spawn_time > ENEMY_SPAWN_COOLDOWN:
            if len(self.enemies) < 10:  # Allow slightly more enemies in dungeon
                self.spawn_enemy()
                self.last_enemy_spawn_time = current_time

        # Update Enemies
        self.enemies.update(dt)
        self.effects.update(dt) # Update effects

        # Combine entities for minimap (only enemies for now)
        all_entities = self.enemies.sprites() # TODO: Add dungeon specific NPCs or objects

        super().update(dt, entities=all_entities)

        # Check if message should be displayed
        if self.display_message:
            if current_time - self.message_start_time > self.message_duration:
                self.display_message = False

    def draw(self, screen):
        super().draw(screen)
        # Draw dungeon specific elements here (e.g., enemies)

        # Draw Enemies relative to the camera
        for enemy in self.enemies:
            enemy_screen_x = (enemy.rect.x - self.camera_x) * self.zoom_level
            enemy_screen_y = (enemy.rect.y - self.camera_y) * self.zoom_level

            # Scale Enemy image
            scaled_enemy_image = pygame.transform.scale(enemy.image, (int(enemy.rect.width * self.zoom_level), int(enemy.rect.height * self.zoom_level)))

            screen.blit(scaled_enemy_image, (enemy_screen_x, enemy_screen_y))

        # Draw the exit portal graphic
        if "dungeon_portal" in self.assets and self.assets["dungeon_portal"] is not None:
            portal_image = self.assets["dungeon_portal"]
            scaled_portal_image = pygame.transform.scale(portal_image, (int(self.exit_portal_rect.width * self.zoom_level), int(self.exit_portal_rect.height * self.zoom_level)))
            exit_portal_screen_x = (self.exit_portal_rect.x - self.camera_x) * self.zoom_level
            exit_portal_screen_y = (self.exit_portal_rect.y - self.camera_x) * self.zoom_level
            screen.blit(scaled_portal_image, (exit_portal_screen_x, exit_portal_screen_y))
        else:
             # Fallback to drawing the placeholder rectangle if the image didn't load
            exit_portal_screen_x = (self.exit_portal_rect.x - self.camera_x) * self.zoom_level
            exit_portal_screen_y = (self.exit_portal_rect.y - self.camera_x) * self.zoom_level
            scaled_exit_portal_width = int(self.exit_portal_rect.width * self.zoom_level)
            scaled_exit_portal_height = int(self.exit_portal_rect.height * self.zoom_level)
            scaled_exit_portal_rect = pygame.Rect(exit_portal_screen_x, exit_portal_screen_y, scaled_exit_portal_width, scaled_exit_portal_height)
            pygame.draw.rect(screen, (0, 0, 255), scaled_exit_portal_rect) # Blue color for exit placeholder

        # Draw effects
        for effect in self.effects:
            effect_screen_x = (effect.rect.x - self.camera_x) * self.zoom_level
            effect_screen_y = (effect.rect.y - self.camera_x) * self.zoom_level
            screen.blit(effect.image, (effect_screen_x, effect_screen_y))

        # Display "NOT HERE" message
        if self.display_message:
            font = pygame.font.Font(None, 50)
            text_surface = font.render("NOT HERE", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)

        # TODO: Draw dungeon specific NPCs or objects