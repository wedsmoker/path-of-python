import pygame
from config.constants import TILE_SIZE

def get_player_head_sprite(class_name):
    # Load the head sprite
    head_sprite = pygame.image.load("graphics/player/head/helm_red.png").convert_alpha()
    return pygame.transform.scale(head_sprite, (TILE_SIZE, TILE_SIZE))

def get_player_hand_sprite(class_name):
    # Load the hand sprite
    hand_sprite = pygame.image.load("graphics/player/hand1/short_sword.png").convert_alpha()
    return pygame.transform.scale(hand_sprite, (TILE_SIZE, TILE_SIZE))

def get_player_leg_sprite(class_name):
    # Load the leg sprite
    leg_sprite = pygame.image.load("graphics/player/legs/pants_blue.png").convert_alpha()
    return pygame.transform.scale(leg_sprite, (TILE_SIZE, TILE_SIZE))

def get_player_sprite(class_name):
    # Load the base sprite
    base_sprite = pygame.image.load("graphics/player/base/human_m.png").convert_alpha()
    return pygame.transform.scale(base_sprite, (TILE_SIZE, TILE_SIZE))