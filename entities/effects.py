import pygame

class VisualEffect(pygame.sprite.Sprite):
    """Base class for temporary visual effects (e.g., explosions, hit effects)."""
    def __init__(self, x, y, duration, image=None, color=None, size=None):
        super().__init__()
        self.duration = duration # in seconds
        self.time_elapsed = 0.0

        if image:
            self.image = image
        elif color and size:
            self.image = pygame.Surface(size, pygame.SRCALPHA)
            self.image.fill(color)
        else:
            self.image = pygame.Surface((10, 10), pygame.SRCALPHA) # Default small transparent surface
            self.image.fill((255, 255, 255, 100)) # Default white, semi-transparent

        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt):
        self.time_elapsed += dt
        if self.time_elapsed >= self.duration:
            self.kill() # Remove effect when duration is over

class StatusEffect:
    """Base class for status effects (e.g., Burning, Poison, Chill)."""
    def __init__(self, target, duration, effect_id, potency=1.0):
        self.target = target
        self.duration = duration # in seconds
        self.time_remaining = duration
        self.effect_id = effect_id
        self.potency = potency
        self.is_active = True

    def apply(self):
        """Called when the effect is first applied."""
        pass

    def update(self, dt):
        """Called each frame to update the effect."""
        if not self.is_active:
            return

        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.remove()

    def remove(self):
        """Called when the effect is removed."""
        self.is_active = False
        print(f"Effect '{self.effect_id}' removed from {self.target.name}.")

# Example specific status effects (can be moved to combat/status_effects.py later)
class Burning(StatusEffect):
    def __init__(self, target, duration, damage_per_second):
        super().__init__(target, duration, "burning")
        self.damage_per_second = damage_per_second

    def update(self, dt):
        super().update(dt)
        if self.is_active:
            self.target.take_damage(self.damage_per_second * dt, damage_type="fire")
            # print(f"{self.target.name} is burning, taking {self.damage_per_second * dt:.2f} fire damage.")