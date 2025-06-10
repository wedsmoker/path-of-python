from items.item import Item

class Gem(Item):
    """Represents a gem item in the game."""

    def __init__(self, name, description, gem_type, effect, effect_value, level_requirement=1, price=10):
        super().__init__(name, description, "gem", level_requirement, price)
        self.gem_type = gem_type  # e.g., "ruby", "sapphire", "emerald"
        self.effect = effect  # e.g., "fire_damage", "cold_resistance", "health_regen"
        self.effect_value = effect_value

    def get_effect(self):
        """Returns the effect of this gem."""
        return self.effect, self.effect_value

    def __str__(self):
        return f"{self.name} (Gem: {self.gem_type}, Effect: {self.effect} +{self.effect_value})"