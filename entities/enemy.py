import pygame
import os
import math
from config.constants import TILE_SIZE
from entities.projectile import Projectile
from ui.damage_text import DamageText

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y, name, health, damage, speed, sprite_path, attack_range=0, attack_cooldown=0, projectile_sprite_path=None, ranged_attack_pattern="single", level=1, xp_value=0):
        super().__init__()
        self.game = game
        self.name = name # Initialize the name attribute
        self.image = self._load_sprite(sprite_path)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.level = level
        self.xp_value = xp_value
        self.health = health
        self.damage = damage # This will be melee damage
        self.speed = speed
        self.sprite_path = sprite_path
        self.current_life = health # Initialize current_life
        self.damage_texts = pygame.sprite.Group() # Group to hold damage text pop-ups

        self.attack_range = attack_range # Distance within which enemy can perform ranged attack
        self.attack_cooldown = attack_cooldown # Time in milliseconds between ranged attacks
        self.last_attack_time = pygame.time.get_ticks() # Last time a ranged attack was performed
        self.projectile_sprite_path = projectile_sprite_path
        self.ranged_attack_pattern = ranged_attack_pattern # e.g., "single", "spread", "burst"
        self._is_bursting = False
        self._burst_projectiles_fired = 0
        self._last_burst_shot_time = 0
        self.burst_projectile_count = 3 # Number of projectiles in a burst
        self.burst_delay = 100 # Delay between projectiles in a burst (ms)

        # Melee attack attributes
        self.melee_range = TILE_SIZE * 1.2 # Melee range, slightly larger than a tile
        self.melee_cooldown = 1000 # 1 second cooldown for melee attacks
        self.last_melee_attack_time = pygame.time.get_ticks()

        print(f"Enemy initialized at ({x}, {y}) with sprite: {sprite_path}") # Debug print

    def _load_sprite(self, sprite_path):
        """Loads the enemy sprite, with error handling."""
        full_path = os.path.join(os.getcwd(), sprite_path)
        try:
            if not os.path.exists(full_path):
                print(f"Error: Enemy sprite file not found: {full_path}")
                # Return a placeholder surface if the image is not found
                placeholder = pygame.Surface((TILE_SIZE, TILE_SIZE))
                placeholder.fill((255, 0, 255))  # Magenta color for missing texture
                return placeholder
            image = pygame.image.load(full_path).convert_alpha()
            scaled_image = pygame.transform.scale(image, (int(TILE_SIZE), int(TILE_SIZE))) # Ensure TILE_SIZE is int
            if scaled_image.get_size() == (0, 0):
                print(f"Warning: Scaled image for {full_path} has zero dimensions. Returning placeholder.")
                placeholder = pygame.Surface((TILE_SIZE, TILE_SIZE))
                placeholder.fill((255, 0, 255))  # Magenta color for missing texture
                return placeholder
            return scaled_image
        except pygame.error as e:
            print(f"Error loading enemy sprite {full_path}: {e}")
            # Return a placeholder surface if loading fails
            placeholder = pygame.Surface((TILE_SIZE, TILE_SIZE))
            placeholder.fill((255, 0, 255))  # Magenta color for missing texture
            return placeholder

    def take_damage(self, amount):
        self.current_life -= amount
        # Create and add damage text
        damage_text = DamageText(str(int(amount)), self.rect.centerx, self.rect.top, (255, 0, 0))
        self.damage_texts.add(damage_text)
        if self.current_life <= 0:
            self.kill()  # Remove the enemy from all sprite groups
            print(f"DEBUG: Enemy {self.name} died. Its xp_value is: {self.xp_value}. Player current XP: {self.game.player.experience}")
            print(f"Enemy {self.name} died. Awarding {self.xp_value} XP to player.") # Debug print
            self.game.player.gain_experience(self.xp_value) # Pass xp_value instead of level

    def _perform_ranged_attack(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            if self.projectile_sprite_path:
                if self.ranged_attack_pattern == "single":
                    self._shoot_projectile(player.rect.centerx, player.rect.centery)
                    self.last_attack_time = current_time
                elif self.ranged_attack_pattern == "spread":
                    self._shoot_spread_projectiles(player.rect.centerx, player.rect.centery, num_projectiles=3, angle_spread=30)
                    self.last_attack_time = current_time
                elif self.ranged_attack_pattern == "burst":
                    self._is_bursting = True
                    self._burst_projectiles_fired = 0
                    self._last_burst_shot_time = current_time # Start burst timer
                    # The actual shooting will happen in the update method
                elif self.ranged_attack_pattern == "circle":
                    self._shoot_circle_projectiles(num_projectiles=8, radius=50)
                    self.last_attack_time = current_time
                elif self.ranged_attack_pattern == "spiral":
                    self._shoot_spiral_projectiles(num_projectiles=15, angle_increment_degrees=20, radius_increment=10)
                    self.last_attack_time = current_time
                # Add more patterns here

            # self.last_attack_time = current_time # Moved inside pattern specific blocks for burst

    def _shoot_projectile(self, target_x, target_y):
        projectile = Projectile(self.game, self.rect.centerx, self.rect.centery,
                                target_x, target_y, 200, self.damage, self.projectile_sprite_path)
        self.game.current_scene.projectiles.add(projectile) # Add to scene's projectile group

    def _shoot_spread_projectiles(self, target_x, target_y, num_projectiles, angle_spread):
        # Calculate initial angle to target
        angle_to_target = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)

        # Calculate angle increment for spread
        start_angle = angle_to_target - math.radians(angle_spread / 2)
        angle_increment = math.radians(angle_spread / (num_projectiles - 1)) if num_projectiles > 1 else 0

        for i in range(num_projectiles):
            current_angle = start_angle + i * angle_increment
            # Calculate a point far away in the direction of the current angle
            # This ensures the projectile travels in the correct direction
            proj_target_x = self.rect.centerx + math.cos(current_angle) * 1000
            proj_target_y = self.rect.centery + math.sin(current_angle) * 1000
            self._shoot_projectile(proj_target_x, proj_target_y)

    def _shoot_circle_projectiles(self, num_projectiles, radius=50):
        """Shoots projectiles in a circle around the enemy."""
        center_x, center_y = self.rect.centerx, self.rect.centery
        for i in range(num_projectiles):
            angle = (2 * math.pi / num_projectiles) * i
            target_x = center_x + math.cos(angle) * radius
            target_y = center_y + math.sin(angle) * radius
            self._shoot_projectile(target_x, target_y)

    def _shoot_spiral_projectiles(self, num_projectiles, angle_increment_degrees=20, radius_increment=10):
        """Shoots projectiles in a spiral pattern."""
        center_x, center_y = self.rect.centerx, self.rect.centery
        base_angle = math.atan2(self.game.player.rect.centery - center_y, self.game.player.rect.centerx - center_x)

        for i in range(num_projectiles):
            angle = base_angle + math.radians(angle_increment_degrees * i)
            current_radius = 50 + (radius_increment * i) # Start with a base radius and increase

            target_x = center_x + math.cos(angle) * current_radius
            target_y = center_y + math.sin(angle) * current_radius
            self._shoot_projectile(target_x, target_y)
    # _shoot_burst_projectiles is no longer needed as burst logic is handled in update
    # def _shoot_burst_projectiles(self, target_x, target_y, num_projectiles, delay):
    #     for _ in range(num_projectiles):
    #         self._shoot_projectile(target_x, target_y)

    def update(self, dt, player, tile_map, tile_size, nearest_skeleton=None):
        # Debug print to check if update is called for any enemy
        # print(f"Enemy {self.name} update called.")

        if not player:
            return

        current_time = pygame.time.get_ticks()

        # Handle burst attack sequence
        if self._is_bursting:
            if self._burst_projectiles_fired < self.burst_projectile_count:
                if current_time - self._last_burst_shot_time > self.burst_delay:
                    self._shoot_projectile(player.rect.centerx, player.rect.centery)
                    self._burst_projectiles_fired += 1
                    self._last_burst_shot_time = current_time
            else:
                self._is_bursting = False
                self.last_attack_time = current_time # Reset main cooldown after burst finishes

        # Update damage texts
        self.damage_texts.update(dt)

        # Calculate distance to player or nearest skeleton
        target = nearest_skeleton if nearest_skeleton else player
        dx, dy = target.rect.centerx - self.rect.centerx, target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # Melee attack logic
        if dist <= self.melee_range and current_time - self.last_melee_attack_time > self.melee_cooldown:
            target.take_damage(self.damage)
            self.last_melee_attack_time = current_time
            # Debug prints for ranged attack
            if self.attack_range > 0:
                print(f"Enemy {self.name} - Dist: {dist:.2f}, Attack Range: {self.attack_range}, Cooldown: {self.attack_cooldown}, Time since last attack: {current_time - self.last_attack_time}")
            # print(f"Enemy performed melee attack on player for {self.damage} damage.") # Debug print

        # Ranged attack logic (only if not in melee range or if ranged attack is preferred)
        # Prioritize ranged attack if within range and off cooldown, otherwise move or melee
        # Only trigger new ranged attack if not currently bursting
        if not self._is_bursting and self.attack_range > 0 and dist <= self.attack_range and current_time - self.last_attack_time > self.attack_cooldown:
            self._perform_ranged_attack(player)
        elif dist > self.melee_range: # Only move if not in melee range
            # Simple AI: Move towards the player if not in attack range or no ranged attack
            if dist > 0:
                # Normalize direction vector
                dx, dy = dx / dist, dy / dist

                # Calculate potential movement
                move_x = dx * self.speed * dt
                move_y = dy * self.speed * dt

                # Store original position for collision rollback
                original_x, original_y = self.rect.x, self.rect.y

                # Attempt to move horizontally
                self.rect.x += move_x
                if self._check_collision(tile_map, tile_size):
                    self.rect.x = original_x  # Rollback if collision

                # Attempt to move vertically
                self.rect.y += move_y
                if self._check_collision(tile_map, tile_size):
                    self.rect.y = original_y  # Rollback if collision

        # print(f"Enemy at ({self.rect.x}, {self.rect.y}) updated. Player at ({player.rect.centerx}, {player.rect.centery}).") # Debug print

    def _check_collision(self, tile_map, tile_size):
        """Checks for collision with solid tiles."""
        # Get the tile coordinates the enemy is currently occupying
        enemy_left_tile = int(self.rect.left / tile_size)
        enemy_right_tile = int(self.rect.right / tile_size)
        enemy_top_tile = int(self.rect.top / tile_size)
        enemy_bottom_tile = int(self.rect.bottom / tile_size)

        # Clamp tile coordinates to map boundaries
        map_width_tiles = len(tile_map[0])
        map_height_tiles = len(tile_map)

        enemy_left_tile = max(0, min(enemy_left_tile, map_width_tiles - 1))
        enemy_right_tile = max(0, min(enemy_right_tile, map_width_tiles - 1))
        enemy_top_tile = max(0, min(enemy_top_tile, map_height_tiles - 1))
        enemy_bottom_tile = max(0, min(enemy_bottom_tile, map_height_tiles - 1))

        # Iterate over the tiles the enemy overlaps with
        for y in range(enemy_top_tile, enemy_bottom_tile + 1):
            for x in range(enemy_left_tile, enemy_right_tile + 1):
                if 0 <= y < map_height_tiles and 0 <= x < map_width_tiles:
                    tile_type = tile_map[y][x]
                    # Assuming 'wall' is a solid tile type. Add other solid types as needed.
                    if tile_type == 'wall':
                        # print(f"Enemy collision with wall at tile ({x}, {y})") # Debug print
                        return True
        return False

    def draw(self, screen, camera_x, camera_y, zoom_level):
        # Calculate the enemy's position on the screen relative to the camera and zoom
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * zoom_level), int(self.rect.height * zoom_level)))
        screen_x = (self.rect.x - camera_x) * zoom_level
        screen_y = (self.rect.y - camera_y) * zoom_level
        screen.blit(scaled_image, (screen_x, screen_y))
        # print(f"Enemy drawn at screen position ({screen_x}, {screen_y})") # Debug print

        # Draw damage texts
        for text_sprite in self.damage_texts:
            text_sprite.draw(screen, camera_x, camera_y, zoom_level)