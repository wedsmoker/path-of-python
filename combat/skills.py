import pygame
from entities.projectile import Projectile
from config.constants import PROJECTILE_SPEED

class Skill:
    def __init__(self, name, mana_cost, cooldown, tags=None):
        self.name = name
        self.mana_cost = mana_cost
        self.cooldown = cooldown # in seconds
        self.current_cooldown = 0.0
        self.tags = tags if tags is not None else []

    def can_use(self, user):
        return user.current_mana >= self.mana_cost and self.current_cooldown <= 0

    def use(self, user, target_pos=None):
        if self.can_use(user):
            user.current_mana -= self.mana_cost
            self.current_cooldown = self.cooldown
            self._execute_skill(user, target_pos)
            return True
        return False

    def _execute_skill(self, user, target_pos):
        """Abstract method to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _execute_skill method.")

    def update(self, dt):
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
            if self.current_cooldown < 0:
                self.current_cooldown = 0

class AttackSkill(Skill):
    def __init__(self, name, mana_cost, cooldown, base_damage, attack_type="physical"):
        super().__init__(name, mana_cost, cooldown, tags=["attack"])
        self.base_damage = base_damage
        self.attack_type = attack_type

    def _execute_skill(self, user, target_pos):
        # For a simple attack, we might just deal damage directly or spawn a melee hitbox
        # For now, let's just print a message
        print(f"{user.name} uses {self.name}!")
        # In a real implementation, this would involve collision detection with enemies
        # and applying damage based on user's stats and skill's base_damage.

class SpellSkill(Skill):
    def __init__(self, name, mana_cost, cooldown, base_damage, damage_type="fire", projectile_speed=PROJECTILE_SPEED):
        super().__init__(name, mana_cost, cooldown, tags=["spell"])
        self.base_damage = base_damage
        self.damage_type = damage_type
        self.projectile_speed = projectile_speed

    def _execute_skill(self, user, target_pos):
        if target_pos:
            # Assuming game engine has a way to add projectiles to the active scene
            # This will need to be passed down from GameEngine -> GameplayScene
            # For now, we'll just create the projectile object.
            projectile = Projectile(user.rect.centerx, user.rect.centery,
                                    target_pos[0], target_pos[1],
                                    self.projectile_speed, self.base_damage, (255, 0, 0)) # Red projectile
            print(f"{user.name} casts {self.name}, launching a projectile!")
            # The game engine/scene will need to add this projectile to its sprite groups
            # self.game.current_scene.add_projectile(projectile) # Example of how it might work
        else:
            print(f"{user.name} casts {self.name} without a target!")

# Example skills
# fireball = SpellSkill("Fireball", 10, 1.5, 20, "fire")
# basic_attack = AttackSkill("Basic Attack", 0, 0.5, {"min": 5, "max": 10})

class Teleport(Skill):
    def __init__(self):
        super().__init__("Teleport", 20, 5, tags=["movement"])  # Example values: name, mana_cost, cooldown
        self.range = 900  # Teleport range in pixels

    def _execute_skill(self, user, target_pos):
        # Calculate the distance between the player and the target
        if target_pos is None:
            return  # No target position, can't teleport

        distance = ((target_pos[0] - user.rect.centerx) ** 2 + (target_pos[1] - user.rect.centery) ** 2) ** 0.5

        # If the distance is greater than the teleport range, limit the teleport distance
        if distance > self.range:
            # Calculate the angle between the player and the target
            angle = pygame.math.Vector2(target_pos[0] - user.rect.centerx, target_pos[1] - user.rect.centery).angle_to(pygame.math.Vector2(1, 0))

            # Calculate the teleport coordinates based on the angle and the teleport range
            teleport_x = user.rect.centerx + self.range * pygame.math.Vector2(1, 0).rotate(-angle).x
            teleport_y = user.rect.centery + self.range * pygame.math.Vector2(1, 0).rotate(-angle).y
        else:
            teleport_x = target_pos[0]
            teleport_y = target_pos[1]

        # Perform the teleport
        user.rect.centerx = teleport_x
        user.rect.centery = teleport_y
        print("Teleport skill used!")