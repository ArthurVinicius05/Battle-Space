import pygame

class Animacao(pygame.sprite.Sprite):
    def __init__(self, x, y, imagens_explosao, escala: float = None, tamanho: tuple = None, velocidade: int = 4):
        super().__init__()
        
        # se nenhuma imagem foi carregada, cria frames provisórios
        if not imagens_explosao:
            frames_tmp = []
            for s in (24, 40, 56, 72, 88, 104):
                surf = pygame.Surface((s, s), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 180, 0, 220), (s//2, s//2), s//2)
                frames_tmp.append(surf)
            imagens_explosao = frames_tmp

        # cria frames redimensionados conforme argumentos
        frames = []
        for img in imagens_explosao:
            if tamanho is not None:
                frm = pygame.transform.scale(img, (int(tamanho[0]), int(tamanho[1])))
            elif escala is not None:
                w = max(1, int(img.get_width() * escala))
                h = max(1, int(img.get_height() * escala))
                frm = pygame.transform.scale(img, (w, h))
            else:
                frm = img.copy()
            frames.append(frm)

        self.frames = frames
        self.index = 0
        self.image = self.frames[self.index]
        # centraliza no ponto (x,y)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.contador = 0
        self.velocidade = max(1, int(velocidade))

    def update(self):
        self.contador += 1
        if self.contador >= self.velocidade:
            self.contador = 0
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.index]
