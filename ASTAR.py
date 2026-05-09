from search_algorithm import SearchAlgorithm
from queue import PriorityQueue
from search_algorithm import Node

class AstarNode(Node):
    """
    Estensione del nodo di ricerca ottimizzata per A*, che integra la funzione di valutazione f(n) = g(n) + h(n).
    """

    def __init__(self, state, parent = None, action = None, g = 0, h = 0) -> None:
        """
        Inizializza l'istanza configurando i parametri operativi e le strutture dati di base.
        """
        self.h = h
        super().__init__(state, parent, action, g)
        
    def __lt__(self, other) -> bool:
        """
        Definisce l'ordinamento nella Priority Queue basandosi su f(n) = g(n) + h(n).
        """
        return self.g + self.h < other.g + other.h 
    
class AStar(SearchAlgorithm):
    """
    Motore di ricerca informata che implementa l'algoritmo A* per la determinazione della rotta energeticamente ottima.
    """

    def __init__(self, heuristic = lambda state, goal, problem : 0, view = False, w = 1) -> None:
        """
        Configura l'istanza dell'algoritmo A* impostando la funzione euristica e le opzioni di tracciamento dei nodi.
        """
        self.heuristic = heuristic
        self.w = w
        super().__init__(view)

    def solve(self, problem) -> list:
        """
        Esegue l'algoritmo A* espandendo gli stati per garantire l'ottimalità della soluzione.
        """
        cost = dict()
        frontier = PriorityQueue()
        frontier.put(AstarNode(problem.init))
        cost[problem.init] = 0
        self.reset_expanded()
        while (not frontier.empty()):
            n = frontier.get()
            if n.g == cost[n.state]:
                self.update_expanded(n.state)
                if (problem.isGoal(n.state)):
                    return self.extract_solution(n)
                for a,s in problem.getSuccessors(n.state):
                    step_cost = problem.get_step_cost(n.state, a, s)
                    new_cost = n.g + step_cost
                    if s not in cost or new_cost < cost[s] - 1e-5:
                        cost[s] = new_cost
                        frontier.put(AstarNode(s, n, a, new_cost, self.w * self.heuristic(s, problem.goal, problem)))
        return None