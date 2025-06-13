import os
import sys
import json

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_image_paths.py <json_list_of_paths>")
        sys.exit(1)

    paths_json = sys.argv[1]
    try:
        paths = json.loads(paths_json)
    except json.JSONDecodeError:
        print("Error: Invalid JSON string for paths.")
        sys.exit(1)

    missing_files = []
    for path in paths:
        if not os.path.exists(path):
            missing_files.append(path)

    if missing_files:
        print("The following image files are missing:")
        for f in missing_files:
            print(f)
    else:
        print("All image files referenced in tilesets exist.")