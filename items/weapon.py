from items.item import Item

class Weapon(Item):
    """Represents a weapon item in the game."""

    def __init__(self, name, description, weapon_type, damage, level_requirement=1, price=10):
        super().__init__(name, description, "weapon", level_requirement, price)
        self.weapon_type = weapon_type  # e.g., "sword", "axe", "bow", "staff"
        self.damage = damage
        self.gem_slots = [None] * 3  # Weapons have 3 gem slots

    def get_damage(self):
        """Returns the damage of this weapon."""
        return self.damage

    def __str__(self):
        return f"{self.name} (Weapon: {self.weapon_type}, Damage: {self.damage})"