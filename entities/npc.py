import pygame
import os
import random

class NPC(pygame.sprite.Sprite):
    def __init__(self, game, x, y, width, height, color, name="NPC", dialogue_id=None):
        super().__init__()
        self.game = game
        self.name = name
        self.dialogue_id = dialogue_id
        self.in_dialogue = False

        # Define sprite paths
        yaktaur_path_base = os.path.join(os.getcwd(), "graphics", "dc-mon")
        merfolk_path_base = os.path.join(os.getcwd(), "graphics", "dc-mon")

        # Hardcode specific sprites for named NPCs
        if self.name == "Bob the Bold":
            sprite_filename = "stone_giant.png"
            sprite_path = os.path.join(yaktaur_path_base, sprite_filename)
        elif self.name == "Alice the Agile":
            sprite_filename = "deep_elf_mage.png"
            sprite_path = os.path.join(yaktaur_path_base, sprite_filename)
        elif self.name == "Charlie the Calm":
            sprite_filename = "deformed_elf.png"
            sprite_path = os.path.join(yaktaur_path_base, sprite_filename)
        else:
            # Load random merfolk sprite for other NPCs
            merfolk_sprites = [
                "giant_eyeball.png",
                "eye_of_draining.png",
                "shining_eye.png",
                "eye_of_devastation.png",
                "great_orb_of_eyes.png",
            ]
            sprite_filename = random.choice(merfolk_sprites)
            sprite_path = os.path.join(merfolk_path_base, sprite_filename)

        if os.path.exists(sprite_path):
            self.image = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            # Fallback to colored rectangle if sprite not found
            self.image = pygame.Surface((width, height))
            self.image.fill(color)

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt):
        # NPCs might have idle animations or simple movement patterns
        pass

    def interact(self, player):
        # Placeholder for interaction logic (e.g., open dialogue, quest, shop)
        if self.dialogue_id:
            self.in_dialogue = True
            self.game.dialogue_manager.start_dialogue(self.dialogue_id)
        # In a real game, this would trigger a dialogue UI