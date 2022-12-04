# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)
# Code optimized by agoniko, now the power of the decision taken is influenced by the decision itself, in this way the other choices are shrunk towards zero and the neural network
# not only provides the decision to be taken (accelerate, brake, turn left/right) but by how much.
import sys
import neat
import pygame
import glob
import os
from Car import Car
from neat import Checkpointer

WIDTH = 1920
HEIGHT = 1080
current_generation = 0


def run(genomes, config):
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    game_map = pygame.image.load('map4.png').convert() # Convert Speeds Up A Lot
    pygame.display.flip()

    nets = []
    cars = []

    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        cars.append(Car())

    global current_generation

    count = 0
    while True:


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        for i,car in enumerate(cars):
            out = nets[i].activate(car.get_data())
            print(out)
            choice = out.index(max(out))
            if choice == 0:
                car.angle += (20 * out[choice]) # Left
            elif choice == 1:
                car.angle -= (20 * out[choice]) # Right
            elif choice == 2 and car.speed > 10:
                 car.speed -= (5 * out[choice])
            else:
                car.speed += (7 * out[choice])  # Speed Up


        still_alive = 0
        for i, car in enumerate(cars):
            if car.alive:
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        count +=1
        if count == 60 * 20:
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.alive:
                car.draw(screen)

        text = generation_font.render("Generation: " + str(current_generation), True, (0,255,255))
        text_rect = text.get_rect()
        text_rect.center = (100, 60)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (100, 100)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60) # 60 FPS
    current_generation += 1


if __name__ == '__main__':
    search_dir = "./checkpoints/"
    files = list(filter(os.path.isfile, glob.glob(search_dir + "*")))
    files.sort(key=lambda x: os.path.getmtime(x))

    if len(files) == 0:
        config_file = "./config.txt"
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_file)
        p = neat.Population(config)
    else:
        filename = files[len(files)-1]
        [os.remove(file) for file in files if file != filename]
        p = Checkpointer.restore_checkpoint(filename)

    pygame.init()
    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(Checkpointer(5,100,"./checkpoints/neat-checkpoint-"))
    p.run(run,100)
