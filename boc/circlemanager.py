from pygame.image import load
from pygame.transform import smoothscale


TYPE_C1 = 1
TYPE_C2 = 2
TYPE_SHADOW = 3
NORMAL_TYPES = [TYPE_C1, TYPE_C2]


class CircleImgManager(object):
    def __init__(self):
        self.cache = {}
        self.imgs = {
            TYPE_C1: load('data/c1.png').convert_alpha(),
            TYPE_C2: load('data/c2.png').convert_alpha(),
            TYPE_SHADOW: load('data/shadow.png').convert_alpha(),
        }

    def surface(self, type, dim):
        key = (type, dim)
        if key not in self.cache:
            img = self.imgs[type]
            self.cache[key] = smoothscale(img, (dim, dim))
        return self.cache[key]


mgr = CircleImgManager()
