class Gem:
    """Represents a gem item in the game."""

    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect

    def get_effect(self):
        """Returns the effect of this gem."""
        return self.effect

    def __str__(self):
        return f"{self.name} (Gem: {self.description}, Effect: {self.effect})"