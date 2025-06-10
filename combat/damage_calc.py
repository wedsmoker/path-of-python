class DamageCalculator:
    """Handles all damage calculations in the game."""

    @staticmethod
    def calculate_damage(attacker, defender, base_damage, damage_type):
        """
        Calculate the total damage dealt to the defender.

        Args:
            attacker: The entity dealing damage
            defender: The entity receiving damage
            base_damage: The base damage value before modifiers
            damage_type: The type of damage (e.g., 'physical', 'fire', 'cold', etc.)

        Returns:
            The total damage dealt to the defender
        """
        # 1. Calculate base damage with weapon modifiers
        weapon_modifier = attacker.get_weapon_damage_modifier(damage_type)
        total_damage = base_damage * weapon_modifier

        # 2. Apply skill modifiers
        skill_modifier = attacker.get_active_skill_modifier(damage_type)
        total_damage *= skill_modifier

        # 3. Apply armor reduction
        armor_reduction = defender.get_armor_reduction(damage_type)
        total_damage *= (1 - armor_reduction)

        # 4. Apply resistances
        resistance = defender.get_resistance(damage_type)
        total_damage *= (1 - resistance)

        # 5. Apply status effects
        status_effect_damage = 0
        for effect in defender.status_effects:
            if effect.get_damage() > 0:
                status_effect_damage += effect.get_damage()

        # 6. Calculate critical hit chance and damage
        is_critical = attacker.is_critical_hit()
        if is_critical:
            total_damage *= attacker.get_critical_damage_multiplier()

        # 7. Apply damage over time effects
        total_damage += status_effect_damage

        # Ensure damage is not negative
        total_damage = max(0, total_damage)

        return total_damage

    @staticmethod
    def calculate_healing(base_healing, healing_type):
        """
        Calculate the total healing amount.

        Args:
            base_healing: The base healing value before modifiers
            healing_type: The type of healing (e.g., 'life', 'mana', etc.)

        Returns:
            The total healing amount
        """
        # 1. Apply healing modifiers
        # (This would be based on the entity's attributes, skills, etc.)
        healing_modifier = 1.0  # Placeholder - would be calculated based on entity's stats

        # 2. Calculate total healing
        total_healing = base_healing * healing_modifier

        return total_healing