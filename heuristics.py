from numpy import sqrt

def manhattan_energy(start: tuple[int, int, int], goal: tuple[int, int, int], problem) -> float:
    """
    Stima il costo energetico residuo tramite la distanza di Manhattan 3D, ottimale per le esplorazioni a movimenti ortogonali.
    """
    dx = abs(start[0] - goal[0])
    dy = abs(start[1] - goal[1])
    dz = abs(start[2] - goal[2])

    cost_x = dx * problem.min_cost_xy()
    cost_y = dy * problem.min_cost_xy()
    cost_z = dz * problem.min_cost_z()

    return max(0.1 * (dx + dy + dz), cost_x + cost_y + cost_z) 

def euclidean_energy(start: tuple[int ,int, int], goal: tuple[int, int, int], problem) -> float:
    """
    Stima il costo energetico residuo tramite la distanza euclidea, ideale per il livello 5 a 26 direzioni.
    """
    dx = abs(start[0] - goal[0]) 
    dy = abs(start[1] - goal[1]) 
    dz = abs(start[2] - goal[2]) 

    distance = sqrt(dx**2 + dy**2 + dz**2)

    wind_discount = sqrt(dx**2 + dy**2) * (1.0 - problem.min_cost_xy())

    g_discount = 0.0
    if start[2] > goal[2]:
        g_discount = dz * (1.0 - problem.min_cost_z())

    total_cost = distance - wind_discount - g_discount

    return max(0.1 * distance, total_cost)

