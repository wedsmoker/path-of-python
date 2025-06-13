import json
import os

def check_image_paths(enemy_data_path="data/enemy_data.json"):
    """
    Checks if sprite_path and projectile_sprite_path in enemy_data.json exist.
    """
    print(f"Checking image paths defined in {enemy_data_path}...")
    
    current_working_directory = os.getcwd()
    print(f"Current working directory: {current_working_directory}")

    try:
        with open(enemy_data_path, "r") as f:
            enemy_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {enemy_data_path} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {enemy_data_path}. Check file format.")
        return

    all_paths_exist = True

    for enemy_type, config in enemy_data.items():
        # Check main sprite_path
        sprite_path = config.get("sprite_path")
        if sprite_path:
            full_sprite_path = os.path.join(current_working_directory, sprite_path)
            if not os.path.exists(full_sprite_path):
                print(f"MISSING: Enemy '{enemy_type}' sprite_path: {sprite_path} (Full path: {full_sprite_path})")
                all_paths_exist = False
            # else:
            #     print(f"OK: Enemy '{enemy_type}' sprite_path: {sprite_path}")
        else:
            print(f"WARNING: Enemy '{enemy_type}' has no 'sprite_path' defined.")

        # Check projectile_sprite_path
        projectile_sprite_path = config.get("projectile_sprite_path")
        if projectile_sprite_path:
            full_projectile_sprite_path = os.path.join(current_working_directory, projectile_sprite_path)
            if not os.path.exists(full_projectile_sprite_path):
                print(f"MISSING: Enemy '{enemy_type}' projectile_sprite_path: {projectile_sprite_path} (Full path: {full_projectile_sprite_path})")
                all_paths_exist = False
            # else:
            #     print(f"OK: Enemy '{enemy_type}' projectile_sprite_path: {projectile_sprite_path}")
        # else:
        #     print(f"INFO: Enemy '{enemy_type}' has no 'projectile_sprite_path' defined (expected for melee-only or training dummy).")

    if all_paths_exist:
        print("\nAll specified image paths in enemy_data.json exist.")
    else:
        print("\nSome image paths are missing. Please review the 'MISSING' entries above.")

if __name__ == "__main__":
    check_image_paths()