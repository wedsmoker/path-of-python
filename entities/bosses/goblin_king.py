from entities.bosses.base_boss import BaseBoss

class GoblinKing(BaseBoss):
    def __init__(self, game, x, y):
        # Load data from boss_config.json for Goblin King
        boss_data = game.boss_system_manager.boss_config["bosses"]["goblin_king"]
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
            attack_range=150, # Example ranged attack range
            attack_cooldown=1500, # Example ranged attack cooldown
            projectile_sprite_path="graphics/spells/components/ice_spear.png", # Using an existing projectile sprite
            ranged_attack_pattern="spread" # Example attack pattern
        )
        print(f"{self.name} initialized.")

    def update(self, dt, player, tile_map, tile_size):
        super().update(dt, player, tile_map, tile_size)
        # Add Goblin King specific update logic here (e.g., trigger specific attack patterns)
        # Example: Check health thresholds for phase changes

    # Implement Goblin King's unique attack patterns and behaviors
    def _perform_ranged_attack(self, target):
        # Override or extend base class ranged attack if needed
        super()._perform_ranged_attack(target)
        # Add Goblin King specific ranged attack logic

    def summon_minions(self):
        # Implement summoning logic
        print(f"{self.name} summons minions!")
        pass # Placeholder

    # Add other unique methods for Goblin King's abilities