import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Game-wide Constants

# Tile and Grid
TILE_SIZE = 64 # Size of each tile in pixels
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Physics and Movement
PLAYER_SPEED = 600 # Pixels per second
ENEMY_BASE_SPEED = 100 # Pixels per second
PROJECTILE_SPEED = 400 # Pixels per second
GRAVITY = 9.8 # Placeholder, might not be used in 2D top-down

# Combat
BASE_CRIT_CHANCE = 0.05 # 5%
BASE_CRIT_MULTIPLIER = 1.5 # 150%
BASE_BLOCK_CHANCE = 0.0 # 0%
ENERGY_SHIELD_RECHARGE_DELAY = 2.0 # Seconds before ES starts recharging
ENERGY_SHIELD_RECHARGE_RATE_PERCENT = 0.05 # 5% of max ES per second

# Distances
ENEMY_SPAWN_DISTANCE = 300
ENEMY_DESPAWN_DISTANCE = 400
PROJECTILE_LIFETIME = 5 # Seconds
PROJECTILE_DESPAWN_DISTANCE = 1000

# Spawning
ENEMY_SPAWN_COOLDOWN = 5000 # Milliseconds

# Layers (for rendering order)
LAYER_BACKGROUND = 0
LAYER_TERRAIN = 1
LAYER_ITEMS = 2
LAYER_PROJECTILES = 3
LAYER_ENEMIES = 4
LAYER_PLAYER = 5
LAYER_EFFECTS = 6
LAYER_UI = 7

# Game States (for scene_manager)
STATE_TITLE_SCREEN = "title_screen"
STATE_GAMEPLAY = "gameplay"
STATE_CHARACTER_SELECTION = "character_selection"
STATE_INVENTORY = "inventory"
STATE_SKILL_TREE = "skill_tree"
STATE_PAUSE_MENU = "pause_menu"
STATE_SETTINGS_MENU = "settings_menu"
STATE_DEVELOPER_INVENTORY = "developer_inventory"

# Input Bindings
# KEY_SKILL_1 = pygame.BUTTON_LEFT # Removed, now used for movement
# KEY_SKILL_2 = pygame.BUTTON_RIGHT # Removed, now used for teleport/movement
KEY_SKILL_1 = pygame.K_q # Reassigned to Q key
KEY_SKILL_2 = pygame.K_w # Reassigned to W key
KEY_SKILL_3 = pygame.K_e
KEY_SKILL_4 = pygame.K_r
KEY_RIGHT_MOUSE = pygame.BUTTON_RIGHT
KEY_PAGE_UP = pygame.K_PAGEUP
KEY_PAGE_DOWN = pygame.K_PAGEDOWN
KEY_SKILL_5 = 6 # Mouse Button 6
KEY_SKILL_6 = 7 # Mouse Button 7
KEY_POTION_1 = pygame.K_1
KEY_POTION_2 = pygame.K_2
KEY_POTION_3 = pygame.K_3
KEY_POTION_4 = pygame.K_4
KEY_INVENTORY = pygame.K_i
KEY_SKILL_TREE = pygame.K_p
KEY_INTERACT = pygame.K_f
KEY_OPTIONS_MENU = pygame.K_o
KEY_PAUSE_MENU = pygame.K_ESCAPE
KEY_SETTINGS_MENU = pygame.K_F1
KEY_DEV_INVENTORY = pygame.K_F2