import math
import pygame
import os
import random
import json
from config.constants import TILE_SIZE
from entities.enemy import Enemy  # Import the Enemy class
from entities.summon_skeletons import Skeleton, WraithEffect


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill((0, 128, 255))  # Blue color for the player
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 100  # Player speed
        self.level = 1
        self.current_mana = 100
        self.max_mana = 100
        self.experience = 0  # Add experience attribute
        self.dragging = False
        self.name = "Player" # Add name attribute

    def has_skill(self, skill_id):
        return True  # Assume the player has the skill

    def take_damage(self, amount):
        pass

    def gain_experience(self, amount):
        self.experience += amount

    def update(self, dt, tile_map, tile_size):
        if self.dragging:
            pos = pygame.mouse.get_pos()
            self.rect.center = pos

    def _check_collision(self, tile_map, tile_size):
        """Checks for collision with solid tiles."""
        # Get the tile coordinates the enemy is currently occupying
        player_left_tile = int(self.rect.left / tile_size)
        player_right_tile = int(self.rect.right / tile_size)
        player_top_tile = int(self.rect.top / tile_size)
        player_bottom_tile = int(self.rect.bottom / tile_size)

        # Clamp tile coordinates to map boundaries
        map_width_tiles = len(tile_map[0])
        map_height_tiles = len(tile_map)

        player_left_tile = max(0, min(player_left_tile, map_width_tiles - 1))
        player_right_tile = max(0, min(player_right_tile, map_width_tiles - 1))
        player_top_tile = max(0, min(player_top_tile, map_height_tiles - 1))
        player_bottom_tile = max(0, min(player_bottom_tile, map_height_tiles - 1))

        # Iterate over the tiles the enemy overlaps with
        for y in range(player_top_tile, player_bottom_tile + 1):
            for x in range(player_left_tile, player_right_tile + 1):
                if 0 <= y < map_height_tiles and 0 <= x < map_width_tiles:
                    tile_type = tile_map[y][x]
                    # Assuming 'wall' is a solid tile type. Add other solid types as needed.
                    if tile_type == 'wall':
                        # print(f"Enemy collision with wall at tile ({x}, {y})") # Debug print
                        return True
        return False

    def draw(self, screen, camera_x, camera_y, zoom_level):
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * zoom_level), int(self.rect.height * zoom_level)))
        screen_x = (self.rect.x - camera_x) * zoom_level
        screen_y = (self.rect.y - camera_y) * zoom_level
        screen.blit(scaled_image, (screen_x, screen_y))


class SkillTest:
    def __init__(self):
        pygame.init()
        self.screen_width = 1600  # Increased width
        self.screen_height = 1200  # Increased height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Skill Test")

        # Load tilemap
        self.dungeon_data = self._load_dungeon_data("data/dungeons/grass.json")
        self.tileset_name = self.dungeon_data.get("tileset", "grassland")
        self.tile_size = TILE_SIZE // 2 # Reduced tile size - Define tile_size BEFORE loading tile images
        self.tile_images = {}
        self._load_tile_images()
        self.tile_map = self.dungeon_data.get("tile_map", [['wall'] * 10] * 10)
        self.map_width = self.dungeon_data.get('width', 50)
        self.map_height = self.dungeon_data.get('height', 50)

        # Create player
        self.player = Player(self, 400, 300)
        self.player_group = pygame.sprite.Group()
        self.player_group.add(self.player)

        # Load enemies (replace with your actual enemy loading logic)
        self.enemies = pygame.sprite.Group()
        self._load_enemies()

        # Set current_scene and its enemies
        self.current_scene = self
        self.current_scene.enemies = self.enemies

        self.clock = pygame.time.Clock()
        self.running = True
        self.skill = None # Generic skill

    def _load_dungeon_data(self, dungeon_path):
        """Loads dungeon data from a JSON file."""
        try:
            with open(dungeon_path, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print(f"Error: Dungeon file not found: {dungeon_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding dungeon JSON. Using default dungeon.")
            return {}

    def _load_tile_images(self):
        """Loads tile images based on the dungeon's tileset."""
        try:
            zone_data_path = os.path.join(os.getcwd(), "data", "zone_data.json")
            with open(zone_data_path, "r") as f:
                zone_data = json.load(f)

            tile_sets = zone_data.get("tile_sets", {})
            tileset_data = zone_data.get("tile_sets", {}).get(self.tileset_name)

            print(f"SkillTest: _load_tile_images: self.tileset_name = {self.tileset_name}")  # Added logging
            print(f"SkillTest: _load_tile_images: tileset_data = {tileset_data}")  # Added logging

            if tileset_data:
                # Load tile images from zone_data.json
                for tile_name, tile_path in tileset_data.items():
                    try:
                        full_path = os.path.join(os.getcwd(), tile_path)
                        if not os.path.exists(full_path):
                            print(f"SkillTest: Error: Tile image file not found: {full_path}")
                            self.tile_images[tile_name] = pygame.Surface((self.tile_size, self.tile_size))
                            self.tile_images[tile_name].fill((255, 0, 255))  # Magenta placeholder
                            continue

                        image = pygame.image.load(full_path).convert_alpha()
                        image = pygame.transform.scale(image, (self.tile_size, self.tile_size)) # Scale the image
                        self.tile_images[tile_name] = image
                        # print(f"SkillTest: Loaded tile image: {tile_name} from {full_path}")  # Added logging
                    except pygame.error as e:
                        print(f"SkillTest: Warning: Could not load tile image {full_path}: {e}")
                        self.tile_images[tile_name] = pygame.Surface((self.tile_size, self.tile_size))
                        self.tile_images[tile_name].fill((255, 0, 255))  # Magenta placeholder
            else:
                # Load tile images from a separate JSON file
                tileset_path = os.path.join(os.getcwd(), "data", "tilesets", f"{self.tileset_name}_tileset.json")
                with open(tileset_path, "r") as f:
                    tileset_data = json.load(f)

                for tile_name, tile_path in tileset_data.items():
                    try:
                        full_path = os.path.join(os.getcwd(), tile_path)
                        if not os.path.exists(full_path):
                            print(f"SkillTest: Error: Tile image file not found: {full_path}")
                            self.tile_images[tile_name] = pygame.Surface((self.tile_size, self.tile_size))
                            self.tile_images[tile_name].fill((255, 0, 255))  # Magenta placeholder
                            continue

                        image = pygame.image.load(full_path).convert_alpha()
                        image = pygame.transform.scale(image, (self.tile_size, self.tile_size)) # Scale the image
                        self.tile_images[tile_name] = image
                        # print(f"SkillTest: Loaded tile image: {tile_name} from {full_path}")  # Added logging
                    except pygame.error as e:
                        print(f"SkillTest: Warning: Could not load tile image {full_path}: {e}")
                        self.tile_images[tile_name] = pygame.Surface((self.tile_size, self.tile_size))
                        self.tile_images[tile_name].fill((255, 0, 255))  # Magenta placeholder

        except FileNotFoundError:
            print(f"SkillTest: Error: data/zone_data.json or tileset file not found. Cannot load tile images.")
        except json.JSONDecodeError:
            print(f"SkillTest: Error: Could not decode data/zone_data.json or tileset file. Check JSON format.")
        except KeyError as e:
            print(f"SkillTest: Error: Missing key in tileset data: {e}")
        
    def _load_enemies(self):
        """Loads enemy data and creates enemy instances."""
        try:
            with open("data/enemy_data.json", 'r') as file:
                enemy_data = json.load(file)
                # Create a few enemies
                for i in range(20): # Increased number of enemies
                    x = random.randint(100, 700)
                    y = random.randint(100, 500)
                    # Use a random enemy type from the loaded data
                    enemy_type = random.choice(list(enemy_data.keys()))
                    enemy_info = enemy_data[enemy_type]
                    enemy = Enemy(self, x, y, enemy_type, enemy_info['health'], enemy_info['damage'], enemy_info['speed'], enemy_info['sprite_path'])
                    self.enemies.add(enemy)
        except FileNotFoundError:
            print("Error: enemy_data.json not found.")
        except json.JSONDecodeError:
            print("Error decoding enemy_data.json.")

    def test_skill(self, skill):
        self.skill = skill

    def run(self):
        from entities.summon_skeletons import SummonSkeletons # This is the one line of code we keep
        self.test_skill(SummonSkeletons(self.player)) # Instantiate the skill

        while self.running:
            dt = self.clock.tick(60) / 1000  # Delta time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.player.rect.collidepoint(event.pos):
                            self.player.dragging = True
                        # Activate skill on left click, regardless of dragging
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if self.skill:
                            self.skill.activate(mouse_x, mouse_y)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.player.dragging = False

            self.update(dt)
            self.draw()

        pygame.quit()

    def update(self, dt):
        # Update player
        self.player.update(dt, self.tile_map, self.tile_size)

        # Find the nearest skeleton for each enemy
        for enemy in self.enemies:
            nearest_skeleton = None
            min_distance = float('inf')
            for sprite in self.enemies:
                if isinstance(sprite, Skeleton):
                    dx, dy = sprite.rect.centerx - enemy.rect.centerx, sprite.rect.centery - enemy.rect.centery
                    dist = math.hypot(dx, dy)
                    if dist < min_distance:
                        min_distance = dist
                        nearest_skeleton = sprite

            if isinstance(enemy, WraithEffect):
                enemy.update(dt, self.player, self.tile_map, self.tile_size)
            else:
                enemy.update(dt, self.player, self.tile_map, self.tile_size, nearest_skeleton=nearest_skeleton)


    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background

        # Draw tilemap
        for y in range(self.map_height):
            for x in range(self.map_width):
                if 0 <= y < len(self.tile_map) and 0 <= x < len(self.tile_map[y]):
                    tile_type_value = self.tile_map[y][x]
                    # Calculate the tile's position
                    tile_x = x * self.tile_size
                    tile_y = y * self.tile_size

                    # Get the tile image
                    tile_image = self.tile_images.get(tile_type_value)
                    if tile_image:
                        self.screen.blit(tile_image, (tile_x, tile_y))
                    else:
                        # Fallback to drawing a colored rectangle if image not found
                        color = (255, 0, 255)  # Magenta for missing textures
                        pygame.draw.rect(self.screen, color, (tile_x, tile_y, self.tile_size, self.tile_size))

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, 0, 0, 1)  # Assuming no camera

        # Draw skeletons (if any)
        for sprite in self.enemies:
            if isinstance(sprite, Skeleton):
                sprite.draw(self.screen, 0, 0, 1)

        # Draw player
        self.player.draw(self.screen, 0, 0, 1)

        pygame.display.flip()

if __name__ == "__main__":
    skill_test = SkillTest()
    skill_test.run()