import pygame
import random
import json
from core.scene_manager import BaseScene
from core.utils import load_image, calculate_distance, direction_to_target, load_zone_data
from entities.enemy import Enemy
from entities.projectile import Projectile
from combat.damage_calc import DamageCalculator
from config.constants import (
    TILE_SIZE, ENEMY_SPAWN_DISTANCE, ENEMY_DESPAWN_DISTANCE,
    ENEMY_SPAWN_COOLDOWN, PROJECTILE_SPEED, PROJECTILE_LIFETIME,
    PROJECTILE_DESPAWN_DISTANCE
)
from core.base_gameplay_scene import BaseGameplayScene

class GameplayScene(BaseGameplayScene):
    def __init__(self, game):
        super().__init__(game)
        self.player = game.spawn_town.player
        self.tile_map = None # Initialize tile_map to prevent AttributeError
        self.enemies = pygame.sprite.Group() # Changed from list to pygame.sprite.Group
        self.damage_calculator = DamageCalculator()
        self.last_enemy_spawn_time = 0
        self.enemy_spawn_cooldown = ENEMY_SPAWN_COOLDOWN
        self.tile_size = TILE_SIZE
        zone_data = load_zone_data()
        self.effects = pygame.sprite.Group() # Add effects group
        if zone_data:
            self.tilemap_path = zone_data.get("tilemap_path")
            self.music_path = zone_data.get("music_path")
            self.allowed_enemies = zone_data.get("allowed_enemies")
        else:
            self.allowed_enemies = []
            self.tilemap_path = None
        self.load_tilemap()

    def load_tilemap(self):
        try:
            self.tilemap_image = load_image(self.tilemap_path)
            self.tile_map = self.tilemap_image # Assign to tile_map for BaseGameplayScene
            self.tilemap_rect = self.tilemap_image.get_rect()
            print(f"Tilemap loaded successfully from: {self.tilemap_path}")
        except FileNotFoundError:
            print(f"ERROR: Tilemap image not found at: {self.tilemap_path}")
            self.tilemap_image = None
        except Exception as e:
            print(f"ERROR loading tilemap: {e}")
            self.tilemap_image = None

    def handle_event(self, event):
        super().handle_event(event)

    def update(self, dt):
        super().update(dt)
        current_time = pygame.time.get_ticks()

        # Enemy Spawning Logic
        if current_time - self.last_enemy_spawn_time > self.enemy_spawn_cooldown:
            if len(self.enemies) < 5:  # Limit the number of enemies
                self.spawn_enemy()
                self.last_enemy_spawn_time = current_time

        # Update Enemies
        for enemy in self.enemies.copy():  # Iterate over a copy for safe removal
            enemy.update(dt, self.player)
            if calculate_distance(self.player.rect.center, enemy.rect.center) > ENEMY_DESPAWN_DISTANCE:
                self.enemies.remove(enemy)
                print("Enemy despawned (too far).")

        # Update Projectiles
        for projectile in self.projectiles.copy(): # Iterate over a copy for safe removal
            projectile.update(dt)
            if projectile.lifetime > PROJECTILE_LIFETIME or \
               calculate_distance(projectile.start_pos, projectile.rect.center) > PROJECTILE_DESPAWN_DISTANCE:
                self.projectiles.remove(projectile)
                print("Projectile despawned (lifetime or distance exceeded).")

            # Projectile-Enemy Collision
            for enemy in self.enemies.copy(): # Iterate over a copy for safe removal
                if projectile.rect.colliderect(enemy.rect):
                    projectile.hit(enemy)
                    self.damage_calculator.apply_damage(enemy, self.player, projectile.damage)
                    self.projectiles.remove(projectile)
                    print("Projectile hit enemy!")
                    break  # Only hit one enemy per projectile

        # Check for enemy deaths and remove them
        for enemy in self.enemies.copy(): # Iterate over a copy for safe removal
            if enemy.current_life <= 0:
                self.enemies.remove(enemy)
                print("Enemy died!")

    def draw(self, screen):
        if self.tilemap_image:
            screen.blit(self.tilemap_image, (0, 0))  # Draw the entire tilemap at (0, 0)
        else:
            screen.fill((0, 0, 0))  # Fallback to black screen if no tilemap

        super().draw(screen)

        # Draw Enemies
        for enemy in self.enemies:
            enemy.draw(screen)

        # Draw Projectiles
        for projectile in self.projectiles:
            screen.blit(projectile.image, (projectile.rect.x - self.camera_x, projectile.rect.y - self.camera_y))

    def spawn_enemy(self):
        """Spawns a new enemy at a random location within a certain distance of the player."""
        if not self.allowed_enemies:
            print("No allowed enemies defined for this zone.")
            return

        enemy_type = random.choice(self.allowed_enemies)
        angle = random.uniform(0, 2 * pygame.pi)  # Random angle in radians
        x = self.player.rect.centerx + ENEMY_SPAWN_DISTANCE * pygame.Vector2(1, 0).rotate_rad(angle).x
        y = self.player.rect.centery + ENEMY_SPAWN_DISTANCE * pygame.Vector2(1, 0).rotate_rad(angle).y

        # Create an instance of the chosen enemy type
        new_enemy = Enemy(self.game, x, y, {"name": enemy_type, "health": 50, "damage": 5, "speed": 50, "sprite_path": None}) # Updated Enemy constructor
        self.enemies.add(new_enemy) # Changed from append to add
        print(f"Spawned a {enemy_type}!")