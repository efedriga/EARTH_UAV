import search_problem as SearchProblem

class Node:
    """
    Struttura dati fondamentale per la rappresentazione di un nodo all'interno dell'albero di ricerca.
    """
    
    def __init__(self, state, parent = None, action = None, g = 0) -> None:
        """
        Inizializza il nodo di ricerca memorizzando lo stato, il genitore, l'azione e il costo g(n).
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        
class SearchAlgorithm:
    """
    Classe base per l'implementazione di algoritmi di ricerca, dotata di strumenti per il monitoraggio delle performance.
    """

    def __init__(self, view = False) -> None:
        """
        Inizializza le strutture dati per il tracciamento dei nodi esplorati.
        """
        self.expanded = 0
        self.expanded_states = set()
        self.expanded_sequence = []
        self.view = view

    def solve(self, problem : SearchProblem) -> list:
        """
        Interfaccia astratta: definisce la firma del motore di ricerca che le classi derivate devono implementare.
        """
        raise Exception("Not implemented")
    
    def update_expanded(self, state) -> None:
        """
        Incrementa il contatore dei nodi esplorati e memorizza la sequenza degli stati visitati
        """
        if (self.view):
            self.expanded_states.add(state)
            self.expanded_sequence.append(state)
        self.expanded += 1

    def reset_expanded(self) -> None:
        """
        Azzera la memoria e il contatore dei nodi espansi.
        """
        if (self.view):
            self.expanded_states = set()
            self.expanded_sequence = []
        self.expanded = 0
        
    def extract_solution(self, node) -> list:
        """
        Ricostruisce la sequenza delle azioni ottimali risalendo la catena dei nodi genitori fino allo stato iniziale.
        """
        sol = list()
        while (node.parent is not None):
            sol.insert(0,node.action)
            node = node.parent
        return sol

