class CharacterClass:
    """Base class for all character classes."""

    def __init__(self, name, description, starting_attributes, unique_bonus, specialization):
        self.name = name
        self.description = description
        self.starting_attributes = starting_attributes  # Dictionary of attribute names and values
        self.unique_bonus = unique_bonus  # Unique bonus description
        self.specialization = specialization  # Specialization description

    def get_starting_attributes(self):
        """Return the starting attributes for this class."""
        return self.starting_attributes

    def get_unique_bonus(self):
        """Return the unique bonus for this class."""
        return self.unique_bonus

    def get_specialization(self):
        """Return the specialization for this class."""
        return self.specialization

class Warrior(CharacterClass):
    """The Warrior class, focused on melee combat."""

    def __init__(self):
        starting_attributes = {
            "strength": 15,
            "dexterity": 10,
            "intelligence": 5,
            "vitality": 15,
            "energy": 10
        }
        unique_bonus = "Warriors deal 10% more damage with melee weapons."
        specialization = "Warriors excel in close combat, with increased health and melee damage."

        super().__init__("Warrior", "A formidable melee fighter", starting_attributes, unique_bonus, specialization)

class Ranger(CharacterClass):
    """The Ranger class, focused on ranged combat."""

    def __init__(self):
        starting_attributes = {
            "strength": 10,
            "dexterity": 15,
            "intelligence": 10,
            "vitality": 10,
            "energy": 15
        }
        unique_bonus = "Rangers deal 10% more damage with ranged weapons."
        specialization = "Rangers are skilled archers, with increased ranged damage and accuracy."

        super().__init__("Ranger", "A skilled archer", starting_attributes, unique_bonus, specialization)

class Mage(CharacterClass):
    """The Mage class, focused on magical abilities."""

    def __init__(self):
        starting_attributes = {
            "strength": 5,
            "dexterity": 10,
            "intelligence": 15,
            "vitality": 10,
            "energy": 15
        }
        unique_bonus = "Mages deal 10% more damage with spells."
        specialization = "Mages wield powerful magic, with increased spell damage and mana."

        super().__init__("Mage", "A powerful spellcaster", starting_attributes, unique_bonus, specialization)

# Add more classes as needed