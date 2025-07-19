import pygame
import random
import os

# Constantes
TAMANHO_BLOCO = 20
LARGURA = 20
ALTURA = 20
FPS = 10

# Cores
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
BRANCO = (255, 255, 255)

class SnakeGame:
    def __init__(self, exibir=True):
        self.exibir = exibir
        self.largura = LARGURA
        self.altura = ALTURA
        self.fonte = None

        if self.exibir:
            pygame.init()
            self.tela = pygame.display.set_mode((self.largura * TAMANHO_BLOCO, self.altura * TAMANHO_BLOCO))
            pygame.display.set_caption("Snake com IA")
            self.relogio = pygame.time.Clock()
            self.fonte = pygame.font.SysFont(None, 24)
        else:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.init()
            self.tela = None
            self.relogio = pygame.time.Clock()

        self.resetar()

    def resetar(self):
        self.snake = [(self.largura // 2, self.altura // 2)]
        self.direcao = (0, -1)
        self.gerar_fruta()
        self.morto = False
        self.pontuacao = 0
        self.passos = 0
        self.passos_sem_comer = 0
        self.historico_cabeca = []

    def gerar_fruta(self):
        while True:
            fruta = (random.randint(0, self.largura - 1), random.randint(0, self.altura - 1))
            if fruta not in self.snake:
                self.fruta = fruta
                break

    def virar(self, direcao):
        dx, dy = direcao
        cx, cy = self.direcao
        if (dx, dy) != (-cx, -cy):
            self.direcao = (dx, dy)

    def atualizar(self):
        if self.morto:
            return

        self.passos += 1

        nova_cabeca = (self.snake[0][0] + self.direcao[0], self.snake[0][1] + self.direcao[1])

        # Colisão
        if (
            nova_cabeca in self.snake or
            nova_cabeca[0] < 0 or nova_cabeca[0] >= self.largura or
            nova_cabeca[1] < 0 or nova_cabeca[1] >= self.altura
        ):
            self.morto = True
            return

        self.snake.insert(0, nova_cabeca)

        # Histórico
        self.historico_cabeca.append(nova_cabeca)
        if len(self.historico_cabeca) > 20:
            self.historico_cabeca.pop(0)

        if nova_cabeca == self.fruta:
            self.pontuacao += 1
            self.gerar_fruta()
            self.passos_sem_comer = 0
        else:
            self.snake.pop()
            self.passos_sem_comer += 1

    def desenhar(self):
        if not self.exibir:
            return

        self.tela.fill(PRETO)

        for bloco in self.snake:
            pygame.draw.rect(self.tela, VERDE, (
                bloco[0] * TAMANHO_BLOCO,
                bloco[1] * TAMANHO_BLOCO,
                TAMANHO_BLOCO,
                TAMANHO_BLOCO
            ))

        pygame.draw.rect(self.tela, VERMELHO, (
            self.fruta[0] * TAMANHO_BLOCO,
            self.fruta[1] * TAMANHO_BLOCO,
            TAMANHO_BLOCO,
            TAMANHO_BLOCO
        ))

        texto = self.fonte.render(f"Pontos: {self.pontuacao}", True, BRANCO)
        self.tela.blit(texto, (10, 10))
        pygame.display.flip()

    def tick(self):
        if self.exibir:
            self.relogio.tick(FPS)