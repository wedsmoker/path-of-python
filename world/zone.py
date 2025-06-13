import pygame
import random
import json
import os # Added import os
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
        self.enemy_data = self._load_enemy_data("data/enemy_data.json") # Load enemy data

    def _load_enemy_data(self, json_path):
        """Loads enemy data from a JSON file."""
        try:
            full_path = os.path.join(os.getcwd(), json_path)
            with open(full_path, "r") as f:
                data = json.load(f)
            return data # Directly return the loaded data, as it's already a dictionary of enemies
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading enemy data from {json_path}: {e}")
            return {}

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
            enemy.update(dt, self.player, self.tile_map, self.tile_size) # Pass tile_map and tile_size
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
            enemy.draw(screen, self.camera_x, self.camera_y, self.zoom_level) # Pass camera and zoom

        # Draw Projectiles
        for projectile in self.projectiles:
            screen.blit(projectile.image, (projectile.rect.x - self.camera_x, projectile.rect.y - self.camera_y))

    def spawn_enemy(self):
        """Spawns a new enemy at a random location within a certain distance of the player."""
        if not self.allowed_enemies:
            print("No allowed enemies defined for this zone.")
            return
        if not self.enemy_data:
            print("Enemy data not loaded. Cannot spawn enemies.")
            return

        enemy_id = random.choice(self.allowed_enemies)
        enemy_info = self.enemy_data.get(enemy_id)
        print(f"Enemy info for '{enemy_id}': {enemy_info}") # Debug print

        if not enemy_info:
            print(f"Enemy data for '{enemy_id}' not found.")
            return

        angle = random.uniform(0, 2 * pygame.pi)  # Random angle in radians
        x = self.player.rect.centerx + ENEMY_SPAWN_DISTANCE * pygame.Vector2(1, 0).rotate_rad(angle).x
        y = self.player.centery + ENEMY_SPAWN_DISTANCE * pygame.Vector2(1, 0).rotate_rad(angle).y

        new_enemy = Enemy(
            self.game,
            x, y,
            name=enemy_info.get("name", "Unknown Enemy"),
            health=enemy_info.get("health", 1), # Directly access health
            damage=enemy_info.get("damage", 1), # Directly access damage
            speed=enemy_info.get("speed", 50), # Directly access speed
            sprite_path=enemy_info.get("sprite_path"), # Use the sprite_path from JSON
            attack_range=enemy_info.get("attack_range", 0),
            attack_cooldown=enemy_info.get("attack_cooldown", 1000),
            projectile_sprite_path=enemy_info.get("projectile_sprite_path"),
            ranged_attack_pattern=enemy_info.get("ranged_attack_pattern", "single"),
            level=enemy_info.get("level", 1),
            xp_value=enemy_info.get("xp_value", 0)
        )
        self.enemies.add(new_enemy)
        print(f"Spawned a {enemy_info.get('name')} (Level {new_enemy.level}, XP {new_enemy.xp_value})!")