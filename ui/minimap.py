import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
import math
from entities.npc import NPC # Import NPC class

class Minimap:
    def __init__(self, player, entities, scene, minimap_size=(250, 250), nearby_radius=600):
        self.player = player
        self.entities = entities # This will need to be updated by the scene
        self.scene = scene # Store the scene
        self.minimap_size = minimap_size
        self.nearby_radius = nearby_radius
        self.image = pygame.Surface(self.minimap_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        # Position the minimap in the top right corner
        self.rect.topright = (SCREEN_WIDTH - 10, 10)

    def update(self, entities):
        # Update the list of entities (called by the scene or HUD)
        self.entities = entities
        self._render_minimap()

    def _render_minimap(self):
        # Clear the minimap surface
        self.image.fill((0, 0, 0, 128)) # Semi-transparent black background

        # Draw player (center of the minimap view)
        player_pos_on_minimap = (self.minimap_size[0] // 2, self.minimap_size[1] // 2)
        pygame.draw.circle(self.image, (0, 255, 0), player_pos_on_minimap, 5) # Green dot for player

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
                color = (255, 255, 255) # Default white dot for unknown types
                if isinstance(entity, NPC):
                    color = (0, 0, 255) # Blue for NPC

                pygame.draw.circle(self.image, color, (int(minimap_x), int(minimap_y)), 3) # Draw entity dot

        # Draw dungeon portal arrow
        if self.scene.dungeon_portal_rect:
            portal_pos = (self.scene.dungeon_portal_rect.centerx, self.scene.dungeon_portal_rect.centery)
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
        for npc in self.scene.npcs:
            npc_pos = (npc.rect.centerx, npc.rect.centery)
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

    def _get_arrow_points(self, start, end, size):
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        point1 = (end[0] - size * math.cos(angle), end[1] - size * math.sin(angle))
        angle_left = angle + math.pi / 6
        point2 = (end[0] - size/2 * math.cos(angle_left), end[1] - size/2 * math.sin(angle_left))
        angle_right = angle - math.pi / 6
        point3 = (end[0] - size/2 * math.cos(angle_right), end[1] - size/2 * math.sin(angle_right))
        return (end, point1, point2, point3)

    def draw(self, screen):
        screen.blit(self.image, self.rect)