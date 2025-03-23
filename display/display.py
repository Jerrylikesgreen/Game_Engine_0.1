import pygame


set_theme = game.game_file.get_theme()

class Display:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.screen = None

    def set_game_theme(self, theme):

        self.game_theme = theme

    def get_game_theme(self):
        return self.game_theme



    def create(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

    def close(self):
        pygame.quit()
        exit()

    def update(self):
        pygame.display.flip()

    def clear(self):
        self.screen.fill((0, 0, 0))


class Panel(Display):
    def __init__(self, width, height, border_color, border_size, surface_color):
        super().__init__(width, height, border_color)
        self.border_color = border_color
        self.border_size = 2
        self.surface_color = "white"

    def create(self):
        super().create()
        self.surface = pygame.Surface((self.width, self.height))


class Button(Panel):
    def __init__(self, width, height, border_color, border_size, text, text_color, text_size):