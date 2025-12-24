class HUD: 
    def __init__(self):
        self.coin_count = 0
        self.game_time = 0
        self.distance = 0
        self.current_level = 1

        self.level_thresholds = {
            1: 10, 
            2: 20, 
            3: 30,
            4: 40,
            5: 50,
            6: 60,
            7: 70
        }  

        self.level_names = {
            1: "Luxúria",
            2: "Gula",
            3: "Avareza",
            4: "Ira",
            5: "Inveja",
            6: "Preguiça",
            7: "orgulho"
        }


        self.timer_active = False

    def start_timer(self):
        self.timer_active = True

    def stop_timer(self):
        self.timer_active = False

    def update_time(self, delta_time):
        if self.timer_active:
            self.game_time += delta_time

    def update_coins(self, amount):
        self.coin_count += amount
        self.check_level_completion()

    def update_distance(self, delta_distance: float):
        self.distance += delta_distance
        print(f"📏 Distância percorrida: {self.distance:.2f}")

    def check_level_completion(self):
        required_coins = self.level_thresholds.get(self.current_level, None)
        if required_coins is None:
            return
        if self.coin_count >= required_coins:
            self.advance_level()

    def advance_level(self):
        self.current_level += 1
        level_name = self.level_names.get(self.current_level, f"Nível {self.current_level}")
        print(f"Avançou para o nível {level_name}!")

    def draw(self):
        """Renderiza a HUD na tela (exemplo textual)."""
        level_name = self.level_names.get(self.current_level, f"Nível {self.current_level}")
        hud_text = (
            f"Moedas: {self.coin_count} | "
            f"Tempo: {self.game_time:.2f}s | "
            f"Distância: {self.distance:.1f}m | "
            f"Pecado: {level_name}"
        )
        print(hud_text)  # substitua por renderização gráfica futuramente
