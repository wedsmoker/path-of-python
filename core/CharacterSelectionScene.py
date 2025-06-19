import pygame
import json
import random
from core.scene_manager import BaseScene
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from ui.menus import Button # Import Button class

class ElectricityEffect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.color = (0, 255, 255) # Cyan for electricity
        self.alpha = 255
        self.image.fill((*self.color, self.alpha))
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 500 # milliseconds
        self.creation_time = pygame.time.get_ticks()

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.creation_time
        if elapsed_time > self.lifetime:
            self.kill() # Remove sprite from all groups
        else:
            self.alpha = 255 - int(255 * (elapsed_time / self.lifetime))
            self.image.fill((*self.color, self.alpha))

class CharacterSelectionScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        # Flicker effect variables for occasional quick flickers
        self.flicker_alpha = 0
        self.flicker_max_alpha = 100 # Max brightness during a flicker
        self.flicker_decay_rate = 4000 # Increased decay rate for even faster fade
        self.flicker_trigger_interval = 1000 # milliseconds, how often a flicker *can* happen
        self.last_flicker_time = pygame.time.get_ticks()
        self.flickering_now = False # Flag to indicate if a flicker is currently happening

        # Room graphic and its darkened version
        self.room_graphic = None 
        self.darkened_room_graphic = None 

        # Initialize helmet_lift_offset before loading class data
        self.helmet_lift_offset = {} # Stores current Y offset for helmet animation (for hover)

        # Class data
        self.classes = self.load_class_data("data/classes.json")
        
        self.selected_class = None
        self.hovered_class = None
        self.character_positions = [] # To store rects for hover detection
        self.helmet_lift_speed = 0.5 # Speed of helmet lift animation (for hover)
        self.selected_char_helmet_lift_offset = 0 # New: for selected character's helmet lift during confirmation
        self.selected_char_helmet_lift_target = SCREEN_HEIGHT # New: target height for selected character's helmet lift
        self.selected_char_helmet_lift_speed = 150.0 # New: speed for selected character's helmet lift

        self.load_graphics()
        self.setup_character_positions()

        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.class_name_font = pygame.font.Font(None, 48)
        self.info_section_rect = pygame.Rect(50, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 100, 150)
        
        # Initialize the "Confirm Choice" button
        self.confirm_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50, 200, 40,
            "Confirm Choice", self.confirm_selection
        )

        # Animation attributes for confirmation
        self.confirm_animation_active = False
        self.animation_start_time = 0
        self.animation_duration = 4000 # Total animation time in ms
        self.screen_shake_intensity = 10 # Increased intensity
        self.screen_shake_duration = 700 # Duration of screen shake
        self.electricity_effects = pygame.sprite.Group()
        self.unselected_character_indices = [] # Store indices of unselected characters
        self.selected_character_walk_out_start_time = 0 # Start walking out after 1 second
        self.selected_character_walk_out_speed = 150 # pixels per second
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.selected_character_rect = None # For visual feedback on click

    def load_class_data(self, json_path):
        """Loads class data from a JSON file."""
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            # Initialize helmet_lift_offset for each class
            for class_name in data:
                self.helmet_lift_offset[class_name] = 0
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading class data from {json_path}: {e}")
            return {}

    def load_graphics(self):
        # Load room graphic
        self.room_graphic = pygame.image.load("graphics/room.png").convert_alpha()
        self.room_graphic = pygame.transform.scale(self.room_graphic, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Create a darkened version of the room graphic
        self.darkened_room_graphic = self.room_graphic.copy()
        dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 250)) # Black with 250 alpha for even more significant darkening
        self.darkened_room_graphic.blit(dark_overlay, (0, 0))

        # Load generic helmet sprite (VR helmet)
        generic_helmet_sprite = pygame.image.load("graphics/player/head/full_black.png").convert_alpha()
        generic_helmet_sprite = pygame.transform.scale(generic_helmet_sprite, (200, 100)) # Scale to desired size

        for class_name, data in self.classes.items():
            # Load base sprite from the path specified in classes.json
            base_sprite_path = data.get("base_sprite")
            if base_sprite_path:
                base_sprite = pygame.image.load(base_sprite_path).convert_alpha()
                base_sprite = pygame.transform.scale(base_sprite, (100, 150))
                data["base_sprite_image"] = base_sprite # Store the loaded image
            else:
                data["base_sprite_image"] = pygame.Surface((100, 150), pygame.SRCALPHA) # Placeholder
            
            # Create full sprite (base sprite + specific weapon/item)
            full_sprite_surface = data["base_sprite_image"].copy() # Start with the specific base sprite
            
            # Load and blit specific items for full sprite
            if class_name == "stalker":
                weapon_sprite = pygame.image.load("graphics/player/hand1/war_axe.png").convert_alpha()
                weapon_sprite = pygame.transform.scale(weapon_sprite, (50, 50)) # Adjust size as needed
                full_sprite_surface.blit(weapon_sprite, (25, 75)) # Position relative to character
            elif class_name == "technomancer":
                item_sprite = pygame.image.load("graphics/player/hand2/misc/book_blue.png").convert_alpha()
                item_sprite = pygame.transform.scale(item_sprite, (50, 50))
                full_sprite_surface.blit(item_sprite, (25, 75))
            elif class_name == "hordemonger":
                item_sprite = pygame.image.load("graphics/player/hand2/misc/dagger.png").convert_alpha()
                item_sprite = pygame.transform.scale(item_sprite, (50, 50))
                full_sprite_surface.blit(item_sprite, (25, 75))
            
            data["full_sprite"] = full_sprite_surface

            # Assign helmet sprite
            data["helmet_sprite"] = generic_helmet_sprite.copy()
            # self.helmet_lift_offset[class_name] = 0 # This line is no longer needed here as it's initialized earlier

    def setup_character_positions(self):
        # Distribute characters horizontally
        num_classes = len(self.classes)
        spacing = SCREEN_WIDTH // (num_classes + 1)
        
        for i, class_name in enumerate(self.classes):
            x = spacing * (i + 1) - 50 # Center the 100px wide sprite
            y = SCREEN_HEIGHT // 2 - 75 # Center the 150px tall sprite
            self.character_positions.append(pygame.Rect(x, y, 100, 150))

    def handle_event(self, event):
        if self.confirm_animation_active:
            return # Disable input during animation

        if event.type == pygame.MOUSEMOTION:
            self.hovered_class = None
            for i, rect in enumerate(self.character_positions):
                if rect.collidepoint(event.pos):
                    self.hovered_class = list(self.classes.keys())[i]
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                for i, rect in enumerate(self.character_positions):
                    if rect.collidepoint(event.pos):
                        self.selected_class = list(self.classes.keys())[i]
                        self.selected_character_rect = rect.copy() # Store rect for visual feedback
                        self.game.logger.info(f"Selected class: {self.selected_class}")
                        break
        self.confirm_button.handle_event(event)
    
    def confirm_selection(self):
        if self.selected_class:
            self.game.logger.info(f"Confirmed class: {self.selected_class}")
            self.confirm_animation_active = True
            self.animation_start_time = pygame.time.get_ticks()
            
            # Identify unselected characters for death animation
            self.unselected_character_indices = []
            for i, class_name in enumerate(self.classes.keys()):
                if class_name != self.selected_class:
                    self.unselected_character_indices.append(i)
            
            # Spawn initial electricity effects for unselected characters
            for index in self.unselected_character_indices:
                char_rect = self.character_positions[index]
                # Spawn electricity at the head of the unselected characters
                self.electricity_effects.add(ElectricityEffect(char_rect.centerx, char_rect.top + 20)) # Approx head position
            
            # Initialize selected character's helmet lift offset for the confirmation animation
            self.selected_char_helmet_lift_offset = self.helmet_lift_offset[self.selected_class]
        else:
            self.game.logger.info("No class selected yet!")

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        if self.confirm_animation_active:
            elapsed_animation_time = current_time - self.animation_start_time

            # Screen Shake
            if elapsed_animation_time < self.screen_shake_duration:
                self.shake_offset_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
                self.shake_offset_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            else:
                self.shake_offset_x = 0
                self.shake_offset_y = 0

            # Update electricity effects
            self.electricity_effects.update(dt)

            # Selected Character Helmet Lift (during confirmation animation)
            if self.selected_class:
                if self.selected_char_helmet_lift_offset < self.selected_char_helmet_lift_target:
                    self.selected_char_helmet_lift_offset += self.selected_char_helmet_lift_speed * dt
                    if self.selected_char_helmet_lift_offset > self.selected_char_helmet_lift_target:
                        self.selected_char_helmet_lift_offset = self.selected_char_helmet_lift_target

            # Selected Character Walk Out
            if self.selected_class and self.selected_char_helmet_lift_offset >= self.selected_char_helmet_lift_target:
                selected_char_index = list(self.classes.keys()).index(self.selected_class)
                current_x = self.character_positions[selected_char_index].x
                new_x = current_x + self.selected_character_walk_out_speed * dt
                self.character_positions[selected_char_index].x = new_x
                
            # Transition to next scene after animation
            if elapsed_animation_time > self.animation_duration:
                if self.game.player:
                    selected_class_data = self.classes[self.selected_class]
                    self.game.player.set_class(self.selected_class, selected_class_data.get("stats", {}))
                self.game.scene_manager.set_scene("intro_scene")
        else:
            # New flickering light effect logic
            if not self.flickering_now:
                if current_time - self.last_flicker_time > self.flicker_trigger_interval:
                    # Randomly decide if a flicker should start
                    if random.random() < 0.2: # Increased chance to start a flicker
                        self.flickering_now = True
                        self.flicker_alpha = self.flicker_max_alpha # Instantly bright
                        self.last_flicker_time = current_time
            else:
                # Decay the flicker alpha
                self.flicker_alpha -= self.flicker_decay_rate * dt / 1000.0 # dt is in ms, convert to seconds
                if self.flicker_alpha <= 0:
                    self.flicker_alpha = 0
                    self.flickering_now = False
                    self.last_flicker_time = current_time # Reset timer for next potential flicker

            # Existing helmet lift animation (for hover)
            for class_name in self.classes:
                if self.hovered_class == class_name:
                    if self.helmet_lift_offset[class_name] < 30: # Max lift height for hover
                        self.helmet_lift_offset[class_name] += self.helmet_lift_speed * dt
                        if self.helmet_lift_offset[class_name] > 30:
                            self.helmet_lift_offset[class_name] = 30
                else:
                    if self.helmet_lift_offset[class_name] > 0:
                        self.helmet_lift_offset[class_name] -= self.helmet_lift_speed * dt
                        if self.helmet_lift_offset[class_name] < 0:
                            self.helmet_lift_offset[class_name] = 0

    def draw(self, screen):
        # Apply screen shake offset if active
        draw_offset_x = self.shake_offset_x if self.confirm_animation_active else 0
        draw_offset_y = self.shake_offset_y if self.confirm_animation_active else 0

        # Draw darkened room graphic
        screen.blit(self.darkened_room_graphic, (draw_offset_x, draw_offset_y))

        # Draw flickering light effect (overlay)
        flicker_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        flicker_surface.fill((255, 255, 255, int(self.flicker_alpha))) # White light, varying alpha
        screen.blit(flicker_surface, (draw_offset_x, draw_offset_y))

        # Draw characters
        for i, (class_name, data) in enumerate(self.classes.items()):
            char_rect = self.character_positions[i]
            
            if self.confirm_animation_active:
                if class_name == self.selected_class:
                    # Draw full sprite
                    screen.blit(data["full_sprite"], (char_rect.x + draw_offset_x, char_rect.y + draw_offset_y))
                    # Draw helmet with the new, higher animated offset for selected character
                    helmet_rect = data["helmet_sprite"].get_rect(midbottom=(char_rect.centerx + draw_offset_x, char_rect.top + 70 - self.selected_char_helmet_lift_offset + draw_offset_y)) # Adjusted initial Y
                    screen.blit(data["helmet_sprite"], helmet_rect.topleft)
                # Unselected characters are handled by electricity effects, no need to draw their sprites here
            else:
                # Normal drawing logic (hover/non-hover)
                helmet_y_offset = self.helmet_lift_offset[class_name]
                
                if self.hovered_class == class_name:
                    # Draw full sprite
                    screen.blit(data["full_sprite"], (char_rect.x + draw_offset_x, char_rect.y + draw_offset_y))
                    # Draw helmet with animated offset (hover)
                    helmet_rect = data["helmet_sprite"].get_rect(midbottom=(char_rect.centerx + draw_offset_x, char_rect.top + 120 - helmet_y_offset + draw_offset_y)) # Adjusted initial Y
                    screen.blit(data["helmet_sprite"], helmet_rect.topleft)
                else:
                    # Draw base sprite
                    screen.blit(data["base_sprite_image"], (char_rect.x + draw_offset_x, char_rect.y + draw_offset_y))
                    # Draw helmet with animated offset (non-hover)
                    helmet_rect = data["helmet_sprite"].get_rect(midbottom=(char_rect.centerx + draw_offset_x, char_rect.top + 120 - helmet_y_offset + draw_offset_y)) # Adjusted initial Y
                    screen.blit(data["helmet_sprite"], helmet_rect.topleft)

        # Draw selected character border (only in normal state)
        if not self.confirm_animation_active and self.selected_character_rect:
            # Adjust selected_character_rect for shake offset if needed, though it's not shaking here
            border_rect = self.selected_character_rect.copy()
            pygame.draw.rect(screen, (255, 255, 0), border_rect, 3) # Yellow border

        # Draw info section and confirm button (only in normal state)
        if not self.confirm_animation_active:
            pygame.draw.rect(screen, (50, 50, 50), self.info_section_rect) # Dark grey background for info section
            self.confirm_button.draw(screen)
            pygame.draw.rect(screen, (200, 200, 200), self.info_section_rect, 2) # Light grey border

            # Display info based on hovered or selected class
            display_class_data = None
            if self.hovered_class:
                display_class_data = self.classes[self.hovered_class]
            elif self.selected_class:
                display_class_data = self.classes[self.selected_class]

            if display_class_data:
                # Display class name in info section
                name_text = self.font.render(f"Class: {display_class_data['name']}", True, (255, 255, 255))
                screen.blit(name_text, (self.info_section_rect.x + 10, self.info_section_rect.y + 10))

                # Display skills
                skills_text = self.font.render(f"Skills: {', '.join(display_class_data['skills'])}", True, (255, 255, 255))
                screen.blit(skills_text, (self.info_section_rect.x + 10, self.info_section_rect.y + 50))

                # Display description
                description_text = self.font.render(f"Description: {display_class_data['description']}", True, (255, 255, 255))
                screen.blit(description_text, (self.info_section_rect.x + 10, self.info_section_rect.y + 90))

        # Draw electricity effects (always, if active)
        self.electricity_effects.draw(screen)