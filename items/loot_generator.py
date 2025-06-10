import random
from items.weapon import Weapon
from items.armor import Armor
from items.gem import Gem

class LootGenerator:
    """Generates loot drops for enemies and containers."""

    def __init__(self):
        # Define possible loot tables (can be loaded from JSON later)
        self.weapon_types = ["sword", "axe", "bow", "staff"]
        self.armor_types = ["helmet", "chestplate", "boots", "gloves"]
        self.gem_types = ["ruby", "sapphire", "emerald", "diamond"]
        self.effects = ["fire_damage", "cold_resistance", "health_regen", "mana_regen"]

    def generate_loot(self, enemy_level):
        """Generates a list of items based on the enemy's level."""
        loot = []
        num_items = random.randint(0, 2)  # 0-2 items per drop

        for _ in range(num_items):
            item_type = random.choice(["weapon", "armor", "gem"])

            if item_type == "weapon":
                weapon = self.generate_weapon(enemy_level)
                loot.append(weapon)
            elif item_type == "armor":
                armor = self.generate_armor(enemy_level)
                loot.append(armor)
            elif item_type == "gem":
                gem = self.generate_gem(enemy_level)
                loot.append(gem)

        return loot

    def generate_weapon(self, item_level):
        """Generates a weapon based on the item level."""
        name = f"{random.choice(self.weapon_types).capitalize()} of Power"
        description = f"A powerful weapon for level {item_level} adventurers."
        weapon_type = random.choice(self.weapon_types)
        damage = random.randint(item_level * 2, item_level * 4)
        weapon = Weapon(name, description, weapon_type, damage, level_requirement=item_level)
        # Randomly populate gem slots
        for i in range(len(weapon.gem_slots)):
            if random.random() < 0.5:  # 50% chance to have a gem
                weapon.gem_slots[i] = self.generate_gem(item_level)
        return weapon

    def generate_armor(self, item_level):
        """Generates an armor piece based on the item level."""
        name = f"{random.choice(self.armor_types).capitalize()} of Protection"
        description = f"A protective armor piece for level {item_level} adventurers."
        armor_type = random.choice(self.armor_types)
        armor_value = random.randint(item_level, item_level * 2)
        return Armor(name, description, armor_type, armor_value, level_requirement=item_level)

    def generate_gem(self, item_level):
        """Generates a gem based on the item level."""
        name = f"{random.choice(self.gem_types).capitalize()} of Enhancement"
        description = f"A gem that enhances your abilities for level {item_level} adventurers."
        gem_type = random.choice(self.gem_types)
        effect = random.choice(self.effects)
        # effect_value = random.randint(item_level, item_level * 3) # Remove effect_value since Gem class doesn't have it
        return Gem(name, description, effect) # Remove effect_value since Gem class doesn't have it