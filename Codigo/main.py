import pygame 
import pygame.mixer
from config import largura, altura
from game import Game
from assets import sons 

pygame.init()  

screen = pygame.display.set_mode((largura, altura))

pygame.mixer.music.load(sons["tela_inicial"])
pygame.mixer.music.play(-1)  
pygame.mixer.music.set_volume(0.5)

pygame.display.set_caption("Battle Space")

game = Game(screen)

game.executar()
