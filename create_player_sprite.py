import pygame

def create_player_sprite(filename="graphics/sprites/player.png", size=32, color=(0, 255, 0)):
    """Creates a simple player sprite PNG file."""
    try:
        pygame.init()
        surface = pygame.Surface((size, size), pygame.SRCALPHA) # Use SRCALPHA for transparency
        pygame.draw.circle(surface, color, (size // 2, size // 2), size // 2) # Draw a circle
        pygame.image.save(surface, filename)
        print(f"Successfully created {filename}")
    except Exception as e:
        print(f"Error creating player sprite: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    create_player_sprite()