import pygame
import os 
import pygame.mixer
from config import largura, altura

pygame.init()
pygame.mixer.init()

TELA = pygame.display.set_mode((largura, altura))

def carregar_imagem(caminho, tamanho=None):
    try:
        imagem = pygame.image.load(caminho).convert_alpha()
        if tamanho:
            imagem = pygame.transform.scale(imagem, tamanho)
        return imagem
    except pygame.error as e:
        print(f"Erro ao carregar a imagem {caminho}: {e}")
        return pygame.Surface((tamanho if tamanho else (50, 50)), pygame.SRCALPHA)

imagens = {
    "nome" : carregar_imagem("images/nome.png", (600, 400)),
    "jogador": carregar_imagem("images/aviao_arthur.png", (100, 100)),
    "missil": carregar_imagem("images/missil_arthur.png", (50, 30)),
    "inimigo": carregar_imagem("images/minivilao.png", (70, 70)),
    "tiro_inimigo": carregar_imagem("images/tiro_vilao.png", (50, 50)),
    "menu_bg": carregar_imagem("images/menu_bg.png", (largura, altura)),
    "tela_final": carregar_imagem("images/tela_final_derrota.png", (largura, altura)),
    "tela_final_vitoria": carregar_imagem("images/tela_final_vitoria.png", (largura, altura)),
    "boss": carregar_imagem("images/vilao.png", (200, 200)),
    "tiro_boss": carregar_imagem("images/tiro_vilao.png", (50, 50)),
    "vilao_medio": carregar_imagem("images/vilao_medio.png", (125, 125))
}


def carregar_sequencia_explosao(base_path, quantidade):
    imagens = []
    for i in range(1, quantidade + 1):
        caminho = os.path.join(base_path, f"exp{i}.png")
        if not os.path.exists(caminho):
            print(f"Erro ao carregar {caminho}: arquivo não encontrado.")
            continue
        try:
            img = pygame.image.load(caminho).convert_alpha()
            imagens.append(img)
        except Exception as e:
            print(f"Erro ao carregar {caminho}: {e}")

    if not imagens:
        print("Aviso: nenhuma imagem de explosao encontrada em", base_path, "-> usando frames provisórios.")
        for s in (24, 40, 56, 72, 88, 104):
            surf = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 160, 0, 200), (s//2, s//2), s//2)
            imagens.append(surf)

    return imagens

imagens["explosao"] = carregar_sequencia_explosao("images/explosao", 6)


def carregar_som(caminho):
    try: 
        return pygame.mixer.Sound(caminho)
    except pygame.error as e:
        print(f"Erro ao carregar o som {caminho}: {e}")
        return None 
    

sons = {
    "tela_inicial": "sounds/music_tela_inicial.mp3",
    "fundo_batalha": "sounds/music_fundo_batalha.mp3",
    "boss": "sounds/music_boss.mp3", 


    "explosao": carregar_som("sounds/music_explosao.wav"),
    "start": carregar_som("sounds/music_start.wav"),
    "tiro": carregar_som("sounds/music_tiro_laser.wav")
}

imagens["parallax_1"] = pygame.transform.scale(
    pygame.image.load("images/fundos/1.png").convert_alpha(), (largura, altura)
)
imagens["parallax_2"] = pygame.transform.scale(
    pygame.image.load("images/fundos/2.png").convert_alpha(), (largura, altura)
)
imagens["parallax_3"] = pygame.transform.scale(
    pygame.image.load("images/fundos/3.png").convert_alpha(), (largura, altura)
)