import math
import time
import random

from multiprocessing import Pool

import curses
from   curses import wrapper as curses_wrap

MIN_SCRN_HEIGHT = 25
MIN_SCRN_WIDTH  = 80

MAX_POPULATION  = 1000
FIT_POPULATION  = 500
ELITE_GUYS      = 50
GEN_STEPS       = 1000
MUTATION_PRBLTY = 0.2

MAX_CONN_WGHT   = 15

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
        
    def __sigmoid(self,x):
        self.__log(x)
        try:
            return 1/(1+math.exp(-x))
        except(OverflowError):
            return float('inf')
        
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
        
        self.alive      = True
        self.length     = length
        self.step_count = 0
        self.direction  = random.choice([self.DIR_DWN,
                                         self.DIR_LFT,
                                         self.DIR_RGT,
                                         self.DIR_UP])
        
        self.id        = id
        self.food      = food
        self.body      = self.__generate_body(world_height,world_width,self.length,self.direction)
        
        self.obstacle_top       = 0
        self.obstacle_dwn       = 0
        self.obstacle_lft       = 0
        self.obstacle_rgt       = 0 
        self.distance_foodx     = 0
        self.distance_foody     = 0
        self.neural_connections = [random.randint(0,MAX_CONN_WGHT) for _ in range(30)]
        
    def __len__(self):
        return len(self.body)
        
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
            self.obstacle_top = MAX_CONN_WGHT
        else:
            self.obstacle_top = 0
            
        if heady+1 > self.limity-1 or (headx,heady+1) in self.body:
            self.obstacle_dwn = MAX_CONN_WGHT
        else:
            self.obstacle_dwn = 0
            
        if headx-1 < 0 or (headx-1,heady) in self.body:
            self.obstacle_lft = MAX_CONN_WGHT
        else:
            self.obstacle_lft = 0
            
        if headx+1 > self.limitx-1 or (headx+1,heady) in self.body:
            self.obstacle_rgt = MAX_CONN_WGHT
        else:
            self.obstacle_rgt = 0
            
    def move(self):
        self.__log(f"Move of snake { self.id }")
        if not self.alive:
            return
        
        if self.body[0][0] < 0 or self.body[0][0] > self.limity-1 or self.body[0][1] < 0 or self.body[0][1] > self.limitx-1:
            self.alive = False
            return
        
        if self.body[0] in self.body[1:]: 
            self.alive = False
            return
        
        x0 = self.distance_foodx/self.limitx-1
        x1 = self.distance_foody/self.limity-1
        x2 = self.obstacle_top/MAX_CONN_WGHT
        x3 = self.obstacle_dwn/MAX_CONN_WGHT
        x4 = self.obstacle_rgt/MAX_CONN_WGHT
        x5 = self.obstacle_lft/MAX_CONN_WGHT
        
        z1 = self.neural_connections[ 0]*x0 + self.neural_connections[ 1]*x1 + self.neural_connections[ 2]*x2 + self.neural_connections[ 3]*x3 + self.neural_connections[ 4]*x4 + self.neural_connections[ 5]*x5
        z2 = self.neural_connections[ 6]*x0 + self.neural_connections[ 7]*x1 + self.neural_connections[ 8]*x2 + self.neural_connections[ 9]*x3 + self.neural_connections[10]*x4 + self.neural_connections[11]*x5
        z3 = self.neural_connections[12]*x0 + self.neural_connections[13]*x1 + self.neural_connections[14]*x2 + self.neural_connections[15]*x3 + self.neural_connections[16]*x4 + self.neural_connections[17]*x5   
        
        o1 = self.__sigmoid(self.neural_connections[18]*z1 + self.neural_connections[19]*z2 + self.neural_connections[20]*z3)
        o2 = self.__sigmoid(self.neural_connections[21]*z1 + self.neural_connections[22]*z2 + self.neural_connections[23]*z3)
        o3 = self.__sigmoid(self.neural_connections[24]*z1 + self.neural_connections[25]*z2 + self.neural_connections[26]*z3)
        o4 = self.__sigmoid(self.neural_connections[27]*z1 + self.neural_connections[28]*z2 + self.neural_connections[28]*z3)
        
        index = [o1,o2,o3,o4].index(max([o1,o2,o3,o4]))
        
        if   index == 0:
            self.direction = self.DIR_UP
        elif index == 1:
            self.direction = self.DIR_DWN
        elif index == 2:
            self.direction = self.DIR_RGT
        elif index == 3:
            self.direction = self.DIR_LFT
        
        self.__log(self.direction)
        
        body = []
        grow = False
        
        if (self.direction == self.DIR_UP):
            head_pos = (self.body[0][0]-1,self.body[0][1])
            
        if (self.direction == self.DIR_DWN):
            head_pos = (self.body[0][0]+1,self.body[0][1])
        
        if (self.direction == self.DIR_LFT):
            head_pos = (self.body[0][0],self.body[0][1]-1)
        
        if (self.direction == self.DIR_RGT):
            head_pos = (self.body[0][0],self.body[0][1]+1)

        if head_pos == self.food.get_position():
            grow=True
            
        body.append(head_pos)

        for bone in self.body[:-1]:
            body.append(bone)
        
        if grow:
            body.append(self.body[-1])
            self.food.change_position(self)
            
        self.body = body        
        self.step_count+=1

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
            
def run(snake:'Snake'):
    for _ in range(GEN_STEPS):
        snake.perceive()
        snake.move()
    
    return snake
        
        
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
        
        with Pool(4) as pool:
            new_snakes = pool.map(run,snakes)
        
        new_snakes = sorted(new_snakes,key = lambda x : len(x)**3 + x.step_count,reverse=True)
        
        snakes              = []
        snakes[:ELITE_GUYS] = new_snakes[:ELITE_GUYS]
        
        new_snakes = new_snakes[ELITE_GUYS:]
        
        while len(snakes)<MAX_POPULATION:
            snake_a = random.choice(new_snakes)
            snake_b = random.choice(new_snakes)
            
            conns_a = []
            conns_b = []
            
            for wght_a,wght_b in zip(snake_a.neural_connections,snake_b.neural_connections):
                last2_bits_a = wght_a & 3
                last2_bits_b = wght_b & 3
                
                wght_a = (wght_a >> 2) << 2
                wght_b = (wght_b >> 2) << 2
                
                wght_a = wght_a | last2_bits_b
                wght_b = wght_b | last2_bits_a
                
                if random.random() > MUTATION_PRBLTY:
                    mask   = 1 << random.choice([0,1,2,3])
                    wght_a = mask ^ wght_a
                    
                if random.random() > MUTATION_PRBLTY:
                    mask   = 1 << random.choice([0,1,2,3])
                    wght_b = mask ^ wght_b
                    
                conns_a.append(wght_a)
                conns_b.append(wght_b)
                
            snake_a.set_connections(conns_a)
            snake_b.set_connections(conns_b)
                
            snakes.append(snake_a)
                
            if len(snakes) < MAX_POPULATION:
                snakes.append(snake_b)
                    
        for snake in snakes:
            snake.step_count = 0
        
        
        for i in range(10):
            screen.addstr(i,0,str(len(snakes[i].body)))
        
        screen.refresh()
        time.sleep(2)

if __name__ == '__main__':
    input("Starting Snakevolution-CLI (Evolving) .... Press Enter to continue ")
    curses_wrap(main)
    print("Program has terminated")