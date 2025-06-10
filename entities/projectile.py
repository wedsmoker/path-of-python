import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, speed, damage, color, image = None, radius=5):
        super().__init__()
        if image is None:
            self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, color, (radius, radius), radius)
        else:
            self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.damage = damage
        self.color = color
        self.radius = radius

        # Calculate direction vector
        self.dx = target_x - x
        self.dy = target_y - y
        magnitude = (self.dx**2 + self.dy**2)**0.5
        if magnitude > 0:
            self.dx /= magnitude
            self.dy /= magnitude
        else:
            self.kill() # If no target, destroy immediately

    def update(self, dt):
        self.rect.x += self.dx * self.speed * dt
        self.rect.y += self.dy * self.speed * dt

        # Simple boundary check (remove if off-screen)
        if not pygame.Rect(0, 0, pygame.display.get_surface().get_width(), pygame.display.get_surface().get_height()).colliderect(self.rect):
            self.kill()

    def hit(self, target):
        # Placeholder for hit logic (e.g., apply damage, status effects)
        print(f"Projectile hit {target.name} for {self.damage} damage.")
        target.take_damage(self.damage)
        self.kill() # Destroy projectile on hit