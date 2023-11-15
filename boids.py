#This code is a translation of a JavaScript code used for simulating boids. 
#The ultimate goal is to execute this Python code in RVIZ to enable its application in drone simulations.

import pygame
import math
import random

# Initial screen size. Change if you want to see other screen resolutions
width = 1920
height = 1080

numBoids = 12 # Boids number that appear in the simulation
visualRange = 75 # Range that set the grouping. 75 is the default (The higher the number, the closer they're.)

boids = [] # void vector

# Function that randomly starts the boids
def initBoids(): 
    for _ in range(numBoids):
        boid = {
            'x': random.uniform(0, width),
            'y': random.uniform(0, height),
            'dx': random.uniform(-5, 5),
            'dy': random.uniform(-5, 5),
            'history': []
        }
        boids.append(boid)

# Trigonometric ratio for distance
def distance(boid1, boid2):
    return math.sqrt((boid1['x'] - boid2['x']) ** 2 + (boid1['y'] - boid2['y']) ** 2)

def nClosestBoids(boid, n):
    # Do a copy
    sorted_boids = boids.copy()
    # Sort copy by distance from 'boid'
    sorted_boids.sort(key=lambda other_boid: distance(boid, other_boid))
    # Return the nearest 'n'
    return sorted_boids[1:n + 1]

# Get the window resolution
def sizeCanvas():
    global width, height
    width, height = pygame.display.get_surface().get_size()

# Sets the margin for collision and reverse the direction when boid collide
def keepWithinBounds(boid):
    margin = 200
    turnFactor = 1

    if boid['x'] < margin:
        boid['dx'] += turnFactor
    if boid['x'] > width - margin:
        boid['dx'] -= turnFactor
    if boid['y'] < margin:
        boid['dy'] += turnFactor
    if boid['y'] > height - margin:
        boid['dy'] -= turnFactor
 
# Find the center of mass of the other boids and adjust velocity slightly to point towards the center of mass
def flyTowardsCenter(boid):
    centeringFactor = 0.05 # Adjust velocity by %

    centerX = 0
    centerY = 0
    numNeighbors = 0

    for otherBoid in boids:
        if distance(boid, otherBoid) < visualRange:
            centerX += otherBoid['x']
            centerY += otherBoid['y']
            numNeighbors += 1

    if numNeighbors:
        centerX = centerX / numNeighbors
        centerY = centerY / numNeighbors

        boid['dx'] += (centerX - boid['x']) * centeringFactor
        boid['dy'] += (centerY - boid['y']) * centeringFactor


# Move away from other boids that are too close to avoid colliding
def avoidOthers(boid):
    minDistance = 20 # The distance to stay away from other boids
    avoidFactor = 0.05 # Adjust velocity by %
    moveX = 0
    moveY = 0

    for otherBoid in boids:
        if otherBoid != boid:
            if distance(boid, otherBoid) < minDistance:
                moveX += boid['x'] - otherBoid['x']
                moveY += boid['y'] - otherBoid['y']

    boid['dx'] += moveX * avoidFactor
    boid['dy'] += moveY * avoidFactor

# Find the average velocity (speed and direction) of the other boids and adjust velocity slightly to match.
def matchVelocity(boid):
    matchingFactor = 0.05 # Adjust by % of average velocity

    avgDX = 0
    avgDY = 0
    numNeighbors = 0

    for otherBoid in boids:
        if distance(boid, otherBoid) < visualRange:
            avgDX += otherBoid['dx']
            avgDY += otherBoid['dy']
            numNeighbors += 1

    if numNeighbors:
        avgDX = avgDX / numNeighbors
        avgDY = avgDY / numNeighbors

        boid['dx'] += (avgDX - boid['dx']) * matchingFactor
        boid['dy'] += (avgDY - boid['dy']) * matchingFactor

# Speed will naturally vary in flocking behavior, but real animals can't go arbitrarily fast.
def limitSpeed(boid):
    speedLimit = 15

    speed = math.sqrt(boid['dx'] ** 2 + boid['dy'] ** 2)
    if speed > speedLimit:
        boid['dx'] = (boid['dx'] / speed) * speedLimit
        boid['dy'] = (boid['dy'] / speed) * speedLimit

DRAW_TRAIL = False

def drawBoid(screen, boid):
    angle = math.atan2(boid['dy'], boid['dx'])
    rotated_surface = pygame.transform.rotate(boid_image, math.degrees(angle))
    rotated_rect = rotated_surface.get_rect(center=(boid['x'], boid['y']))
    screen.blit(rotated_surface, rotated_rect)

    if DRAW_TRAIL:
        for i in range(len(boid['history']) - 1):
            pygame.draw.line(screen, (85, 140, 244, 102), boid['history'][i], boid['history'][i + 1])

def main():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Boids Simulation Algorithm")
    
    global boid_image
    boid_image = pygame.Surface((30, 10), pygame.SRCALPHA)
    pygame.draw.polygon(boid_image, (85, 140, 244), [(0, 0), (30, 5), (30, -5)])
    
    sizeCanvas()

    # Randomly distribute the boids to start
    initBoids()
    
    clock = pygame.time.Clock()
    running = True

    # Main animation loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Update each boid
        for boid in boids:
            # Update the velocities according to each rule
            flyTowardsCenter(boid)
            avoidOthers(boid)
            matchVelocity(boid)
            limitSpeed(boid)
            keepWithinBounds(boid)

            # Update the position based on the current velocity
            boid['x'] += boid['dx']
            boid['y'] += boid['dy']
            boid['history'].append((int(boid['x']), int(boid['y'])))
            boid['history'] = boid['history'][-50:]
        
        #Clear the canvas and redraw all the boids in their current positions
        screen.fill((0, 0, 0))
        for boid in boids:
            drawBoid(screen, boid)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()