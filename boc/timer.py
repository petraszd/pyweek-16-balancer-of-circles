from boc.config import COLOR_TIMER, TIMER_PADDING

from pygame.font import Font


timer_font = Font(None, 32)


class Timer(object):
    def __init__(self):
        self.miliseconds = 0

    def update(self, dt):
        self.miliseconds += dt

    def get_str(self):
        seconds = self.miliseconds // 1000
        milisec = (self.miliseconds - seconds * 1000) // 100
        return u'{:04d}.{:01d}'.format(seconds, milisec)

    def draw(self, surface):
        text_surface = timer_font.render(self.get_str(), True, COLOR_TIMER)

        x = surface.get_width() - text_surface.get_width() - TIMER_PADDING

        #rect.center = position
        rect = text_surface.get_rect()
        rect.move_ip(x, TIMER_PADDING)
        surface.blit(text_surface, rect)
