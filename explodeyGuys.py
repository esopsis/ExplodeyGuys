from __future__ import division
from pygame.locals import *
import pygame, sys
import os
import math
import random
pygame.init()

""" explodeyGuys.py
by Eric J.Parfitt (ejparfitt@gmail.com)

A simple "game,"  You click on a circle and it explodes.  Then the other
circles come and "eat" him.

Version: 1.0 alpha
"""

WIDTH = 500
HEIGHT = 400

windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

GUY_NUM = 300
FPS = 30
clock = pygame.time.Clock()

isClick = False

sinValues = []
cosValues = []
for i in range(361):
    sinValues.append(math.sin(math.radians(i)))
    cosValues.append(math.cos(math.radians(i)))

def getDistance(point1, point2):
    return math.sqrt((y(point1) - y(point2)) ** 2 +
            (x(point1) - x(point2)) ** 2)

def getWrapDistance(point1, point2):
    xDistance = getWrapX(point1, point2)
    yDistance = getWrapY(point1, point2)
    distance = math.sqrt(yDistance ** 2 + xDistance ** 2)
    return distance

def getWrapX(point1, point2):
    xDistance = abs(x(point2) - x(point1))
    if xDistance > WIDTH / 2:
        xDistance = WIDTH - xDistance
        if x(point2) > x(point1):
            xDisplacement = -xDistance
        else:
            xDisplacement = xDistance
    else:
        if x(point1) > x(point2):
            xDisplacement = -xDistance
        else:
            xDisplacement = xDistance
    return xDisplacement

def getWrapY(point1, point2):
    yDistance = abs(y(point2) - y(point1))
    if yDistance > HEIGHT / 2:
        yDistance = HEIGHT - yDistance
        if y(point2) > y(point1):
            yDisplacement = -yDistance
        else:
            yDisplacement = yDistance
    else:
        if y(point1) > y(point2):
            yDisplacement = -yDistance
        else:
            yDisplacement = yDistance
    return yDisplacement
    
def x(point):
    return point[0]

def y(point):
    return point[1]

def getAngle(arg1, arg2 = None):
    if arg2 is None:
        return math.atan2(y(arg1), x(arg1))
    else:
        return math.atan2((y(arg2) - y(arg1)), (x(arg2) - x(arg1)))

def getWrapAngle(point1, point2):
    xDistance = getWrapX(point1, point2)
    yDistance = getWrapY(point1, point2)
    angle = math.atan2(yDistance, xDistance)
    return angle

def sin(angle):
    return sinValues[int(round(math.degrees(angle)))]

def cos(angle):
    return cosValues[int(round(math.degrees(angle)))]

class Vector:
    
    def __init__(self, arg1, arg2):
        if isinstance(arg1, tuple):
            point1 = arg1
            point2 = arg2
            self.xMag = (x(point2) - x(point1))
            self.yMag = (y(point2) - y(point1))
            self.angle = self.calcAngle()
            self.magnitude = self.calcMagnitude()
        else:
            self.angle = arg1
            self.magnitude = arg2
            self.calcComponents()
            
    def setXMag(xMag):
        self.xMag = xMag
        self.calcAngle()
        self.calcMagnitude()
        
    def getXMag(self):
        return self.xMag
    
    def setYMag(yMag):
        self.yMag = yMag
        self.calcAngle()
        self.calcMagnitude()
        
    def getYMag(self):
        return self.yMag
    
    def getAngle(self):
        return self.angle
    
    def getMagnitude(self):
        return self.magnitude
    
    def calcAngle(self):
        self.angle = getAngle((self.xMag, self.yMag))
        
    def calcMagnitude(self):
        self.magnitude = getDistance((self.xMag, self.yMag), (0,0))
        
    def calcComponents(self):
        self.xMag = self.magnitude * cos(self.angle)
        self.yMag = self.magnitude * sin(self.angle)
        
    def setAngle(self, angle):
        self.angle = angle
        self.calcComponents()
        
    def setMagnitude(self, magnitude):
        self.magnitude = magnitude
        self.calcComponents()
        
    def addVector(self, vector):
        self.xMag += vector.xMag
        self.yMag += vector.yMag
        self.calcAngle()
        self.calcMagnitude()
        
    def setVector(self, angle, magnitude):
        self.angle = angle
        self.magnitude = magnitude
        self.calcComponents()
        return self
    
    def addMagnitude(self, magnitude):
        self.setMagnitude(self.magnitude + magnitude)

class Guy:
    vector = Vector(0, 0)
    RADIUS = 6
    DIAMETER = 2 * RADIUS
    BROWNIAN_VEL_MAG = 10
    BROWNIAN_ACCEL_MAG = 1
    BROWNIAN_PROBABILITY = .1
    FORCE = 600
    FRICTION = 1
    RANDAMP = 1
    REST_SPEED = 1
    ALIVE = 0
    EXPLODING = 1
    DEAD = 2
    FLEEING = 3
    EATING = 4
    SEEKING = 5
    DEAD_TIME = 60
    EXPLODE_TIME = 15
    EXPLOSION_RADIUS = 100
    EAT_RADIUS = 40
    FOOD_RADIUS = 100
    FOOD_ACCEL = -2
    MAX_SPEED = 30
    MAX_ROAM_SPEED = 2
    MAX_ACCEL = 5
    ACCEL_SPREAD = .225
    drawXs = [0, 1, 1, 3, 1, 3, 1, 1, 0, -1, -1, -3, -1, -3, -1, -1, 0]
    drawYs = [1, 3, 1, 1, 0, -1, -1, -3, -1, -3, -1, -1, 0, 1, 1, 3, 1]
    
    def __init__(self, xCo = None, yCo = None):
        if xCo == None:
            xCo = random.randint(0,WIDTH)
        if yCo == None:
            yCo = random.randint(0, HEIGHT)
        self.xCo = xCo
        self.yCo = yCo
        self.isClicked = False
        self.status = Guy.ALIVE
        self.velocity = Vector(random.uniform(0, 2 * math.pi),
                Guy.BROWNIAN_VEL_MAG)
        self.acceleration = Vector(random.uniform(0, 2 * math.pi),
                Guy.BROWNIAN_ACCEL_MAG)
        self.explodeCount = 0
        self.deadCount = 0
        self.amountLeft = 150
        
    def clickRespond(self, mouseLoc, isClick):
        mouseX = mouseLoc[0]
        mouseY = mouseLoc[1]
        isOver = (self.xCo - Guy.RADIUS < mouseX < self.xCo + Guy.RADIUS and
                self.yCo - Guy.RADIUS < mouseY < self.yCo + Guy.RADIUS)
        if isOver and isClick:
            self.isClicked = True
            self.status = Guy.EXPLODING
            
    def getPosition(self):
        return (self.xCo, self.yCo)
    
    def move(self):
        self.xCo += self.velocity.getXMag()
        self.yCo += self.velocity.getYMag()
        
    def moveRand(self):
        self.xCo += random.randint(-Guy.RANDAMP, Guy.RANDAMP)
        self.yCo += random.randint(-Guy.RANDAMP, Guy.RANDAMP)
        
    def moveBrownian(self):
        magnitude = Guy.ACCEL_SPREAD
        while(magnitude < Guy.MAX_ACCEL):
            if random.random() < .5:
                magnitude += Guy.ACCEL_SPREAD
            else:
                break
        if random.random() < Guy.BROWNIAN_PROBABILITY:
            self.acceleration.setVector(random.uniform(0, 2 * math.pi),
                    magnitude)
            
    def accelRandom(self):
        self.acceleration.setVector(random.uniform(0, 2 * math.pi),
                    random.uniform(0, Guy.MAX_ACCEL))
        
    def flee(self, guy):
        self.status = Guy.FLEEING
        angle = getWrapAngle(guy.getPosition(), self.getPosition())
        magnitude = Guy.FORCE / getWrapDistance(self.getPosition(),
                guy.getPosition())
        self.velocity.addVector(Guy.vector.setVector(angle, magnitude))
        
    def nearestGuy(self, guys):
        distance = WIDTH + HEIGHT + 1
        for guy in guys:
            newDistance = getWrapDistance(self.getPosition(), guy.getPosition())
            if newDistance < distance:
                distance = newDistance
                nearestGuy = guy
        return (nearestGuy, distance)
    
    def applyFriction(self):
        magnitude = self.velocity.getMagnitude()
        if -Guy.FRICTION < magnitude < Guy.FRICTION:
            self.velocity.setMagnitude(0)
        elif 0 < magnitude:
            self.velocity.addMagnitude(-Guy.FRICTION)
        elif magnitude < 0:
            self.velocity.addMagnitude(Guy.FRICTION)
            
    def accelerate(self):
        self.velocity.addVector(self.acceleration)
        
    def edgeWrap(self):
        if self.xCo < 0 or self.xCo > WIDTH:
            self.xCo = self.xCo % WIDTH
        if self.yCo < 0 or self.yCo > HEIGHT:
            self.yCo = self.yCo % HEIGHT
            
    def draw(self):
        xDraw = int(round(self.xCo))
        yDraw = int(round(self.yCo))
        if not self.status == Guy.EXPLODING:
            pygame.draw.circle(windowSurface, BLACK,
                    [xDraw, yDraw], Guy.RADIUS, 1)
            if self.status == Guy.DEAD:
                pygame.draw.line(windowSurface, BLACK,
                    (xDraw - .6 * Guy.RADIUS,
                    yDraw - .6 * Guy.RADIUS), (xDraw + .6 * Guy.RADIUS,
                    yDraw + .6 * Guy.RADIUS))
                pygame.draw.line(windowSurface, BLACK,
                    (xDraw - .6 * Guy.RADIUS,
                    yDraw + .6 * Guy.RADIUS), (xDraw + .6 * Guy.RADIUS,
                    yDraw - .6 * Guy.RADIUS))
        else:
            for i in range(len(Guy.drawXs) - 1):
                pygame.draw.lines(windowSurface, BLACK, False,
                        [(xDraw + Guy.drawXs[i] * 1.3 / 3 * Guy.RADIUS,
                        yDraw + Guy.drawYs[i] * 1.3 / 3 * Guy.RADIUS),
                        (xDraw + Guy.drawXs[i + 1] * 1.3 / 3 * Guy.RADIUS,
                        yDraw + Guy.drawYs[i + 1]  * 1.3 / 3 * Guy.RADIUS)])    
    
def draw(myObjects):
    windowSurface.fill(WHITE)
    for myObject in myObjects:
        myObject.draw()
    pygame.display.flip()   

def update(guys, deadGuys, mouseLoc, isClick):
    for guy in guys:
        guy.edgeWrap()
        guyMagnitude = guy.velocity.getMagnitude()
        if guy.velocity.getMagnitude() > Guy.MAX_SPEED:
            if guy.velocity.getMagnitude() > 0:
                guy.velocity.setMagnitude(Guy.MAX_SPEED)
            else:
                guy.velocity.setMagnitude(-Guy.MAX_SPEED)
        if (guy.status == Guy.ALIVE or guy.status == Guy.FLEEING or
                guy.status == Guy.EATING or guy.status == Guy.SEEKING):
            guy.clickRespond(mouseLoc, isClick)
            if guy.isClicked:
                for guy2 in guys:
                    if ((guy2.status == Guy.ALIVE or
                            guy2.status == Guy.FLEEING or
                            guy2.status == Guy.EATING or
                             guy2.status == Guy.SEEKING) and
                            getWrapDistance(guy.getPosition(),
                            guy2.getPosition()) < Guy.EXPLOSION_RADIUS):
                        guy2.flee(guy)
                deadGuys.append(guy)
                guy.isClicked = False
                break
            else:
                if len(deadGuys) > 0:
                    nearestGuyStats = guy.nearestGuy(deadGuys)
                    nearestGuy = nearestGuyStats[0]
                    distance = nearestGuyStats[1]
                    if distance < Guy.FOOD_RADIUS:
                        if distance < Guy.RADIUS:
                            nearestGuy.amountLeft -= 1
                            if nearestGuy.amountLeft == 0:
                                guys.remove(nearestGuy)
                                deadGuys.remove(nearestGuy)
                        if distance > Guy.EAT_RADIUS:
                            guy.status = Guy.SEEKING
                        guy.velocity.addVector(Guy.vector.setVector(getWrapAngle(
                                nearestGuy.getPosition(),
                                guy.getPosition()), Guy.FOOD_ACCEL))
                        isRight = (x(nearestGuy.getPosition()) <
                                x(guy.getPosition()))
                        isMovingRight = guy.velocity.getXMag() > 0
                        isMovingLeft = guy.velocity.getXMag() < 0
                        isDown = (0 < y(guy.getPosition()) -
                                y(nearestGuy.getPosition()))
                        isMovingUp = guy.velocity.yMag < 0
                        isTowardsGuy = ((isRight and isMovingLeft) or
                                (not isRight and
                                isMovingRight) or (isDown and isMovingUp) or
                                (not isDown and not isMovingUp))                      
                        amplitude = WIDTH + HEIGHT + 1
                        if not isTowardsGuy:
                            if (abs(guy.velocity.getMagnitude()) <
                                    abs(Guy.FOOD_ACCEL)):
                                amplitude = getDistance(guy.getPosition(),
                                        nearestGuy.getPosition())
                        if amplitude < Guy.EAT_RADIUS:
                            guy.status = Guy.EATING
                    elif guy.status == Guy.EATING or guy.status == Guy.SEEKING:
                        guy.status = Guy.FLEEING
                elif guy.status == Guy.EATING or guy.status == Guy.SEEKING:
                    guy.status = Guy.FLEEING
                    guy.isFoodPass = False
                if (guy.status == Guy.FLEEING or guy.status == Guy.EATING or
                        guy.status == Guy.SEEKING or guy.status == Guy.ALIVE):
                    if (guy.status == Guy.FLEEING and
                            abs(guy.velocity.getMagnitude()) < Guy.REST_SPEED):
                        guy.status = Guy.ALIVE
                        guy.accelRandom()
                    if guy.status == Guy.ALIVE:
                        if guy.velocity.getMagnitude() > Guy.MAX_ROAM_SPEED:
                            guy.velocity.setMagnitude(Guy.MAX_ROAM_SPEED)
                        guy.moveBrownian()
                        guy.accelerate()
                    guy.move()
                
        elif guy.status == Guy.EXPLODING:
            guy.explodeCount += 1
            if guy.explodeCount == Guy.EXPLODE_TIME:
                guy.status = Guy.DEAD
        if (guy.status == Guy.FLEEING or guy.status == guy.SEEKING):
            guy.applyFriction()
    clock.tick(FPS)

deadGuys = []
guys = []
for i in range(GUY_NUM):
    guys.append(Guy())
    
windowSurface.fill(WHITE)

while(True):
    isClick = False
    draw(guys)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            isClick = True
    mouseLoc = pygame.mouse.get_pos()
    update(guys, deadGuys, mouseLoc, isClick)
