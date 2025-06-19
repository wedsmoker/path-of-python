import json
import pygame
from core.utils import draw_text
import random # Import random

class DialogueManager:
    """Manages the game's branching dialogue system."""
    def __init__(self, game):
        self.game = game
        self.current_dialogue_node = None
        self.dialogue_data = {}
        self.load_dialogue_data()
        self.font = pygame.font.Font(None, 24) # Default font for dialogue

    def load_dialogue_data(self):
        """Loads dialogue data from the JSON file."""
        try:
            with open('data/dialogue.json', 'r') as f:
                self.dialogue_data = json.load(f)
        except FileNotFoundError:
            print("ERROR: dialogue.json not found.")
            self.dialogue_data = {"dialogues": {}}
        except json.JSONDecode_Error:
            print("ERROR: Could not decode dialogue.json. Check for JSON syntax errors.")
            self.dialogue_data = {"dialogues": {}}
        try:
            with open('data/spawntown_generated_npcs_dialogue.json', 'r') as f:
                generated_dialogue_data = json.load(f)
            # Merge the generated NPC dialogue into the main dialogue data
            if "dialogues" in generated_dialogue_data:
                self.dialogue_data["dialogues"].update(generated_dialogue_data["dialogues"])
        except FileNotFoundError:
            print("WARNING: spawntown_generated_npcs_dialogue.json not found. Procedurally generated NPCs may not have dialogue.")
        except json.JSONDecodeError:
            print("ERROR: Could not decode spawntown_generated_npcs_dialogue.json. Check for JSON syntax errors.")

    def start_dialogue(self, dialogue_id):
        """Starts a new dialogue tree."""
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
            print(f"WARNING: Dialogue ID '{dialogue_id}' not found.")
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

                if next_node_id == "end_dialogue":
                    self.end_dialogue()
                else:
                    dialogue_tree_id = self.get_current_dialogue_tree_id()
                    if dialogue_tree_id:
                        # ADDED: Check for the target nodes in Charlie's dialogue
                        if dialogue_tree_id == "charlie_dialogue" and (next_node_id == "ask_about_vibe" or next_node_id == "explain_hustle"):
                            self.game.spawn_town.open_shop_window()  # Open the shop window

                        self.current_dialogue_node = self.dialogue_data["dialogues"][dialogue_tree_id]["nodes"].get(next_node_id)
                    else:
                        self.end_dialogue()
            else:
                print(f"Invalid option index: {option_index}")

    def get_current_dialogue_tree_id(self):
        """Helper to find which dialogue tree the current node belongs to."""
        for tree_id, tree_data in self.dialogue_data["dialogues"].items():
            if self.current_dialogue_node in tree_data["nodes"].values():
                return tree_id
        return None

    def is_dialogue_active(self):
        """Checks if dialogue is currently active."""
        return self.current_dialogue_node is not None

    def end_dialogue(self):
        """Ends the current dialogue."""
        self.current_dialogue_node = None

    def draw(self, screen):
        """Draws the dialogue box and text."""
        if not self.is_dialogue_active():
            return

        # Dialogue box background
        box_width = self.game.settings.SCREEN_WIDTH * 0.8
        box_height = self.game.settings.SCREEN_HEIGHT * 0.3
        box_x = (self.game.settings.SCREEN_WIDTH - box_width) // 2
        box_y = self.game.settings.SCREEN_HEIGHT - box_height - 20
        dialogue_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (0, 0, 0, 180), dialogue_rect, border_radius=10) # Semi-transparent black
        pygame.draw.rect(screen, (255, 255, 255), dialogue_rect, 2, border_radius=10) # White border

        # Dialogue text
        text_margin = 20
        text_x = box_x + text_margin
        text_y = box_y + text_margin
        draw_text(screen, self.get_current_dialogue_text(), 20, (255, 255, 255), text_x, text_y)

        # Dialogue options
        options = self.get_current_dialogue_options()
        option_y_offset = text_y + self.font.get_linesize() * 2 # Adjust based on text height
        for i, option in enumerate(options):
            option_text = f"{i+1}. {option['text']}"
            draw_text(screen, option_text, 18, (200, 200, 255), text_x, option_y_offset + (i * 25))