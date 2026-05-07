class SearchProblem(object):
    """
    Interfaccia astratta che definisce la struttura formale e i vincoli di un problema di ricerca nello spazio degli stati.
    """
    
    def __init__(self, init, goal) -> None:
        """
        Inizializza l'istanza del problema definendo lo stato di partenza e l'obiettivo.
        """
        self.init = init
        self.goal = goal

    def getSuccessors(self, state) -> set:
        """
        Interfaccia astratta: genera e restituisce l'insieme delle transizioni di stato valide a partire dallo stato corrente.
        """
        raise Exception("Not implemented")

    def isGoal(self, state) -> bool:
        """
        Interfaccia astratta: verifica se lo stato fornito soddisfa le condizioni di terminazione.
        """
        raise Exception("Not implemented")

    def get_step_cost(self, state, action, next_state) -> float:
        """Interfaccia astratta: calcola e restituisce il costo energetico di transizione tra due stati adiacenti."""
        raise Exception("Not implemented")