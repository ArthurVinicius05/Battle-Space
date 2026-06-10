import pygame
import sys
import pygame.mixer
from config import largura, altura, FPS, fonte_game_over
from assets import imagens, sons 
from entidades import Jogador, Missil, Inimigo, Boss, VilaoMedio
from interface import Botao, Pontuacao, Vida
from animacoes import Animacao


class Parallax:
    def __init__(self, tela, imagens, largura, altura):
        self.tela = tela
        self.largura = largura
        self.altura = altura

        self.camadas = [
            {"img": imagens["parallax_1"], "vel": 0.3, "x": 0},
            {"img": imagens["parallax_2"], "vel": 0.7, "x": 0},
            {"img": imagens["parallax_3"], "vel": 1.5, "x": 0},
        ]

    def atualizar(self):
        for camada in self.camadas:
            camada["x"] -= camada["vel"]
            if camada["x"] <= -self.largura:
                camada["x"] = 0

    def desenhar(self):
        for camada in self.camadas:
            x = camada["x"]
            self.tela.blit(camada["img"], (x, 0))
            self.tela.blit(camada["img"], (x + self.largura, 0))


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.estado = "menu"

        self.botao_jogar = Botao("Iniciar Jogo", largura // 2 - 150, altura // 2, 300, 60, self.iniciar_jogo)
        self.botao_reiniciar = Botao("Reiniciar", largura // 2 - 150, altura // 2 + 100, 300, 60, self.iniciar_jogo)
        self.botao_menu = Botao("Voltar ao Menu", largura // 2 - 150, altura // 2 + 180, 300, 60, self.voltar_menu)

        self.pausado = False

        self.desbloqueios = {10: "vilao_medio", 30: "boss"}

        self.resetar()

    def resetar(self):
        self.jogador = Jogador(150, 200)
        self.missil = Missil(self.jogador)
        self.inimigos = [Inimigo() for _ in range(2)]
        self.boss = Boss()
        self.pontuacao = Pontuacao()
        self.vida = Vida()

        self.parallax = Parallax(self.screen, imagens, largura, altura)

        self.boss_ativo = False
        self.viloes_medios: list[VilaoMedio] = []
        self.viloes_medios_ativos = False
        self.viloes_medios_derrotados = False
        self.tempo_entrada_viloes_medios = None
        self.tempo_estacionario_ms = 10000

        self.mostrar_texto_vitoria = False
        self.tempo_vitoria = None

        self.animacoes = pygame.sprite.Group()

        self.pausado = False
        self.tempo_inicio_jogo = pygame.time.get_ticks()

    def iniciar_jogo(self):
        if sons["start"]:
            sons["start"].play()

        pygame.mixer.music.load(sons["fundo_batalha"])
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.6)

        self.resetar()
        self.estado = "jogando"
        self.tempo_inicio_jogo = pygame.time.get_ticks()


    def voltar_menu(self):
        self.estado = "menu"

    def colisao(self, r1: pygame.Rect, r2: pygame.Rect) -> bool:
        return r1.colliderect(r2)

    def spawn_viloes_medios(self):
        superior = VilaoMedio(x=largura - 100, y=altura // 4, direcao_vertical=-1)
        inferior = VilaoMedio(x=largura - 100, y=3 * altura // 4, direcao_vertical=1)
        superior.iniciar_estacionario(self.tempo_estacionario_ms)
        inferior.iniciar_estacionario(self.tempo_estacionario_ms)
        self.viloes_medios = [superior, inferior]
        self.viloes_medios_ativos = True
        self.tempo_entrada_viloes_medios = pygame.time.get_ticks()

    def atualizar(self):
        teclas = pygame.key.get_pressed()
        self.jogador.mover(teclas)
        self.missil.mover()

        pontos = self.pontuacao.pontos

        if 15 <= pontos < 30 and not self.viloes_medios_ativos and not self.viloes_medios_derrotados:
            self.spawn_viloes_medios()

        if self.viloes_medios_ativos:
            agora = pygame.time.get_ticks()
            tempo_passado = agora - (self.tempo_entrada_viloes_medios or agora)

            for vilao in self.viloes_medios[:]:
                if tempo_passado < self.tempo_estacionario_ms:
                    vilao.ficar_parado()
                else:
                    vilao.avancar()

                vilao.mover()

                if self.missil.triggered and self.colisao(self.missil.get_rect(), vilao.get_rect()):
                    vilao.vida -= 1
                    self.missil.reset()
                    if vilao.vida <= 0:
                        if sons["explosao"]:
                            sons["explosao"].play()
                        self.animacoes.add(
                            Animacao(vilao.x, vilao.y, imagens["explosao"], escala=1.2)
                        )

                if self.colisao(self.jogador.get_rect(), vilao.get_rect()):
                    self.vida.perder_vida(1)

                for tiro in vilao.tiros[:]:
                    if self.colisao(tiro.get_rect(), self.jogador.get_rect()):
                        self.vida.perder_vida(1)
                        try:
                            vilao.tiros.remove(tiro)
                        except ValueError:
                            pass

                if vilao.morreu() or vilao.saiu_da_tela():
                    try:
                        self.viloes_medios.remove(vilao)
                    except ValueError:
                        pass
                    if vilao.morreu():
                        self.pontuacao.adicionar(5)

            if not self.viloes_medios:
                self.viloes_medios_ativos = False
                self.viloes_medios_derrotados = True

        if pontos >= 30 and not self.boss_ativo and self.viloes_medios_derrotados:
            self.animacoes.empty()
            self.boss_ativo = True
            self.boss.iniciar()
            self.inimigos.clear()
            self.viloes_medios.clear()
            self.viloes_medios_ativos = False

            pygame.mixer.music.load(sons["boss"])
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.7)

        if self.boss_ativo:
            self.boss.mover()
            agora = pygame.time.get_ticks()
            if self.boss.tempo_inicio is not None:
                if agora - self.boss.tempo_inicio > 30000 and not self.boss.indo_embora:
                    self.boss.indo_embora = True
                if self.boss.x < -200 and (agora - self.boss.tempo_inicio) > 5000:
                    self.boss.iniciar()

            if self.missil.triggered and self.colisao(self.missil.get_rect(), self.boss.get_rect()):
                self.boss.vida -= 1
                self.missil.reset()
                if self.boss.vida <= 0:
                    if sons["explosao"]:
                        sons["explosao"].play()
                    self.animacoes.add(
                        Animacao(self.boss.x, self.boss.y, imagens["explosao"], escala=2.0)
                    )
                    self.boss_ativo = False
                    self.estado = "vitoria"
                    self.tempo_vitoria = pygame.time.get_ticks()
                    self.mostrar_texto_vitoria = True

            for tiro in self.boss.tiros[:]:
                if self.colisao(tiro.get_rect(), self.jogador.get_rect()):
                    self.vida.perder_vida(1)
                    try:
                        self.boss.tiros.remove(tiro)
                    except ValueError:
                        pass

        if not self.boss_ativo:
            for inimigo in self.inimigos:
                inimigo.mover()
                if self.missil.triggered and self.colisao(self.missil.get_rect(), inimigo.get_rect()):
                    if sons["explosao"]:
                        sons["explosao"].play()
                    self.animacoes.add(
                        Animacao(inimigo.x, inimigo.y, imagens["explosao"], escala=0.7)
                    )
                    inimigo.reset()
                    self.missil.reset()
                    self.pontuacao.adicionar(1)
                if self.colisao(self.jogador.get_rect(), inimigo.get_rect()):
                    self.vida.perder_vida(1)
                    inimigo.reset()
                for tiro in inimigo.tiros[:]:
                    if self.colisao(tiro.get_rect(), self.jogador.get_rect()):
                        self.vida.perder_vida(1)
                        try:
                            inimigo.tiros.remove(tiro)
                        except ValueError:
                            pass

            self.animacoes.update()

        if not self.vida.esta_vivo():
            self.estado = "game_over"

    def desenhar_jogo(self):
        if not self.pausado:
            self.parallax.atualizar()

        self.parallax.desenhar()

        self.jogador.desenhar(self.screen)
        self.missil.desenhar(self.screen)

        if self.boss_ativo:
            self.boss.desenhar(self.screen)
        else:
            for inimigo in self.inimigos:
                inimigo.desenhar(self.screen)

        for vilao in self.viloes_medios:
            vilao.desenhar(self.screen)

        self.pontuacao.desenhar(self.screen)
        self.vida.desenhar(self.screen)

        if self.pausado:
            fonte_pause = pygame.font.SysFont("Arial", 150, bold=True)
            texto = fonte_pause.render("▌▌", True, (255, 255, 255))
            self.screen.blit(texto, ((largura - texto.get_width()) // 2, (altura - texto.get_height()) // 2))

        self.animacoes.draw(self.screen)
        
        pygame.display.update()

    def mostrar_menu(self):
        self.screen.blit(imagens["menu_bg"], (0, 0))
        titulo_img = imagens["nome"]
        titulo_rect = titulo_img.get_rect(center=(largura // 2, altura // 2 - 150))
        self.screen.blit(titulo_img, titulo_rect)
        self.botao_jogar.desenhar(self.screen)
        pygame.display.update()

    def mostrar_tela_vitoria(self):
        self.screen.blit(imagens["tela_final_vitoria"], (0, 0))
        if getattr(self, "mostrar_texto_vitoria", False):
            texto = fonte_game_over.render("Parabéns, você venceu!", True, (0, 255, 255))
            self.screen.blit(texto, ((largura - texto.get_width()) // 2, altura // 2 - 100))
        pygame.mixer.music.load(sons["tela_inicial"])
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)
        self.botao_reiniciar.desenhar(self.screen)
        self.botao_menu.desenhar(self.screen)
        pygame.display.update()

    def mostrar_game_over(self):
        self.screen.blit(imagens["tela_final"], (0, 0))
        texto = fonte_game_over.render("Game Over...", True, (255, 0, 0))
        self.screen.blit(texto, ((largura - texto.get_width()) // 2, altura // 2 - 100))
        pygame.mixer.music.load(sons["tela_inicial"])
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)
        self.botao_reiniciar.desenhar(self.screen)
        self.botao_menu.desenhar(self.screen)
        pygame.display.update()

    def executar(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.estado == "menu":
                    self.botao_jogar.checar_clique(event)
                if self.estado in ["game_over", "vitoria"]:
                    self.botao_reiniciar.checar_clique(event)
                    self.botao_menu.checar_clique(event)

                if event.type == pygame.KEYDOWN and self.estado == "jogando":
                    if event.key == pygame.K_RETURN:
                        self.pausado = not self.pausado
                    elif event.key == pygame.K_SPACE:
                        self.missil.disparar()

            if self.estado == "menu":
                self.mostrar_menu()
            elif self.estado == "jogando":
                if not self.pausado:
                    self.atualizar()
                self.desenhar_jogo()
                self.clock.tick(FPS)
            elif self.estado == "vitoria":
                self.mostrar_tela_vitoria()
                self.clock.tick(FPS)
            elif self.estado == "game_over":
                self.mostrar_game_over()
                self.clock.tick(FPS)
