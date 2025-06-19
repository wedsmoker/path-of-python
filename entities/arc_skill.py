import pygame
import math
import os
import random
import json
from config.constants import TILE_SIZE
from entities.projectile import Projectile
from entities.enemy import Enemy # Import Enemy class
from entities.summon_skeletons import WraithEffect

class ArcSkill:
    def __init__(self, player):
        self.player = player
        self.arc_chain_lightning_image_path = "graphics/spells/air/chain_lightning.png" # Store path instead of loaded image
        self.chain_range = 500  # Increased distance within which lightning can chain to the next enemy
        self.arc_speed = 500  # Speed of the visual lightning projectile
        self.last_used = 0
        self.damage_variation = 5
        self.stun_chance = 0.15
        self.arc_width = TILE_SIZE // 2
        self.lightning_color = (173, 216, 230) # Light blue
        self.lightning_glow_color = (100, 149, 237) # Cornflower blue
        self.max_initial_branches = 2 # Max number of new chains that can originate from the player
        self.max_branches_per_hit = 2 # Max number of new chains that can originate from one hit target

        # Load skill data from JSON
        self._load_skill_data()

        # This set will track all enemies that have been damaged in the current skill activation
        # It's reset each time activate() is called.
        self.enemies_damaged_in_current_cast = set()

    def _load_skill_data(self):
        """Loads Arc skill data from skills.json."""
        skills_file_path = os.path.join(os.getcwd(), "data", "skills.json")
        try:
            with open(skills_file_path, 'r') as f:
                skills_data = json.load(f)
            
            arc_skill_data = None
            for skill in skills_data.get("active_skills", []):
                if skill.get("id") == "arc":
                    arc_skill_data = skill
                    break
            
            if arc_skill_data:
                self.max_chain_length = arc_skill_data.get("chain_count", 4) # Default to 4 if not found
                self.base_damage = arc_skill_data.get("base_damage", {}).get("min", 10) # Using min as base
                self.mana_cost = arc_skill_data.get("mana_cost", 15)
                self.cooldown = arc_skill_data.get("cooldown", 0.7) * 1000 # Convert to milliseconds
                print(f"Arc skill data loaded: max_chain_length={self.max_chain_length}, base_damage={self.base_damage}, mana_cost={self.mana_cost}, cooldown={self.cooldown}")
            else:
                print("Arc skill data not found in skills.json. Using default values.")
                self.max_chain_length = 4
                self.base_damage = 15
                self.mana_cost = 15
                self.cooldown = 700 # Default to 0.7 seconds
        except FileNotFoundError:
            print(f"Error: skills.json not found at {skills_file_path}. Using default Arc skill values.")
            self.max_chain_length = 4
            self.base_damage = 15
            self.mana_cost = 15
            self.cooldown = 700 # Default to 0.7 seconds
        except json.JSONDecodeError:
            print(f"Error decoding skills.json at {skills_file_path}. Using default Arc skill values.")
            self.max_chain_length = 4
            self.base_damage = 15
            self.mana_cost = 15
            self.cooldown = 700 # Default to 0.7 seconds

    def load_arc_image(self, path):
        """Loads and scales the arc image."""
        try:
            image = pygame.image.load(os.path.join(os.getcwd(), path)).convert_alpha()
            return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        except FileNotFoundError:
            print(f"Error: Arc image file not found: {path}")
            return None

    def can_cast(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_used < self.cooldown:
            return False
        if not self.player.has_skill("arc"):
            return False
        if self.player.current_mana < self.mana_cost:
            return False
        return True

    def activate(self, mouse_pos=None): # Added mouse_pos parameter
        """Activates the Arc skill, creating initial projectiles that chain to strike multiple enemies."""
        print("ArcSkill.activate() called!") # Added print statement
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

        # Clear the set of damaged enemies for this new skill activation
        self.enemies_damaged_in_current_cast.clear()

        # Start the chain from the player
        start_x, start_y = self.player.rect.center

        # Find all initial targets within range
        initial_targets = []
        for sprite in self.player.game.current_scene.enemies:
            enemy = sprite
            # Exclude skeletons and wraiths
            if isinstance(enemy, WraithEffect) or enemy.name == "Skeleton":
                continue
            distance = math.hypot(enemy.rect.centerx - start_x, enemy.rect.centery - start_y)
            if distance < self.chain_range:
                initial_targets.append(enemy)
        
        if not initial_targets:
            print("No enemies in range for Arc skill.")
            return

        # Deduct mana cost only if there are initial targets
        self.player.current_mana -= self.mana_cost
        self.last_used = current_time

        # Shuffle and pick a few initial targets to branch out from the player
        random.shuffle(initial_targets)
        num_initial_chains = min(len(initial_targets), self.max_initial_branches)

        for i in range(num_initial_chains):
            target_enemy = initial_targets[i]
            end_x, end_y = target_enemy.rect.center
            damage = self.calculate_damage()
            
            # Add the initial target to the set of enemies damaged in this cast
            # Damage will be applied when the projectile hits in ArcProjectile._handle_enemy_collision
            
            arc_projectile = ArcProjectile(
                self.player.game, 
                start_x, start_y, 
                end_x, end_y, 
                self.arc_speed, 
                damage, 
                self.arc_chain_lightning_image_path, 
                self, 
                (start_x, start_y), 
                1, # chain_count starts at 1
                self.player # Previous target is the player for the initial cast
            )
            self.player.game.current_scene.projectiles.add(arc_projectile)
            print(f"Arc skill activated. Initial target: {target_enemy.name}")

    def calculate_damage(self):
        """Calculates damage with variation and player level scaling."""
        level_bonus = self.player.level * 2
        damage = self.base_damage + random.randint(-self.damage_variation, self.damage_variation) + level_bonus
        return damage

    def trigger_chain_reaction_from_enemy(self, current_target, current_chain_count, previous_target):
        """Triggers a chain reaction that damages nearby enemies from a hit target."""
        print(f"Chain reaction triggered from {current_target.name} (Chain count: {current_chain_count})!")
        
        eligible_enemies = []
        for sprite in self.player.game.current_scene.enemies:
            enemy = sprite
            # Exclude skeletons and wraiths
            if isinstance(enemy, WraithEffect) or enemy.name == "Skeleton":
                continue
            # Allow re-hitting enemies for visual effect, but prevent chaining back to the immediate previous target
            # and prevent chaining to the current target (as it just got hit)
            if enemy == current_target or enemy == previous_target: 
                continue

            distance = math.hypot(enemy.rect.centerx - current_target.rect.centerx, enemy.rect.centery - current_target.rect.centery)
            if distance < self.chain_range:
                eligible_enemies.append((distance, enemy)) # Store distance for sorting

        eligible_enemies.sort(key=lambda x: x[0]) # Sort by distance

        targets_for_branching = [enemy for dist, enemy in eligible_enemies[:self.max_branches_per_hit]]

        if not targets_for_branching:
            print("No further enemies in range for chain reaction from this target.")
            return

        for next_target in targets_for_branching:
            print(f"Chaining to next target: {next_target.name}")
            
            damage = self.calculate_damage()
            
            new_arc_projectile = ArcProjectile(
                self.player.game, # Corrected from self.game to self.player.game
                current_target.rect.centerx,
                current_target.rect.centery,
                next_target.rect.centerx,
                next_target.rect.centery,
                self.arc_speed,
                damage,
                self.arc_chain_lightning_image_path,
                self,
                (current_target.rect.centerx, current_target.rect.centery),
                current_chain_count + 1, # Increment chain count
                current_target # The current target becomes the previous target for the next projectile
            )
            self.player.game.current_scene.projectiles.add(new_arc_projectile)

    def update(self, dt):
        """Updates the Arc skill's state, primarily handling cooldowns."""
        # No specific continuous effects for Arc, but cooldown needs to be managed.
        # The actual projectiles are managed by the game's projectile group.
        pass # Placeholder for now, can add more complex logic later if needed

class ArcProjectile(Projectile):
    def __init__(self, game, x, y, target_x, target_y, speed, damage, sprite_path, arc_skill, start_pos=None, chain_count=0, previous_target=None):
        super().__init__(game, x, y, target_x, target_y, speed, damage, sprite_path)
        self.arc_skill = arc_skill
        self.current_target = None # Store the actual target enemy object
        self.start_pos = start_pos if start_pos is not None else (x, y) # Store the starting position for drawing the line
        self.lifetime = 2000 # Increased lifetime for visual effect, as it's a chaining projectile
        self.chain_count = chain_count # Track how many times this specific chain has linked
        self.previous_target = previous_target # The entity this projectile chained *from*

    def update(self, dt, player, tile_map, tile_size):
        # Move the projectile
        self.rect.x += self.dx * self.speed * dt
        self.rect.y += self.dy * self.speed * dt

        # Check for collision with solid tiles (walls)
        if self._check_collision(tile_map, tile_size):
            self.kill() # Remove projectile on wall hit
            return

        # Check for collision with enemies
        # Iterate over a copy of the enemies group to avoid issues if enemies are removed
        for enemy_sprite in self.game.current_scene.enemies.copy():
            if isinstance(enemy_sprite, Enemy) and self.rect.colliderect(enemy_sprite.rect):
                self.current_target = enemy_sprite
                self._handle_enemy_collision(enemy_sprite)
                self.kill() # Remove this projectile as it has hit its target
                return # Exit update after handling collision

        # Remove projectile after a certain lifetime (if it hasn't hit anything)
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

    def _handle_enemy_collision(self, enemy):
        """Handles collision with an enemy, applies damage, and triggers chain reaction."""
        print(f"ArcProjectile hit enemy: {enemy.name}")
        
        # Only apply damage if this enemy hasn't been damaged by this skill cast yet
        if enemy not in self.arc_skill.enemies_damaged_in_current_cast:
            enemy.take_damage(self.damage)
            self.arc_skill.enemies_damaged_in_current_cast.add(enemy) # Mark as damaged

            # Apply stun chance only on first hit
            if random.random() < self.arc_skill.stun_chance:
                print(f"{enemy.name} stunned!")
                # Implement stun effect on enemy (e.g., enemy.apply_stun())
        else:
            print(f"Enemy {enemy.name} already damaged by this Arc skill cast. Skipping damage.")


        # Trigger chain reaction if max chain length not reached
        if self.chain_count < self.arc_skill.max_chain_length:
            self.arc_skill.trigger_chain_reaction_from_enemy(enemy, self.chain_count, self.previous_target)

    def draw(self, screen, camera_x, camera_y, zoom_level):
        # Calculate screen coordinates for the start and end points of the lightning line
        start_screen_x = (self.start_pos[0] - camera_x) * zoom_level
        start_screen_y = (self.start_pos[1] - camera_y) * zoom_level
        
        end_screen_x = (self.rect.centerx - camera_x) * zoom_level
        end_screen_y = (self.rect.centery - camera_y) * zoom_level

        # Get screen dimensions
        screen_width, screen_height = screen.get_size()

        # Check if any part of the line is within the screen bounds
        # This is a simplified check; a more robust check would involve line-segment-rectangle intersection
        if not (max(start_screen_x, end_screen_x) < 0 or 
                min(start_screen_x, end_screen_x) > screen_width or
                max(start_screen_y, end_screen_y) < 0 or
                min(start_screen_y, end_screen_y) > screen_height):

            line_width = int(self.arc_skill.arc_width * zoom_level)
            num_segments = 10 # Number of segments for the jagged lightning effect
            jaggedness = 10 * zoom_level # How much the segments can deviate

            # Draw the lightning line with jagged effect and glow
            points = []
            points.append((start_screen_x, start_screen_y))

            for i in range(1, num_segments):
                # Calculate a point along the straight line
                t = i / num_segments
                target_segment_x = start_screen_x + (end_screen_x - start_screen_x) * t
                target_segment_y = start_screen_y + (end_screen_y - start_screen_y) * t

                # Add random offset for jaggedness, perpendicular to the line
                angle = math.atan2(end_screen_y - start_screen_y, end_screen_x - start_screen_x)
                perp_angle = angle + math.pi / 2 # Perpendicular angle
                offset = random.uniform(-jaggedness, jaggedness)
                offset_x = math.cos(perp_angle) * offset
                offset_y = math.sin(perp_angle) * offset
                
                points.append((target_segment_x + offset_x, target_segment_y + offset_y))
            
            points.append((end_screen_x, end_screen_y))

            if len(points) > 1:
                # Draw glow effect
                pygame.draw.lines(screen, self.arc_skill.lightning_glow_color, False, points, line_width + 4)
                # Draw main lightning line
                pygame.draw.lines(screen, self.arc_skill.lightning_color, False, points, line_width)

            # Optionally draw a small spark image at the current projectile's position
            if self.image:
                scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * zoom_level), int(self.rect.height * zoom_level)))
                screen.blit(scaled_image, (end_screen_x - scaled_image.get_width() / 2, end_screen_y - scaled_image.get_height() / 2))