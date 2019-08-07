import numpy as np
import time, random
import os

import snake
import brain
from config import *


class Creature:
    def __init__(self, bran, grid=None):
        if grid is None:
            grid = snake.Grid()
        self.snake = snake.Snake(grid)
        self.brain = bran

        self.dead = False

    def fitness(self):
        return self.snake.length - self.snake.steps/1000

    def step(self, die_hunger=True):
        self.brain.set_inputs(self.snake)
        output = self.brain.predict()

        keys = [UP, RIGHT, DOWN, LEFT]
        index = output.argmax()
        self.snake.key_press(keys[index])

        if self.snake.step() is False:
            self.dead = True
        if die_hunger:
            if self.snake.hunger >= 50+50*self.snake.length:
                self.dead = True
            if self.snake.hunger > 0 and self.snake.steps == 0:
                self.dead = True


def draw(grid, indent="", pre=""):
    print(pre)
    s = ""
    for r in range(grid.rows):
        s += indent
        for c in range(grid.cols):
            cell = grid.get(r, c)
            if cell == EMPTY:
                s += "\033[0;107m  \033[0m"
            elif cell == APPLE:
                s += "\033[0;41m  \033[0m"
            elif cell == SNAKE:
                s += "\033[0;42m  \033[0m"
            elif cell == HEAD:
                # s += "\033[1;101;33m[]\033[0m"
                s += "\033[1;42;33m[]\033[0m"
        s += "\n"
    print(s)


if __name__ == '__main__':
    creatures = []

    seed = time.time()
    if os.path.exists(SAVE_FP):
        print("Loading brain from save file...")
        creatures = [Creature(brain.Brain(load=SAVE_FP).mutated(), snake.Grid(seed=seed)) for c in range(NUM_CREATURES)]
    else:
        print("Initializing population...")
        creatures = [Creature(brain.Brain(), snake.Grid(seed=seed)) for c in range(NUM_CREATURES)]

    idx = 0
    while True:
        last_time = time.time()
        s = 0

        longest = creatures[0]
        while True:
            all_dead = True
            for c in creatures:
                if not c.dead:
                    all_dead = False
                    c.step()
                    if c.snake.length > longest.snake.length or (longest.dead and c.snake.length == longest.snake.length):
                        longest = c
            if all_dead:
                break

            if not longest.dead:
                draw(longest.snake.grid,
                     pre="Generation {}, step {};\n Creature {}, length {}, fitness {}".format(idx, s, creatures.index(longest),
                                                                                               longest.snake.length,
                                                                                               round(longest.fitness(), 3)))

            s += 1

        print("Generation {} complete after {} seconds".format(idx, round(time.time()-last_time, 4)))

        creatures = list(sorted(creatures, key=lambda c: c.fitness()))
        best = creatures[-1]
        second_best = creatures[-2]

        print("Best score: {}; Second best score: {}".format(best.snake.length, second_best.snake.length))

        if idx % SAVE_INTERVAL == 0:
            print("Saving...")
            best.brain.save(SAVE_FP)
        print("Repopulating...")

        seed = time.time()
        creatures = [Creature(best.brain, snake.Grid(seed=seed))]
        for n in range(NUM_CREATURES-1):
            creatures.append(Creature(best.brain.crossover(second_best.brain).mutated(), snake.Grid(seed=seed)))

        idx += 1


