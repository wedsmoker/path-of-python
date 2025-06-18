import inspect
import json # Import json module
import os # Import os module
import pygame # Import pygame for key constants
from config.constants import STATE_DEVELOPER_INVENTORY, STATE_GAMEPLAY # Import constants

class SceneManager:
    def __init__(self, game):
        self.game = game  # Store the game engine instance
        self.current_scene = None
        self.current_scene_name = None  # Added to track current scene name
        self.previous_scene_name = None
        self.scenes = {}
        # Load initial scene
        # self.set_scene("spawn_town", self.game.player) # Removed initial scene loading

        # Set initial scene name
        self.current_scene_name = "TitleScreen"

    def add_scene(self, name, scene):
        """Adds a scene to the manager."""
        self.scenes[name] = scene
        self.game.logger.info(f"Added scene {name} of type {type(scene).__name__}")

    def set_scene(self, scene_name, player=None, hud=None, boss_key=None, friendly_entities=None): # Added friendly_entities parameter
        """Sets the current active scene."""
        if self.current_scene:
            self.current_scene.exit()  # Call exit method on current scene
        self.previous_scene_name = self.current_scene_name
        print(f"Scenes keys: {self.scenes.keys()}")
        
        # Get the scene object from the scenes dictionary
        scene = self.scenes[scene_name]
        self.game.logger.info(f"Attempting to switch to scene: {scene_name}")
        self.current_scene = scene
        self.game.current_scene = scene # Set the current scene on the game object
        
        if hasattr(self.current_scene, '__init__'):
            print(f"scene_name: {scene_name}")
            sig = inspect.signature(self.current_scene.__init__)
            kwargs = {}
            if 'game' in sig.parameters:
                kwargs['game'] = self.game
            if 'player' in sig.parameters:
                kwargs['player'] = player if player is not None else self.game.player
            if 'hud' in sig.parameters:
                kwargs['hud'] = hud if hud is not None else self.game.hud
            if 'boss_key' in sig.parameters and boss_key is not None:
                kwargs['boss_key'] = boss_key
            if 'friendly_entities' in sig.parameters: # Pass friendly_entities if accepted
                kwargs['friendly_entities'] = friendly_entities if friendly_entities is not None else []
            
            # Load dungeon_data if path is specified in self.game.scenes_data
            scene_data_from_game_engine = next((s for s in self.game.scenes_data['scenes'] if s['name'] == scene_name), None)
            if scene_data_from_game_engine and "dungeon_data_path" in scene_data_from_game_engine:
                dungeon_data_path = scene_data_from_game_engine["dungeon_data_path"]
                try:
                    with open(dungeon_data_path, "r") as df:
                        dungeon_data = json.load(df)
                    kwargs['dungeon_data'] = dungeon_data
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    self.game.logger.error(f"Error loading dungeon data for scene {scene_name} from {dungeon_data_path}: {e}")
                    kwargs['dungeon_data'] = None # Ensure dungeon_data is None on error
            elif 'dungeon_data' in sig.parameters: # If constructor expects dungeon_data but no path is found
                kwargs['dungeon_data'] = None # Explicitly pass None

            self.current_scene.__init__(**kwargs)
        if hasattr(self.current_scene, 'enter'):
            self.current_scene.enter()  # Call enter method on new scene
        self.current_scene_name = scene_name  # Update current scene name to the string name, not type name
        self.game.logger.info(f"Scene type: {type(scene)}")
        self.game.logger.info(f"Switched to scene: {scene_name}")  # Use logger

    def handle_event(self, event):
        """Passes events to the current scene and handles global scene changes."""
        # Handle developer inventory key press globally
        if self.game.input_handler.is_dev_inventory_key_pressed():
            if self.current_scene_name == STATE_DEVELOPER_INVENTORY:
                self.set_scene(STATE_GAMEPLAY)
            else:
                self.set_scene(STATE_DEVELOPER_INVENTORY)
        
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self, dt):
        """Updates the current scene."""
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, screen):
        """Draws the current scene."""
        if self.current_scene:
            self.current_scene.draw(screen)


class BaseScene:
    """Base class for all game scenes."""
    def __init__(self, game):
        self.game = game

    def enter(self):
        """Called when the scene is entered."""
        pass

    def exit(self):
        """Called when the scene is exited."""
        pass

    def handle_event(self, event):
        """Handles Pygame events for the scene."""
        pass

    def update(self, dt):
        """Updates the scene logic."""
        pass

    def draw(self, screen):
        """Draws the scene to the screen."""
        pass