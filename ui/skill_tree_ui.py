import pygame
from core.scene_manager import BaseScene
from config import settings
from config.constants import KEY_SKILL_TREE
from core.utils import draw_text
import json
import os

class SkillTreeUI(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.skill_tree_data = self.load_skill_tree_data()
        self.skill_rects = {} # Dictionary to store skill rects, keyed by skill ID
        self.grid_size_x = 250 # Width of each grid cell
        self.grid_size_y = 100 # Height of each grid cell
        self.unlocking_skill = False # Flag to prevent multiple unlocks
        self.scroll_y = 0 # Initial scroll offset
        self.max_scroll = 0 # Maximum scroll offset

    def load_skill_tree_data(self):
        skill_tree_path = os.path.join(os.getcwd(), "data", "skill_tree.json")
        try:
            with open(skill_tree_path, "r") as f:
                skill_tree_data = json.load(f)
            return skill_tree_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.game.logger.error(f"Error loading skill tree data: {e}")
            return {"skills": []}

    def enter(self):
        self.game.logger.info("Entering Skill Tree UI.")

    def exit(self):
        self.game.logger.info("Exiting Skill Tree UI.")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == KEY_SKILL_TREE:
                self.game.scene_manager.set_scene("pause_menu", self.game.spawn_town.player)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.unlocking_skill:
            # Check for skill click
            for skill_id, rect in self.skill_rects.items():
                if rect.collidepoint(event.pos):
                    self.attempt_skill_unlock(skill_id)
                    break
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * 10 # Adjust scroll speed as needed
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll)) # Clamp scroll value

    def attempt_skill_unlock(self, skill_id):
        self.unlocking_skill = True # Set the flag
        skill = next((s for s in self.skill_tree_data["skills"] if s["id"] == skill_id), None)
        player = self.game.spawn_town.player

        if player.skill_points >= skill["cost"]:
            # Check dependencies
            can_unlock = True
            for dependency in skill["dependencies"]:
                if dependency not in player.unlocked_skills:
                    can_unlock = False
                    break

            if can_unlock:
                player.skill_points -= skill["cost"]
                player.unlocked_skills.append(skill["id"])
                self.apply_skill_effects(player, skill)
                print(f"Unlocked skill: {skill['name']}")
            else:
                print(f"Cannot unlock skill: {skill['name']} (missing dependencies)")
        else:
            print(f"Not enough skill points to unlock: {skill['name']}")
        self.unlocking_skill = False # Clear the flag

    def apply_skill_effects(self, player, skill):
        if "stat" in skill:
            player.stats[skill["stat"]] = player.stats.get(skill["stat"], 0) + skill["amount"]
            # Update the actual attribute as well
            setattr(player, skill["stat"], player.stats[skill["stat"]])
        if "stat2" in skill:
            player.stats[skill["stat2"]] = player.stats.get(skill["stat2"], 0) + skill["amount2"]
            # Update the actual attribute as well
            setattr(player, skill["stat2"], player.stats[skill["stat2"]])

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR)
        draw_text(screen, "Skill Tree", settings.UI_FONT_SIZE_LARGE, settings.UI_PRIMARY_COLOR, settings.SCREEN_WIDTH // 2, 50, align="center")
        draw_text(screen, f"Skill Points: {self.game.spawn_town.player.skill_points}", settings.UI_FONT_SIZE_DEFAULT, settings.UI_PRIMARY_COLOR, settings.SCREEN_WIDTH // 2, 100, align="center")

        # Grid layout
        start_x = settings.SCREEN_WIDTH // 4
        start_y = 150 # Start below the header
        x_offset = 0
        y_offset = 0
        skill_index = 0
        self.skill_rects = {} # Clear skill rects

        for skill in self.skill_tree_data["skills"]:
            # Calculate position
            x = start_x + x_offset * self.grid_size_x
            y = start_y + y_offset * self.grid_size_y - self.scroll_y # Apply scroll offset

            # Determine color based on unlock status and availability
            if skill["id"] in self.game.spawn_town.player.unlocked_skills:
                color = (0, 255, 0) # Green for unlocked
            elif self.can_unlock_skill(skill):
                color = (255, 255, 255) # White for unlockable
            else:
                color = (100, 100, 100) # Gray for unavailable

            # Draw background rectangle
            skill_name_text = skill["name"] # Get skill name
            font_size = settings.UI_FONT_SIZE_DEFAULT + 4 # Reduce font size
            font_name = pygame.font.match_font('arial') # Fallback font
            font = pygame.font.Font(font_name, font_size)
            text_surface = font.render(skill_name_text, True, color)
            skill_rect = text_surface.get_rect(center=(x, y))
            bg_rect = skill_rect.inflate(20, 10) # Inflate the rect for padding
            pygame.draw.rect(screen, settings.UI_BACKGROUND_COLOR, bg_rect)

            # Draw skill name again, on top of the background
            draw_text(screen, skill_name_text, settings.UI_FONT_SIZE_DEFAULT + 4, color, x, y, align="center")

            self.skill_rects[skill["id"]] = skill_rect # Store the rect, keyed by skill ID

            # Increment offsets for next skill
            x_offset += 1
            if x_offset > 4: # 5 skills per row
                x_offset = 0
                y_offset += 1

            skill_index += 1

        # Calculate max scroll
        num_rows = (len(self.skill_tree_data["skills"]) + 4) // 5 # Calculate number of rows
        grid_height = num_rows * self.grid_size_y
        self.max_scroll = max(0, grid_height - (settings.SCREEN_HEIGHT - 150)) # 150 is the header height

    def can_unlock_skill(self, skill):
        player = self.game.spawn_town.player
        if player.skill_points < skill["cost"]:
            return False
        for dependency in skill["dependencies"]:
            if dependency not in player.unlocked_skills:
                return False
        return True