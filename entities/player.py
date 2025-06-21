from entities.player_sprites import get_player_head_sprite, get_player_hand_sprite, get_player_leg_sprite, get_player_sprite
import pygame
import math
import json
import os
import random
# from core.pathfinding import Pathfinding # Removed pathfinding import
from config.constants import TILE_SIZE, PLAYER_SPEED
from entities.arc_skill import ArcSkill
from entities.summon_skeletons import SummonSkeletons  # Import SummonSkeletons
from entities.cleave_skill import CleaveSkill # Import CleaveSkill
from entities.cyclone_skill import CycloneSkill # Import CycloneSkill
from entities.fireball_skill import FireballSkill # Import FireballSkill
from entities.summon_spiders import SummonSpiders # Import SummonSpiders

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, class_name="knight", initial_stats=None):
        super().__init__()
        self.game = game
        self.class_name = class_name # Initialize with a default or passed class_name
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED  # Adjust as needed
        self.velocity = pygame.math.Vector2(0, 0)
        self.target = None  # The target world coordinates the player is moving towards
        # self.path = []  # Removed path attribute
        self.is_moving = False
        self.last_move_time = pygame.time.get_ticks()
        self.move_interval = 50  # milliseconds between sprite updates

        # Footstep attributes
        self.footstep_sprites = []
        self.footstep_interval = 100  # milliseconds between footsteps
        self.last_footstep_time = pygame.time.get_ticks()

        # Load player sprites - these will be updated by set_class
        self.head1_sprite = get_player_head_sprite(class_name)
        self.hand1_sprite = get_player_hand_sprite(class_name)
        self.leg1_sprite = get_player_leg_sprite(class_name)
        self.base_sprite = get_player_sprite(class_name)

        # Combine sprites
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE], pygame.SRCALPHA)
        self.image.blit(self.base_sprite, (0, 0))
        self.image.blit(self.leg1_sprite, (0, 0))
        self.image.blit(self.hand1_sprite, (0, 0))
        self.image.blit(self.head1_sprite, (0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.rect.width
        self.height = self.rect.height

        # Stats
        self.level = 1
        self.experience = 0
        self.skill_points = 10 # Starting skill points
        self.base_strength = 10
        self.base_dexterity = 10
        self.base_intelligence = 10
        self.base_vitality = 10
        self.current_life = 100
        self.max_life = 100
        self.current_energy_shield = 50
        self.max_energy_shield = 50
        self.current_mana = 100
        self.max_mana = 100
        self.item_find_chance = 0.0
        self.evasion = 0.0
        self.stealth = 0.0

        # Energy Shield Recharge attributes
        self.energy_shield_recharge_delay = 3000 # 3 seconds cooldown before recharge starts
        self.last_energy_shield_hit_time = 0
        self.energy_shield_recharge_rate = 0.10 # 10% of max_energy_shield per second
        self.mana_recharge_rate = 0.1 # 10% of max_mana per second
        self.health_regen_rate = 0.20 # 20% of max_life per second

        # New stats dictionary
        self.stats = {
            "item_find_chance": self.item_find_chance,
            "evasion": self.evasion,
            "stealth": self.stealth,
            "base_strength": self.base_strength,
            "base_dexterity": self.base_dexterity,
            "base_intelligence": self.base_intelligence,
            "base_vitality": self.base_vitality,
            "current_life": self.current_life,
            "max_life": self.max_life,
            "current_energy_shield": self.current_energy_shield,
            "max_energy_shield": self.max_energy_shield,
            "current_mana": self.current_mana,
            "max_mana": self.max_mana,
        }

        # Apply initial stats if provided
        if initial_stats:
            self.apply_stats(initial_stats)

        from items.inventory import Inventory
        self.inventory = Inventory(self.game, 20) # Initialize inventory with a capacity of 20 slots

        # Load skill data from JSON
        self.skills = self.load_skills('data/skill_tree.json')
        self.unlocked_skills = [] # Initialize as empty, will be populated by set_class
        self.skill_key_bindings = {}

        # Create skill key bindings
        for skill in self.skills:
            if "key_binding" in skill:
                self.skill_key_bindings[skill["key_binding"]] = skill["id"]

        self.is_taking_damage = False
        self.damage_start_time = 0
        self.damage_duration = 100  # milliseconds

        # Skill-specific attributes
        self.arc_skill = ArcSkill(self)
        self.summon_skeletons_skill = SummonSkeletons(self)  # Initialize SummonSkeletons skill
        self.cleave_skill = CleaveSkill(self) # Initialize CleaveSkill
        self.cyclone_skill = CycloneSkill(self) # Initialize CycloneSkill
        self.fireball_skill = FireballSkill(self) # Initialize FireballSkill
        self.summon_spiders_skill = SummonSpiders(self) # Initialize SummonSpiders

    def apply_stats(self, stats_dict):
        """Applies a dictionary of stats to the player."""
        for stat_key, value in stats_dict.items():
            if hasattr(self, stat_key):
                setattr(self, stat_key, value)
                self.stats[stat_key] = value
        # Ensure current life, mana, energy shield are capped at max
        self.current_life = self.max_life
        self.current_mana = self.max_mana
        self.current_energy_shield = self.max_energy_shield

    def set_class(self, class_name, class_stats=None):
        """Sets the player's class and updates their sprites and initial skills."""
        self.class_name = class_name
        self.game.logger.info(f"Player class set to: {self.class_name}")

        # Update player sprites based on the new class
        self.head1_sprite = get_player_head_sprite(class_name)
        self.hand1_sprite = get_player_hand_sprite(class_name)
        self.leg1_sprite = get_player_leg_sprite(class_name)
        self.base_sprite = get_player_sprite(class_name)

        # Recombine sprites
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE], pygame.SRCALPHA)
        self.image.blit(self.base_sprite, (0, 0))
        self.image.blit(self.leg1_sprite, (0, 0))
        self.image.blit(self.hand1_sprite, (0, 0))
        self.image.blit(self.head1_sprite, (0, 0))

        # Apply class-specific stats
        if class_stats:
            self.apply_stats(class_stats)

        # Update unlocked skills based on class
        if class_name == "stalker":
            self.unlocked_skills = ["cleave", "cyclone"]
        elif class_name == "technomancer":
            self.unlocked_skills = ["arc", "fireball"]
        elif class_name == "hordemonger":
            self.unlocked_skills = ["summon_skeleton", "summon_spiders"]
        else:
            self.unlocked_skills = [] # Default or error case

        self.skill_key_bindings = {}
        for skill in self.skills:
            if "key_binding" in skill and skill["id"] in self.unlocked_skills:
                self.skill_key_bindings[skill["key_binding"]] = skill["id"]


    def load_skills(self, json_path):
        """Loads skill data from a JSON file."""
        try:
            skill_data_path = os.path.join(os.getcwd(), json_path)
            with open(skill_data_path, "r") as f:
                data = json.load(f)
            return data['skills']
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading skill data from {json_path}: {e}")
            return []

    def has_skill(self, skill_id):
        """Checks if the player has unlocked a specific skill."""
        return skill_id in self.unlocked_skills

    def can_activate_skill(self, skill_id):
        """Checks if the player has the skill and enough mana to activate it."""
        if not self.has_skill(skill_id):
            return False

        if skill_id == "cleave":
            return self.cleave_skill.can_cast()
        elif skill_id == "cyclone":
            return self.cyclone_skill.can_cast()
        elif skill_id == "arc":
            return self.arc_skill.can_cast()
        elif skill_id == "summon_skeleton":
            return self.summon_skeletons_skill.can_cast()
        elif skill_id == "fireball":
            return self.fireball_skill.can_cast()
        elif skill_id == "summon_spiders":
            return self.summon_spiders_skill.can_cast()

        # Fallback for skills not explicitly handled above (e.g., passive skills from skill_tree.json)
        skill = next((s for s in self.skills if s['id'] == skill_id), None)
        if skill is None:
            return False

        if self.current_mana < skill['cost']:
            return False

        return True

    def activate_skill(self, skill_id, mouse_pos=None):
        """Activates the skill and applies its effects."""
        if not self.can_activate_skill(skill_id):
            return False

        if skill_id == "cleave":
            self.cleave_skill.activate()
            return True
        elif skill_id == "cyclone":
            self.cyclone_skill.activate()
            return True
        elif skill_id == "arc":
            self.arc_skill.activate()
            return True
        elif skill_id == "summon_skeleton":
            if mouse_pos:
                self.summon_skeletons_skill.activate(mouse_pos[0], mouse_pos[1])
            return True
        elif skill_id == "fireball":
            if mouse_pos:
                self.fireball_skill.activate(mouse_pos[0], mouse_pos[1])
            return True
        elif skill_id == "summon_spiders":
            self.summon_spiders_skill.activate() # Removed mouse_pos arguments
            return True

        # Fallback for skills not explicitly handled above (e.g., passive skills from skill_tree.json)
        skill = next((s for s in self.skills if s['id'] == skill_id), None)
        if skill is None:
            return False

        # Deduct mana cost
        self.current_mana -= skill['cost']

        # Apply skill effects
        stat = skill.get('stat')
        amount = skill.get('amount')
        if stat and amount:
            if stat in self.stats:
                self.stats[stat] += amount
                # Update the corresponding attribute
                setattr(self, stat, self.stats[stat])
            else:
                print(f"Warning: Stat '{stat}' not found in player stats.")

        stat2 = skill.get('stat2')
        amount2 = skill.get('amount2')
        if stat2 and amount2:
            if stat2 in self.stats:
                self.stats[stat2] += amount2
                # Update the corresponding attribute
                setattr(self, stat2, self.stats[stat2])
            else:
                print(f"Warning: Stat '{stat2}' not found in player stats.")

        print(f"Skill '{skill_id}' activated!")

        # Visual effect (placeholder)
        effect_surface = pygame.Surface((50, 50))
        effect_surface.fill((255, 255, 0)) # Yellow color

        # Create a sprite for the effect
        effect_sprite = pygame.sprite.Sprite()
        effect_sprite.image = effect_surface
        effect_sprite.rect = effect_sprite.image.get_rect(center=self.rect.center)

        self.game.current_scene.effects.add(effect_sprite)
        return True

    def set_target(self, world_x, world_y):
        # Set the target directly to world coordinates
        self.target = (world_x, world_y)
        self.is_moving = True
        # Calculate initial velocity towards the target
        direction_x = self.target[0] - self.rect.x
        direction_y = self.target[1] - self.rect.y
        distance = math.hypot(direction_x, direction_y)
        if distance > 0:
            direction_x /= distance
            direction_y /= distance
            self.velocity.x = direction_x * self.speed
            self.velocity.y = direction_y * self.speed
        else:
            self.velocity.x = 0
            self.velocity.y = 0
            self.is_moving = False
            self.target = None
    
    def take_damage(self, damage):
        """Reduces the player's current energy shield first, then life, and triggers a screen pulse."""
        remaining_damage = damage

        # Apply damage to energy shield first
        if self.current_energy_shield > 0:
            self.last_energy_shield_hit_time = pygame.time.get_ticks() # Reset recharge timer
            if remaining_damage >= self.current_energy_shield:
                remaining_damage -= self.current_energy_shield
                self.current_energy_shield = 0
                print(f"Energy shield depleted. Remaining damage: {remaining_damage}")
            else:
                self.current_energy_shield -= remaining_damage
                remaining_damage = 0
                print(f"Energy shield took {damage} damage. Current energy shield: {self.current_energy_shield}")

        # Apply any remaining damage to life
        if remaining_damage > 0:
            self.current_life -= remaining_damage
            if self.current_life < 0:
                self.current_life = 0
            print(f"Player took {remaining_damage} damage to life. Current life: {self.current_life}")

        if self.current_life <= 0:
            self.current_life = 0
            print("Player died!")
            self.game.current_scene.display_death_message = True
            self.game.current_scene.death_message_start_time = pygame.time.get_ticks()
            self.game.current_scene.death_message_duration = 5000 # 5 seconds

        # Trigger screen pulse effect
        self.is_taking_damage = True
        self.damage_start_time = pygame.time.get_ticks()

    def gain_experience(self, amount):
        """
        Awards experience to the player based on the given amount.
        Checks for level-ups and calls the level_up method if enough experience is gained.
        """
        print(f"Player.gain_experience called with amount: {amount}") # Debug print
        self.experience += amount
        print(f"Gained {amount} experience. Total experience: {self.experience}")

        # Check for level up
        xp_for_next_level = self.level * 100 # Example: 100 XP per level
        if self.experience >= xp_for_next_level:
            self.level_up()

    def level_up(self):
        """
        Increases player level and boosts all base stats, max life, mana, and energy shield.
        """
        self.level += 1
        self.experience = 0 # Reset experience for the new level
        print(f"Player leveled up to level {self.level}!")

        # Increase base stats
        self.base_strength += 2
        self.base_dexterity += 2
        self.base_intelligence += 2
        self.base_vitality += 2

        # Increase max life, mana, and energy shield
        self.max_life += 50
        self.current_life = self.max_life # Fully heal on level up
        self.max_mana += 50
        self.current_mana = self.max_mana # Fully restore mana on level up
        self.max_energy_shield += 30
        self.current_energy_shield = self.max_energy_shield # Fully restore energy shield on level up

        # Update stats dictionary
        self.stats["base_strength"] = self.base_strength
        self.stats["base_dexterity"] = self.base_dexterity
        self.stats["base_intelligence"] = self.base_intelligence
        self.stats["base_vitality"] = self.base_vitality
        self.stats["max_life"] = self.max_life
        self.stats["max_mana"] = self.max_mana
        self.stats["max_energy_shield"] = self.max_energy_shield
    
    def activate_arc(self):
        """Activates the Arc skill, chaining electricity to strike multiple enemies."""
        self.arc_skill.activate()

    def activate_summon_skeletons(self, x, y):
        """Activates the Summon Skeletons skill."""
        self.summon_skeletons_skill.activate(x, y)

    def _check_collision(self, tile_map, tile_size):
        """Checks for collision with solid tiles, allowing movement through single-tile gaps."""
        # Get the tile coordinates the enemy is currently occupying
        enemy_left_tile = int(self.rect.left / tile_size)
        enemy_right_tile = int(self.rect.right / tile_size)
        enemy_top_tile = int(self.rect.top / tile_size)
        enemy_bottom_tile = int(self.rect.bottom / tile_size)

        if not tile_map:
            return False
        # Clamp tile coordinates to map boundaries
        map_width_tiles = len(tile_map[0])
        map_height_tiles = len(tile_map)

        enemy_left_tile = max(0, min(enemy_left_tile, map_width_tiles - 1))
        enemy_right_tile = max(0, min(enemy_right_tile, map_width_tiles - 1))
        enemy_top_tile = max(0, min(enemy_top_tile, map_height_tiles - 1))
        enemy_bottom_tile = max(0, min(enemy_bottom_tile, map_height_tiles - 1))

        # Check for collision on each side of the player
        collide_left = False
        collide_right = False
        collide_top = False
        collide_bottom = False

        for y in range(enemy_top_tile, enemy_bottom_tile + 1):
            if tile_map[y][enemy_left_tile] in ('wall', 'mountain', 'building', 'rubble'):
                collide_left = True
            if tile_map[y][enemy_right_tile] in ('wall', 'mountain', 'building', 'rubble'):
                collide_right = True

        for x in range(enemy_left_tile, enemy_right_tile + 1):
            if tile_map[enemy_top_tile][x] in ('wall', 'mountain', 'building', 'rubble'):
                collide_top = True
            if tile_map[enemy_bottom_tile][x] in ('wall', 'mountain', 'building', 'rubble'):
                collide_bottom = True

        # Allow squeezing through single-tile gaps based on movement direction
        if self.velocity.x != 0:  # Moving horizontally
            if collide_left and collide_right:
                return True  # Blocked horizontally
        elif self.velocity.y != 0:  # Moving vertically
            if collide_top and collide_bottom:
                return True  # Blocked vertically

        return False  # No collision

    def check_and_correct_position(self):
        """Checks if the player is on an unwalkable tile and moves them to a walkable one."""
        tile_size = TILE_SIZE  # Assuming tile size is accessible here
        tile_map = self.game.scene_manager.current_scene.tile_map
        player_tile_x = int(self.rect.centerx // tile_size)
        player_tile_y = int(self.rect.centery // tile_size)

        if 0 <= player_tile_x < self.game.scene_manager.current_scene.map_width and \
           0 <= player_tile_y < self.game.scene_manager.current_scene.map_height:
            if player_tile_y < len(tile_map) and player_tile_x < len(tile_map[player_tile_y]):
                tile_type = tile_map[player_tile_y][player_tile_x]
                if tile_type in ('wall', 'mountain', 'building', 'rubble'):
                    # Find a nearby walkable tile
                    for offset in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                        new_tile_x = player_tile_x + offset[0]
                        new_tile_y = player_tile_y + offset[1]
                        if 0 <= new_tile_x < self.game.scene_manager.current_scene.map_width and 0 <= new_tile_y < self.game.scene_manager.current_scene.map_height:
                            if new_tile_y < len(tile_map) and new_tile_x < len(tile_map[new_tile_y]):
                                new_tile_type = tile_map[new_tile_y][new_tile_x]
                                if new_tile_type not in ('wall', 'mountain', 'building', 'rubble'):
                                    # Move the player to the center of this tile
                                    self.rect.x = new_tile_x * tile_size
                                    self.rect.y = new_tile_y * tile_size
                                    break # Stop searching after finding one walkable tile
                            

    def blink(self, target_x, target_y):
        """Teleports the player to the target location if it's walkable."""
        tile_size = TILE_SIZE
        tile_map = self.game.scene_manager.current_scene.tile_map

        target_tile_x = int(target_x // tile_size)
        target_tile_y = int(target_y // tile_size)

        if 0 <= target_tile_x < self.game.scene_manager.current_scene.map_width:
            if 0 <= target_tile_y < self.game.scene_manager.current_scene.map_height:
                if target_tile_y < len(tile_map):
                    if target_tile_x < len(tile_map[target_tile_y]):
                        tile_type = tile_map[target_tile_y][target_tile_x]
                        if tile_type not in ('wall', 'mountain', 'building', 'rubble'):
                            # Teleport the player to the target location
                            self.rect.x = target_x
                            self.rect.y = target_y
                            print(f"Player blinked to ({target_x}, {target_y})")
                        else:
                            print("Cannot blink to an unwalkable tile.")
                    else:
                        print("Cannot blink outside the map boundaries.")
                else:
                    print("Cannot blink outside the map boundaries.")
            else:
                print("Cannot blink outside the map boundaries.")
        else:
            print("Cannot blink outside the map boundaries.")

    def update(self, dt):
        # Get the tile_map and tile_size from the current scene
        tile_map = self.game.scene_manager.current_scene.tile_map
        tile_size = TILE_SIZE

        # Check and correct the player's position at the start of each update
        self.check_and_correct_position()

        dt = min(dt, 0.1)  # Clamp dt to a maximum of 0.1
        current_time = pygame.time.get_ticks()

        if self.is_moving and self.target:
            # Calculate the potential new position
            new_x = self.rect.x + self.velocity.x * dt
            new_y = self.rect.y + self.velocity.y * dt

            # Store original position for collision rollback
            original_x, original_y = self.rect.x, self.rect.y

            # Attempt to move horizontally
            self.rect.x = new_x
            if self._check_collision(tile_map, tile_size):
                self.rect.x = original_x  # Rollback if collision

            # Attempt to move vertically
            self.rect.y = new_y
            if self._check_collision(tile_map, tile_size):
                self.rect.y = original_y  # Rollback if collision

        # Check if the player has reached the target
            distance_x = self.target[0] - self.rect.x
            distance_y = self.target[1] - self.rect.y
            distance_to_target = math.hypot(distance_x, distance_y)

            # Stop if the player is very close to the target
            if distance_to_target < 5: # Adjust threshold as needed
                self.rect.x = self.target[0] # Snap to target to prevent overshooting
                self.rect.y = self.target[1]
                self.velocity.x = 0
                self.velocity.y = 0
                self.is_moving = False
                self.target = None
            else:
                # Recalculate velocity in case the target was updated mid-movement
                direction_x = self.target[0] - self.rect.x
                direction_y = self.target[1] - self.rect.y
                distance = math.hypot(direction_x, direction_y)
                if distance > 0:
                    direction_x /= distance
                    direction_y /= distance
                    self.velocity.x = direction_x * self.speed
                    self.velocity.y = direction_y * self.speed
                else:
                    self.velocity.x = 0
                    self.velocity.y = 0
                    self.is_moving = False
                    self.target = None

        # Energy Shield Recharge Logic
        if self.current_energy_shield < self.max_energy_shield:
            if current_time - self.last_energy_shield_hit_time > self.energy_shield_recharge_delay:
                recharge_amount = self.max_energy_shield * self.energy_shield_recharge_rate * dt * 10 # Scale by 10 for faster recharge
                self.current_energy_shield = min(self.max_energy_shield, self.current_energy_shield + recharge_amount)
                # print(f"Energy shield recharging. Current ES: {self.current_energy_shield}")
        # Mana Recharge Logic
        if self.current_mana < self.max_mana:
            recharge_amount = self.max_mana * self.mana_recharge_rate * dt
            self.current_mana = min(self.max_mana, self.current_mana + recharge_amount)
# Health Regeneration Logic (only in SpawnTown)
        if self.game.scene_manager.current_scene.name == "SpawnTown":
            if self.current_life < self.max_life:
                regen_amount = self.max_life * self.health_regen_rate * dt
                self.current_life = min(self.max_life, self.current_life + regen_amount)

        # Footstep logic
        if self.is_moving and current_time - self.last_footstep_time > self.footstep_interval:
            self.last_footstep_time = current_time
            self.create_footstep()

        for sprite in list(self.footstep_sprites):  # Iterate over a copy of the list
            if current_time - sprite.creation_time > 2000:  # 2 seconds
                self.footstep_sprites.remove(sprite)
                self.game.current_scene.effects.remove(sprite)

        # Screen pulse effect
        if self.is_taking_damage:
            current_time = pygame.time.get_ticks()
            if current_time - self.damage_start_time > self.damage_duration:
                self.is_taking_damage = False

        # Update active skills
        self.cleave_skill.update(dt)
        self.cyclone_skill.update(dt)
        self.arc_skill.update(dt)
        self.summon_skeletons_skill.update(dt)
        self.fireball_skill.update(dt)
        self.summon_spiders_skill.update(dt)

    def create_footstep(self):
        # Load a random cloud_magic_trail image
        footstep_image = pygame.image.load(f"graphics/player/base/shadow.png").convert_alpha()
        footstep_sprite = pygame.sprite.Sprite()
        footstep_sprite.image = footstep_image
        footstep_sprite.rect = footstep_sprite.image.get_rect(center=self.rect.center)
        footstep_sprite.creation_time = pygame.time.get_ticks()  # Store creation time
        self.footstep_sprites.append(footstep_sprite)
        self.game.current_scene.effects.add(footstep_sprite)

    def draw(self, screen):
        screen_x = (self.rect.x - self.game.current_scene.camera_x) * self.game.current_scene.zoom_level
        screen_y = (self.rect.y - self.game.current_scene.camera_y) * self.game.current_scene.zoom_level
        scaled_image = pygame.transform.scale(self.image, (int(self.width * self.game.current_scene.zoom_level), int(self.height * self.game.current_scene.zoom_level)))
        screen.blit(scaled_image, (screen_x, screen_y))

        if self.is_taking_damage:
            # Create a red surface
            red_surface = pygame.Surface(screen.get_size())
            red_surface.fill((255, 0, 0))
            red_surface.set_alpha(100)  # Adjust alpha for desired intensity

        # Blit the red surface to the screen
            screen.blit(red_surface, (0, 0))

    def update_stat_from_dev_screen(self, stat_key, new_value):
        """
        Updates a player stat from the developer screen.
        This method is called by the DeveloperInventoryScreen.
        """
        if hasattr(self, stat_key):
            setattr(self, stat_key, new_value)
            self.stats[stat_key] = new_value
            # Special handling for current_life, max_life, current_mana, max_mana, etc.
            if stat_key == "max_life":
                self.current_life = min(self.current_life, self.max_life)
            elif stat_key == "max_mana":
                self.current_mana = min(self.current_mana, self.max_mana)
            elif stat_key == "max_energy_shield":
                self.current_energy_shield = min(self.current_energy_shield, self.max_energy_shield)
            # Add more special handling for other stats if needed
            print(f"Player stat '{stat_key}' updated to {new_value}")
        else:
            pass
    
    def deactivate_skill(self, skill_id):
        """Deactivates the specified skill."""
        if skill_id == "cyclone":
            self.cyclone_skill.deactivate()
