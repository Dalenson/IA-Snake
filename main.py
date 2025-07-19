import pygame
from snake import SnakeGame
from q_learning_agent import QLearningAgent
import matplotlib.pyplot as plt
import time

agent = QLearningAgent(
    actions=[0, 1, 2],
    epsilon=1.0,
    epsilon_decay=0.9995,
    min_epsilon=0.01
)

MAX_PASSOS = 200

direcoes = [(0, -1), (1, 0), (0, 1), (-1, 0)]

def direcao_discreta(direcao):
    return direcoes.index(direcao)

def obter_estado(jogo):
    cabeca = jogo.snake[0]
    dir_x, dir_y = jogo.direcao

    esquerda = (-dir_y, dir_x)
    direita = (dir_y, -dir_x)
    frente = (dir_x, dir_y)

    def colisao(pos):
        x, y = pos
        return (
            x < 0 or x >= jogo.largura or
            y < 0 or y >= jogo.altura or
            pos in jogo.snake
        )

    pos_frente = (cabeca[0] + frente[0], cabeca[1] + frente[1])
    pos_esq = (cabeca[0] + esquerda[0], cabeca[1] + esquerda[1])
    pos_dir = (cabeca[0] + direita[0], cabeca[1] + direita[1])

    fruta_x, fruta_y = jogo.fruta
    cx, cy = cabeca

    dx_sign = 1 if fruta_x - cx > 0 else -1 if fruta_x - cx < 0 else 0
    dy_sign = 1 if fruta_y - cy > 0 else -1 if fruta_y - cy < 0 else 0
    dist_fruta = abs(cx - fruta_x) + abs(cy - fruta_y)
    dist_norm = round(dist_fruta / (jogo.largura + jogo.altura), 2)

    return (
        colisao(pos_frente),
        colisao(pos_esq),
        colisao(pos_dir),
        dx_sign,
        dy_sign,
        dist_norm,
        direcao_discreta(jogo.direcao)
    )

def aplicar_acao(jogo, acao):
    idx = direcoes.index(jogo.direcao)

    if acao == 0:
        jogo.direcao = direcoes[(idx - 1) % 4]
    elif acao == 2:
        jogo.direcao = direcoes[(idx + 1) % 4]
    # ação 1 mantém direção atual

def calcular_recompensa(jogo, estado, proximo_estado):
    if jogo.morto:
        return -100

    if jogo.snake[0] == jogo.fruta:
        return 100

    recompensa = -1

    # Penalização por girar sobre si mesmo
    if jogo.historico_cabeca.count(jogo.snake[0]) > 2:
        recompensa -= 10

    cabeca = jogo.snake[0]
    if cabeca in jogo.snake[1:]:
        recompensa -= 50

    dist_antes = estado[5]
    dist_depois = proximo_estado[5]

    if dist_depois < dist_antes:
        recompensa += 15
    elif dist_depois == dist_antes:
        recompensa -= 1
    else:
        recompensa -= 5

    return recompensa

def main(treinar=False, visualizar_final=True, n_jogos=100000):
    agent.carregar("qtable.pkl")

    if not treinar:
        agent.epsilon = 0
        n_jogos = 1

    pontuacoes = []

    for episodio in range(1, n_jogos + 1):
        jogo = SnakeGame(exibir=not treinar)
        jogo.resetar()

        while not jogo.morto:
            estado = obter_estado(jogo)
            acao = agent.choose_action(estado)
            aplicar_acao(jogo, acao)
            jogo.atualizar()

            if jogo.passos >= MAX_PASSOS:
                jogo.morto = True

            if treinar:
                proximo_estado = obter_estado(jogo)
                recompensa = calcular_recompensa(jogo, estado, proximo_estado)
                agent.learn(estado, acao, recompensa, proximo_estado)
                agent.update_epsilon()

            if not treinar:
                jogo.desenhar()
                jogo.tick()

        pontuacoes.append(jogo.pontuacao)

        if episodio % 100 == 0:
            media = sum(pontuacoes[-100:]) / 100
            print(f"Episódio {episodio} | Pontuação: {jogo.pontuacao} | Média 100: {media:.2f} | ε: {agent.epsilon:.3f}")

        if treinar and episodio % 500 == 0:
            agent.salvar("qtable.pkl")

    if treinar:
        agent.salvar("qtable.pkl")
        print("Treinamento finalizado.")

    # Exibição final da IA jogando se desejado
    if not treinar and visualizar_final:
        jogo = SnakeGame(exibir=True)
        jogo.resetar()
        while not jogo.morto:
            estado = obter_estado(jogo)
            acao = agent.choose_action(estado)
            aplicar_acao(jogo, acao)
            jogo.atualizar()
            jogo.desenhar()
            jogo.tick()

if __name__ == "__main__":
    # Para treinar: main(treinar=True)
    # Para ver a IA jogando: main(treinar=False)
    main(treinar=False)