import os, time

import snake
import brain
from config import *


class Creature:
    def __init__(self, bran, seed=None):
        self.snake = snake.Snake(seed)
        self.brain = bran

        self.dead = False

    def step(self):
        self.brain.set_inputs(self.snake)
        output = self.brain.predict()

        keys = [UP, RIGHT, DOWN, LEFT]
        index = output.argmax()
        self.snake.key_press(keys[index])

        if self.snake.step() is False:
            self.dead = True


def draw(creature, indent="", pre=""):
    print(pre)
    s = ""
    for r in range(GAME_HEIGHT):
        s += indent
        for c in range(GAME_WIDTH):
            cell = creature.snake.grid.get(r, c)
            if cell == EMPTY:
                s += "\033[0;107m  \033[0m"
            elif cell == APPLE:
                s += "\033[0;41m  \033[0m"
            elif cell == SNAKE:
                s += "\033[0;42m  \033[0m"
            elif cell == HEAD:
                if creature.dead:
                    s += "\033[1;101;33m[]\033[0m"
                else:
                    s += "\033[1;42;33m[]\033[0m"
        s += "\n"
    print(s)


if os.path.exists(SAVE_FP):
    creature = Creature(brain.Brain(load=SAVE_FP))
    while True:
        creature.step()
        draw(creature, pre="Score: {}".format(creature.snake.length))

        if creature.dead:
            creature = Creature(brain.Brain(load=SAVE_FP))
            time.sleep(0.25)

        time.sleep(0.02)
