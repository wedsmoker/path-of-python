# Skill Activation Plan

This document outlines how skills are activated in the Path of Python game, focusing on mouse clicks and page up/down keys.

## Input Handling

The `InputHandler` class in `core/input_handler.py` processes mouse and keyboard events. The `handle_event` method processes Pygame events, including `KEYDOWN`, `KEYUP`, `MOUSEBUTTONDOWN`, `MOUSEBUTTONUP`, and `MOUSEMOTION`. It stores the state of keys and mouse buttons (pressed, just pressed, just released).

## Skill Activation

The `get_skill_key_pressed` method in `core/input_handler.py` determines which skill key has been pressed.

## Skill Bindings

The following keys and mouse buttons are bound to skills, based on the `config/constants.py` file:

*   Skill 1: Left Mouse Button (`pygame.BUTTON_LEFT`)
*   Skill 2: Right Mouse Button (`pygame.BUTTON_RIGHT`)
*   Skill 3: Page Up (`pygame.K_PAGEUP`)
*   Skill 4: Page Down (`pygame.K_PAGEDOWN`)

## Input Flow Diagram

```mermaid
graph LR
    A[User Input (Mouse/Keyboard)] --> B(InputHandler.handle_event);
    B --> C{Event Type?};
    C -- MouseButtonDown --> D[Store Mouse Button Press];
    C -- KeyDown --> E[Store Key Press];
    D --> F(InputHandler.get_skill_key_pressed);
    E --> F;
    F --> G{Skill Key Pressed?};
    G -- Yes --> H[Return Skill Index];
    G -- No --> I[Return None];
    H --> J[Activate Skill (combat/skills.py)];
    I --> K[Do Nothing];
```

## Notes

*   The player's movement is now controlled by the WASD keys