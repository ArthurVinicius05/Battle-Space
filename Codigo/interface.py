import pygame
from config import fonte_padrao, BRANCO, VERDE, VERMELHO

class Botao:
    def __init__(self, texto, x, y, largura, altura, acao):
        self.texto = texto
        self.rect = pygame.Rect(x, y, largura, altura)
        self.acao = acao
        self.cor_normal = (50, 50, 50)
        self.cor_hover = (180, 180, 180)
        self.fonte = fonte_padrao

    def desenhar(self, tela):
        mouse_pos = pygame.mouse.get_pos()
        cor = self.cor_hover if self.rect.collidepoint(mouse_pos) else self.cor_normal
        pygame.draw.rect(tela, cor, self.rect)
        texto_img = self.fonte.render(self.texto, True, BRANCO)
        texto_rect = texto_img.get_rect(center=self.rect.center)
        tela.blit(texto_img, texto_rect)

    def checar_clique(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):  
                self.acao()

class Pontuacao:
    def __init__(self):
        self.pontos = 0
        self.cor = BRANCO
        self.posicao = (20, 20)
        self.fonte = fonte_padrao

    def adicionar(self, valor):
        self.pontos += valor

    def resetar(self):
        self.pontos = 0

    def desenhar(self, tela):
        texto = self.fonte.render(f"Pontos: {self.pontos}", True, self.cor)
        tela.blit(texto, self.posicao)

class Vida:
    def __init__(self, max_vida=5, x=20, y=70, largura=200, altura=20):
        self.max_vida = max_vida
        self.vida_atual = max_vida
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura

    def perder_vida(self, quantidade=0.5):
        self.vida_atual = max(0, self.vida_atual - quantidade)

    def desenhar(self, tela):
        pygame.draw.rect(tela, VERMELHO, (self.x, self.y, self.largura, self.altura))
        proporcao = self.vida_atual / self.max_vida
        pygame.draw.rect(tela, VERDE, (self.x, self.y, self.largura * proporcao, self.altura))

    def esta_vivo(self):
        return self.vida_atual > 0

class BarraBoss:
    def __init__(self, boss, x=500, y=20, largura=700, altura=20):
        self.boss = boss
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura

    def desenhar(self, tela):
        pygame.draw.rect(tela, VERMELHO, (self.x, self.y, self.largura, self.altura))
        proporcao = self.boss.vida_atual / self.boss.vida_max
        pygame.draw.rect(tela, VERDE, (self.x, self.y, self.largura * proporcao, self.altura))
