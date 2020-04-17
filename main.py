import math
import random
import time
from tkinter import Tk, Canvas
from threading import Timer


class Game:
    def __init__(self, cWidth, cHeight):
        self.root = Tk()
        self.root.bind('<KeyPress>', self.HandleKeyboardPress)
        self.root.bind('<KeyRelease>', self.HandleKeyboardRelease)
        self.width = cWidth
        self.height = cHeight

        self.canvas = Canvas(self.root, width=cWidth, height=cHeight, background='black')
        self.canvas.pack()
        self.sprites = {
            # obj: canvasID,
        }
        self._ship = Ship(self)
        self.sprites[self._ship] = self.canvas.create_oval(*self._ship.coords, fill='white')

        self.NewRock()

    def Overlap(self, IDs):
        objects = [self.GetSpriteByID(ID) for ID in IDs]
        print('Game.Overlap(', objects)
        print('Bullets', [isinstance(obj, Bullet) for obj in objects])
        print('Rocks', [isinstance(obj, Rock) for obj in objects])

        if any([isinstance(obj, Bullet) for obj in objects]):
            print('Bullet is touching something')
            if any([isinstance(obj, Rock) for obj in objects]):
                for obj in objects:
                    if isinstance(obj, Rock):
                        self.DeleteSprite(obj)
                        self.NewRock()

    def NewRock(self):
        rock = Rock(self)
        self.AddSprite(rock)

    def HandleKeyboardPress(self, event):
        print('HandleKeyboardPress(', event)
        if event.keysym.lower() in ['left', 'right', 'up', 'down']:
            self._ship.Thrust(event.keysym.lower())
        if event.keysym.lower() == 'space':
            self._ship.Shoot()

    def HandleKeyboardRelease(self, event):
        print('HandleKeyboardPress(', event)
        if event.keysym.lower() in ['left', 'right', 'up', 'down']:
            self._ship.Thrust(None)

    def AddSprite(self, obj):
        self.sprites[obj] = self.canvas.create_oval(
            *obj.coords,
            fill=obj.color,
        )

    def GetSpriteByID(self, ID):
        for k, v in self.sprites.items():
            if v == ID:
                return k

    def DeleteSprite(self, obj):
        ID = self.sprites.get(obj, None)
        if ID:
            self.canvas.delete(ID)
            self.sprites.pop(obj)

    def Update(self):
        print('Game.Update()')
        for sprite, ID in self.sprites.copy().items():
            sprite.Update()
            self.canvas.coords(ID, sprite.coords)
            print(sprite)

            res = self.canvas.find_overlapping(*sprite.coords)
            if len(res) > 1:
                self.Overlap(res)


class Body:
    WIDTH = 10

    def __init__(self, host):
        self.host = host

        self.x = self.host.width / 2
        self.y = self.host.height / 2

        self.xVelocity = 0
        self.yVelocity = 0

        self.yAcceleration = 0
        self.xAcceleration = 0

        self.color = 'white'

    @property
    def coords(self):
        return (
            self.x,
            self.y,
            self.x + self.WIDTH,
            self.y + self.WIDTH
        )

    def Update(self):
        self.xVelocity += self.xAcceleration
        self.xVelocity *= self.DRAG
        self.x += self.xVelocity

        self.yVelocity += self.yAcceleration
        self.yVelocity *= self.DRAG
        self.y += self.yVelocity

        if self.x < 0 - self.WIDTH / 2:
            self.x += self.host.width
        elif self.x > self.host.width - self.WIDTH / 2:
            self.x -= self.host.width

        if self.y < 0 - self.WIDTH / 2:
            self.y += self.host.height
        elif self.y > self.host.height - self.WIDTH / 2:
            self.y -= self.host.height

    def __str__(self):
        return f'<{type(self).__name__}: x={self.x}, y={self.y}, xVel={self.xVelocity}, yVel={self.yVelocity}>'


class Bullet(Body):
    SPEED = 10
    DRAG = 1.0
    LIFE_SPAN = 2

    def __init__(self, host, x, y, xDirection, yDirection):
        super().__init__(host)

        self.x = x
        self.y = y

        self.xVelocity = xDirection * self.SPEED
        self.yVelocity = yDirection * self.SPEED

        self.color = 'red'

        self._creationTime = time.monotonic()

    def Update(self):
        super().Update()
        if time.monotonic() - self._creationTime > self.LIFE_SPAN:
            self.host.DeleteSprite(self)


class Ship(Body):
    WIDTH = 25
    THRUST_FORCE = 1
    DRAG = 0.99  # 1.0 means no drag
    SHOOT_DELAY = 0.2

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._lastShotTime = time.monotonic()

    def Thrust(self, direction):
        if direction == 'up':
            self.yAcceleration = - self.THRUST_FORCE
        elif direction == 'down':
            self.yAcceleration = self.THRUST_FORCE
        elif direction == 'left':
            self.xAcceleration = -self.THRUST_FORCE
        elif direction == 'right':
            self.xAcceleration = self.THRUST_FORCE
        else:
            self.xAcceleration = 0
            self.yAcceleration = 0

    def Shoot(self):
        if self.xVelocity or self.yVelocity:
            if time.monotonic() - self._lastShotTime > self.SHOOT_DELAY:
                self._lastShotTime = time.monotonic()
                bullet = Bullet(
                    self.host,
                    self.x + self.WIDTH / 2, self.y + self.WIDTH / 2,
                    *UnitVector(self.xVelocity, self.yVelocity)
                )
                self.host.AddSprite(bullet, )


class Rock(Body):
    DRAG = 1.0
    SMALLEST = 25

    def __init__(self, host, *a, **k):
        super().__init__(host, *a, **k)
        self.color = 'grey'
        self.WIDTH = random.randint(int(self.host.width / 25), int(self.host.width / 10))
        self.x = random.randint(0, self.host.width)
        self.y = random.randint(0, self.host.height)
        self.xVelocity = random.randint(1, 10)
        self.yVelocity = random.randint(1, 10)


def UnitVector(x, y):
    mag = math.sqrt((math.pow(x, 2) + math.pow(y, 2)))
    xUnit = x / mag
    yUnit = y / mag
    return xUnit, yUnit


game = Game(400, 400)


def Loop():
    while True:
        game.Update()
        time.sleep(0.1)


Timer(0, Loop).start()
game.root.mainloop()
