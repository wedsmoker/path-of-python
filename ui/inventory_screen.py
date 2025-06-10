import pygame
from core.scene_manager import BaseScene
from config import settings
from core.utils import draw_text
from config.constants import STATE_GAMEPLAY, KEY_INVENTORY

class InventoryScreen(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(None, settings.UI_FONT_SIZE_LARGE)
        self.text_font = pygame.font.Font(None, settings.UI_FONT_SIZE_DEFAULT)
        self.gem_slot_color = (100, 100, 100)  # Example color for gem slots
        self.gem_slot_size = 20  # Example size for gem slots
        self.gem_slot_spacing = 5  # Example spacing between gem slots
        self.item_slot_size = 50  # Example size for item slots
        try:
            self.background_image = pygame.image.load("graphics/gui/window_inventory.png").convert()
        except FileNotFoundError:
            self.game.logger.error("Inventory background image not found!")
            self.background_image = None

    def enter(self):
        self.game.logger.info("Entering Inventory Screen.")

    def exit(self):
        self.game.logger.info("Exiting Inventory Screen.")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == KEY_INVENTORY:
                self.game.scene_manager.set_scene("pause_menu", self.game.spawn_town.player)

    def update(self, dt):
        pass

    def draw(self, screen):
        if self.background_image:
            screen.blit(self.background_image, (0, 0))  # Draw the background image
        else:
            screen.fill(settings.UI_BACKGROUND_COLOR)  # Fallback to background color

        draw_text(screen, "Inventory Screen", settings.UI_FONT_SIZE_LARGE, settings.UI_PRIMARY_COLOR,
                  settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 50, align="center")
        draw_text(screen, f"Press '{pygame.key.name(KEY_INVENTORY).upper()}' to return to game", settings.UI_FONT_SIZE_SMALL, settings.UI_SECONDARY_COLOR,
                  settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 20, align="center")

        # Display items in inventory
        player = self.game.spawn_town.player
        if player and player.inventory and player.inventory.items:
            item_x = 100
            item_y = 200
            for item, quantity in player.inventory.items.items():
                # Load item icon
                item_icon = None
                if item.name == "Health Potion":
                    try:
                        item_icon = pygame.image.load("graphics/item/potion/ruby.png").convert_alpha()
                    except FileNotFoundError:
                        item_icon = None
                elif item.name == "Basic Sword":
                    try:
                        item_icon = pygame.image.load("graphics/item/weapon/quickblade.png").convert_alpha()
                    except FileNotFoundError:
                        item_icon = None
                else:
                    print(f"No icon found for item: {item}")

                if item_icon:
                    item_icon = pygame.transform.scale(item_icon, (self.item_slot_size, self.item_slot_size))
                    screen.blit(item_icon, (item_x, item_y))
                else:
                    pygame.draw.rect(screen, (255, 0, 255), (item_x, item_y, self.item_slot_size, self.item_slot_size))  # Magenta if icon is missing

                # Display quantity
                draw_text(screen, str(quantity), settings.UI_FONT_SIZE_SMALL, settings.UI_PRIMARY_COLOR,
                          item_x + self.item_slot_size // 2, item_y + self.item_slot_size, align="center")

                # Example: Drawing gem slots for the first item in the inventory
                if hasattr(item, 'gem_slots'):
                    num_slots = len(item.gem_slots)
                    start_x = item_x + self.item_slot_size + 10  # Example X position
                    start_y = item_y

                    for i in range(num_slots):
                        slot_x = start_x + i * (self.gem_slot_size + self.gem_slot_spacing)
                        slot_y = start_y
                        pygame.draw.rect(screen, self.gem_slot_color, (slot_x, slot_y, self.gem_slot_size, self.gem_slot_size))

                item_x += 150  # Space between items