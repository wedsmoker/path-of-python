import pygame
import math
import random
from config.constants import TILE_SIZE

class CycloneSkill:
    def __init__(self, player):
        self.player = player
        self.game = player.game
        self.id = "cyclone"
        self.name = "Cyclone"
        self.description = "Spins rapidly, hitting all enemies in a circle repeatedly while draining mana."
        self.mana_cost = 10 # Initial cost from data/skills.json
        self.base_damage = {"min": 10, "max": 20, "type": "physical"} # From data/skills.json
        self.cooldown = 0 # From data/skills.json
        self.channel_cost_per_second = self.player.max_mana * 0.20 # 20% of max mana per second (updated from 0.05)
        self.hit_interval = 0.05 # From data/skills.json (seconds) - Decreased for faster hits
        self.last_hit_time = 0
        self.is_channeling = False
        self.radius = TILE_SIZE * 3.375 # Area of effect for Cyclone, increased by 1.5x (2.25 * 1.5 = 3.375)

        # Visual effect attributes
        self.cyclone_effect_sprites = pygame.sprite.Group() # Use a sprite group for multiple sprites
        self.rotation_angle = 0
        self.rotation_speed = 1080 # degrees per second (720 * 1.5 = 1080)
        self.num_orbiting_weapons = 3 # Number of weapons orbiting

        # Load default weapon graphic
        self.default_weapon_image = pygame.image.load("graphics/UNUSED/weapons/ancient_sword.png").convert_alpha()
        self.default_weapon_image = pygame.transform.scale(self.default_weapon_image, (TILE_SIZE, TILE_SIZE)) # Scale to tile size
        self.default_weapon_image.set_alpha(180) # Slightly transparent

    def can_cast(self):
        if self.player.current_mana < self.mana_cost:
            print("Not enough mana for Cyclone!")
            return False
        return True

    def activate(self):
        if not self.can_cast():
            return
        print(f"CycloneSkill.activate() called. is_channeling set to True.")
        self.is_channeling = True
        self.last_hit_time = pygame.time.get_ticks()
        print(f"Player activated Cyclone! Mana remaining: {self.player.current_mana}")

        # Create and add multiple continuous visual effect sprites
        if not self.cyclone_effect_sprites: # Only create if group is empty
            for i in range(self.num_orbiting_weapons):
                effect_sprite = pygame.sprite.Sprite()
                effect_sprite.image = self.default_weapon_image
                effect_sprite.rect = effect_sprite.image.get_rect(center=self.player.rect.center)
                effect_sprite.initial_angle_offset = (360 / self.num_orbiting_weapons) * i # Distribute evenly
                self.cyclone_effect_sprites.add(effect_sprite)
                self.game.current_scene.effects.add(effect_sprite)

    def deactivate(self):
        self.is_channeling = False
        print("Cyclone deactivated.")
        # Remove all continuous visual effect sprites
        for sprite in self.cyclone_effect_sprites:
            self.game.current_scene.effects.remove(sprite)
        self.cyclone_effect_sprites.empty() # Clear the group

    def update(self, dt):
        if not self.is_channeling:
            print("Cyclone update: Not channeling, returning.")
            return

        current_time = pygame.time.get_ticks()

        # Drain mana over time
        mana_drain_amount = self.channel_cost_per_second * dt
        self.player.current_mana -= mana_drain_amount
        print(f"Cyclone update: Draining {mana_drain_amount:.2f} mana. Current mana: {self.player.current_mana:.2f}")

        if self.player.current_mana <= 0:
            self.player.current_mana = 0
            self.deactivate()
            print("Cyclone stopped: Out of mana.")
            return

        # Hit enemies at intervals
        if current_time - self.last_hit_time >= self.hit_interval * 1000:
            print(f"Cyclone update: Time for hit. Last hit: {self.last_hit_time}, Current time: {current_time}")
            self.last_hit_time = current_time
            self._perform_hit()

        # Update visual effect position and rotation for each sprite
        self.rotation_angle = (self.rotation_angle + self.rotation_speed * dt) % 360
        
        for sprite in self.cyclone_effect_sprites:
            # Calculate orbiting position with individual offset
            current_orbit_angle = self.rotation_angle + sprite.initial_angle_offset
            offset_x = self.radius * math.cos(math.radians(current_orbit_angle))
            offset_y = self.radius * math.sin(math.radians(current_orbit_angle))
            
            sprite.rect = sprite.image.get_rect(center=(self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y))


    def _perform_hit(self):
        print("Cyclone _perform_hit() called.")
        hit_enemies = set()
        player_center = self.player.rect.center
        print(f"Player center: {player_center}")
        for enemy in self.game.current_scene.enemies:
            enemy_center = enemy.rect.center
            distance = math.hypot(player_center[0] - enemy_center[0], player_center[1] - enemy_center[1])
            print(f"Checking enemy {enemy.name} at {enemy_center}. Distance: {distance:.2f}, Radius: {self.radius:.2f}")
            if distance <= self.radius:
                hit_enemies.add(enemy)
        
        if not hit_enemies:
            print("Cyclone _perform_hit(): No enemies in range.")

        for enemy in hit_enemies:
            damage_amount = random.randint(self.base_damage["min"], self.base_damage["max"])
            enemy.take_damage(damage_amount)
            print(f"Cyclone hit {enemy.name} for {damage_amount} {self.base_damage['type']} damage!")

        # Removed the old visual effect placeholder