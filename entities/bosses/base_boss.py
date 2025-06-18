import pygame
from entities.enemy import Enemy
import random
import math

class BaseBoss(Enemy):
    def __init__(self, game, x, y, name, health, damage, speed, sprite_path, attack_range=0, attack_cooldown=0, projectile_sprite_path=None, ranged_attack_pattern="single", level=1, xp_value=0):
        super().__init__(game, x, y, name, health, damage, speed, sprite_path, attack_range, attack_cooldown, projectile_sprite_path, ranged_attack_pattern, level, xp_value)
        # Add any base boss specific attributes here
        print(f"BaseBoss {self.name} initialized.")

        # Movement variables
        self.base_speed = speed  # Store the base speed
        self.jump_force = -500  # Upward force for jumping
        self.gravity = 20  # Gravity to pull the enemy down
        self.vertical_velocity = 0  # Initial vertical velocity
        self.is_jumping = False  # Flag to check if the enemy is currently jumping
        self.jump_interval = 3000  # Time between jumps in milliseconds
        self.last_jump_time = pygame.time.get_ticks()
        self.movement_direction = pygame.math.Vector2(1, 0)  # Initial movement direction

        # Dash ability
        self.dash_speed = 800  # Speed of the dash
        self.dash_duration = 0.2  # Duration of the dash in seconds
        self.is_dashing = False
        self.dash_start_time = 0
        self.dash_direction = pygame.math.Vector2(0, 0)

        # Charge ability
        self.charge_speed = 600
        self.is_charging = False
        self.charge_duration = 1  # Charge for 1 second
        self.charge_start_time = 0

        # Patterned movement
        self.movement_pattern = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Example pattern (right, left, down, up)
        self.zigzag_amplitude = 100 # How far the boss moves perpendicular to its main direction
        self.zigzag_frequency = 0.05 # How often the boss changes its perpendicular direction
        self.zigzag_time = 0 # To track the sine wave for zigzag movement
        self.pattern_index = 0
        self.pattern_duration = 2  # Follow pattern for 2 seconds
        self.pattern_start_time = 0
        self.is_following_pattern = False
        self.is_teleporting = False # Corrected initialization
        self.is_zigzagging = False # Corrected initialization

        # Variable Jitter
        self.jitter_intensity = 0.2
        self.jitter_change_interval = 1000  # Change jitter every 1 second
        self.last_jitter_change = pygame.time.get_ticks()

        # Ranged attack attributes
        self.attack_range = attack_range # Distance within which enemy can perform ranged attack
        self.attack_cooldown = attack_cooldown # Time in milliseconds between ranged attacks
        self.last_attack_time = pygame.time.get_ticks() # Last time a ranged attack was performed
        self.projectile_sprite_path = projectile_sprite_path
        # self.ranged_attack_pattern = ranged_attack_pattern # e.g., "single", "spread", "burst" - now dynamic
        self.available_attack_patterns = ["single", "spread", "burst", "circle", "spiral", "rotating_burst", "wave"] # New: list of patterns
        self.current_attack_pattern = random.choice(self.available_attack_patterns) # New: current pattern
        self._is_bursting = False
        self._burst_projectiles_fired = 0
        self._last_burst_shot_time = 0
        self.burst_projectile_count = 3 # Number of projectiles in a burst
        self.burst_delay = 100 # Delay between projectiles in a burst (ms)

    def update(self, dt, player, tile_map, tile_size):
        # Base boss update logic (can call super().update() or override completely)
        super().update(dt, player, tile_map, tile_size)

        if not player:
            return

        current_time = pygame.time.get_ticks()

        # Update Jitter Intensity
        if current_time - self.last_jitter_change > self.jitter_change_interval:
            self.jitter_intensity = random.uniform(0.1, 0.5)  # Vary jitter intensity
            self.last_jitter_change = current_time

        # Jumping logic
        if current_time - self.last_jump_time > self.jump_interval and not self.is_jumping:
            self.vertical_velocity = self.jump_force
            self.is_jumping = True
            self.last_jump_time = current_time

        # Apply gravity
        self.vertical_velocity += self.gravity * dt
        # Cap vertical velocity to prevent excessive falling speed
        self.vertical_velocity = min(self.vertical_velocity, 1000)

        # Ability triggers (randomly choose an ability)
        if not self.is_dashing and not self.is_charging and not self.is_following_pattern and not self.is_teleporting and not self.is_zigzagging:
            ability_choice = random.randint(0, 5)  # 0: Dash, 1: Charge, 2: Pattern, 3: Ranged Attack, 4: Teleport, 5: ZigZag
            if ability_choice == 0:
                self.start_dash()
            elif ability_choice == 1:
                self.start_charge(player)
            elif ability_choice == 2:
                self.start_pattern()
            elif ability_choice == 3:
                self._perform_ranged_attack(player)
            elif ability_choice == 4:
                self.start_teleport(tile_map, tile_size)
            elif ability_choice == 5:
                self.start_zigzag()

        # Dash ability update
        if self.is_dashing:
            if current_time - self.dash_start_time <= self.dash_duration * 1000:
                move_x = self.dash_direction.x * self.dash_speed * dt
                move_y = self.dash_direction.y * self.dash_speed * dt
                self.rect.x += move_x
                self.rect.y += move_y
                if self._check_collision(tile_map, tile_size):
                    self.rect.x -= move_x  # Revert movement
                    self.rect.y -= move_y
                    self.is_dashing = False
            else:
                self.is_dashing = False

        # Charge ability update
        elif self.is_charging:
            if current_time - self.charge_start_time <= self.charge_duration * 1000:
                dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    dx, dy = dx / dist, dy / dist
                move_x = dx * self.charge_speed * dt
                move_y = dy * self.charge_speed * dt
                self.rect.x += move_x
                self.rect.y += move_y
                if self._check_collision(tile_map, tile_size):
                    self.rect.x -= move_x  # Revert movement
                    self.rect.y -= move_y
                    self.is_charging = False
            else:
                self.is_charging = False

        # Patterned movement update
        elif self.is_following_pattern:
            if current_time - self.pattern_start_time <= self.pattern_duration * 1000:
                direction = self.movement_pattern[self.pattern_index]
                move_x = direction[0] * self.base_speed * dt
                move_y = direction[1] * self.base_speed * dt
                self.rect.x += move_x
                self.rect.y += move_y
                if self._check_collision(tile_map, tile_size):
                    self.rect.x -= move_x  # Revert movement
                    self.rect.y -= move_y
                    self.pattern_index = (self.pattern_index + 1) % len(self.movement_pattern)  # Next pattern
                else:
                    self.pattern_index = (self.pattern_index + 1) % len(self.movement_pattern)  # Next pattern
            else:
                self.is_following_pattern = False

        # Zigzag movement update
        elif self.is_zigzagging:
            self._perform_zigzag_movement(dt, player)
            # Zigzag movement continues until a new ability is chosen, or it hits a wall
            if self._check_collision(tile_map, tile_size):
                self.is_zigzagging = False # Stop zigzagging if collision

        # Default movement (if not dashing, charging, following pattern, or zigzagging)
        else:
            # Calculate potential movement
            dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 0:
                dx, dy = dx / dist, dy / dist
            else: # If boss is on top of player, don't move
                dx, dy = 0, 0

            # Jittering effect
            jitter_x = random.uniform(-self.jitter_intensity, self.jitter_intensity)
            jitter_y = random.uniform(-self.jitter_intensity, self.jitter_intensity)
            dx += jitter_x
            dy += jitter_y

            # Normalize the movement vector after adding jitter
            move_vector = pygame.math.Vector2(dx, dy)
            if move_vector.length_squared() > 0: # Only normalize if length is not zero
                move_vector.normalize_ip()
            else:
                move_vector = pygame.math.Vector2(0,0) # Keep as zero vector if it was zero

            move_x = move_vector.x * self.base_speed * dt
            move_y = move_vector.y * self.base_speed * dt

            # Apply vertical movement (jumping/falling)
            move_y += self.vertical_velocity * dt

            # Store original position for collision rollback
            original_x, original_y = self.rect.x, self.rect.y

            # Attempt to move horizontally
            self.rect.x += move_x
            collision = self._check_collision(tile_map, tile_size)
            if collision:
                self.rect.x = original_x  # Rollback if collision
                move_x *= -1  # Reverse horizontal direction for bouncing
                # If collision, try moving vertically instead
                self.rect.y += move_y
                if self._check_collision(tile_map, tile_size):
                    self.rect.y = original_y # Rollback vertical movement as well
                    # If both horizontal and vertical movements are blocked, try diagonal movements
                    # Try top-left
                    self.rect.x -= move_x
                    self.rect.y -= move_y
                    if self._check_collision(tile_map, tile_size):
                        self.rect.x = original_x
                        self.rect.y = original_y
                    else:
                        # Top-left movement was successful
                        pass
                else:
                    # Vertical movement was successful
                    pass
            else:
                # Horizontal movement was successful, continue
                pass

            # Attempt to move vertically
            self.rect.y += move_y
            collision = self._check_collision(tile_map, tile_size)
            if collision:
                self.rect.y = original_y  # Rollback if collision
                self.vertical_velocity = 0  # Stop vertical movement
                self.is_jumping = False  # Reset jumping flag
                # If collision, try moving horizontally instead
                self.rect.x += move_x
                if self._check_collision(tile_map, tile_size):
                    self.rect.x = original_x # Rollback horizontal movement as well
                    # If both horizontal and vertical movements are blocked, try diagonal movements
                    # Try bottom-right
                    self.rect.x += move_x
                    self.rect.y += move_y
                    if self._check_collision(tile_map, tile_size):
                        self.rect.x = original_x
                        self.rect.y = original_y
                    else:
                        # Bottom-right movement was successful
                        pass
                else:
                    # Horizontal movement was successful
                    pass
            else:
                # Vertical movement was successful, continue
                pass

        # Store current position for next update
        self.last_x = self.rect.x
        self.last_y = self.rect.y

        # Handle burst attack sequence
        if self._is_bursting:
            if self._burst_projectiles_fired < self.burst_projectile_count:
                if current_time - self._last_burst_shot_time > self.burst_delay:
                    # Target the player during burst, or potentially the nearest skeleton if implemented
                    self._shoot_projectile(player.rect.centerx, player.rect.centery)
                    self._burst_projectiles_fired += 1
                    self._last_burst_shot_time = current_time
            else:
                self._is_bursting = False
                self.last_attack_time = current_time # Reset main cooldown after burst finishes

        # Add any base boss specific update logic here

    def start_dash(self):
        """Initiates the dash ability."""
        self.is_dashing = True
        self.dash_start_time = pygame.time.get_ticks()
        self.dash_direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

    def start_charge(self, player):
        """Initiates the charge ability."""
        self.is_charging = True
        self.charge_start_time = pygame.time.get_ticks()

    def start_pattern(self):
        """Initiates the patterned movement."""
        self.is_following_pattern = True
        self.pattern_start_time = pygame.time.get_ticks()
        self.pattern_index = 0

    def start_teleport(self, tile_map, tile_size):
        """Initiates the teleport ability."""
        self.is_teleporting = True
        self._perform_teleport(tile_map, tile_size)
        self.is_teleporting = False # Teleport is instant, so reset flag immediately

    def start_zigzag(self):
        """Initiates the zigzag movement."""
        self.is_zigzagging = True
        self.zigzag_time = 0 # Reset zigzag time

    def _perform_teleport(self, tile_map, tile_size):
        """Teleports the boss to a random valid location on the map."""
        # Find a random valid tile to teleport to
        valid_positions = []
        for row_idx, row in enumerate(tile_map):
            for col_idx, tile_id in enumerate(row):
                # Assuming 0 is an empty/walkable tile
                if tile_id == 0:
                    valid_positions.append((col_idx * tile_size, row_idx * tile_size))

        if valid_positions:
            new_x, new_y = random.choice(valid_positions)
            self.rect.x = new_x
            self.rect.y = new_y
            print(f"Boss teleported to ({new_x}, {new_y})")
        else:
            print("No valid teleport positions found.")

    def _perform_zigzag_movement(self, dt, player):
        """Moves the boss in a zigzag pattern towards the player."""
        # Calculate direction towards player
        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            main_direction = pygame.math.Vector2(dx / dist, dy / dist)
        else:
            main_direction = pygame.math.Vector2(0, 0) # If boss is on top of player, no main direction

        # Calculate perpendicular direction for zigzag
        perp_direction = pygame.math.Vector2(-main_direction.y, main_direction.x)

        # Apply sine wave to perpendicular movement
        self.zigzag_time += dt
        zigzag_offset = math.sin(self.zigzag_time * self.zigzag_frequency) * self.zigzag_amplitude

        # Combine main direction with zigzag offset
        move_vector = main_direction * self.base_speed + perp_direction * zigzag_offset
        if move_vector.length_squared() > 0: # Only normalize if length is not zero
            move_vector.normalize_ip()
        else:
            move_vector = pygame.math.Vector2(0,0) # Keep as zero vector if it was zero

        move_x = move_vector.x * self.base_speed * dt
        move_y = move_vector.y * self.base_speed * dt

        self.rect.x += move_x
        self.rect.y += move_y

    def _perform_ranged_attack(self, target): # Modified to accept target
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            if self.projectile_sprite_path:
                # Dynamically choose an attack pattern
                self.current_attack_pattern = random.choice(self.available_attack_patterns) # Choose a new pattern
                
                if self.current_attack_pattern == "single":
                    self._shoot_projectile(target.rect.centerx, target.rect.centery)
                    self.last_attack_time = current_time
                elif self.current_attack_pattern == "spread":
                    self._shoot_spread_projectiles(target.rect.centerx, target.rect.centery, num_projectiles=3, angle_spread=30)
                    self.last_attack_time = current_time
                elif self.current_attack_pattern == "burst":
                    self._is_bursting = True
                    self._burst_projectiles_fired = 0
                    self._last_burst_shot_time = current_time # Start burst timer
                    # The actual shooting will happen in the update method
                elif self.current_attack_pattern == "circle":
                    self._shoot_circle_projectiles(num_projectiles=8, radius=50)
                    self.last_attack_time = current_time
                elif self.current_attack_pattern == "spiral":
                    self._shoot_spiral_projectiles(num_projectiles=15, angle_increment_degrees=20, radius_increment=10)
                    self.last_attack_time = current_time
                elif self.current_attack_pattern == "rotating_burst":
                    self._shoot_rotating_burst_projectiles(num_projectiles=5, rotation_speed=5)
                    self.last_attack_time = current_time
                elif self.current_attack_pattern == "wave":
                    self._shoot_wave_projectiles(num_projectiles=10, wave_amplitude=50, wave_frequency=0.1)
                    self.last_attack_time = current_time
                # Add more patterns here

    def _shoot_projectile(self, target_x, target_y):
        from entities.projectile import Projectile
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

    def _shoot_rotating_burst_projectiles(self, num_projectiles, rotation_speed):
        """Shoots projectiles in a burst that rotates over time."""
        center_x, center_y = self.rect.centerx, self.rect.centery
        # Calculate initial angle towards the player
        initial_angle = math.atan2(self.game.player.rect.centery - center_y, self.game.player.rect.centerx - center_x)

        for i in range(num_projectiles):
            # Calculate angle for each projectile, adding a rotation component
            angle = initial_angle + math.radians(rotation_speed * i)
            target_x = center_x + math.cos(angle) * 1000 # Shoot far away
            target_y = center_y + math.sin(angle) * 1000
            self._shoot_projectile(target_x, target_y)

    def _shoot_wave_projectiles(self, num_projectiles, wave_amplitude, wave_frequency):
        """Shoots projectiles in a wave-like pattern."""
        center_x, center_y = self.rect.centerx, self.rect.centery
        # Calculate initial angle towards the player
        initial_angle = math.atan2(self.game.player.rect.centery - center_y, self.game.player.rect.centerx - center_x)

        for i in range(num_projectiles):
            # Calculate an offset based on a sine wave
            offset_angle = wave_amplitude * math.sin(wave_frequency * i)
            angle = initial_angle + math.radians(offset_angle)
            target_x = center_x + math.cos(angle) * 1000
            target_y = center_y + math.sin(angle) * 1000
            self._shoot_projectile(target_x, target_y)
    # Add any base boss specific methods here (e.g., phase transitions, unique abilities)