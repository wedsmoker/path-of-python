import pygame
from config.constants import (
    KEY_SKILL_1, KEY_SKILL_2, KEY_SKILL_3, KEY_SKILL_4,
    KEY_POTION_1, KEY_POTION_2, KEY_POTION_3, KEY_POTION_4,
    KEY_INVENTORY, KEY_SKILL_TREE, KEY_INTERACT,
    KEY_RIGHT_MOUSE, KEY_PAGE_UP, KEY_PAGE_DOWN
)

class InputHandler:
    def __init__(self):
        self.keys_pressed = {} # Stores currently held keys (continuous)
        self.just_pressed_keys = {} # Stores keys pressed in the current frame (single-frame)
        self.just_released_keys = {} # Stores keys released in the current frame (single-frame)
        self.mouse_buttons_pressed = {} # Stores currently held mouse buttons
        self.just_pressed_mouse_buttons = {} # Stores mouse buttons pressed in the current frame
        self.just_released_mouse_buttons = {} # Stores mouse buttons released in the current frame
        self.mouse_pos = (0, 0)

    def handle_event(self, event):
        """Processes a single Pygame event."""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed[event.key] = True
            self.just_pressed_keys[event.key] = True
        elif event.type == pygame.KEYUP:
            self.keys_pressed[event.key] = False
            self.just_released_keys[event.key] = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons_pressed[event.button] = True
            self.just_pressed_mouse_buttons[event.button] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons_pressed[event.button] = False
            self.just_released_mouse_buttons[event.button] = True
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos

    def is_key_pressed(self, key):
        """Checks if a specific key is currently held down."""
        return self.keys_pressed.get(key, False)

    def is_key_just_pressed(self, key):
        """Checks if a specific key was pressed in the current frame."""
        return self.just_pressed_keys.get(key, False)

    def is_key_just_released(self, key):
        """Checks if a specific key was released in the current frame."""
        return self.just_released_keys.get(key, False)

    def is_mouse_button_pressed(self, button):
        """Checks if a specific mouse button is currently held down."""
        return self.mouse_buttons_pressed.get(button, False)

    def is_mouse_button_just_pressed(self, button):
        """Checks if a specific mouse button was pressed in the current frame."""
        return self.just_pressed_mouse_buttons.get(button, False)

    def is_mouse_button_just_released(self, button):
        """Checks if a specific mouse button was released in the current frame."""
        return self.just_released_mouse_buttons.get(button, False)

    def get_mouse_pos(self):
        """Returns the current mouse position."""
        return self.mouse_pos

    def get_skill_key_pressed(self):
        """Returns the index of the pressed skill key (0-3), or None if none."""
        if self.is_key_just_pressed(KEY_SKILL_1): return 0
        if self.is_key_just_pressed(KEY_SKILL_2): return 1
        if self.is_key_just_pressed(KEY_SKILL_3): return 2
        if self.is_key_just_pressed(KEY_SKILL_4): return 3
        if self.is_mouse_button_just_pressed(KEY_RIGHT_MOUSE): return 4
        if self.is_key_just_pressed(KEY_PAGE_UP): return 5
        if self.is_key_just_pressed(KEY_PAGE_DOWN): return 6
        return None

    def get_potion_key_pressed(self):
        """Returns the index of the pressed potion key (0-3), or None if none."""
        if self.is_key_just_pressed(KEY_POTION_1): return 0
        if self.is_key_just_pressed(KEY_POTION_2): return 1
        if self.is_key_just_pressed(KEY_POTION_3): return 2
        if self.is_key_just_pressed(KEY_POTION_4): return 3
        return None

    def is_inventory_key_pressed(self):
        """Checks if the inventory key is pressed."""
        return self.is_key_just_pressed(KEY_INVENTORY)

    def is_skill_tree_key_pressed(self):
        """Checks if the skill tree key is pressed."""
        return self.is_key_just_pressed(KEY_SKILL_TREE)

    def is_interact_key_pressed(self):
        """Checks if the interact key is pressed."""
        return self.is_key_just_pressed(KEY_INTERACT)

    def reset_inputs(self):
        """Resets single-frame input states at the end of a new frame/loop."""
        self.just_pressed_keys.clear()
        self.just_released_keys.clear()
        self.just_pressed_mouse_buttons.clear()
        self.just_released_mouse_buttons.clear()