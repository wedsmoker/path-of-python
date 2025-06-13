import pygame
import json
import os
import ui

def generate_scene_file(dungeon_name, dungeon_data):
    '''Generates a new scene file for the dungeon.'''
    scene_dir = "core/dungeons"
    if not os.path.exists(scene_dir):
        os.makedirs(scene_dir)
    filepath = os.path.join(scene_dir, f'{dungeon_name}.py')

    # Sanitize the dungeon name for use as a class name
    class_name = ''.join(c if c.isalnum() else '_' for c in dungeon_name)
    if class_name[0].isdigit():
        class_name = '_' + class_name

    scene_content = f'''
import pygame
import json
import os
from core.base_gameplay_scene import BaseGameplayScene

class {class_name}(BaseGameplayScene):
    def __init__(self, game, player, hud, dungeon_data=None):
        super().__init__(game, player, hud, tileset_name=dungeon_data.get("tileset", "default"), dungeon_data=dungeon_data)
        self.name = "{dungeon_name}"
        self.dungeon_data = dungeon_data
        self.tile_map = self.dungeon_data["tile_map"]
        self.map_width = self.dungeon_data["width"]
        self.map_height = self.dungeon_data["height"]
        self.entities = []  # Initialize an empty list of entities
        self.effects = pygame.sprite.Group()  # Initialize the effects group

    def load_dungeon_data(self, dungeon_name):
        # This method is no longer strictly needed if dungeon_data is passed directly,
        # but kept for compatibility or if other parts of the code rely on it.
        dungeon_data_path = os.path.abspath(os.path.join(os.getcwd(), "data", "dungeons", f'{{dungeon_name}}.json'))
        try:
            with open(dungeon_data_path, "r") as f:
                dungeon_data = json.load(f)
            return dungeon_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading dungeon data from {{dungeon_data_path}}: {{e}}")
            return {{}}

    def update(self, dt):
        super().update(dt, self.entities)  # Pass the entities list to the update method
        self.effects.update(dt) # Update the effects

    def draw(self, screen):
        super().draw(screen)
        for sprite in self.effects:
            screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y))
'''

    with open(filepath, 'w') as f:
        f.write(scene_content)

    print(f"Scene file generated at {filepath}")

def add_scene_to_game_engine(dungeon_name):
    '''Adds the new scene to the data/scenes.json file.'''
    scenes_data_path = "data/scenes.json"
    try:
        with open(scenes_data_path, "r") as f:
            scenes_data = json.load(f)

        # Check if the scene already exists
        for scene_data in scenes_data['scenes']:
            if scene_data['name'] == dungeon_name:
                print(f"Scene {dungeon_name} already exists in data/scenes.json")
                return

        # Sanitize the dungeon name for use as a class name
        class_name = ''.join(c if c.isalnum() else '_' for c in dungeon_name)
        if class_name[0].isdigit():
            class_name = '_' + class_name

        # Add the new scene to the scene list
        new_scene = {
            "name": dungeon_name,
            "class": f"core.dungeons.{dungeon_name}.{class_name}",
            "dungeon_data_path": f"data/dungeons/{dungeon_name}.json" # Added this line
        }
        scenes_data['scenes'].append(new_scene)

        # Write the modified data back to the JSON file
        with open(scenes_data_path, "w") as f:
            json.dump(scenes_data, f, indent=4)

        print(f"Scene {dungeon_name} added to data/scenes.json")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error updating data/scenes.json: {e}")

def add_portal_to_spawntown(new_dungeon_name, portal_graphic, find_portal_location, dungeon_data):
    '''Adds a portal to spawntown in zone_data.json that leads to the new dungeon.'''
    zone_data_path = "data/zone_data.json"
    try:
        with open(zone_data_path, "r") as f:
            zone_data = json.load(f)
        spawn_town_data = zone_data["zones"]["spawn_town"]
        portals = spawn_town_data.get("portals", [])

        # Use the portal_x and portal_y from the dungeon_data
        portal_x = dungeon_data.get('portal_x')
        portal_y = dungeon_data.get('portal_y')

        # If portal_x and portal_y are not available, use the find_portal_location function
        if portal_x is None or portal_y is None:
            location = find_portal_location(dungeon_data['tile_map'])
            portal_x, portal_y = location[0], location[1]
        
        # Create a new portal entry
        new_portal = {
            "target_scene": new_dungeon_name,
            "location": [portal_x * 32, portal_y * 32],  # Convert tile coordinates to pixel coordinates
            "graphic": portal_graphic
        }
        portals.append(new_portal)
        print(f"Added new portal to {new_dungeon_name} in spawntown in zone_data.json")
        print(f"new_dungeon_name: {new_dungeon_name}")
        print(f"portal_graphic: {portal_graphic}")
        print(f"location: {new_portal['location']}")

        spawn_town_data["portals"] = portals
        zone_data["zones"]["spawn_town"] = spawn_town_data  # Update spawn_town_data in zone_data

        # Save the modified zone_data back to the JSON file
        with open(zone_data_path, "w") as f:
            json.dump(zone_data, f, indent=4)
# Add a portal to the new dungeon that leads back to spawntown
        dungeon_data_path = os.path.abspath(os.path.join(os.getcwd(), "data", "dungeons", f'{new_dungeon_name}.json'))
        try:
            with open(dungeon_data_path, "r") as f:
                dungeon_data = json.load(f)
            
            # Find a suitable location for the portal in the dungeon
            portal_x = dungeon_data.get('portal_x')
            portal_y = dungeon_data.get('portal_y')

            # If portal_x and portal_y are not available, use the find_portal_location function
            if portal_x is None or portal_y is None:
                location = find_portal_location(dungeon_data['tile_map'])
                portal_x, portal_y = location[0], location[1]

            # Create a new portal entry
            new_portal = {
                "target_scene": "spawn_town",
                "location": [portal_x * 32, portal_y * 32],  # Convert tile coordinates to pixel coordinates
                "graphic": portal_graphic
            }

            dungeon_data["portals"] = dungeon_data.get("portals", [])
            dungeon_data["portals"].append(new_portal)

            # Save the modified dungeon data back to the JSON file
            with open(dungeon_data_path, "w") as f:
                json.dump(dungeon_data, f, indent=4)

            print(f"Added new portal to spawntown in {new_dungeon_name} in data/dungeons/{{new_dungeon_name}}.json")

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error updating dungeon data in data/dungeons/{{new_dungeon_name}}.json: {{e}}")

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error updating spawntown data in zone_data.json: {e}")

def remove_scene_from_scenes_json(dungeon_name):
    '''Removes the scene from data/scenes.json.'''
    scenes_data_path = "data/scenes.json"
    try:
        with open(scenes_data_path, "r") as f:
            scenes_data = json.load(f)

        # Find the scene to remove
        scene_to_remove = None
        for scene_data in scenes_data['scenes']:
            if scene_data['name'] == dungeon_name:
                scene_to_remove = scene_data
                break

        # Remove the scene if found
        if scene_to_remove:
            scenes_data['scenes'].remove(scene_to_remove)
            print(f"Scene {dungeon_name} removed from data/scenes.json")

            # Write the modified data back to the JSON file
            with open(scenes_data_path, "w") as f:
                json.dump(scenes_data, f, indent=4)
        else:
            print(f"Scene {dungeon_name} not found in data/scenes.json")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error updating data/scenes.json: {e}")

def remove_portal_from_spawntown(dungeon_name):
    '''Removes the portal to the specified dungeon from spawntown.'''
    zone_data_path = "data/zone_data.json"
    try:
        with open(zone_data_path, "r") as f:
            zone_data = json.load(f)
        spawn_town_data = zone_data["zones"]["spawn_town"]
        portals = spawn_town_data.get("portals", [])

        # Create a new list to store the portals to keep
        updated_portals = []
        for portal in portals:
            if portal["target_scene"] != dungeon_name:
                updated_portals.append(portal)

        spawn_town_data["portals"] = updated_portals
        zone_data["zones"]["spawn_town"] = spawn_town_data  # Update spawn_town_data in zone_data

    # Save the modified zone_data back to the JSON file
        with open(zone_data_path, "w") as f:
            json.dump(zone_data, f, indent=4)

        print(f"Portal to {dungeon_name} removed from spawntown.")

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error updating spawntown data: {e}")

def find_portal_location(tile_map):
    """Finds a suitable location for the portal in spawntown near existing portals."""
    # Get the locations of existing portals from zone_data.json
    zone_data_path = "data/zone_data.json"

    if not tile_map or len(tile_map) == 0 or len(tile_map[0]) == 0 or not all(tile is not None for row in tile_map for tile in row):
        print("Invalid tile map. Returning default portal location.")
        return 10, 10

    try:
        with open(zone_data_path, "r") as f:
            zone_data = json.load(f)
        spawn_town_data = zone_data["zones"]["spawn_town"]
        portals = spawn_town_data.get("portals", [])
        if portals:
            # Choose a random existing portal location
            import random
            portal = random.choice(portals)
            x = portal["location"][0] / 32
            y = portal["location"][1] / 32
            # Return a location near the chosen portal, ensuring positive coordinates
            x = max(0, x + random.randint(-5, 5))
            y = max(0, y + random.randint(-5, 5))
            return x, y
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        print("Error loading zone data. Returning default portal location.")
        return 10, 10

    # If no existing portals are found or an error occurs, return a default location
    return 0, 0

def run(self):
    self.root.mainloop()

if __name__ == "__main__":
    gui = DungeonGeneratorGUI()
    gui.run()