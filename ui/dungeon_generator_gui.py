import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pygame
import json
import tkinter as tk
import math
from tkinter import ttk, filedialog, simpledialog, messagebox

from PIL import Image, ImageTk

from core.new_dungeon_generator import generate_new_dungeon, save_dungeon_data, translate_tile_type, load_enemy_data
from ui.dungeon_gui_scene_generator import generate_scene_file, add_scene_to_game_engine, add_portal_to_spawntown, remove_scene_from_scenes_json, remove_portal_from_spawntown
from ui.dungeon_display import display_dungeon

class DungeonGeneratorGUI:
    def __init__(self, game):
        # Removed pygame.init() and pygame.display.set_mode((1, 1)) to avoid conflicts with main Pygame loop
        self.game = game
        self.game.logger.info("DungeonGeneratorGUI initialized.")
        self.root = tk.Tk()
        self.root.after(100, self.update_tkinter)

        self.root.title("Dungeon Generator")

        self.width_label = ttk.Label(self.root, text="Width:")
        self.width_label.grid(row=0, column=0)
        self.width_entry = ttk.Entry(self.root)
        self.width_entry.insert(0, "50")
        self.width_entry.grid(row=0, column=1)

        self.height_label = ttk.Label(self.root, text="Height:")
        self.height_label.grid(row=1, column=0)
        self.height_entry = ttk.Entry(self.root)
        self.height_entry.insert(0, "50")
        self.height_entry.grid(row=1, column=1)

        self.tileset_label = ttk.Label(self.root, text="Tileset:")
        self.tileset_label.grid(row=2, column=0)
        with open('data/tileset_mappings.json', 'r') as f:
            tileset_data = json.load(f)
        self.tileset_options = list(tileset_data.keys())
        self.tileset_combo = ttk.Combobox(self.root, values=self.tileset_options)
        self.tileset_combo.set("default")
        self.tileset_combo.grid(row=2, column=1)

        self.enemy_types_label = ttk.Label(self.root, text="Enemy Types:")
        # Load enemy types dynamically from enemy_data.json
        enemy_data = load_enemy_data('data/enemy_data.json')
        self.enemy_types_options = list(enemy_data.keys())
        self.enemy_types_vars = {}
        current_row = 3 # Checkboxes start at row 3
        num_columns = 2 # Number of columns for enemy checkboxes
        num_enemy_types = len(self.enemy_types_options)
        num_enemy_rows = math.ceil(num_enemy_types / num_columns) # Calculate rows needed for enemies

        for i, enemy_type in enumerate(self.enemy_types_options):
            var = tk.BooleanVar()
            self.enemy_types_vars[enemy_type] = var
            checkbox = tk.Checkbutton(self.root, text=enemy_type, variable=var)
            checkbox.grid(row=current_row + (i // num_columns), column=1 + (i % num_columns), sticky=tk.W)
        
        # Adjust row for num_enemies_label based on number of enemy types
        self.num_enemies_label = ttk.Label(self.root, text="Number of Enemies:")
        self.num_enemies_label.grid(row=current_row + num_enemy_rows, column=0)
        self.num_enemies_entry = ttk.Entry(self.root)
        self.num_enemies_entry.insert(0, "5") # Default to 5 enemies
        self.num_enemies_entry.grid(row=current_row + num_enemy_rows, column=1)


        self.dungeon_name_label = ttk.Label(self.root, text="Dungeon Name:")
        self.dungeon_name_label.grid(row=5 + num_enemy_rows, column=0) # Adjusted row
        self.dungeon_name_entry = ttk.Entry(self.root)
        self.dungeon_name_entry.insert(0, "New Dungeon")
        self.dungeon_name_entry.grid(row=5 + num_enemy_rows, column=1) # Adjusted row

        self.portal_graphic_label = ttk.Label(self.root, text="Portal Graphic:")
        self.portal_graphic_label.grid(row=6 + num_enemy_rows, column=0) # Adjusted row
        self.portal_graphic_button = ttk.Button(self.root, text="Browse", command=self.browse_portal_graphic)
        self.portal_graphic_button.grid(row=6 + num_enemy_rows, column=1) # Adjusted row
        self.portal_graphic_path = tk.StringVar()

        self.map_algorithm_label = ttk.Label(self.root, text="Map Algorithm:")
        self.map_algorithm_label.grid(row=7 + num_enemy_rows, column=0) # Adjusted row
        self.map_algorithm_options = ["perlin_noise", "room_based"]
        self.map_algorithm_combo = ttk.Combobox(self.root, values=self.map_algorithm_options)
        self.map_algorithm_combo.set("perlin_noise")
        self.map_algorithm_combo.grid(row=7 + num_enemy_rows, column=1) # Adjusted row

        self.portal_placement_label = ttk.Label(self.root, text="Portal Placement:")
        self.portal_placement_label.grid(row=8 + num_enemy_rows, column=0) # Adjusted row
        self.portal_placement_options = ["random", "specific"]
        self.portal_placement_combo = ttk.Combobox(self.root, values=self.portal_placement_options)
        self.portal_placement_combo.set("random")
        self.portal_placement_combo.grid(row=8 + num_enemy_rows, column=1) # Adjusted row
        self.portal_placement_combo.bind("<<ComboboxSelected>>", self.update_portal_coordinates)

        self.portal_x_label = ttk.Label(self.root, text="Portal X:")
        self.portal_x_label.grid(row=9 + num_enemy_rows, column=0) # Adjusted row
        self.portal_x_entry = ttk.Entry(self.root)
        self.portal_x_entry.grid(row=9 + num_enemy_rows, column=1) # Adjusted row
        self.portal_y_label = ttk.Label(self.root, text="Portal Y:")
        self.portal_y_label.grid(row=10 + num_enemy_rows, column=0) # Adjusted row
        self.portal_y_entry = ttk.Entry(self.root)
        self.portal_y_entry.grid(row=10 + num_enemy_rows, column=1) # Adjusted row
        self.update_portal_coordinates()

        self.decorations_label = ttk.Label(self.root, text="Decorations:")
        self.decorations_label.grid(row=11 + num_enemy_rows, column=0) # Adjusted row
        self.decorations_options = ["graphics/dc-dngn/dngn_sparkling_fountain", "graphics/dc-dngn/dngn_orcish_idol"]  # Add more decorations here
        self.decorations_vars = {}
        for i, decoration in enumerate(self.decorations_options):
            var = tk.BooleanVar()
            self.decorations_vars[decoration] = var
            checkbox = tk.Checkbutton(self.root, text=decoration, variable=var)
            checkbox.grid(row=11 + num_enemy_rows + i, column=1, sticky=tk.W) # Adjusted row offset

        self.perlin_noise_threshold_label = ttk.Label(self.root, text="Perlin Noise Threshold:")
        self.perlin_noise_threshold_label.grid(row=13 + num_enemy_rows, column=0) # Adjusted row
        self.perlin_noise_threshold_entry = ttk.Entry(self.root)
        self.perlin_noise_threshold_entry.insert(0, "0.0")
        self.perlin_noise_threshold_entry.grid(row=13 + num_enemy_rows, column=1) # Adjusted row

        self.generate_button = ttk.Button(self.root, text="Generate Dungeon", command=self.generate_dungeon)
        self.generate_button.grid(row=14 + num_enemy_rows, column=0, columnspan=2) # Adjusted row

        self.dungeon_frame = ttk.Frame(self.root)
        self.dungeon_frame.grid(row=0, column=2, rowspan=15 + num_enemy_rows) # Adjusted rowspan

        self.canvas = tk.Canvas(self.dungeon_frame, width=600, height=400)
        self.canvas.pack()
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<ButtonRelease-1>", self.stop_pan)
        self.canvas.bind("<B1-Motion>", self.pan)
        self.canvas.bind("<Button-1>", self.place_object)

        self.toolbar_frame = ttk.Frame(self.root)
        self.toolbar_frame.grid(row=0, column=3, rowspan=15 + num_enemy_rows, sticky=tk.NS) # Adjusted rowspan

        self.portal_button = ttk.Button(self.toolbar_frame, text="Place Portal", command=self.select_portal)
        self.portal_button.pack(pady=5)

        self.decoration_buttons = {}
        for decoration in self.decorations_options:
            button = ttk.Button(self.toolbar_frame, text=f"Place {decoration.split('/')[-1]}", command=lambda d=decoration: self.select_decoration(d))
            button.pack(pady=5)
            self.decoration_buttons[decoration] = button

        self.zoom_info_label = ttk.Label(self.toolbar_frame, text="Zoom: Mouse Wheel\nPan: Drag Mouse")
        self.zoom_info_label.pack(pady=5)

        self.remove_dungeon_button = ttk.Button(self.toolbar_frame, text="Remove Dungeon", command=self.open_remove_dungeon_dialog)
        self.remove_dungeon_button.pack(pady=5)

        self.zoom_scale = 1.0
        self.dungeon_data = None
        self.pan_start_x = None
        self.pan_start_y = None
        self.offset_x = 0
        self.offset_y = 0
        self.placing_object = None

    def browse_portal_graphic(self):
        filename = filedialog.askopenfilename(initialdir="graphics/dc-dngn/gateways", title="Select Portal Graphic", filetypes=(("PNG files", "*.png"), ("all files", "*.*")))
        self.portal_graphic_path.set(filename)

    def update_portal_coordinates(self, event=None):
        if self.portal_placement_combo.get() == "specific":
            self.portal_x_label.config(state=tk.NORMAL)
            self.portal_x_entry.config(state=tk.NORMAL)
            self.portal_y_label.config(state=tk.NORMAL)
            self.portal_y_entry.config(state=tk.NORMAL)
        else:
            self.portal_x_label.config(state=tk.DISABLED)
            self.portal_x_entry.config(state=tk.DISABLED)
            self.portal_y_label.config(state=tk.DISABLED)
            self.portal_y_entry.config(state=tk.DISABLED)

    def generate_dungeon(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            perlin_noise_threshold = float(self.perlin_noise_threshold_entry.get())
            num_enemies = int(self.num_enemies_entry.get()) # Get number of enemies
        except ValueError:
            messagebox.showerror("Error", "Width, height, Perlin noise threshold, and number of enemies must be numbers.")
            return

        dungeon_params = {
            'width': width,
            'height': height,
            'tileset': self.tileset_combo.get(),
            'enemy_types': [enemy_type for enemy_type, var in self.enemy_types_vars.items() if var.get()],
            'num_enemies': num_enemies, # Add num_enemies to params
            'name': self.dungeon_name_entry.get(),
            'portal_graphic': self.portal_graphic_path.get(),
            'map_algorithm': self.map_algorithm_combo.get(),
            'portal_placement': self.portal_placement_combo.get(),
            'perlin_noise_threshold': perlin_noise_threshold
        }

        if dungeon_params['portal_placement'] == "specific":
            try:
                dungeon_params['portal_x'] = int(self.portal_x_entry.get())
                dungeon_params['portal_y'] = int(self.portal_y_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Portal X and Y must be integers.")
                return # Added return here to prevent further execution if error occurs

        dungeon_params['decorations'] = [decoration for decoration, var in self.decorations_vars.items() if var.get()]

        self.dungeon_data = generate_new_dungeon(dungeon_params)

        self.display_dungeon(self.dungeon_data)

        filename = simpledialog.askstring("Save Dungeon", "Enter filename:")
        if filename:
            self.save_dungeon_data(self.dungeon_data, filename)

    def display_dungeon(self, dungeon_data):
        self.photo = display_dungeon(dungeon_data, self.canvas, self.offset_x, self.offset_y, self.zoom_scale)

    def zoom(self, event):
        if event.delta > 0:
            self.zoom_scale *= 1.1
        else:
            self.zoom_scale /= 1.1
        self.display_dungeon(self.dungeon_data)

    def start_pan(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.canvas.config(cursor="fleur")

    def stop_pan(self, event):
        self.pan_start_x = None
        self.pan_start_y = None
        self.canvas.config(cursor="")

    def pan(self, event):
        if self.pan_start_x is not None and self.pan_start_y is not None:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.offset_x += dx
            self.offset_y += dy
            self.display_dungeon(self.dungeon_data)
            self.pan_start_x = event.x
            self.pan_start_y = event.y

    def select_portal(self):
        self.placing_object = 'portal'
        messagebox.showinfo("Info", "Select a location to place the portal.")

    def select_decoration(self, decoration):
        self.placing_object = decoration
        messagebox.showinfo("Info", f"Select a location to place the {decoration.split('/')[-1]}.")

    def place_object(self, event):
        if self.placing_object:
            x = int((event.x - self.offset_x) / (32 * self.zoom_scale))
            y = int((event.y - self.offset_y) / (32 * self.zoom_scale))
            print(f"Placing {self.placing_object} at {x}, {y}")
            # Modify the dungeon data to place the object at the selected location
            if self.dungeon_data and 0 <= x < self.dungeon_data['width'] and 0 <= y < self.dungeon_data['height']:
                self.dungeon_data['tile_map'][y][x] = self.placing_object
                self.display_dungeon(self.dungeon_data)
            self.placing_object = None

    def save_dungeon_data(self, dungeon_data, filename):
        """Saves dungeon data to a JSON file and adds a portal to spawntown."""
        dungeon_dir = "data/dungeons"
        if not os.path.exists(dungeon_dir):
            os.makedirs(dungeon_dir)
        filepath = os.path.join(dungeon_dir, f'{filename}.json')
        with open(filepath, 'w') as f:
            json.dump(dungeon_data, f, indent=4)
        print(f"Dungeon data saved to {filepath}")
        print(f"save_dungeon_data filename: {filename}") # Print statement

        # Generate new scene file
        generate_scene_file(filename, dungeon_data)

        # Add the new scene to the game engine
        add_scene_to_game_engine(filename)
        # Add portal to spawntown in zone_data.json
        add_portal_to_spawntown(filename, dungeon_data.get('portal_graphic', "graphics/UNUSED/features/dngn_exit.png"), self.find_portal_location, dungeon_data)
        self.game.scene_manager.load_scenes() # Reload scenes after adding a new one
    
    def open_remove_dungeon_dialog(self):
        """Opens a dialog box to remove a dungeon."""
        remove_dungeon_dialog = tk.Toplevel(self.root)
        remove_dungeon_dialog.title("Remove Dungeon")

        dungeon_files = [f for f in os.listdir('data/dungeons') if f.endswith('.json')]
        dungeon_list = tk.Listbox(remove_dungeon_dialog, selectmode=tk.MULTIPLE)
        for dungeon_file in dungeon_files:
            dungeon_list.insert(tk.END, dungeon_file[:-5])
        dungeon_list.pack(pady=5)

        remove_button = ttk.Button(remove_dungeon_dialog, text="Remove", command=lambda: self.remove_dungeon(dungeon_list.curselection(), dungeon_files, remove_dungeon_dialog))
        remove_button.pack(pady=5)

    def remove_dungeon(self, selected_dungeons_indices, dungeon_files, remove_dungeon_dialog):
        """Removes the selected dungeons."""
        for index in selected_dungeons_indices:
            dungeon_file = dungeon_files[index]
            dungeon_name = dungeon_file[:-5]
            filepath = os.path.join('data/dungeons', dungeon_file)
            try:
                os.remove(filepath)
                print(f"Dungeon file {dungeon_file} removed.")
                remove_portal_from_spawntown(dungeon_name)
            except OSError as e:
                print(f"Error removing dungeon file {dungeon_file}: {e}")

            # Remove the scene from data/scenes.json
            remove_scene_from_scenes_json(dungeon_name)

        remove_dungeon_dialog.destroy()

    def find_portal_location(self, tile_map):
        """Finds a suitable location for the portal in spawntown near existing portals."""
        # Get the locations of existing portals from zone_data.json
        zone_data_path = "data/zone_data.json"
        try:
            with open(zone_data_path, "r") as f:
                zone_data = json.load(f)
            spawn_town_data = zone_data["zones"]["spawn_town"]
            portals = spawn_town_data.get("portals", [])
            if portals:
                # Choose a random existing portal location
                import random
                portal = random.choice(portals)
                x, y = portal["location"]
                # Return a location near the chosen portal, ensuring positive coordinates
                x = max(0, x + random.randint(-5, 5))
                y = max(0, y + random.randint(-5, 5))
                return x, y
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass  # Handle errors gracefully

        # If no existing portals are found or an error occurs, return a default location
        if tile_map and len(tile_map) > 0 and len(tile_map[0]) > 0:
            return 0, 0
        return 10, 10

    def update_tkinter(self):
        self.root.update_idletasks()
        self.root.update()
        self.root.after(100, self.update_tkinter)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # When running as a standalone script, a dummy game object is needed
    class DummyGame:
        def __init__(self):
            self.settings = type('Settings', (object,), {'FULLSCREEN': False})()
            self.logger = type('Logger', (object,), {'info': print, 'error': print})()
            self.scene_manager = type('SceneManager', (object,), {'set_scene': print})()
        def apply_display_settings(self):
            pass

    gui = DungeonGeneratorGUI(DummyGame())
    gui.run()