import pygame

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7

    # Música de fundo
    def play_music(self, filepath, loop=True):
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self):
        pygame.mixer.music.stop()

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)

    # Efeitos sonoros
    def load_sound(self, name, filepath):
        self.sounds[name] = pygame.mixer.Sound(filepath)
        self.sounds[name].set_volume(self.sfx_volume)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def set_sfx_volume(self, volume):
        self.sfx_volume = volume
        for sound in self.sounds.values():
            sound.set_volume(volume)