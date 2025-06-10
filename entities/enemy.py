import pygame
import os
import math
import random
from config.constants import TILE_SIZE
from entities.player import Player

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y, enemy_data):
        super().__init__()
        self.game = game
        self.name = enemy_data.get("name", "Unknown Enemy")
        self.max_life = enemy_data.get("health", 50)
        self.current_life = self.max_life
        self.damage = enemy_data.get("damage", 5)
        self.speed = enemy_data.get("speed", 50) # Pixels per second
        self.xp_value = enemy_data.get("xp_value", 10) # Add xp_value to JSON later
        self.abilities = enemy_data.get("abilities", []) # For future use

        sprite_path = enemy_data.get("sprite_path")
        if sprite_path and os.path.exists(sprite_path):
            self.image = pygame.image.load(sprite_path).convert_alpha()
            # Assuming a default size for now, might need to adjust based on actual sprites
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        else:
            print(f"Warning: Sprite not found for {self.name} at {sprite_path}. Using placeholder.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 0, 0)) # Red placeholder

        self.rect = self.image.get_rect(topleft=(x, y))
        self.original_y = y # Store the original Y position for bobbing
        self.bob_offset = 0
        self.bob_speed = 0.5 # Adjust for bobbing speed
        self.attack_range = TILE_SIZE * 1.5 # Adjust attack range as needed
        self.is_attacking = False
        self.attack_cooldown = 2000 # Milliseconds
        self.last_attack_time = 0

        # Load attack sprite
        self.attack_image = pygame.image.load("graphics/UNUSED/spells/components/bolt.png").convert_alpha() if os.path.exists("graphics/UNUSED/spells/components/bolt.png") else None
        self.attack_animation_duration = 500 # Milliseconds
        
        # ADDED LOGGING
        print(f"Enemy initialized: {self.name}, game object: {getattr(self, 'game', None)}")

    def update(self, dt):
        # Basic AI: Bobbing movement
        self.bob_offset = math.sin(pygame.time.get_ticks() * self.bob_speed) * 5 # Adjust amplitude (5) as needed
        self.rect.y = self.original_y + self.bob_offset

        # Basic AI: Move towards player and attack
        if not self.is_attacking:
            player = self.game.current_scene.player
            distance_to_player = math.hypot(self.rect.centerx - player.rect.centerx, self.rect.centery - player.rect.centery)

            if distance_to_player <= self.attack_range:
                # Attack the player
                self.attack(player)
            else:
                # Move towards the player
                direction_x = player.rect.centerx - self.rect.centerx
                direction_y = player.rect.centery - self.rect.centery
                distance = math.hypot(direction_x, direction_y)
                if distance > 0:
                    direction_x /= distance
                    direction_y /= distance
                    self.rect.x += direction_x * self.speed * dt
                    self.rect.y += direction_y * self.speed * dt

    def attack(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.is_attacking = True
            self.last_attack_time = current_time

            # Display attack sprite
            if self.attack_image:
                attack_x = self.rect.centerx
                attack_y = self.rect.centery

                # Create a sprite for the attack effect
                attack_sprite = pygame.sprite.Sprite()
                attack_sprite.image = self.attack_image
                attack_sprite.rect = attack_sprite.image.get_rect(center=(attack_x, attack_y))

                self.game.current_scene.effects.add(attack_sprite)

            player.take_damage(self.damage)
            print(f"{self.name} attacks {player.class_name} for {self.damage} damage!")
            self.is_attacking = False # Reset attack flag immediately after attack

    def take_damage(self, damage_amount):
        self.current_life -= damage_amount
        if self.current_life <= 0:
            self.current_life = 0
            self.die()

    def die(self):
        self.kill() # Remove sprite from all groups
        print(f"{self.name} has been defeated!")
        print(f"{self.name} dropped loot!")
        print(f"{self.game.current_scene.player.class_name} gained {self.xp_value} experience!")
        # Trigger loot drop, experience gain, etc.