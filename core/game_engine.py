import sys
import os
sys.path.append(".")
import pygame
from config import settings # Import settings module directly
from config.constants import STATE_TITLE_SCREEN, STATE_GAMEPLAY, STATE_PAUSE_MENU, STATE_SETTINGS_MENU, STATE_INVENTORY, STATE_SKILL_TREE
from core.input_handler import InputHandler
from core.scene_manager import SceneManager, BaseScene
from core.utils import draw_text
# from entities.player import Player # Removed Player import here
from ui.hud import HUD # Import HUD
from ui.inventory_screen import InventoryScreen # Import InventoryScreen
from ui.skill_tree_ui import SkillTreeUI # Import SkillTreeUI
from ui.dialogue_manager import DialogueManager
from progression.quests import QuestManager # Import QuestManager
import sys
import logging # Import logging module
import traceback # Import traceback module
from core.swamp_cave_dungeon import SwampCaveDungeon # Import SwampCaveDungeon

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

        # self.player = Player(self, self.settings.SCREEN_WIDTH // 2, self.settings.SCREEN_HEIGHT // 2) # Removed player instantiation
        # self.hud = HUD(self, self.settings.SCREEN_WIDTH // 2, self.settings.SCREEN_HEIGHT // 2) # HUD will be initialized by BaseGameplayScene or specific scenes
        self.dialogue_manager = DialogueManager(self)
        self.quest_manager = QuestManager('data/quests.json') # Initialize QuestManager

        self.scene_manager = SceneManager(self) # Pass self (GameEngine instance) to SceneManager

        # Import scenes to avoid circular dependency issues and for cleaner structure
        from ui.menus import PauseMenu, SettingsMenu
        from ui.inventory_screen import InventoryScreen
        from ui.skill_tree_ui import SkillTreeUI
        from world.zone import GameplayScene
        from ui.title_screen import TitleScreen
        self.title_screen = TitleScreen(self)

        self.scene_manager.add_scene(STATE_TITLE_SCREEN, self.title_screen)
        self.scene_manager.add_scene(STATE_PAUSE_MENU, PauseMenu(self))
        from ui.title_screen import InfoScreen
        self.info_screen = InfoScreen(self)
        self.scene_manager.add_scene("info_screen", self.info_screen)
        from core.spawn_town import SpawnTown
        self.spawn_town = SpawnTown(self) # SpawnTown will now create the player and HUD
        self.scene_manager.add_scene("spawn_town", self.spawn_town)
        self.scene_manager.add_scene(STATE_SETTINGS_MENU, SettingsMenu(self))
        self.scene_manager.add_scene(STATE_INVENTORY, InventoryScreen(self))
        self.scene_manager.add_scene(STATE_SKILL_TREE, SkillTreeUI(self))

        # Add the SwampCaveDungeon scene
        # The player and HUD instances are created in SpawnTown and need to be passed to other gameplay scenes
        # We'll need to access the player and HUD from the active gameplay scene (SpawnTown initially)
        # A better approach might be to manage player and HUD at the GameEngine level or pass them explicitly
        # For now, let's assume we can access them from the current gameplay scene if it's SpawnTown
        # TODO: Refactor player/HUD management for better scene transitions

        # Temporarily instantiate player and HUD here for dungeon scene creation
        # This is a workaround and should be refactored
        temp_player = self.spawn_town.player # Access player from SpawnTown instance
        temp_hud = self.spawn_town.hud # Access HUD from SpawnTown instance
        self.swamp_cave_dungeon = SwampCaveDungeon(self, temp_player, temp_hud)
        self.scene_manager.add_scene("swamp_cave_dungeon", self.swamp_cave_dungeon)


        self.scene_manager.add_scene(STATE_GAMEPLAY, GameplayScene(self))

        # self.scene_manager.set_scene("spawn_town", self.player) # REMOVED
        self.scene_manager.set_scene(STATE_TITLE_SCREEN)
        # For testing, you could set the scene directly to the dungeon:
        # self.scene_manager.set_scene("swamp_cave_dungeon")


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

                self.screen.fill((0, 0, 0)) # Clear screen
                self.scene_manager.draw(self.screen)
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'effects'):
                    for sprite in self.scene_manager.current_scene.effects:
                        self.screen.blit(sprite.image, (sprite.rect.x - self.scene_manager.current_scene.camera_x, sprite.rect.y - self.scene_manager.current_scene.camera_y))

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