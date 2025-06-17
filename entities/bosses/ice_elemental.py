from entities.bosses.base_boss import BaseBoss

class IceElemental(BaseBoss):
    def __init__(self, game, x, y):
        # Load data from boss_config.json for Ice Elemental
        boss_data = game.boss_system_manager.boss_config["bosses"]["ice_elemental"]
        super().__init__(
            game=game,
            x=x,
            y=y,
            name=boss_data["name"],
            health=boss_data["stats"]["health"],
            damage=boss_data["stats"]["damage"],
            speed=boss_data["stats"]["speed"],
            sprite_path=boss_data["sprite"],
            # Add other boss-specific parameters from config if needed
            attack_range=200, # Example ranged attack range
            attack_cooldown=1000, # Example ranged attack cooldown
            projectile_sprite_path="graphics/UNUSED/spells/components/ice.png", # Using an existing projectile sprite from UNUSED
            ranged_attack_pattern="burst" # Example attack pattern
        )
        print(f"{self.name} initialized.")

    def update(self, dt, player, tile_map, tile_size):
        super().update(dt, player, tile_map, tile_size)
        # Add Ice Elemental specific update logic here

    # Implement Ice Elemental's unique attack patterns and behaviors
    def _perform_ranged_attack(self, target):
        super()._perform_ranged_attack(target)
        # Add Ice Elemental specific ranged attack logic

    def freeze_aoe(self):
        # Implement freeze area-of-effect logic
        print(f"{self.name} casts Freeze AoE!")
        pass # Placeholder

    # Add other unique methods