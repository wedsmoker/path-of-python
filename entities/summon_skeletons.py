import math
import pygame
import os
import random
import json
from config.constants import TILE_SIZE
from entities.enemy import Enemy

class SummonSkeletons:
    def __init__(self, player):
        self.player = player
        self.skeleton_image_path = "graphics/dc-mon/undead/skeletons/skeleton_humanoid_small.png"
        self.wraith_image_path = "graphics/dc-mon/undead/shadow_wraith.png"  # Path to the wraith image
        self.summon_range = 2 * TILE_SIZE
        # self.max_skeletons = 50  # Maximum number of skeletons
        self.skeleton_health = 30
        self.skeleton_damage = 5
        self.skeleton_speed = 50
        self.last_used = 0
        self.cooldown = 500  # .5 second cooldown
        # self.active_skeletons = [] # Removed: Keep track of active skeletons - now managed by scene's friendly_entities

        # Load skill data from JSON
        self._load_skill_data()

    def _load_skill_data(self):
        """Loads Summon Skeletons skill data from skills.json."""
        skills_file_path = os.path.join(os.getcwd(), "data", "skills.json")
        try:
            with open(skills_file_path, 'r') as f:
                skills_data = json.load(f)

            summon_skeletons_data = None
            for skill in skills_data.get("active_skills", []):
                if skill.get("id") == "summon_skeleton":
                    summon_skeletons_data = skill
                    break

            if summon_skeletons_data:
                self.mana_cost = summon_skeletons_data.get("mana_cost", 20)
                self.cooldown = summon_skeletons_data.get("cooldown", 1) * 1000  # Convert to milliseconds
                self.max_skeletons = summon_skeletons_data.get("max_skeletons", 999)
                self.skeleton_health = summon_skeletons_data.get("skeleton_health", 30)
                self.skeleton_damage = summon_skeletons_data.get("skeleton_damage", 5)
                self.skeleton_speed = summon_skeletons_data.get("skeleton_speed", 50)
                print(f"Summon Skeletons skill data loaded: mana_cost={self.mana_cost}, cooldown={self.cooldown}, max_skeletons={self.max_skeletons}, skeleton_health={self.skeleton_health}, skeleton_damage={self.skeleton_damage}, skeleton_speed={self.skeleton_speed}")
            # else:
                print("Summon Skeletons skill data not found in skills.json. Using default values.")
                self.mana_cost = 20
                self.cooldown = 1000
                self.max_skeletons = 999
                self.skeleton_health = 30
                self.skeleton_damage = 5
                self.skeleton_speed = 50
        except FileNotFoundError:
            print(f"Error: skills.json not found at {skills_file_path}. Using default Summon Skeletons skill values.")
            self.mana_cost = 20
            self.cooldown = 1000
            self.max_skeletons = 999
            self.skeleton_health = 30
            self.skeleton_damage = 5
            self.skeleton_speed = 50
        except json.JSONDecodeError:
            print(f"Error decoding skills.json at {skills_file_path}. Using default Summon Skeletons skill values.")
            self.mana_cost = 20
            self.cooldown = 1000
            self.max_skeletons = 999
            self.skeleton_health = 30
            self.skeleton_damage = 5
            self.skeleton_speed = 50
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def can_cast(self):
        """Checks if the skill can be cast (mana, cooldown, max skeletons)."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_used < self.cooldown:
            return False
        if not self.player.has_skill("summon_skeleton"):
            return False
        if self.player.current_mana < self.mana_cost:
            return False
        # if len(self.player.game.current_scene.friendly_entities) >= self.max_skeletons:
            return False
        return True

    def activate(self, x, y):
        """Activates the Summon Skeletons skill, summoning a random number of skeletons (1-3) to fight for the player."""
        print("SummonSkeletons.activate() called!")  # Add print statement
        current_time = pygame.time.get_ticks()
        if not self.can_cast(): # Use the new can_cast method
            print("Cannot activate Summon Skeletons skill: Conditions not met (cooldown, mana, or max skeletons).")
            return

        # Deduct mana cost
        self.player.current_mana -= self.mana_cost
        self.last_used = current_time

        # Determine a random number of skeletons to summon (between 1 and 3)
        num_to_summon = random.randint(1, 3)
        print(f"Attempting to summon {num_to_summon} skeletons.")
        # Add debug print to show current active skeletons and number to summon
        print(f"DEBUG: Current active skeletons: {len(self.player.game.current_scene.friendly_entities)}, Attempting to summon: {num_to_summon}")


        # Summon the determined number of skeletons, respecting the max limit
        for _ in range(num_to_summon):
            # if len(self.player.game.current_scene.friendly_entities) < self.max_skeletons:
                # Summon skeleton with a small random offset
            offset_x = random.randint(-int(TILE_SIZE * 0.75), int(TILE_SIZE * 0.75)) # Increased offset range
            offset_y = random.randint(-int(TILE_SIZE * 0.75), int(TILE_SIZE * 0.75)) # Increased offset range
            self._summon_skeleton(x + offset_x, y + offset_y)
            # else:
                # print("Maximum skeletons reached during summoning sequence.")
                # break # Stop summoning if max limit is hit

    def _summon_skeleton(self, x, y):
        """Summons a single skeleton at the specified location."""

        # Create a skeleton enemy
        # Calculate scaled stats based on player level
        player_level = self.player.level
        scaled_health = self.skeleton_health + (player_level - 1) * 5  # Example: +5 health per level
        scaled_damage = self.skeleton_damage + (player_level - 1) * 10  # Example: +10 damage per level
        scaled_speed = self.skeleton_speed + (player_level - 2) * 5  # Example: +5 speed per level (start scaling from level 2)
        
        # Ensure stats don't go below base values for level 1
        scaled_health = max(self.skeleton_health, scaled_health)
        scaled_damage = max(self.skeleton_damage, scaled_damage)
        scaled_speed = max(self.skeleton_speed, scaled_speed)

        # Create a skeleton enemy with scaled stats
        skeleton = Skeleton(self.player.game, x, y, scaled_health, scaled_damage, scaled_speed, self.skeleton_image_path, self, player_level=player_level) # Pass self (SummonSkeletons instance) as owner
        # Add skeleton to the scene's friendly_entities group
        self.player.game.current_scene.friendly_entities.add(skeleton)
        self.player.game.current_scene.enemies.add(skeleton)  # Add skeleton to enemies group so they can be targeted
        # self.active_skeletons.append(skeleton) # Removed: now managed by scene's friendly_entities
        print("Summoned a skeleton!")

        #Create wraith effect
        wraith = WraithEffect(self.player.game, x, y, self.wraith_image_path, scale=2)
        self.player.game.current_scene.enemies.add(wraith)


    def remove_skeleton(self, skeleton):
        """Removes a skeleton from the active skeletons list."""
        # Remove skeleton from the scene's friendly_entities group
        if skeleton in self.player.game.current_scene.friendly_entities:
            self.player.game.current_scene.friendly_entities.remove(skeleton)
            print(f"Removed a skeleton from active list. Current active: {len(self.player.game.current_scene.friendly_entities)}")

    def update(self, dt):
        """Updates the SummonSkeletons skill's state, primarily handling cooldowns."""
        pass # Placeholder for now, can add more complex logic later if needed


class Skeleton(Enemy):
    def __init__(self, game, x, y, health, damage, speed, sprite_path, owner, player_level):
        super().__init__(game, x, y, "Skeleton", health, damage, speed, sprite_path)
        self.player_level = player_level
        # Calculate scale factor based on player level
        # Base scale is 1.0 for level 1, increases by 0.1 for every 5 levels
        scale_increment_per_level = 0.50 # Increased to 50%per level
        self.scale_factor = 2.0 + (self.player_level - 1) * scale_increment_per_level # Base scale 2.0 for level 1
        
        # Load and scale the sprite image
        original_image = pygame.image.load(os.path.join(os.getcwd(), sprite_path)).convert_alpha()
        new_width = int(original_image.get_width() * self.scale_factor)
        new_height = int(original_image.get_height() * self.scale_factor)
        self.image = pygame.transform.scale(original_image, (new_width, new_height))
        self.rect = self.image.get_rect(center=(x, y)) # Update rect after scaling
        self.owner = owner  # The SummonSkeletons instance that summoned this skeleton
        self.is_friendly = True  # Skeletons are friendly to the player
        self.faction = "player_minions"  # Set skeleton's faction
        self.attack_range = TILE_SIZE * 1.5 # Melee range
        self.attack_cooldown = 1000 # 1 second cooldown
        self.last_attack_time = pygame.time.get_ticks()
        self.following_range = TILE_SIZE * 20 # Increased following range
        self.enemy_finding_range = TILE_SIZE * 8 # Range to find enemies
        self.circle_angle = random.uniform(0, 2 * math.pi)  # Initial random angle for circling
        self.circle_speed = random.uniform(0.5, 1.5)  # Random speed for circling
        self.circle_radius = random.uniform(TILE_SIZE * 1.5, TILE_SIZE * 2.5)  # Random radius for circling

    def take_damage(self, amount):
        """Overrides Enemy.take_damage to handle removal from active_skeletons list."""
        # Call the parent class's take_damage method
        super().take_damage(amount)

        # If the skeleton died, remove it from the owner's active_skeletons list
        if self.current_life <= 0:
            if self.owner: # Ensure owner exists
                self.owner.remove_skeleton(self)


    def update(self, dt, player, tile_map, tile_size):
        """Update the skeleton's behavior: move towards and attack enemies."""
        if not player:
            return

        current_time = pygame.time.get_ticks()

        # Find the nearest enemy (excluding other skeletons) within the finding range
        nearest_enemy = self._find_nearest_enemy(player, self.enemy_finding_range)

        if nearest_enemy:
            # Calculate distance to the nearest enemy
            dx, dy = nearest_enemy.rect.centerx - self.rect.centerx, nearest_enemy.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)

            # Melee attack logic
            if dist <= self.attack_range and current_time - self.last_attack_time > self.attack_cooldown:
                nearest_enemy.take_damage(self.damage)
                self.last_attack_time = current_time
                print(f"Skeleton attacked {nearest_enemy.name} for {self.damage} damage.")
            # Move towards the nearest enemy
            elif dist > 0:
                # Normalize direction vector
                dx, dy = dx / dist, dy / dist
                # Calculate potential movement
                move_x = dx * self.speed * dt
                move_y = dy * self.speed * dt # Corrected potential typo here

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
        
        if not nearest_enemy:
            # Calculate distance to player
            dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)

            # Move towards the player if no enemies are nearby and within following range
            if dist > 0 and dist < self.following_range:
                self._circle_around_player(dt, player, tile_map, tile_size)

    def _find_nearest_enemy(self, player, finding_range):
        """Find the nearest enemy (that is not a skeleton) to attack within the finding range."""
        nearest_enemy = None
        min_distance = float('inf')

        # Iterate over all enemies in the current scene
        for sprite in self.game.current_scene.enemies:
            # Ensure it's an Enemy and not a friendly skeleton
            if isinstance(sprite, Enemy) and not isinstance(sprite, Skeleton):
                # Calculate distance to the enemy
                dx, dy = sprite.rect.centerx - self.rect.centerx, sprite.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)

                if dist < min_distance and dist <= finding_range:
                    min_distance = dist
                    nearest_enemy = sprite

        # If no enemies are found within the finding range, return None
        return nearest_enemy
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

    def _circle_around_player(self, dt, player, tile_map, tile_size):
        """Makes the skeleton circle and dance around the player."""
        # Update the circle angle
        self.circle_angle += self.circle_speed * dt
        if self.circle_angle > 2 * math.pi:
            self.circle_angle -= 2 * math.pi

        # Calculate the offset using sine and cosine functions for a wave-like motion
        offset_x = math.cos(self.circle_angle) * self.circle_radius + math.sin(2 * self.circle_angle) * self.circle_radius * 0.3
        offset_y = math.sin(self.circle_angle) * self.circle_radius + math.cos(2 * self.circle_angle) * self.circle_radius * 0.3

        # Calculate the new position
        new_x = player.rect.centerx + offset_x
        new_y = player.rect.centery + offset_y

        # Store original position for collision rollback
        original_x, original_y = self.rect.x, self.rect.y

        # Move to the new position
        self.rect.x = new_x - self.rect.width / 2
        if self._check_collision(tile_map, tile_size):
            self.rect.x = original_x  # Rollback if collision

        self.rect.y = new_y - self.rect.height / 2
        if self._check_collision(tile_map, tile_size):
            self.rect.y = original_y  # Rollback if collision

class WraithEffect(pygame.sprite.Sprite):
    def __init__(self, game, x, y, image_path, scale=1):
        super().__init__()
        self.game = game
        self.original_image = pygame.image.load(os.path.join(os.getcwd(), image_path)).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (int(self.original_image.get_width() * scale), int(self.original_image.get_height() * scale)))
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 255
        self.fade_speed = 255  # Adjust for faster/slower fade - set to max for instant fade
        self.duration = 1000 # 1 second
        self.start_time = pygame.time.get_ticks()

    def update(self, dt, player=None, tile_map=None, tile_size=None, nearest_skeleton=None):
        time_elapsed = pygame.time.get_ticks() - self.start_time
        if time_elapsed > self.duration:
            self.alpha -= self.fade_speed * dt
            if self.alpha <= 0:
                self.kill()  # Remove the sprite
        self.image.set_alpha(self.alpha)

    def draw(self, screen, camera_x, camera_y, zoom_level):
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * zoom_level), int(self.original_image.get_height() * zoom_level)))
        screen_x = (self.rect.x - camera_x) * zoom_level
        screen_y = (self.rect.y - camera_y) * zoom_level
        screen.blit(scaled_image, (screen_x, screen_y))