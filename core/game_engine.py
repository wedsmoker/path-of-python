import sys
import os
sys.path.append(".")
import pygame
from config import settings # Import settings module directly
from config.constants import STATE_TITLE_SCREEN, STATE_GAMEPLAY, STATE_PAUSE_MENU, STATE_SETTINGS_MENU, STATE_INVENTORY, STATE_SKILL_TREE
from core.input_handler import InputHandler
from core.scene_manager import SceneManager, BaseScene
from core.utils import draw_text
from ui.hud import HUD # Import HUD
from ui.inventory_screen import InventoryScreen # Import InventoryScreen
from ui.skill_tree_ui import SkillTreeUI # Import SkillTreeUI
from ui.dialogue_manager import DialogueManager
from progression.quests import QuestManager # Import QuestManager
import sys
import logging # Import logging module
import traceback # Import traceback module
from core.swamp_cave_dungeon import SwampCaveDungeon # Import SwampCaveDungeon
import json
import inspect # Import inspect module

class GameEngine:
    """Manages the main game loop, scenes, and core systems."""
    def __init__(self):
        pygame.init()
        # Initialize the screen *before* applying display settings
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SHOWN)
        # Configure logging
        logging.basicConfig(level=logging.DEBUG if settings.DEBUG_MODE else logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.info("GameEngine initialized.")

        self.settings = settings # Make settings accessible
        pygame.display.set_caption(self.settings.CAPTION)
        self.clock = pygame.time.Clock()
        self.running = True

        self.apply_display_settings() # Apply initial display settings

        self.input_handler = InputHandler()

        self.player = None # Initialize player to None
        self.hud = None # Initialize hud to None
        self.dialogue_manager = DialogueManager(self)
        self.quest_manager = QuestManager('data/quests.json') # Initialize QuestManager

        self.scene_manager = SceneManager(self) # Pass self (GameEngine instance) to SceneManager

        # Load scenes from data/scenes.json
        self.load_scenes()

        self.scene_manager.set_scene(STATE_TITLE_SCREEN)


    def load_scenes(self):
        """Loads scenes from data/scenes.json."""
        with open('data/scenes.json', 'r') as f:
            self.scenes_data = json.load(f) # Store scenes_data as a self attribute

        self.scenes = {}
        for scene_data in self.scenes_data['scenes']: # Use self.scenes_data
            name = scene_data['name']
            class_path = scene_data['class']
            module_name, class_name = class_path.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            scene_class = getattr(module, class_name)
            
            scene_args = {'game': self}
            dungeon_data = None

            if name == "spawn_town":
                from core.spawn_town import SpawnTown
                scene = scene_class(self)
                self.spawn_town = scene
                self.player = scene.player # Set player from SpawnTown instance
                self.hud = scene.hud # Set HUD from SpawnTown instance
            else:
                # Check if the scene constructor expects player and hud
                if hasattr(scene_class, '__init__'):
                    sig = inspect.signature(scene_class.__init__)
                    if 'player' in sig.parameters and 'hud' in sig.parameters:
                        scene_args['player'] = self.player
                        scene_args['hud'] = self.hud
                    
                    # Load dungeon_data if path is specified
                    if "dungeon_data_path" in scene_data:
                        dungeon_data_path = scene_data["dungeon_data_path"]
                        try:
                            with open(dungeon_data_path, "r") as df:
                                dungeon_data = json.load(df)
                            scene_args['dungeon_data'] = dungeon_data
                        except (FileNotFoundError, json.JSONDecodeError) as e:
                            self.logger.error(f"Error loading dungeon data for scene {name} from {dungeon_data_path}: {e}")
                            scene_args['dungeon_data'] = None # Ensure dungeon_data is None on error

                scene = scene_class(**scene_args)
            
            self.logger.info(f"Attempting to add scene: {name} with class {class_name}")
            self.scene_manager.add_scene(name, scene)

    def run(self):
        """Runs the main game loop."""
        try:
            while self.running:
                dt = self.clock.tick(self.settings.FPS) / 1000.0 # Delta time in seconds

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.input_handler.handle_event(event)
                    self.scene_manager.handle_event(event)

                self.scene_manager.update(dt)
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'effects'):
                    self.scene_manager.current_scene.effects.update(dt)
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'projectiles'):
                    self.scene_manager.current_scene.projectiles.update(dt, self.scene_manager.current_scene.player, self.scene_manager.current_scene.tile_map, self.scene_manager.current_scene.tile_size)


                self.screen.fill((0, 0, 0)) # Clear screen
                self.scene_manager.draw(self.screen)
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'effects'):
                    for sprite in self.scene_manager.current_scene.effects:
                        self.screen.blit(sprite.image, (sprite.rect.x - self.scene_manager.current_scene.camera_x, sprite.rect.y - self.scene_manager.current_scene.camera_y))
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'projectiles'):
                    for sprite in self.scene_manager.current_scene.projectiles:
                        sprite.draw(self.screen, self.scene_manager.current_scene.camera_x, self.scene_manager.current_scene.camera_y, self.scene_manager.current_scene.zoom_level)


                self.input_handler.reset_inputs() # Reset input states for the next frame

                if self.settings.DEBUG_MODE:
                    debug_y_offset = 10
                    if self.settings.SHOW_FPS:
                        fps_text = f"FPS: {int(self.clock.get_fps())}"
                        draw_text(self.screen, fps_text, 18, (255, 255, 0), 10, debug_y_offset)
                        debug_y_offset += 20
                    if self.settings.SHOW_SCENE_NAME:
                        scene_name_text = f"Scene: {self.scene_manager.current_scene_name}"
                        draw_text(self.screen, scene_name_text, 18, (255, 255, 0), 10, debug_y_offset)
                        debug_y_offset += 20
                    if self.settings.SHOW_DELTA_TIME:
                        dt_text = f"DT: {dt:.4f}s"
                        draw_text(self.screen, dt_text, 18, (255, 255, 0), 10, debug_y_offset)
                        debug_y_offset += 20
                    if self.settings.SHOW_PLAYER_TILE_COORDS:
                        if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'player'):
                            player = self.scene_manager.current_scene.player
                            tile_x = int(player.rect.x / 32)
                            tile_y = int(player.rect.y / 32)
                            player_coords_text = f"Player Tile: ({tile_x}, {tile_y})"
                            draw_text(self.screen, player_coords_text, 18, (255, 255, 0), 10, debug_y_offset)
                            debug_y_offset += 20

                pygame.display.flip()

            self.quit_game()
        except Exception as e:
            self.logger.exception("An unhandled exception occurred during the game loop:")
            traceback.print_exc() # Print the full traceback
            self.quit_game()

    def apply_display_settings(self):
        """Applies display settings from config.settings."""
        self.logger.info("Applying display settings.")
        self.logger.info(f"Fullscreen: {self.settings.FULLSCREEN}, Borderless: {self.settings.BORDERLESS}, Vsync: {self.settings.VSYNC}")
        flags = pygame.FULLSCREEN if self.settings.FULLSCREEN else pygame.SHOWN
        if self.settings.VSYNC:
            flags |= pygame.DOUBLEBUF # Vsync is often tied to double buffering

        self.screen = pygame.display.set_mode(
            (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT),
            flags,
            vsync=self.settings.VSYNC
        )
        pygame.display.set_caption(self.settings.CAPTION)

        # Center the window
        window_x = (pygame.display.Info().current_w - self.settings.SCREEN_WIDTH) // 2
        window_y = (pygame.display.Info().current_h - self.settings.SCREEN_HEIGHT) // 2
        # os.environ['SDL_VIDEO_WINDOW_POS'] = f"{window_x},{window_y}"

    def quit_game(self):
        """Sets the running flag to False to exit the game loop."""
        self.running = False
        pygame.quit()
        # sys.exit() # Temporarily commented out for debugging