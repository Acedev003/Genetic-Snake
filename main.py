import time
import random

import  curses
import _curses

from curses import wrapper as curses_wrap

MIN_SCRN_HEIGHT = 25
MIN_SCRN_WIDTH  = 80

class Snake:
     
    def __generate_body(self,world_height,world_width,length,direction):
        headx = random.randint(length,world_width-1)
        heady = random.randint(length,world_height-1)
        
        if (direction == self.DIR_UP):
            return [(heady-i,headx)for i in range(length)]
        
        if (direction == self.DIR_DWN):
            return [(heady+i,headx)for i in range(length)]
        
        if (direction == self.DIR_LFT):
            return [(heady,headx-i)for i in range(length)]
        
        if (direction == self.DIR_RGT):
            return [(heady,headx+i)for i in range(length)]
    
        
    def __log(self,msg):
        file = open("log.txt",'a+')
        file.writelines([str(msg)+"\n"])
        file.close()
    
    
    def __init__(self,world_height,world_width,length=15):
        self.DIR_UP  =  1
        self.DIR_RGT =  2
        self.DIR_DWN = -1
        self.DIR_LFT = -2

        self.alive     = True
        self.length    = length
        self.direction = random.choice([self.DIR_DWN,
                                        self.DIR_LFT,
                                        self.DIR_RGT,
                                        self.DIR_UP])

        self.body      = self.__generate_body(world_height,world_width,self.length,self.direction)
        
    def draw(self,screen: 'curses._CursesWindow'):
        for bone in self.body:
            screen.addch(bone[0],bone[1],'#')
    
    def set_direction(self,direction):
        self.direction = direction
    
    def move(self):
        body = []
        
        if (self.direction == self.DIR_UP):
            body.append((self.body[0][0]-1,self.body[0][1]))
            
        if (self.direction == self.DIR_DWN):
            body.append((self.body[0][0]+1,self.body[0][1]))
        
        if (self.direction == self.DIR_LFT):
            body.append((self.body[0][0],self.body[0][1]-1))
        
        if (self.direction == self.DIR_RGT):
            body.append((self.body[0][0],self.body[0][1]+1))

        for bone in self.body[:-1]:
            body.append(bone)

        self.body = body
        self.__log(body)
            
    def am_i_alive(self):
        pass
    
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
    
    snake = Snake(maxy,maxx)
    
    while running:    
        screen.clear()
        key = screen.getch()
        if key == ord('q') or key == ord('Q'):
            running = False
            continue
        if key == curses.KEY_UP:
            snake.set_direction(snake.DIR_UP)
        elif key == curses.KEY_DOWN:
            snake.set_direction(snake.DIR_DWN)
        elif key == curses.KEY_LEFT:
            snake.set_direction(snake.DIR_LFT)
        elif key == curses.KEY_RIGHT:
            snake.set_direction(snake.DIR_RGT)
        
        snake.draw(screen)
        snake.move()
        screen.refresh()
        time.sleep(0.09)

if __name__ == '__main__':
    input("Starting TermSnake .... Press Enter to continue ")
    curses_wrap(main)
    print("Program has terminated")