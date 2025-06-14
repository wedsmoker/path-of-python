import heapq
from config.constants import TILE_SIZE

class Pathfinding:
    """
    Finds paths using the A* algorithm.
    """
    def __init__(self, game):
        """
        Initializes the pathfinding algorithm.
        Args:
            game: The GameEngine object.
        """
        self.game = game
        self.tile_size = TILE_SIZE  # Assuming tile size is 32
        self.open_set_counter = 0

    def heuristic(self, start, end):
        """
        Calculates the Manhattan distance heuristic.
        """
        return abs(start[0] - end[0]) + abs(start[1] - end[1])

    def find_path(self, start_tile, end_tile):
        """
        Finds a path from start_world_pos to end_world_pos using A* algorithm.
        Ignores all boundaries by treating all tiles as walkable.
        """
        #start_tile = (int(start_world_pos[0] // self.tile_size), int(start_world_pos[1] // self.tile_size))
        #end_tile = (int(end_world_pos[0] // self.tile_size), int(end_world_pos[1] // self.tile_size))

        print(f"Pathfinding: find_path called with start_tile={start_tile}, end_tile={end_tile}")

        open_set = []
        self.open_set_counter = 0
        heapq.heappush(open_set, (0, self.open_set_counter, start_tile))  # (f_score, tiebreaker, tile)
        self.open_set_counter += 1

        came_from = {}
        g_score = {start_tile: 0}
        f_score = {start_tile: self.heuristic(start_tile, end_tile)}

        while open_set:
            current_f_score, _, current_tile = heapq.heappop(open_set)

            print(f"Pathfinding: current_tile={current_tile}, end_tile={end_tile}")

            if current_tile == end_tile:
                print(f"Pathfinding: Path found! Path: {self._reconstruct_path(came_from, current_tile)}")
                return self._reconstruct_path(came_from, current_tile)

            for neighbor_offset in [(0, 1), (0, -1), (1, 0), (-1, 0)]: # 4-directional movement
                neighbor_tile = (current_tile[0] + neighbor_offset[0], current_tile[1] + neighbor_offset[1])

                # Check if neighbor is within map bounds and is walkable
                if not (0 <= neighbor_tile[0] < self.game.scene_manager.current_scene.map_width and \
                        0 <= neighbor_tile[1] < self.game.scene_manager.current_scene.map_height):
                    continue # Skip if out of bounds

                # Check if the neighbor tile is walkable
                tile_map = self.game.scene_manager.current_scene.tile_map
                tile_type = tile_map[neighbor_tile[1]][neighbor_tile[0]]
                if tile_type in ('mountain', 'building', 'rubble'):
                    continue  # Skip if it's a wall

                tentative_g_score = g_score[current_tile] + 1 # Cost to move to neighbor is 1

                if neighbor_tile not in g_score or tentative_g_score < g_score[neighbor_tile]:
                    came_from[neighbor_tile] = current_tile
                    g_score[neighbor_tile] = tentative_g_score
                    f_score[neighbor_tile] = tentative_g_score + self.heuristic(neighbor_tile, end_tile)
                    heapq.heappush(open_set, (f_score[neighbor_tile], self.open_set_counter, neighbor_tile))
                    self.open_set_counter += 1
        print(f"Pathfinding: No path found")
        return None # No path found

    def _reconstruct_path(self, came_from, current_tile):
        """
        Reconstructs the path from the came_from dictionary.
        """
        path = [current_tile]
        while current_tile in came_from:
            current_tile = came_from[current_tile]
            path.append(current_tile)
        path.reverse()
        return path