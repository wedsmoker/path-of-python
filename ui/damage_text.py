import pygame
import random

class DamageText(pygame.sprite.Sprite):
    def __init__(self, text, x, y, color, font_size=30, lifetime=2000, speed=0.1):
        super().__init__()
        self.text = text
        self.base_color = color
        self.font_size = font_size
        self.lifetime = lifetime # milliseconds
        self.speed = speed # pixels per millisecond (upwards movement)
        self.spawn_time = pygame.time.get_ticks()
        
        # Initial random horizontal drift
        self.initial_dx = random.uniform(-0.03, 0.03) # Small horizontal drift
        self.current_dx = self.initial_dx

        # Dynamic font size and color based on damage value (assuming text is a number)
        try:
            damage_value = int(text)
            # Scale font size based on damage (e.g., larger damage = larger text)
            self.font_size = int(font_size + (damage_value / 50.0) * 10) # Max +10 for 50 damage
            self.font_size = min(self.font_size, 50) # Cap max font size

            # Adjust color towards yellow/orange for higher damage
            r, g, b = self.base_color
            if damage_value > 20: # Example threshold for more vibrant color
                r = min(255, r + int((damage_value - 20) * 2))
                g = min(255, g + int((damage_value - 20) * 1))
                b = max(0, b - int((damage_value - 20) * 0.5))
            self.current_color = (r, g, b)
        except ValueError:
            self.current_color = self.base_color # Fallback if text is not a number
        
        self.font = pygame.font.Font(None, self.font_size)
        self.image = self.font.render(self.text, True, self.current_color)
        
        # Add a subtle outline/shadow for better readability
        outline_color = (0, 0, 0) # Black outline
        outline_thickness = 2
        outline_surface = self.font.render(self.text, True, outline_color)
        
        # Create a new surface to combine text and outline
        combined_width = self.image.get_width() + outline_thickness * 2
        combined_height = self.image.get_height() + outline_thickness * 2
        combined_surface = pygame.Surface((combined_width, combined_height), pygame.SRCALPHA)
        
        # Blit outline
        for dx_offset in range(-outline_thickness, outline_thickness + 1):
            for dy_offset in range(-outline_thickness, outline_thickness + 1):
                if dx_offset != 0 or dy_offset != 0: # Don't blit outline at center
                    combined_surface.blit(outline_surface, (dx_offset + outline_thickness, dy_offset + outline_thickness))
        
        # Blit main text
        combined_surface.blit(self.image, (outline_thickness, outline_thickness))
        self.image = combined_surface

        # Initial random offset for X position
        self.rect = self.image.get_rect(center=(x + random.uniform(-10, 10), y))

    def update(self, dt):
        # Move text upwards
        self.rect.y -= self.speed * dt

        # Apply horizontal drift
        self.rect.x += self.current_dx * dt

        # Fade out over time
        elapsed_time = pygame.time.get_ticks() - self.spawn_time
        if elapsed_time > self.lifetime:
            self.kill() # Remove sprite when lifetime is over
        else:
            alpha = 255 - int(255 * (elapsed_time / self.lifetime))
            self.image.set_alpha(alpha)

    def draw(self, screen, camera_x, camera_y, zoom_level):
        # Calculate screen coordinates relative to camera and zoom
        screen_x = (self.rect.x - camera_x) * zoom_level
        screen_y = (self.rect.y - camera_y) * zoom_level
        
        # Scale the image based on zoom level
        scaled_image = pygame.transform.scale(self.image, (int(self.image.get_width() * zoom_level), int(self.image.get_height() * zoom_level)))
        
        screen.blit(scaled_image, (screen_x, screen_y))