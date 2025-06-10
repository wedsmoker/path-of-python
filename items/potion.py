from items.item import Item

class HealthPotion(Item):
    """Represents a health potion item in the game."""

    def __init__(self, name, description, level_requirement=1, price=5):
        super().__init__(name, description, "consumable", level_requirement, price)

    def use(self, target):
        """Heals the target for a certain amount."""
        heal_amount = 20  # Example heal amount
        target.heal(heal_amount)
        return f"{self.name} healed {target.name} for {heal_amount} health."

    def __str__(self):
        return f"{self.name} (Potion)"