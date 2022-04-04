
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



green = (0, 255, 0)
red = (255, 0, 0)
purple = (128, 0, 128)
black = (0, 0, 0)

clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        self.snakeLength = 2
        self.snakeList = []         #list to keep track of the "blocks" currently in snake object
        self.foodLocation = [0, 0]
        self.counter = 0            #total lifetime of snake
        self.head = [random.randrange(0, XSIZE/10) * 10, random.randrange(YSIZE/10) * 10]
        self.snakeList.append(copy.deepcopy(self.head))
        self.lastFood = 0           #incremented every time the snakes moves, resets when food is collected
        self.state = 0              #keeps track of which direction the snake was moving previously (don't think this is necessary, but put it in so that 
                                    #the direction only changes when the activation function is above some value.
        self.outputFood()


    def move(self, net, ge):
        gameOver = False                #gameOver flag, default false.

        inputs = self.distances()       #array of 24 inputs, calculates the distance to the walls, food, and its own body in pixels (not grid). 
        output = net.activate(inputs)   
        
        for i, val in enumerate(output):
            if val > 0.5:
                self.state = i


        xspeed, yspeed = 10, 0
        if (self.state == 0):           #change the direction depending on the state, which the activate function changes
            xspeed = -10
            yspeed = 0
        if (self.state == 1):
            xspeed = 10
            yspeed = 0
        if (self.state == 2):
            xspeed = 0
            yspeed = -10
        if (self.state == 3):
            xspeed = 0
            yspeed = 10

        self.head[0] += xspeed
        self.head[1] += yspeed

        self.snakeList.append(copy.deepcopy(self.head))
        self.counter += 1
        self.lastFood += 1

        for i in self.snakeList[:-1]:               #snake collides with itself (last element is head)
            if i == self.head:
                gameOver = True
                self.counter -= 20

        if self.head == self.foodLocation:          #upon collecting food
            self.snakeLength += 1
            ge.fitness += 2
            self.lastFood = 0
            self.outputFood()

        if len(self.snakeList) > self.snakeLength:  #delete the tail if the current length is larger than the object's score variable
            del self.snakeList[0]

        if (self.head[0] < 0 or self.head[0] >= XSIZE) or (self.head[1] < 0 or self.head[1] >= YSIZE): #bounds check
            gameOver = True
            self.counter -= 20

        if self.lastFood > 100:                     #"hunger", preventing snake from looping and gaining fitness
            gameOver = True
            self.counter -= 50

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
            x = random.randrange(0, XSIZE/10)           #randomly generate food location until it is not inside current snake
            y = random.randrange(0, YSIZE/10)
            for i in self.snakeList:
                if x * 10 == i[0] and y * 10 == i[1]:
                    isCollide = True
                    break
                else:
                    isCollide = False
        self.foodLocation[0] = x * 10
        self.foodLocation[1] = y * 10

    def distances(self):                                
        out = [
            self.foodLocation[0] > self.head[0],
            self.foodLocation[0] < self.head[0],
            self.foodLocation[1] > self.head[1],
            self.foodLocation[1] < self.head[1],
            self.state == 0,
            self.state == 1,
            self.state == 2,
            self.state == 3,
            self.isDeath(0),
            self.isDeath(1),
            self.isDeath(2),
            self.isDeath(3)
        ]
       
        

        return out

    def isDeath(self, s):
        newPos = copy.deepcopy(self.head)
        if s == 0:
            newPos[0] -= 10
            if newPos[0] < 0 or newPos in self.snakeList:
                return True
        elif s == 1:
            newPos[0] += 10
            if newPos[0] >= XSIZE or newPos in self.snakeList:
                return True
        elif s == 2:
            newPos[1] -= 10
            if newPos[1] < 0 or newPos in self.snakeList:
                return True
        elif s == 3:
            newPos[1] += 10
            if newPos[1] >= YSIZE or newPos in self.snakeList:
                return True
        return False

    
    def getCount(self):                             #various accessor functions used for testing different fitness functions.
        return self.counter

    def getLength(self):
        return self.snakeLength

    def getLastFood(self):
        return self.lastFood

    def getHead(self):
        return self.head

    def getFoodLocation(self):
        return self.foodLocation



gen = 0
tdelay = 40

def eval_genomes(genomes, config):
    global gen
    global tdelay
    global clock

    gen += 1

    nets = []           #three arrays to hold the networks, genomes, and snakes themselves.
    ge = []
    snakes = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        snakes.append(Snake())
        ge.append(genome)

    gameOver = False

    while len(snakes) > 0:
        gameOver = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:                       
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:                    #you can use arrow keys to slow down or speed up the simulation speed.
                if event.key == pygame.K_LEFT:
                    tdelay -= 5
                if event.key == pygame.K_RIGHT:
                    tdelay += 5

        j = 0
        while j < len(snakes):                                  #iterate through the snake list one time
            gameOver = snakes[j].move(nets[j], ge[j])           #move the snake and return gameOver

            if gameOver:                                        #if game over, calculate fitness and pop all lists. don't increment j if popping
                length = snakes[j].getLength() - 2
                lifetime = snakes[j].getCount()
                ge[j].fitness += 0.1 * lifetime
                snakes.pop(j)
                nets.pop(j)
                ge.pop(j)
            else:
                j += 1

       

        dis.fill(black)
        if len(snakes) > 0:                                     #draw the first snake (could also move this to top of while loop to avoid extra line)
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

