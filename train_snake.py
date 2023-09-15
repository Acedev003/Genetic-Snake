import copy
import time
import random
import pickle
import json
import statistics

from world import Snake,Food
from multiprocessing import Pool

import curses
from   curses import wrapper as curses_wrap

MIN_SCRN_HEIGHT = 25
MIN_SCRN_WIDTH  = 25

MAX_POPULATION  = 10000
FIT_POPULATION  = 8000
ELITE_GUYS      = 1000
GEN_STEPS       = 2000
MUTATION_PRBLTY = 0.40

MAX_CONN_WGHT   = 8
CONNECTIONS_CNT = 30

CPU_POOL_SIZE    = 3

SNAKE_LIFE = 2000
START_SIZE = 3

FOOD_CHAR  = "@"
SNAKE_CHAR = "#"
            
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
            mask   = 1 << random.choice([0,1,2,3,4])
            wght_a = mask ^ wght_a
                    
        if random.random() < MUTATION_PRBLTY:
                    mask   = 1 << random.choice([0,1,2,3,4])
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

def log_json(data:dict):
    with open("stats.txt",'a') as file:
        file.write(json.dumps(data)+"\n")

def main(screen: 'curses._CursesWindow'):
    train_loop_running = True
    replay_enabled     = False
    generation_count   = 0
    best_snake_size    = 0
    execution_time     = 0

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
    
    food   = Food(screen_height-1,screen_width-1,FOOD_CHAR)
    snakes = [Snake(
                id=str(i),
                food=copy.deepcopy(food),
                world_height=screen_height-1,
                world_width=screen_width-1,
                def_length=START_SIZE,
                start_life=SNAKE_LIFE,
                max_connection_weight=MAX_CONN_WGHT,
                connection_count=CONNECTIONS_CNT,
                snake_char=SNAKE_CHAR) for i in range(MAX_POPULATION)] # Population of snakes to be used for training
    
    while train_loop_running:
        
        # Reinitialize new food for new generations 
        if generation_count != 0:
            food = Food(screen_height-1,screen_width-1,FOOD_CHAR)
            for i,snake in enumerate(snakes):
                snake.food = copy.deepcopy(food)
        
        # Make snakes perceive and move about in the environment
        start_time = time.time()
        with Pool(CPU_POOL_SIZE) as pool:
            new_snakes = pool.map(interact,snakes)
        execution_time = time.time() - start_time
        
        # Fitness based sorting and elimination of the population
        new_snakes = sorted(new_snakes,key = lambda x : x.step_count)
        new_snakes = sorted(new_snakes,key = lambda x : x.penalty)
        new_snakes = sorted(new_snakes,key = lambda x : x.alive,reverse=True)
        new_snakes = sorted(new_snakes,key = lambda x : len(x),reverse=True)[:FIT_POPULATION]
        
        # Elitism - selecting the top players directly to next generation
        snakes  = []
        snakes += new_snakes[:ELITE_GUYS]
        
        # Getting data of current generation's best snake
        best_snake       = copy.deepcopy(snakes[0])
        best_snks_food   = best_snake.food
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
        
        log_json(dict({
            "gen_count" : generation_count,
            "gen_comp_time" : execution_time,
            "max_size" : len(snakes[0]),
            "avg_size_10" : sum([len(snakes[i].body) for i in range(10)])/10,
            f"freq_penalty_10" : statistics.mode([x.penalty for x in snakes[:10]])
        }))
        
        screen.addstr(screen_height-2,0,f"Generation: {generation_count}")
        generation_count+=1
        screen.refresh()
        
        
        # Reset bodies of mutated snakes for next generation
        for snake in snakes:
            snake.reset_body()
        
        if generation_count > 20 and replay_enabled:
            time.sleep(2)

            # Replay of current generation's best snake
            replay_movement(best_snake,best_snks_food,screen)
            
        time.sleep(2)
        screen.clear()
        
        # Save best_snake if current length defeats previous record
        if len(best_snake)>best_snake_size:
            best_snake_size = len(best_snake.body)
            with open('best_snake.snk','wb') as file:
                pickle.dump(best_snake,file)    
            best_snake.log(f"Snake {best_snake.id} Saved")
        
        best_snake.reset_body()
        best_snake.debug = False    # Resets the best snake debug mode
        
        screen.addstr(f"Processing Generation {generation_count}")
        screen.refresh()

if __name__ == '__main__':
    input("Starting Snakevolution-CLI (Evolving-Train) .... Press Enter to continue ")
    
    # Wrapper for curses intialization and auto de-initialize
    curses_wrap(main)                  
    
    print("Program has terminated")