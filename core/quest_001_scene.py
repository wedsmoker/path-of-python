import pygame
import json
import os
from core.base_gameplay_scene import BaseGameplayScene
from entities.player import Player
from entities.enemy import Enemy
from entities.npc import NPC
from items.item import Item
from ui.hud import HUD
from config.constants import TILE_SIZE

class Quest001Scene(BaseGameplayScene):
    def __init__(self, game, player=None, hud=None, dungeon_data=None):
        # Call BaseGameplayScene's init, passing dungeon_data for tileset name
        super().__init__(game, player, hud, tileset_name=dungeon_data.get('tileset', 'default'))
        self.game = game
        self.dungeon_data = dungeon_data
        self.tile_size = TILE_SIZE
        
        # Explicitly load map dimensions and tile map from dungeon_data
        # BaseGameplayScene does not set these directly from dungeon_data in its __init__
        self.tile_map = dungeon_data.get('tile_map', [])
        self.map_width = dungeon_data.get('width', 0)
        self.map_height = dungeon_data.get('height', 0)

        self.npcs = pygame.sprite.Group() # NPCs are specific to this scene
        self.effects = pygame.sprite.Group() # Effects are specific to this scene
        self.items = pygame.sprite.Group() # Items are specific to this scene
        self.name = "Quest001Scene" # Set scene name

        if self.dungeon_data:
            # BaseGameplayScene's __init__ loads enemies if dungeon_data is passed.
            # We only need to load NPCs and items here.
            self.load_scene_specific_entities(self.dungeon_data)
            self.load_decorations(self.dungeon_data.get('decorations', []))
            
            # Set player spawn point - find the 'player_spawn' tile or the first 'floor' tile
            player_spawn_x, player_spawn_y = 0, 0
            spawn_found = False
            if self.tile_map:
                for y, row in enumerate(self.tile_map):
                    for x, tile_type in enumerate(row):
                        if tile_type == 'player_spawn':
                            player_spawn_x = x * self.tile_size
                            player_spawn_y = y * self.tile_size
                            spawn_found = True
                            break
                        elif tile_type == 'floor' and not spawn_found: # Fallback to first floor tile if no specific spawn
                            player_spawn_x = x * self.tile_size
                            player_spawn_y = y * self.tile_size
                            spawn_found = True # Mark as found, but keep looking for 'player_spawn'
                    if spawn_found and 'player_spawn' in row: # If player_spawn was found in this row, break outer loop
                        break
                    elif spawn_found and 'player_spawn' not in row: # If only floor was found, and no player_spawn in this row, break
                        break
            
            if self.player:
                self.player.rect.x = player_spawn_x
                self.player.rect.y = player_spawn_y
        else:
            self.game.logger.error("Quest001Scene: No dungeon data provided.")

    # Renamed to be more specific, as BaseGameplayScene handles general entity loading (enemies)
    def load_scene_specific_entities(self, dungeon_data):
        # Load NPCs (if any)
        for npc_data in dungeon_data.get('npcs', []):
            npc_type = npc_data['type']
            x, y = npc_data['x'], npc_data['y']
            npc = NPC(self.game, npc_type, x, y)
            self.npcs.add(npc)

        # Load items (if any)
        for item_data in dungeon_data.get('items', []):
            item_name = item_data['name']
            x, y = item_data['x'], item_data['y']
            item = Item(item_name, x, y) # Assuming Item constructor takes name, x, y
            self.items.add(item)

    def enter(self):
        self.game.player = self.player
        self.game.hud = self.hud
        self.game.current_map = self.tile_map
        # Combine all sprite groups for game.all_sprites
        self.game.all_sprites = pygame.sprite.Group(
            self.player,
            self.enemies, # From BaseGameplayScene
            self.projectiles, # From BaseGameplayScene
            self.portals, # From BaseGameplayScene
            self.friendly_entities, # From BaseGameplayScene
            self.npcs, # Specific to Quest001Scene
            self.items, # Specific to Quest001Scene
            self.effects # Specific to Quest001Scene
        )
        self.game.logger.info("Entered Quest001Scene scene.")

    def exit(self):
        self.game.logger.info("Exited Quest001Scene scene.")

    def handle_event(self, event):
        super().handle_event(event) # Call base class handle_event for common input

    def update(self, dt):
        super().update(dt) # Call base class update for player, enemies, projectiles, portals, friendly_entities, camera
        
        # Update scene-specific entities
        self.npcs.update(dt) # NPCs might need their own update logic
        self.effects.update(dt) # Update effects
        
        # Check for player-item collisions
        collided_items = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in collided_items:
            self.player.inventory.add_item(item)
            self.game.logger.info(f"Player picked up {item.name}")

    def draw(self, screen):
        super().draw(screen) # Call base class draw for map, player, enemies, friendly_entities, portals, projectiles, HUD, dialogue
# Draw decorations
        for decoration in self.decorations:
            screen_x = decoration['x'] * self.tile_size - self.camera_x * self.zoom_level
            screen_y = decoration['y'] * self.tile_size - self.camera_y * self.zoom_level
            scaled_image = pygame.transform.scale(decoration['image'], (int(decoration['image'].get_width() * self.zoom_level * 2), int(decoration['image'].get_height() * self.zoom_level * 2)))
            screen.blit(scaled_image, (screen_x, screen_y))
        
        # Draw scene-specific entities (NPCs, items, and effects)
        for npc_sprite in self.npcs:
            # Calculate sprite's position relative to the camera
            npc_x = (npc_sprite.rect.x - self.camera_x) * self.zoom_level
            npc_y = (npc_sprite.rect.y - self.camera_y) * self.zoom_level
            scaled_npc_image = pygame.transform.scale(npc_sprite.image, (int(npc_sprite.image.get_width() * self.zoom_level), int(npc_sprite.image.get_height() * self.zoom_level)))
            screen.blit(scaled_npc_image, (npc_x, npc_y))

        for item_sprite in self.items:
            # Calculate sprite's position relative to the camera
            item_x = (item_sprite.rect.x - self.camera_x) * self.zoom_level
            item_y = (item_sprite.rect.y - self.camera_y) * self.zoom_level
            scaled_item_image = pygame.transform.scale(item_sprite.image, (int(item_sprite.image.get_width() * self.zoom_level), int(item_sprite.image.get_height() * self.zoom_level)))
            screen.blit(scaled_item_image, (item_x, item_y))

        for effect_sprite in self.effects:
            # Calculate sprite's position relative to the camera
            effect_x = (effect_sprite.rect.x - self.camera_x) * self.zoom_level
            effect_y = (effect_sprite.rect.y - self.camera_y) * self.zoom_level
            scaled_effect_image = pygame.transform.scale(effect_sprite.image, (int(effect_sprite.image.get_width() * self.zoom_level), int(effect_sprite.image.get_height() * self.zoom_level)))
            screen.blit(scaled_effect_image, (effect_x, effect_y))