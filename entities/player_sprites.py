import pygame
from config.constants import TILE_SIZE

def get_player_head_sprite(class_name):
    # Load the head sprite based on class_name
    if class_name == "stalker":
        head_sprite = pygame.image.load("graphics/player/head/helm_red.png").convert_alpha()
    elif class_name == "technomancer":
        head_sprite = pygame.image.load("graphics/player/head/helm_green.png").convert_alpha()
    elif class_name == "hordemonger":
        head_sprite = pygame.image.load("graphics/player/head/helm_green.png").convert_alpha()
    else:
        head_sprite = pygame.image.load("graphics/player/head/helm_red.png").convert_alpha() # Default
    return pygame.transform.scale(head_sprite, (TILE_SIZE, TILE_SIZE))

def get_player_hand_sprite(class_name):
    # Load the hand sprite based on class_name
    if class_name == "stalker":
        hand_sprite = pygame.image.load("graphics/player/hand1/war_axe.png").convert_alpha()
    elif class_name == "technomancer":
        hand_sprite = pygame.image.load("graphics/player/hand2/misc/book_blue.png").convert_alpha()
    elif class_name == "hordemonger":
        hand_sprite = pygame.image.load("graphics/player/hand2/misc/dagger.png").convert_alpha()
    else:
        hand_sprite = pygame.image.load("graphics/player/hand1/short_sword.png").convert_alpha() # Default
    return pygame.transform.scale(hand_sprite, (TILE_SIZE, TILE_SIZE))

def get_player_leg_sprite(class_name):
    # Load the leg sprite based on class_name
    if class_name == "stalker":
        leg_sprite = pygame.image.load("graphics/player/legs/pants_brown.png").convert_alpha()
    elif class_name == "technomancer":
        leg_sprite = pygame.image.load("graphics/player/legs/pants_blue.png").convert_alpha()
    elif class_name == "hordemonger":
        leg_sprite = pygame.image.load("graphics/player/legs/trouser_green.png").convert_alpha() # Corrected filename
    else:
        leg_sprite = pygame.image.load("graphics/player/legs/pants_blue.png").convert_alpha() # Default
    return pygame.transform.scale(leg_sprite, (TILE_SIZE, TILE_SIZE))

def get_player_sprite(class_name):
    # Load the base sprite based on class_name
    if class_name == "stalker":
        base_sprite = pygame.image.load("graphics/player/base/vampire_m.png").convert_alpha()
    elif class_name == "technomancer":
        base_sprite = pygame.image.load("graphics/player/base/merfolk_f.png").convert_alpha()
    elif class_name == "hordemonger":
        base_sprite = pygame.image.load("graphics/player/base/demonspawn_black_m.png").convert_alpha()
    else:
        base_sprite = pygame.image.load("graphics/player/base/human_m.png").convert_alpha() # Default
    return pygame.transform.scale(base_sprite, (TILE_SIZE, TILE_SIZE))