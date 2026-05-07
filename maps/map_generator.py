import json
import random


def save_map(name, obstacles) -> None:
    """
    Salva la configurazione topografica generata in un file JSON compatibile con il simulatore.
    """
    data = {"x_lim": 50, "y_lim": 50, "z_lim": 30, "obstacles": obstacles}

    filename = f"{name}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def build_block(obs_list, x_start, y_start, width, depth, height) -> None:
    """
    Genera gli ostacoli riempiendo la mappa entro i limiti specificati.
    """
    for x in range(x_start, x_start + width):
        for y in range(y_start, y_start + depth):
            for z in range(0, height):
                if 0 <= x < 50 and 0 <= y < 50 and 0 <= z < 30:
                    obs_list.append([x, y, z])


def generate_map() -> None:
    """
    Coordina la generazione della mappa, inserendo ostacoli in base ai parametri configurati.
    """
    obs = []
    for i in range(0, 50, 10):
        for j in range(0, 50, 10):
            h = random.randint(10, 25)

            build_block(obs, i + 1, j + 1, 8, 8, h)

    save_map("random1", obs)


if __name__ == "__main__":
    generate_map()
