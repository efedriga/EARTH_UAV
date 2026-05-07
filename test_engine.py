import os
from world import World
from path_finding import PathFinding
from ASTAR import AStar
from heuristics import manhattan_energy, euclidean_energy


def run_tests():
    """
    Esegue e visualizza una serie di test per valutare l'efficacia dell'algoritmo A* con diverse condizioni di vento e livelli di complessità.
    """
    map_path = os.path.join("maps", "map_test.json")
    world = World(map_path)

    tests = [
        (1, "Base", 0.0, (0, 0), None),
        (2, "Gravità", 0.0, (0, 0), None),
        (3, "Vento Favorevole (sud-est 0,8)", 0.8, (0.707, -0.707), None),
        (3, "Vento Contrario (nord-ovest 0,8)", 0.8, (-0.707, 0.707), None),
        (3, "Vento Nord 0,8)", 0.8, (1, 0), None),
        (
            4,
            "Vento stratificato: [0-2] est 0,2 | [3-5] ovest 0,9",
            0.0,
            (0, 0),
            {
                **{z: (0.2, (1, 0)) for z in range(0, 10)},
                **{z: (0.2, (1, 0)) for z in range(10, 20)},
                **{z: (0.2, (1, 0)) for z in range(20, 31)},
            },
        ),
        (5, "26 Dir, no vento", 0.0, (0, 0), None),
    ]

    print("TEST:")

    for level, description, wind_intensity, wind_direction, stratified_layers in tests:
        # vento
        if stratified_layers is not None:
            world.set_stratified_wind(stratified_layers)
        else:
            world.set_uniform_wind(wind_intensity, wind_direction)

        # algoritmo ed euristica
        problem = PathFinding(world.start, world.goal, world, level=level)
        if level == 5:
            heuristic = euclidean_energy
        else:
            heuristic = manhattan_energy
        solver = AStar(heuristic=heuristic)
        path = solver.solve(problem)

        # calcolo costi
        current_state = world.start
        total_energy = 0.0
        total_distance = 0.0

        for action in path:
            next_state = (
                current_state[0] + action[0],
                current_state[1] + action[1],
                current_state[2] + action[2],
            )

            total_energy += problem.get_step_cost(current_state, action, next_state)
            total_distance += problem.get_step_distance(
                current_state, action, next_state
            )

            current_state = next_state

        # confronto con RTH
        rth_path, rth_energy = problem.calculate_classical_rth()
        if rth_energy > 0:
            savings = ((rth_energy - total_energy) / rth_energy) * 100
        else:
            savings = 0.0

        # output
        print(f"Livello {level} | {description}")
        print(f"- Spostamenti totali : {len(path)}")
        print(f"- Distanza geometrica: {total_distance:.2f} m")
        print(
            f"- Energia consumata  : {total_energy:.2f} u.e. (vs RTH: {rth_energy:.2f} u.e.)"
        )
        print(f"- Risparmio RTH      : {savings:.1f} %")
        print(f"- Nodi esplorati (A*): {solver.expanded}")
        print("-------------------------------")


if __name__ == "__main__":
    run_tests()
