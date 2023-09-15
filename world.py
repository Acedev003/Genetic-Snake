import math
import random
import curses


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
    
    def __init__(self,id:str,food:'Food',world_height:int,world_width:int,def_length:int,start_life:int,max_connection_weight:int,connection_count:int,snake_char="#"):
        self.DIR_UP  =  1
        self.DIR_RGT =  2
        self.DIR_DWN = -1
        self.DIR_LFT = -2
        
        self.limitx  = world_width
        self.limity  = world_height
        
        self.alive      = True
        self.def_length = def_length
        self.step_count = 0
        self.debug      = False
        self.direction  = random.choice([self.DIR_DWN,
                                         self.DIR_LFT,
                                         self.DIR_RGT,
                                         self.DIR_UP])
        self.initial_direction = self.direction
        
        self.id        = id
        self.strt_life = start_life
        self.life      = start_life
        self.penalty   = 0
        self.food      = food
        self.snk_char  = snake_char
        self.body      = self.__generate_body(world_height,world_width,self.def_length,self.direction)
        
        self.obstacle_top       = 0
        self.obstacle_dwn       = 0
        self.obstacle_lft       = 0
        self.obstacle_rgt       = 0 
        self.distance_foodx     = 0
        self.distance_foody     = 0
        self.neural_connections = [random.randint(-max_connection_weight,max_connection_weight) for _ in range(connection_count)]
        
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
            self.obstacle_top = 1
        else:
            self.obstacle_top = 0
        
        if heady+1 > self.limity-1 or (heady+1,headx) in self.body:
            self.obstacle_dwn = 1
        else:
            self.obstacle_dwn = 0
            
        if headx-1 < 0 or (heady,headx-1) in self.body:
            self.obstacle_lft = 1
        else:
            self.obstacle_lft = 0
            
        if headx+1 > self.limitx-1 or (heady,headx+1) in self.body:
            self.obstacle_rgt = 1
        else:
            self.obstacle_rgt = 0
            
    # Use brain and then move the snake
    def move(self):
        if not self.alive:
            return
        
        # Died due to not eating for long
        if self.life < 1:
            self.__log(f"Snake {self.id} Dead   : No life")
            self.penalty = 9998
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
            self.life=self.strt_life
            body.append(self.body[-1])
            self.food.change_position(self)
        
        # Wall Collision Check
        if body[0][0] < 0 or body[0][0] > self.limity-1 or body[0][1] < 0 or body[0][1] > self.limitx-1:
            self.__log(f"Snake {self.id} Dead   : Wall collision")
            self.penalty = 9999
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
            screen.addch(bone[0],bone[1],self.snk_char)
        
    # Resets snake to initial state
    def reset_body(self):
        self.life       = self.strt_life
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
    def __init__(self,world_height,world_width,food_char='@',pos=None):
        self.world_height = world_height
        self.world_width  = world_width
        
        self.food_char    = food_char
        
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
        screen.addch(self.position[0],self.position[1],self.food_char)
