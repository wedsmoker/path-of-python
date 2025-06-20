import pygame
import json
import os
from core.scene_manager import BaseScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT, UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, UI_BACKGROUND_COLOR
from ui.menus import Button

class SaveMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.text_color = UI_PRIMARY_COLOR
        self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE_DEFAULT)
        self.back_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50,
            "Back", self.go_back
        )
        self.save_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50,
            "Save Game", self.save_game
        )
        self.load_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50,
            "Load Game", self.load_game
        )
        self.save_files = self.load_save_files()
        self.selected_save = None
        self.previous_scene_name = None

    def enter(self):
        self.game.logger.info("Entering Save Menu.")
        self.previous_scene_name = self.game.scene_manager.current_scene_name

    def exit(self):
        self.game.logger.info("Exiting Save Menu.")

    def handle_event(self, event):
        self.back_button.handle_event(event)
        self.save_button.handle_event(event)
        self.load_button.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, save_file in enumerate(self.save_files):
                save_rect = pygame.Rect(50, 100 + i * 30, 200, 30)
                if save_rect.collidepoint(mouse_pos):
                    self.selected_save = save_file
                    print(f"Selected save: {self.selected_save}") # Debugging

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(UI_BACKGROUND_COLOR)
        text_surface = self.font.render("Save Menu", True, self.text_color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 100))
        screen.blit(text_surface, text_rect)
        self.back_button.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)

        # Draw save list
        for i, save_file in enumerate(self.save_files):
            text_color = (0, 255, 0) if save_file == self.selected_save else self.text_color
            save_surface = self.font.render(save_file, True, text_color)
            save_rect = save_surface.get_rect(topleft=(50, 100 + i * 30))
            screen.blit(save_surface, save_rect)

    def save_game(self):
        player = self.game.player
        save_data = {
            "class": player.class_name,
            "stats": player.stats,
            "skills": player.skills,
            "level": player.level,
            "x": player.rect.x,
            "y": player.rect.y
        }
        
        # Determine the next available save slot
        save_number = 1
        while os.path.exists(os.path.join("saves", f"save_{save_number}.json")):
            save_number += 1

        filename = f"save_{save_number}.json"
        filepath = os.path.join("saves", filename)
        with open(filepath, "w") as f:
            json.dump(save_data, f)
        self.game.logger.info(f"Game saved to {filepath}")

    def load_game(self):
        if self.selected_save:
            filepath = os.path.join("saves", self.selected_save)
            with open(filepath, "r") as f:
                save_data = json.load(f)

            player = self.game.player
            class_name = save_data["class"]
            class_data = self.game.scene_manager.scenes["character_selection"].classes[class_name] # Access class data from character selection scene
            player.set_class(class_name, class_data.get("stats", {}))

            player.apply_stats(save_data["stats"])
            player.skills = save_data["skills"]
            player.level = save_data["level"]
            player.rect.x = save_data["x"]
            player.rect.y = save_data["y"]

            # Ensure current life, mana, energy shield are capped at max
            player.current_life = min(player.current_life, player.max_life)
            player.current_mana = min(player.current_mana, player.max_mana)
            player.current_energy_shield = min(player.current_energy_shield, player.max_energy_shield)

            self.game.scene_manager.set_scene("spawn_town")
            self.game.logger.info(f"Game loaded from {filepath}")
        else:
            print("No save selected")

    def load_save_files(self):
        save_files = []
        for filename in os.listdir("saves"):
            if filename.startswith("save_") and filename.endswith(".json"):
                save_files.append(filename)
        return save_files

    def go_back(self):
        self.game.scene_manager.set_scene(self.previous_scene_name)