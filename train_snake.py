import copy
import math
import time
import random
import pickle

from multiprocessing import Pool

import curses
from   curses import wrapper as curses_wrap

MIN_SCRN_HEIGHT = 25
MIN_SCRN_WIDTH  = 25

MAX_POPULATION  = 10000
FIT_POPULATION  = 5000
ELITE_GUYS      = 500
GEN_STEPS       = 2000
MUTATION_PRBLTY = 0.40

MAX_CONN_WGHT   = 32
CONNECTIONS_CNT = 30

CPU_POOL_SIZE    = 4

SNAKE_LIFE = 1000
START_SIZE = 3

FOOD_CHAR  = "@"
SNAKE_CHAR = "#"

class Snake:
    """
    The class that describes the functions and capabilities of the only species in this world - Le Snake 
    """
    # Used to generate the initial snake body
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
    
    #softmax function    
    def __softmax(self,x:list):
        x       = [val-max(x) for val in x]
        exp_val = [ math.exp(val) for val in x ]
        denom   = sum(exp_val)
        return [x/denom for x in exp_val]
    
    # Helper Logging utility
    def __log(self,msg):
        if not self.debug:
            return
        
        file = open("log.txt",'a+')
        file.writelines([str(msg)+"\n"])
        file.close()
    
    def __init__(self,id:str,food:'Food',world_height:int,world_width:int,length:int = START_SIZE,life=SNAKE_LIFE):
        self.DIR_UP  =  1
        self.DIR_RGT =  2
        self.DIR_DWN = -1
        self.DIR_LFT = -2
        
        self.limitx  = world_width
        self.limity  = world_height
        
        self.alive      = True
        self.def_length = length
        self.step_count = 0
        self.debug      = False
        self.direction  = random.choice([self.DIR_DWN,
                                         self.DIR_LFT,
                                         self.DIR_RGT,
                                         self.DIR_UP])
        self.initial_direction = self.direction
        
        self.id        = id
        self.life      = life
        self.penalty   = 0
        self.food      = food
        self.body      = self.__generate_body(world_height,world_width,self.def_length,self.direction)
        
        self.obstacle_top       = 0
        self.obstacle_dwn       = 0
        self.obstacle_lft       = 0
        self.obstacle_rgt       = 0 
        self.distance_foodx     = 0
        self.distance_foody     = 0
        self.neural_connections = [random.randint(-MAX_CONN_WGHT,MAX_CONN_WGHT) for _ in range(CONNECTIONS_CNT)]
        
    def __len__(self):
        return len(self.body)
        
    # Update connections
    def set_connections(self,connections):
        self.neural_connections = connections
    
    # Look around for food and obstacles
    def perceive(self):
        if not self.alive:
            return
        
        heady = self.body[0][0]
        headx = self.body[0][1]
        
        self.distance_foody = heady - self.food.position[0]
        self.distance_foodx = headx - self.food.position[1]
    
        if heady-1 < 0 or (heady-1,headx) in self.body:
            self.obstacle_top = 0.1
        else:
            self.obstacle_top = 0
        
        if heady+1 > self.limity-1 or (heady+1,headx) in self.body:
            self.obstacle_dwn = 0.1
        else:
            self.obstacle_dwn = 0
            
        if headx-1 < 0 or (heady,headx-1) in self.body:
            self.obstacle_lft = 0.1
        else:
            self.obstacle_lft = 0
            
        if headx+1 > self.limitx-1 or (heady,headx+1) in self.body:
            self.obstacle_rgt = 0.1
        else:
            self.obstacle_rgt = 0
            
    # Use brain and then move the snake
    def move(self):
        if not self.alive:
            return
        
        # Died due to not eating for long
        if self.life < 1:
            self.__log(f"Snake {self.id} Dead   : No life")
            self.penalty = 1000
            self.alive   = False
            return
        
        # Inputs
        x0 = (self.distance_foody)
        x1 = (self.distance_foodx)
        x2 = self.obstacle_top
        x3 = self.obstacle_dwn
        x4 = self.obstacle_rgt
        x5 = self.obstacle_lft
        
        self.__log(f"Snake {self.id} Inputs : {[x0,x1,x2,x3,x4,x5]}")
        self.__log(f"Snake {self.id} Body   : ")
        self.__log(f"   {self.body}")
        self.__log("")
        
        # Neural Network with hidden layers (z1,z2,z3) and outputs (o1,o2,o3,o4) and 30 Neurons
        z1 = self.neural_connections[ 0]*x0 + self.neural_connections[ 1]*x1 + self.neural_connections[ 2]*x2 + self.neural_connections[ 3]*x3 + self.neural_connections[ 4]*x4 + self.neural_connections[ 5]*x5
        z2 = self.neural_connections[ 6]*x0 + self.neural_connections[ 7]*x1 + self.neural_connections[ 8]*x2 + self.neural_connections[ 9]*x3 + self.neural_connections[10]*x4 + self.neural_connections[11]*x5
        z3 = self.neural_connections[12]*x0 + self.neural_connections[13]*x1 + self.neural_connections[14]*x2 + self.neural_connections[15]*x3 + self.neural_connections[16]*x4 + self.neural_connections[17]*x5   
        
        o1 = self.neural_connections[18]*z1 + self.neural_connections[19]*z2 + self.neural_connections[20]*z3
        o2 = self.neural_connections[21]*z1 + self.neural_connections[22]*z2 + self.neural_connections[23]*z3
        o3 = self.neural_connections[24]*z1 + self.neural_connections[25]*z2 + self.neural_connections[26]*z3
        o4 = self.neural_connections[27]*z1 + self.neural_connections[28]*z2 + self.neural_connections[29]*z3
        
        o1,o2,o3,o4 = self.__softmax([o1,o2,o3,o4])
        
        # Alternate network with 24 neurons
        # o1 = self.__sigmoid(self.neural_connections[ 0]*x0 + self.neural_connections[ 1]*x1 + self.neural_connections[ 2]*x2 + self.neural_connections[ 3]*x3 + self.neural_connections[ 4]*x4 + self.neural_connections[ 5]*x5)
        # o2 = self.__sigmoid(self.neural_connections[ 6]*x0 + self.neural_connections[ 7]*x1 + self.neural_connections[ 8]*x2 + self.neural_connections[ 9]*x3 + self.neural_connections[10]*x4 + self.neural_connections[11]*x5)
        # o3 = self.__sigmoid(self.neural_connections[12]*x0 + self.neural_connections[13]*x1 + self.neural_connections[14]*x2 + self.neural_connections[15]*x3 + self.neural_connections[16]*x4 + self.neural_connections[17]*x5)  
        # o4 = self.__sigmoid(self.neural_connections[18]*x0 + self.neural_connections[19]*x1 + self.neural_connections[20]*x2 + self.neural_connections[21]*x3 + self.neural_connections[22]*x4 + self.neural_connections[23]*x5)
        
        index = [o1,o2,o3,o4].index(max([o1,o2,o3,o4]))
        
        self.__log(f"Snake {self.id} Output : {[o1,o2,o3,o4]}")
        
        if   index == 0:
            self.__log(f"Snake {self.id} Direct : UP")
            self.direction = self.DIR_UP
        elif index == 1:
            self.__log(f"Snake {self.id} Direct : DWN")
            self.direction = self.DIR_DWN
        elif index == 2:
            self.__log(f"Snake {self.id} Direct : RGT")
            self.direction = self.DIR_RGT
        elif index == 3:
            self.__log(f"Snake {self.id} Direct : LFT")
            self.direction = self.DIR_LFT
        
        body = []
        grow = False
        
        # Movement Logic
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
            self.life=SNAKE_LIFE
            body.append(self.body[-1])
            self.food.change_position(self)
        
        # Wall Collision Check
        if body[0][0] < 0 or body[0][0] > self.limity-1 or body[0][1] < 0 or body[0][1] > self.limitx-1:
            self.__log(f"Snake {self.id} Dead   : Wall collision")
            self.penalty = 100
            self.alive   = False
            return
        
        # Self Cannibalism Check
        if body[0] in body[1:]: 
            self.__log(f"Snake {self.id} Dead   : Ate itself")
            self.penalty = 10000
            self.alive = False
            return
        
        self.body = body        
        self.step_count+=1
        self.life-=1
        
        
    # Render snake in screen
    def draw(self,screen: 'curses._CursesWindow'):
        if not self.alive:
            return
        for bone in self.body:
            screen.addch(bone[0],bone[1],SNAKE_CHAR)
        
    # Resets snake to initial state
    def reset_body(self):
        self.life       = SNAKE_LIFE
        self.step_count = 0
        self.penalty    = 0
        self.alive      = True
        self.body       = self.__generate_body(self.limity,self.limitx,self.def_length,self.initial_direction)
    
    # Helper utility to log data into a log file
    def log(self,x):
        self.__log(x)

class Food:
    """
    Food class that serves as the food each snake eats
    """
    def __init__(self,world_height,world_width,pos=None):
        self.world_height = world_height
        self.world_width  = world_width
        if pos:
            self.position = pos
        else:
            self.position = (random.randint(0,self.world_height-1),random.randint(0,self.world_width-1))    # Randomly position within world bounds
        self.initial_pos  = self.position
        
    def reset_position(self):
        self.position = self.initial_pos            # Resets position to initial position  
        
    # Return current position of food
    def get_position(self):
        return self.position
    
    # Update position to new random location
    def change_position(self,predator:'Snake'):
        self.position = (random.randint(0,self.world_height-1),random.randint(0,self.world_width-1))       
        
        while self.position in predator.body:
            self.position = (random.randint(0,self.world_height-1),random.randint(0,self.world_width-1))
    
    # Render food to screen
    def draw(self,screen: 'curses._CursesWindow'):     
        screen.addch(self.position[0],self.position[1],FOOD_CHAR)
            
def interact(snake:'Snake'):
    for _ in range(GEN_STEPS):
        snake.perceive()
        snake.move()
    
    return snake

def crossover_and_mutate(snake_a:'Snake',snake_b:'Snake'):
    """
    Crossover, mutate and swap weights of neural connections of 2 snakes.
    """
    conns_a = []    # Neural connections of snake_a
    conns_b = []    # Neural connections of snake_b
            
    for wght_a,wght_b in zip(snake_a.neural_connections,snake_b.neural_connections):

        # Crossover
        
        last2_bits_a = wght_a & 2
        last2_bits_b = wght_b & 2
        wght_a = (wght_a >> 2) << 2
        wght_b = (wght_b >> 2) << 2
        wght_a = wght_a | last2_bits_b
        wght_b = wght_b | last2_bits_a
                
        # Mutation by random flipping of a bit
        if random.random() < MUTATION_PRBLTY:
            mask   = 1 << random.choice([0])
            wght_a = mask ^ wght_a
                    
        if random.random() < MUTATION_PRBLTY:
                    mask   = 1 << random.choice([0])
                    wght_b = mask ^ wght_b
                    
        conns_a.append(wght_a)
        conns_b.append(wght_b)
    
    return (conns_a,conns_b)

def replay_movement(snake:'Snake',food:'Food',screen:'curses._CursesWindow'):
    count = 5000
    curses.raw()
    curses.cbreak()
    while snake.alive or count < 0:
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
        count-=1   
    
    screen.clear()
    curses.raw(False)
    curses.cbreak(False)

def main(screen: 'curses._CursesWindow'):
    train_loop_running = True
    generation_count   = 0
    best_snake_size    = 0

    screen_height,screen_width = screen.getmaxyx()
    
    if screen_height < MIN_SCRN_HEIGHT:
        train_loop_running = False
        screen.addstr(f"Screen Height less than required (min_height:{MIN_SCRN_HEIGHT}). Press any key to exit")
        screen.getkey()
    if screen_width < MIN_SCRN_WIDTH:
        train_loop_running = False
        screen.addstr(f"Screen Width less than required (min_width:{MIN_SCRN_WIDTH}). Press any key to exit")
        screen.getkey()
    
    # Disable delay for getch and set cursor visibility to 0
    screen.nodelay(True)
    curses.curs_set(0)
    
    foods  = [Food(screen_height-1,screen_width-1) for _ in range(MAX_POPULATION)]                  # Food for each unique snake used for training
    snakes = [Snake(str(i),foods[i],screen_height-1,screen_width-1) for i in range(MAX_POPULATION)] # Population of snakes to be used for training
    
    while train_loop_running:
        
        # Reinitialize new food for new generations 
        if generation_count != 0:
            foods = [Food(screen_height-1,screen_width-1) for _ in range(MAX_POPULATION)]
            for i,snake in enumerate(snakes):
                snake.food = foods[i]
        
        # Make snakes perceive and move about in the environment
        with Pool(CPU_POOL_SIZE) as pool:
            new_snakes = pool.map(interact,snakes)
        
        # Fitness based sorting and elimination of the population
        new_snakes = sorted(new_snakes,key = lambda x : len(x)**4-x.penalty,reverse=True)[:FIT_POPULATION]
        
        # Elitism - selecting the top players directly to next generation
        snakes  = []
        snakes += new_snakes[:ELITE_GUYS]
        
        # Getting data of current generation's best snake
        best_snake       = copy.deepcopy(snakes[0])
        best_snks_food   = best_snake.food
        best_snake.reset_body()
        best_snake.debug = True
        best_snake.log("")
        best_snake.log("+-------------------------------------------------------------------------+")
        best_snake.log(f"Snake {best_snake.id} Neural :")
        best_snake.log("")
        best_snake.log(f"   {best_snake.neural_connections}")
        best_snake.log("")
        best_snks_food.reset_position()
        
        # Crossover and mutate from new population till MAX_POPULATION is reached for next generation
        while len(snakes)<MAX_POPULATION:
            snake_a = copy.deepcopy(random.choice(new_snakes))
            snake_b = copy.deepcopy(random.choice(new_snakes))
            
            connections = crossover_and_mutate(snake_a,snake_b)
                
            snake_a.set_connections(connections[0])
            snake_b.set_connections(connections[1])
            
            snakes.append(snake_a)
                
            if len(snakes) < MAX_POPULATION:
                snakes.append(snake_b)
        
        # Print data of the top 10 new snakes
        screen.clear()
        for i in range(10):
            screen.addstr(i,0,f"Size : {len(snakes[i].body)}")
            screen.addstr(i,20,f"Penalty : {snakes[i].penalty}")
            screen.addstr(i,40,f"ID : {snakes[i].id}")
        
        screen.addstr(screen_height-2,0,f"Generation: {generation_count}")
        generation_count+=1
        screen.refresh()
        
        # Reset bodies of mutated snakes for next generation
        for snake in snakes:
            snake.reset_body()
        
        time.sleep(2)
        
        # Replay of current generation's best snake
        replay_movement(best_snake,best_snks_food,screen)

        time.sleep(2)
        screen.clear()
        
        # Save best_snake if current length defeats previous record
        if len(best_snake.body)>best_snake_size:
            best_snake_size = len(best_snake.body)
            with open('best_snake.snk','wb') as file:
                pickle.dump(best_snake,file)    
            best_snake.log(f"Snake {best_snake.id} Saved")
        
        best_snake.debug = False    # Resets the best snake debug mode
        
        screen.addstr(f"Processing Generation {generation_count+1}")
        screen.refresh()

if __name__ == '__main__':
    input("Starting Snakevolution-CLI (Evolving-Train) .... Press Enter to continue ")
    
    # Wrapper for curses intialization and auto de-initialize
    curses_wrap(main)                  
    
    print("Program has terminated")