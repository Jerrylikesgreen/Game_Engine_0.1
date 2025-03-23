import pygame
from game.game_file import game_theme


class Display:
    """
    Base display (window) class. Expects:
      - width (int)
      - height (int)
      - title (string)
      - game_theme (dict) e.g. the dictionary from game_file
    """
    def __init__(self, width, height, title, game_theme):
        self.width = game_theme.get("display_width", width)
        self.height = game_theme.get("display_height", height)
        self.title = game_theme.get("display_title", title)
        self.screen = None
        self.game_theme = game_theme


    def set_game_theme(self, game_theme):
        self.game_theme = game_theme

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
        # Use surface_color from the theme dictionary if you want
        color = self.game_theme.get("surface_color", (0, 0, 0))
        # If surface_color is a string like 'white', convert to pygame color
        # or just do a quick mapping yourself. For now, let's just show an example:
        if isinstance(color, str) and color.lower() == "white":
            color = (255, 255, 255)
        self.screen.fill(color)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    background = Background(
        "background.png",
        speed=(0.1, 0.1),
        repeat_x=True,
        repeat_y=True
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        dt = clock.tick(60) / 1000.0  # milliseconds to seconds
        background.update(dt)

        screen.fill((0, 0, 0))
        background.draw(screen)
        pygame.display.flip()

    pygame.quit()
