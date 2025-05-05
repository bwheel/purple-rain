import sys, math, random

from dataclasses import dataclass as component
from enum import Enum
from typing import Tuple

import pygame
import esper

@component
class Constants:
    BACKGROUND_COLOR = (0, 0, 0)
    RAIN_DROP_COLOR = (128, 0, 128)
    RAIN_DROP_WIDTH = 5
    RAIN_DROP_HEIGHT = 15
    RAIN_DROP_SPEED = 700

@component
class Position:
    x: float = 0.0
    y: float = 0.0

@component
class Velocity:
    dx: float = 0.0
    dy: float = 0.0

@component
class Raindrop:
    color: Tuple[int, int, int]

@component
class Background:
    color: Tuple[int, int, int]

class MovementProcessor(esper.Processor):

    def process(self, dt):
        for _, (vel, pos) in esper.get_components(Velocity, Position):
            pos.x += vel.dx * dt
            pos.y += vel.dy * dt

class RenderProcessor(esper.Processor):

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen

    def process(self, _):
        
        # clear display buffer with bckground
        _, background = esper.get_component(Background)[0]
        self.screen.fill(background.color)

        # apply all the raindrops to display buffer
        for _, (drop, pos) in esper.get_components(Raindrop, Position):
            #r = pygame.Rect()
            #pygame.draw.rect(self.screen, drop.color, r)
            self.screen.fill(drop.color, (pos.x, pos.y, Constants.RAIN_DROP_WIDTH, Constants.RAIN_DROP_HEIGHT))
        
        # apply display-buffer to screen
        pygame.display.flip()

class RaindropSpawnProcessor(esper.Processor):

    def __init__(self, screen_width: float):
        super().__init__()
        self.total_cols = math.floor(screen_width / Constants.RAIN_DROP_WIDTH)
    
    def process(self, _):
        should_generate = random.randint(0, 1) == 1
        if should_generate:
            col_index = random.randint(1, self.total_cols)
            x = float(col_index) * Constants.RAIN_DROP_WIDTH
            y = 0
            if not any([ p.x == x for (_, (_, p)) in esper.get_components(Raindrop, Position)]):
                init_rain_drop(x, y)

class RaindropDestroyProcessor(esper.Processor):

    def __init__(self, screen_dimentions: Tuple[float, float]):
        super().__init__()
        (self.screen_width, self.screen_height) = screen_dimentions

    def process(self, _):
        [ esper.delete_entity(e) 
            for (e,  (_, p)) in esper.get_components(Raindrop, Position)
            if p.y > self.screen_height  or p.y < 0 or p.x < 0 or p.x > self.screen_width]
        

def init_background(screen: pygame.Surface):
    # initialize background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(Constants.BACKGROUND_COLOR)
    esper.create_entity(Background(color=Constants.BACKGROUND_COLOR))

def init_rain_drop( x: int, y: int):
    drop_entity = esper.create_entity()
    esper.add_component(drop_entity, Position(x=x, y=y))
    esper.add_component(drop_entity, Velocity(dx=0, dy=Constants.RAIN_DROP_SPEED))
    esper.add_component(drop_entity, Raindrop(color=Constants.RAIN_DROP_COLOR))

def main():
    # initialize game
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((1280, 480), pygame.SCALED)
    pygame.display.set_caption("Purple Rain")

    init_background(screen)

    # create processors
    esper.add_processor(MovementProcessor())
    esper.add_processor(RenderProcessor(screen))
    esper.add_processor(RaindropSpawnProcessor(screen_width=1280))
    esper.add_processor(RaindropDestroyProcessor((1280, 480)))

    # initialize game loop
    clock = pygame.Clock()
    running = True
    while running:

        # handle inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                break
        dt = clock.tick(60) / 1000.0

        esper.process(dt)

    pygame.quit()



if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as ex:
        print(str(ex))
        sys.exit(1)