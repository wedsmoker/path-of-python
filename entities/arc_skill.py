import pygame
import math
import os
import random
from config.constants import TILE_SIZE
from entities.projectile import Projectile

class ArcSkill:
    def __init__(self, player):
        self.player = player
        self.arc_chain_lightning_image = self.load_arc_image("graphics/spells/air/chain_lightning.png")
        self.max_chain_length = 5  # Increased max chain length
        self.chain_range = 250  # Increased chain range
        self.arc_speed = 300  # Increased arc speed
        self.cooldown = 1000  # Cooldown in milliseconds
        self.last_used = 0
        self.base_damage = 15
        self.damage_variation = 5
        self.stun_chance = 0.15
        self.chain_reaction_chance = 0.05
        self.mana_cost = 10
        self.particle_life = 500
        self.particle_speed = 50
        self.arc_width = TILE_SIZE // 2

    def load_arc_image(self, path):
        """Loads and scales the arc image."""
        try:
            image = pygame.image.load(os.path.join(os.getcwd(), path)).convert_alpha()
            return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        except FileNotFoundError:
            print(f"Error: Arc image file not found: {path}")
            return None

    def activate(self):
        """Activates the Arc skill, creating a projectile that chains to strike multiple enemies."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_used < self.cooldown:
            print("Arc skill is on cooldown!")
            return

        if not self.player.has_skill("arc"):
            print("Cannot activate Arc skill: Skill not unlocked!")
            return

        if self.player.current_mana < self.mana_cost:
            print("Cannot activate Arc skill: Not enough mana!")
            return

        # Deduct mana cost
        self.player.current_mana -= self.mana_cost
        self.last_used = current_time

        # Start the chain from the player
        start_x, start_y = self.player.rect.center

        # Find the nearest enemy
        target_enemy = self.find_nearest_enemy(start_x, start_y)

        if not target_enemy:
            return

        # Create arc projectile
        end_x, end_y = target_enemy.rect.center
        damage = self.calculate_damage()
        arc_projectile = ArcProjectile(start_x, start_y, end_x, end_y, self.arc_speed, damage, (255, 255, 0), self, image=self.arc_chain_lightning_image)  # Yellow color
        self.player.game.current_scene.projectiles.add(arc_projectile)

    def calculate_damage(self):
        """Calculates damage with variation and player level scaling."""
        level_bonus = self.player.level * 2
        damage = self.base_damage + random.randint(-self.damage_variation, self.damage_variation) + level_bonus
        return damage

    def find_nearest_enemy(self, x, y):
        """Finds the nearest enemy within a certain range."""
        nearest_enemy = None
        min_distance = float('inf')

        for sprite in self.player.game.current_scene.enemies:
            enemy = sprite
            distance = math.hypot(enemy.rect.centerx - x, enemy.rect.centery - y)
            if distance < min_distance and distance < self.chain_range:
                min_distance = distance
                nearest_enemy = enemy

        return nearest_enemy

class ArcProjectile(Projectile):
    def __init__(self, x, y, target_x, target_y, speed, damage, color, arc_skill, image, radius=5):
        super().__init__(x, y, target_x, target_y, speed, damage, color, image=image, radius=radius)
        self.arc_skill = arc_skill

    def hit(self, target):
        super().hit(target)
        # Chain to the next enemy
        if random.random() < self.arc_skill.chain_reaction_chance:
            self.arc_skill.trigger_chain_reaction(target)

    def trigger_chain_reaction(self, target):
        """Triggers a chain reaction that damages nearby enemies."""
        print("Chain reaction triggered!")
        # Implement chain reaction effect here