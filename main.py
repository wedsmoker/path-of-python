import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import pygame
from core.game_engine import GameEngine
from core.scene_manager import SceneManager
from entities.player import Player
from ui.title_screen import TitleScreen, InfoScreen
from ui.menus import Button
from core.IntroScene import IntroScene  # Import the IntroScene

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("./data/corrupted.wav")  # Changed to corrupted.wav
    pygame.mixer.music.play(-1) # -1 means loop indefinitely
    # screen_width = 800
    # screen_height = 600
    # screen = pygame.display.set_mode((screen_width, screen_height))
    # pygame.display.set_caption("Path of Python")

    game = GameEngine()
    #player = Player(x=5, y=5)
    #game.player = player
    scene_manager = game.scene_manager
    # Set player in spawn town

    # Initialize TitleScreen and set it as the initial scene
    title_screen = TitleScreen(game)
    info_screen = InfoScreen(game)
    intro_scene = IntroScene(game)  # Initialize the IntroScene
    game.info_screen = info_screen
    scene_manager.add_scene("intro_scene", intro_scene)  # Add the IntroScene to the SceneManager
    from config.constants import STATE_TITLE_SCREEN
    #scene_manager.set_scene(STATE_TITLE_SCREEN)

    game.run()
    pygame.quit()