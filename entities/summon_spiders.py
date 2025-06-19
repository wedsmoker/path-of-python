import math
import pygame
import os
import random
import json
from config.constants import TILE_SIZE
from entities.enemy import Enemy

class SummonSpiders:
    def __init__(self, player):
        self.player = player
        self.spider_image_paths = [
            "graphics/dc-mon/animals/jumping_spider.png",
            "graphics/dc-mon/animals/redback.png",
            "graphics/dc-mon/animals/tarantella.png",
            "graphics/dc-mon/animals/trapdoor_spider.png",
            "graphics/dc-mon/animals/wolf_spider.png"
        ]
        self.summon_range = 5 * TILE_SIZE  # Increased range for spiders
        self.max_spiders = 30
        self.spider_health = 15  # Low health
        self.spider_damage = 3
        self.spider_speed = 280 # Increased spider speed (70 * 4 = 280)
        self.last_used = 0
        self.cooldown = 10000  # 10 second cooldown
        self.mana_cost = 30
        self.summon_spread_radius = TILE_SIZE * 10 # Radius around player to spread spiders

        self._load_skill_data()

    def _load_skill_data(self):
        """Loads Summon Spiders skill data from skills.json."""
        skills_file_path = os.path.join(os.getcwd(), "data", "skills.json")
        try:
            with open(skills_file_path, 'r') as f:
                skills_data = json.load(f)

            summon_spiders_data = None
            for skill in skills_data.get("active_skills", []):
                if skill.get("id") == "summon_spiders":
                    summon_spiders_data = skill
                    break

            if summon_spiders_data:
                self.mana_cost = summon_spiders_data.get("mana_cost", 30)
                self.cooldown = summon_spiders_data.get("cooldown", 10.0) * 1000  # Convert to milliseconds
                self.max_spiders = summon_spiders_data.get("minion_count", 30)
                self.spider_health = summon_spiders_data.get("minion_health_multiplier", 0.5) * self.spider_health # Apply multiplier
                self.spider_damage = summon_spiders_data.get("minion_damage", 3)
                self.spider_speed = summon_spiders_data.get("minion_speed", 280) # Updated default minion_speed
                self.minion_attack_slow_duration = summon_spiders_data.get("minion_attack_slow_duration", 2.0)
                self.minion_attack_slow_amount = summon_spiders_data.get("minion_attack_slow_amount", 0.3)
                self.minion_poison_duration = summon_spiders_data.get("minion_poison_duration", 3.0)
                self.minion_poison_damage = summon_spiders_data.get("minion_poison_damage", {"min": 2, "max": 4, "type": "chaos"})
                print(f"Summon Spiders skill data loaded: mana_cost={self.mana_cost}, cooldown={self.cooldown}, max_spiders={self.max_spiders}, spider_health={self.spider_health}, spider_damage={self.spider_damage}, spider_speed={self.spider_speed}")
            else:
                print("Summon Spiders skill data not found in skills.json. Using default values.")
        except FileNotFoundError:
            print(f"Error: skills.json not found at {skills_file_path}. Using default Summon Spiders skill values.")
        except json.JSONDecodeError:
            print(f"Error decoding skills.json at {skills_file_path}. Using default Summon Spiders skill values.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def can_cast(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_used < self.cooldown:
            return False
        if not self.player.has_skill("summon_spiders"):
            return False
        if self.player.current_mana < self.mana_cost:
            return False
        return True

    def activate(self): # Removed target_x, target_y parameters
        current_time = pygame.time.get_ticks()
        if current_time - self.last_used < self.cooldown:
            print("Summon Spiders skill is on cooldown!")
            return False # Return False if on cooldown

        if not self.player.has_skill("summon_spiders"):
            print("Cannot activate Summon Spiders skill: Skill not unlocked!")
            return False

        if self.player.current_mana < self.mana_cost:
            print("Cannot activate Summon Spiders skill: Not enough mana!")
            return False

        # Deduct mana cost
        self.player.current_mana -= self.mana_cost
        self.last_used = current_time

        num_to_summon = self.max_spiders
        print(f"Attempting to summon {num_to_summon} spiders.")
        print(f"Summon Spiders: Player current mana: {self.player.current_mana}, Mana cost: {self.mana_cost}")
        print(f"Summon Spiders: Cooldown: {self.cooldown}, Last used: {self.last_used}, Current time: {current_time}")
        print(f"Summon Spiders: Player has skill 'summon_spiders': {self.player.has_skill('summon_spiders')}")

        player_world_x = self.player.rect.centerx
        player_world_y = self.player.rect.centery

        for _ in range(num_to_summon):
            # Generate random offsets within the summon_spread_radius around the player
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.summon_spread_radius)

            offset_x = distance * math.cos(angle)
            offset_y = distance * math.sin(angle)

            spawn_x = player_world_x + offset_x
            spawn_y = player_world_y + offset_y

            self._summon_spider(spawn_x, spawn_y)
        return True # Indicate successful activation

    def _summon_spider(self, x, y):
        """Summons a single spider at the specified location."""
        player_level = self.player.level
        scaled_health = self.spider_health + (player_level - 1) * 2  # Example scaling
        scaled_damage = self.spider_damage + (player_level - 1) * 0.5 # Example scaling
        scaled_speed = self.spider_speed + (player_level - 1) * 1 # Example scaling

        scaled_health = max(self.spider_health, scaled_health)
        scaled_damage = max(self.spider_damage, scaled_damage)
        scaled_speed = max(self.spider_speed, scaled_speed)

        # Randomly select a spider image path
        selected_sprite_path = random.choice(self.spider_image_paths)

        spider = Spider(self.player.game, x, y, scaled_health, scaled_damage, scaled_speed, selected_sprite_path, self, player_level,
                        self.minion_attack_slow_duration, self.minion_attack_slow_amount,
                        self.minion_poison_duration, self.minion_poison_damage)
        self.player.game.current_scene.friendly_entities.add(spider)
        self.player.game.current_scene.enemies.add(spider)  # Add spider to enemies group so they can be targeted
        print("Summoned a spider!")
        print(f"Summoned spider at world coordinates: ({x}, {y})")

    def remove_spider(self, spider):
        """Removes a spider from the active spiders list."""
        if spider in self.player.game.current_scene.friendly_entities:
            self.player.game.current_scene.friendly_entities.remove(spider)
            print(f"Removed a spider from active list. Current active: {len(self.player.game.current_scene.friendly_entities)}")

    def update(self, dt):
        """Updates the SummonSpiders skill's state, primarily handling cooldowns."""
        pass # Placeholder for now, can add more complex logic later if needed

class Spider(Enemy):
    def __init__(self, game, x, y, health, damage, speed, sprite_path, owner, player_level,
                 slow_duration, slow_amount, poison_duration, poison_damage):
        super().__init__(game, x, y, "Spider", health, damage, speed, sprite_path)
        self.player_level = player_level
        # Increased base scale factor for better visibility
        self.scale_factor = 2.0 + (self.player_level - 1) * 0.1 # Base scale 2.0, smaller increment

        original_image = pygame.image.load(os.path.join(os.getcwd(), sprite_path)).convert_alpha()
        new_width = int(original_image.get_width() * self.scale_factor)
        new_height = int(original_image.get_height() * self.scale_factor)
        self.image = pygame.transform.scale(original_image, (new_width, new_height))
        self.rect = self.image.get_rect(center=(x, y))
        self.owner = owner
        self.is_friendly = True
        self.faction = "player_minions"
        self.attack_range = TILE_SIZE * 1.0 # Melee range
        self.attack_cooldown = 750 # Faster attack cooldown
        self.last_attack_time = pygame.time.get_ticks()
        self.following_range = TILE_SIZE * 20
        self.enemy_finding_range = TILE_SIZE * 10 # Increased range to find enemies
        self.circle_angle = random.uniform(0, 2 * math.pi)
        self.circle_speed = random.uniform(1.0, 2.0) # Faster circling
        self.circle_radius = random.uniform(TILE_SIZE * 1.0, TILE_SIZE * 2.0) # Smaller circling radius

        self.slow_duration = slow_duration
        self.slow_amount = slow_amount
        self.poison_duration = poison_duration
        self.poison_damage = poison_damage

    def take_damage(self, amount):
        super().take_damage(amount)
        if self.current_life <= 0:
            if self.owner:
                self.owner.remove_spider(self)

    def update(self, dt, player, tile_map, tile_size):
        if not player:
            return

        current_time = pygame.time.get_ticks()

        nearest_enemy = self._find_nearest_enemy(player, self.enemy_finding_range)

        if nearest_enemy:
            dx, dy = nearest_enemy.rect.centerx - self.rect.centerx, nearest_enemy.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)

            if dist <= self.attack_range and current_time - self.last_attack_time > self.attack_cooldown:
                nearest_enemy.take_damage(self.damage)
                # Apply slow
                nearest_enemy.apply_slow(self.slow_amount, self.slow_duration)
                # Apply poison
                nearest_enemy.apply_poison(self.poison_damage["min"], self.poison_duration) # Corrected to use min damage for poison
                self.last_attack_time = current_time
                print(f"Spider attacked {nearest_enemy.name} for {self.damage} damage, applied slow and poison.")
            elif dist > 0:
                dx, dy = dx / dist, dy / dist
                move_x = dx * self.speed * dt
                move_y = dy * self.speed * dt # Corrected typo here

                original_x, original_y = self.rect.x, self.rect.y

                self.rect.x += move_x
                if self._check_collision(tile_map, tile_size):
                    self.rect.x = original_x

                self.rect.y += move_y
                if self._check_collision(tile_map, tile_size):
                    self.rect.y = original_y
        else:
            dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)

            if dist > 0 and dist < self.following_range:
                self._circle_around_player(dt, player, tile_map, tile_size)

    def _find_nearest_enemy(self, player, finding_range):
        nearest_enemy = None
        min_distance = float('inf')

        for sprite in self.game.current_scene.enemies:
            if isinstance(sprite, Enemy) and not isinstance(sprite, Spider):
                dx, dy = sprite.rect.centerx - self.rect.centerx, sprite.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)

                if dist < min_distance and dist <= finding_range:
                    min_distance = dist
                    nearest_enemy = sprite
        return nearest_enemy

    def _check_collision(self, tile_map, tile_size):
        enemy_left_tile = int(self.rect.left / tile_size)
        enemy_right_tile = int(self.rect.right / tile_size)
        enemy_top_tile = int(self.rect.top / tile_size)
        enemy_bottom_tile = int(self.rect.bottom / tile_size)

        map_width_tiles = len(tile_map[0])
        map_height_tiles = len(tile_map)

        enemy_left_tile = max(0, min(enemy_left_tile, map_width_tiles - 1))
        enemy_right_tile = max(0, min(enemy_right_tile, map_width_tiles - 1))
        enemy_top_tile = max(0, min(enemy_top_tile, map_height_tiles - 1))
        enemy_bottom_tile = max(0, min(enemy_bottom_tile, map_height_tiles - 1))

        for y in range(enemy_top_tile, enemy_bottom_tile + 1):
            for x in range(enemy_left_tile, enemy_right_tile + 1):
                if 0 <= y < map_height_tiles and 0 <= x < map_width_tiles:
                    tile_type = tile_map[y][x]
                    if tile_type == 'wall':
                        return True
        return False

    def _circle_around_player(self, dt, player, tile_map, tile_size):
        self.circle_angle += self.circle_speed * dt
        if self.circle_angle > 2 * math.pi:
            self.circle_angle -= 2 * math.pi

        offset_x = math.cos(self.circle_angle) * self.circle_radius + math.sin(2 * self.circle_angle) * self.circle_radius * 0.3
        offset_y = math.sin(self.circle_angle) * self.circle_radius + math.cos(2 * self.circle_angle) * self.circle_radius * 0.3

        new_x = player.rect.centerx + offset_x
        new_y = player.rect.centery + offset_y

        original_x, original_y = self.rect.x, self.rect.y

        self.rect.x = new_x - self.rect.width / 2
        if self._check_collision(tile_map, tile_size):
            self.rect.x = original_x

        self.rect.y = new_y - self.rect.height / 2
        if self._check_collision(tile_map, tile_size):
            self.rect.y = original_y