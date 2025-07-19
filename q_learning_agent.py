import random
import pickle
import pickle
    
class QLearningAgent:
    def __init__(self, actions):
        self.q_table = {}
        self.actions = actions
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.999

    def carregar(self, caminho):
        try:
            with open(caminho, 'rb') as f:
                data = pickle.load(f)
                self.q_table = data.get('q_table', {})
                self.epsilon = data.get('epsilon', 1.0)
            print(f"Modelo carregado de {caminho}")
        except FileNotFoundError:
            print(f"Nenhum arquivo encontrado em {caminho}, iniciando do zero.")
            self.q_table = {}
            self.epsilon = 1.0
        except EOFError:
            print(f"Arquivo {caminho} está vazio ou corrompido, iniciando do zero.")
            self.q_table = {}
            self.epsilon = 1.0

    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        self.q_table = {}
        self.actions = actions  # [0, 1, 2] → virar_esquerda, seguir_reto, virar_direita
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)  # exploração
        else:
            qs = [self.get_q(state, a) for a in self.actions]
            max_q = max(qs)
            return self.actions[qs.index(max_q)]  # melhor ação

    def learn(self, state, action, reward, next_state):
        old_q = self.get_q(state, action)
        future_qs = [self.get_q(next_state, a) for a in self.actions]
        max_future_q = max(future_qs)
        new_q = old_q + self.alpha * (reward + self.gamma * max_future_q - old_q)
        self.q_table[(state, action)] = new_q

    def update_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def salvar(self, caminho):
        with open(caminho, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'epsilon': self.epsilon
            }, f)