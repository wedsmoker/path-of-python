from entities.player_sprites import get_player_head_sprite, get_player_hand_sprite, get_player_leg_sprite, get_player_sprite
import pygame
import math
import json
import os
import random
# from core.pathfinding import Pathfinding # Removed pathfinding import
from config.constants import TILE_SIZE, PLAYER_SPEED
from entities.arc_skill import ArcSkill

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, class_name="knight"):
        super().__init__()
        self.game = game
        self.class_name = class_name
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED  # Adjust as needed
        self.velocity = pygame.math.Vector2(0, 0)
        self.target = None  # The target world coordinates the player is moving towards
        # self.path = []  # Removed path attribute
        self.is_moving = False
        self.last_move_time = pygame.time.get_ticks()
        self.move_interval = 50  # milliseconds between sprite updates

        # Load player sprites
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
        self.current_mana = 50
        self.max_mana = 50
        self.item_find_chance = 0.0
        self.evasion = 0.0
        self.stealth = 0.0

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

        from items.inventory import Inventory
self.footstep_sprites = []
        self.footstep_interval = 100  # milliseconds between footsteps
        self.last_footstep_time = pygame.time.get_ticks()
self.footstep_sprites = []
        self.footstep_interval = 100  # milliseconds between footsteps
        self.last_footstep_time = pygame.time.get_ticks()
        self.inventory = Inventory(self.game, 20) # Initialize inventory with a capacity of 20 slots

        # Load skill data from JSON
        self.skills = self.load_skills('data/skill_tree.json')
        self.unlocked_skills = [] # List to store unlocked skill IDs
        self.skill_key_bindings = {} # Dictionary to store skill key bindings

        # Create skill key bindings
        for skill in self.skills:
            if "key_binding" in skill:
                self.skill_key_bindings[skill["key_binding"]] = skill["id"]

        self.is_taking_damage = False
        self.damage_start_time = 0
        self.damage_duration = 100  # milliseconds

        # Skill-specific attributes
        # self.arc_chain_lightning_image = pygame.image.load("graphics/spells/air/chain_lightning.png").convert_alpha() if os.path.exists("graphics/spells/air/chain_lightning.png") else None
        self.arc_skill = ArcSkill(self)

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

        skill = next((s for s in self.skills if s['id'] == skill_id), None)
        if skill is None:
            return False

        if self.current_mana < skill['cost']:
            return False

        return True

    def activate_skill(self, skill_id):
        """Activates the skill and applies its effects."""
        if not self.can_activate_skill(skill_id):
            return False

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
        """Reduces the player's current life by the specified damage amount and triggers a screen pulse."""
        self.current_life -= damage
        if self.current_life < 0:
            self.current_life = 0
        print(f"Player took {damage} damage. Current life: {self.current_life}")
        if self.current_life <= 0:
            self.current_life = 0
            print("Player died!")
            self.game.current_scene.display_death_message = True
            self.game.current_scene.death_message_start_time = pygame.time.get_ticks()
            self.game.current_scene.death_message_duration = 5000 # 5 seconds

        # Trigger screen pulse effect
        self.is_taking_damage = True
        self.damage_start_time = pygame.time.get_ticks()

    def activate_arc(self):
        """Activates the Arc skill, chaining electricity to strike multiple enemies."""
        self.arc_skill.activate()

current_time = pygame.time.get_ticks()
        if self.is_moving and current_time - self.last_footstep_time > self.footstep_interval:
            self.last_footstep_time = current_time
            self.create_footstep()

        for sprite in list(self.footstep_sprites):  # Iterate over a copy of the list
            if current_time - sprite.creation_time > 2000:  # 2 seconds
                self.footstep_sprites.remove(sprite)
                self.game.current_scene.effects.remove(sprite)

    def create_footstep(self):
        # Load a random cloud_magic_trail image
        footstep_image = pygame.image.load(f"graphics/effect/cloud_magic_trail{random.randint(0, 3)}.png").convert_alpha()
        footstep_sprite = pygame.sprite.Sprite()
        footstep_sprite.image = footstep_image
        footstep_sprite.rect = footstep_sprite.image.get_rect(center=self.rect.center)
        footstep_sprite.creation_time = pygame.time.get_ticks()  # Store creation time
        self.footstep_sprites.append(footstep_sprite)
        self.game.current_scene.effects.add(footstep_sprite)
    def update(self, dt):
        dt = min(dt, 0.1)  # Clamp dt to a maximum of 0.1
        if self.is_moving and self.target:
            # Move the player
            self.rect.x += self.velocity.x * dt
            self.rect.y += self.velocity.y * dt

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

        # Screen pulse effect
        if self.is_taking_damage:
            current_time = pygame.time.get_ticks()
            if current_time - self.damage_start_time > self.damage_duration:
                self.is_taking_damage = False

        # Handle skill activation - REMOVE THIS
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_PAGEDOWN]:
        #     self.activate_arc()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - self.game.current_scene.camera_x, self.rect.y - self.game.current_scene.camera_y))

        if self.is_taking_damage:
            # Create a red surface
            red_surface = pygame.Surface(screen.get_size())
            red_surface.fill((255, 0, 0))
            red_surface.set_alpha(100)  # Adjust alpha for desired intensity

        # Blit the red surface to the screen
            screen.blit(red_surface, (0, 0))
