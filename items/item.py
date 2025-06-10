class Item:
    """Represents a base item in the game."""

    def __init__(self, name, description, item_type, level_requirement=1, price=10):
        self.name = name
        self.description = description
        self.item_type = item_type  # e.g., "weapon", "armor", "consumable", "quest_item"
        self.level_requirement = level_requirement
        self.price = price

    def __str__(self):
        return f"{self.name} ({self.item_type.capitalize()})"

    def get_description(self):
        """Returns the item's description."""
        return self.description

    def get_level_requirement(self):
        """Returns the level requirement for this item."""
        return self.level_requirement

    def get_price(self):
        """Returns the price of this item."""
        return self.price