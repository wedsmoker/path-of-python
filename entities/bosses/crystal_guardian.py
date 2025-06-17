from entities.bosses.base_boss import BaseBoss

class CrystalGuardian(BaseBoss):
    def __init__(self, game, x, y, **kwargs):
        # Load data from boss_config.json for Crystal Guardian
        boss_data = game.boss_system_manager.boss_config["bosses"]["crystal_guardian"]
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
            attack_range=250, # Example ranged attack range
            attack_cooldown=800, # Example ranged attack cooldown
            projectile_sprite_path="graphics/UNUSED/spells/components/ice_spear.png", # Using an existing projectile sprite from UNUSED
            ranged_attack_pattern="circle", # Example attack pattern
            **kwargs
        )
        print(f"{self.name} initialized.")

    def update(self, dt, player, tile_map, tile_size):
        super().update(dt, player, tile_map, tile_size)
        # Add Crystal Guardian specific update logic here

    # Implement Crystal Guardian's unique attack patterns and behaviors
    def _perform_ranged_attack(self, target):
        super()._perform_ranged_attack(target)
        # Add Crystal Guardian specific ranged attack logic

    def crystal_shard(self):
        # Implement crystal shard attack logic
        print(f"{self.name} fires crystal shards!")
        pass # Placeholder

    def energy_beam(self):
        # Implement energy beam attack logic
        print(f"{self.name} fires an energy beam!")
        pass # Placeholder

    # Add other unique methods