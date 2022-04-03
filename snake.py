
from math import gamma
import sys
print (sys.path)
import os
import pygame
import random
import math
import neat
import copy

XSIZE, YSIZE = 200, 200

pygame.init()
dis = pygame.display.set_mode((XSIZE, YSIZE))
pygame.display.update()
pygame.display.set_caption("Snake Game")

def setMoveState(event, x):
    if event.key == pygame.K_LEFT:
        state = 0
    elif event.key == pygame.K_RIGHT:
        state = 1
    elif event.key == pygame.K_UP:
        state = 2
    elif event.key == pygame.K_DOWN:
        state = 3
    else:
        state = x
    return state


green = (0, 255, 0)
red = (255, 0, 0)
purple = (128, 0, 128)
black = (0, 0, 0)
white = (255, 255, 255)

xspeed = 5
yspeed = 0
px = 200
py = 200

quitGame = False
gameOver = False


font = pygame.font.Font('freesansbold.ttf', 20)
gameOverText = font.render("Game Over!", black, purple)
centerRect = gameOverText.get_rect()
centerRect.center = (XSIZE/2, YSIZE/2)

state = 0

clock = pygame.time.Clock()
state = 0

class Snake:
    def __init__(self):
        self.snakeLength = 2
        self.snakeList = []
        self.foodLocation = [0, 0]
        self.x = XSIZE/2
        self.y = YSIZE/2
        self.counter = 0
        self.head = [self.x, self.y]
        self.snakeList.append(self.head)
        self.lastFood = 0
        self.outputFood()


    def move(self, gameOver, net):
        gameOver = False

        inputs = self.distances()
        output = net.activate(inputs)
        state = output.index(max(output))

        xspeed, yspeed = 5, 0
        if (state == 0):
            xspeed = -5
            yspeed = 0
        if (state == 1):
            xspeed = 5
            yspeed = 0
        if (state == 2):
            xspeed = 0
            yspeed = -5
        if (state == 3):
            xspeed = 0
            yspeed = 5
        self.x += xspeed * 2
        self.y += yspeed * 2

        self.head = [self.x, self.y]
        self.snakeList.append(self.head)
        self.counter += 1
        self.lastFood += 1

        for i in self.snakeList[:-1]:
            if i == self.head:
                gameOver = True

        if self.head == self.foodLocation:
            self.snakeLength += 1
            self.lastFood = 0
            self.outputFood()

        if len(self.snakeList) > self.snakeLength:
            del self.snakeList[0]

        if (self.x < 0 or self.x >= XSIZE) or (self.y < 0 or self.y >= YSIZE):
            gameOver = True

        return gameOver



    def drawSnake(self):
        for i in self.snakeList:
            pygame.draw.rect(dis, green, [i[0], i[1], 9, 9])
        pygame.draw.rect(dis, red, [self.foodLocation[0], self.foodLocation[1], 9, 9])
        pygame.draw.line(dis, purple, self.foodLocation, self.head)

    def outputFood(self):
        x, y = 0, 0
        isCollide = True
        while (isCollide):
            x = random.randrange(0, XSIZE/10)
            y = random.randrange(0, YSIZE/10)
            for i in self.snakeList:
                if x == i[0] and y == i[1]:
                    isCollide = True
                    break
                else:
                    isCollide = False
        self.foodLocation[0] = x * 10
        self.foodLocation[1] = y * 10

    def distances(self):
        out = []

        d = copy.deepcopy(self.head)
        c = copy.deepcopy(d)
        b = copy.deepcopy(d)

        for i in range(8):
            d = copy.deepcopy(self.head)
            c = copy.deepcopy(d)
            b = copy.deepcopy(d)
            isBlock = False
            isFood = False
            while (d[0] >= 0 and d[0] <= XSIZE) and (d[1] >= 0 and d[1] <= YSIZE):
                if (i == 0):
                    d[0] += 10
                elif (i == 1):
                    d[0] -= 10
                elif (i == 2):
                    d[1] += 10
                elif (i == 3):
                    d[1] -= 10
                elif (i == 4):
                    d[0] -= 10
                    d[1] -= 10
                elif (i == 5):
                    d[0] -= 10
                    d[1] += 10
                elif (i == 6):
                    d[0] += 10
                    d[1] += 10
                elif (i == 7):
                    d[0] += 10
                    d[1] -= 10
                for blocks in self.snakeList:
                    if blocks == d:
                        c = copy.deepcopy(d)
                        isBlock = True
                        break
                if d == self.foodLocation:
                    b = copy.deepcopy(d)
                    isFood = True
            out.append(math.dist(self.head, d))
            if not isBlock:
                c = d
            if not isFood:
                b = d
            out.append(math.dist(self.head, c))
            out.append(math.dist(self.head, b))

        return out
    
    def getCount(self):
        return self.counter

    def getLength(self):
        return self.snakeLength

    def getLastFood(self):
        return self.lastFood



gen = 0
tdelay = 40

def eval_genomes(genomes, config):
    global gen
    global tdelay
    global clock

    gen += 1

    nets = []
    ge = []
    snakes = []

    for genome_id, genome in genomes:
        net = neat.nn.feed_forward.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        snakes.append(Snake())
        genome.fitness = 0
        ge.append(genome)

    gameOver = False

    while len(snakes) > 0:
        gameOver = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    tdelay -= 5
                if event.key == pygame.K_RIGHT:
                    tdelay += 5

        j = 0
        while j < len(snakes):
            gameOver = snakes[j].move(gameOver, nets[j])
            if (snakes[j].getLastFood() > 100):
                gameOver = True

            if gameOver:
                length = snakes[j].getLength() - 1
                lifetime = snakes[j].getCount()
                ge[j].fitness = length * 50 + lifetime
                snakes.pop(j)
                nets.pop(j)
                ge.pop(j)
            else:
                j += 1

       

        dis.fill(black)
        if len(snakes) > 0:
            snakes[0].drawSnake()

        
        pygame.display.update()
        clock.tick(tdelay)
        

        


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 700)

    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)

