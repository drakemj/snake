
from math import gamma
import sys
print (sys.path)
import pygame
import random

XSIZE, YSIZE = 400, 400

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
        self.snakeLength = 1
        self.snakeList = []
        self.foodLocation = [0, 0]
        self.x = 200
        self.y = 200
        head = [self.x, self.y]
        self.snakeList.append(head)
        self.outputFood()


    def move(self, state, gameOver):
        xspeed, yspeed = 5, 0
        if (state == 0 and self.y % 10 == 0):
            xspeed = -5
            yspeed = 0
        if (state == 1 and self.y % 10 == 0):
            xspeed = 5
            yspeed = 0
        if (state == 2 and self.x % 10 == 0):
            xspeed = 0
            yspeed = -5
        if (state == 3 and self.x % 10 == 0):
            xspeed = 0
            yspeed = 5
        self.x += xspeed * 2
        self.y += yspeed * 2

        head = [self.x, self.y]
        self.snakeList.append(head)

        for i in self.snakeList[:-1]:
            if i == head:
                gameOver = True

        if head == self.foodLocation:
            self.snakeLength += 1
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

    def outputFood(self):
        x, y = 0, 0
        isCollide = True
        while (isCollide):
            x = random.randrange(0, 40)
            y = random.randrange(0, 40)
            for i in self.snakeList:
                if x == i[0] and y == i[1]:
                    isCollide = True
                    break
                else:
                    isCollide = False
        self.foodLocation[0] = x * 10
        self.foodLocation[1] = y * 10



newSnake = Snake()

while not quitGame:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitGame = True
        if event.type == pygame.KEYDOWN:
            gameOver = False
            state = setMoveState(event, state)
    
    if not gameOver:
            
        gameOver = newSnake.move(state, gameOver)
        dis.fill(black)
        newSnake.drawSnake()

        
        pygame.display.update()
        clock.tick(5)
        
        if gameOver:
            dis.blit(gameOverText, centerRect)
            pygame.display.update()
            pygame.time.wait(1000)
            gameOver = True
            del newSnake
            newSnake = Snake()



pygame.quit()
quit()
