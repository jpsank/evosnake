import os, time
import numpy as np

import snake
import main
from config import *


G_WIDTH = 50
G_HEIGHT = 50
POPULATION = 20

grid = snake.Grid(G_WIDTH, G_HEIGHT)
for _ in range(POPULATION-1):
    grid.set_apple()
if os.path.exists(SAVE_FP):
    creatures = [main.Creature(main.brain.Brain(load=SAVE_FP), grid) for _ in range(POPULATION)]
else:
    creatures = [main.Creature(main.brain.Brain(), grid) for _ in range(POPULATION)]

high_score = 0
idx = 0
while True:
    for c in creatures:
        if not c.dead:
            c.step(False)
    ranked = sorted(creatures, key=lambda c: c.snake.length)
    best = ranked[-1]
    second_best = ranked[-2]

    for c in creatures:
        if c.dead:
            c.snake.clear()
            creatures.remove(c)
        else:
            if c.snake.hunger == 0 and c.snake.length > 1:
                creatures.append(main.Creature(best.brain.crossover(c.brain).mutated(), grid))

    if len(creatures) < POPULATION:
        creatures.append(main.Creature(best.brain.crossover(second_best.brain).mutated(), grid))

    if best.snake.length > high_score:
        high_score = best.snake.length
        print("Saving, high score {}...".format(high_score))
        best.brain.save(SAVE_FP)

    print(", ".join("score: {}".format(c.snake.length) for c in ranked))
    main.draw(grid)
    time.sleep(0.04)
    idx += 1

