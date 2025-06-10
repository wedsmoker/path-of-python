import random
import noise

class MapGenerator:
    """Generates procedural maps for the game."""

    def __init__(self, width, height, seed=None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 10000)
        random.seed(self.seed)

    def generate_map(self):
        """Generate a procedural map."""
        map_data = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Generate terrain based on Perlin noise
                noise_value = noise.pnoise2(x / self.width,
                                           y / self.height,
                                           octaves=8,
                                           persistence=0.6,
                                           lacunarity=2.0,
                                           repeatx=1024,
                                           repeaty=1024,
                                           base=self.seed)

                # Assign tile types based on noise value, using available tile assets
                if noise_value < -0.3:
                    tile_type = 'water'
                elif noise_value < -0.2:
                    tile_type = 'sand'
                elif noise_value < 0.1:
                    tile_type = 'grass'
                elif noise_value < 0.3:
                    tile_type = 'forest'
                elif noise_value < 0.4:
                    tile_type = 'mountain'
                elif noise_value < 0.5:
                    tile_type = 'building'
                elif noise_value < 0.6:
                    tile_type = 'street'
                else:
                    tile_type = 'rubble'

                row.append(tile_type)
            map_data.append(row)

        return map_data

    def generate_entities(self, map_data):
        """Generate entities (enemies, NPCs, etc.) on the map."""
        entities = []

        for y in range(self.height):
            for x in range(self.width):
                tile_type = map_data[y][x]

                # Spawn entities based on terrain type
                if tile_type == 'grass' and random.random() < 0.05:
                    entities.append({
                        'type': 'enemy',
                        'x': x,
                        'y': y,
                        'name': 'Forest Goblin'
                    })
                elif tile_type == 'grass' and random.random() < 0.1:
                    entities.append({
                        'type': 'npc',
                        'x': x,
                        'y': y,
                        'name': 'Villager'
                    })

        return entities

    def generate_structures(self, map_data):
        """Generate structures (houses, dungeons, etc.) on the map."""
        structures = []

        for y in range(self.height):
            for x in range(self.width):
                tile_type = map_data[y][x]

                # Spawn structures based on terrain type
                if tile_type == 'grass' and random.random() < 0.001:
                    structures.append({
                        'type': 'house',
                        'x': x,
                        'y': y
                    })
                elif tile_type == 'forest' and random.random() < 0.0005:
                    structures.append({
                        'type': 'dungeon',
                        'x': x,
                        'y': y
                    })

        return structures

    def generate_decorations(self, map_data):
        """Generate decorations (trees, rocks, etc.) on the map."""
        decorations = []

        for y in range(self.height):
            for x in range(self.width):
                tile_type = map_data[y][x]

                # Spawn decorations based on terrain type
                if tile_type == 'forest' and random.random() < 0.05:
                    decorations.append({
                        'type': 'tree',
                        'x': x,
                        'y': y,
                        'variation': random.choice(['oak', 'pine', 'birch'])
                    })
                elif tile_type == 'grass' and random.random() < 0.02:
                    decorations.append({
                        'type': 'rock',
                        'x': x,
                        'y': y,
                        'size': random.choice(['small', 'medium', 'large'])
                    })
                elif tile_type == 'sand' and random.random() < 0.01:
                    decorations.append({
                        'type': 'cactus',
                        'x': x,
                        'y': y,
                        'size': random.choice(['small', 'medium', 'large'])
                    })

        return decorations

    def generate_villages(self, map_data):
        """Generate villages on the map."""
        villages = []

        # Find suitable locations for villages (near water sources)
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if (map_data[y][x] == 'grass' and
                    (map_data[y-1][x] == 'water' or
                     map_data[y+1][x] == 'water' or
                     map_data[y][x-1] == 'water' or
                     map_data[y][x+1] == 'water')):

                    if random.random() < 0.001:  # Rare chance to spawn a village
                        village_center = {'x': x, 'y': y}
                        villages.append(village_center)

                        # Add houses around the village center
                        for i in range(5):  # Add 5 houses
                            house_x = village_center['x'] + random.randint(-3, 3)
                            house_y = village_center['y'] + random.randint(-3, 3)
                            if 0 <= house_x < self.width and 0 <= house_y < self.height:
                                map_data[house_y][house_x] = 'building' # Changed to 'building' for consistency

        return villages

    def generate_ruins(self, map_data):
        """Generate ancient ruins on the map."""
        ruins = []

        # Find suitable locations for ruins (in forests)
        for y in range(self.height):
            for x in range(self.width):
                if map_data[y][x] == 'forest' and random.random() < 0.0005:
                    ruins.append({'x': x, 'y': y})
                    # Mark the area as ruins
                    for dy in range(-2, 3):
                        for dx in range(-2, 3):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                map_data[ny][nx] = 'rubble' # Changed to 'rubble' for consistency

        return ruins

    def generate_caves(self, map_data):
        """Generate cave entrances on the map."""
        caves = []

        # Find suitable locations for caves (in forests)
        for y in range(self.height):
            for x in range(self.width):
                tile_type = map_data[y][x]
                if tile_type == 'forest' and random.random() < 0.001:
                    caves.append({'x': x, 'y': y})
                    # Mark the area as cave entrance
                    map_data[y][x] = 'building' # Using 'building' as a generic structure for now

        return caves

    def generate_roads(self, map_data):
        """Generate roads on the map."""
        roads = []
        num_roads = 5  # Number of roads to generate

        for _ in range(num_roads):
            start_x, start_y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            end_x, end_y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)

            # Simple pathfinding (straight line)
            x, y = start_x, start_y
            while x != end_x or y != end_y:
                if random.random() < 0.5:
                    x += 1 if x < end_x else -1 if x > end_x else 0
                else:
                    y += 1 if y < end_y else -1 if y > end_y else 0

                if 0 <= x < self.width and 0 <= y < self.height:
                    map_data[y][x] = 'street'  # Use 'street' tile for roads
                    roads.append({'x': x, 'y': y})

        return roads

    def generate_shops(self, map_data):
        """Generate shops on the map."""
        shops = []
        num_shops = 3  # Number of shops to generate

        for _ in range(num_shops):
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)

            # Check if the location is suitable for a shop (e.g., near a road or in a town area)
            if map_data[y][x] == 'street' or map_data[y][x] == 'grass':
                map_data[y][x] = 'building'  # Use 'building' tile for shops
                shops.append({'x': x, 'y': y})

        return shops

    def generate_all(self):
        """Generate the complete map with all features."""
        map_data = self.generate_map()
        entities = self.generate_entities(map_data)
        structures = self.generate_structures(map_data)
        decorations = self.generate_decorations(map_data)
        villages = self.generate_villages(map_data)
        ruins = self.generate_ruins(map_data)
        caves = self.generate_caves(map_data)
        roads = self.generate_roads(map_data)
        shops = self.generate_shops(map_data)

        return {
            'map': map_data,
            'entities': entities,
            'structures': structures,
            'decorations': decorations,
            'villages': villages,
            'ruins': ruins,
            'caves': caves
        }

class SpawnTownMapGenerator(MapGenerator):
    """Generates procedural maps for the spawntown."""

    def generate_map(self):
        """Generate a procedural map for spawntown."""
        map_data = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Generate terrain based on Perlin noise
                noise_value = noise.pnoise2(x / self.width * 2,
                                           y / self.height * 2,
                                           octaves=10,
                                           persistence=0.5,
                                           lacunarity=2.0,
                                           repeatx=1024,
                                           repeaty=1024,
                                           base=self.seed)

                # Assign tile types based on noise value, using available tile assets
                if noise_value < -0.5:
                    tile_type = 'water'
                elif noise_value < -0.4:
                    tile_type = 'sand'
                elif noise_value < -0.3:
                    tile_type = 'grass'
                elif noise_value < -0.2:
                    tile_type = 'path'
                elif noise_value < -0.1:
                    tile_type = 'cobblestone'
                elif noise_value < 0.0:
                    tile_type = 'house'
                elif noise_value < 0.1:
                    tile_type = 'building'
                elif noise_value < 0.2:
                    tile_type = 'street'
                elif noise_value < 0.3:
                    tile_type = 'market'
                elif noise_value < 0.4:
                    tile_type = 'shop'
                elif noise_value < 0.5:
                    tile_type = 'garden'
                elif noise_value < 0.6:
                    tile_type = 'well'
                elif noise_value < 0.7:
                    tile_type = 'rubble'
                else:
                    tile_type = 'mountain'

                row.append(tile_type)
            map_data.append(row)

        return map_data

    def generate_entities(self, map_data):
        """Generate entities (enemies, NPCs, etc.) on the map."""
        entities = []

        for y in range(self.height):
            for x in range(self.width):
                tile_type = map_data[y][x]

                # Spawn entities based on terrain type
                if tile_type == 'grass' and random.random() < 0.1:
                    entities.append({
                        'type': 'npc',
                        'x': x,
                        'y': y,
                        'name': 'Villager'
                    })
                elif tile_type == 'street' and random.random() < 0.2:
                    entities.append({
                        'type': 'npc',
                        'x': x,
                        'y': y,
                        'name': 'Merchant'
                    })
                elif tile_type == 'market' and random.random() < 0.3:
                    entities.append({
                        'type': 'npc',
                        'x': x,
                        'y': y,
                        'name': 'Town Crier'
                    })

        return entities