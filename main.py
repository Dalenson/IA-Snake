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
    cabeca = self.cobra[0]
    dir_x, dir_y = self.direcao  # exemplo: (1, 0) → direita
    
    # Direções rotacionadas
    esquerda = (-dir_y, dir_x)
    direita = (dir_y, -dir_x)
    frente = (dir_x, dir_y)

    def colisao(pos):
        return pos in self.cobra or not (0 <= pos[0] < largura and 0 <= pos[1] < altura)

    pos_frente = (cabeca[0] + frente[0], cabeca[1] + frente[1])
    pos_esquerda = (cabeca[0] + esquerda[0], cabeca[1] + esquerda[1])
    pos_direita = (cabeca[0] + direita[0], cabeca[1] + direita[1])

    perigo_frente = int(colisao(pos_frente))
    perigo_esquerda = int(colisao(pos_esquerda))
    perigo_direita = int(colisao(pos_direita))

    # Direção atual
    dir_cima = int(self.direcao == (0, -1))
    dir_baixo = int(self.direcao == (0, 1))
    dir_esquerda = int(self.direcao == (-1, 0))
    dir_direita = int(self.direcao == (1, 0))

    # Comida em relação à cabeça
    comida_x, comida_y = self.comida
    cabeca_x, cabeca_y = cabeca

    comida_esquerda = int(comida_x < cabeca_x)
    comida_direita = int(comida_x > cabeca_x)
    comida_cima = int(comida_y < cabeca_y)
    comida_baixo = int(comida_y > cabeca_y)

    # Estado final como tupla imutável (boa para dicionário da Q-table)
    estado = (
        perigo_frente,
        perigo_direita,
        perigo_esquerda,
        dir_cima,
        dir_baixo,
        dir_esquerda,
        dir_direita,
        comida_esquerda,
        comida_direita,
        comida_cima,
        comida_baixo
    )

    return estado

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

def main(treinar=True):
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