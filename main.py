import streamlit as st
import time
from world import World
from path_finding import PathFinding
from ASTAR import AStar
from heuristics import manhattan_energy, euclidean_energy
from dashboard_utils import get_user_inputs, create_3d_plot

# Configurazione
st.set_page_config(page_title="E.A.R.T.H. UAV Dashboard", layout="wide")


def build_world(
    map_path,
    level,
    wind_intensity,
    wind_dir,
    stratified_layers,
    start_coord,
    goal_coord,
) -> World:
    """
    Inizializza l'ambiente, configurando la topografia e il vento in base al livello selezionato.
    """
    world = World(map_path)
    world.start = start_coord
    world.goal = goal_coord

    if level == 3:
        world.set_uniform_wind(wind_intensity, wind_dir)
    elif level >= 4:
        layers_dict = {}
        for z in range(world.z_lim + 1):
            if z < 10:
                layer_key = 0
            elif z < 20:
                layer_key = 10
            else:
                layer_key = 20
            layers_dict[z] = stratified_layers[layer_key]
        world.set_stratified_wind(layers_dict)
    return world


def solve_mission(world, level) -> tuple:
    """
    Esegue la simulazione completa della missione, gestendo il calcolo algoritmico e l'analisi delle performance.
    """
    start_time = time.time()
    heuristic = manhattan_energy if level < 5 else euclidean_energy
    problem = PathFinding(world.get_start(), world.get_goal(), world, level=level)
    solver = AStar(heuristic=heuristic, view=True)
    path_actions = solver.solve(problem)

    if not path_actions:
        execution_time = time.time() - start_time
        return (None, 0.0, solver, problem, None, 0.0, 0.0, execution_time, 0.0)

    path_coords = [world.get_start()]
    current = world.get_start()
    energy = 0.0
    distance = 0.0
    for action in path_actions:
        next_state = (
            current[0] + action[0],
            current[1] + action[1],
            current[2] + action[2],
        )
        energy += problem.get_step_cost(current, action, next_state)
        distance += problem.get_step_distance(current, action, next_state)
        current = next_state
        path_coords.append(current)

    rth_path_coords, rth_energy = problem.calculate_classical_rth()
    energy_saved_pct = 0.0
    if rth_energy > 0:  # evita divisione per 0
        energy_saved_pct = (
            (rth_energy - energy) / rth_energy * 100
        )

    execution_time = time.time() - start_time
    return (
        path_coords,
        energy,
        solver,
        problem,
        rth_path_coords,
        rth_energy,
        energy_saved_pct,
        execution_time,
        distance,
    )


def main() -> None:
    """
    Gestisce il flusso dell'applicazione, gli input utente e il rendering dei dati.
    """
    # input dall'utente
    (
        level,
        map_path,
        wind_intensity,
        wind_dir,
        stratified_layers,
        show_expanded,
        show_wind,
        user_start,
        user_goal,
        coords_are_valid,
    ) = get_user_inputs()

    # avviamo i calcoli
    if st.sidebar.button(
        "AVVIA CALCOLO", type="primary", disabled=not coords_are_valid
    ):
        world = build_world(
            map_path,
            level,
            wind_intensity,
            wind_dir,
            stratified_layers,
            user_start,
            user_goal,
        )

        with st.spinner("Calcolo traiettoria"):
            (
                path_coords,
                energy,
                solver,
                problem,
                rth_path_coords,
                rth_energy,
                energy_saved_pct,
                execution_time,
                distance,
            ) = solve_mission(world, level)

        if path_coords is None:
            st.error("Nessun percorso trovato")
            return

        # grafico 3D
        fig = create_3d_plot(
            world,
            path_coords,
            solver,
            show_expanded,
            show_wind,
            level,
            rth_path_coords,
        )
        st.plotly_chart(fig, use_container_width=True)

        # metriche riepilogo
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Energia", f"{energy:.2f} u.e.")
        m2.metric("Distanza", f"{distance:.2f} m")
        m3.metric("Nodi espansi", f"{solver.expanded}")
        m4.metric("Risparmio vs RTH", value=f"{energy_saved_pct:.1f}%")
        m5.metric("Tempo di calcolo", f"{execution_time:.2f} s")

    # Schermata iniziale
    else:
        st.write(
            """
            # E.A.R.T.H. UAV

            **E.A.R.T.H.** (Energy-Aware Return-To-Home) è un simulatore 3D progettato per calcolare la rotta di volo più efficiente per un drone. 
            Il cuore del sistema è l'algoritmo A*, che analizza gli ostacoli, la gravità e il vento per minimizzare 
            il consumo di batteria, confrontando i risultati con il classico volo in linea retta (RTH).

            **Come configurare la missione:**
            1. Scegli il livello di complessità della simulazione e carica la mappa con i relativi ostacoli.
            2. Inserisci le coordinate di partenza e di arrivo.
            3. Nei livelli avanzati, definisci la direzione e l'intensità del vento.
            4. Usa gli interruttori per mostrare i vettori del vento o visualizzare i nodi esplorati dall'algoritmo.
            5. Premi "AVVIA CALCOLO" per iniziare la missione.

            ---
            #### I 5 Livelli di Simulazione

            * **Livello 1:** movimenti ortogonali a 6 direzioni. Il sistema cerca il percorso più breve aggirando gli ostacoli.
            * **Livello 2:** salire di quota richiede più energia, il drone penalizza le ascese e privilegia le traiettorie in discesa.
            * **Livello 3:** viene aggiunto un vento uniforme su tutta la mappa.
            * **Livello 4:** viene aggiunto un vento stratificato su tre altitudini, ogni fascia avrà intensità e direzione diverse.
            * **Livello 5:** vengono permessi spostamenti in diagonale, aumentando le direzioni disponibili a 26.
            """,
        )


if __name__ == "__main__":
    main()
