import pygame


class AudioManager:
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.6

    def load_sound(self, name, path, volume=None):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(self.sfx_volume if volume is None else volume)
        self.sounds[name] = sound

    def play_sound(self, name):
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def play_music(self, path, loops=-1, volume=None):
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.music_volume if volume is None else volume)
        pygame.mixer.music.play(loops)

    def stop_music(self):
        pygame.mixer.music.stop()

    def pause_music(self):
        pygame.mixer.music.pause()

    def resume_music(self):
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)

    def set_sfx_volume(self, volume):
        self.sfx_volume = volume
        for sound in self.sounds.values():
            sound.set_volume(volume)