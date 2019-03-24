from numpy import *

from parametters import *


class ProjectileBehavior:

    def __init__(self, projectiles=[]):
        self.projectiles = projectiles

    def update(self):
        for projectile in self.projectiles:
            if projectile.is_active:
                if projectile.trajectory[0] > 0 or (projectile.trajectory[0] == 0 and projectile.orientation == RIGHT):
                    projectile.move_right(multiplier=projectile.trajectory[0] * PROJECTILE_SPEED)
                else:
                    projectile.move_left(multiplier=projectile.trajectory[0] * PROJECTILE_SPEED)

                if projectile.trajectory[1] < 0 or (projectile.trajectory[0] == 0 and projectile.orientation == DOWN):
                    projectile.move_up(multiplier=projectile.trajectory[1] * PROJECTILE_SPEED)
                else:
                    projectile.move_down(multiplier=projectile.trajectory[1] * PROJECTILE_SPEED)

                if not projectile.can_move_left() or not projectile.can_move_right():
                    projectile.set_active(False)
        self.clean()

    def clean(self):
        cmpt = len(self.projectiles) - 1
        while cmpt > -1 and len(self.projectiles) > 0:
            cmpt -= 1
            projectile = self.projectiles.__getitem__(cmpt)
            if not projectile.is_active:
                self.projectiles.pop(cmpt)


class EnnemyBehavior:
    def __init__(self, characters=[]):
        self.characters = characters

    def update(self):
        for character in self.characters:
            if character.is_active:
                if character.orientation == RIGHT and not character.can_move_right():
                    character.orientation = LEFT
                if character.orientation == LEFT and not character.can_move_left():
                    character.orientation = RIGHT

                if character.orientation == RIGHT:
                    character.move_right()
                else:
                    character.move_left()

                if character.hit:
                    character.hp -= 1
                    if character.hp <= 0:
                        character.set_active(False)
        self.clean()

    def clean(self):
        cmpt = len(self.characters) - 1
        while cmpt > -1 and len(self.characters) > 0:
            cmpt -= 1
            character = self.characters.__getitem__(cmpt)
            if not character.is_active:
                self.characters.pop(cmpt)


class EnemyAIBoss:
    def __init__(self, character):
        self.character = character
        x = linspace(0, 4 * pi, 20000)
        y = []
        for i in range(0, 80):
            y.append((cos(x[(i + 1) * 125]) - cos(x[i * 125]), sin(x[125 * (i + 1)]) - sin(x[125 * i])))
        moving_circle = []
        for i in range(len(y)):
            tuuple = [0, 0, 0, 0]
            if y[i][1] <= 0:
                tuuple[3] = abs(y[i][1])
            else:
                tuuple[2] = y[i][1]
            if y[i][0] <= 0:
                tuuple[0] = abs(y[i][0])
            else:
                tuuple[1] = y[i][0]
            moving_circle.append(tuuple)
        self.routine_func = moving_circle
        self.i = 0

    def update(self):
        if self.i > len(self.routine_func) - 1:
            self.i = 0

        self.character.move_up(self.routine_func[self.i][2])
        self.character.move_down(self.routine_func[self.i][3])
        self.character.move_left(self.routine_func[self.i][0])
        self.character.move_right(self.routine_func[self.i][1])
        self.i += 1
        if self.character.hit:
            self.character.hp -= 1
            if self.character.hp <= 0:
                self.character.set_active(False)
        self.character.attack()
