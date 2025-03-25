import pygame, sys, json, os, copy
from engine.map_editor.button import Button


class MapEditor:
    def __init__(self, map_filename, metadata_filename="map_data.json"):
        self.tile_size = 32
        self.map_filename = map_filename

        # Automatically load all images from the "tiles" directory.
        self.tile_img = self.load_images("tiles")
        self.tile_keys = list(self.tile_img.keys())
        self.selected_tile = self.tile_keys[0]

        self.undo_stack = []
        self.redo_stack = []

        self.camera_offset_x = 0
        self.camera_offset_y = 0

        self.font = pygame.font.SysFont("arial", 16)

        # Load the map from JSON.
        self.map = self.load_map(self.map_filename)
        self.map_width = len(self.map[0])
        self.map_height = len(self.map)
        self.map_surface = pygame.Surface((self.map_width * self.tile_size, self.map_height * self.tile_size))
        self.tile_surface = pygame.Surface((self.tile_size * 4 + 50, self.tile_size * 2 * len(self.tile_img) + 50))
        self.setting_surface = pygame.Surface((800, 20))

        # Load map metadata for multiple maps.
        self.map_metadata = self.load_map_metadata(metadata_filename)
        self.displaying_map_menu = False

    def load_map_metadata(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return data.get("maps", [])

    def open_map_menu(self, screen):
        """Display a simple map selection menu using the metadata."""
        self.displaying_map_menu = True
        menu_surface = pygame.Surface((400, 300))
        menu_surface.fill((100, 100, 100))
        menu_rect = menu_surface.get_rect(center=(400, 300))

        # Render the list of maps.
        map_buttons = []
        btn_height = 40
        spacing = 10
        for i, map_info in enumerate(self.map_metadata):
            btn_rect = pygame.Rect(50, 50 + i * (btn_height + spacing), 300, btn_height)
            map_buttons.append((btn_rect, map_info))

        while self.displaying_map_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Adjust mouse_pos relative to the menu.
                    relative_mouse = (mouse_pos[0] - menu_rect.left, mouse_pos[1] - menu_rect.top)
                    for btn_rect, map_info in map_buttons:
                        if btn_rect.collidepoint(relative_mouse):
                            # When a map is selected, load it.
                            self.load_new_map(map_info["filename"])
                            self.displaying_map_menu = False

            # Draw the menu.
            menu_surface.fill((100, 100, 100))
            for btn_rect, map_info in map_buttons:
                pygame.draw.rect(menu_surface, (200, 200, 200), btn_rect)
                text_surface = self.font.render(map_info["name"], True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=btn_rect.center)
                menu_surface.blit(text_surface, text_rect)

            screen.blit(menu_surface, menu_rect)
            pygame.display.update()

    def load_new_map(self, filename):
        """Load a new map and update internal state."""
        self.map_filename = filename
        self.map = self.load_map(self.map_filename)
        self.map_width = len(self.map[0])
        self.map_height = len(self.map)
        # Recreate the map surface with the new dimensions.
        self.map_surface = pygame.Surface((self.map_width * self.tile_size, self.map_height * self.tile_size))
        # Optionally, reset the undo/redo stacks.
        self.undo_stack.clear()
        self.redo_stack.clear()

    def run(self, screen, clock):
        running = True
        while running:
            clock.tick(60)
            self.handle_events(screen)
            self.update()
            self.draw(screen)
        return True

    def handle_events(self, screen):
        for event in pygame.event.get():
            self.mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_z:
                    self.undo()
                if event.key == pygame.K_y:
                    self.redo()
                if event.key == pygame.K_r:
                    self.save_map(self.map_filename)

                if event.key == pygame.K_LEFT:
                    self.camera_offset_x = max(0, self.camera_offset_x - self.tile_size)
                if event.key == pygame.K_RIGHT:
                    self.camera_offset_x += self.tile_size
                if event.key == pygame.K_UP:
                    self.camera_offset_y = max(0, self.camera_offset_y - self.tile_size)
                if event.key == pygame.K_DOWN:
                    self.camera_offset_y += self.tile_size

                # For testing, let’s say pressing L opens the map menu.
                if event.key == pygame.K_l:
                    self.open_map_menu(screen)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check for palette clicks.
                palette_x = 20
                palette_y = 20
                tiles_per_row = 2
                spacing = 10
                for i, tile_key in enumerate(self.tile_keys):
                    col = i % tiles_per_row
                    row = i // tiles_per_row
                    pos_x = palette_x + col * (self.tile_size * 2 + spacing)
                    pos_y = palette_y + row * (self.tile_size * 2 + spacing)
                    rect = pygame.Rect(pos_x, pos_y, self.tile_size * 2, self.tile_size * 2)
                    if rect.collidepoint(self.mouse_pos):
                        self.selected_tile = tile_key
                        break
                # Check button inputs, map editing clicks, etc.
                map_origin_x = self.tile_size * 4 + 50 - self.camera_offset_x
                map_origin_y = 20 - self.camera_offset_y
                map_rect = pygame.Rect(map_origin_x, map_origin_y,
                                       self.map_surface.get_width(), self.map_surface.get_height())
                if map_rect.collidepoint(self.mouse_pos):
                    relative_x = self.mouse_pos[0] - map_origin_x
                    relative_y = self.mouse_pos[1] - map_origin_y
                    col = relative_x // self.tile_size
                    row = relative_y // self.tile_size
                    if row < self.map_height and col < self.map_width:
                        self.push_state()  # Save state before change
                        self.map[row][col] = self.selected_tile

    def update(self):
        # Update any dynamic parts if necessary
        pass

    def draw(self, screen):
        screen.fill((50, 50, 150))
        self.setting_surface.fill((50, 50, 150))
        # Draw the map tiles.
        for row_index, row in enumerate(self.map):
            for col_index, tile_key in enumerate(row):
                tile_image = self.tile_img[tile_key]
                self.map_surface.blit(tile_image, (col_index * self.tile_size, row_index * self.tile_size))

        # Draw grid on the map_surface.
        for col in range(self.map_width + 1):
            x = col * self.tile_size
            pygame.draw.line(self.map_surface, (0, 0, 0), (x, 0), (x, self.map_height * self.tile_size))
        for row in range(self.map_height + 1):
            y = row * self.tile_size
            pygame.draw.line(self.map_surface, (0, 0, 0), (0, y), (self.map_width * self.tile_size, y))

        # Draw the tile palette.
        self.tile_surface.fill((50, 50, 150))
        palette_x = 20
        palette_y = 20
        tiles_per_row = 2
        spacing = 10
        for i, tile_key in enumerate(self.tile_keys):
            col = i % tiles_per_row
            row = i // tiles_per_row
            pos_x = palette_x + col * (self.tile_size * 2 + spacing)
            pos_y = palette_y + row * (self.tile_size * 2 + spacing)
            scaled_tile_image = pygame.transform.scale(self.tile_img[tile_key],
                                                       (self.tile_size * 2, self.tile_size * 2))
            self.tile_surface.blit(scaled_tile_image, (pos_x, pos_y))
            if self.selected_tile == tile_key:
                pygame.draw.rect(self.tile_surface, (255, 0, 0),
                                 (pos_x, pos_y, self.tile_size * 2, self.tile_size * 2), 2)

        # Draw buttons (example positions).
        self.undo_b = Button(image=None, pos=(720, 10), text_input="Undo (z)", font=self.font,
                             base_color=(200, 200, 200), hovering_color=(150, 150, 150))
        self.undo_b.changeColor(self.mouse_pos)
        self.redo_b = Button(image=None, pos=(650, 10), text_input="Redo (y)", font=self.font,
                             base_color=(200, 200, 200), hovering_color=(150, 150, 150))
        self.redo_b.changeColor(self.mouse_pos)
        self.save_b = Button(image=None, pos=(430, 10), text_input="Save (r)", font=self.font,
                             base_color=(200, 200, 200), hovering_color=(150, 150, 150))
        self.save_b.changeColor(self.mouse_pos)
        self.load_b = Button(image=None, pos=(500, 10), text_input="Load (l)", font=self.font,
                             base_color=(200, 200, 200), hovering_color=(150, 150, 150))
        self.load_b.changeColor(self.mouse_pos)

        self.redo_b.update(self.setting_surface)
        self.undo_b.update(self.setting_surface)
        self.load_b.update(self.setting_surface)
        self.save_b.update(self.setting_surface)

        map_draw_x = self.tile_size * 4 + 50 - self.camera_offset_x
        map_draw_y = 20 - self.camera_offset_y
        screen.blit(self.map_surface, (map_draw_x, map_draw_y))
        screen.blit(self.tile_surface, (0, 0))
        screen.blit(self.setting_surface, (0, 0))

        pygame.display.update()

    def load_map(self, filename):
        with open(filename, 'r') as f:
            map_data = json.load(f)
        return map_data

    def save_map(self, filename):
        with open(filename, "w") as f:
            json.dump(self.map, f)

    def load_images(self, directory_path, valid_extensions=('.png', '.jpg', '.jpeg', '.bmp')):
        images = {}
        for filename in os.listdir(directory_path):
            if filename.lower().endswith(valid_extensions):
                key = os.path.splitext(filename)[0]
                file_path = os.path.join(directory_path, filename)
                images[key] = pygame.image.load(file_path).convert_alpha()
        return images

    def push_state(self):
        self.undo_stack.append(copy.deepcopy(self.map))
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(copy.deepcopy(self.map))
            self.map = self.undo_stack.pop()
            self.save_map(self.map_filename)

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(copy.deepcopy(self.map))
            self.map = self.redo_stack.pop()
            self.save_map(self.map_filename)
