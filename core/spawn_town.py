import pygame
import json
import os
import random
from core.base_gameplay_scene import BaseGameplayScene
from entities.player import Player
from entities.npc import NPC
from entities.enemy import Enemy # Import Enemy class
from ui.hud import HUD
from world.map_generator import MapGenerator, SpawnTownMapGenerator
from core.pathfinding import Pathfinding  # Import the Pathfinding class
from config.constants import ( # Import necessary constants
    ENEMY_SPAWN_DISTANCE, ENEMY_SPAWN_COOLDOWN, TILE_SIZE,
    KEY_RIGHT_MOUSE, KEY_PAGE_UP, KEY_PAGE_DOWN,
    KEY_SKILL_1, KEY_SKILL_2, KEY_SKILL_3, KEY_SKILL_4
)
import math # Import math for distance calculation
from core.swamp_cave_dungeon import SwampCaveDungeon # Import the dungeon scene
from config import settings # Import settings
from items.weapon import Weapon # Import the Weapon class
from items.potion import HealthPotion # Import the HealthPotion class

class SpawnTown(BaseGameplayScene):
    def __init__(self, game):
        # Load initial player position from zone_data.json
        initial_player_x = 0
        initial_player_y = 0
        tileset_name = "default_tileset"  # Default tileset
        try:
            zone_data_path = os.path.join(os.getcwd(), "data", "zone_data.json")
            with open(zone_data_path, "r") as f:
                zone_data = json.load(f)
            spawn_town_data = zone_data["zones"]["spawn_town"]
            initial_player_x, initial_player_y = spawn_town_data["initial_player_position"]
            # Get allowed enemies from zone data
            self.allowed_enemies = spawn_town_data.get("allowed_enemies", [])
            # Load portals from zone data
            self.portals = spawn_town_data.get("portals", [])
            # Get tileset name from zone data
            tileset_name = spawn_town_data.get("tile_set", "default")
             # Remove suffix
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"SpawnTown: Warning: Could not load initial player position, allowed enemies, or portals from zone_data.json: {e}")
            # Fallback to default if data is missing or corrupted
            initial_player_x = game.settings.SCREEN_WIDTH // 2
            initial_player_y = game.settings.SCREEN_HEIGHT // 2
            self.allowed_enemies = []
            self.portals = []

        # Instantiate player and HUD here
        player = Player(game, initial_player_x, initial_player_y)
        hud = HUD(player, self)

        super().__init__(game, player, hud, tileset_name=tileset_name) # Pass player and hud to the base class

        self.name = "SpawnTown"

        # Unlock starting skill
        self.player.unlocked_skills.append("neural_interface")
        self.player.unlocked_skills.append("arc") # Unlock arc by default

        # Display "RIGHT CLICK TO ARC" message
        self.display_message = True
        self.message_start_time = pygame.time.get_ticks()
        self.message_duration = 5000 # 5 seconds

        # Instantiate MapGenerator and then generate the map
        map_generator = SpawnTownMapGenerator(200, 200) # Create an instance with desired width and height
        all_map_data = map_generator.generate_all()
        self.tile_map = all_map_data['map']

        self.map_width = len(self.tile_map[0])
        self.map_height = len(self.tile_map)

        # Instantiate Pathfinding
        self.pathfinding = Pathfinding(game)  # Pass the game object to Pathfinding

        self.npcs = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group() # Add enemy group
        self.effects = pygame.sprite.Group() # Add effects group
        self.last_enemy_spawn_time = pygame.time.get_ticks() # Initialize enemy spawn timer

        # Function to create an NPC with random sprites
        def create_npc(x, y, name, dialogue_id):
            head_dir = os.path.join(os.getcwd(), "graphics", "player", "head")
            legs_dir = os.path.join(os.getcwd(), "graphics", "player", "legs")
            hand1_dir = os.path.join(os.getcwd(), "graphics", "player", "hand1")

            head_sprites = [f for f in os.listdir(head_dir) if os.path.isfile(os.path.join(head_dir, f))]
            legs_sprites = [f for f in os.listdir(legs_dir) if os.path.isfile(os.path.join(legs_dir, f))]
            hand1_sprites = [f for f in os.listdir(hand1_dir) if os.path.isfile(os.path.join(hand1_dir, f))]

            head_sprite = random.choice(head_sprites) if head_sprites else None
            # legs_sprite = random.choice(legs_sprites) if legs_sprites else None # REMOVE LEGS SPRITE
            legs_sprite = None # REMOVE LEGS SPRITE
            hand1_sprite = random.choice(hand1_sprites) if hand1_sprites else None

            # Combine the sprites into a single surface
            npc_image = pygame.Surface((TILE_SIZE, TILE_SIZE * 2), pygame.SRCALPHA)  # Assuming 32x64 is a reasonable size

            try:
                base_sprite = pygame.image.load(os.path.join(os.getcwd(), "graphics", "player", "base", "human_m.png")).convert_alpha()
                base_sprite = pygame.transform.scale(base_sprite, (TILE_SIZE, TILE_SIZE))
                npc_image.blit(base_sprite, (0, 0))

                if legs_sprite:
                    legs_path = os.path.join(legs_dir, legs_sprite)
                    legs = pygame.image.load(legs_path).convert_alpha()
                    legs = pygame.transform.scale(legs, (TILE_SIZE, TILE_SIZE))
                    npc_image.blit(legs, (0, TILE_SIZE))

                if head_sprite:
                    head_path = os.path.join(head_dir, head_sprite)
                    head = pygame.image.load(head_path).convert_alpha()
                    head = pygame.transform.scale(head, (TILE_SIZE, TILE_SIZE))
                    npc_image.blit(head, (0, 0))

                if hand1_sprite:
                    hand1_path = os.path.join(hand1_dir, hand1_sprite)
                    hand1 = pygame.image.load(hand1_path).convert_alpha()
                    hand1 = pygame.transform.scale(hand1, (TILE_SIZE, TILE_SIZE))
                    npc_image.blit(hand1, (0, int(TILE_SIZE / 2))) # Blit hand1 below head

            except FileNotFoundError as e:
                print(f"Error loading NPC sprite: {e}")
                npc_image.fill((255, 0, 255))  # Magenta for missing texture
            except Exception as e:
                print(f"An unexpected error occurred loading NPC sprite: {e}")
                npc_image.fill((255, 0, 255)) # Magenta for error

            npc = NPC(game, x, y, TILE_SIZE, TILE_SIZE * 2, (0, 255, 0), name, dialogue_id)
            npc.image = npc_image
            return npc

        # Create some NPCs
        npc1 = create_npc(600, 400, "Bob the Bold", "bob_dialogue")
        self.npcs.add(npc1)

        npc2 = create_npc(700, 500, "Alice the Agile", "alice_dialogue")
        self.npcs.add(npc2)

        npc3 = create_npc(800, 400, "Charlie the Calm", "charlie_dialogue")
        self.npcs.add(npc3)

        # Load portal images and create portal rects
        self.portal_images = {}
        self.portal_rects = []
        try:
            zone_data_path = os.path.join(os.getcwd(), "data", "zone_data.json")
            with open(zone_data_path, "r") as f:
                zone_data = json.load(f)
            spawn_town_data = zone_data["zones"]["spawn_town"]
            self.portals = spawn_town_data.get("portals", [])

            for portal in self.portals:
                portal_image = None
                portal_image_path = portal.get("graphic")
                if portal_image_path:
                    full_path = os.path.join(os.getcwd(), portal_image_path)
                    try:
                        portal_image = pygame.image.load(full_path).convert_alpha()
                        self.portal_images[portal["target_scene"]] = portal_image
                    except FileNotFoundError:
                        print(f"SpawnTown: Warning: Could not load portal image: {full_path}")

            portal_x = portal.get("location", [0, 0])[0]
            portal_y = portal.get("location", [0, 0])[1]
            portal_rect = pygame.Rect(portal_x, portal_y, 64, 64)  # Example size
            self.portal_rects.append(portal_rect)

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"SpawnTown: Warning: Could not load portal data from zone_data.json: {e}")

        # Create items
        weapon = Weapon("Basic Sword", "A simple sword.", "sword", 10)
        health_potion = HealthPotion("Health Potion", "A potion that heals you.")

        # Add items to player's inventory
        self.player.inventory.add_item(health_potion, 1)
        self.player.inventory.add_item(weapon, 1)
        self.load_portal_data()

    def spawn_enemy(self):
        """Spawns a new enemy at a random location within a certain distance of the player."""
        if not self.allowed_enemies:
            # print("No allowed enemies defined for this zone.") # Commented out to reduce console spam
            return

        # For now, just spawn a generic enemy. In the future, use allowed_enemies to pick type.
        # enemy_type = random.choice(self.allowed_enemies) # Use this when different enemy types are implemented

        angle = random.uniform(0, 2 * math.pi)  # Random angle in radians
        # Spawn relative to the player's current position
        player_pos = self.player.rect.center
        x = player_pos[0] + ENEMY_SPAWN_DISTANCE * math.cos(angle)
        y = player_pos[1] + ENEMY_SPAWN_DISTANCE * math.sin(angle)

        # Create a generic enemy for now
        # TODO: Use enemy data from zone_data.json for SpawnTown enemies
        new_enemy = Enemy(self.game, x, y, {"name": "Generic Enemy", "health": 50, "damage": 5, "speed": 50, "sprite_path": None}) # Use the updated Enemy constructor
        self.enemies.add(new_enemy)
        # print(f"Spawned a Generic Enemy at ({int(x)}, {int(y)})!") # Commented out to reduce console spam)


    def handle_event(self, event):
        super().handle_event(event) # Call base class event handler

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left-click
            # Check for NPC interaction
            for npc in self.npcs:
                # Calculate NPC's screen position
                npc_screen_x = (npc.rect.x - self.camera_x) * self.zoom_level
                npc_screen_y = (npc.rect.y - self.camera_y) * self.zoom_level

                # Create a rect for the NPC at its screen position
                npc_screen_rect = pygame.Rect(npc_screen_x, npc_screen_y,
                                              npc.rect.width * self.zoom_level,
                                              npc.rect.height * self.zoom_level)
                # print(f"SpawnTown: handle_event: event.pos={event.pos}, npc_screen_rect={npc_screen_rect}") # Commented out to reduce console spam

                if npc_screen_rect.collidepoint(event.pos):
                    npc.interact(self.player) # Pass the player object
                    return # Consume event if NPC is interacted with

            # Check for portal interaction
            for i, portal_rect in enumerate(self.portal_rects):
                # Calculate portal's screen position
                portal_screen_x = (portal_rect.x - self.camera_x) * self.zoom_level
                portal_screen_y = (portal_rect.y - self.camera_y) * self.zoom_level

                # Create a rect for the portal at its screen position
                portal_screen_rect = pygame.Rect(portal_screen_x, portal_screen_y,
                                                 portal_rect.width * self.zoom_level,
                                                 portal_rect.height * self.zoom_level)

                if portal_screen_rect.collidepoint(event.pos):
                    print(f"Interacted with portal {i}! Changing scene to {self.portals[i]['target_scene']}...") # Debug print
                    # Trigger scene change to the target scene
                    target_scene = self.portals[i]['target_scene']
                    self.game.scene_manager.set_scene(target_scene, player=self.player, hud=self.hud)
                    return

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        # Enemy Spawning Logic
        if current_time - self.last_enemy_spawn_time > ENEMY_SPAWN_COOLDOWN:
            if len(self.enemies) < 5:  # Limit the number of enemies
                self.spawn_enemy()
            self.last_enemy_spawn_time = current_time

        # Update NPCs and Enemies
        self.npcs.update(dt)
        self.enemies.update(dt)
        self.effects.update(dt)

        # Combine NPCs and Enemies for the minimap
        all_entities = self.npcs.sprites() + self.enemies.sprites()

        # Pass the combined list of entities to the base class update, which passes it to the HUD
        super().update(dt, entities=all_entities)

        # Check if message should be displayed
        if self.display_message:
            if current_time - self.message_start_time > self.message_duration:
                self.display_message = False


    def draw(self, screen):
        print("SpawnTown: draw: Drawing tilemap...") # Debug log
        if hasattr(self, 'tile_map') and self.tile_map:
            print(f"SpawnTown: draw: tilemap is valid. Map dimensions: {self.map_width}x{self.map_height}") # Debug log
            print(f"SpawnTown: draw: Camera X: {self.camera_x}, Camera Y: {self.camera_y}, Zoom: {self.zoom_level}") # Debug log
            super().draw(screen) # Draw map, player, and HUD from base class
        else:
            print("SpawnTown: draw: WARNING: tile_map is invalid or not set!") # Debug log

        # Draw NPCs relative to the camera
        for npc in self.npcs:
            # Calculate NPC's screen position
            npc_screen_x = (npc.rect.x - self.camera_x) * self.zoom_level
            npc_screen_y = (npc.rect.y - self.camera_y) * self.zoom_level

            # Scale NPC image
            scaled_npc_image = pygame.transform.scale(npc.image, (int(npc.rect.width * self.zoom_level), int(npc.rect.height * self.zoom_level)))

            screen.blit(scaled_npc_image, (npc_screen_x, npc_screen_y))

        # Draw Enemies relative to the camera
        for enemy in self.enemies:
             # Calculate Enemy's screen position
            enemy_screen_x = (enemy.rect.x - self.camera_x) * self.zoom_level
            enemy_screen_y = (enemy.rect.y - self.camera_y) * self.zoom_level

            # Scale Enemy image (using a simple colored square for now)
            # In the future, load actual enemy sprites
            scaled_enemy_image = pygame.transform.scale(enemy.image, (int(enemy.rect.width * self.zoom_level), int(enemy.rect.height * self.zoom_level)))

            screen.blit(scaled_enemy_image, (enemy_screen_x, enemy_screen_y))

        # Draw effects
        for effect in self.effects:
            effect_screen_x = (effect.rect.x - self.camera_x) * self.zoom_level
            effect_screen_y = (effect.rect.y - self.camera_y) * self.zoom_level
            screen.blit(effect.image, (effect_screen_x, effect_screen_y))

        # Draw the dungeon portals
        for i, portal_rect in enumerate(self.portal_rects):
            portal_screen_x = (portal_rect.x - self.camera_x) * self.zoom_level
            portal_screen_y = (portal_rect.y - self.camera_y) * self.zoom_level
            scaled_portal_width = int(portal_rect.width * self.zoom_level)
            scaled_portal_height = int(portal_rect.height * self.zoom_level)
            scaled_portal_rect = pygame.Rect(portal_screen_x, portal_screen_y, scaled_portal_width, scaled_portal_height)

            portal_image = self.portal_images.get(self.portals[i]['target_scene'])
            if portal_image:
                scaled_portal_image = pygame.transform.scale(portal_image, (scaled_portal_width, scaled_portal_height))
                screen.blit(scaled_portal_image, (portal_screen_x, portal_screen_y))
            else:
                pygame.draw.rect(screen, (255, 0, 0), scaled_portal_rect) # Red placeholder

        # Display "RIGHT CLICK TO ARC" message
        if self.display_message:
            font = pygame.font.Font(None, 50)
            text_surface = font.render("RIGHT CLICK TO ARC", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)

    def load_portal_data(self):
        """Loads portal data from zone_data.json and updates the portal_images and portal_rects lists."""
        self.portal_images = {}
        self.portal_rects = []
        try:
            zone_data_path = os.path.join(os.getcwd(), "data", "zone_data.json")
            with open(zone_data_path, "r") as f:
                zone_data = json.load(f)
            spawn_town_data = zone_data["zones"]["spawn_town"]
            self.portals = spawn_town_data.get("portals", [])

            for portal in self.portals:
                portal_image = None
                portal_image_path = portal.get("graphic")
                if portal_image_path:
                    full_path = os.path.join(os.getcwd(), portal_image_path)
                    try:
                        portal_image = pygame.image.load(full_path).convert_alpha()
                        self.portal_images[portal["target_scene"]] = portal_image
                    except FileNotFoundError:
                        print(f"SpawnTown: Warning: Could not load portal image: {full_path}")

                portal_x = portal.get("location", [0, 0])[0]
                portal_y = portal.get("location", [0, 0])[1]
                portal_rect = pygame.Rect(portal_x, portal_y, 64, 64)  # Example size
                self.portal_rects.append(portal_rect)

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"SpawnTown: Warning: Could not load portal data from zone_data.json: {e}")