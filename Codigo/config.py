import pygame

largura, altura = 1280, 720
FPS = 60
BRANCO   = (255, 255, 255)
VERDE    = (0, 255, 0)
VERMELHO = (255, 0, 0)

pygame.init()

try:
    fonte_padrao =  pygame.font.SysFont("Arial", 40)
    fonte_game_over =  pygame.font.SysFont("Arial", 100)
except Exception as e:
    print(f"Erro ao inicializar fontes: {e}")
    pygame.font.init()
    fonte_padrao =  pygame.font.SysFont("Arial", 40)
    fonte_game_over =  pygame.font.SysFont("Arial", 100)
