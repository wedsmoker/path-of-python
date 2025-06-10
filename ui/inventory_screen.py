import pygame
from core.scene_manager import BaseScene
from config import settings
from core.utils import draw_text
from config.constants import STATE_GAMEPLAY, KEY_INVENTORY

class InventoryScreen(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(None, settings.UI_FONT_SIZE_LARGE)
        self.text_font = pygame.font.Font(None, settings.UI_FONT_SIZE_DEFAULT)

    def enter(self):
        self.game.logger.info("Entering Inventory Screen.")

    def exit(self):
        self.game.logger.info("Exiting Inventory Screen.")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == KEY_INVENTORY:
                self.game.scene_manager.set_scene("pause_menu", self.game.spawn_town.player)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR)
        draw_text(screen, "Inventory Screen", settings.UI_FONT_SIZE_LARGE, settings.UI_PRIMARY_COLOR,
                  settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 50, align="center")
        draw_text(screen, f"Press '{pygame.key.name(KEY_INVENTORY).upper()}' to return to game", settings.UI_FONT_SIZE_SMALL, settings.UI_SECONDARY_COLOR,
                  settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 20, align="center")