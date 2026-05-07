import os
import math
import streamlit as st
import plotly.graph_objects as go
from world import World


# IMPORTAZIONI E COSTANTI

WIND_MAP = {
    "N": (0, 1),
    "NE": (0.707, 0.707),
    "E": (1, 0),
    "SE": (0.707, -0.707),
    "S": (0, -1),
    "SW": (-0.707, -0.707),
    "W": (-1, 0),
    "NW": (-0.707, 0.707),
}

LEVEL_OPTIONS = {
    1: "Livello 1",
    2: "Livello 2",
    3: "Livello 3",
    4: "Livello 4",
    5: "Livello 5",
}

MAP_FOLDER = "maps"


# INTERFACCIA UTENTE
def get_user_inputs() -> tuple:
    """
    Configura il pannello di controllo per l'acquisizione dei parametri fisici, ambientali e di visualizzazione.
    """
    st.sidebar.write("## Configurazione missione")
    st.sidebar.write("")

    # Selezione Livello
    selected_level = st.sidebar.selectbox(
        "Livello di complessità", options=list(LEVEL_OPTIONS.values())
    )
    level = None
    for k, v in LEVEL_OPTIONS.items():
        if v == selected_level:
            level = k
            break
    if level == 1:
        st.sidebar.success("Modalità base")
    if level == 2:
        st.sidebar.success("Gravità attiva")
    if level == 3:
        st.sidebar.success("Vento attivo")
    if level == 4:
        st.sidebar.success("Vento stratificato attivo")
    if level == 5:
        st.sidebar.success("Movimenti diagonali attivi")

    # Selezione Mappa
    if not os.path.exists(MAP_FOLDER):
        os.makedirs(MAP_FOLDER)

    maps_dict = {}

    for f in os.listdir(MAP_FOLDER):
        if f.endswith(".json"):
            clean_name = f.replace(".json", "")
            maps_dict[clean_name] = f

    maps_dict = dict(sorted(maps_dict.items()))

    user_choice = st.sidebar.selectbox("Scegli mappa", list(maps_dict.keys()))
    selected_map = maps_dict[user_choice]
    map_path = os.path.join(MAP_FOLDER, selected_map)

    # Coordinate Start e Goal
    temp_world = World(map_path)

    st.sidebar.markdown("---")

    # start
    st.sidebar.write("**Partenza**")
    c1, c2, c3 = st.sidebar.columns(3)
    sx = c1.number_input(
        "X",
        min_value=0,
        max_value=temp_world.x_lim,
        value=temp_world.start[0],
        key="sx",
    )
    sy = c2.number_input(
        "Y",
        min_value=0,
        max_value=temp_world.y_lim,
        value=temp_world.start[1],
        key="sy",
    )
    sz = c3.number_input(
        "Z",
        min_value=0,
        max_value=temp_world.z_lim,
        value=temp_world.start[2],
        key="sz",
    )
    user_start = (sx, sy, sz)

    valid_start = temp_world.is_valid_state(user_start)
    if not valid_start:
        st.sidebar.error("Posizione Start non valida")

        # goal
    st.sidebar.write("**Arrivo**")
    c4, c5, c6 = st.sidebar.columns(3)
    gx = c4.number_input(
        "X", min_value=0, max_value=temp_world.x_lim, value=temp_world.goal[0], key="gx"
    )
    gy = c5.number_input(
        "Y", min_value=0, max_value=temp_world.y_lim, value=temp_world.goal[1], key="gy"
    )
    gz = c6.number_input(
        "Z", min_value=0, max_value=temp_world.z_lim, value=temp_world.goal[2], key="gz"
    )
    user_goal = (gx, gy, gz)

    valid_goal = temp_world.is_valid_state(user_goal)
    if not valid_goal:
        st.sidebar.error("Posizione Goal non valida")

    start_is_goal = user_start == user_goal
    if start_is_goal:
        st.sidebar.error("Start e Goal coincidono")

    coords_are_valid = (valid_start and valid_goal) and not start_is_goal

    # Parametri Vento
    wind_intensity = 0.0
    wind_dir = (0.0, 0.0)
    stratified_layers = {}

    if level == 3:
        st.sidebar.subheader("Vento Uniforme")
        intensity_slider = st.sidebar.slider("Intensità", 0, 10, 5, step=1)
        wind_intensity = intensity_slider / 10.0
        dir_key = st.sidebar.selectbox(
            "Direzione", options=list(WIND_MAP.keys()), index=0
        )
        wind_dir = WIND_MAP[dir_key]

    elif level >= 4:
        st.sidebar.subheader("Venti Stratificati")
        for z_band in [0, 10, 20]:
            with st.sidebar.expander(f"Quota {z_band}-{z_band + 10}"):
                intensity_slider = st.slider(
                    f"Intensità:",
                    0,
                    10,
                    5,
                    step=1,
                    key=f"i{z_band}",
                )
                direction = st.selectbox(
                    f"Direzione:",
                    options=list(WIND_MAP.keys()),
                    key=f"d{z_band}",
                )
            stratified_layers[z_band] = (
                intensity_slider / 10.0,
                WIND_MAP[direction],
            )

    st.sidebar.markdown("---")
    show_expanded = st.sidebar.toggle("Mostra espansione A*", value=True)
    show_wind = st.sidebar.toggle("Mostra Vettori Vento", value=True)

    return (
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
    )


# MOTORE GRAFICO
def create_3d_plot(
    world,
    path_coords,
    solver,
    show_expanded,
    show_wind,
    level,
    rth_path_coords=None,
) -> go.Figure:
    """
    Crea il grafico 3D con Plotly, renderizzando ostacoli, flussi del vento, nodi esplorati e traiettorie calcolate.
    """
    fig = go.Figure()

    # Bussola
    fig.add_trace(
        go.Scatter3d(
            x=[25, 25, 55, -5],
            y=[55, -5, 25, 25],
            z=[15, 15, 15, 15],
            mode="text",
            text=["N", "S", "E", "W"],
            textfont=dict(size=16, color="white", family="Arial Black"),
            name="Orientamento",
            hoverinfo="none",
        )
    )

    # Ostacoli
    ox, oy, oz = world.get_walls_for_plot()
    fig.add_trace(
        go.Scatter3d(
            x=ox,
            y=oy,
            z=oz,
            mode="markers",
            marker=dict(size=5, color="grey", symbol="square"),
            name="Ostacoli",
        )
    )

    # Percorso RTH classico
    if rth_path_coords:
        rpx, rpy, rpz = zip(*rth_path_coords)
        fig.add_trace(
            go.Scatter3d(
                x=rpx,
                y=rpy,
                z=rpz,
                mode="lines",
                line=dict(color="purple", width=3, dash="dash"),
                name="RTH Classico",
            )
        )

    # Percorso A*
    px, py, pz = [], [], []
    for coord in path_coords:
        px.append(coord[0])
        py.append(coord[1])
        pz.append(coord[2])

    fig.add_trace(
        go.Scatter3d(
            x=px,
            y=py,
            z=pz,
            mode="lines",
            line=dict(color="yellow", width=5),
            name="Percorso A*",
        )
    )

    # Vento
    vx, vy, vz, wx, wy, wz, real_intensity = [], [], [], [], [], [], []
    if level >= 3:
        for z_v in range(5, world.z_lim + 1, 10):
            for y_v in range(5, world.y_lim + 1, 10):
                for x_v in range(5, world.x_lim + 1, 10):
                    w_vec = world.get_wind((x_v, y_v, z_v))
                    if abs(w_vec[0]) > 0 or abs(w_vec[1]) > 0 or abs(w_vec[2]) > 0:
                        vx.append(x_v)
                        vy.append(y_v)
                        vz.append(z_v)
                        wx.append(w_vec[0])
                        wy.append(w_vec[1])
                        wz.append(w_vec[2])
                        real_intensity.append(
                            math.sqrt(w_vec[0] ** 2 + w_vec[1] ** 2 + w_vec[2] ** 2)
                        )

    if not vx:
        vx, vy, vz = [0], [0], [0]
        wx, wy, wz = [0.0], [0.0], [0.0]
        real_intensity = [0.0]

    fig.add_trace(
        go.Cone(
            x=vx,
            y=vy,
            z=vz,
            u=wx,
            v=wy,
            w=wz,
            sizemode="scaled",
            sizeref=0.2,
            anchor="tip",
            showscale=False,
            colorscale="Blues",
            opacity=0.4,
            name="Flusso Vento",
            visible=show_wind,
            customdata=real_intensity,
            hovertemplate="Intensità: %{real_intensity:.2f}<extra></extra>",
        )
    )

    # Nodi Espansi
    ex, ey, ez = [], [], []
    for nodo in solver.expanded_sequence:
        ex.append(nodo[0])
        ey.append(nodo[1])
        ez.append(nodo[2])

    fig.add_trace(
        go.Scatter3d(
            x=ex if show_expanded else [],
            y=ey if show_expanded else [],
            z=ez if show_expanded else [],
            mode="markers",
            marker=dict(size=1.5, color="orange", opacity=0.4),
            name="Analisi A*",
            visible=show_expanded,
        )
    )

    # Start
    fig.add_trace(
        go.Scatter3d(
            x=[px[0]],
            y=[py[0]],
            z=[pz[0]],
            mode="markers",
            marker=dict(size=5, color="#00ffb3", symbol="square"),
            name="Start",
        )
    )

    # Goal
    fig.add_trace(
        go.Scatter3d(
            x=[px[-1]],
            y=[py[-1]],
            z=[pz[-1]],
            mode="markers",
            marker=dict(size=5, color="#ff008c", symbol="square"),
            name="Goal",
        )
    )

    # Drone
    fig.add_trace(
        go.Scatter3d(
            x=[px[0]],
            y=[py[0]],
            z=[pz[0]],
            mode="markers",
            marker=dict(size=5, color="#00ff4c", symbol="square"),
            name="Drone",
        )
    )

    # Animazione
    frames = []
    num_steps = len(px)
    num_expanded = len(ex)

    # espansione nodi
    if show_expanded and num_expanded > 0:
        anim_steps = min(200, num_expanded)
        for i in range(anim_steps):
            idx = int((i + 1) / anim_steps * num_expanded)
            frames.append(
                go.Frame(
                    data=[
                        go.Scatter3d(x=ex[:idx], y=ey[:idx], z=ez[:idx]),
                        go.Scatter3d(x=[px[0]], y=[py[0]], z=[pz[0]]),
                    ],
                    traces=[5, 8],
                    name=f"exp_{i}",
                )
            )

        # movimento drone
    for i in range(num_steps):
        frames.append(
            go.Frame(
                data=[
                    go.Scatter3d(x=ex, y=ey, z=ez)
                    if show_expanded
                    else go.Scatter3d(x=[], y=[], z=[]),
                    go.Scatter3d(x=[px[i]], y=[py[i]], z=[pz[i]]),
                ],
                traces=[5, 8],
                name=f"mov_{i}",
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis=dict(
                range=[-5, 55],
                visible=False,
            ),
            yaxis=dict(
                range=[-5, 55],
                visible=False,
            ),
            zaxis=dict(
                range=[0, 30],
                showgrid=True,
                zeroline=False,
                showbackground=False,
                visible=True,
            ),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=0.6),
        ),
        updatemenus=[
            {
                "type": "buttons",
                "direction": "right",
                "showactive": False,
                "x": 0.0,
                "y": 0.0,
                "xanchor": "left",
                "yanchor": "bottom",
                "buttons": [
                    {
                        "args": [
                            None,
                            {
                                "frame": {"duration": 25, "redraw": True},
                                "fromcurrent": True,
                            },
                        ],
                        "label": "Play",
                        "method": "animate",
                    },
                    {
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                            },
                        ],
                        "label": "Pausa",
                        "method": "animate",
                    },
                ],
            }
        ],
        template="plotly_dark",
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig.frames = frames

    return fig
