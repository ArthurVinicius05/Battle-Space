import pygame
import random
from config import largura, altura      
from assets import imagens               
from typing import Optional, List
from assets import sons 

# Classe base para entidades do jogo 
class Entidade:
    def __init__(self, x: int, y: int, imagem: pygame.Surface):
        self.x = float(x)
        self.y = float(y)
        self.imagem = imagem

    def desenhar(self, tela: pygame.Surface):
        tela.blit(self.imagem, (int(self.x), int(self.y)))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y),
                           self.imagem.get_width(), self.imagem.get_height())

    @property
    def largura(self) -> int:
        return self.imagem.get_width()

    @property
    def altura(self) -> int:
        return self.imagem.get_height()


# Jogador
class Jogador(Entidade):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, imagens["jogador"])
        self.vel = 12
        self.vida = 3

    def mover(self, teclas):
        max_x = largura - self.largura
        max_y = altura - self.altura

        if teclas[pygame.K_UP] and self.y > 0:
            self.y = max(0, self.y - self.vel)
        if teclas[pygame.K_DOWN] and self.y < max_y:
            self.y = min(max_y, self.y + self.vel)


# Míssil do jogador
class Missil(Entidade):
    def __init__(self, jogador: Jogador):
        super().__init__(-999, -999, imagens["missil"])  
        self.vel = 20
        self.jogador = jogador
        self.triggered = False

    def reset(self):
        self.x = -999
        self.y = -999
        self.triggered = False

    def mover(self):
        if self.triggered:
            self.x += self.vel
            if self.x > largura:
                self.reset()
        else:
            pass

    def disparar(self):
        if not self.triggered:
            self.x = self.jogador.x + self.jogador.largura
            self.y = self.jogador.y + self.jogador.altura // 2
            self.triggered = True
            if sons["tiro"]:
                sons["tiro"].play()

    def desenhar(self, tela: pygame.Surface):
        if self.triggered:
            tela.blit(self.imagem, (int(self.x), int(self.y)))


class TiroInimigo(Entidade):
    def __init__(self, x: int, y: int, vel_x: float = -8, vel_y: float = 0, owner: Optional[str] = None):
        super().__init__(x, y, imagens["tiro_inimigo"])
        self.vel_x = float(vel_x)
        self.vel_y = float(vel_y)
        self.owner = owner

    def mover(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def fora_da_tela(self) -> bool:
        return self.x < -self.largura or self.x > largura + self.largura or self.y < -self.altura or self.y > altura + self.altura


# Inimigo básico
class Inimigo(Entidade):
    def __init__(self):
        super().__init__(0, 0, imagens["inimigo"])
        self.reset()

    def reset(self):
        self.x = random.randint(largura + 100, largura + 900)
        self.y = random.randint(0, altura - self.altura)
        self.tiros: List[TiroInimigo] = []
        self.tempo_ultimo_tiro = pygame.time.get_ticks()

    def mover(self):
        self.x -= 4
        agora = pygame.time.get_ticks()

        if agora - self.tempo_ultimo_tiro > 2000:
            self.tiros.append(TiroInimigo(self.x, self.y + self.altura // 2, vel_x=-8, owner="inimigo"))
            self.tempo_ultimo_tiro = agora

        for tiro in self.tiros:
            tiro.mover()

        self.tiros = [t for t in self.tiros if not t.fora_da_tela()]

        if self.x < -self.largura:
            self.reset()

    def desenhar(self, tela):
        super().desenhar(tela)
        for tiro in self.tiros:
            tiro.desenhar(tela)

    def morreu(self) -> bool:
        return False

    def saiu_da_tela(self) -> bool:
        return self.x < -self.largura


# Boss
class Boss(Entidade):
    def __init__(self):
        super().__init__(largura + 200, altura // 2 - 100, imagens["boss"])
        self.vida = 20
        self.tiros: List[TiroInimigo] = []
        self.tempo_ultimo_tiro = pygame.time.get_ticks()
        self.direcao = 1
        self.tempo_ultimo_tiro_angulo = pygame.time.get_ticks()
        self.angulo_index = 0
        self.angulos = [(-10,0), (-8,-4), (-8,4), (-6,-6), (-6,6)]
        self.tempo_inicio: Optional[int] = None
        self.indo_embora = False

    def mover(self):
        self.y += self.direcao * 3
        if self.y <= 0:
            self.y = 0
            self.direcao = 1
        if self.y >= altura - self.altura:
            self.y = altura - self.altura
            self.direcao = -1

        agora = pygame.time.get_ticks()

        if agora - self.tempo_ultimo_tiro_angulo > 5000:
            self.angulo_index = (self.angulo_index + 1) % len(self.angulos)
            self.tempo_ultimo_tiro_angulo = agora

        if agora - self.tempo_ultimo_tiro > 1000:
            for dx, dy in self.angulos:
                self.tiros.append(TiroInimigo(self.x, self.y + self.altura // 2, vel_x=dx, vel_y=dy, owner="boss"))
            self.tempo_ultimo_tiro = agora

        for tiro in self.tiros:
            tiro.mover()

        self.tiros = [t for t in self.tiros if not t.fora_da_tela() and 0 <= t.y <= altura]

        if self.indo_embora:
            self.x -= 8

    def iniciar(self):
        self.tempo_inicio = pygame.time.get_ticks()
        self.indo_embora = False
        self.x = largura - 250
        self.vida = 20
        self.tiros.clear()
        self.tempo_ultimo_tiro = pygame.time.get_ticks()
        self.tempo_ultimo_tiro_angulo = pygame.time.get_ticks()
        self.angulo_index = 0

    def desenhar(self, tela):
        super().desenhar(tela)
        for tiro in self.tiros:
            tiro.desenhar(tela)
        largura_barra = int(min(400, largura * 0.5))
        pygame.draw.rect(tela, (255, 0, 0), (largura // 2 - largura_barra // 2, 20, largura_barra, 20))
        proporcao = max(0.0, min(1.0, self.vida / 20))
        pygame.draw.rect(tela, (0, 255, 0), (largura // 2 - largura_barra // 2, 20, int(largura_barra * proporcao), 20))

    def morreu(self) -> bool:
        return getattr(self, "vida", 0) <= 0

    def saiu_da_tela(self) -> bool:
        return self.x < -self.largura


# Vilão Médio
class VilaoMedio(Entidade):
    ativos = 0  

    def __init__(self, x: Optional[int] = None, y: Optional[int] = None, direcao_vertical: int = 1):
        if x is None:
            x = largura - 150
        if y is None:
            y = random.randint(0, altura - imagens["vilao_medio"].get_height())

        super().__init__(x, y, imagens["vilao_medio"])
        self.vida = 3
        self.tiros: List[TiroInimigo] = []
        self.tempo_ultimo_tiro = pygame.time.get_ticks()
        self.velocidade = 0.0         
        self.velocidade_y = 2.0 * direcao_vertical
        self.direcao_vertical = direcao_vertical
        self.ativo = True
        self.contabilizado = True
        self.tempo_inicio_estacionario: Optional[int] = None
        self.tempo_max_estacionario_ms = 10000  
        VilaoMedio.ativos += 1

    def iniciar_estacionario(self, duracao_ms: int = 10000):
        self.tempo_inicio_estacionario = pygame.time.get_ticks()
        self.tempo_max_estacionario_ms = duracao_ms
        self.ficar_parado()

    def deve_avancar_por_tempo(self) -> bool:
        if self.tempo_inicio_estacionario is None:
            return False
        agora = pygame.time.get_ticks()
        return (agora - self.tempo_inicio_estacionario) >= self.tempo_max_estacionario_ms

    def mover(self):
        agora = pygame.time.get_ticks()

        if agora - self.tempo_ultimo_tiro > 1500:
            offsets = (-15, 0, 15)
            for off in offsets:
                self.tiros.append(TiroInimigo(self.x, self.y + self.altura // 2 + off, vel_x=-5, owner="vilao_medio"))
            self.tempo_ultimo_tiro = agora

        for tiro in self.tiros:
            tiro.mover()
        self.tiros = [t for t in self.tiros if not t.fora_da_tela()]

        self.x += self.velocidade
        self.y += self.velocidade_y

        if self.y <= 0:
            self.y = 0
            self.velocidade_y = abs(self.velocidade_y)
        elif self.y >= altura - self.altura:
            self.y = altura - self.altura
            self.velocidade_y = -abs(self.velocidade_y)

        if self.velocidade == 0 and self.deve_avancar_por_tempo():
            self.avancar()

        if self.velocidade < 0 and self.x < -self.largura:
            self.ativo = False
            VilaoMedio.ativos -= 1

    def ficar_parado(self):
        self.velocidade = 0

    def avancar(self):
        self.velocidade = -8

    def morrer(self):
        if self.ativo:
            self.ativo = False
            VilaoMedio.ativos -= 1

    def morreu(self) -> bool:
        return (not getattr(self, "ativo", True)) or getattr(self, "vida", 0) <= 0

    def saiu_da_tela(self) -> bool:
        return self.x < -self.largura

    def desenhar(self, tela):
        if not self.ativo:
            return
        super().desenhar(tela)
        for tiro in self.tiros:
            tiro.desenhar(tela)