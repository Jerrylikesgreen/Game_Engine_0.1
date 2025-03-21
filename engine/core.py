# engine/core.py

import pygame

class GameEngine:
    def __init__(self, screen_width=800, screen_height=600):
        # Screen dimensions or other config
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Collection of entities (game objects)
        self.entities = []
        
        # Background color
        self.background_color = (0, 0, 0)  # Black by default

    def add_entity(self, entity):
        """
        Add a new entity to the engine.
        """
        self.entities.append(entity)

    def remove_entity(self, entity):
        """
        Remove an existing entity from the engine.
        """
        if entity in self.entities:
            self.entities.remove(entity)

    def update(self, dt):
        """
        Update all entities.
        
        :param dt: 'delta time' in seconds since the last frame.
        """
        for entity in self.entities:
            entity.update(dt)

    def render(self, screen):
        """
        Render (draw) the current frame.
        
        :param screen: Pygame surface representing the main game window.
        """
        # Clear the screen
        screen.fill(self.background_color)

        # Draw each entity
        for entity in self.entities:
            entity.render(screen)
