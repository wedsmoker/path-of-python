import pygame
import os
import json
from config import settings
from core.utils import draw_text
from ui.dungeon_renderer import render_dungeon_pygame

class TeleporterMenu:
    def __init__(self, x, y, dungeon_scenes_data, game):
        self.rect = pygame.Rect(x, y, 650, 300) # Increased width for map visualizer
        self.dungeon_scenes_data = dungeon_scenes_data
        self.game = game
        self.is_open = False
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20) # Smaller font for descriptions
        self.title_font = pygame.font.Font(None, 32)
        self.selected_option = 0
        self.current_tilemap_data = None
        self.map_visualizer_surface = None
        self.scene_graphics = {} # To store loaded images

        self.tabs = ["Dungeons", "Quests"]
        self.current_tab = "Dungeons" # Default tab
        self.scroll_offset = 0 # This will be pixel offset for quests, item index for dungeons
        self._load_tilemap_for_selection() # Load initial map visualizer
        self.dungeon_item_height = 40 # Height of each dungeon item (graphic + text)
        self.visible_items = 5 # Number of items visible at once for dungeons (approx for quests)

        self._load_scene_graphics()

    # Removed _load_quests method as quests are now managed by QuestManager

    def _load_scene_graphics(self):
        for scene_data in self.dungeon_scenes_data:
            graphic_path = scene_data.get('graphic')
            if graphic_path:
                full_path = os.path.join(os.getcwd(), graphic_path)
                try:
                    image = pygame.image.load(full_path).convert_alpha()
                    # Scale image to a suitable size for the menu, e.g., 32x32
                    self.scene_graphics[scene_data['name']] = pygame.transform.scale(image, (32, 32))
                except FileNotFoundError:
                    print(f"TeleporterMenu: Warning: Could not load graphic for {scene_data['name']}: {full_path}")
                    self.scene_graphics[scene_data['name']] = None # Store None if not found

    def _wrap_text(self, text, font, max_width):
        """Wraps text to fit within a specified width."""
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] < max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line)) # Add the last line
        return [line for line in lines if line] # Filter out empty lines

    def _calculate_quest_item_heights(self, content_width):
        all_quests = list(self.game.quest_manager.quests.values())
        heights = []
        description_max_width = content_width - 10 # Content width minus padding
        for quest_data in all_quests:
            title_height = self.font.get_height()
            wrapped_description_lines = self._wrap_text(quest_data.description, self.small_font, description_max_width)
            description_height = len(wrapped_description_lines) * self.small_font.get_height()
            # Add some padding between title and description, and below the item
            total_height = title_height + description_height + 5 + 5 # 5 for padding between title/desc, 5 for bottom padding
            heights.append(total_height)
        return heights

    def _load_tilemap_for_selection(self):
        print(f"[_load_tilemap_for_selection] Called. Current tab: {self.current_tab}, Selected option: {self.selected_option}")
        print(f"[_load_tilemap_for_selection] Length of dungeon_scenes_data: {len(self.dungeon_scenes_data) if self.dungeon_scenes_data else 0}")
        print(f"[_load_tilemap_for_selection] Length of all_quests: {len(self.game.quest_manager.quests.values())}")
        print(f"[_load_tilemap_for_selection] Selected option: {self.selected_option}")
        self.current_tilemap_data = None
        self.map_visualizer_surface = None
        # Initialize map_visualizer_surface for quest descriptions if no tilemap is expected
        if self.current_tab == "Quests":
            content_list_width = 300
            visualizer_area_width = self.rect.width - content_list_width - 20
            visualizer_area_height = self.rect.height - 80
            self.map_visualizer_surface = pygame.Surface((visualizer_area_width, visualizer_area_height), pygame.SRCALPHA)
            self.map_visualizer_surface.fill((20, 20, 20)) # Background for description area

        if self.current_tab == "Dungeons" and self.dungeon_scenes_data:
            if 0 <= self.selected_option < len(self.dungeon_scenes_data):
                selected_scene_data = self.dungeon_scenes_data[self.selected_option]
                dungeon_data_path = selected_scene_data.get('dungeon_data_path')
                print(f"[_load_tilemap_for_selection] dungeon_data_path for selected dungeon: {dungeon_data_path}")
                if dungeon_data_path:
                    
                    full_path = os.path.join(os.getcwd(), dungeon_data_path)
                    print(f"[_load_tilemap_for_selection] Attempting to load dungeon: {selected_scene_data['name']}")
                    print(f"[_load_tilemap_for_selection] Dungeon file_path: {selected_scene_data.get('file_path')}")
                    print(f"[_load_tilemap_for_selection] Constructed full_path for dungeon: {full_path}")
                    print(f"[_load_tilemap_for_selection] os.path.exists(full_path) for dungeon: {os.path.exists(full_path)}")
                    try:
                        with open(full_path, 'r') as f:
                            self.current_tilemap_data = json.load(f)
                        print(f"[_load_tilemap_for_selection] Loaded dungeon tilemap data for {selected_scene_data['name']}. Data present: {bool(self.current_tilemap_data)}")
                    except FileNotFoundError:
                        print(f"TeleporterMenu: Warning: Tilemap data not found for {selected_scene_data['name']}: {full_path}")
                    except json.JSONDecodeError:
                        print(f"TeleporterMenu: Error: Could not decode JSON for {selected_scene_data['name']}: {full_path}")

        elif self.current_tab == "Quests":
            all_quests = list(self.game.quest_manager.quests.values())
            if 0 <= self.selected_option < len(all_quests):
                selected_quest = all_quests[self.selected_option]
                if selected_quest.is_unlocked and selected_quest.tilemap_scene_name:
                    # Find the scene data for the quest's tilemap scene
                    scene_entry = next((s for s in self.dungeon_scenes_data if s['name'] == selected_quest.tilemap_scene_name), None)
                    if scene_entry and scene_entry.get('dungeon_data_path'):
                        dungeon_data_path = scene_entry['dungeon_data_path']
                        full_path = os.path.join(os.getcwd(), dungeon_data_path)
                        print(f"[_load_tilemap_for_selection] Attempting to load quest: {selected_quest.title}")
                        print(f"[_load_tilemap_for_selection] Quest tilemap_path: {selected_quest.tilemap_path}")
                        print(f"[_load_tilemap_for_selection] Constructed full_path for quest: {full_path}")
                        print(f"[_load_tilemap_for_selection] os.path.exists(full_path) for quest: {os.path.exists(full_path)}")
                        try:
                            with open(full_path, 'r') as f:
                                self.current_tilemap_data = json.load(f)
                            print(f"[_load_tilemap_for_selection] Loaded quest tilemap data for {selected_quest.title}. Data present: {bool(self.current_tilemap_data)}")
                        except FileNotFoundError:
                            print(f"TeleporterMenu: Warning: Tilemap data not found for quest {selected_quest.title}: {full_path}")
                        except json.JSONDecodeError:
                            print(f"TeleporterMenu: Error: Could not decode JSON for quest {selected_quest.title}: {full_path}")
                # If no tilemap data was loaded for the quest, display its objectives and description
                if not self.current_tilemap_data and self.current_tab == "Quests":
                    print(f"[_load_tilemap_for_selection] No tilemap data for quest {selected_quest.title}. Displaying objectives and description.")
                    content_list_width = 300 # From content_rect.width
                    visualizer_area_width = self.rect.width - content_list_width - 20
                    # visualizer_area_height = self.rect.height - 80 # Already calculated and surface initialized

                    text_y = 10 # Start drawing from top with padding
                    
                    # Display Quest Title
                    draw_text(self.map_visualizer_surface, selected_quest.title, self.font.get_height(), (255, 255, 0), 10, text_y, align="left")
                    text_y += self.font.get_height() + 5 # Padding after title

                    # Display Objectives
                    if selected_quest.objectives:
                        draw_text(self.map_visualizer_surface, "Objectives:", self.font.get_height(), (200, 200, 200), 10, text_y, align="left")
                        text_y += self.font.get_height() + 2

                        for objective in selected_quest.objectives: # Changed from .items() to direct iteration
                            objective_text = objective['description'] # Access as dictionary
                            is_completed = objective['completed'] # Access as dictionary
                            
                            status_icon = "[X]" if is_completed else "[ ]"
                            display_text = f"{status_icon} {objective_text}"
                            
                            obj_color = (150, 255, 150) if is_completed else (255, 255, 255) # Green for completed, white for incomplete

                            wrapped_obj_lines = self._wrap_text(display_text, self.small_font, visualizer_area_width - 30) # 30 for padding and icon
                            for line in wrapped_obj_lines:
                                draw_text(self.map_visualizer_surface, line, self.small_font.get_height(), obj_color, 20, text_y, align="left") # Indent objectives
                                text_y += self.small_font.get_height() + 2
                            text_y += 5 # Small padding after each objective
                    else:
                        draw_text(self.map_visualizer_surface, "No objectives defined.", self.small_font.get_height(), (150, 150, 150), 10, text_y, align="left")
                    
                    text_y += 10 # Padding before description

                    # Display Quest Description
                    draw_text(self.map_visualizer_surface, "Description:", self.font.get_height(), (200, 200, 200), 10, text_y, align="left")
                    text_y += self.font.get_height() + 2

                    description_text = selected_quest.description
                    wrapped_lines = self._wrap_text(description_text, self.small_font, visualizer_area_width - 20) # 20 for padding
                    
                    for line in wrapped_lines:
                        draw_text(self.map_visualizer_surface, line, self.small_font.get_height(), (255, 255, 255), 10, text_y, align="left")
                        text_y += self.small_font.get_height() + 2 # Line spacing
        
        print(f"[_load_tilemap_for_selection] current_tilemap_data after load attempt: {bool(self.current_tilemap_data)}")
        if self.current_tilemap_data:
            # Generate the visualizer surface using render_dungeon_pygame
            tile_map = self.current_tilemap_data.get('tile_map')
            tileset = self.current_tilemap_data.get('tileset')
            print(f"[_load_tilemap_for_selection] Attempting to render. tile_map present: {bool(tile_map)}, tileset present: {bool(tileset)}")
            if tile_map and tileset:
                # Calculate the dimensions of the visualizer area
                # These values are derived from the draw method's calculations
                content_list_width = 300 # From content_rect.width
                visualizer_area_width = self.rect.width - content_list_width - 20
                visualizer_area_height = self.rect.height - 80

                # Calculate the original pixel dimensions of the tilemap
                tile_size = 32 # Assuming each tile is 32x32 pixels
                original_map_width = self.current_tilemap_data['width'] * tile_size
                original_map_height = self.current_tilemap_data['height'] * tile_size

                # Determine the appropriate zoom_scale to fit the map within the visualizer area
                scale_w = visualizer_area_width / original_map_width if original_map_width > 0 else 1
                scale_h = visualizer_area_height / original_map_height if original_map_height > 0 else 1
                
                # Use a slightly smaller scale to ensure padding and prevent clipping at edges
                # Also, ensure a minimum scale if the map is tiny, to make it visible
                zoom_scale = min(scale_w, scale_h) * 0.9 # 0.9 to add a small border/padding
                zoom_scale = max(0.1, zoom_scale) # Ensure a minimum visible size

                self.map_visualizer_surface = render_dungeon_pygame(
                    {
                        'tile_map': tile_map, 
                        'tileset': tileset, 
                        'width': self.current_tilemap_data['width'], 
                        'height': self.current_tilemap_data['height']
                    }, 
                    zoom_scale=zoom_scale
                )
                if self.map_visualizer_surface:
                    print(f"[_load_tilemap_for_selection] map_visualizer_surface created with dimensions: {self.map_visualizer_surface.get_size()}")
                else:
                    print(f"[_load_tilemap_for_selection] Warning: map_visualizer_surface is None after render_dungeon_pygame.")
            else:
                print(f"[_load_tilemap_for_selection] Error: Missing tile_map or tileset in current_tilemap_data.")

    def handle_event(self, event):
        if not self.is_open:
            return None

        # Content area for scrollable list (re-calculate for event handling)
        content_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 75, 300, self.rect.height - 80) # Adjusted width

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check for tab clicks
                for i, tab_name in enumerate(self.tabs):
                    tab_rect = pygame.Rect(self.rect.x + 10 + i * 100, self.rect.y + 40, 90, 30)
                    if tab_rect.collidepoint(event.pos):
                        self.current_tab = tab_name
                        self.selected_option = 0 # Reset selection when changing tabs
                        self.scroll_offset = 0 # Reset scroll when changing tabs
                        self._load_tilemap_for_selection() # Update map visualizer
                        return None # Consume event

                # Check if a dungeon scene was clicked (only if Dungeons tab is active)
                if self.current_tab == "Dungeons":
                    for i, scene_data in enumerate(self.dungeon_scenes_data):
                        item_y = self.rect.y + 80 + (i - self.scroll_offset) * self.dungeon_item_height
                        item_rect = pygame.Rect(self.rect.x + 10, item_y, content_rect.width, self.dungeon_item_height) # Use content_rect.width
                        if item_rect.collidepoint(event.pos) and content_rect.collidepoint(event.pos): # Ensure click is within menu content area
                            self.selected_option = i # Set selected option on click
                            self._load_tilemap_for_selection() # Update map visualizer
                            self.is_open = False
                            return scene_data['name']
                elif self.current_tab == "Quests":
                    all_quests = list(self.game.quest_manager.quests.values()) # Get all quests
                    quest_heights = self._calculate_quest_item_heights(content_rect.width)
                    
                    current_y_in_content_rect = 0
                    for i, quest_data in enumerate(all_quests):
                        item_height = quest_heights[i]
                        absolute_item_y = content_rect.y + current_y_in_content_rect - self.scroll_offset
                        
                        item_rect = pygame.Rect(content_rect.x, absolute_item_y, content_rect.width, item_height)
                        
                        if item_rect.collidepoint(event.pos) and content_rect.collidepoint(event.pos): # Ensure click is within menu content area
                            if quest_data.is_unlocked: # Only allow selection if unlocked
                                self.selected_option = i
                                self._load_tilemap_for_selection() # Update map visualizer
                                self.is_open = False
                                return quest_data.tilemap_scene_name
                            return None # Consume event
                        current_y_in_content_rect += item_height
                
                # Check for close button
                close_button_rect = pygame.Rect(self.rect.x + self.rect.width - 30, self.rect.y + 5, 25, 25)
                if close_button_rect.collidepoint(event.pos):
                    self.is_open = False
                    return "close"
            elif event.button == 4: # Mouse wheel up
                if self.current_tab == "Dungeons":
                    self.scroll_offset = max(0, self.scroll_offset - 1) # Still item-based for dungeons
                    self._load_tilemap_for_selection() # Update map visualizer on scroll
                elif self.current_tab == "Quests":
                    self.scroll_offset = max(0, self.scroll_offset - self.small_font.get_height() * 2) # Pixel-based scroll, scroll by 2 lines
                    self._load_tilemap_for_selection() # Update map visualizer on scroll
            elif event.button == 5: # Mouse wheel down
                if self.current_tab == "Dungeons":
                    max_scroll = max(0, len(self.dungeon_scenes_data) - self.visible_items)
                    self.scroll_offset = min(max_scroll, self.scroll_offset + 1) # Still item-based for dungeons
                    self._load_tilemap_for_selection() # Update map visualizer on scroll
                elif self.current_tab == "Quests":
                    quest_heights = self._calculate_quest_item_heights(content_rect.width)
                    total_quests_height = sum(quest_heights)
                    max_scroll_offset = max(0, total_quests_height - content_rect.height)
                    self.scroll_offset = min(max_scroll_offset, self.scroll_offset + self.small_font.get_height() * 2) # Pixel-based scroll, scroll by 2 lines
                    self._load_tilemap_for_selection() # Update map visualizer on scroll

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.is_open = False
                return "close"
            elif event.key == pygame.K_UP:
                if self.current_tab == "Dungeons" and self.dungeon_scenes_data:
                    self.selected_option = (self.selected_option - 1) % len(self.dungeon_scenes_data)
                    if self.selected_option < self.scroll_offset:
                        self.scroll_offset = self.selected_option
                    self._load_tilemap_for_selection() # Update map visualizer
                elif self.current_tab == "Quests":
                    all_quests = list(self.game.quest_manager.quests.values())
                    quest_heights = self._calculate_quest_item_heights(content_rect.width)
                    if all_quests:
                        self.selected_option = (self.selected_option - 1) % len(all_quests)
                        # Adjust scroll_offset to make selected item visible
                        cumulative_height_before_selected = sum(quest_heights[:self.selected_option])
                        if cumulative_height_before_selected < self.scroll_offset:
                            self.scroll_offset = cumulative_height_before_selected
                        self._load_tilemap_for_selection() # Update map visualizer
            elif event.key == pygame.K_DOWN:
                if self.current_tab == "Dungeons" and self.dungeon_scenes_data:
                    self.selected_option = (self.selected_option + 1) % len(self.dungeon_scenes_data)
                    if self.selected_option >= self.scroll_offset + self.visible_items:
                        self.scroll_offset = self.selected_option
                    self._load_tilemap_for_selection() # Update map visualizer
                elif self.current_tab == "Quests":
                    all_quests = list(self.game.quest_manager.quests.values())
                    quest_heights = self._calculate_quest_item_heights(content_rect.width)
                    if all_quests:
                        self.selected_option = (self.selected_option + 1) % len(all_quests)
                        # Adjust scroll_offset to make selected item visible
                        cumulative_height_up_to_selected = sum(quest_heights[:self.selected_option + 1])
                        if cumulative_height_up_to_selected > self.scroll_offset + content_rect.height:
                            self.scroll_offset = cumulative_height_up_to_selected - content_rect.height
                        self._load_tilemap_for_selection() # Update map visualizer
            elif event.key == pygame.K_RETURN:
                if self.current_tab == "Dungeons" and self.dungeon_scenes_data:
                    selected_scene = self.dungeon_scenes_data[self.selected_option]['name']
                    self.is_open = False
                    return selected_scene
                elif self.current_tab == "Quests":
                    all_quests = list(self.game.quest_manager.quests.values())
                    if all_quests and all_quests[self.selected_option].is_unlocked: # Only allow action if unlocked
                        selected_quest = all_quests[self.selected_option]
                        self.is_open = False
                        return selected_quest.tilemap_scene_name
        return None

    def draw(self, screen):
        if not self.is_open:
            return

        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2) # Border

        # Draw title (now dynamic based on tab)
        draw_text(screen, "Teleporter", self.title_font.get_height(), (255, 255, 255), self.rect.centerx, self.rect.y + 10, align="center")

        # Draw close button
        close_button_rect = pygame.Rect(self.rect.x + self.rect.width - 30, self.rect.y + 5, 25, 25)
        pygame.draw.rect(screen, (200, 0, 0), close_button_rect)
        draw_text(screen, "X", 20, (255, 255, 255), close_button_rect.centerx, close_button_rect.centery, align="center")

        # Draw tabs
        for i, tab_name in enumerate(self.tabs):
            tab_rect = pygame.Rect(self.rect.x + 10 + i * 100, self.rect.y + 40, 90, 30)
            tab_color = (100, 100, 100) if self.current_tab != tab_name else (70, 70, 70)
            pygame.draw.rect(screen, tab_color, tab_rect)
            pygame.draw.rect(screen, (200, 200, 200), tab_rect, 1)
            draw_text(screen, tab_name, 20, (255, 255, 255), tab_rect.centerx, tab_rect.centery, align="center")

        # Content area for scrollable list
        content_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 75, 300, self.rect.height - 80) # Adjusted width
        pygame.draw.rect(screen, (30, 30, 30), content_rect) # Background for content

        if self.current_tab == "Dungeons":
            # Draw dungeon scene options with graphics (scrollable)
            for i, scene_data in enumerate(self.dungeon_scenes_data):
                # Only draw if the item is within the visible bounds of the content_rect
                item_y_relative_to_content_top = (i - self.scroll_offset) * self.dungeon_item_height
                if item_y_relative_to_content_top < content_rect.height and item_y_relative_to_content_top + self.dungeon_item_height > 0:
                    scene_name = scene_data['name']
                    graphic = self.scene_graphics.get(scene_name)

                    text_color = (255, 255, 255)
                    if i == self.selected_option:
                        text_color = (255, 255, 0) # Highlight selected option

                    item_y = content_rect.y + item_y_relative_to_content_top + 5 # Offset from content_rect top
                    
                    # Draw graphic if available
                    if graphic:
                        graphic_x = content_rect.x + 5
                        graphic_y = item_y
                        screen.blit(graphic, (graphic_x, graphic_y))
                        text_x = graphic_x + 32 + 10 # Offset text by graphic width + padding
                    else:
                        text_x = content_rect.x + 5 # No graphic, start text at the beginning

                    draw_text(screen, scene_name, self.font.get_height(), text_color, text_x, item_y + (32 - self.font.get_height()) // 2, align="left") # Center text vertically with graphic

            # Draw scrollbar
            if len(self.dungeon_scenes_data) > self.visible_items:
                scrollbar_height = content_rect.height
                scrollbar_track_rect = pygame.Rect(content_rect.right - 15, content_rect.y, 10, scrollbar_height)
                pygame.draw.rect(screen, (100, 100, 100), scrollbar_track_rect) # Scrollbar track

                # Calculate thumb height and position
                thumb_height = max(20, scrollbar_height * self.visible_items / len(self.dungeon_scenes_data))
                scroll_range = len(self.dungeon_scenes_data) - self.visible_items
                if scroll_range > 0:
                    thumb_y = scrollbar_track_rect.y + (scrollbar_height - thumb_height) * self.scroll_offset / scroll_range
                else:
                    thumb_y = scrollbar_track_rect.y # No scrolling needed, thumb at top

                scrollbar_thumb_rect = pygame.Rect(content_rect.right - 15, thumb_y, 10, thumb_height)
                pygame.draw.rect(screen, (150, 150, 150), scrollbar_thumb_rect) # Scrollbar thumb
        elif self.current_tab == "Quests":
            # Create a sub-surface for the quest content to enable clipping
            content_surface = pygame.Surface(content_rect.size, pygame.SRCALPHA)
            content_surface.fill((30, 30, 30)) # Fill with background color

            all_quests = list(self.game.quest_manager.quests.values()) # Get all quests
            quest_heights = self._calculate_quest_item_heights(content_rect.width) # Get dynamic heights

            current_y_in_content_surface = 0
            for i, quest_data in enumerate(all_quests):
                item_height = quest_heights[i]

                # Calculate y position relative to the content_surface
                relative_item_y = current_y_in_content_surface - self.scroll_offset

                # Only draw if the item is within the visible bounds of the content_surface
                if relative_item_y < content_rect.height and relative_item_y + item_height > 0:
                    quest_name = quest_data.title
                    quest_description = quest_data.description
                    is_unlocked = quest_data.is_unlocked

                    text_color = (255, 255, 255)
                    if not is_unlocked:
                        text_color = (100, 100, 100) # Grey out if locked
                    elif i == self.selected_option:
                        text_color = (255, 255, 0) # Highlight selected option if unlocked and selected

                    # Draw quest title on content_surface
                    draw_text(content_surface, quest_name, self.font.get_height(), text_color, 5, relative_item_y, align="left")

                    # Draw wrapped quest description on content_surface
                    description_y = relative_item_y + self.font.get_height() + 2 # Start description below title with a little padding
                    description_max_width = content_rect.width - 10 # Content rect width minus padding
                    wrapped_description_lines = self._wrap_text(quest_description, self.small_font, description_max_width)
                    
                    for line_num, line in enumerate(wrapped_description_lines):
                        draw_text(content_surface, line, self.small_font.get_height(), text_color, 5, description_y + line_num * self.small_font.get_height(), align="left")
                
                current_y_in_content_surface += item_height # Accumulate height for next item

            # Blit the content_surface onto the main screen
            screen.blit(content_surface, content_rect.topleft)

            # Draw scrollbar for quests
            total_quests_height = sum(quest_heights)
            if total_quests_height > content_rect.height:
                scrollbar_height = content_rect.height
                scrollbar_track_rect = pygame.Rect(content_rect.right - 15, content_rect.y, 10, scrollbar_height)
                pygame.draw.rect(screen, (100, 100, 100), scrollbar_track_rect) # Scrollbar track

                # Calculate thumb height and position
                thumb_height = max(20, scrollbar_height * content_rect.height / total_quests_height)
                max_scroll_offset = max(0, total_quests_height - content_rect.height)
                if max_scroll_offset > 0:
                    thumb_y = scrollbar_track_rect.y + (scrollbar_height - thumb_height) * self.scroll_offset / max_scroll_offset
                else:
                    thumb_y = scrollbar_track_rect.y # No scrolling needed, thumb at top

                scrollbar_thumb_rect = pygame.Rect(content_rect.right - 15, thumb_y, 10, thumb_height)
                pygame.draw.rect(screen, (150, 150, 150), scrollbar_thumb_rect) # Scrollbar thumb

        # Draw map visualizer
        if self.map_visualizer_surface:
            visualizer_x = self.rect.x + content_rect.width + 15 # Position to the right of the content list
            visualizer_y = self.rect.y + 75 # Align with the top of the content list
            
            # Create a sub-surface for the visualizer area to handle clipping
            visualizer_area_width = self.rect.width - content_rect.width - 20 # Total menu width - list width - padding
            visualizer_area_height = self.rect.height - 80 # Same height as content list
            visualizer_area_rect = pygame.Rect(visualizer_x, visualizer_y, visualizer_area_width, visualizer_area_height)
            
            pygame.draw.rect(screen, (20, 20, 20), visualizer_area_rect) # Background for visualizer

            # Calculate position to center the map_visualizer_surface within the visualizer_area_rect
            scaled_map_width = self.map_visualizer_surface.get_width()
            scaled_map_height = self.map_visualizer_surface.get_height()
            
            map_x = visualizer_area_rect.x + (visualizer_area_rect.width - scaled_map_width) // 2
            map_y = visualizer_area_rect.y + (visualizer_area_rect.height - scaled_map_height) // 2
            
            screen.blit(self.map_visualizer_surface, (map_x, map_y))