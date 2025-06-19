import random
import pygame
import os
import math
import json
from config.constants import TILE_SIZE
from entities.projectile import Projectile
from entities.enemy import Enemy

class FireballSkill:
    def __init__(self, player):
        self.player = player
        self.projectile_sprite_path = "graphics/spells/fire/fireball.png" # Corrected path
        self.explosion_sprite_path = "graphics/effect/cloud_fire0.png" # Placeholder, actual animation needed
        self.burning_ground_sprite_path = "graphics/effect/cloud_fire1.png" # Placeholder
        self.mana_cost = 8
        self.base_damage = {"min": 10, "max": 15, "type": "fire"}
        self.cooldown = 0
        self.cast_time = 0.5
        self.explosion_radius = 75
        self.burning_ground_duration = 5.0
        self.burning_ground_damage = {"min": 3, "max": 5, "type": "fire"}
        self.burning_ground_tick_interval = 1.0
        self.burning_ground_chance_to_ignite = 0.75
        self.last_used = 0

        self._load_skill_data()

    def _load_skill_data(self):
        """Loads Fireball skill data from skills.json."""
        skills_file_path = os.path.join(os.getcwd(), "data", "skills.json")
        try:
            with open(skills_file_path, 'r') as f:
                skills_data = json.load(f)
            
            fireball_data = None
            for skill in skills_data.get("active_skills", []):
                if skill.get("id") == "fireball":
                    fireball_data = skill
                    break
            
            if fireball_data:
                self.mana_cost = fireball_data.get("mana_cost", 8)
                self.base_damage = fireball_data.get("base_damage", {"min": 10, "max": 15, "type": "fire"})
                self.cooldown = fireball_data.get("cooldown", 0) * 1000 # Convert to milliseconds
                self.cast_time = fireball_data.get("cast_time", 0.5)
                self.explosion_radius = fireball_data.get("explosion_radius", 75)
                self.burning_ground_duration = fireball_data.get("burning_ground_duration", 5.0)
                self.burning_ground_damage = fireball_data.get("burning_ground_damage", {"min": 3, "max": 5, "type": "fire"})
                self.burning_ground_tick_interval = fireball_data.get("burning_ground_tick_interval", 1.0)
                self.burning_ground_chance_to_ignite = fireball_data.get("burning_ground_chance_to_ignite", 0.75)
                print(f"Fireball skill data loaded: mana_cost={self.mana_cost}, base_damage={self.base_damage}, cooldown={self.cooldown}")
            else:
                print("Fireball skill data not found in skills.json. Using default values.")
        except FileNotFoundError:
            print(f"Error: skills.json not found at {skills_file_path}. Using default Fireball skill values.")
        except json.JSONDecodeError:
            print(f"Error decoding skills.json at {skills_file_path}. Using default Fireball skill values.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    def can_cast(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_used < self.cooldown:
            return False, "Skill is on cooldown!"
        if not self.player.has_skill("fireball"):
            return False, "Skill not unlocked!"
        if self.player.current_mana < self.mana_cost:
            return False, "Not enough mana!"
        return True, ""

    def activate(self, target_x, target_y):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_used < self.cooldown:
            print("Fireball skill is on cooldown!")
            return

        if not self.player.has_skill("fireball"):
            print("Cannot activate Fireball skill: Skill not unlocked!")
            return

        if self.player.current_mana < self.mana_cost:
            print("Cannot activate Fireball skill: Not enough mana!")
            return

        self.player.current_mana -= self.mana_cost
        self.last_used = current_time

        print(f"FireballSkill.activate: Player pos=({self.player.rect.centerx}, {self.player.rect.centery}), Target pos=({target_x}, {target_y})")

        # Calculate initial spawn position slightly offset from player to avoid immediate self-collision
        offset_distance = 50 # Pixels to offset from player's center
        
        # Calculate direction vector from player to target
        player_center_x = self.player.rect.centerx
        player_center_y = self.player.rect.centery
        
        dx = target_x - player_center_x
        dy = target_y - player_center_y
        
        magnitude = math.hypot(dx, dy)
        
        if magnitude > 0:
            unit_dx = dx / magnitude
            unit_dy = dy / magnitude
        else: # Target is exactly on player, default to facing direction or a small forward offset
            unit_dx = 0
            unit_dy = -1 # Default to facing upwards if no target direction (can be improved with player facing direction)

        spawn_x = player_center_x + unit_dx * offset_distance
        spawn_y = player_center_y + unit_dy * offset_distance

        # Create a fireball projectile
        fireball_projectile = FireballProjectile(
            self.player.game,
            spawn_x, # Use calculated spawn_x
            spawn_y, # Use calculated spawn_y
            target_x,
            target_y,
            speed=500, # Adjust projectile speed as needed
            damage=random.randint(self.base_damage["min"], self.base_damage["max"]),
            sprite_path=self.projectile_sprite_path,
            explosion_radius=self.explosion_radius,
            burning_ground_duration=self.burning_ground_duration,
            burning_ground_damage=self.burning_ground_damage,
            burning_ground_tick_interval=self.burning_ground_tick_interval,
            burning_ground_chance_to_ignite=self.burning_ground_chance_to_ignite,
            explosion_sprite_path=self.explosion_sprite_path,
            burning_ground_sprite_path=self.burning_ground_sprite_path
        )
        self.player.game.current_scene.projectiles.add(fireball_projectile)
        print("Fireball launched!")

    def update(self, dt):
        """Updates the Fireball skill's state, primarily handling cooldowns."""
        # No specific continuous effects for Fireball, but cooldown needs to be managed.
        pass # Placeholder for now, can add more complex logic later if needed

class FireballProjectile(Projectile):
    def __init__(self, game, x, y, target_x, target_y, speed, damage, sprite_path,
                 explosion_radius, burning_ground_duration, burning_ground_damage,
                 burning_ground_tick_interval, burning_ground_chance_to_ignite,
                 explosion_sprite_path, burning_ground_sprite_path):
        super().__init__(game, x, y, target_x, target_y, speed, damage, sprite_path)
        self.explosion_radius = explosion_radius
        self.burning_ground_duration = burning_ground_duration
        self.burning_ground_damage = burning_ground_damage
        self.burning_ground_tick_interval = burning_ground_tick_interval
        self.burning_ground_chance_to_ignite = burning_ground_chance_to_ignite
        self.explosion_sprite_path = explosion_sprite_path
        self.burning_ground_sprite_path = burning_ground_sprite_path
        self.exploded = False # Flag to ensure explosion effect is triggered only once
        print(f"FireballProjectile __init__ completed. Initial pos=({self.rect.centerx}, {self.rect.centery}), Target=({self.target_x}, {self.target_y}), dx={self.dx:.2f}, dy={self.dy:.2f}")


    def update(self, dt, player, tile_map, tile_size):
        # Move the projectile
        self.rect.x += self.dx * self.speed * dt
        self.rect.y += self.dy * self.speed * dt

        # print(f"FireballProjectile update: Current pos=({self.rect.centerx}, {self.rect.centery}), dt={dt:.4f}") # Debug print

        # Check for collision with enemies first
        collided_enemies = pygame.sprite.spritecollide(self, self.game.current_scene.enemies, False)
        if collided_enemies:
            for enemy in collided_enemies:
                # Ensure the enemy is not friendly (e.g., a player minion)
                if not hasattr(enemy, 'is_friendly') or not enemy.is_friendly:
                    enemy.take_damage(self.damage)
            # Trigger explosion and burning ground on enemy hit
            if not self.exploded: # Ensure it's only triggered once
                self._trigger_explosion_and_burning_ground(self.rect.centerx, self.rect.centery)
                self.exploded = True
            self.kill() # Remove projectile on hit
            return # Exit update after handling collision and killing self

        # Check for collision with solid tiles (walls)
        if self._check_collision(tile_map, tile_size):
            if not self.exploded: # Ensure it's only triggered once
                self._trigger_explosion_and_burning_ground(self.rect.centerx, self.rect.centery)
                self.exploded = True
            self.kill() # Remove projectile on wall hit
            return # Exit update after handling collision and killing self

        # Remove projectile after a certain lifetime
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            if not self.exploded: # Ensure it's only triggered once
                self._trigger_explosion_and_burning_ground(self.rect.centerx, self.rect.centery)
                self.exploded = True
            self.kill()
            return # Exit update after handling collision and killing self

    def _trigger_explosion_and_burning_ground(self, x, y):
        """Triggers an explosion and creates burning ground at the given location."""
        print(f"Explosion at {x}, {y} with radius {self.explosion_radius}")
        # Create explosion effect (animation)
        explosion = ExplosionEffect(self.game, x, y, self.explosion_sprite_path, scale=2)
        self.game.current_scene.projectiles.add(explosion)

        # Create burning ground
        burning_ground = BurningGround(
            self.game, x, y, self.explosion_radius, self.burning_ground_duration,
            self.burning_ground_damage, self.burning_ground_tick_interval,
            self.burning_ground_chance_to_ignite, self.burning_ground_sprite_path
        )
        self.game.current_scene.projectiles.add(burning_ground)

        # Apply explosion damage to enemies within radius
        for enemy in self.game.current_scene.enemies:
            distance = math.hypot(enemy.rect.centerx - x, enemy.rect.centery - y)
            if distance <= self.explosion_radius:
                # Ensure the enemy is not friendly (e.g., a player minion)
                if not hasattr(enemy, 'is_friendly') or not enemy.is_friendly:
                    enemy.take_damage(self.damage) # Apply full damage for simplicity, can add falloff

class ExplosionEffect(pygame.sprite.Sprite):
    def __init__(self, game, x, y, image_path, scale=1):
        super().__init__()
        self.game = game
        self.original_image = pygame.image.load(os.path.join(os.getcwd(), image_path)).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (int(self.original_image.get_width() * scale), int(self.original_image.get_height() * scale)))
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 255
        self.fade_speed = 500 # Adjust for faster/slower fade
        self.duration = 500 # How long the explosion stays visible
        self.start_time = pygame.time.get_ticks()

    def update(self, dt, player=None, tile_map=None, tile_size=None, nearest_skeleton=None):
        time_elapsed = pygame.time.get_ticks() - self.start_time
        if time_elapsed > self.duration:
            self.alpha -= self.fade_speed * dt
            if self.alpha <= 0:
                self.kill()
        self.image.set_alpha(self.alpha)

    def draw(self, screen, camera_x, camera_y, zoom_level):
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * zoom_level), int(self.rect.height * zoom_level)))
        scaled_image.set_alpha(self.alpha) # Apply alpha to the scaled image
        screen_x = (self.rect.x - camera_x) * zoom_level
        screen_y = (self.rect.y - camera_y) * zoom_level
        screen.blit(scaled_image, (screen_x, screen_y))

class BurningGround(pygame.sprite.Sprite):
    def __init__(self, game, x, y, radius, duration, damage_range, tick_interval, chance_to_ignite, sprite_path):
        super().__init__()
        self.game = game
        self.radius = radius
        self.duration = duration * 1000 # Convert to milliseconds
        self.damage_range = damage_range
        self.tick_interval = tick_interval * 1000 # Convert to milliseconds
        self.chance_to_ignite = chance_to_ignite
        self.start_time = pygame.time.get_ticks()
        self.last_tick_time = self.start_time
        self.center_x = x
        self.center_y = y

        self.original_image = pygame.image.load(os.path.join(os.getcwd(), sprite_path)).convert_alpha()
        # Scale image to match radius
        scaled_width = int(self.radius * 2)
        scaled_height = int(self.radius * 2)
        self.image = pygame.transform.scale(self.original_image, (scaled_width, scaled_height))
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 200 # Semi-transparent

    def update(self, dt, player=None, tile_map=None, tile_size=None, nearest_skeleton=None):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill() # Remove burning ground after duration

        if current_time - self.last_tick_time > self.tick_interval:
            self._apply_burning_effect()
            self.last_tick_time = current_time

    def _apply_burning_effect(self):
        """Applies burning damage and ignite chance to enemies within the radius."""
        for enemy in self.game.current_scene.enemies:
            distance = math.hypot(enemy.rect.centerx - self.center_x, enemy.rect.centery - self.center_y)
            if distance <= self.radius:
                # Ensure the enemy is not friendly (e.g., a player minion)
                if not hasattr(enemy, 'is_friendly') or not enemy.is_friendly:
                    damage = random.randint(self.damage_range["min"], self.damage_range["max"])
                    enemy.take_damage(damage)
                    if random.random() < self.chance_to_ignite:
                        enemy.apply_ignite(self.duration / 1000) # Ignite for the duration of burning ground (convert ms back to seconds)

    def draw(self, screen, camera_x, camera_y, zoom_level):
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * zoom_level), int(self.rect.height * zoom_level)))
        scaled_image.set_alpha(self.alpha)
        screen_x = (self.rect.x - camera_x) * zoom_level
        screen_y = (self.rect.y - camera_y) * zoom_level
        screen.blit(scaled_image, (screen_x, screen_y))