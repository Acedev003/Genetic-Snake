import time
import random

import curses
from   curses import wrapper as curses_wrap

MIN_SCRN_HEIGHT = 25
MIN_SCRN_WIDTH  = 80

MAX_POPULATION = 1000
FIT_POPULATION = 500
ELITE_GUYS     = 50
GEN_STEPS      = 1000000


class Snake:    
    
    def __generate_body(self,world_height,world_width,length,direction):
        headx = random.randint(length,world_width-1)
        heady = random.randint(length,world_height-1)
        
        if (direction == self.DIR_UP):
            return [(heady+i,headx)for i in range(length)]
        
        if (direction == self.DIR_DWN):
            return [(heady-i,headx)for i in range(length)]
        
        if (direction == self.DIR_LFT):
            return [(heady,headx+i)for i in range(length)]
        
        if (direction == self.DIR_RGT):
            return [(heady,headx-i)for i in range(length)]
        
    def __log(self,msg):
        file = open("log.txt",'a+')
        file.writelines([str(msg)+"\n"])
        file.close()
    
    def __init__(self,id:str,food:'Food',world_height:int,world_width:int,length:int = 3):
        self.DIR_UP  =  1
        self.DIR_RGT =  2
        self.DIR_DWN = -1
        self.DIR_LFT = -2
        
        self.limitx  = world_width
        self.limity  = world_height
        
        self.alive     = True
        self.length    = length
        self.direction = random.choice([self.DIR_DWN,
                                        self.DIR_LFT,
                                        self.DIR_RGT,
                                        self.DIR_UP])
        
        self.food      = food
        self.body      = self.__generate_body(world_height,world_width,self.length,self.direction)
        
        self.obstacle_top       = 0
        self.obstacle_dwn       = 0
        self.obstacle_lft       = 0
        self.obstacle_rgt       = 0 
        self.distance_foodx     = 0
        self.distance_foody     = 0
        self.neural_connections = [random.randint(0,8) for i in range(30)]
        
    def set_connections(self,connections):
        self.neural_connections = connections
        
    def perceive(self):
        if not self.alive:
            return
        
        heady = self.body[0][0]
        headx = self.body[0][1]
        
        self.distance_foody = heady - self.food.position[0]
        self.distance_foodx = headx - self.food.position[1]
    
        if heady-1 < 0 or (headx,heady-1) in self.body:
            self.obstacle_top = 8
        else:
            self.obstacle_top = 0
            
        if heady+1 > self.limity-1 or (headx,heady+1) in self.body:
            self.obstacle_dwn = 8
        else:
            self.obstacle_dwn = 0
            
        if headx-1 < 0 or (headx-1,heady) in self.body:
            self.obstacle_lft = 8
        else:
            self.obstacle_lft = 0
            
        if headx+1 > self.limitx-1 or (headx+1,heady) in self.body:
            self.obstacle_rgt = 8
        else:
            self.obstacle_rgt = 0
            
    def move(self):
        pass
    

class Food:
    def __init__(self,world_height,world_width,pos=None):
        self.world_height = world_height
        self.world_width  = world_width
        if pos:
            self.position = pos
        else:
            self.position = (random.randint(0,self.world_height-1),random.randint(0,self.world_width-1))
        
    def get_position(self):
        return self.position
    
    def change_position(self,predator:'Snake'):
        self.position = (random.randint(0,self.world_height-1),random.randint(0,self.world_width-1))
        
        while self.position in predator.body:
            self.position = (random.randint(0,self.world_height-1),random.randint(0,self.world_width-1))
            

def main(screen: 'curses._CursesWindow'):
    running = True
    
    maxy,maxx = screen.getmaxyx()
    
    if maxy < MIN_SCRN_HEIGHT:
        running = False
        screen.addstr(f"Screen Height less than required (min_height:{MIN_SCRN_HEIGHT}). Press any key to exit")
        screen.getkey()
    if maxx < MIN_SCRN_WIDTH:
        running = False
        screen.addstr(f"Screen Width less than required (min_width:{MIN_SCRN_WIDTH}). Press any key to exit")
        screen.getkey()
    
    screen.nodelay(True)
    curses.curs_set(0)
    
    snakes = None
    
    while running:
        foods = [Food(maxy-1,maxx-1) for i in range(MAX_POPULATION)]
        if snakes is None:
            snakes = [Snake(str(i),foods[i],maxy-1,maxx-1) for i in range(MAX_POPULATION)]
        
        for i in range(GEN_STEPS):
            for snake in snakes:
                snake.perceive()
                snake.move()
            
        
        time.sleep(0.001)

if __name__ == '__main__':
    input("Starting Snakevolution-CLI (Evolving) .... Press Enter to continue ")
    curses_wrap(main)
    print("Program has terminated")