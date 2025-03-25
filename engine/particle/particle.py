import pygame
from pygame.math import Vector2
from typing import Tuple, Optional

class Particle(pygame.sprite.Sprite):
    def __init__(
        self,
        groups: pygame.sprite.Group,
        pos: Tuple[float, float],
        color: Tuple[int, int, int],
        direction: Vector2,
        speed: float,
        size: int,
        fade_speed: float,
        screen_width: int,
        screen_height: int,
        lifetime: Optional[float] = None,
        acceleration: Optional[Vector2] = None,
        angular_velocity: float = 0.0
    ):
        """
        Initialize a particle.

        :param groups: Sprite groups to add the particle to.
        :param pos: Initial position as a tuple.
        :param color: Particle color (RGB tuple).
        :param direction: Initial direction as a Vector2.
        :param speed: Movement speed.
        :param size: Diameter of the particle.
        :param fade_speed: Rate at which the particle fades.
        :param screen_width: Width of the screen (for bounds checking).
        :param screen_height: Height of the screen (for bounds checking).
        :param lifetime: Optional lifetime of the particle in seconds.
        :param acceleration: Optional acceleration vector (default: Vector2(0, 0)).
        :param angular_velocity: Optional angular velocity (degrees per second) for rotation.
        """
        super().__init__(groups)
        self.pos = Vector2(pos)
        # Normalize the direction and initialize velocity
        self.direction = direction.normalize() if direction.length() != 0 else Vector2(0, 0)
        self.velocity = self.direction * speed
        self.acceleration = acceleration if acceleration is not None else Vector2(0, 0)
        self.fade_speed = fade_speed
        self.size = size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.lifetime = lifetime
        self.age = 0.0
        self.alpha = 255

        # Rotation attributes
        self.angular_velocity = angular_velocity
        self.rotation = 0.0

        self.color = color
        self.create_surf()

    def create_surf(self) -> None:
        """Create the particle surface with per-pixel alpha."""
        self.original_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.original_image, self.color, (self.size // 2, self.size // 2), self.size // 2)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt: float) -> None:
        """Update particle position, fade effect, rotation, and lifetime."""
        # Update velocity with acceleration
        self.velocity += self.acceleration * dt
        # Update position based on velocity
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        # Update rotation if an angular velocity is specified
        if self.angular_velocity:
            self.rotation = (self.rotation + self.angular_velocity * dt) % 360
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
            self.image.set_alpha(self.alpha)
            self.rect = self.image.get_rect(center=self.pos)

        # Fade the particle by reducing alpha
        self.alpha = max(0, self.alpha - self.fade_speed * dt)
        self.image.set_alpha(self.alpha)

        # Update the age and kill the particle if it exceeds its lifetime
        if self.lifetime is not None:
            self.age += dt
            if self.age >= self.lifetime:
                self.kill()

        # Remove the particle if it goes out of bounds (using a margin for grace)
        margin = 50
        if (self.pos.x < -margin or self.pos.x > self.screen_width + margin or
            self.pos.y < -margin or self.pos.y > self.screen_height + margin):
            self.kill()
