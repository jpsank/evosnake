import numpy as np
import random, math
from config import *
import json


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def tanh(x):
    return np.tanh(x)


def softmax(A):
    expA = np.exp(A)
    return expA / expA.sum()


def relu(x):
    return np.maximum(x, 0)


def normalize(x):
    return x / np.linalg.norm(x)


def dist(pos1, pos2):
    return math.sqrt(pow(pos1[0]-pos2[0], 2) + pow(pos1[1]-pos2[1], 2))


def random_weight(*shape):
    return np.random.rand(*shape)*2-1

# INPUTS
# - length of snake
# - current direction of snake
# - identity of item directly in front of snake's head ("smell")
# - delta x from head to apple
# - delta y from head to apple


class Brain:
    def __init__(self, load=None):
        self.layers = []
        if load is not None:
            self.load(load)
        else:
            for i in range(len(NODES)-1):
                self.layers.append(random_weight(NODES[i], NODES[i + 1]))

        self.inputs = np.zeros((NUM_INPUTS, 1))

    def set_inputs(self, snake):
        directions = [UP, np.add(UP, RIGHT),
                      RIGHT, np.add(RIGHT, DOWN),
                      DOWN, np.add(DOWN, LEFT),
                      LEFT, np.add(LEFT, UP)]

        vision = []
        for d in directions:
            see = snake.look_in_direction(d)
            v = 0
            if APPLE in see and (SNAKE not in see or see[APPLE] < see[SNAKE]):
                v = 1
            else:
                if SNAKE in see:
                    v = -1/see[SNAKE]
                else:
                    v = -1/see[WALL]
            vision.append(v)
            # vision += [1/see[t] if t in see else 0 for t in tiles]

        self.inputs = np.array([vision])

    def predict(self):
        feedforward = self.inputs
        for layer in self.layers:
            feedforward = relu(np.dot(feedforward, layer))
        return feedforward[0]

    def crossover(self, partner):
        child = Brain()

        for i, layer in enumerate(self.layers):
            layer = np.copy(layer)
            for r, row in enumerate(layer):
                for c, col in enumerate(row):
                    if random.random() < 0.5:
                        layer[r, c] = partner.layers[i][r, c]
            child.layers[i] = layer

        return child

    def mutated(self, m=0.05):
        child = Brain()

        for i, layer in enumerate(self.layers):
            layer = np.copy(layer)
            for r, row in enumerate(layer):
                for c, col in enumerate(row):
                    if random.random() < m:
                        layer[r, c] = random_weight(1)[0]
            child.layers[i] = layer

        return child

    def save(self, fp):
        np.save(fp, self.layers)

    def load(self, fp):
        self.layers = np.load(fp, allow_pickle=True)



