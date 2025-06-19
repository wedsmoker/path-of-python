import pygame
import json
import os
import random
from core.base_gameplay_scene import BaseGameplayScene
from entities.player import Player
from entities.npc import NPC
from ui.hud import HUD
from world.map_generator import MapGenerator, SpawnTownMapGenerator
from core.pathfinding import Pathfinding  # Import the Pathfinding class
from config.constants import ( # Import necessary constants
    TILE_SIZE,
    KEY_RIGHT_MOUSE, KEY_PAGE_UP, KEY_PAGE_DOWN,
    KEY_SKILL_1, KEY_SKILL_2, KEY_SKILL_3, KEY_SKILL_4
)
from core.swamp_cave_dungeon import SwampCaveDungeon # Import the dungeon scene
from config import settings # Import settings
from items.weapon import Weapon # Import the Weapon class
from items.potion import HealthPotion # Import the HealthPotion class
from ui.shop_window import ShopWindow
from core.utils import draw_text

# Function to create an NPC with random sprites
def create_npc(game, x, y, name, dialogue_id):
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

    npc = NPC(game, x, y, TILE_SIZE, TILE_SIZE, (0, 255, 0), name, dialogue_id)
    
    return npc

class SpawnTown(BaseGameplayScene):
    def __init__(self, game, player=None, hud=None, friendly_entities=None):
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
            # Load portals from zone data
            self.portals = spawn_town_data.get("portals", [])
            # Get tileset name from zone data
            tileset_name = spawn_town_data.get("tile_set", "default")
             # Remove suffix
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"SpawnTown: Warning: Could not load initial player position, or portals from zone_data.json: {e}")
            # Fallback to default if data is missing or corrupted
            initial_player_x = game.settings.SCREEN_WIDTH // 2
            initial_player_y = game.settings.SCREEN_HEIGHT // 2
            self.portals = []

        # Instantiate player and HUD here
        if player is None:
            player = Player(game, initial_player_x, initial_player_y)
        if hud is None:
            hud = HUD(player, self)

        super().__init__(game, player, hud, tileset_name=tileset_name, friendly_entities=friendly_entities) # Pass player, hud, and friendly_entities to the base class

        self.name = "SpawnTown"

        # Unlock starting skill
        self.player.unlocked_skills.append("neural_interface")
        self.player.unlocked_skills.append("arc") # Unlock arc by default

        # Display messages
        self.display_message1 = True
        self.message1_start_time = pygame.time.get_ticks()
        self.message1_duration = 5000  # 5 seconds
        self.display_message2 = False
        self.message2_start_time = 0
        self.message2_duration = 5000  # 5 seconds
        self.display_message3 = False
        self.message3_start_time = 0
        self.message3_duration = 5000  # 5 seconds

        # Instantiate MapGenerator and then generate the map
        map_generator = SpawnTownMapGenerator(200, 200) # Create an instance with desired width and height
        all_map_data = map_generator.generate_all()
        self.tile_map = all_map_data['map']

        self.map_width = len(self.tile_map[0])
        self.map_height = len(self.tile_map)

        # Instantiate Pathfinding
        self.pathfinding = Pathfinding(game)  # Pass the game object to Pathfinding

        self.npcs = pygame.sprite.Group()
        # Add procedurally generated NPCs to the scene
        for entity_data in all_map_data.get('entities', []):
            if entity_data['type'] == 'npc':
                npc = create_npc(game, entity_data['x'] * TILE_SIZE, entity_data['y'] * TILE_SIZE, entity_data['name'], entity_data['dialogue_id'])
                self.npcs.add(npc)
        print(f"SpawnTown: Received {len(all_map_data.get('entities', []))} entities from map generator.")
        print(f"SpawnTown: Added {len(self.npcs)} NPCs to self.npcs group.")
        self.effects = pygame.sprite.Group() # Add effects group

        # Create some NPCs
        npc1 = create_npc(game, 600, 400, "Bob the Bold", "bob_dialogue")
        self.npcs.add(npc1)

        npc2 = create_npc(game, 700, 500, "Alice the Agile", "alice_dialogue")
        self.npcs.add(npc2)

        npc3 = create_npc(game, 800, 400, "Charlie the Calm", "charlie_dialogue")
        self.npcs.add(npc3)
        self.charlie = npc3 # Store charlie for shop positioning

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
        self.ui_elements = [] # List to store UI elements
        self.shop_window = None # Initialize shop_window to None
        self.player.money = 100 # Starting money
        self.shop_message = None

    def enter(self):
        self.game.logger.info("Entering SpawnTown.")

        if not pygame.mixer.music.get_busy():
            # Load music files from the data/music directory
            music_dir = os.path.join(os.getcwd(), "data", "music")
            self.music_files = [f for f in os.listdir(music_dir) if os.path.isfile(os.path.join(music_dir, f))]
            self.current_music_index = 0

            # Define a function to play the next song
            def play_next_song():
                if self.music_files:
                    next_song = os.path.join(music_dir, self.music_files[self.current_music_index % len(self.music_files)])
                    pygame.mixer.music.load(next_song)
                    pygame.mixer.music.play()
                    self.current_music_index += 1
                else:
                    print("No music files found in data/music/")

            # Set the function to be called when a song finishes
            def music_end_callback():
                play_next_song()

            # Set the end event for the music
            pygame.mixer.music.set_endevent(pygame.USEREVENT+1)

            # Set the function to be called when a song finishes
            pygame.mixer.music.set_endevent(pygame.USEREVENT+1)

            # Start playing the music
            play_next_song()

        pygame.event.clear(pygame.USEREVENT+1)

    def exit(self):
        self.game.logger.info("Exiting SpawnTown.")

    def open_shop_window(self):
        """Opens the shop window in the spawn town scene next to Charlie."""
        try:
            with open('data/items.json', 'r') as f:
                items_data = json.load(f)
        except FileNotFoundError:
            self.game.logger.error("ERROR: items.json not found.")
            return
        except json.JSONDecodeError:
            self.game.logger.error("ERROR: Could not decode items.json. Check for JSON syntax errors.")
            return

        # Combine items from all categories
        all_items = []
        for category in items_data:
            all_items.extend(items_data[category])

        # Assuming there's a ShopWindow class in ui/shop_window.py

        # Get Charlie's position in the spawn town scene
        charlie_x = self.charlie.rect.x
        charlie_y = self.charlie.rect.y

        # Calculate the shop window position (next to Charlie)
        shop_x = charlie_x + 50  # Adjust the offset as needed
        shop_y = charlie_y

        # Create the shop window
        self.shop_window = ShopWindow(shop_x, shop_y, items_data, self.game)
        self.add_ui_element(self.shop_window)
        self.game.dialogue_manager.end_dialogue()
        if self.charlie:
            self.charlie.in_dialogue = False
        if self.shop_window:
            self.shop_window.is_open = True

    def close_shop_window(self):
        """Closes the shop window."""
        if self.shop_window:
            self.ui_elements.remove(self.shop_window)
            self.shop_window = None
            if self.charlie:
                self.charlie.in_dialogue = False
            if self.game.dialogue_manager:
                self.game.dialogue_manager.start_dialogue(self.charlie.dialogue_id)
        self.shop_message = None

    def add_ui_element(self, element):
        """Adds a UI element to the list of elements to be drawn."""
        self.ui_elements.append(element)

    def handle_event(self, event):
        # Open shop window if dialogue option is chosen
        for npc in self.npcs:
            if npc.name == "Charlie the Calm" and npc.in_dialogue and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.open_shop_window()
                break

        super().handle_event(event) # Call base class event handler

        if self.shop_window:
            shop_action = self.shop_window.handle_event(event) # Handle shop window events
            if shop_action == "close":
                self.close_shop_window()
                return
            elif shop_action:
                # Try to buy the item
                if 'price' in shop_action:
                    if self.player.money >= shop_action['price']:
                        self.player.money -= shop_action['price']
                        print(f"Bought {shop_action['name']}! Remaining money: {self.player.money}")
                        self.player.inventory.add_item(shop_action, 1)
                        self.shop_message = f"Bought {shop_action['name']}!"
                        #self.close_shop_window() # REMOVE
                    else:
                        print("Not enough money!")
                        self.shop_message = "Not enough money!"
                return


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
                    self.game.scene_manager.set_scene(target_scene, player=self.player, hud=self.hud, friendly_entities=self.friendly_entities.sprites())
                    return

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        # Update NPCs and Effects
        self.npcs.update(dt)
        self.effects.update(dt)

        # Combine NPCs for the minimap
        all_entities = self.npcs.sprites()

        # Pass the combined list of entities to the base class update, which passes it to the HUD
        super().update(dt, entities=all_entities)

        # Message 1
        if self.display_message1:
            if current_time - self.message1_start_time > self.message1_duration:
                self.display_message1 = False
                self.display_message2 = True
                self.message2_start_time = current_time

        # Message 2
        if self.display_message2:
            if current_time - self.message2_start_time > self.message2_duration:
                self.display_message2 = False
                self.display_message3 = True
                self.message3_start_time = current_time

        # Message 3
        if self.display_message3:
            if current_time - self.message3_start_time > self.message3_duration:
                self.display_message3 = False


    def draw(self, screen):
         # Debug log
        if hasattr(self, 'tile_map') and self.tile_map:
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

        # Display messages
        font = pygame.font.Font(None, 50)
        if self.display_message1:
            text_surface = font.render("Left click for movement...", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)
        elif self.display_message2:
            text_surface = font.render("Right click to blink...", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)
        elif self.display_message3:
            text_surface = font.render("Mouse side button to attack...", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)

        self.draw_ui_elements(screen) # Draw UI elements

        if self.shop_message:
            draw_text(screen, self.shop_message, 24, (255, 255, 255), settings.SCREEN_WIDTH // 2, 50, align="center")

    def draw_ui_elements(self, screen):
        """Draws all UI elements in the scene."""
        for element in self.ui_elements:
            element.draw(screen)

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

                # Move these lines inside the loop
                portal_x = portal.get("location", [0, 0])[0]
                portal_y = portal.get("location", [0, 0])[1]
                portal_rect = pygame.Rect(portal_x, portal_y, 64, 64)  # Example size
                self.portal_rects.append(portal_rect)

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"SpawnTown: Warning: Could not load portal data from zone_data.json: {e}")

    @property
    def player_money(self):
        return self.player.money

    @player_money.setter
    def player_money(self, value):
        self.player.money = value

    def next_song(self):
        if self.music_files:
            self.current_music_index += 1
            next_song = os.path.join(os.getcwd(), "data", "music", self.music_files[self.current_music_index % len(self.music_files)])
            pygame.mixer.music.load(next_song)
            pygame.mixer.music.play()
        else:
            print("No music files found in data/music/")