import pygame
from core.scene_manager import BaseScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT, UI_FONT_SIZE_LARGE, UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, UI_SECONDARY_COLOR, UI_BACKGROUND_COLOR, UI_ACCENT_COLOR
from config.constants import STATE_GAMEPLAY, STATE_PAUSE_MENU, STATE_SETTINGS_MENU, STATE_INVENTORY, STATE_SKILL_TREE
from core.utils import draw_text

class PauseMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self._setup_buttons()

    def _setup_buttons(self):
        button_width = 200
        button_height = 50
        start_y = SCREEN_HEIGHT // 2 - 150
        spacing = 60

        self.buttons.append(Button(
            50, 50, button_width, button_height,
            "Return to Spawntown", lambda: self.game.scene_manager.set_scene("spawn_town", self.game.spawn_town.player)
        ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height,
            "Resume Game", lambda: self.game.scene_manager.set_scene(self.game.scene_manager.previous_scene_name, self.game.player, self.game.hud)
        ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2, start_y + spacing, button_width, button_height,
            "Inventory", lambda: self.game.scene_manager.set_scene(STATE_INVENTORY, self.game.spawn_town.player)
        ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * spacing, button_width, button_height,
            "Skill Tree", lambda: self.game.scene_manager.set_scene(STATE_SKILL_TREE, self.game.spawn_town.player)
        ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2, start_y + 3 * spacing, button_width, button_height,
            "Settings", lambda: self.game.scene_manager.set_scene(STATE_SETTINGS_MENU, self.game.spawn_town.player)
        ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2, start_y + 4 * spacing, button_width, button_height,
            "Exit Game", lambda: self.game.quit_game()
        ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2, start_y + 5 * spacing, button_width, button_height,
            "Return to Title", lambda: self.game.scene_manager.set_scene("title_screen")
        ))

    def enter(self):
        self.game.logger.info("Entering Pause Menu.")

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
        screen.fill(UI_BACKGROUND_COLOR)
        draw_text(screen, "PAUSED", UI_FONT_SIZE_LARGE, UI_PRIMARY_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, align="center")
        for button in self.buttons:
            button.draw(screen)

class SettingsMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self._setup_buttons()

    def _setup_buttons(self):
        button_width = 250
        button_height = 50
        start_y = SCREEN_HEIGHT // 2 - 100
        spacing = 60

        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height,
            "Toggle Fullscreen", lambda: self._toggle_fullscreen()
        ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2, start_y + spacing, button_width, button_height,
            "Toggle Debug Mode", lambda: self._toggle_debug_mode()
        ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * spacing, button_width, button_height,
            "Volume Settings", lambda: self.game.scene_manager.set_scene("volume_settings", self.game.spawn_town.player)
        ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2, start_y + 3 * spacing, button_width, button_height,
            "Back to Pause Menu", lambda: self.game.scene_manager.set_scene("pause_menu", self.game.spawn_town.player)
        ))

    def _toggle_fullscreen(self):
        self.game.settings.FULLSCREEN = not self.game.settings.FULLSCREEN
        self.game.apply_display_settings() # Assuming GameEngine has this method
        self.game.logger.info(f"Fullscreen: {self.game.settings.FULLSCREEN}")

    def _toggle_debug_mode(self):
        self.game.settings.DEBUG_MODE = not self.game.settings.DEBUG_MODE
        self.game.logger.info(f"Debug Mode: {self.game.settings.DEBUG_MODE}")

    def enter(self):
        self.game.logger.info("Entering Settings Menu.")

    def exit(self):
        self.game.logger.info("Exiting Settings Menu.")

    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                break

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(UI_BACKGROUND_COLOR)
        draw_text(screen, "SETTINGS", UI_FONT_SIZE_LARGE, UI_PRIMARY_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, align="center")
        for button in self.buttons:
            button.draw(screen)

class VolumeSettingsMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.volume = pygame.mixer.music.get_volume()
        self.slider_x = SCREEN_WIDTH // 2 - 100
        self.slider_y = SCREEN_HEIGHT // 2
        self.slider_width = 200
        self.slider_height = 20
        self.slider_rect = pygame.Rect(self.slider_x, self.slider_y, self.slider_width, self.slider_height)
        self.thumb_width = 10
        self.dragging = False
        self.next_song_button = Button(
            SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 2 - 10, 100, 40,
            "Next Song", lambda: self.game.spawn_town.next_song()
        )

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
            self.game.scene_manager.set_scene(STATE_SETTINGS_MENU, self.game.spawn_town.player)
        self.next_song_button.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(UI_BACKGROUND_COLOR)
        draw_text(screen, "Volume Settings", UI_FONT_SIZE_LARGE, UI_PRIMARY_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, align="center")

        # Draw slider
        pygame.draw.rect(screen, UI_SECONDARY_COLOR, self.slider_rect)
        # Draw thumb
        thumb_x = self.slider_x + int(self.volume * self.slider_width)
        thumb_rect = pygame.Rect(thumb_x - self.thumb_width // 2, self.slider_y, self.thumb_width, self.slider_height)
        pygame.draw.rect(screen, UI_ACCENT_COLOR, thumb_rect)
        self.next_song_button.draw(screen)

class CharacterStatsMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.back_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50,
            "Back", lambda: self.game.scene_manager.set_scene(STATE_PAUSE_MENU, self.game.spawn_town.player) # Or previous scene
        )

    def enter(self):
        self.game.logger.info("Entering Character Stats Menu.")

    def exit(self):
        self.game.logger.info("Exiting Character Stats Menu.")

    def handle_event(self, event):
        self.back_button.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(UI_BACKGROUND_COLOR)
        draw_text(screen, "CHARACTER STATS", UI_FONT_SIZE_LARGE, UI_PRIMARY_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, align="center")
        # Placeholder for drawing actual character stats
        draw_text(screen, "Life: XXX / XXX", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, align="center")
        draw_text(screen, "Mana: XXX / XXX", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, align="center")
        draw_text(screen, "Energy Shield: XXX / XXX", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, align="center")
        self.back_button.draw(screen)

class Button:
    def __init__(self, x, y, width, height, text, action, font_size=UI_FONT_SIZE_DEFAULT, color=UI_PRIMARY_COLOR, bg_color=UI_SECONDARY_COLOR, hover_color=UI_ACCENT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = pygame.font.SysFont(UI_FONT, font_size)
        self.color = color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        current_bg_color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, current_bg_color, self.rect)
        pygame.draw.rect(surface, self.color, self.rect, 2) # Border

        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.action()
                return True
        return False