from items.item import Item

class Armor(Item):
    """Represents an armor item in the game."""

    def __init__(self, name, description, armor_type, armor_value, level_requirement=1, price=10):
        super().__init__(name, description, "armor", level_requirement, price)
        self.armor_type = armor_type  # e.g., "helmet", "chestplate", "boots", "gloves"
        self.armor_value = armor_value

    def get_armor_value(self):
        """Returns the armor value of this item."""
        return self.armor_value

    def __str__(self):
         return f"{self.name} (Armor: {self.armor_value}, Type: {self.armor_type})"