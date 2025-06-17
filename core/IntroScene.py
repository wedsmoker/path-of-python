import pygame
import json
from core.scene_manager import BaseScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class IntroScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.dialogue_file = "data/intro_dialogue.json"  # Assuming you have this file
        self.face_image1_path = "graphics/dc-mon/human.png"
        self.face_image2_path = "graphics/dc-mon/human.png"  # Using the same image for now
        self.face_image1 = pygame.image.load(self.face_image1_path)
        self.face_image2 = pygame.image.load(self.face_image2_path)
        self.face_image1 = pygame.transform.scale(self.face_image1, (self.face_image1.get_width() * 8, self.face_image1.get_height() * 8)) # Make face twice as big
        self.face_image2 = pygame.transform.scale(self.face_image2, (self.face_image2.get_width() * 8, self.face_image2.get_height() * 8)) # Make face twice as big
        self.current_face = 0
        self.font = pygame.font.Font(None, 36)
        self.text_color = (255, 255, 255)
        self.background_color = (0, 0, 0)
        self.dialogue_data = self.load_dialogue()
        self.dialogue = self.dialogue_data["dialogues"]["old_scavenger_intro"] if self.dialogue_data else None
        self.current_node_id = self.dialogue["start_node"] if self.dialogue else None
        self.animation_timer = 0
        self.animation_interval = 0  # milliseconds, adjust for animation speed
        self.fading = False
        self.fade_alpha = 255
        self.fade_speed = 2
        self.selected_option = 0 # Track the selected option
        self.frame_counter = 0
        if not self.dialogue_data:
            self.fading = True # If dialogue is empty, skip to fading

        # Load halo sprite sheet
        self.halo_sprite_sheet_path = "graphics/gui/halo.png"
        try:
            self.halo_sprite_sheet = pygame.image.load(self.halo_sprite_sheet_path)
            self.halo_frame_width = 2490 // 5
            self.halo_frame_height = 2490 // 5
            self.halo_current_frame = 0
            print(f"Halo sprite sheet dimensions: {self.halo_sprite_sheet.get_width()}x{self.halo_sprite_sheet.get_height()}")
            print(f"Halo frame dimensions: {self.halo_frame_width}x{self.halo_frame_height}")
        except pygame.error as e:
            print(f"Error loading halo sprite sheet: {e}")
            self.halo_sprite_sheet = None

    def load_dialogue(self):
        try:
            with open(self.dialogue_file, 'r') as f:
                dialogue = json.load(f)
            return dialogue
        except FileNotFoundError:
            print(f"Error: Dialogue file not found: {self.dialogue_file}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in dialogue file: {self.dialogue_file}")
            return None

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_interval:
            self.animation_timer -= self.animation_interval
            self.current_face = 1 - self.current_face  # Toggle between 0 and 1
            if self.halo_sprite_sheet:
                self.frame_counter += 1
                if self.frame_counter % 2 == 0:
                    self.halo_current_frame = (self.halo_current_frame + 1) % 25

        if self.fading:
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                pygame.mixer.music.stop() # Stop the music
                self.game.scene_manager.set_scene("spawn_town")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.fading and self.dialogue:
                if self.current_node_id != "end_dialogue":
                    current_node = self.dialogue["nodes"][self.current_node_id]
                    if current_node["options"]:
                        if event.key == pygame.K_1:
                            self.selected_option = 0
                        elif event.key == pygame.K_2 and len(current_node["options"]) > 1:
                            self.selected_option = 1
                        elif event.key == pygame.K_3:
                            return

                        self.current_node_id = current_node["options"][self.selected_option]["next_node"]
                        self.selected_option = 0 # Reset selected option
                    else:
                        self.fading = True
                else:
                    self.fading = True
            elif event.key == pygame.K_SPACE and self.fading:
                self.fading = True

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        for word in words:
            word_surface = font.render(word, True, self.text_color)
            word_width = word_surface.get_width()
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width + font.size(" ")[0]
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width + font.size(" ")[0]
        lines.append(" ".join(current_line))
        return lines

    def draw(self, screen):
        screen.fill(self.background_color)

        # Calculate face position
        face_width = self.face_image1.get_width()
        face_height = self.face_image1.get_height()
        face_x = (SCREEN_WIDTH - face_width) // 2
        face_y = (SCREEN_HEIGHT - face_height) // 2 - 170  # Raise the face and halo
        halo_y = (SCREEN_HEIGHT - self.halo_frame_height) // 2 - 170

        # Draw halo.gif behind the face
        if self.halo_sprite_sheet:
            frame_x = (self.halo_current_frame % 5) * self.halo_frame_width
            frame_y = (self.halo_current_frame // 5) * self.halo_frame_height
            halo_rect = pygame.Rect(frame_x, frame_y, self.halo_frame_width, self.halo_frame_height)
            halo_x = (SCREEN_WIDTH - self.halo_frame_width) // 2
            screen.blit(self.halo_sprite_sheet, (halo_x, halo_y), halo_rect)

        # Draw animated face
        face_image = self.face_image1 if self.current_face == 0 else self.face_image2
        screen.blit(face_image, (face_x, face_y))

        # Draw dialogue text at the top
        if self.dialogue and self.current_node_id and self.current_node_id != "end_dialogue":
            current_node = self.dialogue["nodes"][self.current_node_id]
            text = current_node["text"]
            wrapped_lines = self.wrap_text(text, self.font, SCREEN_WIDTH - 100)
            y_offset = face_y + face_height + 20  # Position text below the face
            for line in wrapped_lines:
                text_surface = self.font.render(line, True, self.text_color)
                text_rect = text_surface.get_rect(centerx=SCREEN_WIDTH // 2, y=y_offset)
                screen.blit(text_surface, text_rect)
                y_offset += self.font.get_linesize()

            # Draw options
            if current_node["options"]:
                # Draw dialogue box
                dialogue_box_height = 200
                dialogue_box_rect = pygame.Rect(50, SCREEN_HEIGHT - dialogue_box_height - 50, SCREEN_WIDTH - 100, dialogue_box_height)
                pygame.draw.rect(screen, (50, 50, 50), dialogue_box_rect)
                for i, option in enumerate(current_node["options"]):
                    option_text = f"{i+1}. {option['text']}"
                    option_surface = self.font.render(option_text, True, self.text_color)
                    option_rect = option_surface.get_rect(x=dialogue_box_rect.x + 20, y=dialogue_box_rect.y + 20 + i * 40)
                    screen.blit(option_surface, option_rect)

        # Draw fade effect
        if self.fading:
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            screen.blit(fade_surface, (0, 0))