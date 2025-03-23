import pygame, sys, json, os, copy

from engine.map_editor.button import Button


class MapEditor:
    def __init__(self, map_filename):
        self.tile_size = 32
        self.map_filename = map_filename

        # Automatically load all images from the "tiles" directory.
        self.tile_img = self.load_images("tiles")
        # List of tile keys (order for palette)
        self.tile_keys = list(self.tile_img.keys())
        # Start with the first tile selected
        self.selected_tile = self.tile_keys[0]

        self.undo_stack = []
        self.redo_stack = []

        # Set up font for drawing buttons
        self.font = pygame.font.SysFont("arial", 16)

        # Load the map from JSON. The map should be a 2D list of strings.
        self.map = self.load_map(self.map_filename)
        self.map_width = len(self.map[0])
        self.map_height = len(self.map)
        # Create a surface for the map.
        self.map_surface = pygame.Surface((self.map_width * self.tile_size, self.map_height * self.tile_size))
        self.tile_surface = pygame.Surface((self.tile_size * 4 + 50, self.tile_size * 2 * len(self.tile_img) + 50))

    def run(self, screen, clock):
        running = True
        while running:
            clock.tick(60)
            self.handle_events()
            self.update()
            self.draw(screen)
        return True

    def handle_events(self):
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if click is on the Undo button
                if self.redo_b.checkForInput(self.mouse_pos):
                    self.redo()
                if self.undo_b.checkForInput(self.mouse_pos):
                    self.undo()
                if self.load_b.checkForInput(self.mouse_pos):
                    print("loaded map")
                if self.save_b.checkForInput(self.mouse_pos):
                    self.save_map(self.map_filename)

                map_offset_x = self.tile_size * 4 + 50
                map_offset_y = 20
                map_rect = pygame.Rect(map_offset_x, map_offset_y, self.map_surface.get_width(),
                                       self.map_surface.get_height())
                if map_rect.collidepoint(self.mouse_pos):
                    # Adjust the mouse position relative to the map surface.
                    relative_x = self.mouse_pos[0] - map_offset_x
                    relative_y = self.mouse_pos[1] - map_offset_y
                    col = relative_x // self.tile_size
                    row = relative_y // self.tile_size
                    if row < self.map_height and col < self.map_width:
                        self.push_state()  # Save state before change
                        self.map[row][col] = self.selected_tile

                # Check if the click is inside the palette on the tile_surface.
                # The palette is drawn at fixed coordinates on tile_surface (which is blitted at (0,0)).
                palette_x = 20
                palette_y = 20
                for i, tile_key in enumerate(self.tile_keys):
                    # Each tile is drawn at double size (64x64) with a 10px spacing.
                    rect = pygame.Rect(palette_x, palette_y + i * (self.tile_size * 2 + 10), self.tile_size * 2,
                                       self.tile_size * 2)
                    if rect.collidepoint(self.mouse_pos):
                        self.selected_tile = tile_key
                        break

    def update(self):
        # Update any dynamic parts if necessary
        pass

    def draw(self, screen):
        screen.fill((50, 50, 150))
        # Draw the map by iterating over rows and columns.
        for row_index, row in enumerate(self.map):
            for col_index, tile_key in enumerate(row):
                tile_image = self.tile_img[tile_key]
                self.map_surface.blit(tile_image, (col_index * self.tile_size, row_index * self.tile_size))

        self.tile_surface.fill((50, 50, 150))

        # Draw the tile palette on the left side of tile_surface.
        # Each tile is displayed at double size (64x64).
        palette_x = 20
        palette_y = 20
        for i, tile_key in enumerate(self.tile_keys):
            pos_x = palette_x
            # Use (self.tile_size * 2) for double the size and add spacing of 10 pixels.
            pos_y = palette_y + i * (self.tile_size * 2 + 10)
            # Scale the tile image to 64x64.
            scaled_tile_image = pygame.transform.scale(self.tile_img[tile_key],
                                                       (self.tile_size * 2, self.tile_size * 2))
            self.tile_surface.blit(scaled_tile_image, (pos_x, pos_y))
            # Draw a red border if this tile is selected.
            if self.selected_tile == tile_key:
                pygame.draw.rect(self.tile_surface, (255, 0, 0), (pos_x, pos_y, self.tile_size * 2, self.tile_size * 2),2)

        screen.blit(self.map_surface, (self.tile_size * 4 + 50, 20))
        screen.blit(self.tile_surface, (0, 0))

        self.undo_b = Button(image=None, pos=(720, 10), text_input="Undo (z)", font=self.font, base_color=(200, 200, 200), hovering_color=(150, 150, 150))
        self.undo_b.changeColor(self.mouse_pos)

        self.redo_b = Button(image=None, pos=(650, 10), text_input="Redo (y)", font=self.font, base_color=(200, 200, 200), hovering_color=(150, 150, 150))
        self.redo_b.changeColor(self.mouse_pos)

        self.save_b = Button(image=None, pos=(430, 10), text_input="Save (r)", font=self.font, base_color=(200, 200, 200),hovering_color=(150, 150, 150))
        self.save_b.changeColor(self.mouse_pos)

        self.load_b = Button(image=None, pos=(500, 10), text_input="Load", font=self.font, base_color=(200, 200, 200),hovering_color=(150, 150, 150))
        self.load_b.changeColor(self.mouse_pos)

        self.redo_b.update(screen)
        self.undo_b.update(screen)
        self.load_b.update(screen)
        self.save_b.update(screen)

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
        # Save a deep copy of the current map state
        self.undo_stack.append(copy.deepcopy(self.map))
        # Once a new change is made, clear the redo stack
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            # Save current state in redo stack
            self.redo_stack.append(copy.deepcopy(self.map))
            # Restore last state from undo stack
            self.map = self.undo_stack.pop()
            self.save_map(self.map_filename)

    def redo(self):
        if self.redo_stack:
            # Save current state in undo stack
            self.undo_stack.append(copy.deepcopy(self.map))
            # Restore last state from redo stack
            self.map = self.redo_stack.pop()
            self.save_map(self.map_filename)
