import pygame
from config.settings import SCREEN_WIDTH
from config.settings import SCREEN_HEIGHT
from config.settings import UI_FONT
from config.settings import UI_FONT_SIZE_DEFAULT
from config.settings import UI_PRIMARY_COLOR
from config.settings import UI_SECONDARY_COLOR
from config.settings import RED
from config.settings import BLUE
from config.settings import GREEN
from config.settings import UI_BACKGROUND_COLOR
from config.constants import KEY_SKILL_1, KEY_SKILL_2, KEY_SKILL_3, KEY_SKILL_4, KEY_POTION_1, KEY_POTION_2, KEY_POTION_3, KEY_POTION_4
from core.utils import draw_text
from ui.minimap import Minimap
import json
import os

class HUD:
    def __init__(self, player, scene):
        self.player = player
        self.minimap = Minimap(self.player, [], scene) # Initialize with an empty entity list for now
        self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE_DEFAULT)
        self.skill_tree_data = self.load_skill_tree_data()

    def load_skill_tree_data(self):
        skill_tree_path = os.path.join(os.getcwd(), "data", "skill_tree.json")
        try:
            with open(skill_tree_path, "r") as f:
                skill_tree_data = json.load(f)
            return skill_tree_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading skill tree data: {e}")
            return {"skills": []}

    def update(self, dt, entities):
        self.minimap.update(entities)

    def draw(self, screen):
        # Draw Health Bar
        self._draw_bar(screen, 10, SCREEN_HEIGHT - 40, 200, 20, self.player.current_life, self.player.max_life, RED, "HP")

        # Draw Energy Shield Bar
        self._draw_bar(screen, 10, SCREEN_HEIGHT - 65, 200, 20, self.player.current_energy_shield, self.player.max_energy_shield, BLUE, "ES")

        # Draw Mana Bar
        self._draw_bar(screen, 10, SCREEN_HEIGHT - 90, 200, 20, self.player.current_mana, self.player.max_mana, GREEN, "MP")

        # Draw Skill Bar (Placeholder)
        self._draw_skill_bar(screen)

        # Draw Potion Slots (Placeholder)
        self._draw_potion_slots(screen)

        # Draw Minimap
        self.minimap.draw(screen)
        # Draw Level/Experience Gauge
        self._draw_experience_gauge(screen)

    def _draw_bar(self, screen, x, y, width, height, current_value, max_value, color, label):
        # Background bar
        pygame.draw.rect(screen, UI_BACKGROUND_COLOR, (x, y, width, height))
        # Foreground bar
        if max_value > 0:
            fill_width = (current_value / max_value) * width
            pygame.draw.rect(screen, color, (x, y, fill_width, height))
        # Border
        pygame.draw.rect(screen, UI_PRIMARY_COLOR, (x, y, width, height), 2)
        # Text
        text = f"{label}: {int(current_value)}/{int(max_value)}"
        draw_text(screen, text, UI_FONT_SIZE_DEFAULT - 4, UI_PRIMARY_COLOR, x + width // 2, y + height // 2, align="center")

    def _draw_skill_bar(self, screen):
        bar_x = SCREEN_WIDTH - 250  # Position on the right
        bar_y = SCREEN_HEIGHT - 100  # Position at the bottom
        slot_size = 50
        spacing = 10

        #draw_text(screen, "Skills:", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, bar_x - 60, bar_y + slot_size // 2, align="midright")

        for i, skill_id in enumerate(self.player.skills):
            slot_rect = pygame.Rect(bar_x + i * (slot_size + spacing), bar_y, slot_size, slot_size)
            pygame.draw.rect(screen, UI_SECONDARY_COLOR, slot_rect)
            pygame.draw.rect(screen, UI_PRIMARY_COLOR, slot_rect, 2)
            # Display key binding for skill slot
            skill_keys = [KEY_SKILL_1, KEY_SKILL_2, KEY_SKILL_3, KEY_SKILL_4]
            #key_name = pygame.key.name(skill_keys[i]).upper()
            #draw_text(screen, key_name, UI_FONT_SIZE_DEFAULT - 8, UI_PRIMARY_COLOR, slot_rect.centerx, slot_rect.centery, align="center")
            skill = next((s for s in self.skill_tree_data["skills"] if s["id"] == skill_id), None)
            if skill:
                draw_text(screen, skill["name"], UI_FONT_SIZE_DEFAULT - 8, UI_PRIMARY_COLOR, slot_rect.centerx, slot_rect.centery, align="center")
            else:
                draw_text(screen, "None", UI_FONT_SIZE_DEFAULT - 8, UI_PRIMARY_COLOR, slot_rect.centerx, slot_rect.centery, align="center")

    def _draw_potion_slots(self, screen):
        bar_x = SCREEN_WIDTH // 2 + 100
        bar_y = SCREEN_HEIGHT - 50
        slot_size = 40
        spacing = 10

        draw_text(screen, "Potions:", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, bar_x - 60, bar_y + slot_size // 2, align="midright")

        for i in range(4):
            slot_rect = pygame.Rect(bar_x + i * (slot_size + spacing), bar_y, slot_size, slot_size)
            pygame.draw.rect(screen, UI_SECONDARY_COLOR, slot_rect)
            pygame.draw.rect(screen, UI_PRIMARY_COLOR, slot_rect, 2)
            # Display key binding for potion slot
            potion_keys = [KEY_POTION_1, KEY_POTION_2, KEY_POTION_3, KEY_POTION_4]
            key_name = pygame.key.name(potion_keys[i]).upper()
            draw_text(screen, key_name, UI_FONT_SIZE_DEFAULT - 8, UI_PRIMARY_COLOR, slot_rect.centerx, slot_rect.centery, align="center")

    def _draw_experience_gauge(self, screen):
        gauge_x = SCREEN_WIDTH // 2 - 150 # Centered at the top
        gauge_y = 10
        gauge_width = 300
        gauge_height = 25

        # Background bar
        pygame.draw.rect(screen, UI_BACKGROUND_COLOR, (gauge_x, gauge_y, gauge_width, gauge_height))

        # Calculate XP for next level
        xp_for_next_level = self.player.level * 100
        
        # Foreground bar
        if xp_for_next_level > 0:
            fill_width = (self.player.experience / xp_for_next_level) * gauge_width
            pygame.draw.rect(screen, (0, 200, 255), (gauge_x, gauge_y, fill_width, gauge_height)) # Light blue for XP

        # Border
        pygame.draw.rect(screen, UI_PRIMARY_COLOR, (gauge_x, gauge_y, gauge_width, gauge_height), 2)

        # Text: Level and XP
        xp_remaining = xp_for_next_level - self.player.experience
        text = f"Level: {self.player.level} | XP: {int(self.player.experience)}/{int(xp_for_next_level)} ({int(xp_remaining)} left)"
        draw_text(screen, text, UI_FONT_SIZE_DEFAULT - 4, UI_PRIMARY_COLOR, gauge_x + gauge_width // 2, gauge_y + gauge_height // 2, align="center")