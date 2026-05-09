from search_problem import SearchProblem
from world import World
from numpy import sqrt


GRAVITY_MAX = 1.0
GRAVITY_MIN = 0.5

class PathFinding(SearchProblem):
    """
    Specializzazione del problema di ricerca per la navigazione UAV, che integra la fisica del volo, la gravità e l'aerodinamica.
    """

    def __init__(self, init, goal, world: World, level: int = 1) -> None:
        """
        Inizializza il problema di navigazione definendo lo stato iniziale, l'obiettivo,  i vincoli fisici e il livello.
        """
        self.world = world
        self.level = level
        super().__init__(init, goal)

    def getSuccessors(self, state: tuple[int, int, int]) -> set:
        """
        Genera l'insieme delle transizioni valide dallo stato corrente, applicando i vincoli di mobilità previsti dal livello.
        """
        successors = set()
        x, y, z = state

        valid_dirs = []

        if self.level < 5:
            valid_dirs = [
                (1, 0, 0),
                (-1, 0, 0),
                (0, 1, 0),
                (0, -1, 0),
                (0, 0, 1),
                (0, 0, -1),
            ]

        elif self.level == 5:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        action = (dx, dy, dz)

                        if action != (0, 0, 0):
                            valid_dirs.append(action)

        for dx, dy, dz in valid_dirs:
            next_state = (x + dx, y + dy, z + dz)

            if self.world.is_valid_state(next_state):
                action = (dx, dy, dz)
                successors.add((action, next_state))

        return successors

    def isGoal(self, state: tuple[int, int, int]) -> bool:
        """
        Verifica se lo stato corrente coincide esattamente con le coordinate dell'obiettivo finale.
        """
        return state == self.goal

    def min_cost_xy(self) -> float:
        """
        Calcola il minimo costo energetico per un movimento planare (asse x,y), considerando il vento massimo.
        """
        if self.level < 3:
            return 1.0
        return 1 - self.world.get_max_wind()

    def min_cost_z(self) -> float:
        """
        Calcola il minimo costo energetico per una variazione di quota (asse z), considerando la gravità.
        """
        if self.level == 1:
            return 1.0
        return 0.5

    def get_step_cost(self, state, action, next_state) -> float:
        """
        Calcola il dispendio energetico di un singolo passo considerando gli effetti di distanza, gravità e flussi d'aria.
        """
        dx, dy, dz = action

        cost = sqrt(dx**2 + dy**2 + dz**2)
        distance = sqrt(dx**2 + dy**2 + dz**2)

        if self.level >= 2:
            if dz > 0:
                cost += GRAVITY_MAX
            elif dz < 0:
                cost -= GRAVITY_MIN

        if self.level >= 3:
            wx, wy, wz = self.world.get_wind(state)

            wind_effect = (dx * wx) + (dy * wy) + (dz * wz)
            cost -= wind_effect

        cost = max(0.1 * distance, cost) 
        return cost

    def get_step_distance(self, state, action, next_state) -> float:
        """
        Restituisce la distanza geometrica percorsa tra due stati adiacenti, ignorando l'impatto energetico.
        """
        dx, dy, dz = action
        return sqrt(dx**2 + dy**2 + dz**2)

    def calculate_classical_rth(self) -> tuple[list, float]:
        """
        Calcola la traiettoria e il costo energetico della manovra Return-To-Home standard per scopi comparativi.
        """
        start = self.world.get_start()
        goal = self.world.get_goal()

        if self.world.walls:
            max_wall_z = max(w[2] for w in self.world.walls)
        else:
            max_wall_z = 0

        cruise_h = max(start[2], goal[2], max_wall_z + 1)

        path = [start]
        current = start
        total_cost = 0.0

        while current[2] < cruise_h:
            action = (0, 0, 1)
            next_s = (current[0], current[1], current[2] + 1)
            total_cost += self.get_step_cost(current, action, next_s)
            current = next_s
            path.append(current)

        while current[0] != goal[0] or current[1] != goal[1]:
            step_x = 1 if goal[0] > current[0] else -1 if goal[0] < current[0] else 0
            step_y = 1 if goal[1] > current[1] else -1 if goal[1] < current[1] else 0

            action = (step_x, step_y, 0)
            next_s = (current[0] + step_x, current[1] + step_y, current[2])

            total_cost += self.get_step_cost(current, action, next_s)
            current = next_s
            path.append(current)

        while current[2] > goal[2]:
            action = (0, 0, -1)
            next_s = (current[0], current[1], current[2] - 1)
            total_cost += self.get_step_cost(current, action, next_s)
            current = next_s
            path.append(current)

        return path, total_cost
