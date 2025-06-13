import pygame
import random
import json
from noise import pnoise2

def load_tileset(tileset_path):
    """Loads a tileset from a JSON file and returns a dictionary of tile names to Pygame surfaces."""
    with open(tileset_path, 'r') as f:
        tileset_data = json.load(f)

    tileset = {}
    for tile_name, tile_path in tileset_data.items():
        tile_image = pygame.image.load(tile_path).convert_alpha()
        tileset[tile_name] = tile_image
    return tileset

def load_enemy_data(enemy_data_path):
    """Loads enemy data from a JSON file and returns a dictionary of enemy types to data."""
    with open(enemy_data_path, 'r') as f:
        enemy_data = json.load(f)
    return enemy_data

def translate_tile_type(tile_type, tileset_mapping):
    """Translates a tile type to a specific tile based on the tileset mapping."""
    return tileset_mapping.get(tile_type, 'unknown')

def generate_perlin_noise_map(width, height, threshold, scale=10.0, octaves=6, persistence=0.5, lacunarity=2.0, noise_multiplier=5.0):
    """Generates a tile map using Perlin noise."""
    tile_map = [['floor' for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            noise_val = pnoise2(x / scale, y / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity) * noise_multiplier
            if noise_val > threshold:
                tile_map[y][x] = 'wall'
    return tile_map

def generate_room_based_map(width, height, room_count=10, min_room_size=5, max_room_size=10):
    """Generates a tile map using a room-based algorithm."""
    tile_map = [['wall' for _ in range(width)] for _ in range(height)]
    rooms = []

    for _ in range(room_count):
        room_width = random.randint(min_room_size, max_room_size)
        room_height = random.randint(min_room_size, max_room_size)
        x = random.randint(1, width - room_width - 1)
        y = random.randint(1, height - room_height - 1)

        room = {'x': x, 'y': y, 'width': room_width, 'height': room_height}
        rooms.append(room)

        # Carve out the room
        for i in range(x, x + room_width):
            for j in range(y, y + room_height):
                tile_map[j][i] = 'floor'

    # Connect the rooms with corridors (simple approach: connect each room to the next)
    for i in range(len(rooms) - 1):
        room1 = rooms[i]
        room2 = rooms[i + 1]
        # Connect the centers of the rooms
        x1 = room1['x'] + room1['width'] // 2
        y1 = room1['y'] + room1['height'] // 2
        x2 = room2['x'] + room2['width'] // 2
        y2 = room2['y'] + room2['height'] // 2
        # Carve a path between the rooms
        while x1 != x2:
            tile_map[y1][x1] = 'floor'
            x1 += 1 if x1 < x2 else -1
        while y1 != y2:
            tile_map[y1][x1] = 'floor'
            y1 += 1 if y1 < y2 else -1

    return tile_map

def place_portal(tile_map, portal_graphic, placement="random", x=None, y=None):
    """Places a portal on the tile map."""
    if placement == "random":
        # Find a random floor tile
        floor_tiles = []
        for row_index, row in enumerate(tile_map):
            for col_index, tile in enumerate(row):
                if tile == 'floor':
                    floor_tiles.append((col_index, row_index))

        if not floor_tiles:
            print("No floor tiles found to place the portal.")
            return tile_map

        portal_x, portal_y = random.choice(floor_tiles)
    elif placement == "specific" and x is not None and y is not None:
        portal_x, portal_y = x, y
    else:
        print("Invalid portal placement parameters.")
        return tile_map

    # Place the portal
    tile_map[portal_y][portal_x] = 'portal'
    return tile_map, portal_x, portal_y

def add_decorations(tile_map, decorations):
    """Adds decorations to the tile map."""
    for decoration in decorations:
        # Find a random floor tile
        floor_tiles = []
        for row_index, row in enumerate(tile_map):
            for col_index, tile in enumerate(row):
                if tile == 'floor':
                    floor_tiles.append((col_index, row_index))

        if not floor_tiles:
            print("No floor tiles found to place decorations.")
            continue

        decoration_x, decoration_y = random.choice(floor_tiles)
        tile_map[decoration_y][decoration_x] = 'decoration'
    return tile_map
def place_enemies(tile_map, enemy_types, enemy_data, num_enemies):
    """Places enemies on random floor tiles."""
    floor_tiles = []
    for row_index, row in enumerate(tile_map):
        for col_index, tile in enumerate(row):
            if tile == 'floor':
                floor_tiles.append((col_index, row_index))

    if not floor_tiles:
        print("No floor tiles found to place enemies.")
        return []

    placed_enemies = []
    for _ in range(num_enemies):
        if not floor_tiles:
            break # No more floor tiles to place enemies

        enemy_x, enemy_y = random.choice(floor_tiles)
        floor_tiles.remove((enemy_x, enemy_y)) # Ensure enemies don't spawn on the same tile

        # Choose a random enemy type from the allowed types for this dungeon
        chosen_enemy_type = random.choice(enemy_types)
        
        # Get enemy details from enemy_data.json
        enemy_details = enemy_data.get(chosen_enemy_type)
        if enemy_details:
            placed_enemies.append({
                'type': chosen_enemy_type,
                'x': enemy_x,
                'y': enemy_y,
                'health': enemy_details['health'],
                'damage': enemy_details['damage'],
                'speed': enemy_details['speed'],
                'sprite_path': enemy_details['sprite_path']
            })
        else:
            print(f"Warning: Enemy type '{chosen_enemy_type}' not found in enemy_data.json")

    return placed_enemies

def generate_new_dungeon(params):
    """Generates a new dungeon based on the given parameters."""
    width = params['width']
    height = params['height']
    tileset_name = params['tileset']
    enemy_types = params['enemy_types']
    name = params['name']
    portal_graphic = params['portal_graphic']
    map_algorithm = params['map_algorithm']
    portal_placement = params['portal_placement']
    portal_x = params.get('portal_x')
    portal_y = params.get('portal_y')
    decorations = params['decorations']
    perlin_noise_threshold = params.get('perlin_noise_threshold', 0.0)

    # Load tileset and enemy data
    tileset_path = f'data/tilesets/{tileset_name}_tileset.json'
    tileset = load_tileset(tileset_path)
    enemy_data_path = 'data/enemy_data.json'
    enemy_data = load_enemy_data(enemy_data_path)

    # Load tileset mapping
    with open('data/tileset_mappings.json', 'r') as f:
        tileset_mappings = json.load(f)
    tileset_mapping = tileset_mappings.get(tileset_name, tileset_mappings['default'])

    # Generate tile map
    if map_algorithm == 'perlin_noise':
        tile_map = generate_perlin_noise_map(width, height, perlin_noise_threshold)
    elif map_algorithm == 'room_based':
        tile_map = generate_room_based_map(width, height)
    else:
        raise ValueError(f"Unknown map algorithm: {map_algorithm}")

    # Place portal
    tile_map, portal_x, portal_y = place_portal(tile_map, portal_graphic, portal_placement, portal_x, portal_y)

    # Add decorations
    tile_map = add_decorations(tile_map, decorations)

    # Create dungeon data
    # Place enemies
    num_enemies = params.get('num_enemies', 5) # Default to 5 enemies if not specified
    enemies = place_enemies(tile_map, enemy_types, enemy_data, num_enemies)

    # Create dungeon data
    dungeon_data = {
        'width': width,
        'height': height,
        'tileset': tileset_name,
        'tile_map': tile_map,
        'enemy_types': enemy_types,
        'name': name,
        'portal_graphic': portal_graphic,
        'map_algorithm': map_algorithm,
        'portal_placement': portal_placement,
        'portal_x': portal_x,
        'portal_y': portal_y,
        'decorations': decorations,
        'enemies': enemies
    }

    return dungeon_data

def save_dungeon_data(dungeon_data, filename):
    """Saves dungeon data to a JSON file."""
    filepath = f'data/dungeons/{filename}.json'
    with open(filepath, 'w') as f:
        json.dump(dungeon_data, f, indent=4)
    print(f"Dungeon data saved to {filepath}")