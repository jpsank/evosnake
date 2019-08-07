import os, time
from matplotlib import pyplot
import numpy as np
import curses

from config import *
import main
import brain
import snake

SCALE_X, SCALE_Y = 10, 5
RAD = 1


def draw_brain(bran):
    pyplot.figure()
    for l, layer in enumerate(bran.layers):
        for n, neuron in enumerate(layer):
            x, y = l*SCALE_X, n*SCALE_Y
            circle = pyplot.Circle((x, y), radius=RAD, fill=False)
            pyplot.gca().add_patch(circle)
            for w, weight in enumerate(neuron):
                x2, y2 = (l+1)*SCALE_X, w*SCALE_Y
                circle = pyplot.Circle((x2, y2), radius=RAD, fill=False)
                pyplot.gca().add_patch(circle)

                line = pyplot.Line2D((x, x2),
                                     (y, y2),
                                     linewidth=abs(weight),
                                     color="r" if weight < 0 else "g")
                pyplot.gca().add_line(line)
    pyplot.axis('scaled')
    pyplot.axis('off')
    pyplot.title('Neural Network architecture', fontsize=15)
    pyplot.show()


if os.path.exists(SAVE_FP):
    print("Loading brain from save file...")
    grid = snake.Grid()
    creatures = [main.Creature(brain.Brain(load=SAVE_FP), grid) for c in range(2)]

    while True:
        for i,c in enumerate(creatures):
            if not c.dead:
                c.step()
            else:
                c.snake.clear()
                creatures[i] = main.Creature(brain.Brain(load=SAVE_FP), grid)

        main.draw(grid)

        time.sleep(0.06)