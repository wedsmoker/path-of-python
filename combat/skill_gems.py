from combat.skills import Skill, AttackSkill, SpellSkill

class SkillGem:
    def __init__(self, name, gem_type, skill_instance=None, support_effect=None):
        self.name = name
        self.gem_type = gem_type # "active" or "support"
        self.skill_instance = skill_instance # An instance of Skill, AttackSkill, or SpellSkill
        self.support_effect = support_effect # A function or object that modifies a skill

    def __str__(self):
        return f"{self.name} ({self.gem_type.capitalize()} Gem)"

class SupportEffect:
    def __init__(self, name, description, modifiers):
        self.name = name
        self.description = description
        self.modifiers = modifiers # Dictionary of modifiers, e.g., {"damage_percent": 0.20, "mana_cost_percent": 0.50}

    def apply_to_skill(self, skill):
        """Applies this support effect's modifiers to a given skill."""
        # This is a simplified example. In a real game, this would be more complex
        # and might involve modifying skill attributes directly or adding callbacks.
        if "damage_percent" in self.modifiers and hasattr(skill, 'base_damage'):
            # Assuming base_damage is a dict with 'min' and 'max'
            if isinstance(skill.base_damage, dict):
                skill.base_damage["min"] *= (1 + self.modifiers["damage_percent"])
                skill.base_damage["max"] *= (1 + self.modifiers["damage_percent"])
            else: # If base_damage is a single number
                skill.base_damage *= (1 + self.modifiers["damage_percent"])
            print(f"Applied {self.name} to {skill.name}: Damage increased by {self.modifiers['damage_percent']*100:.0f}%")

        if "mana_cost_percent" in self.modifiers:
            skill.mana_cost *= (1 + self.modifiers["mana_cost_percent"])
            print(f"Applied {self.name} to {skill.name}: Mana cost increased by {self.modifiers['mana_cost_percent']*100:.0f}%")

# Example Support Gems
# faster_casting = SkillGem("Faster Casting", "support", support_effect=SupportEffect("Faster Casting", "Increases cast speed", {"cast_speed_percent": 0.20}))
# added_fire_damage = SkillGem("Added Fire Damage", "support", support_effect=SupportEffect("Added Fire Damage", "Adds fire damage to attacks", {"damage_type": "fire", "flat_damage": 5}))