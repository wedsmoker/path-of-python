import json
import pygame
from core.utils import draw_text
import random
import time
from utility.resource_path import resource_path

class DialogueManager:
    """Manages the game's branching dialogue system with hacker-style visuals."""
    def __init__(self, game):
        self.game = game
        self.current_dialogue_node = None
        self.dialogue_data = {}
        self.load_dialogue_data()
        self.font_large = pygame.font.Font(None, 36)  # Larger font for main text
        self.font_options = pygame.font.Font(None, 32)  # Slightly smaller for options
        self.animation_time = 0
        self.chars_visible = 0  # For typewriter effect
        self.option_rects = []  # Clickable hitboxes for the current options, set each draw()

    def load_dialogue_data(self):
        """Loads dialogue data from the JSON file."""
        try:
            with open(resource_path('data/dialogue.json'), 'r', encoding='utf-8') as f:
                self.dialogue_data = json.load(f)
        except FileNotFoundError:
            print("ERROR: dialogue.json not found.")
            self.dialogue_data = {"dialogues": {}}
        except json.JSONDecodeError:
            print("ERROR: Could not decode dialogue.json. Check for JSON syntax errors.")
            self.dialogue_data = {"dialogues": {}}
        try:
            with open(resource_path('data/spawntown_generated_npcs_dialogue.json'), 'r') as f:
                generated_dialogue_data = json.load(f)
            # Merge the generated NPC dialogue into the main dialogue data
            if "dialogues" in generated_dialogue_data:
                self.dialogue_data["dialogues"].update(generated_dialogue_data["dialogues"])
        except FileNotFoundError:
            print("WARNING: spawntown_generated_npcs_dialogue.json not found. Procedurally generated NPCs may not have dialogue.")
        except json.JSONDecodeError:
            print("ERROR: Could not decode spawntown_generated_npcs_dialogue.json. Check for JSON syntax errors.")
        try:
            with open(resource_path('data/post_quest_dialogue.json'), 'r', encoding='utf-8') as f:
                self.post_quest_dialogue_data = json.load(f)
        except FileNotFoundError:
            print("WARNING: post_quest_dialogue.json not found. Post-quest dialogues may not be available.")
            self.post_quest_dialogue_data = {"dialogues": {}}
        except json.JSONDecodeError:
            print("ERROR: Could not decode post_quest_dialogue.json. Check for JSON syntax errors.")
            self.post_quest_dialogue_data = {"dialogues": {}}

    def start_dialogue(self, dialogue_id):
        """Starts a new dialogue tree."""
        dialogue_tree = self.post_quest_dialogue_data["dialogues"].get(dialogue_id)
        if not dialogue_tree:
            dialogue_tree = self.dialogue_data["dialogues"].get(dialogue_id)

        if dialogue_tree:
            # Check if this is a procedurally generated NPC dialogue
            if dialogue_id in ["villager_dialogue", "merchant_dialogue", "town_crier_dialogue"]:
                # Randomly select one node from the available nodes
                nodes = list(dialogue_tree["nodes"].keys())
                if nodes:
                    random_node_id = random.choice(nodes)
                    self.current_dialogue_node = dialogue_tree["nodes"].get(random_node_id)
                else:
                    print(f"WARNING: No nodes found for generated NPC dialogue ID '{dialogue_id}'.")
                    self.current_dialogue_node = None
            else:
                # For other dialogue types, use the defined start_node
                self.current_dialogue_node = dialogue_tree["nodes"].get(dialogue_tree["start_node"])
        else:
            print(f"WARNING: Dialogue ID '{dialogue_id}' not found in either dialogue data set.")
            self.current_dialogue_node = None

    def get_current_dialogue_text(self):
        """Gets the text for the current dialogue node."""
        if self.current_dialogue_node:
            return self.current_dialogue_node.get("text", "")
        return ""

    def get_current_dialogue_options(self):
        """Gets the options for the current dialogue node."""
        if self.current_dialogue_node:
            return self.current_dialogue_node.get("options", [])
        return []

    def choose_option(self, option_index):
        """Processes the player's chosen dialogue option."""
        if self.current_dialogue_node:
            options = self.current_dialogue_node.get("options", [])
            if 0 <= option_index < len(options):
                selected_option = options[option_index]
                next_node_id = selected_option.get("next_node")

                # Check if the option triggers a quest
                quest_to_trigger = selected_option.get("triggers_quest")
                if quest_to_trigger and hasattr(self.game, 'quest_manager'):
                    self.game.quest_manager.start_quest(quest_to_trigger)
                # Check if the option completes a quest objective
                objective_to_complete = selected_option.get("completes_objective")
                if objective_to_complete and hasattr(self.game, 'quest_tracker'):
                    obj_type = objective_to_complete.get("type")
                    obj_target = objective_to_complete.get("target")
                    if obj_type and obj_target:
                        self.game.quest_tracker.update_quest_progress(obj_type, obj_target)
                # Check if the option opens a menu
                menu_to_open = selected_option.get("opens_menu")
                if menu_to_open:
                    if menu_to_open == "flesh_algorithm_terminal":
                        self.game.flesh_algorithm_terminal.open()

                if next_node_id == "end_dialogue":
                    self.end_dialogue()
                else:
                    dialogue_tree_id = self.get_current_dialogue_tree_id()
                    if dialogue_tree_id:
                        # ADDED: Check for the target nodes in Charlie's dialogue
                        if dialogue_tree_id == "charlie_dialogue" and (next_node_id == "ask_about_vibe" or next_node_id == "explain_hustle"):
                            self.game.spawn_town.open_shop_window()  # Open the shop window

                        # Determine which dialogue data to use based on the current dialogue_tree_id
                        if dialogue_tree_id in self.post_quest_dialogue_data["dialogues"]:
                            self.current_dialogue_node = self.post_quest_dialogue_data["dialogues"][dialogue_tree_id]["nodes"].get(next_node_id)
                        else:
                            self.current_dialogue_node = self.dialogue_data["dialogues"][dialogue_tree_id]["nodes"].get(next_node_id)
                        self.animation_time = 0  # Reset animation for new node
                        self.chars_visible = 0   # Reset visible characters
                    else:
                        self.end_dialogue()
            else:
                print(f"Invalid option index: {option_index}")

    def get_current_dialogue_tree_id(self):
        """Helper to find which dialogue tree the current node belongs to."""
        for tree_id, tree_data in self.dialogue_data["dialogues"].items():
            if self.current_dialogue_node in tree_data["nodes"].values():
                return tree_id
        for tree_id, tree_data in self.post_quest_dialogue_data["dialogues"].items():
            if self.current_dialogue_node in tree_data["nodes"].values():
                return tree_id
        return None

    def handle_click(self, pos):
        """Handles a mouse click at screen position `pos`. Returns True if it hit an option."""
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                self.choose_option(i)
                return True
        return False

    def is_dialogue_active(self):
        """Checks if dialogue is currently active."""
        return self.current_dialogue_node is not None

    def end_dialogue(self):
        """Ends the current dialogue."""
        self.current_dialogue_node = None
        if hasattr(self.game, 'current_npc') and self.game.current_npc:
            self.game.current_npc.dialogue_finished = True


    def draw(self, screen):
        """Draws the dialogue with hacker-style visuals."""
        if not self.is_dialogue_active():
            return

        # Full screen semi-transparent black background
        bg_rect = pygame.Rect(0, 0, self.game.settings.SCREEN_WIDTH, self.game.settings.SCREEN_HEIGHT)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)

        # Update animation
        self.animation_time += 0.1
        self.chars_visible = min(len(self.get_current_dialogue_text()), 
                               int(self.animation_time * 5))

        # Draw main text in top half
        text_area_height = self.game.settings.SCREEN_HEIGHT // 2
        text_margin = 40
        text_x = self.game.settings.SCREEN_WIDTH // 2
        text_y = (self.game.settings.SCREEN_HEIGHT // 2) // 2

        # Get text with typewriter effect
        visible_text = self.get_current_dialogue_text()[:self.chars_visible]
        
        # Draw with animated green color (pulsing brightness)
        green_intensity = int(50 + 50 * abs(pygame.math.Vector2(self.animation_time, 0).length()))
        text_color = (0, min(255, 100 + green_intensity), 0)
        
        draw_text(screen, visible_text, 36, text_color, text_x, text_y, 
                 align="center", max_width=self.game.settings.SCREEN_WIDTH - (2 * text_margin))

        # Draw options in bottom half
        options = self.get_current_dialogue_options()
        option_area_top = self.game.settings.SCREEN_HEIGHT // 2
        option_spacing = 40
        
        # Calculate starting Y for options to center the block of options in the bottom half
        total_options_height = len(options) * option_spacing
        option_x = self.game.settings.SCREEN_WIDTH // 2
        option_y = option_area_top + (self.game.settings.SCREEN_HEIGHT // 4) - (total_options_height // 2)

        mouse_pos = pygame.mouse.get_pos()
        self.option_rects = []

        for i, option in enumerate(options):
            option_center_y = option_y + (i * option_spacing)

            # Stable hitbox (no jitter) used for hover/click detection
            option_rect = pygame.Rect(0, 0, self.game.settings.SCREEN_WIDTH - (2 * text_margin), option_spacing)
            option_rect.center = (option_x, option_center_y)
            self.option_rects.append(option_rect)
            is_hovered = option_rect.collidepoint(mouse_pos)

            # Random jitter for hacker effect
            jitter_x = random.randint(-2, 2)
            jitter_y = random.randint(-2, 2)

            prefix = "> " if not is_hovered else ">> "
            option_text = f"{prefix}{option['text']}"
            option_color = (255, 255, 255) if is_hovered else (0, 255, 0)
            draw_text(screen, option_text, 32, option_color,
                     option_x + jitter_x, option_center_y + jitter_y,
                     align="center", max_width=self.game.settings.SCREEN_WIDTH - (2 * text_margin))

        # Reset animation if dialogue changes
        if self.animation_time > 1000:  # Prevent overflow
            self.animation_time = 0