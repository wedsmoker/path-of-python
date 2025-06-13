import pygame
import json
import os
from core.scene_manager import BaseScene
from config import settings
from core.utils import draw_text
from config.constants import STATE_GAMEPLAY, KEY_DEV_INVENTORY
from items.weapon import Weapon
from items.armor import Armor
from items.potion import HealthPotion
from items.gem import Gem
from items.item import Item # Import base Item class

class DeveloperInventoryScreen(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(None, settings.UI_FONT_SIZE_LARGE)
        self.text_font = pygame.font.Font(None, settings.UI_FONT_SIZE_DEFAULT)
        self.input_box_active = False
        self.input_text = ""
        self.available_items = self.load_available_items()
        self.filtered_items = list(self.available_items.keys())
        self.selected_item_index = 0

    def load_available_items(self):
        items_data = {}
        try:
            items_file_path = os.path.join(os.getcwd(), 'data', 'items.json')
            with open(items_file_path, 'r') as f:
                data = json.load(f)
            
            # Load armor
            for armor_data in data.get("armor", []):
                name = armor_data.get("name")
                description = f"Type: {armor_data.get('type')}, Defense: {armor_data.get('base_defense')}"
                armor_type = armor_data.get("type")
                base_defense = armor_data.get("base_defense")
                if name:
                    items_data[name] = Armor(name, description, armor_type, base_defense)

            # Load weapons
            for weapon_data in data.get("weapons", []):
                name = weapon_data.get("name")
                description = f"Type: {weapon_data.get('type')}, Damage: {weapon_data.get('base_damage')}"
                weapon_type = weapon_data.get("type")
                base_damage = weapon_data.get("base_damage")
                if name:
                    # Assuming base_damage is a string like "X-Y", we'll just use the first number for simplicity
                    damage_value = int(base_damage.split('-')[0]) if '-' in base_damage else int(base_damage)
                    items_data[name] = Weapon(name, description, weapon_type, damage_value)

            # Load gems (treating them as generic items for now, as their effects are complex)
            for gem_data in data.get("gems", []):
                effect_data = gem_data.get('effect', {})
                effect_str = json.dumps(effect_data) if effect_data else "N/A" # Convert effect dictionary to string
                name = gem_data.get("name")
                description = f"Type: {gem_data.get('type')}, Tags: {', '.join(gem_data.get('tags', []))}"
                if name:
                    items_data[name] = Gem(name, description, effect_str)

            # Add basic potion for now, as it's not in items.json
            items_data["Health Potion"] = HealthPotion("Health Potion", "Restores health.")

        except FileNotFoundError:
            self.game.logger.error("items.json not found!")
        except json.JSONDecodeError:
            self.game.logger.error("Error decoding items.json!")
        except Exception as e:
            self.game.logger.error(f"An error occurred loading items: {e}")
        
        return items_data

    def enter(self):
        self.game.logger.info("Entering Developer Inventory Screen.")
        self.input_box_active = False
        self.input_text = ""
        self.filtered_items = list(self.available_items.keys())
        self.selected_item_index = 0

    def exit(self):
        self.game.logger.info("Exiting Developer Inventory Screen.")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == KEY_DEV_INVENTORY:
                self.game.scene_manager.set_scene(STATE_GAMEPLAY)
            elif event.key == pygame.K_RETURN:
                if self.input_box_active:
                    self.filter_items(self.input_text)
                    self.input_box_active = False
                else:
                    self.add_selected_item()
            elif event.key == pygame.K_BACKSPACE:
                if self.input_box_active:
                    self.input_text = self.input_text[:-1]
                    self.filter_items(self.input_text)
            elif event.key == pygame.K_UP:
                if not self.input_box_active:
                    self.selected_item_index = (self.selected_item_index - 1) % len(self.filtered_items)
            elif event.key == pygame.K_DOWN:
                if not self.input_box_active:
                    self.selected_item_index = (self.selected_item_index + 1) % len(self.filtered_items)
            else:
                if self.input_box_active:
                    self.input_text += event.unicode
                    self.filter_items(self.input_text)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_input_box_rect().collidepoint(event.pos):
                self.input_box_active = True
            else:
                self.input_box_active = False
            
            # Check for clicks on "Add" and "Remove" buttons
            add_button_rect = self.get_add_button_rect()
            remove_button_rect = self.get_remove_button_rect()
            
            if add_button_rect.collidepoint(event.pos):
                self.add_selected_item()
            elif remove_button_rect.collidepoint(event.pos):
                self.remove_selected_item()

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(settings.UI_BACKGROUND_COLOR)
        draw_text(screen, "Developer Inventory", settings.UI_FONT_SIZE_LARGE, settings.UI_PRIMARY_COLOR,
                  settings.SCREEN_WIDTH // 2, 50, align="center")
        draw_text(screen, f"Press '{pygame.key.name(KEY_DEV_INVENTORY).upper()}' to return to game", settings.UI_FONT_SIZE_SMALL, settings.UI_SECONDARY_COLOR,
                  settings.SCREEN_WIDTH // 2, 90, align="center")

        # Draw input box
        input_box_rect = self.get_input_box_rect()
        pygame.draw.rect(screen, settings.WHITE if self.input_box_active else settings.UI_SECONDARY_COLOR, input_box_rect, 2)
        input_surface = self.text_font.render(self.input_text, True, settings.WHITE)
        screen.blit(input_surface, (input_box_rect.x + 5, input_box_rect.y + 5))

        # Display filtered items
        item_display_y = 200
        for i, item_name in enumerate(self.filtered_items):
            color = settings.UI_ACCENT_COLOR if i == self.selected_item_index else settings.UI_PRIMARY_COLOR
            draw_text(screen, item_name, settings.UI_FONT_SIZE_DEFAULT, color,
                      settings.SCREEN_WIDTH // 2, item_display_y + i * 30, align="center")

        # Draw Add and Remove buttons
        add_button_rect = self.get_add_button_rect()
        remove_button_rect = self.get_remove_button_rect()

        pygame.draw.rect(screen, settings.GREEN, add_button_rect)
        pygame.draw.rect(screen, settings.RED, remove_button_rect)

        draw_text(screen, "Add Item", settings.UI_FONT_SIZE_DEFAULT, settings.WHITE,
                  add_button_rect.centerx, add_button_rect.centery, align="center")
        draw_text(screen, "Remove Item", settings.UI_FONT_SIZE_DEFAULT, settings.WHITE,
                  remove_button_rect.centerx, remove_button_rect.centery, align="center")

        # Display player inventory
        player = self.game.player
        if player and player.inventory:
            draw_text(screen, "Player Inventory:", settings.UI_FONT_SIZE_DEFAULT, settings.UI_PRIMARY_COLOR,
                      100, 500, align="left")
            inventory_y = 530
            for item_instance, quantity in player.inventory.items.items():
                draw_text(screen, f"{item_instance.name}: {quantity}", settings.UI_FONT_SIZE_SMALL, settings.WHITE,
                          100, inventory_y, align="left")
                inventory_y += 25

    def get_input_box_rect(self):
        input_box_width = 400
        input_box_height = 40
        input_box_x = (settings.SCREEN_WIDTH - input_box_width) // 2
        input_box_y = 120
        return pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)

    def get_add_button_rect(self):
        button_width = 150
        button_height = 50
        button_x = settings.SCREEN_WIDTH // 2 - button_width - 10
        button_y = settings.SCREEN_HEIGHT - 100
        return pygame.Rect(button_x, button_y, button_width, button_height)

    def get_remove_button_rect(self):
        button_width = 150
        button_height = 50
        button_x = settings.SCREEN_WIDTH // 2 + 10
        button_y = settings.SCREEN_HEIGHT - 100
        return pygame.Rect(button_x, button_y, button_width, button_height)

    def filter_items(self, search_text):
        self.filtered_items = [
            item_name for item_name in self.available_items.keys()
            if search_text.lower() in item_name.lower()
        ]
        self.selected_item_index = 0

    def add_selected_item(self):
        if self.filtered_items:
            selected_item_name = self.filtered_items[self.selected_item_index]
            item_instance = self.available_items[selected_item_name]
            self.game.player.inventory.add_item(item_instance, 1)
            self.game.logger.info(f"Added {selected_item_name} to player inventory.")

    def remove_selected_item(self):
        if self.filtered_items:
            selected_item_name = self.filtered_items[self.selected_item_index]
            item_instance = self.available_items[selected_item_name]
            self.game.player.inventory.remove_item(item_instance, 1)
            self.game.logger.info(f"Removed {selected_item_name} from player inventory.")