import random
import pygame
import json
from ui.dialogue_manager import DialogueManager
from core.scene_manager import BaseScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class IntroScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        
        self.dialogue_manager = DialogueManager(game)
        self.dialogue_id = "old_scavenger_intro" # The specific dialogue to use for the intro
        self.dialogue_manager.start_dialogue(self.dialogue_id)

        self.fading = False
        self.fade_alpha = 255
        self.fade_speed = 10
        self.background_color = (0, 0, 0) # Keep background black

    def update(self, dt):
        if self.fading:
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                pygame.mixer.music.stop() # Stop the music
                self.game.scene_manager.set_scene("spawn_town")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.fading:
                if event.key == pygame.K_1:
                    self.dialogue_manager.choose_option(0)
                elif event.key == pygame.K_2:
                    self.dialogue_manager.choose_option(1)
                elif event.key == pygame.K_3:
                    self.dialogue_manager.choose_option(2)
                elif event.key == pygame.K_RETURN: # Advance dialogue on Enter key
                    if not self.dialogue_manager.is_dialogue_active():
                        self.fading = True
                
                if not self.dialogue_manager.is_dialogue_active() and not self.fading:
                    self.fading = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if not self.fading:
                self.dialogue_manager.handle_click(event.pos)
                if not self.dialogue_manager.is_dialogue_active():
                    self.fading = True

    def draw(self, screen):
        screen.fill(self.background_color)

        # Draw dialogue
        self.dialogue_manager.draw(screen)

        # Draw fade effect
        if self.fading:
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            screen.blit(fade_surface, (0, 0))