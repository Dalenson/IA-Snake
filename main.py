import pygame
from snake import SnakeGame
from q_learning_agent import QLearningAgent
import time
import matplotlib.pyplot as plt

# plt.ion()  # modo interativo ligado
# fig, ax = plt.subplots()
# linha, = ax.plot([], [])
# ax.set_xlim(0, 1000)  # ajuste conforme número de episódios
# ax.set_ylim(0, 50)    # ajuste conforme a pontuação esperada
# ax.set_xlabel('Episódio')
# ax.set_ylabel('Pontuação')
# ax.set_title('Pontuação por Episódio')

def atualizar_grafico(pontuacoes):
    linha.set_xdata(range(len(pontuacoes)))
    linha.set_ydata(pontuacoes)
    ax.relim()
    ax.autoscale_view()
    # plt.draw()
    # plt.pause(0.01)

# Define ações
# 0: virar à esquerda
# 1: seguir reto
# 2: virar à direita
agent = QLearningAgent(
    actions=[0, 1, 2],
    epsilon=1.0,
    epsilon_decay=0.9995,  # desacelere bastante
    min_epsilon=0.01       # não deixe a IA ficar completamente determinística tão rápido
)
MAX_PASSOS = 50
direcoes = [(0, -1), (1, 0), (0, 1), (-1, 0)]

def direcao_discreta(direcao):
    direcoes = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    return direcoes.index(direcao)

# Função para obter estado discreto
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
    dist_fruta = abs(cx - fruta_x) + abs(cy - fruta_y)  # nova informação crítica

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

# Aplica a ação escolhida pela IA
def aplicar_acao(jogo, acao):
    direcoes = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # cima, direita, baixo, esquerda
    idx = direcoes.index(jogo.direcao)

    if acao == 0:
        jogo.direcao = direcoes[(idx - 1) % 4]
    elif acao == 2:
        jogo.direcao = direcoes[(idx + 1) % 4]
    # ação 1 mantém a mesma direção

def calcular_recompensa(jogo, estado, proximo_estado):
    if jogo.morto:
        return -100

    if jogo.snake[0] == jogo.fruta:
        return 100

    recompensa = -1  # penalidade básica

    # Penaliza se está girando em si mesmo
    if jogo.historico_cabeca.count(jogo.snake[0]) > 2:
        recompensa -= 10

    # Recompensa se está se aproximando da fruta
    dist_antes = estado[5]
    dist_depois = proximo_estado[5]
    if dist_depois < dist_antes:
        recompensa += 5
    elif dist_depois > dist_antes:
        recompensa -= 2

    recompensa += 0.5

    if dist_depois < dist_antes:
        recompensa += 10  # maior que antes
    elif dist_depois == dist_antes:
        recompensa -= 1  # menos que se afastar
    else:
        recompensa -= 5  # se afastou da fruta

    return recompensa

def main(treinar=False):
    TOTAL_JOGOS = 100000
    if(treinar == False):
        TOTAL_JOGOS = 1
    jogo = SnakeGame()
    pontuacoes = []
    agent.carregar("qtable.pkl")

    if not treinar:
        agent.epsilon = 0 

    for episodio in range(1, TOTAL_JOGOS + 1):
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

            # Treinamento sem exibir tela
            if(treinar == True):
                jogo.relogio.tick(0)
            else:
                # jogo.desenhar()
                jogo.relogio.tick(60)

        pontuacoes.append(jogo.pontuacao)
        if episodio % 100 == 0:
            media = sum(pontuacoes[-100:]) / 100
            print(f"Episódio {episodio} | Última pontuação: {jogo.pontuacao} | Média 100: {media:.2f} | ε: {agent.epsilon:.3f}")
        if(treinar == True):
            agent.salvar("qtable.pkl")

    if(treinar == True):      
        # Salvar a Q-table
        agent.salvar("qtable.pkl")
        print("Treinamento finalizado.")

    # Loop final apenas para ver a IA jogando com ε = 0
    agent.epsilon = 0
    continuar = True
    while continuar:
        if(jogo.morto):
            continuar = False
        jogo = SnakeGame()
        jogo.resetar()
        while not jogo.morto:
            estado = obter_estado(jogo)
            acao = agent.choose_action(estado)
            aplicar_acao(jogo, acao)
            jogo.atualizar()
            if jogo.passos_sem_comer >= 40:
                jogo.morto = True
            jogo.desenhar()
            jogo.tick()

if __name__ == "__main__":
    main()