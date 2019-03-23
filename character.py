import pygame
from parametters import *
from pygame.math import Vector2

class HitBox(pygame.sprite.Sprite):

    def __init__(self, rect, is_rect=True):
        super().__init__()
        self.rect = rect
        self.radius = (rect.x / 2) ** 2 + (rect.y / 2) ** 2  # (x/2) ^2 + (y/2) ^2
        self.is_rect = is_rect

    def touched(self, other_hitbox, ratio=1):
        """
        Returns true if there is an intersection between the two objects
        :param other_hitbox:
        :return:
        """
        return pygame.sprite.collide_rect(self, other_hitbox) if self.is_rect else pygame.sprite.collide_circle(self,
                                                                                                                other_hitbox)

    def ontouch(self, other):
        print("Object touched")


class Character(HitBox):

    def __init__(self, screen, name="Paladin", is_forward=False,):
        self.screen = screen
        self.is_forward = is_forward
        self.image = pygame.image.load(
            "resources/images/" + name.lower() + "_" + ("bw" if not is_forward else "fw") + ".png")
        if not is_forward:
            self.image = pygame.transform.flip(self.image, True, False)
        self.name = name
        self.rect = self.image.get_rect()
        super().__init__(self.rect)
        self.screen_rect = screen.get_rect()

        # Start the character at the bottom center of the screen.
        self.rect.centerx = 0 + width
        self.rect.bottom = self.screen_rect.bottom - int(ground_width * 89 / 100)

        # Speed of the character
        self.speed = 3
        self.min_speed = self.speed
        self.center = float(self.speed)

        # Set a variable for each movement.
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.is_attacking = False

        self.direction = [RIGHT, LEFT]  # if is_forward else [LEFT, RIGHT]
        self.orientation = self.direction[0]
        self.animation = pygame.image.load("resources/images/slash.png")


    def attack(self):
        animation_rect = animation.get_rect()
        animation_rect.bottom = self.rect.bottom

        animation_rect.centerx = self.rect.centerx

        if self.orientation == RIGHT:
            animation_rect.centerx += self.speed
        elif self.orientation == LEFT:
            animation_rect.centerx -= self.speed

        self.animation = animation
        self.animation_rect = animation_rect

    def update(self):
        if self.rect.right <= self.screen_rect.right:
            if self.moving_right:
                self.orientation = self.direction[0]
                self.rect.centerx += self.speed

        if self.rect.left > 0:
            if self.moving_left:
                self.orientation = self.direction[1]
                self.rect.centerx -= self.speed

        if self.rect.top > 0:
            if self.moving_up:
                self.rect.bottom -= self.speed

        if self.rect.bottom <= self.screen_rect.bottom - int(ground_width * 90 / 100):
            if self.moving_down:
                self.rect.bottom += self.speed

        if self.is_attacking:
            self.attack()

    def orient(self, image, rect, orientation=RIGHT):
        self.screen.blit(image if orientation == RIGHT else pygame.transform.flip(image, True, False), rect)

    def blitme(self):
        self.orient(self.image, self.rect, self.orientation)
        if self.is_attacking and self.animation is not None:
            self.orient(self.animation, self.animation_rect, self.orientation)

