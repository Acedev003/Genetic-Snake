import math
import time
import random
import pickle

from   world  import Snake,Food

import curses
from   curses import wrapper as curses_wrap

MIN_SCRN_HEIGHT = 25
MIN_SCRN_WIDTH  = 80

MAX_POPULATION  = 10000
FIT_POPULATION  = 5000
ELITE_GUYS      = 2000
GEN_STEPS       = 2000
MUTATION_PRBLTY = 0.50

MAX_CONN_WGHT   = 32
CONNECTIONS_CNT = 30

CPU_POOL_SIZE    = 4

SNAKE_LIFE = 500
START_SIZE = 3

FOOD_CHAR  = "@"
SNAKE_CHAR = "#"

def main(screen: 'curses._CursesWindow'):
    
    snake = None
    with open("best_snake.snk",'rb') as file:
        snake = pickle.load(file)    
    
    snake.reset_body()
    food = snake.food
    
    screen_height,screen_width = screen.getmaxyx()
    
    snake.limity = screen_height - 1
    snake.limitx = screen_width - 1
    
    food.world_height = screen_height - 1
    food.world_width  = screen_width - 1
    food.reset_position()
    
    screen.nodelay(True)
    curses.curs_set(0)
    
    while snake.alive:
        screen.clear()
        key = screen.getch()
        if key == ord('q') or key == ord('Q'):
            snake.alive=False
            
        food.draw(screen)
        snake.perceive()
        snake.move()  
        snake.draw(screen)   
        screen.refresh()
        time.sleep(0.05)
        
        
if __name__ == '__main__':
    input("Starting Snakevolution-CLI (Evolving-Test) .... Press Enter to continue ")
    
    # Wrapper for curses intialization and auto de-initialize
    curses_wrap(main)
    
    print("Program has terminated")
