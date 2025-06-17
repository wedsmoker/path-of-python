import pygame
import json
import os
import random
import math # Import math for distance calculation
from entities.boss_portal import BossPortal # Assuming BossPortal is needed
from config.constants import TILE_SIZE, KEY_INTERACT # Assuming TILE_SIZE and KEY_INTERACT are needed
from core.boss_scenes.boss_room_scene import BossRoomScene # To transition to the boss scene
from core.input_handler import InputHandler # Import InputHandler

class BossSystemManager:
    def __init__(self, game):
        self.game = game
        self.boss_config = self._load_boss_config()
        self.enemy_data = self._load_enemy_data() # Load enemy data
        self.active_portals = pygame.sprite.Group() # Group to hold active boss portals
        self.input_handler = InputHandler() # Instantiate InputHandler

    def _load_boss_config(self):
        """Loads the boss configuration from boss_config.json."""
        boss_config_path = os.path.join(os.getcwd(), "data", "boss_config.json")
        try:
            with open(boss_config_path, "r") as f:
                return json.load(f).get("bosses", {}) # Return the 'bosses' dictionary
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading boss configuration from {boss_config_path}: {e}")
            return {}

    def _load_enemy_data(self):
        """Loads the enemy data from enemy_data.json."""
        enemy_data_path = os.path.join(os.getcwd(), "data", "enemy_data.json")
        try:
            with open(enemy_data_path, "r") as f:
                return json.load(f) # Load the entire enemy data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading enemy data from {enemy_data_path}: {e}")
            return {}

    def attempt_spawn_portal(self, dungeon_scene):
        """
        Attempts to spawn a boss portal in the given dungeon scene.
        Determines the boss based on the average level of enemies in the dungeon.
        """
        if not dungeon_scene or not hasattr(dungeon_scene, 'dungeon_data') or not dungeon_scene.dungeon_data:
            print("BossSystemManager: Cannot attempt spawn portal, dungeon scene or data is missing.")
            return

        enemy_types_in_dungeon = dungeon_scene.dungeon_data.get('enemy_types', [])
        if not enemy_types_in_dungeon:
            print("BossSystemManager: No enemy types defined in dungeon data.")
            return

        total_xp = 0
        valid_enemies_count = 0
        for enemy_type_key in enemy_types_in_dungeon:
            enemy_info = self.enemy_data.get(enemy_type_key)
            if enemy_info and 'xp_value' in enemy_info:
                total_xp += enemy_info['xp_value']
                valid_enemies_count += 1
            else:
                print(f"BossSystemManager: Warning: Enemy type '{enemy_type_key}' not found or missing 'xp_value' in enemy_data.json")

        if valid_enemies_count == 0:
            print("BossSystemManager: No valid enemies with XP values found in dungeon data.")
            return

        average_enemy_xp = total_xp / valid_enemies_count
        print(f"BossSystemManager: Calculated average enemy XP: {average_enemy_xp}")

        # Get the previous scene name
        previous_scene_name = self.game.scene_manager.previous_scene_name

        boss_key = self._get_boss_key_from_average_xp(average_enemy_xp, previous_scene_name)

        if not boss_key:
            print(f"BossSystemManager: No boss configured for average enemy XP level: {average_enemy_xp}")
            return

        # TODO: Implement logic to determine if a portal should spawn (e.g., random chance, quest completion)
        # For now, let's always spawn one for testing if one doesn't exist
        if not self.active_portals:
            print(f"BossSystemManager: Attempting to spawn portal for boss: {boss_key}")
            self._spawn_portal(dungeon_scene, boss_key)
        else:
            print("BossSystemManager: Portal already exists in the current scene.")

    def _get_boss_key_from_average_xp(self, average_xp, previous_scene_name):
        """
        Determines the boss key based on the average enemy XP.
        Mapping provided by the user.
        """
        boss_name = None
        if 0 <= average_xp <= 15:
            boss_name = "goblin_king"
        elif 16 <= average_xp <= 30:
            boss_name = "ice_elemental"
        elif 31 <= average_xp <= 50:
            boss_name = "sandstone_golem"
        elif 51 <= average_xp <= 75:
            boss_name = "swamp_thing"
        elif average_xp >= 76:
            boss_name = "crystal_guardian"
        else:
            return None

        # Combine the boss name and previous scene name with a delimiter
        return f"{boss_name}|{previous_scene_name}"


    def _spawn_portal(self, dungeon_scene, boss_key):
        """Spawns a boss portal in the dungeon scene at a suitable location."""
        # Find a suitable location (e.g., walkable tile, somewhat far from entrance)
        spawn_location = self._find_suitable_spawn_location(dungeon_scene)

        if spawn_location:
            print(f"BossSystemManager: _spawn_portal: boss_key = {boss_key}")
            portal = BossPortal(
                self.game,
                spawn_location[0] * TILE_SIZE,
                spawn_location[1] * TILE_SIZE,
                boss_key
            )
            self.active_portals.add(portal)
            # Add the portal to the dungeon scene's entities or a dedicated portal group in the scene
            if hasattr(dungeon_scene, 'portals'): # Assuming dungeon scenes have a 'portals' group
                dungeon_scene.portals.add(portal)
            else:
                # If not, you might need to add it to a general entities group or handle it differently
                print("BossSystemManager: Warning: Dungeon scene does not have a 'portals' group. Portal not added to scene.")
            print(f"BossSystemManager: Spawned portal for boss {boss_key} at tile {spawn_location}")
        else:
            print(f"BossSystemManager: Could not find a suitable spawn location for the portal.")

    def _find_suitable_spawn_location(self, dungeon_scene):
        """
        Finds a suitable tile location for the boss portal.
        Locates the first "portal" tile in the dungeon scene's tile_map.
        """
        # Check if the dungeon scene has a tile_map
        if not hasattr(dungeon_scene, 'tile_map') or dungeon_scene.tile_map is None:
            print("BossSystemManager: _find_suitable_spawn_location: Dungeon scene has no tile_map or tile_map is None.")
            return None

        tile_map = dungeon_scene.tile_map
        map_width_tiles = len(tile_map[0])
        map_height_tiles = len(tile_map)

        # Add logging to print the tile_map and its dimensions
        # print(f"BossSystemManager: _find_suitable_spawn_location: tile_map = {tile_map}")
        # print(f"BossSystemManager: _find_suitable_spawn_location: map_width_tiles = {map_width_tiles}, map_height_tiles = {map_height_tiles}")

        for y in range(map_height_tiles):
            for x in range(map_width_tiles):
                if 0 <= y < map_height_tiles and 0 <= x < map_width_tiles:
                    tile_type = tile_map[y][x]
                    if tile_type == 'portal':
                        return (x, y)

        print("BossSystemManager: No 'portal' tile found in the dungeon scene.")
        return None

    def handle_portal_interaction(self, portal, player, hud):
        """Handles the player interacting with a boss portal."""
        if portal.boss_key is None:
            print("BossSystemManager: Error: portal.boss_key is None. Cannot transition to boss room.")
            return
        print(f"BossSystemManager: Player interacted with portal to boss: {portal.boss_key}")
        # Transition to the boss room scene
        self.game.scene_manager.set_scene("boss_room", player, hud, boss_key=portal.boss_key)
        # Remove the portal after interaction (or handle persistence if needed)
        self.active_portals.remove(portal)
        # You might also need to remove it from the dungeon scene's entity groups

    def update(self, dt, player=None):
        """Updates the state of active portals and checks for player interaction."""
        self.active_portals.update(dt)

        if player:
            interaction_distance = TILE_SIZE * 1.5 # Define interaction distance

            for portal in self.active_portals:
                portal_world_x = portal.rect.centerx
                portal_world_y = portal.rect.centery
                player_world_x = player.rect.centerx
                player_world_y = player.rect.centery

                distance = math.hypot(player_world_x - portal_world_x, player_world_y - portal_world_y)

                if distance < interaction_distance:
                    # Check if the interact key is pressed
                    # Assuming game.input_handler is accessible and has a method to check key state
                    # You might need to pass input state or the input handler itself
                    if self.game.input_handler.is_key_pressed(KEY_INTERACT):
                        self.handle_portal_interaction(portal, player, self.game.current_scene.hud)
                        break # Interact with only one portal at a time

    def draw(self, screen, camera_x, camera_y, zoom_level):
        """Draws active portals."""
        # Portals are drawn by the scene they are in, but this method could be used
        # if the manager was responsible for drawing. Keeping for potential future use.
        pass