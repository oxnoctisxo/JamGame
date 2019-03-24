import random  as rand

import pygame

from ais import *
from parametters import *

images_cache = {}


def get_image_for(name, dimensions, is_forward=False):
    if (name + ("bw" if not is_forward else "fw")) not in images_cache:
        image = pygame.image.load(
            IMAGE_RESOURCES + name.lower() + "_" + ("bw" if not is_forward else "fw") + ".png")
        image = pygame.transform.scale(image, dimensions)
        if not is_forward:
            image = pygame.transform.flip(image, True, False)
        images_cache[name + ("bw" if not is_forward else "fw")] = image
        return image
    else:
        return images_cache[name + ("bw" if not is_forward else "fw")]


class HitBox(pygame.sprite.Sprite):

    def __init__(self, rect, is_rect=True):
        super().__init__()
        self.rect = rect
        self.radius = (rect.x / 2) ** 2 + (rect.y / 2) ** 2  # (x/2) ^2 + (y/2) ^2
        self.is_rect = is_rect
        self.is_active = False
        self.spawned = False
        self.collision_listeners = []
        self.type = ENNEMY_TYPE

    def touched(self, other_hitbox, ratio=0.9):
        """
        Returns true if there is an intersection between the two objects
        :param other_hitbox:
        :return:
        """

        intersection = self.rect.clip(other_hitbox.rect)
        return self.is_active and other_hitbox.is_active and (intersection.width != 0 or intersection.height != 0)
        # return
        #   pygame.sprite.collide_rect(self, other_hitbox) if self.is_rect else pygame.sprite.collide_circle(self,
        #                                                                                                   other_hitbox)

    def ontouch(self, collision_listener):
        if self.is_active and collision_listener.is_active and collision_listener.type != self.type:
            self.hit = True
            collision_listener.hit = True
            if VERBOSE:
                print("Object touched")

    def add_collision_listenr(self, collision_listener):
        self.collision_listeners.append(collision_listener)

    def remove_collision_listenr(self, collision_listener):
        cmpt = len(collision_listener) - 1
        while cmpt > -1 and len(collision_listener) > 0:
            cmpt -= 1
            character = self.collision_listeners.__getitem__(cmpt)
            if not character.is_active:
                self.collision_listeners.pop(cmpt)

    # for i in range(0, len(self.collision_listeners)):
    #   if self.collision_listeners[i] == self.collision_listener:
    #      self.collision_listeners.pop(i)

    def hitbox_update(self):
        # Checks all the collisions
        for collision_listener in self.collision_listeners:
            if collision_listener.is_active and self.is_active and collision_listener.type != self.type:
                if self.touched(collision_listener):
                    self.ontouch(collision_listener)
                    collision_listener.ontouch(self)
        self.clean_collision_listeners()

    def clean_collision_listeners(self):
        cmpt = len(self.collision_listeners) - 1
        while cmpt > -1 and len(self.collision_listeners) > 0:
            cmpt -= 1
            projectile = self.collision_listeners.__getitem__(cmpt)
            if not projectile.is_active:
                self.collision_listeners.pop(cmpt)


class Character(HitBox):

    def __init__(self, screen, name="Paladin", is_forward=False, dimensions=CHARACTER_DIMENSIONS):
        self.screen = screen
        self.is_forward = is_forward
        self.image = get_image_for(name=name, dimensions=dimensions, is_forward=is_forward)
        self.name = name
        self.is_boss = False
        self.rect = self.image.get_rect()
        super().__init__(self.rect)
        self.screen_rect = screen.get_rect()

        # Start the character at the bottom center of the screen.
        self.rect.centerx = 0 + width
        self.rect.bottom = self.screen_rect.bottom - int(ground_width * 89 / 100)

        # Speed of the character
        self.speed_x = 6
        self.speed_y = 6
        self.initial_speed = self.speed_x
        self.center = float(self.speed_x)

        # Set a variable for each movement.
        self.moving_horizontally = False
        self.moving_vertically = False
        self.is_attacking = False

        self.direction = [RIGHT, LEFT]  # if is_forward else [LEFT, RIGHT]
        self.orientation = self.direction[0]
        self.rigid_bodies = []
        self.type = ENNEMY_TYPE

        # Jumping animation

        self.jumping_animation = []
        self.jumping_animation.extend([self.move_up] * 25)
        self.jumping_animation.extend([self.move_down] * 25)
        self.jumping_animation_indice = 0
        self.is_jumping = False

        # Projectile
        self.projectiles = []
        self.projectileAI = ProjectileBehavior(self.projectiles)

        self.last_shoot = time.time()
        self.shotting_wait = PLAYER_ATTACK_SPEED

        # Hitting
        self.hit = False

        # RPG side
        self.hp = PLAYER_HP
        self.attacking_sound_i = pygame.mixer.Sound(SOUND_RESOURCES + ATTACK_SOUND)

    def get_pos(self):
        return self.rect.centerx, self.rect.centery

    def set_active(self, val=False):
        if not val:
            self.is_active = False
            self.hit = False
            self.jumping = False
        else:
            self.is_active = True

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jumping_animation_indice = 0

    def manage_jump(self):
        if self.jumping_animation_indice < len(self.jumping_animation) and self.is_jumping:
            self.jumping_animation[self.jumping_animation_indice](multiplier=JUMP_MULTIPLIER)
            self.jumping_animation_indice = self.jumping_animation_indice + 1
        else:
            self.is_jumping = False
            self.jumping_animation_indice = 0

    def move_up(self, val=True, multiplier=1):
        self.moving_vertically = val
        self.speed_y = int(-abs(self.initial_speed * multiplier))

    def move_down(self, val=True, multiplier=1):
        self.moving_vertically = val
        self.speed_y = int(abs(self.initial_speed * multiplier))

    def move_right(self, val=True, multiplier=1):
        self.moving_horizontally = val
        self.speed_x = int(abs(self.initial_speed * multiplier))

    def move_left(self, val=True, multiplier=1):
        self.moving_horizontally = val
        self.speed_x = int(-abs(self.initial_speed * multiplier))

    def __str__(self):
        return str(self.name)

    def clean_projectiles(self):
        """
        Cleans non active projectiles , useful for performance improvements
        :return:
        """
        cmpt = len(self.projectiles) - 1
        while cmpt > -1 and len(self.projectiles) > 0:
            cmpt -= 1
            projectile = self.projectiles.__getitem__(cmpt)
            if not projectile.is_active:
                self.projectiles.pop(cmpt)

    def attacking_sound(self):
        pygame.mixer.Channel(ATTACK_CHANNEL).play(self.attacking_sound_i)

    def attack(self):
        if self.type == PLAYER_TYPE:
            current_time = time.time()
            if current_time - self.last_shoot > self.shotting_wait:
                p = Projectile(self.screen, origin=self.type)
                p.rect.centerx = self.rect.centerx
                p.rect.centery = self.rect.centery
                p.orientation = self.orientation
                p.set_trajectory()
                p.is_active = True
                self.projectiles.append(p)
                self.last_shoot = current_time
                self.attacking_sound()
        self.clean_projectiles()

    def campled_movement(self, offset, isX=True):
        """
        Returns the closets version of the offset which doesn't collide with a wall
        :param offset:
        :param isX:
        :return:
        """
        sol = offset
        for i in range(0, abs(offset) + 1):
            ok_i = True
            for rigid_body in self.rigid_bodies:
                # Tries to predict a collision
                intersection = self.rect.move(sol if isX else 0, sol if not isX else 0).clip(rigid_body.rect)
                if intersection:
                    # If a wall collision was predicted
                    ok_i = False
                    break
            if ok_i:
                break
            else:
                sol += -1 if offset > 0 else 1
        return sol

    def can_move_right(self):
        return self.rect.right <= self.screen_rect.right

    def can_move_left(self):
        return self.rect.left > 0

    def is_moving_right(self):
        return self.speed_x >= 0

    def is_moving_left(self):
        return self.speed_x < 0

    def update(self):
        if not self.is_active:
            return
        self.projectileAI.update()

        if (self.can_move_right() and self.is_moving_right()) or (self.can_move_left() and self.is_moving_left()):
            if self.moving_horizontally:
                self.orientation = self.direction[0] if self.speed_x > 0 else self.direction[
                    1] if self.speed_x < 0 else self.orientation
                real_offset = self.campled_movement(self.speed_x, isX=True)
                self.rect.centerx += real_offset

        if self.rect.top > 0 or self.rect.bottom <= self.screen_rect.bottom:
            if self.moving_vertically:
                real_offset = self.campled_movement(self.speed_y, isX=False)
                self.rect.bottom += real_offset
                # If we did hit the ground
                if real_offset != self.speed_y:
                    self.jumping = False
                    self.jumping_animation_indice = 0

        self.manage_jump()
        if self.is_attacking:
            self.attack()

        self.hitbox_update()

    def orient(self, image, rect, orientation=RIGHT):
        self.screen.blit(image if orientation == RIGHT else pygame.transform.flip(image, True, False), rect)

    def blitme(self):
        if self.is_active:
            self.orient(self.image, self.rect, self.orientation)
        # if self.is_attacking and self.animation is not None:
        #    self.orient(self.animation, self.animation_rect, self.orientation)


class RigidBody(Character):

    def __init__(self, screen, x, y, filename="ground", dimension=RIGID_BODY_DIMENSIONS):
        super().__init__(screen, filename, True, dimension)
        self.screen = screen

        self.rect.x = x
        self.rect.y = y - dimension[1]
        self.is_active = True
        self.type = RIGID_BODY

    def update(self):
        if not self.is_active:
            return
        # Checks all the collisions
        for collision_listener in self.collision_listeners:
            if collision_listener.is_active:
                if self.touched(collision_listener):
                    self.ontouch(collision_listener)


class Spawn(pygame.sprite.Sprite):

    def __init__(self, screen, x, y, orientation=RIGHT, mask=None, type=ENNEMY_TYPE, is_for_boss=False):
        super().__init__()

        self.screen = screen
        self.x = x
        self.y = y
        self.mask = mask
        self.is_for_boss = is_for_boss
        self.image = pygame.image.load("resources/images/spawn.png")
        self.rect = self.image.get_rect()
        self.type = type
        self.screen_rect = screen.get_rect()
        # Start the character at the bottom center of the screen.
        self.rect.centerx = x
        self.rect.centery = y
        self.is_active = False

    def spawn(self, item):
        """
        Spawn an item if it can be spawned
        :return:
        """
        if self.can_spawn(item):
            item.is_active = True
            item.rect.centerx = self.rect.centerx
            item.rect.centery = self.rect.centery
            item.spawned = True
            item.blitme()
            self.blitme()

    def can_spawn(self, item):
        """
        Tells if an item is allowed to spawn somewhere
        TODO : Use byte masks ( since they can be added etc... ) instead of constants
        """
        return self.type == item.type or (self.is_for_boss and item.is_boss)

    def orient(self, image, rect, orientation=RIGHT):
        self.screen.blit(image, rect)

    def blitme(self):
        self.orient(self.image, self.rect, RIGHT)


class Projectile(Character):
    def __init__(self, screen, source=pygame.mouse, name="Projectile", is_forward=False,
                 dimensions=PROJECTILE_DIMENSIONS,
                 origin=ENNEMY_TYPE):
        super().__init__(screen, name, is_forward=is_forward, dimensions=dimensions)
        self.sender_type = origin
        self.type = origin
        self.source = source
        self.spin_direction = 0
        self.spinner_sound = pygame.mixer.Sound(SOUND_RESOURCES + SPINNER_SOUND)

    def ontouch(self, collision_listener):
        if VERBOSE:
            print("Collision listener on touch")

    # if self.is_active:
    # collision_listener.onHit()
    # self.set_active(False)

    def set_trajectory(self):
        x_mouse, y_mouse = self.source.get_pos()
        x = self.rect.centerx
        y = self.rect.centery
        self.is_active = True
        self.start_time = 0
        right_side = pow((pow(x_mouse - x, 2) + pow(y_mouse - y, 2)), 0.5)
        norm = 1 / right_side if right_side != 0 else 1
        self.trajectory = ((x_mouse - x) * norm, (y_mouse - y) * norm)

    def update(self):
        if not self.is_active:
            return

        if self.can_move_right() and self.can_move_left():
            if self.moving_horizontally:
                self.orientation = self.direction[0] if self.speed_x > 0 else self.direction[
                    1] if self.speed_x < 0 else self.orientation
                self.rect.centerx += self.campled_movement(self.speed_x, isX=True)

        if self.rect.top > 0 or self.rect.bottom <= self.screen_rect.bottom:
            if self.moving_vertically:
                real_offset = self.campled_movement(self.speed_y, isX=False)
                self.rect.bottom += real_offset
                # If we did hit the ground
                if real_offset != self.speed_y:
                    self.jumping = False
                    self.jumping_animation_indice = 0

        self.manage_jump()
        if self.name.lower() == "spinner":
            pygame.mixer.Channel(SPINNER_CHANNEL).play(self.spinner_sound)

    def orient(self, image, rect, orientation=RIGHT):
        if self.spin_direction == 0:
            self.screen.blit(pygame.transform.flip(image, False, False), rect)
        elif self.spin_direction == 1:
            self.screen.blit(pygame.transform.flip(image, False, True), rect)
        elif self.spin_direction == 2:
            self.screen.blit(pygame.transform.flip(image, True, False), rect)
        elif self.spin_direction == 3:
            self.screen.blit(pygame.transform.flip(image, True, True), rect)

    def blitme(self):
        if self.is_active:
            self.orient(self.image, self.rect, self.orientation)
            self.spin_direction = ((self.spin_direction + 1) % 4)


class Ennemy(Character):

    def __init__(self, screen, name="Ennmy1", is_forward=False, dimensions=CHARACTER_DIMENSIONS):
        super().__init__(screen, name, is_forward, dimensions)
        self.speed_x = self.speed_x + rand.randint(-1, 1)
        self.speed_y = self.speed_y + rand.randint(-1, 1)
        self.initial_speed = self.initial_speed + rand.randint(-2, 2)
        self.hp = MOB_HP

    def ontouch(self, collision_listener):
        if collision_listener.is_active and self.is_active and collision_listener.type != self.type:
            self.hit = True


class Hero(Character):

    def __init__(self, screen, name="Paladin", is_forward=False, dimensions=CHARACTER_DIMENSIONS):
        super().__init__(screen, name, is_forward, dimensions)
        self.type = PLAYER_TYPE
        self.hp = PLAYER_HP
        self.speed_x = self.speed_x + rand.randint(-1, 1)
        self.speed_y = self.speed_y + rand.randint(-1, 1)
        self.trajectory = None

    def ontouch(self, collision_listener):
        if self.is_active and collision_listener.is_active and self.type != collision_listener.type:
            self.hp = self.hp - 1
            if self.hp == 0:
                self.set_active(False)


class Boss(Character):

    def __init__(self, screen, player=None, name="Boss", is_forward=False, dimensions=BOSS_DIMENSION):
        super().__init__(screen, name, is_forward, dimensions)
        self.speed_x = self.speed_x + rand.randint(-1, 1)
        self.speed_y = self.speed_y + rand.randint(-1, 1)
        self.initial_speed = self.initial_speed + rand.randint(-2, 2)
        self.player = player
        self.hp = 10
        self.play_boss_sound()
        self.type = ENNEMY_TYPE
        self.shotting_wait = 1
        self.is_boss = True
        self.rect.centerx, self.rect.centery = (758, 325)

    def play_normal_sound(self):
        pygame.mixer.music.load(SOUND_RESOURCES + 'idle.ogg')
        pygame.mixer.music.play(-1)

    def play_boss_sound(self):
        pygame.mixer.music.load(SOUND_RESOURCES + 'boss.ogg')
        pygame.mixer.music.play(-1)

    def ontouch(self, collision_listener):
        if collision_listener.type != self.type and self.is_active and collision_listener.is_active:
            self.hit = True

    def set_active(self, val=False):
        """
        Overrite the normal parent to allow chaging the music
        :param val:
        :return:
        """
        if not val:
            print("Boss Died")
            self.is_active = False
            self.hit = False
            self.jumping = False
            self.play_normal_sound()
        else:
            self.is_active = True
            self.hit = False
            self.jumping = False
            self.hp = 50
            self.play_boss_sound()

    def attack(self):
        current_time = time.time()
        if current_time - self.last_shoot > self.shotting_wait:
            p = Projectile(self.screen, source=self.player, name="Spinner", origin=self.type,
                           dimensions=ARROW_DIMENSIONS,
                           is_forward=True)
            p.rect.centerx = self.rect.centerx
            p.rect.centery = self.rect.centery
            p.orientation = self.orientation
            p.set_trajectory()
            p.is_active = True
            self.projectiles.append(p)
            self.last_shoot = current_time

### PopUp
