from core.music_manager import MusicManager
import sys
import os

from ui.flesh_algorithm_terminal import FleshAlgorithmTerminal
sys.path.append(".")
import pygame
from utility.resource_path import resource_path
from config import settings # Import settings module directly
from config.constants import STATE_TITLE_SCREEN, STATE_GAMEPLAY, STATE_PAUSE_MENU, STATE_SETTINGS_MENU, STATE_INVENTORY, STATE_SKILL_TREE, STATE_DEVELOPER_INVENTORY
from core.input_handler import InputHandler
from core.scene_manager import SceneManager, BaseScene
from core.utils import draw_text
from ui.hud import HUD # Import HUD
from ui.inventory_screen import InventoryScreen # Import InventoryScreen
from ui.paste_tree_screen import PasteTreeScreen # Import PasteTreeScreen
from ui.dialogue_manager import DialogueManager
from progression.quests import QuestManager # Import QuestManager
from progression.quest_tracker import QuestTracker # Import QuestTracker
from ui.developer_inventory_screen import DeveloperInventoryScreen
import sys
import logging # Import logging module
import traceback # Import traceback module
from core.swamp_cave_dungeon import SwampCaveDungeon # Import SwampCaveDungeon
from utility.font_cache import clear_font_cache
import json
import inspect # Import inspect module

class GameEngine:
    """Manages the main game loop, scenes, and core systems."""
    def __init__(self):
        # Note: SDL_VIDEO_CENTERED and pygame.init() are now handled in main.py
        # before GameEngine is created. This ensures proper initialization order.

        # Initialize the screen with basic settings first
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

        # Configure logging
        logging.basicConfig(level=logging.DEBUG if settings.DEBUG_MODE else logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.music_manager = MusicManager()

        self.logger.info("GameEngine initialized.")

        self.settings = settings # Make settings accessible
        pygame.display.set_caption(self.settings.CAPTION)

        # Set window icon
        try:
            icon_path = resource_path("icon.ico")
            icon_surface = pygame.image.load(icon_path)
            pygame.display.set_icon(icon_surface)
        except (pygame.error, FileNotFoundError) as e:
            self.logger.warning(f"Could not load window icon: {e}")

        self.clock = pygame.time.Clock()
        self.running = True

        # Track display changes to prevent reentrant calls during mode transitions
        self._display_change_time = 0
        self._display_grace_period = 1000  # 1 second grace period in milliseconds

        # Flag to defer display settings application to main loop
        self._pending_display_settings = False

        # Flag to block drawing during display mode changes
        self._applying_display_settings = False

        # Fallback to system cursor in fullscreen mode to prevent freeze
        self._use_system_cursor = False

        # Load custom cursor image
        self.custom_cursor_image = pygame.image.load(resource_path('graphics/gui/cursor.png')).convert_alpha()
        pygame.mouse.set_visible(False)


        self.input_handler = InputHandler()

        self.player = None # Initialize player to None
        self.hud = None # Initialize hud to None
        self.dialogue_manager = DialogueManager(self)
        self.flesh_algorithm_terminal = FleshAlgorithmTerminal(self)
        self.quest_manager = QuestManager(resource_path('data/quests.json')) # Initialize QuestManager
        self.quest_tracker = QuestTracker() # Initialize QuestTracker

        self.scene_manager = SceneManager(self) # Pass self (GameEngine instance) to SceneManager - MOVED THIS LINE UP

        # Apply display settings properly
        self.apply_display_settings()

        # Load scenes from data/scenes.json
        self.developer_inventory_screen = DeveloperInventoryScreen(self)
        self.scene_manager.add_scene(STATE_DEVELOPER_INVENTORY, self.developer_inventory_screen)
        self.load_scenes()

        self.scene_manager.set_scene(STATE_TITLE_SCREEN)

    def load_scenes(self):
        """Loads scenes from data/scenes.json."""
        with open(resource_path('data/scenes.json'), 'r') as f:
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
                            with open(resource_path(dungeon_data_path), "r") as df:
                                dungeon_data = json.load(df)
                            scene_args['dungeon_data'] = dungeon_data
                        except (FileNotFoundError, json.JSONDecodeError) as e:
                            self.logger.error(f"Error loading dungeon data for scene {name} from {dungeon_data_path}: {e}")
                            scene_args['dungeon_data'] = None # Ensure dungeon_data is None on error

                    # Pass 'is_dark' parameter if it exists in scene_data AND the scene's __init__ accepts it
                    if "darkness" in scene_data and 'is_dark' in sig.parameters: # Re-added 'is_dark' in sig.parameters check
                        scene_args['is_dark'] = scene_data["darkness"]
                        self.logger.info(f"GameEngine: Passing is_dark: {scene_args['is_dark']} to scene {name} during initial load.")

                scene = scene_class(**scene_args)

            self.logger.info(f"Attempting to add scene: {name} with class {class_name}")
            self.scene_manager.add_scene(name, scene)

    
    def _show_loading_feedback(self, message: str):
        """Shows a loading message on screen during display settings changes.
        
        Args:
            message: The message to display
        """
        # Create a larger, more visible loading surface
        width, height = 400, 80
        temp_surface = pygame.Surface((width, height))
        temp_surface.fill((20, 20, 20))  # Dark gray background
        # Add a border
        pygame.draw.rect(temp_surface, (100, 100, 100), temp_surface.get_rect(), 2)
        
        # Draw the message
        draw_text(temp_surface, message, 28, (255, 255, 255), width // 2, height // 2 - 10, align="center")
        
        # Draw to center of screen
        x = (self.settings.SCREEN_WIDTH - width) // 2
        y = (self.settings.SCREEN_HEIGHT - height) // 2
        self.screen.blit(temp_surface, (x, y))
        pygame.display.flip()
        # Only pump events if display is active to avoid blocking
        if pygame.display.get_active():
            try:
                pygame.event.pump()
            except:
                pass  # Ignore event pump errors during display changes
    
    def schedule_display_settings_change(self):
        """
        Schedules a display settings change to happen at the next safe point in the main loop.
        This prevents race conditions when changing display modes during event handling.
        """
        self.logger.info("Scheduling display settings change for next frame")
        self._pending_display_settings = True

    def apply_display_settings(self):
        """
        Applies display settings from config.settings.
        This involves re-creating the main display surface, which can be a slow operation.
        """
        self.logger.info("apply_display_settings: Starting")
        self._pending_display_settings = False  # Clear the pending flag
        self._applying_display_settings = True  # Block drawing during this operation

        self.logger.info("Attempting to apply new display settings...")
        self.logger.debug(f"Target settings: Resolution=({self.settings.SCREEN_WIDTH}x{self.settings.SCREEN_HEIGHT}), "
                         f"Fullscreen={self.settings.FULLSCREEN}, Borderless={self.settings.BORDERLESS}, Vsync={self.settings.VSYNC}")

        # Center the window before reinitializing the display
        if not self.settings.FULLSCREEN:
            os.environ['SDL_VIDEO_CENTERED'] = '1'
        start_time = pygame.time.get_ticks() # Use pygame.time.get_ticks() for consistent timing
        timeout = 5000  # 5 second timeout in milliseconds

        flags = 0
        if self.settings.FULLSCREEN:
            flags = pygame.FULLSCREEN  # Simple fullscreen flag only
        elif self.settings.BORDERLESS:
            flags = pygame.NOFRAME

        try:
            self.logger.info(f"Calling pygame.display.set_mode() with flags={flags}")

            # Simple, direct set_mode call like in test_fullscreen.py
            # Don't use vsync parameter - it can cause issues on Windows
            self.screen = pygame.display.set_mode(
                (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT),
                flags
            )
            self.logger.info("Display mode set successfully.")

            # Force a display update
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            self.logger.info("Display flip completed.")

        except pygame.error as e:
            self.logger.error(f"Failed to set display mode: {e}. Falling back to default.")
            if pygame.time.get_ticks() - start_time > timeout:
                self.logger.error("Display change timed out. Falling back to windowed mode.")
                self.settings.FULLSCREEN = False
                self.settings.BORDERLESS = False
                try:
                    self.screen = pygame.display.set_mode((1280, 720))
                    self.settings.SCREEN_WIDTH = 1280
                    self.settings.SCREEN_HEIGHT = 720
                except pygame.error as fallback_e:
                    self.logger.critical(f"Failed to set even a fallback display mode: {fallback_e}")
                    # If even the fallback fails, we have a critical problem.
                    self.quit_game()
                    return # Exit the method
                # After a display mode change, font surfaces can become invalid.
                # We re-initialize the font module and clear our custom font cache.
                self.logger.debug("Before pygame.font.init()") # Added log
                pygame.font.init()
                clear_font_cache()
                self.logger.info("Pygame font module initialized and font cache cleared.")
                self.logger.debug("After pygame.font.init()") # Added log

                # Reinitialize fonts for UI elements.
                self.logger.debug("Before self.reinitialize_ui_fonts()")
                self.reinitialize_ui_fonts()
                self.logger.debug("After self.reinitialize_ui_fonts()")
                pygame.display.set_caption(self.settings.CAPTION)

                # Re-set window icon after fallback display mode
                try:
                    icon_path = resource_path("icon.ico")
                    icon_surface = pygame.image.load(icon_path)
                    pygame.display.set_icon(icon_surface)
                except (pygame.error, FileNotFoundError) as e:
                    self.logger.warning(f"Could not load window icon: {e}")

                return # Exit the method after fallback
            # Fallback to a known safe mode if the desired mode fails
            try:
                self.screen = pygame.display.set_mode((1280, 720))
                self.settings.SCREEN_WIDTH = 1280
                self.settings.SCREEN_HEIGHT = 720
                self.settings.FULLSCREEN = False
                self.settings.BORDERLESS = False
            except pygame.error as fallback_e:
                self.logger.critical(f"Failed to set even a fallback display mode: {fallback_e}")
                # If even the fallback fails, we have a critical problem.
                self.quit_game()
                return # Exit the method

        # After a display mode change, font surfaces can become invalid.
        # We re-initialize the font module and clear our custom font cache.
        pygame.font.init()
        clear_font_cache()
        self.logger.info("Pygame font module initialized and font cache cleared.")

        # Reinitialize fonts for UI elements.
        self.reinitialize_ui_fonts()

        pygame.display.set_caption(self.settings.CAPTION)

        # Re-set window icon after display mode change
        try:
            icon_path = resource_path("icon.ico")
            icon_surface = pygame.image.load(icon_path)
            pygame.display.set_icon(icon_surface)
        except (pygame.error, FileNotFoundError) as e:
            self.logger.warning(f"Could not load window icon: {e}")

        # Record the time of this display change to prevent reentrant calls
        self._display_change_time = pygame.time.get_ticks()
        self.logger.info(f"Display change timestamp set to {self._display_change_time}")

        self._applying_display_settings = False  # Re-enable drawing
        self.logger.info("apply_display_settings: Completed successfully")

        # Reset cursor mode for windowed, enable system cursor for fullscreen
        if self.settings.FULLSCREEN:
            self.logger.info("Fullscreen mode - using system cursor to prevent freeze")
            self._use_system_cursor = True
            pygame.mouse.set_visible(True)
        else:
            self.logger.info("Windowed mode - using custom cursor")
            self._use_system_cursor = False
            # Only reinitialize custom cursor in windowed mode (can freeze in fullscreen)
            try:
                self.custom_cursor_image = pygame.image.load(resource_path('graphics/gui/cursor.png')).convert_alpha()
                pygame.mouse.set_visible(False)  # Hide system cursor in windowed mode
                self.logger.info("Custom cursor reinitialized after display change")
            except Exception as e:
                self.logger.error(f"Failed to reinitialize custom cursor: {e}")
                self._use_system_cursor = True
                pygame.mouse.set_visible(True)  # Fall back to system cursor

    def reinitialize_ui_fonts(self):
        """
        Reinitializes fonts for UI elements.

        Previously, this method iterated through all scenes, causing a freeze
        when applying settings due to the high number of scenes and UI elements.

        Now, it's designed to be more performant by re-initializing fonts only
        for the currently active scene. This assumes that scenes will correctly
        initialize their own fonts when they become active.
        """
        self.logger.info("Reinitializing UI fonts for the current scene.")
        current_scene = self.scene_manager.current_scene
        if current_scene and hasattr(current_scene, 'reinitialize_fonts'):
            self.logger.info(f"Reinitializing fonts for active scene: {self.scene_manager.current_scene_name}")
            try:
                current_scene.reinitialize_fonts()
            except Exception as e:
                self.logger.error(f"Could not reinitialize fonts for scene {self.scene_manager.current_scene_name}: {e}")
        else:
            if current_scene:
                self.logger.warning(f"Current scene '{self.scene_manager.current_scene_name}' has no reinitialize_fonts method.")
            else:
                self.logger.warning("No current scene found to reinitialize fonts for.")

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

                # Apply pending display settings changes at a safe point
                if self._pending_display_settings:
                    self.apply_display_settings()
                    # Don't skip the frame - let the new scene draw
                    # Just clear the screen to black first
                    self.screen.fill((0, 0, 0))
                    pygame.display.flip()

                # Check if display is still valid before operations
                # Only reinitialize if not in grace period after manual display change
                if not pygame.display.get_active():
                    time_since_display_change = pygame.time.get_ticks() - self._display_change_time
                    if time_since_display_change > self._display_grace_period:
                        self.logger.warning("Display surface is not active, reinitializing...")
                        self.logger.info(f"Time since display change: {time_since_display_change}ms > grace period: {self._display_grace_period}ms")
                        self.apply_display_settings()
                    else:
                        self.logger.debug(f"Skipping display reinitialize - in grace period ({time_since_display_change}ms < {self._display_grace_period}ms)")

                self.scene_manager.update(dt)
                self.music_manager.update()
                # Check if the settings menu needs UI recreation
                # DISABLED: UI recreation after fullscreen toggle causes freeze on Windows
                # The UI will naturally update when the user exits and re-enters the settings menu
                # time_since_change = pygame.time.get_ticks() - self._display_change_time
                # if self.scene_manager.current_scene_name == "settings_menu" and hasattr(self.scene_manager.current_scene, '_needs_ui_recreation') and self.scene_manager.current_scene._needs_ui_recreation:
                #     if time_since_change > 1000:  # Wait at least 1 second after display change
                #         self.logger.info("SettingsMenu needs UI recreation, calling recreate_ui().")
                #         self.scene_manager.current_scene.recreate_ui()
                #         self.scene_manager.current_scene._needs_ui_recreation = False
                #     else:
                #         self.logger.debug(f"Waiting for display to settle before UI recreation ({time_since_change}ms < 1000ms)")
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'effects'):
                    self.scene_manager.current_scene.effects.update(dt)
                if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'projectiles'):
                    self.scene_manager.current_scene.projectiles.update(dt, self.scene_manager.current_scene.player, self.scene_manager.current_scene.tile_map, self.scene_manager.current_scene.tile_size)

                # --- Rendering starts here ---
                try:
                    self.screen.fill((0, 0, 0)) # Clear the screen with black

                    # Draw all game elements directly to the screen
                    self.scene_manager.draw(self.screen)

                    # Draw effects
                    if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'effects'):
                        for sprite in self.scene_manager.current_scene.effects:
                            self.screen.blit(sprite.image, (sprite.rect.x - self.scene_manager.current_scene.camera_x, sprite.rect.y - self.scene_manager.current_scene.camera_y))

                    # Draw projectiles
                    if self.scene_manager.current_scene and hasattr(self.scene_manager.current_scene, 'projectiles'):
                        for sprite in self.scene_manager.current_scene.projectiles:
                            sprite.draw(self.screen, self.scene_manager.current_scene.camera_x, self.scene_manager.current_scene.camera_y, self.scene_manager.current_scene.zoom_level)

                    self.input_handler.reset_inputs() # Reset input states for the next frame

                    # Draw the custom cursor on top of everything

                    # Skip custom cursor if using system cursor (fullscreen workaround)
                    if not self._use_system_cursor:
                        # SAFER MOUSE POSITION RETRIEVAL - prevents freeze in fullscreen mode
                        try:
                            mouse_pos = pygame.mouse.get_pos()
                            cursor_x = mouse_pos[0] - self.custom_cursor_image.get_width() // 2
                            cursor_y = mouse_pos[1] - self.custom_cursor_image.get_height() // 2
                            self.screen.blit(self.custom_cursor_image, (cursor_x, cursor_y))
                        except Exception as e:
                            self.logger.warning(f"Failed to get mouse position for cursor: {e}")
                            # Switch to system cursor on error (fullscreen workaround)
                            self._use_system_cursor = True
                            pygame.mouse.set_visible(True)
                    else:
                        pass  # Using system cursor in fullscreen mode

                    pygame.display.flip()
                except pygame.error as e:
                    self.logger.error(f"Failed to fill or flip display: {e}")
                    self.apply_display_settings() # Try to reinitialize display
                    continue # Skip this frame if display is not ready

            self.quit_game()
        except Exception as e:
            self.logger.exception("An unhandled exception occurred during the game loop:")
            traceback.print_exc() # Print the full traceback
            self.quit_game()

    def quit_game(self):
        """Sets the running flag to False to exit the game loop."""
        self.running = False
        pygame.quit()
        # sys.exit() # Temporarily commented out for debugging