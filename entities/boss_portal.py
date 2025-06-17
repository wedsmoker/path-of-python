import pygame
import os
from config.constants import TILE_SIZE

class BossPortal(pygame.sprite.Sprite):
    def __init__(self, game, x, y, boss_key):
        super().__init__()
        self.game = game
        self.boss_key = boss_key
        # Placeholder sprite - replace with an actual portal sprite
# Load the actual portal sprite
        portal_sprite_path = os.path.join('graphics', 'dc-dngn', 'gateways', 'dngn_enter_zot_open.png')
        try:
            self.image = pygame.image.load(portal_sprite_path).convert_alpha()
            # Scale the image to double its size
            self.image = pygame.transform.scale(self.image, (self.image.get_width() * 2, self.image.get_height() * 2))
        except pygame.error as e:
            print(f"Warning: Could not load portal sprite {portal_sprite_path}: {e}")
            # Fallback to placeholder if image loading fails
            self.image = pygame.Surface([TILE_SIZE * 2, TILE_SIZE * 2], pygame.SRCALPHA)
            self.image.fill((0, 255, 255)) # Cyan color for visibility
        self.rect = self.image.get_rect(topleft=(x, y))
        print(f"BossPortal initialized at ({x}, {y}) with boss_key: {self.boss_key}")

    def update(self, dt):
        # Check for player collision and interaction
        if self.rect.colliderect(self.game.player.rect):
            # In a real implementation, you'd check for a specific interaction key press
            # For now, let's just print a message
            print("Player is near the boss portal. Press interact key to enter.")
            # TODO: Add interaction logic (e.g., check for 'E' key press)

    def draw(self, screen, camera_x, camera_y, zoom_level):
        # Draw the portal sprite
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * zoom_level), int(self.rect.height * zoom_level)))
        screen_x = (self.rect.x - camera_x) * zoom_level
        screen_y = (self.rect.y - camera_y) * zoom_level
        screen.blit(scaled_image, (screen_x, screen_y))