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
    def __init__(self, game, player=None, hud=None, boss_key=None, dungeon_data=None, friendly_entities=None): # Added friendly_entities
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
        super().__init__(game, player, hud, tileset_name, dungeon_data, friendly_entities=friendly_entities) # Pass friendly_entities
        self.name = "BossRoomScene" # Set the scene name

        self.boss = None
        self._spawn_boss()

        # Placeholder for boss room specific state or elements
        self.is_boss_defeated = False
        self.return_portals = pygame.sprite.Group()  # Group to hold return portals
        self.input_handler = InputHandler()  # Instantiate InputHandler for interaction check
        self.warning_message = "YOURE GONNA FUCKING DIE"
        self.display_warning_message = True
        self.warning_message_start_time = 0
        self.warning_message_alpha = 255  # Initial alpha value for the fade effect
        self.warning_message_fade_speed = 50  # Adjust the fade speed as needed
        self.warning_message_duration = 5000  # Duration in milliseconds (5 seconds)
        self.message_fade_delay = 3000 # Delay before message starts fading
        self.message_fade_start_time = 0 # Time when the message should start fading
        self.boss_defeat_message_displayed = False
        self.boss_defeat_message_alpha = 255
        self.boss_defeat_message = "yeah whatev..... i was goin easy.....i don care..."
        self.boss_defeat_message_start_time = 0
        #self.boss_defeat_message_fade_start_time = 0  # Remove this line
        self.is_boss_defeat_handled = False

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
                boss_speed = enemy_data.get("damage")
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
        current_time = pygame.time.get_ticks()

        # Handle initial warning message
        if self.display_warning_message and not self.boss_defeat_message_displayed:
            self._update_warning_message(current_time)

        # Handle boss defeat message
        if self.boss_defeat_message_displayed:
            self._update_boss_defeat_message(current_time, dt)

        print(f"DEBUG: Boss in enemies group: {self.boss in self.enemies}")

        boss_alive = self.boss and self.boss.current_life > 0
        boss_in_enemies = self.boss in self.enemies if self.boss else False

        print(f"DEBUG: boss_alive: {boss_alive}, boss_in_enemies: {boss_in_enemies}")

        if self.boss and self.boss.current_life <= 0 and not self.is_boss_defeat_handled:
            print("DEBUG: Boss death condition met in BossRoomScene!")
            self.is_boss_defeated = True
            print(f"Boss {self.boss.name} defeated!")
            # Trigger boss defeated logic (e.g., spawn exit portal, play animation)
            self.boss_defeat_message_displayed = True
            self.display_warning_message = False  # Make sure the message is not displayed
            self.boss_defeat_message_start_time = pygame.time.get_ticks()  # Reset the start time
            #self.boss_defeat_message_fade_start_time = pygame.time.get_ticks()  # Reset the fade start time
            self.boss_defeat_message_alpha = 255
            self._handle_boss_defeat()
            self.is_boss_defeat_handled = True

        super().update(dt, self.all_sprites)

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
                        self.game.scene_manager.set_scene(portal.boss_key, self.player, self.hud, friendly_entities=self.friendly_entities.sprites()) # Pass friendly_entities
                    else:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        # Adjust mouse coordinates for camera and zoom
                        mouse_world_x = (mouse_x / self.game.zoom_level) + self.camera_x
                        mouse_world_y = (mouse_y / self.game.zoom_level) + self.camera_y

                        if portal.rect.collidepoint(mouse_world_x, mouse_world_y) and pygame.mouse.get_pressed()[0]:
                            print(f"BossRoomScene: Player interacted with return portal to: {portal.boss_key} via mouse click")  # boss_key is used to store target scene
                            self.game.scene_manager.set_scene(portal.boss_key, self.player, self.hud, friendly_entities=self.friendly_entities.sprites()) # Pass friendly_entities
                            break  # Interact with only one portal at a time
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
        alpha = self.warning_message_alpha

        # Create a surface to fill the screen with black
        black_surface = pygame.Surface((self.game.settings.SCREEN_WIDTH, self.game.settings.SCREEN_HEIGHT))
        black_surface.fill((0, 0, 0))
        black_surface.set_alpha(alpha)

        # Draw the black surface onto the screen
        screen.blit(black_surface, (0, 0))

        # Render the text with the current alpha value
        font = pygame.font.Font(None, 100)
        text = self.warning_message
        text_surface = font.render(text, True, (255, 0, 0))
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=(self.game.settings.SCREEN_WIDTH // 2, self.game.settings.SCREEN_HEIGHT // 2))

        # Blit the text surface onto the screen
        screen.blit(text_surface, text_rect)

    def display_boss_defeat_message_effect(self, screen):
        """Displays the boss defeat message on the screen with a fade effect."""
        # Ensure alpha is within valid range
        alpha = self.boss_defeat_message_alpha
        print(f"DEBUG: display_boss_defeat_message_effect alpha: {alpha}")

        # Create a surface to fill the screen with black
        black_surface = pygame.Surface((self.game.settings.SCREEN_WIDTH, self.game.settings.SCREEN_HEIGHT))
        black_surface.fill((0, 0, 0))
        black_surface.set_alpha(alpha)

        # Draw the black surface onto the screen
        screen.blit(black_surface, (0, 0))

        # Render the text with the current alpha value
        font = pygame.font.Font(None, 100)
        text = self.boss_defeat_message
        text_surface = font.render(text, True, (255, 0, 0))
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=(self.game.settings.SCREEN_WIDTH // 2, self.game.settings.SCREEN_HEIGHT // 2))

        # Blit the text surface onto the screen
        screen.blit(text_surface, text_rect)

    def draw(self, screen):
        """Draws the boss room."""
        super().draw(screen)
        # Add boss room specific drawing here (e.g., boss health bar)

        if self.boss:
            health_percentage = self.boss.current_life / self.boss.health
            bar_width = int(self.game.settings.SCREEN_WIDTH * 0.5)  # 50% of screen width
            bar_height = 20
            bar_x = (self.game.settings.SCREEN_WIDTH - bar_width) // 2
            bar_y = 50  # Below the HUD
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))  # Background
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(bar_width * health_percentage), bar_height))  # Health
        # Draw return portals
        for portal in self.return_portals:
            portal.draw(screen, self.camera_x, self.camera_y, self.zoom_level)

        if self.display_warning_message or self.boss_defeat_message_displayed:
            if self.boss_defeat_message_displayed:
                self.display_boss_defeat_message_effect(screen)
            else:
                self.display_warning_message_effect(screen)

    def _update_warning_message(self, current_time):
        """Updates the state of the initial warning message."""
        if self.warning_message_start_time == 0:
            self.warning_message_start_time = current_time
        elapsed_time = current_time - self.warning_message_start_time
        if self.message_fade_start_time == 0 and elapsed_time > self.message_fade_delay:
            self.message_fade_start_time = current_time  # Set the fade start time
        if self.message_fade_start_time != 0:
            fade_elapsed_time = current_time - self.message_fade_start_time
            if fade_elapsed_time > self.warning_message_duration:
                self.warning_message_alpha -= self.warning_message_fade_speed
                if self.warning_message_alpha <= 0:
                    self.display_warning_message = False  # Stop displaying the message when fully faded

    def _update_boss_defeat_message(self, current_time, dt):
        """Updates the state of the boss defeat message."""
        elapsed_time = current_time - self.boss_defeat_message_start_time
        print(f"DEBUG: elapsed_time: {elapsed_time}, boss_defeat_message_alpha: {self.boss_defeat_message_alpha}")

        if elapsed_time > self.message_fade_delay:
            self.boss_defeat_message_alpha -= self.warning_message_fade_speed * dt
            print(f"DEBUG: fading, boss_defeat_message_alpha: {self.boss_defeat_message_alpha}")
            if self.boss_defeat_message_alpha <= 0:
                self.boss_defeat_message_alpha = 0
                self.boss_defeat_message_displayed = False
                self.game.scene_manager.set_scene("spawn_town", self.player, self.hud, friendly_entities=self.friendly_entities.sprites())  # Go back to spawn town, Pass friendly_entities
                print("DEBUG: Transitioning to spawn_town")

    def _handle_boss_defeat(self):
        """Handles actions after the boss is defeated."""
        print("Handling boss defeat: Spawning exit portal.")

        # Stop the current song
        pygame.mixer.music.stop()

        # Play a random song from data/music
        music_dir = os.path.join(os.getcwd(), "data", "music")
        try:
            music_files = [f for f in os.listdir(music_dir) if f.endswith(".ogg") or f.endswith(".mp3")]
            if music_files:
                random_song = random.choice(music_files)
                pygame.mixer.music.load(os.path.join(music_dir, random_song))
                pygame.mixer.music.play(-1)  # Play the song in a loop
                print(f"Playing random song: {random_song}")
            else:
                print("No music files found in data/music.")
        except FileNotFoundError:
            print("data/music directory not found.")

        #self.game.scene_manager.set_scene("spawn_town", self.player, self.hud)  # Go back to spawn town

        # Display the "yeah whatev..." message
        #self.warning_message = "yeah whatev..... i was goin easy.....i don care..."
        #self.display_warning_message = True
        #self.warning_message_start_time = pygame.time.get_ticks()
        #self.boss_defeat_message_alpha = 255
        self.message_fade_start_time = 0  # Reset the fade start time
        #self.message_fade_complete = False

        # # Determine spawn location for the return portal (e.g., center of the map)
        # spawn_x = (self.map_width // 2) * TILE_SIZE
        # spawn_y = (self.map_height // 2) * TILE_SIZE

        # return_portal = BossPortal(
        #     self.game,
        #     spawn_x,
        #     spawn_y,
        #     "spawn_town"  # Set the target scene as the boss_key for the return portal
        # )
        # self.return_portals.add(return_portal)
        # print(f"Spawned return portal at ({spawn_x}, {spawn_y})")

    # Add other boss room specific methods as needed
    # For example:
    # def _check_win_condition(self):
    #     """Checks if the boss has been defeated."""
    #     pass
    # def _trigger_phase_change(self):
    #     """Handles boss phase transitions."""
    #     pass