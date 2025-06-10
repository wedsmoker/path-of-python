import inspect

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
        print(f"Added scene {name} of type {type(scene).__name__}")

    def set_scene(self, scene_class, player=None, hud=None):
        """Sets the current active scene."""
        if self.current_scene:
            self.current_scene.exit()  # Call exit method on current scene
        self.previous_scene_name = self.current_scene_name
        print(f"Scenes keys: {self.scenes.keys()}")
        scene = self.scenes[scene_class]
        self.game.logger.info(f"Attempting to switch to scene: {scene_class}")
        self.current_scene = scene
        self.game.current_scene = scene # Set the current scene on the game object
        if hasattr(self.current_scene, '__init__'):
            print(f"scene_class: {scene_class}")
            sig = inspect.signature(self.current_scene.__init__)
            kwargs = {}
            if 'game' in sig.parameters:
                kwargs['game'] = self.game
            if 'player' in sig.parameters and player is not None:
                kwargs['player'] = player
            if 'hud' in sig.parameters and hud is not None:
                kwargs['hud'] = hud
            self.current_scene.__init__(**kwargs)
        if hasattr(self.current_scene, 'enter'):
            self.current_scene.enter()  # Call enter method on new scene
        self.current_scene_name = type(scene).__name__  # Update current scene name
        self.game.logger.info(f"Scene type: {type(scene)}")
        self.game.logger.info(f"Switched to scene: {type(scene).__name__}")  # Use logger

    def handle_event(self, event):
        """Passes events to the current scene."""
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