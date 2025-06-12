import pygame
from core.game_engine import GameEngine
from core.override_spawn_town import OverriddenSpawnTown
from core.scene_manager import SceneManager

class MyGameEngine(GameEngine):
    def __init__(self):
        super().__init__()

        # Replace the original SpawnTown scene with the OverriddenSpawnTown scene
        self.spawn_town = OverriddenSpawnTown(self)
        self.scene_manager.scenes["spawn_town"] = self.spawn_town
        print("GameEngine initialized with OverriddenSpawnTown.")