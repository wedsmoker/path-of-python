import pygame
import json  # Import json to read zone_data.json
import os  # Import os to construct file paths
from ui.dialogue_manager import DialogueManager
from core.scene_manager import BaseScene
from entities.player import Player
from entities.boss_portal import BossPortal  # Import BossPortal
from ui.hud import HUD
from config.constants import (
    KEY_INVENTORY, KEY_SKILL_TREE, KEY_INTERACT, KEY_OPTIONS_MENU,
    STATE_INVENTORY, STATE_SKILL_TREE, STATE_PAUSE_MENU, STATE_SETTINGS_MENU, TILE_SIZE,
    KEY_RIGHT_MOUSE, KEY_SKILL_1, KEY_SKILL_2, KEY_SKILL_3, KEY_SKILL_4, KEY_PAGE_UP, KEY_PAGE_DOWN,
    KEY_SKILL_5, KEY_SKILL_6 # Added KEY_SKILL_5, KEY_SKILL_6
)
import math # Import math for distance calculation

from entities.enemy import Enemy # Import the Enemy class
from entities.projectile import Projectile # Import the Projectile class

# Removed: from core.boss_system_manager import BossSystemManager # Import BossSystemManager
class BaseGameplayScene(BaseScene):
    def __init__(self, game, player=None, hud=None, tileset_name="default", dungeon_data=None, friendly_entities=None):  # Added friendly_entities parameter
        # Moved import here to avoid circular dependency
        from core.boss_system_manager import BossSystemManager
        self.boss_system_manager = BossSystemManager(game) # Instantiate BossSystemManager
        super().__init__(game)
        
        # Camera settings - Initialize these always
        self.camera_x = 0
        self.camera_y = 0
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.zoom_level = 1.0
        self.map_width = 50  # Placeholder, will be updated when the map is loaded
        self.map_height = 30  # Placeholder, will be updated when the map is loaded
        self.tile_size = TILE_SIZE  # Get from constants
        self.frame_count = 0
        self.name = None # Initialize name attribute
        self.friendly_entities = pygame.sprite.Group() # Initialize friendly entities group
        self.death_sequence_initiated = False

        self.player = player  # Player is now passed in or remains None
        self.hud = hud 
        if self.player is not None and self.hud is not None:
            self.tileset_name = tileset_name  # Store the tileset name
            self.dungeon_data = dungeon_data # Store dungeon data
            self.portal_spawned = False # Add a flag to indicate whether the portal has been spawned
            self.enemies_loaded = False # Add a flag to indicate whether the enemies have been loaded
            self.tile_images = {}
            self._load_tile_images()
            self.projectiles = pygame.sprite.Group()
            self.enemies = pygame.sprite.Group() # Group to hold enemy sprites
            self.portals = pygame.sprite.Group() # Group to hold boss portals
            self.npcs = [
                {"name": "Old Scavenger", "tile_x": 10, "tile_y": 10, "dialogue_id": "old_scavenger_intro"}
            ]
            self.decorations = []
            # If dungeon_data is provided, attempt to load enemies
            if self.dungeon_data and not self.enemies_loaded:
                self.load_enemies(self.dungeon_data.get('enemies', []))
            
            if friendly_entities: # Add friendly entities if passed
                for entity in friendly_entities:
                    self.friendly_entities.add(entity)

            self.post_init()
            return  # Do not re-initialize if player and HUD are passed in
        
        self.tileset_name = tileset_name  # Store the tileset name
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group() # Group to hold enemy sprites
        self.portals = pygame.sprite.Group() # Group to hold boss portals
        self.dungeon_data = dungeon_data # Store dungeon data
        self.portal_spawned = False # Add a flag to indicate whether the portal has been spawned
        self.enemies_loaded = False # Add a flag to indicate whether the enemies have been loaded
        
        self.tile_images = {}
        #self.faded_tile_images = {}  # Dictionary to store faded tile images
        self._load_tile_images()

        # Placeholder NPC for testing dialogue
        # In a real game, this would be managed by an NPC system
        self.npcs = [
            {"name": "Old Scavenger", "tile_x": 10, "tile_y": 10, "dialogue_id": "old_scavenger_intro"}
        ]

        # If dungeon_data is provided, attempt to load enemies
        if self.dungeon_data:
            # Set player_spawn_location if not provided in dungeon_data
            if 'player_spawn_location' not in self.dungeon_data and hasattr(self, 'tile_map'):
                # Find first floor tile if spawn location not specified
                for y, row in enumerate(self.tile_map):
                    for x, tile_type in enumerate(row):
                        if tile_type == 'floor':
                            self.player_spawn_location = (x * self.tile_size, y * self.tile_size)
                            break
                    else:
                        continue
                    break
                else:
                    # Default to (0, 0) if no floor tile found
                    self.player_spawn_location = (0, 0)
            elif 'player_spawn_location' in self.dungeon_data:
                self.player_spawn_location = self.dungeon_data['player_spawn_location']

            # Load enemies if present in dungeon_data
            if not self.enemies_loaded:
                self.load_decorations(self.dungeon_data.get('decorations', []))
                self.load_enemies(self.dungeon_data.get('enemies', []))
        
        if friendly_entities: # Add friendly entities if passed
            for entity in friendly_entities:
                self.friendly_entities.add(entity)

        self.post_init()

    def post_init(self):
        """
        Called by subclasses after their own initialization is complete.
        Responsible for tasks that require the full scene to be set up,
        like spawning the boss portal.
        """
        if self.dungeon_data and not self.portal_spawned: # Only attempt to spawn if portal hasn't been spawned yet
            # Attempt to spawn a boss portal in this scene now that tile_map and player_spawn_location should be set
            self.boss_system_manager.attempt_spawn_portal(self)
            self.portal_spawned = True # Set the flag to True after attempting to spawn the portal

        # Update enemy XP values based on enemy_data.json
        enemy_config_path = os.path.join(os.getcwd(), "data", "enemy_data.json")
        try:
            with open(enemy_config_path, "r") as f:
                all_enemy_configs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading enemy configuration from {enemy_config_path}: {e}")
            all_enemy_configs = {}

        for enemy in self.enemies:
            config = all_enemy_configs.get(enemy.name, {})
            if config:
                enemy.xp_value = config.get('xp_value', 0)
                print(f"Updated XP value for {enemy.name} to {enemy.xp_value}")

    def _load_tile_images(self):
        """Loads tile images based on the dungeon's tileset."""
        try:
            zone_data_path = os.path.join(os.getcwd(), "data", "zone_data.json")
            with open(zone_data_path, "r") as f:
                zone_data = json.load(f)

            tile_sets = zone_data.get("tile_sets", {})
            tileset_data = tile_sets.get(self.tileset_name)

            if tileset_data:
                pass
            else:
                pass

            if tileset_data:
                # Load tile images from zone_data.json
                for tile_name, tile_path in tileset_data.items():
                    try:
                        full_path = os.path.join(os.getcwd(), tile_path)
                        if not os.path.exists(full_path):
                            print(f"BaseGameplayScene: Error: Tile image file not found: {full_path}")
                            self.tile_images[tile_name] = pygame.Surface((self.tile_size, self.tile_size))
                            self.tile_images[tile_name].fill((255, 0, 255))  # Magenta placeholder
                            continue

                        image = pygame.image.load(full_path).convert_alpha()
                        self.tile_images[tile_name] = image

                        # Create a faded version of the tile image
                        #faded_image = image.copy()
                        #for i in range(faded_image.get_width()):
                        #    for j in range(faded_image.get_height()):
                        #        color = faded_image.get_at((i, j))
                        #        new_color = (color[0], color[1], color[2], 0)  # Fully transparent
                        #        faded_image.set_at((i, j), new_color)
                        #faded_image.set_at((i, j), new_color)
                        #self.faded_tile_images[tile_name] = faded_image

                        # print(f"BaseGameplayScene: Loaded tile image: {tile_name} from {full_path}")  # Added logging
                    except pygame.error as e:
                        print(f"BaseGameplayScene: Warning: Could not load tile image {full_path}: {e}")
                        self.tile_images[tile_name] = pygame.Surface((self.tile_size, self.tile_size))
                        self.tile_images[tile_name].fill((255, 0, 255))  # Magenta placeholder
                        #self.faded_tile_images[tile_name] = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)  # Transparent placeholder

            else:
                # Load tile images from a separate JSON file
                tileset_path = os.path.join(os.getcwd(), "data", "tilesets", f"{self.tileset_name}_tileset.json")
                with open(tileset_path, "r") as f:
                    tileset_data = json.load(f)

                for tile_name, tile_path in tileset_data.items():
                    try:
                        full_path = os.path.join(os.getcwd(), tile_path)
                        if not os.path.exists(full_path):
                            print(f"BaseGameplayScene: Error: Tile image file not found: {full_path}")
                            self.tile_images[tile_name] = pygame.Surface((self.tile_size, self.tile_size))
                            self.tile_images[tile_name].fill((255, 0, 255))  # Magenta placeholder
                            continue

                        image = pygame.image.load(full_path).convert_alpha()
                        self.tile_images[tile_name] = image

                        # Create a faded version of the tile image
                        #faded_image = image.copy()
                        #for i in range(faded_image.get_width()):
                        #    for j in range(faded_image.get_height()):
                        #        color = faded_image.get_at((i, j))
                        #        new_color = (color[0], color[1], color[2], 0)  # Fully transparent
                        #faded_image.set_at((i, j), new_color)
                        #self.faded_tile_images[tile_name] = faded_image

                        # print(f"BaseGameplayScene: Loaded tile image: {tile_name} from {full_path}")  # Added logging
                    except pygame.error as e:
                        print(f"BaseGameplayScene: Warning: Could not load tile image {full_path}: {e}")
                        self.tile_images[tile_name] = pygame.Surface((self.tile_size, self.tile_size))
                        self.tile_images[tile_name].fill((255, 0, 255))  # Magenta placeholder
                        #self.faded_tile_images[tile_name] = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)  # Transparent placeholder

        except FileNotFoundError:
            print(f"BaseGameplayScene: Error: data/zone_data.json or tileset file not found. Cannot load tile images.")
        except json.JSONDecodeError:
            print(f"BaseGameplayScene: Error: Could not decode data/zone_data.json or tileset file. Check JSON format.")
        except KeyError as e:
            print(f"BaseGameplayScene: Error: Missing key in tileset data: {e}")

    def load_enemies(self, enemies_data):
        """Loads enemies from the dungeon data."""
        if self.enemies_loaded:
            return

        # Do NOT clear self.enemies here, as it might contain friendly entities
        # self.enemies.empty() 
        # Load enemy data from enemy_data.json
        enemy_config_path = os.path.join(os.getcwd(), "data", "enemy_data.json")
        try:
            with open(enemy_config_path, "r") as f:
                all_enemy_configs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading enemy configuration from {enemy_config_path}: {e}")
            all_enemy_configs = {}

        for enemy_info in enemies_data:
            enemy_type = enemy_info.get('type')
            config = all_enemy_configs.get(enemy_type, {})

            if not config:
                print(f"Warning: No config found for enemy type: {enemy_type}")
                continue

            # Use config values directly
            health = config.get('health', 10)
            damage = config.get('damage', 1)
            speed = config.get('speed', 50)
            sprite_path = config.get('sprite_path', 'graphics/dc-mon/misc/demon_small.png')
            attack_range = config.get('attack_range', 0)
            attack_cooldown = config.get('attack_cooldown', 0)
            projectile_sprite_path = config.get('projectile_sprite_path')
            ranged_attack_pattern = config.get('ranged_attack_pattern', 'single')
            xp_value = config.get('xp_value', 0)

            enemy = Enemy(
                self.game,
                enemy_info['x'] * self.tile_size,
                enemy_info['y'] * self.tile_size,
                enemy_type, # Pass the enemy_type as the name
                health,
                damage,
                speed,
                sprite_path,
                attack_range,
                attack_cooldown,
                projectile_sprite_path,
                ranged_attack_pattern,
                xp_value
            )
            self.enemies.add(enemy)
        print(f"BaseGameplayScene: Loaded {len(self.enemies)} enemies.")
    def load_decorations(self, decorations_data):
        """Loads decorations from the dungeon data."""
        for decoration_info in decorations_data:
            decoration_type = decoration_info.get('type')
            x = decoration_info.get('x')
            y = decoration_info.get('y')
            sprite_path = decoration_info.get('sprite_path')

            try:
                full_path = os.path.join(os.getcwd(), sprite_path)
                image = pygame.image.load(full_path).convert_alpha()
                self.decorations.append({
                    'type': decoration_type,
                    'x': x,
                    'y': y,
                    'image': image
                })
            except pygame.error as e:
                print(f"BaseGameplayScene: Warning: Could not load decoration image {sprite_path}: {e}")

        print(f"BaseGameplayScene: Loaded {len(self.decorations)} decorations.")
        self.decorations_loaded = True

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
                self.game.scene_manager.set_scene(STATE_INVENTORY, self.player, self.hud, friendly_entities=self.friendly_entities.sprites()) # Pass friendly entities
            elif event.key == KEY_SKILL_TREE:
                self.game.scene_manager.set_scene(STATE_SKILL_TREE, self.player, self.hud, friendly_entities=self.friendly_entities.sprites()) # Pass friendly entities
            elif event.key == pygame.K_ESCAPE:
                self.game.scene_manager.set_scene(STATE_PAUSE_MENU, player=self.player, hud=self.hud, friendly_entities=self.friendly_entities.sprites()) # Pass friendly entities
            elif event.key == KEY_OPTIONS_MENU:
                self.game.scene_manager.set_scene(STATE_SETTINGS_MENU, self.player, self.hud, friendly_entities=self.friendly_entities.sprites()) # Pass friendly entities
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

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse button down event. Button: {event.button}")
            if event.button == 4:  # Scrolling up
                self.zoom_level += 0.1
            elif event.button == 5:  # Scrolling down
                self.zoom_level -= 0.1
            if event.button == pygame.BUTTON_RIGHT:
                # Get the mouse position in world coordinates
                world_x = (event.pos[0] + self.camera_x * self.zoom_level) / self.zoom_level
                world_y = (event.pos[1] + self.camera_y * self.zoom_level) / self.zoom_level
                if self.player:
                    if self.player.current_mana >= 15: # Check if player has enough mana
                        self.player.blink(world_x, world_y)
                        self.player.current_mana -= 15 # Deduct mana cost
                    else:
                        print("Not enough mana to blink!")
            elif event.button == 1: # Left-click
                # Get the mouse position in world coordinates
                world_x = (event.pos[0] + self.camera_x * self.zoom_level) / self.zoom_level
                world_y = (event.pos[1] + self.camera_y * self.zoom_level) / self.zoom_level
                if self.player:
                    self.player.set_target(world_x, world_y)
            else: # Handle other mouse buttons for skills
                skill_key_constant = None
                if event.button == KEY_SKILL_5: # Mouse Button 6
                    skill_key_constant = "KEY_SKILL_5"
                elif event.button == KEY_SKILL_6: # Mouse Button 7
                    skill_key_constant = "KEY_SKILL_6"

                if skill_key_constant and self.player:
                    # Find the skill ID associated with this key binding
                    skill_id_to_activate = self.player.skill_key_bindings.get(skill_key_constant)
                    
                    if skill_id_to_activate:
                        world_mouse_x = (event.pos[0] + self.camera_x * self.zoom_level) / self.zoom_level
                        world_mouse_y = (event.pos[1] + self.camera_y * self.zoom_level) / self.zoom_level
                        self.player.activate_skill(skill_id_to_activate, mouse_pos=(world_mouse_x, world_mouse_y))


        if event.type == pygame.MOUSEBUTTONUP:
            # Handle skill deactivation on mouse button release
            skill_key_constant = None
            if event.button == KEY_SKILL_6: # Mouse Button 7
                skill_key_constant = "KEY_SKILL_6"

            if skill_key_constant and self.player:
                # Find the skill ID associated with this key binding
                skill_id_to_deactivate = self.player.skill_key_bindings.get(skill_key_constant)
                
                if skill_id_to_deactivate:
                    self.player.deactivate_skill(skill_id_to_deactivate)
# Check for interaction with Portals
        if event.type == pygame.MOUSEBUTTONDOWN:
            world_x = -1
            world_y = -1
            if event.button == 1:  # Left-click
                # Get the mouse position in world coordinates
                world_x = (event.pos[0] + self.camera_x * self.zoom_level) / self.zoom_level
                world_y = (event.pos[1] + self.camera_y * self.zoom_level) / self.zoom_level

            for portal in self.portals:
                if isinstance(portal, BossPortal) and portal.rect.collidepoint(world_x, world_y):
                    self.game.scene_manager.set_scene("boss_room", self.player, self.hud, friendly_entities=self.friendly_entities.sprites()) # Pass friendly entities
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(os.path.join(os.getcwd(), "data", "boss1.mp3"))
                    pygame.mixer.music.play(0)  # Play once
                    pygame.mixer.music.queue(os.path.join(os.getcwd(), "data", "boss.mp3"))  # Play the boss music in a loop
                    return  # Interact with only one portal at a time
        # Pass event to minimap
        if self.hud and self.hud.minimap:
            minimap_rect = self.hud.minimap.rect
            self.hud.minimap.handle_event(event, minimap_rect)
    def update(self, dt, entities=None):
        if self.player:  # Only update player if player exists
            self.player.update(dt)
        if self.hud:  # Only update HUD if HUD exists
            self.boss_system_manager.update(dt, self.player) # Update BossSystemManager and pass player
            entities_to_pass = entities if entities is not None else self.enemies
            self.hud.update(dt, entities_to_pass)

        self.debug_log()
        self.frame_count += 1

        # Update enemies
        if not self.tile_map:
            return
        self.enemies.update(dt, self.player, self.game.current_scene.tile_map, self.tile_size)
        
        # Update friendly entities
        self.friendly_entities.update(dt, self.player, self.game.current_scene.tile_map, self.tile_size)

        # Update portals
        # Add a check to ensure self.portals is a sprite group before updating
        if isinstance(self.portals, pygame.sprite.Group):
            self.portals.update(dt)
        else:
            # Optional: Log a warning if self.portals is not a sprite group
            print(f"BaseGameplayScene: Warning: Non-sprite object found in self.portals is not a sprite group Skipping update.")

        # Update projectiles
        self.projectiles.update(dt, self.player, self.game.current_scene.tile_map, self.tile_size)

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


        if hasattr(self.game, 'display_death_message') and self.display_death_message:
            current_time = pygame.time.get_ticks()
            if current_time - self.death_message_start_time > self.death_message_duration:
                self.display_death_message = False
                # Respawn the player in spawntown
                
                if self.player:
                    self.player.current_life = self.player.max_life
                    self.player.current_mana = self.player.max_mana


        # Store the previous zoom level
        previous_zoom_level = self.zoom_level

        # Limit zoom level
        self.zoom_level = max(1, min(self.zoom_level, 5))

        # Calculate camera position
        if self.player:  # Only calculate camera if player exists
            # Calculate the zoom factor
            zoom_factor = previous_zoom_level / self.zoom_level

            # Calculate the new camera position
            self.camera_x = self.player.rect.centerx - (self.game.settings.SCREEN_WIDTH / 2) / self.zoom_level + self.camera_offset_x
            self.camera_y = self.player.rect.centery - (self.game.settings.SCREEN_HEIGHT / 2) / self.zoom_level + self.camera_offset_y

            # Adjust camera position based on zoom factor
            self.camera_x = (self.player.rect.centerx - self.game.settings.SCREEN_WIDTH / 2) + (self.camera_x - (self.player.rect.centerx - self.game.settings.SCREEN_WIDTH / 2)) * zoom_factor + self.camera_offset_x
            self.camera_y = (self.player.rect.centery - self.game.settings.SCREEN_HEIGHT / 2) + (self.camera_y - (self.player.rect.centery - self.game.settings.SCREEN_HEIGHT / 2)) * zoom_factor + self.camera_offset_y
        else:
            self.camera_x = 0
            self.camera_y = 0

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
# Draw decorations
        for decoration in self.decorations:
            screen_x = decoration['x'] * self.tile_size - self.camera_x * self.zoom_level
            screen_y = decoration['y'] * self.tile_size - self.camera_y * self.zoom_level
            scaled_image = pygame.transform.scale(decoration['image'], (int(decoration['image'].get_width() * self.zoom_level), int(decoration['image'].get_height() * self.zoom_level)))
            screen.blit(scaled_image, (screen_x, screen_y))
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
                                        print(f"BaseGameplayScene: WARNING: No image for tile type '{tile_type_value}' at ({x},{y}). Drawing magenta.")
                                        pass
                            else:
                                # print(f"BaseGameplayScene: draw: Tile at ({{x}}, {{y}}) is off-screen. Screen pos: ({{tile_x:.2f}}, {{tile_y:.2f}})") # Debug log
                                if self.frame_count % 60 == 0:
                                    pass


            # Draw the player (centered on screen)
            if self.player:  # Only draw player if player exists
                self.player.draw(screen)

            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(screen, self.camera_x, self.camera_y, self.zoom_level)
            
            # Draw friendly entities
            for entity in self.friendly_entities:
                entity.draw(screen, self.camera_x, self.camera_y, self.zoom_level)

            # Draw portals
            for portal in self.portals:
                # Skip non-Sprite objects and log a warning
                if not isinstance(portal, pygame.sprite.Sprite):
                    continue
                portal.draw(screen, self.camera_x, self.camera_y, self.zoom_level)

            # Draw projectiles
            for projectile in self.projectiles:
                projectile.draw(screen, self.camera_x, self.camera_y, self.zoom_level)

            # Draw the HUD (unaffected by camera)
            if self.hud:  # Only draw HUD if HUD exists
                self.hud.draw(screen)
                hud_drawn = True

            # Draw dialogue if active
            if self.game.dialogue_manager.is_dialogue_active():
                self.game.dialogue_manager.draw(screen)

        else:
            hud_drawn = False

        if hasattr(self, 'display_death_message') and self.display_death_message and not self.death_sequence_initiated:
            self.death_sequence_initiated = True
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
            self.game.scene_manager.set_scene("spawn_town", friendly_entities=self.friendly_entities.sprites()) # Pass friendly entities
            if self.player:
                self.player.current_life = self.player.max_life
                self.player.current_mana = self.player.max_mana
                self.display_death_message = False
                self.death_sequence_initiated = False
