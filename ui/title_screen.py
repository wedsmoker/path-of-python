import pygame
from core.scene_manager import BaseScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT, UI_FONT_SIZE_LARGE, UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, UI_SECONDARY_COLOR, UI_BACKGROUND_COLOR, UI_ACCENT_COLOR
from core.spawn_town import SpawnTown
from core.utils import draw_text
import random
import math
from ui.menus import Button

class TitleScreen(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("Courier New", UI_FONT_SIZE_LARGE * 2)
        self.start_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50,
            "Start Game", lambda: self.game.scene_manager.set_scene("spawn_town")
        )
        self.info_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120, 200, 50,
            "Info", lambda: self.game.scene_manager.set_scene("info_screen")
        )
        self.dungeon_maker_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 190, 200, 50,
            "Dungeon Maker", self.open_dungeon_generator
        )
        self.animation_frame = 0
        self.image_index = 0
        self.alpha = 0
        self.alpha_direction = 1
        self.x_offset = 0

    def open_dungeon_generator(self):
        try:
            from ui.dungeon_generator_gui import DungeonGeneratorGUI
            dungeon_generator = DungeonGeneratorGUI(self.game)
            dungeon_generator.run()
        except ImportError as e:
            self.game.logger.error(f"Failed to open dungeon generator: {e}")
        except Exception as e:
            self.game.logger.error(f"Error in dungeon generator: {e}")

    def enter(self):
        self.game.logger.info("Entering Title Screen.")

    def exit(self):
        self.game.logger.info("Exiting Title Screen.")

    def handle_event(self, event):
        self.start_button.handle_event(event)
        self.info_button.handle_event(event)
        self.dungeon_maker_button.handle_event(event)

    def update(self, dt):
        self.animation_frame += 0.001
        if self.animation_frame > 120:
            self.animation_frame = 0

        self.x_offset += 0.1
        if self.x_offset > SCREEN_WIDTH:
            self.x_offset = 0

    def draw(self, screen):
        screen.fill(UI_BACKGROUND_COLOR)

        # Load background images
        self.background_images = [
            pygame.image.load("graphics/dc-dngn/dngn_blood_fountain.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_blood_fountain2.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_blue_fountain.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_blue_fountain2.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_sparkling_fountain.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_sparkling_fountain2.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/crumbled_column.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_orcish_idol.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/elephant_statue.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/granite_stump.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/zot_pillar.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_closed_door.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_open_door.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_trap_arrow.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_trap_axe.png").convert_alpha(),
            pygame.image.load("graphics/dc-dngn/dngn_trap_blade.png").convert_alpha()
        ]

        # Draw the background images with a parallax effect
        num_vertical_repeats = 50
        for j in range(num_vertical_repeats):
            # Create a unique list of images for each layer
            layer_images = random.sample(self.background_images, len(self.background_images))
            x_start = 0
            while x_start < SCREEN_WIDTH:
                for i, image in enumerate(layer_images):
                    # Scale the image
                    image = pygame.transform.scale(image, (image.get_width() * 5, image.get_height() * 5))
                    x = int(x_start - self.x_offset)
                    y = j * image.get_height() - SCREEN_HEIGHT // 2
                    screen.blit(image, (x, y))
                    x_start += image.get_width()

        # Load the title image
        title_image = pygame.image.load("graphics/title.png").convert_alpha()
        title_rect = title_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title_image, title_rect)

        self.start_button.draw(screen)
        self.info_button.draw(screen)
        self.dungeon_maker_button.draw(screen)

class InfoScreen(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.text_color = UI_PRIMARY_COLOR
        self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE_DEFAULT)
        self.info_text = [
            "Path of Python",
            "A post-apocalyptic ARPG",
            "Developed by a mysterious person",
            "",
            "Unravel the story of humanity's fall",
            "and the AI's rise.",
            "",
            "Inspired by Path of Exile.",
        ]
        self.back_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50,
            "Back", lambda: self.game.scene_manager.set_scene("title_screen")
        )

    def enter(self):
        self.game.logger.info("Entering Info Screen.")

    def exit(self):
        self.game.logger.info("Exiting Info Screen.")

    def handle_event(self, event):
        self.back_button.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(UI_BACKGROUND_COLOR)
        y_offset = SCREEN_HEIGHT // 4
        for line in self.info_text:
            text_surface = self.font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 30
        self.back_button.draw(screen)