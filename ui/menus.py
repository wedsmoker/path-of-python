import pygame
from core.scene_manager import BaseScene
from config import settings
from config.constants import STATE_GAMEPLAY, STATE_PAUSE_MENU, STATE_INVENTORY, STATE_SKILL_TREE
from core.utils import draw_text
from ui.settings_menu import SettingsMenu
from ui.button import Button

class PauseMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.recreate_ui()

    def recreate_ui(self):
        self.buttons.clear()
        button_width = 200
        button_height = 50
        start_y = settings.SCREEN_HEIGHT // 2 - 150
        spacing = 60

        self.buttons.append(Button(
            50, 50, button_width, button_height,
            "Return to Spawntown", lambda: self.game.scene_manager.set_scene("spawn_town")
        ))
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height,
            "Resume Game", lambda: self.game.scene_manager.set_scene(self.game.scene_manager.gameplay_scene_name)
        ))
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + spacing, button_width, button_height,
            "Inventory", lambda: self.game.scene_manager.set_scene(STATE_INVENTORY)
        ))
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * spacing, button_width, button_height,
            "Save / Load", lambda: self.game.scene_manager.set_scene("save_menu")
        ))
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + 3 * spacing, button_width, button_height,
            "Settings", lambda: self.game.scene_manager.set_scene("settings_menu")
        ))
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + 4 * spacing, button_width, button_height,
            "Exit Game", lambda: self.game.quit_game()
        ))
        self.buttons.append(Button(
            settings.SCREEN_WIDTH // 2 - button_width // 2, start_y + 5 * spacing, button_width, button_height,
            "Return to Title", lambda: self.game.scene_manager.set_scene("title_screen")
        ))

    def enter(self):
        self.game.logger.info("Entering Pause Menu.")
        self.recreate_ui()

    def exit(self):
        self.game.logger.info("Exiting Pause Menu.")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.buttons[1].action()
            return

        for button in self.buttons:
            if button.handle_event(event):
                break

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR)
        draw_text(screen, "PAUSED", settings.UI_FONT_SIZE_LARGE, settings.UI_PRIMARY_COLOR, settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4, align="center")
        for button in self.buttons:
            button.draw(screen)

    def reinitialize_fonts(self):
        self.game.logger.info("Reinitializing fonts for PauseMenu buttons.")
        self.recreate_ui()

class VolumeSettingsMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.volume = pygame.mixer.music.get_volume()
        self.dragging = False
        self.recreate_ui()

    def recreate_ui(self):
        self.slider_x = settings.SCREEN_WIDTH // 2 - 100
        self.slider_y = settings.SCREEN_HEIGHT // 2
        self.slider_width = 200
        self.slider_height = 20
        self.slider_rect = pygame.Rect(self.slider_x, self.slider_y, self.slider_width, self.slider_height)
        self.thumb_width = 10
        self.next_song_button = Button(
            settings.SCREEN_WIDTH // 2 + 120, settings.SCREEN_HEIGHT // 2 - 10, 100, 40,
            "Next Song", lambda: self.game.music_manager.play_random_song()
        )

    def enter(self):
        self.recreate_ui()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.slider_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x = event.pos[0]
                self.volume = (mouse_x - self.slider_x) / self.slider_width
                self.volume = max(0, min(1, self.volume))
                pygame.mixer.music.set_volume(self.volume)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.scene_manager.set_scene("settings_menu")
        self.next_song_button.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR)
        draw_text(screen, "Volume Settings", settings.UI_FONT_SIZE_LARGE, settings.UI_PRIMARY_COLOR, settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4, align="center")

        # Draw slider
        pygame.draw.rect(screen, settings.UI_SECONDARY_COLOR, self.slider_rect)
        # Draw thumb
        thumb_x = self.slider_x + int(self.volume * self.slider_width)
        thumb_rect = pygame.Rect(thumb_x - self.thumb_width // 2, self.slider_y, self.thumb_width, self.slider_height)
        pygame.draw.rect(screen, settings.UI_ACCENT_COLOR, thumb_rect)
        self.next_song_button.draw(screen)

    def reinitialize_fonts(self):
        self.game.logger.info("Reinitializing fonts for VolumeSettingsMenu buttons.")
        self.recreate_ui()

class CharacterStatsMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.recreate_ui()

    def recreate_ui(self):
        self.back_button = Button(
            settings.SCREEN_WIDTH // 2 - 100, settings.SCREEN_HEIGHT - 100, 200, 50,
            "Back", lambda: self.game.scene_manager.set_scene(STATE_PAUSE_MENU)
        )

    def enter(self):
        self.game.logger.info("Entering Character Stats Menu.")
        self.recreate_ui()

    def exit(self):
        self.game.logger.info("Exiting Character Stats Menu.")

    def handle_event(self, event):
        self.back_button.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR)
        draw_text(screen, "CHARACTER STATS", settings.UI_FONT_SIZE_LARGE, settings.UI_PRIMARY_COLOR, settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4, align="center")
        # Placeholder for drawing actual character stats
        draw_text(screen, "Life: XXX / XXX", settings.UI_FONT_SIZE_DEFAULT, settings.UI_PRIMARY_COLOR, settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 50, align="center")
        draw_text(screen, "Mana: XXX / XXX", settings.UI_FONT_SIZE_DEFAULT, settings.UI_PRIMARY_COLOR, settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2, align="center")
        draw_text(screen, "Energy Shield: XXX / XXX", settings.UI_FONT_SIZE_DEFAULT, settings.UI_PRIMARY_COLOR, settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 50, align="center")
        self.back_button.draw(screen)

    def reinitialize_fonts(self):
        self.game.logger.info("Reinitializing fonts for CharacterStatsMenu buttons.")
        self.recreate_ui()