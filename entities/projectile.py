import pygame
import os
import math
from config.constants import TILE_SIZE

class Projectile(pygame.sprite.Sprite):
    def __init__(self, game, x, y, target_x, target_y, speed, damage, sprite_path):
        super().__init__()
        self.game = game
        self.image = self._load_sprite(sprite_path)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.damage = damage
        self.target_x = target_x
        self.target_y = target_y
        self.dx, self.dy = self._calculate_direction(x, y, target_x, target_y)
        self.lifetime = 3000 # Milliseconds, adjust as needed
        self.spawn_time = pygame.time.get_ticks()

    def _load_sprite(self, sprite_path):
        """Loads the projectile sprite, with error handling."""
        full_path = os.path.join(os.getcwd(), sprite_path)
        try:
            if not os.path.exists(full_path):
                print(f"Error: Projectile sprite file not found: {full_path}")
                placeholder = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2))
                placeholder.fill((255, 0, 0))  # Red color for missing texture
                return placeholder
            image = pygame.image.load(full_path).convert_alpha()
            return pygame.transform.scale(image, (TILE_SIZE // 2, TILE_SIZE // 2)) # Scale down for projectiles
        except pygame.error as e:
            print(f"Error loading projectile sprite {full_path}: {e}")
            placeholder = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2))
            placeholder.fill((255, 0, 0))  # Red color for missing texture
            return placeholder

    def _calculate_direction(self, start_x, start_y, target_x, target_y):
        """Calculates the normalized direction vector towards the target."""
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            return dx / dist, dy / dist
        return 0, 0

    def update(self, dt, player, tile_map, tile_size):
        # Move the projectile
        self.rect.x += self.dx * self.speed * dt
        self.rect.y += self.dy * self.speed * dt

        # Check for collision with player
        if self.rect.colliderect(player.rect):
            player.take_damage(self.damage)
            self.kill() # Remove projectile on hit

        # Check for collision with solid tiles (walls)
        if self._check_collision(tile_map, tile_size):
            self.kill() # Remove projectile on wall hit

        # Remove projectile after a certain lifetime
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

    def _check_collision(self, tile_map, tile_size):
        """Checks for collision with solid tiles."""
        # Get the tile coordinates the projectile is currently occupying
        proj_left_tile = int(self.rect.left / tile_size)
        proj_right_tile = int(self.rect.right / tile_size)
        proj_top_tile = int(self.rect.top / tile_size)
        proj_bottom_tile = int(self.rect.bottom / tile_size)

        # Clamp tile coordinates to map boundaries
        map_width_tiles = len(tile_map[0])
        map_height_tiles = len(tile_map)

        proj_left_tile = max(0, min(proj_left_tile, map_width_tiles - 1))
        proj_right_tile = max(0, min(proj_right_tile, map_width_tiles - 1))
        proj_top_tile = max(0, min(proj_top_tile, map_height_tiles - 1))
        proj_bottom_tile = max(0, min(proj_bottom_tile, map_height_tiles - 1))

        # Iterate over the tiles the projectile overlaps with
        for y in range(proj_top_tile, proj_bottom_tile + 1):
            for x in range(proj_left_tile, proj_right_tile + 1):
                if 0 <= y < map_height_tiles and 0 <= x < map_width_tiles:
                    tile_type = tile_map[y][x]
                    if tile_type == 'wall':
                        return True
        return False

    def draw(self, screen, camera_x, camera_y, zoom_level):
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * zoom_level), int(self.rect.height * zoom_level)))
        screen_x = (self.rect.x - camera_x) * zoom_level
        screen_y = (self.rect.y - camera_y) * zoom_level
        # Draw a glow/outline effect behind the projectile for better visibility
        glow_radius = int(scaled_image.get_width() * 0.3) # A little bigger than the graphic
        glow_color = (255, 0, 0) # Bright red

        # Calculate the center of the projectile on screen
        center_x = screen_x + scaled_image.get_width() / 2
        center_y = screen_y + scaled_image.get_height() / 2

        pygame.draw.circle(screen, glow_color, (int(center_x), int(center_y)), glow_radius)

        # Draw the actual projectile image on top
        screen.blit(scaled_image, (screen_x, screen_y))