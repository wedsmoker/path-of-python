import pygame
from entities.effects import Effect

class StatusEffect:
    """Base class for all status effects."""

    def __init__(self, duration, intensity):
        self.duration = duration  # Duration in seconds
        self.intensity = intensity  # Intensity of the effect
        self.timer = 0  # Timer to track effect duration

    def apply(self, target):
        """Apply the effect to the target."""
        pass

    def update(self, dt):
        """Update the effect's duration."""
        self.timer += dt
        if self.timer >= self.duration:
            return True  # Effect has ended
        return False

    def get_damage(self):
        """Calculate damage per second from this effect."""
        return 0

class Burn(StatusEffect):
    """Burn effect that deals fire damage over time."""

    def __init__(self, duration, intensity):
        super().__init__(duration, intensity)

    def apply(self, target):
        target.add_effect(Effect("burn", self.intensity))

    def get_damage(self):
        return self.intensity * 2  # 2 damage per second per intensity

class Chill(StatusEffect):
    """Chill effect that slows movement."""

    def __init__(self, duration, intensity):
        super().__init__(duration, intensity)

    def apply(self, target):
        target.add_effect(Effect("chill", self.intensity))

    def get_damage(self):
        return 0  # Chill doesn't deal direct damage

class Freeze(StatusEffect):
    """Freeze effect that temporarily stuns the target."""

    def __init__(self, duration, intensity):
        super().__init__(duration, intensity)

    def apply(self, target):
        target.add_effect(Effect("freeze", self.intensity))

    def get_damage(self):
        return 0  # Freeze doesn't deal direct damage

class Shock(StatusEffect):
    """Shock effect that deals lightning damage over time."""

    def __init__(self, duration, intensity):
        super().__init__(duration, intensity)

    def apply(self, target):
        target.add_effect(Effect("shock", self.intensity))

    def get_damage(self):
        return self.intensity * 3  # 3 damage per second per intensity

class Poison(StatusEffect):
    """Poison effect that deals nature damage over time."""

    def __init__(self, duration, intensity):
        super().__init__(duration, intensity)

    def apply(self, target):
        target.add_effect(Effect("poison", self.intensity))

    def get_damage(self):
        return self.intensity * 1.5  # 1.5 damage per second per intensity

class Bleed(StatusEffect):
    """Bleed effect that deals physical damage over time."""

    def __init__(self, duration, intensity):
        super().__init__(duration, intensity)

    def apply(self, target):
        target.add_effect(Effect("bleed", self.intensity))

    def get_damage(self):
        return self.intensity  # 1 damage per second per intensity