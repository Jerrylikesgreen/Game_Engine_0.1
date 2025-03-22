

import pygame
from engine.core import GameEngine

def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Game Engine_0.1")

    actions = {
        "move_left": move_left
    }

    game_engine = GameEngine(width, height, "keys.json", actions)


    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            game_engine.input_handling(event)

        dt = clock.get_time() / 1000.0  
        game_engine.update(dt)

        game_engine.render(screen)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

def move_left():
    print("move left")

if __name__ == "__main__":
    main()
