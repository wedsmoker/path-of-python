import pygame
from config import settings
from core.utils import draw_text
import os
import random
import json

class Button:
    def __init__(self, rect, color, hover_color, click_color, text, font, text_color):
        self.rect = rect
        self.color = color
        self.hover_color = hover_color
        self.click_color = click_color
        self.text = text
        self.font = font
        self.text_color = text_color
        self.hovered = False
        self.pressed = False

    def draw(self, screen):
        current_color = self.click_color if self.pressed else (self.hover_color if self.hovered else self.color)
        pygame.draw.rect(screen, current_color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False

    def is_clicked(self):
        return self.hovered and self.pressed

class ShopWindow:
    """Displays a shop window with items from items.json."""
    def __init__(self, x, y, items_data, game):
        self.game = game
        self.width = settings.SCREEN_WIDTH * 0.4  # Reduced width
        self.height = settings.SCREEN_HEIGHT * 0.6  # Reduced height
        self.x = (settings.SCREEN_WIDTH - self.width) // 2  # Center horizontally
        self.y = y - self.height + 300 # Adjusted position
        with open('data/items.json', 'r') as f:
            self.items_data = json.load(f)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.close_button = Button(pygame.Rect(self.x + self.width - 80, self.y + 10, 70, 30), (200, 50, 50), (255, 75, 75), (150, 25, 25), "Close", self.font, (255, 255, 255))
        self.item_buy_buttons = []
        self.selected_item = None
        self.message = None
        self.message_timer = 0
        self.items_per_row = 1
        self.item_vertical_spacing = 20  # Reduced item spacing
        self.items_per_page = 3
        self.current_page = {}
        self.is_open = False
        self.group_height = self.height // 3  # Height of each item group
        self.item_groups = list(self.items_data.keys())  # Define the order of item groups based on keys in items_data
        if "gem" in self.item_groups:
            self.item_groups[self.item_groups.index("gem")] = "runes"

        try:
            self.shop_image = pygame.image.load(os.path.join(".", "graphics", "dc-dngn", "shops", "shop_booth.png")).convert_alpha()
            self.shop_image = pygame.transform.scale(self.shop_image, (int(self.width), int(self.height)))
            self.item_image = pygame.image.load(os.path.join(".", "graphics", "dc-dngn", "shops", "item.png")).convert_alpha()
            self.item_image = pygame.transform.scale(self.item_image, (32, 32))

            weapon_image_path = os.path.join(".", "graphics", "dc-dngn", "shops", "shop_weapon.png")
            self.weapon_image = pygame.image.load(weapon_image_path).convert_alpha()
            self.weapon_image = pygame.transform.scale(self.weapon_image, (32, 32))  # Adjusted size

            armor_image_path = os.path.join(".", "graphics", "dc-dngn", "shops", "shop_armour.png")
            self.armor_image = pygame.image.load(armor_image_path).convert_alpha()
            self.armor_image = pygame.transform.scale(self.armor_image, (32, 32))  # Adjusted size

            rune_image_path = os.path.join(".", "graphics", "item", "misc", "runes", "rune_cerebov.png")
            self.rune_image = pygame.image.load(rune_image_path).convert_alpha()
            self.rune_image = pygame.transform.scale(self.rune_image, (32, 32))  # Adjusted size

        except FileNotFoundError as e:
            print(f"Error loading images: {e}")
            self.shop_image = None
            self.item_image = None
            self.weapon_image = None
            self.armor_image = None
            self.rune_image = None

        # Navigation buttons
        self.next_button = {}
        self.prev_button = {}
        for item_type in self.item_groups:
            self.current_page[item_type] = 0
            # Adjusted button positions
            button_y = self.y + (self.item_groups.index(item_type) * self.group_height) + self.group_height - 30
            button_x_center = self.x + (self.width // 2) - 20 # Center of shop window
            self.next_button[item_type] = Button(pygame.Rect(button_x_center + 25, button_y, 40, 20), (50, 50, 150), (75, 75, 175), (25, 25, 125), "Next", self.small_font, (255, 255, 255))
            self.prev_button[item_type] = Button(pygame.Rect(button_x_center - 65, button_y, 40, 20), (50, 50, 150), (75, 75, 175), (25, 25, 125), "Prev", self.small_font, (255, 255, 255))


    def handle_event(self, event):
        """Handles events within the shop window."""
        self.close_button.handle_event(event)

        if self.close_button.is_clicked():
            self.is_open = False
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_3}))
            return "close"

        for item_type in self.item_groups:
            self.next_button[item_type].handle_event(event)
            self.prev_button[item_type].handle_event(event)

            if self.next_button[item_type].is_clicked():
                self.current_page[item_type] += 1
                if self.current_page[item_type] * self.items_per_page >= len(self.items_data[item_type]):
                    self.current_page[item_type] = 0  # Wrap around to the first page
            if self.prev_button[item_type].is_clicked():
                self.current_page[item_type] -= 1
                if self.current_page[item_type] < 0:
                    self.current_page[item_type] = (len(self.items_data[item_type]) + self.items_per_page - 1) // self.items_per_page - 1 # Wrap around to the last page


        for button in self.item_buy_buttons:
            button.handle_event(event)
            if button.is_clicked():
                item = button.item
                if 'price' in item:
                    if self.game.spawn_town.player.money >= item['price']:
                        self.game.spawn_town.player.money -= item['price']
                        self.game.spawn_town.player.inventory.add_item(item, 1)
                        self.message = f"Bought {item['name']}!"
                        self.message_timer = pygame.time.get_ticks()
                    else:
                        self.message = "Not enough money!"
                        self.message_timer = pygame.time.get_ticks()
                return

        return None

    def draw(self, screen):
        """Draws the shop window and items."""
        if self.shop_image:
            screen.blit(self.shop_image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (0, 0, 0, 180), self.rect, border_radius=10)  # Semi-transparent black
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)  # White border

        # Draw close button
        self.close_button.draw(screen)

        # Display player money
        draw_text(screen, f"Money: {self.game.spawn_town.player.money}", 18, (255, 255, 255), self.x + self.width // 2 - 75, self.y + 30)

        # Display items in sections with pagination
        item_margin = 20
        item_x_start = self.x + item_margin
        item_x = item_x_start
        self.item_buy_buttons = []
        item_index = 0

        group_x_offset = 5  # Offset to horizontally center the group graphics

        for i, item_type in enumerate(self.item_groups):
            group_y_start = self.y + (i * self.group_height) + item_margin
            text_x = item_x_start
            image_x = text_x + 80 # Position image next to text
            group_name = item_type.capitalize()
            if item_type == "runes":
                group_name = "Runes"
            draw_text(screen, group_name, 20, (255, 255, 255), text_x, group_y_start)

            # Center the images horizontally within their respective groups
            image_y = group_y_start - 5

            if item_type == "weapon" and self.weapon_image:
                screen.blit(self.weapon_image, (image_x, image_y))
            elif item_type == "armor" and self.armor_image:
                screen.blit(self.armor_image, (image_x, image_y))
            elif item_type == "runes" and self.rune_image:
                screen.blit(self.rune_image, (image_x, image_y))

            if i > 0:
                pygame.draw.line(screen, (255, 255, 255), (self.x, group_y_start - 10), (self.x + self.width, group_y_start - 10), 2)

            self.next_button[item_type].draw(screen)
            self.prev_button[item_type].draw(screen)

            start_index = self.current_page[item_type] * self.items_per_page
            end_index = start_index + self.items_per_page
            displayed_items = self.items_data[item_type][start_index:end_index]

            item_y = group_y_start + 40  # Start item display below the line

            for item in displayed_items:
                if self.item_image:
                    screen.blit(self.item_image, (item_x - 40, item_y))
                if 'price' in item:
                    item_text = f"{item['name']} - {item['price']}"
                else:
                    item_text = f"{item['name']}"
                draw_text(screen, item_text, 18, (200, 200, 255), item_x, item_y)
                if 'description' in item:
                    draw_text(screen, item['description'], 12, (150, 150, 150), item_x, item_y + 20)
                buy_button = Button(pygame.Rect(self.x + self.width - 70, item_y, 50, 20), (50, 150, 50), (75, 175, 75), (25, 75, 25), "Buy", self.small_font, (255, 255, 255))
                buy_button.item = item
                self.item_buy_buttons.append(buy_button)
                buy_button.draw(screen)

                item_y += self.item_vertical_spacing  # Adjust vertical spacing
                item_index += 1

            item_x = item_x_start
            item_index = 0