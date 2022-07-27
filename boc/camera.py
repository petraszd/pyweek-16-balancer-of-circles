class Camera(object):
    def __init__(self, player, screen_center):
        self.screen_center = screen_center
        self.pl = player
        self.dx, self.dy = -self.pl.pos + self.screen_center

    def update(self, dt):
        self.dx, self.dy = -self.pl.pos + self.screen_center

    def x(self, global_x):
        return int(self.dx + global_x)

    def y(self, global_y):
        return int(self.dy + global_y)
