

import pygame, random, math
from engine.core import GameEngine
from engine.particle.particle import Particle
from engine.utils import draw_text

def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Game Engine_0.1")

    particle_group = pygame.sprite.Group()

    actions = {
        "move_left": move_left
    }

    game_engine = GameEngine(width, height, 32,"keys.json", actions)

    running = True
    clock = pygame.time.Clock()

    #game_engine.map_editor(screen, clock)

    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # On left mouse button click, create an explosion at the mouse position.
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    create_explosion_effect(particle_group, pos, width, height)

            game_engine.input_handling(event)


        dt = clock.get_time() / 1000.0  
        game_engine.update(dt)

        #game_engine.render(screen)

        particle_group.update(dt)
        particle_group.draw(screen)

        draw_text(
            screen,
            'fps={}'.format(round(clock.get_fps())),
            25,
            (255, 255, 255),
            (10, 10)
        )
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

def move_left():
    print("move left")

def create_explosion_effect(groups: pygame.sprite.Group, pos: tuple, screen_width: int, screen_height: int,
                            num_particles: int = 200):
    """
    Create an explosive burst of particles.

    :param groups: The sprite groups to which the particles will be added.
    :param pos: The (x, y) position where the explosion originates.
    :param screen_width: The screen width for boundary checking.
    :param screen_height: The screen height for boundary checking.
    :param num_particles: Number of particles to spawn.
    """
    for _ in range(num_particles):
        # Randomize the angle for explosion spread.
        angle = random.uniform(0, 2 * math.pi)
        direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))

        # Example values tuned for an explosive effect:
        speed = random.uniform(250, 500)  # High speed for explosive spread.
        size = random.randint(5, 12)  # Particle size.
        fade_speed = random.uniform(150, 250)  # Fade speed; slower fade can look dramatic.
        lifetime = random.uniform(0.8, 1.5)  # Particles live a bit longer.
        # Use a mix of bright explosion colors: orange, red, and yellow.
        color_choices = [(255, 69, 0), (255, 140, 0), (255, 215, 0)]
        color = random.choice(color_choices)
        acceleration = pygame.math.Vector2(0, 100)  # Gravity-like pull for realism.
        angular_velocity = random.uniform(-360, 360)  # Rapid spin for added flair.

        # Spawn the particle.
        Particle(
            groups=groups,
            pos=pos,
            color=color,
            direction=direction,
            speed=speed,
            size=size,
            fade_speed=fade_speed,
            screen_width=screen_width,
            screen_height=screen_height,
            lifetime=lifetime,
            acceleration=acceleration,
            angular_velocity=angular_velocity
        )

if __name__ == "__main__":
    main()
