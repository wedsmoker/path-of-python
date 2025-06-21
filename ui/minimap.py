import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
import math
from entities.npc import NPC  # Import NPC class
from entities.boss_portal import BossPortal
from entities.enemy import Enemy

class Minimap:
    def __init__(self, player, entities, scene, minimap_size=(250, 250), nearby_radius=100):
        self.player = player
        self.entities = entities  # This will need to be updated by the scene
        self.scene = scene  # Store the scene
        self.minimap_size = minimap_size
        self.nearby_radius = nearby_radius
        self.image = pygame.Surface(self.minimap_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        # Position the minimap in the top right corner
        self.rect.topright = (SCREEN_WIDTH - 10, 10)

        self.tilemap_cache = None  # Add tilemap cache
        self.last_scene = None  # Track the last scene
        self.enlarged = False
        self.enlarge_button_rect = None
        self.close_button_rect = None
        self.portal_glow_radius = 20  # Initial glow radius
        self.portal_glow_direction = 1  # 1 for increasing, -1 for decreasing

    def update(self, entities, scene):
        # Update the list of entities (called by the scene or HUD)
        self.entities = entities
        self.scene = scene  # Update the scene
        self._update_portal_glow() # Update portal glow every frame
        self._render_minimap()
        self.last_scene = self.scene  # Update last_scene AFTER rendering

    def _update_portal_glow(self):
        self.portal_glow_radius += 0.5 * self.portal_glow_direction # Increased rate of change
        if self.portal_glow_radius > 40: # Increased maximum radius
            self.portal_glow_direction = -1
        elif self.portal_glow_radius < 10:
            self.portal_glow_direction = 1

    def _render_tilemap(self):
        # Check if the scene has changed or if the tilemap_cache is invalid
        if self.scene != self.last_scene or self.tilemap_cache is None:
            # Ensure the scene has a tile_map and tile_images
            if not hasattr(self.scene, 'tile_map') or not hasattr(self.scene, 'tile_images'):
                return

            tile_map = self.scene.tile_map
            tile_images = self.scene.tile_images

            # Calculate the size of the full map in pixels
            map_width = len(tile_map[0]) * TILE_SIZE
            map_height = len(tile_map) * TILE_SIZE

            # Create a surface for the entire tilemap
            full_tilemap = pygame.Surface((map_width, map_height), pygame.SRCALPHA)

            # Iterate through the tilemap and draw each tile
            for y, row in enumerate(tile_map):
                for x, tile_type in enumerate(row):
                    tile_image = tile_images.get(tile_type)
                    if tile_image:
                        full_tilemap.blit(tile_image, (x * TILE_SIZE, y * TILE_SIZE))

            # Scale the entire tilemap to the minimap size
            self.tilemap_cache = pygame.transform.scale(full_tilemap, self.minimap_size)

            self.last_scene = self.scene  # Update the last scene

    def _render_minimap(self):
        # Clear the minimap surface
        self.image.fill((0, 0, 0, 128))  # Semi-transparent black background

        # Calculate scaling factor for the full map
        if hasattr(self.scene, 'tile_map'):
            map_width = len(self.scene.tile_map[0]) * TILE_SIZE
            map_height = len(self.scene.tile_map[0]) * TILE_SIZE

            # Get zoom value from the scene
            zoom = getattr(self.scene, 'zoom_level', 1.0)  # Default to 1.0 if zoom is not defined

            # Calculate player position on the minimap
            player_x = (self.player.rect.centerx / map_width) * self.minimap_size[0] / 2
            player_y = (self.player.rect.centery / map_height) * self.minimap_size[1] / 2

            # Ensure the player's position stays within the bounds of the minimap
            player_x = max(0, min(player_x, self.minimap_size[0]))
            player_y = max(0, min(player_y, self.minimap_size[1]))

        # Draw player (center of the minimap view)
        player_pos_on_minimap = (self.minimap_size[0] // 2, self.minimap_size[1] // 2)
        # Render the tilemap from the cache
        self._render_tilemap()
        if self.tilemap_cache:
            self.image.blit(self.tilemap_cache, (0, 0))

            # Draw player
            pygame.draw.circle(self.image, (0, 255, 0), (int(player_x), int(player_y)), 5)  # Green dot for player

        # Draw nearby entities
        for entity in self.entities:
            # Assuming entities have a 'rect' attribute with x, y position
            entity_pos = (entity.rect.centerx, entity.rect.centery)
            player_pos = (self.player.rect.centerx, self.player.rect.centery)

            distance = math.dist(player_pos, entity_pos)

            # Calculate position relative to player
            relative_pos = (entity_pos[0] - player_pos[0], entity_pos[1] - player_pos[1])

            # Scale position to minimap size
            # We need a scaling factor. Let's map the nearby_radius to half the minimap size.
            scale_factor = (self.minimap_size[0] / 2) / self.nearby_radius
            scaled_pos = (relative_pos[0] * scale_factor, relative_pos[1] * scale_factor)

            # Translate to minimap coordinates (relative to the center)
            minimap_x = player_pos_on_minimap[0] + scaled_pos[0]
            minimap_y = player_pos_on_minimap[1] + scaled_pos[1]

            # Ensure the dot is within the minimap bounds
            if 0 <= minimap_x < self.minimap_size[0] and 0 <= minimap_y < self.minimap_size[1]:
                # Determine color based on entity type
                color = (255, 255, 255)  # Default white dot for unknown types
                if isinstance(entity, NPC):
                    color = (0, 0, 255)  # Blue for NPC
                elif isinstance(entity, BossPortal):
                    color = (255, 0, 0)  # Red for BossPortal
                    # Draw multiple concentric circles for glow effect
                    num_glow_circles = 5
                    for i in range(1, num_glow_circles + 1):
                        glow_radius = int(self.portal_glow_radius * (num_glow_circles + 1 - i) / num_glow_circles)
                        glow_color = [255, 0, 0]  # Bright red
                        glow_color.append(int(200 / i))  # Adjust alpha value
                        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
                        self.image.blit(glow_surface, (int(minimap_x) - glow_radius, int(minimap_y) - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)

                    pygame.draw.circle(self.image, color, (int(minimap_x), int(minimap_y)), 3)  # Draw entity dot on top of glow
                elif isinstance(entity, Enemy):
                    color = (255, 255, 0) # Yellow for Enemy
                else:
                    color = (255, 255, 255) # White for other entities

                pygame.draw.circle(self.image, color, (int(minimap_x), int(minimap_y)), 3)  # Draw entity dot

        # Draw dungeon portal arrows (only for the teleporter menu portal)
        if hasattr(self.scene, 'portals'):
            for portal in self.scene.portals:
                if isinstance(portal, BossPortal):
                    continue  # Skip BossPortals
                if portal.get('target_scene') == "teleporter_menu":  # Only draw the teleporter portal
                    portal_x = portal.get("location", [0, 0])[0]
                    portal_y = portal.get("location", [0, 0])[1]
                    portal_pos = (portal_x, portal_y)
                    player_pos = (self.player.rect.centerx, self.player.rect.centery)
                    relative_pos = (portal_pos[0] - player_pos[0], portal_pos[1] - player_pos[1])

                    # Normalize the relative position
                    distance = math.dist(player_pos, portal_pos)
                    if distance > 0:
                        normalized_pos = (relative_pos[0] / distance, relative_pos[1] / distance)
                    else:
                        normalized_pos = (0, 0)

                    # Scale the normalized position to the minimap size
                    arrow_x = player_pos_on_minimap[0] + normalized_pos[0] * (self.minimap_size[0] / 2)
                    arrow_y = player_pos_on_minimap[1] + normalized_pos[1] * (self.minimap_size[1] / 2)

                    # Draw the arrow regardless of whether it's within the minimap bounds
                    arrow_color = (255, 100, 0)  # Orange arrow for portal
                    arrow_points = self._get_arrow_points(player_pos_on_minimap, (int(arrow_x), int(arrow_y)), 10)
                    pygame.draw.polygon(self.image, arrow_color, arrow_points)

        # Draw NPC arrows
        for entity in self.entities:
            if isinstance(entity, NPC):
                npc_pos = (entity.rect.centerx, entity.rect.centery)
                player_pos = (self.player.rect.centerx, self.player.rect.centery)
                relative_pos = (npc_pos[0] - player_pos[0], npc_pos[1] - player_pos[1])

                # Normalize the relative position
                distance = math.dist(player_pos, npc_pos)
                if distance > 0:
                    normalized_pos = (relative_pos[0] / distance, relative_pos[1] / distance)
                else:
                    normalized_pos = (0, 0)

                # Scale the normalized position to the minimap size
                arrow_x = player_pos_on_minimap[0] + normalized_pos[0] * (self.minimap_size[0] / 2)
                arrow_y = player_pos_on_minimap[1] + normalized_pos[1] * (self.minimap_size[1] / 2)

                # Draw the arrow regardless of whether it's within the minimap bounds
                arrow_color = (100, 0, 255)  # Purple arrow for NPC
                arrow_points = self._get_arrow_points(player_pos_on_minimap, (int(arrow_x), int(arrow_y)), 10)
                pygame.draw.polygon(self.image, arrow_color, arrow_points)

        # Draw enlarge button
        if not self.enlarged:
            button_color = (100, 100, 100)
            text_color = (255, 255, 255)
            button_width = 20
            button_height = 20
            button_x = self.minimap_size[0] - button_width - 5
            button_y = 5
            self.enlarge_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            pygame.draw.rect(self.image, button_color, self.enlarge_button_rect)
            font = pygame.font.Font(None, 20)
            text_surface = font.render("+", True, text_color)
            text_rect = text_surface.get_rect(center=self.enlarge_button_rect.center)
            self.image.blit(text_surface, text_rect)

    def _get_arrow_points(self, start, end, size):
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        point1 = (end[0] - size * math.cos(angle), end[1] - size * math.sin(angle))
        angle_left = angle + math.pi / 6
        point2 = (end[0] - size / 2 * math.cos(angle_left), end[1] - size / 2 * math.sin(angle_left))
        angle_right = angle - math.pi / 6
        point3 = (end[0] - size / 2 * math.cos(angle_right), end[1] - size / 2 * math.sin(angle_right))
        return (end, point1, point2, point3)

    def draw(self, screen):
        if self.enlarged:
            # Draw enlarged minimap background
            enlarged_size = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            enlarged_rect = pygame.Rect(0, 0, enlarged_size[0], enlarged_size[1])
            enlarged_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            pygame.draw.rect(screen, (0, 0, 0), enlarged_rect)

            # Scale the cached tilemap
            enlarged_image = pygame.transform.scale(self.tilemap_cache, enlarged_size)
            screen.blit(enlarged_image, enlarged_rect)

            # Calculate scaling factor for the full map
            if hasattr(self.scene, 'tile_map'):
                map_width = len(self.scene.tile_map[0]) * TILE_SIZE
                map_height = len(self.scene.tile_map[0]) * TILE_SIZE

                # Get zoom value from the scene
                zoom = getattr(self.scene, 'zoom_level', 1.0)  # Default to 1.0 if zoom is not defined

                # Calculate player position on the enlarged map
                player_x = (self.player.rect.centerx / map_width) * enlarged_size[0] / 2
                player_y = (self.player.rect.centery / map_height) * enlarged_size[1] / 2

                # Ensure the player's position stays within the bounds of the enlarged map
                player_x = max(0, min(player_x, enlarged_size[0]))
                player_y = max(0, min(player_y, enlarged_size[1]))

                # Draw the player's position on the enlarged map
                pygame.draw.circle(screen, (0, 255, 0), (int(player_x + enlarged_rect.left), int(player_y + enlarged_rect.top)), 5)

                # Draw entities on the enlarged map
                for entity in self.entities:
                    entity_pos = (entity.rect.centerx, entity.rect.centery)
                    # Calculate position on the enlarged map
                    entity_x = (entity.rect.centerx / map_width) * enlarged_size[0]
                    entity_y = (entity.rect.centery / map_height) * enlarged_size[1]

                    # Ensure the entity's position stays within the bounds of the enlarged map
                    entity_x = max(0, min(entity_x, enlarged_size[0]))
                    entity_y = max(0, min(entity_y, enlarged_size[1]))

                    # Determine color based on entity type
                    color = (255, 255, 255)  # Default white dot for unknown types
                    if isinstance(entity, NPC):
                        color = (0, 0, 255)  # Blue for NPC
                    elif isinstance(entity, BossPortal):
                        color = (255, 0, 0)  # Red for BossPortal
                        # Draw multiple concentric circles for glow effect
                        num_glow_circles = 5
                        for i in range(1, num_glow_circles + 1):
                            glow_radius = int(self.portal_glow_radius * (num_glow_circles + 1 - i) / num_glow_circles)
                            glow_color = [255, 0, 0]  # Bright red
                            glow_color.append(int(200 / i))  # Adjust alpha value
                            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
                            screen.blit(glow_surface, (int(entity_x + enlarged_rect.left) - glow_radius, int(entity_y + enlarged_rect.top) - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)

                        pygame.draw.circle(screen, color, (int(entity_x + enlarged_rect.left), int(entity_y + enlarged_rect.top)), 3)  # Draw entity dot on top of glow
                    elif isinstance(entity, Enemy):
                        color = (255, 255, 0) # Yellow for Enemy
                    else:
                        color = (255, 255, 255) # White for other entities

                    # Draw the entity's position on the enlarged map
                    pygame.draw.circle(screen, color, (int(entity_x + enlarged_rect.left), int(entity_y + enlarged_rect.top)), 3)

            # Draw close button
            close_button_size = 20
            close_button_x = enlarged_rect.right - close_button_size
            close_button_y = enlarged_rect.top
            self.close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)
            pygame.draw.rect(screen, (200, 0, 0), self.close_button_rect)
            font = pygame.font.Font(None, 20)
            text_surface = font.render("X", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.close_button_rect.center)
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(self.image, self.rect)

    def handle_event(self, event, minimap_rect):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.enlarged:
                # Calculate screen position of close button
                close_button_size = 20
                enlarged_size = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                enlarged_rect = pygame.Rect(0, 0, enlarged_size[0], enlarged_size[1])
                enlarged_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                close_button_x = enlarged_rect.right - close_button_size
                close_button_y = enlarged_rect.top
                close_button_screen_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)

                if close_button_screen_rect.collidepoint(event.pos):
                    self.enlarged = False
            else:
                # Check enlarge button click
                if self.enlarge_button_rect:
                    # Calculate relative position to the minimap
                    relative_x = event.pos[0] - minimap_rect.x
                    relative_y = event.pos[1] - minimap_rect.y
                    if self.enlarge_button_rect.collidepoint(relative_x, relative_y):
                        self.enlarged = True