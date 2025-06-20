import pygame
import sys
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
            "Start Game", lambda: self.game.scene_manager.set_scene("character_selection")  # Changed to intro_scene
        )
        self.info_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 110, 200, 50,
            "Info", lambda: self.game.scene_manager.set_scene("info_screen")
        )
        self.load_character_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 170, 200, 50,
            "Load Game", lambda: self.game.scene_manager.set_scene("save_menu")
        )
        self.dungeon_maker_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 230, 200, 50,
            "Dungeon Maker", self.open_dungeon_generator
        )
        self.exit_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 290, 200, 50,
            "Exit Game", lambda: (pygame.quit(), sys.exit())
        )
        self.volume_slider = VolumeSlider(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 150, 200, 20,
            pygame.mixer.music.get_volume(),
            lambda vol: pygame.mixer.music.set_volume(vol)
        )
        self.animation_frame = 0
        self.image_index = 0
        self.alpha = 0
        self.alpha_direction = 1
        self.x_offset = 0

    def open_dungeon_generator(self):
        try:
            import importlib
            from ui import dungeon_generator_gui
            from ui.dungeon_generator_gui import DungeonGeneratorGUI
            original_fullscreen = self.game.settings.FULLSCREEN
            self.game.settings.FULLSCREEN = False
            self.game.apply_display_settings()
            dungeon_generator = DungeonGeneratorGUI(self.game)
            
            dungeon_generator.run()
            self.game.settings.FULLSCREEN = original_fullscreen
            self.game.apply_display_settings()
            self.game.logger.info("Dungeon Generator opened.")
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
        self.load_character_button.handle_event(event)
        self.dungeon_maker_button.handle_event(event)
        self.exit_button.handle_event(event)
        self.volume_slider.handle_event(event)

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
        self.load_character_button.draw(screen)
        self.dungeon_maker_button.draw(screen)
        self.exit_button.draw(screen)

        # Draw rectangle around volume slider
        pygame.draw.rect(screen, UI_SECONDARY_COLOR, (self.volume_slider.rect.x - 5, self.volume_slider.rect.y - 5, self.volume_slider.rect.width + 10, self.volume_slider.rect.height + 10), 2)
        self.volume_slider.draw(screen)
        draw_text(screen, "Volume", UI_FONT_SIZE_DEFAULT, UI_PRIMARY_COLOR, self.volume_slider.rect.x + self.volume_slider.rect.width // 2, self.volume_slider.rect.y - 30, align="center")


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

class VolumeSlider:
    def __init__(self, x, y, width, height, initial_volume, on_change_callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.volume = initial_volume
        self.on_change_callback = on_change_callback
        self.thumb_width = 10
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x = event.pos[0]
                self.volume = (mouse_x - self.rect.x) / self.rect.width
                self.volume = max(0, min(1, self.volume))
                self.on_change_callback(self.volume)

    def draw(self, surface):
        # Draw slider background
        pygame.draw.rect(surface, UI_SECONDARY_COLOR, self.rect)
        # Draw thumb
        thumb_x = self.rect.x + int(self.volume * self.rect.width)
        thumb_rect = pygame.Rect(thumb_x - self.thumb_width // 2, self.rect.y, self.thumb_width, self.rect.height)
        pygame.draw.rect(surface, UI_ACCENT_COLOR, thumb_rect)