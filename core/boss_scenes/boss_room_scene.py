import pygame
import random
import os
import json
import math  # Import math for distance calculation
from core.base_gameplay_scene import BaseGameplayScene
from entities.bosses.base_boss import BaseBoss  # Assuming BaseBoss is needed for type hinting or specific logic
from config.constants import TILE_SIZE, KEY_INTERACT  # Assuming TILE_SIZE and KEY_INTERACT are needed
from entities.boss_portal import BossPortal  # Import BossPortal for the return portal
from core.input_handler import InputHandler  # Import InputHandler


class BossRoomScene(BaseGameplayScene):
    def __init__(self, game, player=None, hud=None, boss_key=None, dungeon_data=None):
        # Load boss configuration
        self.enemies = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        self.tile_map = []
        self.boss_config = self._load_boss_config()
        self.dungeon_data = dungeon_data
        self.boss_key = boss_key
        self.boss_config_data = self._load_boss_config()

        if self.boss_key:
            # Parse the boss_key to extract the boss name and previous scene name
            parts = self.boss_key.split("|")
            self.boss_name = parts[0]
            self.previous_scene_name = parts[1] if len(parts) > 1 else "spawn_town"  # Default to spawn_town if no previous scene
        else:
            self.boss_name = None
            self.previous_scene_name = "spawn_town"

        if self.boss_name is None:
            print("BossRoomScene: boss_name is None. Selecting a random boss.")
            if self.boss_config:
                self.boss_name = random.choice(list(self.boss_config.keys()))
            else:
                print("BossRoomScene: Error: No boss configuration found.")
                return

        self.boss_data = self.boss_config.get(self.boss_name)

        if not self.boss_data:
            print(f"Error: Boss data not found for key: {boss_key}. Selecting a random boss.")
            # Select a random boss from the boss_config
            if self.boss_config:
                while self.boss_config:
                    self.boss_name = random.choice(list(self.boss_config.keys()))
                    self.boss_data = self.boss_config.get(self.boss_name)
                    if self.boss_data and self.boss_data.get("layout_path"):
                        break
                    else:
                        print(f"BossRoomScene: Warning: Boss {self.boss_name} has no layout_path. Selecting another boss.")
                        del self.boss_config[self.boss_name]  # Remove the boss from the config to avoid infinite loops
                else:
                    print("BossRoomScene: Error: No boss configuration found or no boss with layout_path.")
                    game.scene_manager.set_scene("spawn_town", player, hud)
                    return

        if not self.boss_data.get("layout_path"):
            print(f"BossRoomScene: Warning: Boss {self.boss_name} has no layout_path. Using default layout.")
            self.boss_data["layout_path"] = "data/boss_rooms/generic_boss_layout.json"

        # Load the specific boss room layout and tileset from boss_data
        dungeon_data_path = os.path.join(os.getcwd(), self.boss_data.get("layout_path"))

        # Extract the dungeon name from the previous_scene_name
        dungeon_name = self.previous_scene_name  # Assuming previous_scene_name is the dungeon name

        # Retrieve the tileset_name from the dungeon_to_boss_mapping
        tileset_name = "default"  # Default tileset

        # Determine tileset name based on boss or dungeon
        if self.boss_name:
            for dungeon, mapping in self.boss_config_data.get("dungeon_to_boss_mapping", {}).items():
                if mapping.get("boss_key") == self.boss_key:
                    tileset_name = mapping.get("tileset_name", "default")
                    break
        else:
            if "dungeon_to_boss_mapping" in self.boss_config_data:
                if dungeon_name in self.boss_config_data["dungeon_to_boss_mapping"]:
                    tileset_name = self.boss_config_data["dungeon_to_boss_mapping"][dungeon_name].get("tileset_name", "default")

        self.all_sprites = pygame.sprite.Group()
        try:
            with open(dungeon_data_path, "r") as f:
                dungeon_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading boss room layout from {dungeon_data_path}: {e}")
            self.tile_map = [[]]
            # Handle error
            game.scene_manager.set_scene("spawn_town", player, hud)
            return

        # Load tilemap data
        self.tile_map = dungeon_data["tilemap"]
        self.map_width = dungeon_data["width"]
        self.map_height = dungeon_data["height"]
        self.dungeon_data = dungeon_data # Store the dungeon data

        # Initialize the base gameplay scene with the loaded data
        super().__init__(game, player, hud, tileset_name, dungeon_data)

        self.boss = None
        self._spawn_boss()

        # Placeholder for boss room specific state or elements
        self.is_boss_defeated = False
        self.return_portals = pygame.sprite.Group()  # Group to hold return portals
        self.input_handler = InputHandler()  # Instantiate InputHandler for interaction check
        self.warning_message = "YOURE GONNA FUCKING DIE"
        self.display_warning_message = True
        self.warning_message_start_time = pygame.time.get_ticks()
        self.warning_message_alpha = 255  # Initial alpha value for the fade effect
        self.warning_message_fade_speed = 2  # Adjust the fade speed as needed
        self.warning_message_duration = 5000  # Duration in milliseconds (5 seconds)

        # Fade effect attributes
        # self.fade_alpha = 0  # Start fully transparent
        # self.fade_direction = 1  # Start fading in

    def _load_boss_config(self):
        """Loads the boss configuration from boss_config.json."""
        boss_config_path = os.path.join(os.getcwd(), "data", "boss_config.json")
        try:
            with open(boss_config_path, "r") as f:
                return json.load(f).get("bosses", {})  # Return the 'bosses' dictionary
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading boss configuration from {boss_config_path}: {e}")
            return {}

    def _spawn_boss(self):
        """Spawns the boss based on the boss_key."""
        if not self.boss_data or "enemies" not in self.boss_data:
            print("BossRoomScene: No boss data or enemies found.")
            return

        for enemy_data in self.boss_data["enemies"]:
            if enemy_data["type"] == self.boss_name:
                boss_type = enemy_data.get("type")
                boss_sprite_path = enemy_data.get("sprite_path")
                boss_health = enemy_data.get("health")
                boss_damage = enemy_data.get("damage")
                boss_speed = enemy_data.get("speed")
                boss_attack_range = enemy_data.get("attack_range", 0)
                boss_attack_cooldown = enemy_data.get("attack_cooldown", 0)
                boss_projectile_sprite_path = enemy_data.get("projectile_sprite_path")
                boss_ranged_attack_pattern = enemy_data.get("ranged_attack_pattern", "single")
                boss_xp_value = enemy_data.get("xp_value", 0)  # Assuming bosses give XP
                spawn_x = (self.map_width // 2) * TILE_SIZE
                spawn_y = (self.map_height // 2) * TILE_SIZE

                # Instantiate the boss class
                self.boss = BaseBoss(
                    self.game,
                    spawn_x,
                    spawn_y,
                    boss_type,  # Name
                    boss_health,
                    boss_damage,
                    boss_speed,
                    boss_sprite_path,
                    boss_attack_range,
                    boss_attack_cooldown,
                    boss_projectile_sprite_path,
                    boss_ranged_attack_pattern,
                    boss_xp_value
                )
                self.enemies.add(self.boss)  # Add the boss to the enemies group
                print(f"Spawned boss: {boss_type} at ({spawn_x}, {spawn_y})")
                return  # Only spawn one boss

        print(f"BossRoomScene: No boss found with name {self.boss_name} in the layout.")

    def handle_event(self, event):
        """Handles events specific to the boss room."""
        super().handle_event(event)
        # Add boss room specific event handling here (e.g., pausing during boss fight)

    def update(self, dt, entities=None):
        """Updates the state of the boss room."""
        if self.display_warning_message:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.warning_message_start_time
            if elapsed_time > self.warning_message_duration:
                # Start fading after the duration
                self.warning_message_alpha -= self.warning_message_fade_speed
                if self.warning_message_alpha <= 0:
                    self.display_warning_message = False  # Stop displaying the message when fully faded

        super().update(dt, self.all_sprites)

        if self.boss and self.boss in self.enemies and self.boss.health <= 0:
            self.is_boss_defeated = True
            print(f"Boss {self.boss.name} defeated!")
            # Trigger boss defeated logic (e.g., spawn exit portal, play animation)
            self._handle_boss_defeat()

        # Update return portals
        self.return_portals.update(dt)

        # Check for player interaction with return portals
        if self.player and self.return_portals:
            interaction_distance = TILE_SIZE * 1.5  # Define interaction distance

            for portal in self.return_portals:
                portal_world_x = portal.rect.centerx
                portal_world_y = portal.rect.centery
                player_world_x = self.player.rect.centerx
                player_world_y = self.player.rect.centery

                distance = math.hypot(player_world_x - portal_world_x, player_world_y - portal_world_y)

                if distance < interaction_distance:
                    if self.input_handler.is_key_pressed(KEY_INTERACT):
                        print(f"BossRoomScene: Player interacted with return portal to: {portal.boss_key}")  # boss_key is used to store target scene
                        self.game.scene_manager.set_scene(portal.boss_key, self.player, self.hud)
                        break  # Interact with only one portal at a time

        # Update fade effect
        # self.fade_alpha += self.fade_direction * 10  # Adjust the speed of fading here

        # if self.fade_alpha <= 0:
        #    self.fade_alpha = 0
        #    self.fade_direction = 1
        # elif self.fade_alpha >= 255:
        #    self.fade_alpha = 255
        #    self.fade_direction = -1

    def display_warning_message_effect(self, screen):
        """Displays the warning message on the screen with a fade effect."""
        # Ensure alpha is within valid range
        self.warning_message_alpha = max(0, min(255, self.warning_message_alpha))

        # Create a surface to fill the screen with black
        black_surface = pygame.Surface((self.game.settings.SCREEN_WIDTH, self.game.settings.SCREEN_HEIGHT))
        black_surface.fill((0, 0, 0))
        black_surface.set_alpha(self.warning_message_alpha)

        # Draw the black surface onto the screen
        screen.blit(black_surface, (0, 0))

        # Render the text with the current alpha value
        font = pygame.font.Font(None, 100)
        text_surface = font.render(self.warning_message, True, (255, 0, 0))
        text_surface.set_alpha(self.warning_message_alpha)
        text_rect = text_surface.get_rect(center=(self.game.settings.SCREEN_WIDTH // 2, self.game.settings.SCREEN_HEIGHT // 2))

        # Blit the text surface onto the screen
        screen.blit(text_surface, text_rect)

    def draw(self, screen):
        """Draws the boss room."""
        super().draw(screen)
        # Add boss room specific drawing here (e.g., boss health bar)

        # Draw return portals
        for portal in self.return_portals:
            portal.draw(screen, self.camera_x, self.camera_y, self.zoom_level)

        if self.display_warning_message:
            self.display_warning_message_effect(screen)

    def _handle_boss_defeat(self):
        """Handles actions after the boss is defeated."""
        print("Handling boss defeat: Spawning exit portal.")
        # Determine spawn location for the return portal (e.g., center of the map)
        spawn_x = (self.map_width // 2) * TILE_SIZE
        spawn_y = (self.map_height // 2) * TILE_SIZE

        return_portal = BossPortal(
            self.game,
            spawn_x,
            spawn_y,
            "spawn_town"  # Set the target scene as the boss_key for the return portal
        )
        self.return_portals.add(return_portal)
        print(f"Spawned return portal at ({spawn_x}, {spawn_y})")

    # Add other boss room specific methods as needed
    # For example:
    # def _check_win_condition(self):
    #     """Checks if the boss has been defeated."""
    #     pass

    # def _trigger_phase_change(self):
    #     """Handles boss phase transitions."""
    #     pass