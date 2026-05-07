import json

class World(object):
    """
    Modellatore dell'ambiente tridimensionale: gestisce la topografia, le collisioni e il vento.
    """

    def __init__(self, map_filepath: str = None) -> None:
        """
        Inizializza l'ambiente di volo caricando la configurazione topografica dal file specificato.
        """
        self.x_lim = 0
        self.y_lim = 0
        self.z_lim = 0
        self.walls = set()
        self.start = None
        self.goal = None
        self.wind_intensity = 0.0
        self.wind_direction = (0.0, 0.0, 0.0)
        self.stratified_wind = {}
        self.max_wind_intensity = 0.0

        if map_filepath:
            self.load_map(map_filepath)

    def load_map(self, filepath: str) -> None:
        """
        Inizializza l'ambiente e gli ostacoli caricando la topografia da un file JSON.
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Errore: Il file {filepath} non esiste. Mappa non caricata.")
            return
        except json.JSONDecodeError:
            print(f"Errore: Il file {filepath} non è un JSON valido.")
            return

        self.x_lim = data.get("x_lim", 50)
        self.y_lim = data.get("y_lim", 50)
        self.z_lim = data.get("z_lim", 30)

        self.start = tuple(data.get("start", [0, 0, 0]))
        self.goal = tuple(data.get("goal", [self.x_lim - 1, self.y_lim - 1, 0]))
        self.walls = set(tuple(b) for b in data.get("obstacles", []))

    def get_start(self) -> tuple:
        """
        Restituisce la coordinata di partenza (x, y, z).
        """
        return self.start

    def get_goal(self) -> tuple:
        """
        Restituisce la coordinata di arrivo (x, y, z).
        """
        return self.goal

    def is_valid_state(self, state: tuple) -> bool:
        """
        Verifica che la coordinata appartenga ai confini della mappa e non coincida con un ostacolo.
        """
        x, y, z = state

        return (
            0 <= x <= self.x_lim
            and 0 <= y <= self.y_lim
            and 0 <= z <= self.z_lim
            and state not in self.walls
        )


    def set_uniform_wind(self, intensity: float, direction: tuple) -> None:
        """
        Applica un vento uniforme su tutta la mappa in base all'intensità e al versore indicati.
        """
        self.wind_intensity = intensity
        self.max_wind_intensity = intensity

        self._uniform_wind_vector = (
            direction[0] * intensity,
            direction[1] * intensity,
            0.0,
        )

        self.stratified_wind.clear()

    def set_stratified_wind(self, layers: dict) -> None:
        """
        Applica un vento stratificato, assegnando specifici vettori di intensità e direzione in base alla quota Z.
        """
        self.stratified_wind.clear()
        self.wind_intensity = 0.0
        self._uniform_wind_vector = (0.0, 0.0, 0.0)

        current_max = 0.0

        for z, (intensity, direction) in layers.items():
            self.stratified_wind[z] = (
                direction[0] * intensity,
                direction[1] * intensity,
                0.0,
            )

            if intensity > current_max:
                current_max = intensity

        self.max_wind_intensity = current_max

    def get_max_wind(self) -> float:
        """
        Restituisce la massima intensità del vento presente nell'ambiente.
        """
        return self.max_wind_intensity

    def get_wind(self, state: tuple[int, int, int]) -> tuple[float, float, float]:
        """
        Restituisce il vettore vento attivo in una specifica coordinata, valutando l'eventuale stratificazione.
        """
        z = state[2]

        if self.stratified_wind:
            return self.stratified_wind.get(z, (0.0, 0.0, 0.0))

        return self._uniform_wind_vector

    def get_walls_for_plot(self) -> tuple:
        """
        Formatta le coordinate degli ostacoli per consentirne la visualizzazione tridimensionale nel motore grafico.
        """
        if not self.walls:
            return [], [], []

        x_coords = [wall[0] for wall in self.walls]
        y_coords = [wall[1] for wall in self.walls]
        z_coords = [wall[2] for wall in self.walls]

        return x_coords, y_coords, z_coords
