import random
import numpy as np
from config import *


class Snake:
    def __init__(self, seed=None):
        self.grid = Grid(GAME_WIDTH, GAME_HEIGHT, seed=seed)

        self.drc = None
        self.length = 1

        self.body = []
        self.head = self.grid.set(int(self.grid.rows/2), int(self.grid.cols/2), HEAD)

        self.apple = self.grid.set_random(APPLE)

        self.steps = 0
        self.hunger = 0

    def key_press(self, dir):
        backwards = turn_180(self.drc)
        if backwards != dir:
            self.drc = dir

    def offset_head(self, drc):
        return np.add(self.head, drc)

    def look_in_direction(self, drc):
        see = {}

        pos = self.head
        look = None
        distance = 0
        while look is not WALL:
            distance += 1
            pos = np.add(pos, drc)
            look = self.grid.get(*pos)
            if look not in see:
                see[look] = distance
        return see

    def step(self):
        if self.hunger >= 50+50*self.length:
            return False
        if self.hunger > 0 and self.steps == 0:
            return False

        if self.drc is not None:
            r, c = self.offset_head(self.drc)
            under = self.grid.get(r, c)
            if under == APPLE:
                self.length += 1
                self.apple = self.grid.set_random(APPLE)
                self.hunger = 0
            elif under == SNAKE or under == WALL:
                return False

            if len(self.body) >= self.length:
                self.grid.set(*self.body[0], EMPTY)
                del self.body[0]

            self.body.append(self.head)
            self.grid.set(*self.body[-1], SNAKE)

            self.head = self.grid.set(r, c, HEAD)

            self.steps += 1
        self.hunger += 1
        return True

    def one_hot_tile(self, tile):
        keys = [EMPTY, APPLE, SNAKE, HEAD]
        return [1 if k == tile else 0 for k in keys]

    def one_hot_direction(self, direction):
        keys = [EMPTY, APPLE, SNAKE, HEAD]
        return [1 if k == direction else 0 for k in keys]


class Grid:
    def __init__(self, width, height, seed=None):
        self.cols = width
        self.rows = height

        self.random = random.Random(seed)

        self.array = np.full((self.rows, self.cols), EMPTY)

    def set(self, r, c, val):
        self.array[r][c] = val
        return r, c

    def get(self, r, c):
        if not self.in_bounds(r, c):
            return WALL
        return self.array[r][c]

    def set_random(self, val, must_be_empty=True):
        r = self.random.randrange(self.rows)
        c = self.random.randrange(self.cols)
        if self.array[r][c] == EMPTY or must_be_empty is False:
            self.array[r][c] = val
            return r, c
        else:
            return self.set_random(val)

    def in_bounds(self, r, c):
        if r >= self.rows or r < 0 or c >= self.cols or c < 0:
            return False
        return True


def turn_right(drc):
    if drc == UP:
        return RIGHT
    elif drc == RIGHT:
        return DOWN
    elif drc == DOWN:
        return LEFT
    elif drc == LEFT:
        return UP


def turn_left(drc):
    if drc == UP:
        return LEFT
    elif drc == LEFT:
        return DOWN
    elif drc == DOWN:
        return RIGHT
    elif drc == RIGHT:
        return UP


def turn_180(drc):
    if drc == UP:
        return DOWN
    elif drc == LEFT:
        return RIGHT
    elif drc == DOWN:
        return UP
    elif drc == RIGHT:
        return LEFT
