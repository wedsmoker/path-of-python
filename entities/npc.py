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

        # Load random merfolk sprite
        merfolk_sprites = [
            "merfolk_aquamancer.png",
            "merfolk_fighter.png",
            "merfolk_impaler.png",
            "merfolk_javelineer.png",
            "merfolk_plain.png"
        ]
        merfolk_path = os.path.join(os.getcwd(), "graphics", "dc-mon", random.choice(merfolk_sprites))
        if os.path.exists(merfolk_path):
            self.image = pygame.image.load(merfolk_path).convert_alpha()
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