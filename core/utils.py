import os
import json
import pygame

def load_json(filepath):
    """Loads data from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return None

def save_json(filepath, data):
    """Saves data to a JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except IOError:
        print(f"Error: Could not write to file at {filepath}")
        return False

def get_asset_path(asset_type, filename):
    """Constructs a path to an asset."""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Go up two levels from core/utils.py
    return os.path.join(base_path, "graphics", asset_type, filename)

def load_image(filename):
    """Loads an image from the specified file."""
    try:
        image = pygame.image.load(filename).convert_alpha()
        return image
    except pygame.error as message:
        print(f"Cannot load image: {filename}")
        image = pygame.Surface((32, 32))
        image.fill((255, 0, 255))
        return image

def calculate_distance(point1, point2):
    """Calculates the distance between two points."""
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

def direction_to_target(source, target):
    """Calculates the direction vector from source to target."""
    dx = target[0] - source[0]
    dy = target[1] - source[1]
    return pygame.math.Vector2(dx, dy).normalize()

def draw_text(surface, text, size, color, x, y, align="topleft"):
    """Renders text on a surface."""
    font_name = pygame.font.match_font('arial') # Fallback font
    try:
        font = pygame.font.Font(font_name, size)
    except:
        font = pygame.SysFont(font_name, size) # Fallback if Font fails

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if align == "center":
        text_rect.center = (x, y)
    elif align == "topright":
        text_rect.topright = (x, y)
    elif align == "midleft":
        text_rect.midleft = (x, y)
    elif align == "midright":
        text_rect.midright = (x, y)
    elif align == "bottomleft":
        text_rect.bottomleft = (x, y)
    elif align == "bottomright":
        text_rect.bottomright = (x, y)
    else: # topleft
        text_rect.topleft = (x, y)

    surface.blit(text_surface, text_rect)
    return text_surface
def load_zone_data():
    """Loads zone data from a JSON file."""
    try:
        with open("data/zone_data.json", "r") as file:
            zone_data = json.load(file)
            current_zone = zone_data.get("zones", [])[0]  # Load the first zone as default
            tilemap_path = current_zone.get("tilemap", "graphics/tilesets/placeholder.txt")
            music_path = current_zone.get("music", None)
            allowed_enemies = current_zone.get("enemies", [])
            print(f"Loaded zone data for: {current_zone.get('name')}")
            return {
                "tilemap_path": tilemap_path,
                "music_path": music_path,
                "allowed_enemies": allowed_enemies
            }
    except FileNotFoundError:
        print("ERROR: zone_data.json not found!")
        return {
            "tilemap_path": "graphics/tilesets/placeholder.txt",
            "music_path": None,
            "allowed_enemies": []
        }
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON format in zone_data.json!")
        return {
            "tilemap_path": "graphics/tilesets/placeholder.txt",
            "music_path": None,
            "allowed_enemies": []
        }
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        return {
            "tilemap_path": "graphics/tilesets/placeholder.txt",
            "music_path": None,
            "allowed_enemies": []
        }