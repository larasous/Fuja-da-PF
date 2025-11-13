from src.engine.window import Window
from src.ui.lore_screen import LoreScreen

if __name__ == "__main__":
    app = Window()
    app.state = "lore"
    app.show_lore("assets/lore/intro.json", typing_speed=0.05, pause_between_blocks=3.0)
    app.run()