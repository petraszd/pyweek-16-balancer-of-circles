import pygame


class MusicManagerDummy(object):
    def play_background_music(self):
        pass

    def play_shoot(self):
        pass

    def play_over(self):
        pass


class MusicManager(object):
    def __init__(self):
        pygame.mixer.music.load('data/music.ogg')
        pygame.mixer.music.set_volume(0.7)
        self.shootfx = pygame.mixer.Sound('data/shoot.wav')
        self.shootfx.set_volume(0.5)

        self.overfx = pygame.mixer.Sound('data/game_over.wav')
        self.overfx.set_volume(0.5)

    def play_background_music(self):
        pygame.mixer.music.play(-1)

    def play_shoot(self):
        self.shootfx.play()

    def play_over(self):
        self.overfx.play()


def init_manager():
    try:
        pygame.mixer.init()
        return MusicManager()
    except Exception as e:
        print "Warning no sound"
        print e
        return MusicManagerDummy()


music_mgr = init_manager()
