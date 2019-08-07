import numpy as np
import time, random
import os

import snake
import brain
from config import *


NUM_PAIRS = 1024
PER_PAIR = 2


def is_power_of(num, p):
    if num == 1:
        return True
    elif num % p != 0:
        return False
    else:
        return is_power_of(num/p, p)


class Creature:
    def __init__(self, bran, grid):
        self.snake = snake.Snake(grid)
        self.brain = bran

        self.dead = False

    def fitness(self):
        return self.snake.length + self.snake.steps/1000

    def step(self):
        self.brain.set_inputs(self.snake)
        output = self.brain.predict()

        keys = [UP, RIGHT, DOWN, LEFT]
        index = output.argmax()
        self.snake.key_press(keys[index])

        if self.snake.step() is False:
            self.dead = True
        if self.snake.hunger >= 50+50*self.snake.length:
            self.dead = True
        if self.snake.hunger > 0 and self.snake.steps == 0:
            self.dead = True


class Pair:
    def __init__(self, g=None):
        self.grid = snake.Grid() if g is None else g
        self.creatures = []

        self.done = False

        self.remaining = 0

    def add_creature(self, bran):
        self.creatures.append(Creature(bran, self.grid))

    def get_ranked(self):
        return sorted(self.creatures, key=lambda c: c.fitness())

    def get_fittest(self):
        return self.get_ranked()[-1]

    def fitness(self):
        return self.get_fittest().fitness() + self.remaining*100

    def step(self):
        remaining = 0
        for c in self.creatures:
            if not c.dead:
                c.step()
                remaining += 1
        if remaining == 0:
            self.done = True
        self.remaining = remaining


def draw(grid, indent=""):
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
                s += "\033[1;42;33m[]\033[0m"
        s += "\n"
    print(s)


if __name__ == '__main__':
    if not is_power_of(NUM_PAIRS, PER_PAIR):
        raise Exception("Population {}, must be power of {}".format(NUM_PAIRS, PER_PAIR))

    pairs = [Pair() for p in range(NUM_PAIRS)]

    seed = time.time()
    if os.path.exists(SAVE_FP):
        print("Loading brain from save file...")
        for p in pairs:
            for c in range(PER_PAIR):
                p.add_creature(brain.Brain(load=SAVE_FP).mutated())
    else:
        print("Initializing population...")
        for p in pairs:
            for c in range(PER_PAIR):
                p.add_creature(brain.Brain())

    idx = 0
    while True:
        rnd = 0
        while True:
            step = 0
            while True:
                best = None
                finished = 0
                for p in pairs:
                    if p.done:
                        finished += 1
                    else:
                        p.step()
                    if best is None or p.fitness() > best.fitness():
                        best = p

                print("Generation {}; round {}, {}/{};\n {}".format(idx, rnd, finished, len(pairs),
                                                                    " ".join("score: {}".format(c.snake.length) for c in best.creatures if not c.dead)))
                if len(pairs) == 1:
                    draw(best.grid, indent=str(rnd))
                    time.sleep(0.03)
                else:
                    if best.remaining > 1:
                        draw(best.grid, indent=str(rnd))
                step += 1

                if finished == len(pairs):
                    break
            if len(pairs) == 1:
                break
            pool = [p.get_fittest().brain for p in pairs]

            num_pairs = int(len(pool)/PER_PAIR)
            pairs = []
            for i in range(num_pairs):
                p = Pair()
                for c in range(PER_PAIR):
                    p.add_creature(pool[i+c])
                pairs.append(p)
            rnd += 1

        ranked = pairs[0].get_ranked()
        winner = ranked[-1]
        second_place = ranked[-2]

        print("Saving...")
        winner.brain.save(SAVE_FP)

        pairs = [Pair() for p in range(NUM_PAIRS)]
        for p in pairs:
            for c in range(PER_PAIR):
                p.add_creature(winner.brain.crossover(second_place.brain).mutated())

        idx += 1


