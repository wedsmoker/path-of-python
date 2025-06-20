
import pygame
import json
import os
from core.base_gameplay_scene import BaseGameplayScene

class arena2(BaseGameplayScene):
    def __init__(self, game, player, hud, dungeon_data=None):
        super().__init__(game, player, hud, tileset_name=dungeon_data.get("tileset", "default"), dungeon_data=dungeon_data)
        self.name = "arena2"
        self.dungeon_data = dungeon_data
        self.tile_map = self.dungeon_data["tile_map"]
        self.map_width = self.dungeon_data["width"]
        self.map_height = self.dungeon_data["height"]
        self.entities = []  # Initialize an empty list of entities
        self.effects = pygame.sprite.Group()  # Initialize the effects group

    def load_dungeon_data(self, dungeon_name):
        # This method is no longer strictly needed if dungeon_data is passed directly,
        # but kept for compatibility or if other parts of the code rely on it.
        dungeon_data_path = os.path.abspath(os.path.join(os.getcwd(), "data", "dungeons", f'{dungeon_name}.json'))
        try:
            with open(dungeon_data_path, "r") as f:
                dungeon_data = json.load(f)
            return dungeon_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading dungeon data from {dungeon_data_path}: {e}")
            return {}

    def update(self, dt):
        super().update(dt, self.entities)  # Pass the entities list to the update method
        self.effects.update(dt) # Update the effects

    def draw(self, screen):
        super().draw(screen)
        for sprite in self.effects:
            screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y))
