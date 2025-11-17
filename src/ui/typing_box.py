import imgui
import time


class TypingBox:
    def __init__(self, text_blocks, typing_speed=0.05, pause_between_blocks=2.5):
        self.text_blocks = text_blocks
        self.typing_speed = typing_speed
        self.pause_between_blocks = pause_between_blocks

        self.start_time = time.time()
        self.finished = False

        # pré-calcular intervalos de tempo
        self.block_timings = []
        total = 0
        for block in text_blocks:
            duration = len(block) * typing_speed + pause_between_blocks
            self.block_timings.append((total, total + duration))
            total += duration

    def update(self):
        now = time.time() - self.start_time
        if now > self.block_timings[-1][1]:
            self.finished = True

    def draw(self, window_width, window_height):
        # janela do lore
        lore_width, lore_height = 900, 200
        center_x = (window_width - lore_width) // 2
        center_y = int(window_height * 0.75)

        imgui.set_next_window_position(center_x, center_y)
        imgui.set_next_window_size(lore_width, lore_height)

        imgui.begin(
            "Lore",
            False,
            imgui.WINDOW_NO_TITLE_BAR
            | imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SCROLLBAR,
        )

        now = time.time() - self.start_time

        for i, (start, end) in enumerate(self.block_timings):
            if start <= now < end:
                block = self.text_blocks[i]
                typing_duration = len(block) * self.typing_speed
                time_into_block = now - start

                if time_into_block < typing_duration:
                    visible_chars = int(time_into_block / self.typing_speed)
                    visible_text = block[:visible_chars]
                else:
                    visible_text = block

                imgui.text_wrapped(visible_text)
                break

        imgui.end()
