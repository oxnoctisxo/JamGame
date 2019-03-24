import pygame

from parametters import *


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
        return intersection.width != 0 or intersection.height != 0
        # return
        #   pygame.sprite.collide_rect(self, other_hitbox) if self.is_rect else pygame.sprite.collide_circle(self,
        #                                                                                                   other_hitbox)

    def ontouch(self):
        if self.is_active:
            if VERBOSE:
                print("Object touched")

    def add_collision_listenr(self, collision_listener):
        self.collision_listeners.append(collision_listener)

    def hitbox_update(self):
        # Checks all the collisions
        for collision_listener in self.collision_listeners:
            if collision_listener.is_active:
                if self.touched(collision_listener):
                    self.ontouch()


class Character(HitBox):

    def __init__(self, screen, name="Paladin", is_forward=False, dimensions=CHARACTER_DIMENSIONS):
        self.screen = screen
        self.is_forward = is_forward
        self.image = pygame.image.load(
            IMAGE_RESOURCES + name.lower() + "_" + ("bw" if not is_forward else "fw") + ".png")
        self.image = pygame.transform.scale(self.image, dimensions)
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
        self.speedx = 6
        self.speedy = 6
        self.initial_speed = self.speedx
        self.center = float(self.speedx)

        # Set a variable for each movement.
        self.moving_horizontally = False
        self.moving_vertically = False
        self.is_attacking = False

        self.direction = [RIGHT, LEFT]  # if is_forward else [LEFT, RIGHT]
        self.orientation = self.direction[0]
        self.animation = pygame.image.load("resources/images/slash.png")
        self.rigid_bodies = []
        self.type = ENNEMY_TYPE

        # Jumping animation

        self.jumping_animation = []
        self.jumping_animation.extend([self.move_up] * 25)
        self.jumping_animation.extend([self.move_down] * 25)
        self.jumping_animation_indice = 0
        self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jumping_animation_indice = 0

    def manage_jump(self):
        if self.jumping_animation_indice < len(self.jumping_animation) and self.is_jumping:
            self.jumping_animation[self.jumping_animation_indice](multiplier=2)
            self.jumping_animation_indice = self.jumping_animation_indice + 1
            if VERBOSE:
                print("Jumping", self.jumping_animation_indice)
        else:
            self.is_jumping = False
            self.jumping_animation_indice = 0

    def move_up(self, val=True, multiplier=1):
        self.moving_vertically = val
        self.speedy = -abs(self.initial_speed * multiplier)

    def move_down(self, val=True, multiplier=1):
        self.moving_vertically = val
        self.speedy = abs(self.initial_speed * multiplier)

    def move_right(self, val=True, multiplier=1):
        self.moving_horizontally = val
        self.speedx = abs(self.initial_speed * multiplier)

    def move_left(self, val=True, multiplier=1):
        self.moving_horizontally = val
        self.speedx = -abs(self.initial_speed * multiplier)

    def __str__(self):
        return str(self.name)

    def attack(self):
        animation_rect = self.animation.get_rect()
        animation_rect.bottom = self.rect.bottom

        animation_rect.centerx = self.rect.centerx

        animation_rect.centerx += self.speedx

        self.animation_rect = animation_rect

    def campled_movement(self, offset, isX=True):
        """
        Returns the closets version of the offest which doesn't collide with a wall
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

    def update(self):
        if not self.is_active:
            return
        if self.can_move_right() and self.can_move_left():
            if self.moving_horizontally:
                self.orientation = self.direction[0] if self.speedx >= 0 else self.direction[1]
                self.rect.centerx += self.campled_movement(self.speedx, isX=True)

        if self.rect.top > 0 and self.rect.bottom <= self.screen_rect.bottom:
            if self.moving_vertically:
                real_offset = self.campled_movement(self.speedy, isX=False)
                self.rect.bottom += real_offset
                # If we did hit the ground
                if real_offset != self.speedy:
                    self.jumping = False
                    self.jumping_animation_indice = 0

        self.manage_jump()
        if self.is_attacking:
            self.attack()

        self.hitbox_update()

    def orient(self, image, rect, orientation=RIGHT):
        self.screen.blit(image if orientation == RIGHT else pygame.transform.flip(image, True, False), rect)

    def blitme(self):
        self.orient(self.image, self.rect, self.orientation)
        if self.is_attacking and self.animation is not None:
            self.orient(self.animation, self.animation_rect, self.orientation)


class RigidBody(Character):

    def __init__(self, screen, x, y, filename="ground", dimension=RIGID_BODY_DIMENSIONS):
        super().__init__(screen, filename, True, dimension)
        self.screen = screen

        self.rect.x = x
        self.rect.y = y - dimension[1]
        self.is_active = True
        self.type = RIGID_BODY

    def update(self):
        # Checks all the collisions
        for collision_listener in self.collision_listeners:
            if collision_listener.is_active:
                if self.touched(collision_listener):
                    self.ontouch()


class Spawn(pygame.sprite.Sprite):

    def __init__(self, screen, x, y, orientation=RIGHT, mask=None, type=ENNEMY_TYPE):
        super().__init__()

        self.screen = screen
        self.x = x
        self.y = y
        self.mask = mask
        self.image = pygame.image.load("resources/images/spawn.png")
        self.rect = self.image.get_rect()
        self.type = type
        self.screen_rect = screen.get_rect()
        # Start the character at the bottom center of the screen.
        self.rect.centerx = 0 + width / 2
        self.rect.bottom = self.screen_rect.bottom - int(ground_width * 89 / 100)

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
        :param item:
        :return:
        """
        return self.type == item.type

    def orient(self, image, rect, orientation=RIGHT):
        self.screen.blit(image, rect)

    def blitme(self):
        self.orient(self.image, self.rect, RIGHT)


class EnnemyAI1:

    def __init__(self, characters=[]):
        self.characters = characters

    def update(self):
        for character in self.characters:
            if character.orientation == RIGHT and not character.can_move_right():
                character.orientation = LEFT
            if character.orientation == LEFT and not character.can_move_left():
                character.orientation = RIGHT

            if character.orientation == RIGHT:
                character.move_right()
            else:
                character.move_left()

class Projectile:
    def __init__(self, x,y,speed_x,speed_y,origin):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.sender_type = origin
    def move(self):
        self.x += speed_x
        self.y += speed_y


# class Boss:
#
#     def __init__(self,x,y,patern,brain):
#         self.attacks = []
#         self.pos = (x,y)
#         self.IsDead = True
#         self.patern = patern
#         self.brain = brain
#
#
#     def on_hit(self):
#         print('boss tué')
#         self.brain.Wave()
#
#
#
#
#     def on_hit(self):
#         self.IsDead = True
#         self.brain.num_en -= 1
#         print("ennemi tué")
#         if self.brain.num_en <= 0:
#             self.brain.Boss()
#
#
#
#
# class Brain:
#
#     def __init__ (self, boss):
#         self.en_list = ["LOL", "WOW", "Spinner"] #liste des ennemis (fauudra foutre les types)
#         self.waves = [[6,0,0],[6,2,0],[8,6,3]] #qtt de chaque ennemi pour chaque vague
#         self.attacks = [1,1,2]   #patterns d'attaques du boss
#         self.wave = 0  #vague suivante
#         self.boss = boss
#         self.num_en = 0
#         self.spawnTime = False
#
#     def Wave(self):
#         if self.wave >= len(self.waves):
#             print("Finiti")
#             return False                    #Mettre un systteme de fin du jeu/loop en place
#         self.spawnTime = True
#         for i in range(len(self.en_list)):
#             print("spawn de {} {}".format(str(self.waves[self.wave][i]),self.en_list[i]))   # INSERER FONCTIONDE SPAWN
#             self.num_en += self.waves[self.wave][i]
#         self.spawnTime = False
#
#
#     def Boss(self):
#         if self.wave >= len(self.waves):
#             print("Finito")
#             return False                    #Mettre un systteme de fin du jeu/loop en place
#         print("spawn du boss avec le patern " + str(self.attacks[self.wave]))    #INSERER SPAWN DE BOSS
#         self.wave += 1
#
