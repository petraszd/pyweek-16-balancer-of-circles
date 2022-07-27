from pygame.gfxdraw import vline, hline
from pygame.draw import rect as draw_rect
from pygame.surface import Surface

from boc.config import COLOR_GRID, CELL_SIZE, COLOR_ARENA, COLOR_BACK

class Arena(object):
    def __init__(self, w, h, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.w = w
        self.h = h
        self.half_w = w // 2
        self.half_h = h // 2

        self.color = Surface((w, h))
        self.color.fill(COLOR_ARENA)

    def draw(self, surface, cam):
        self.draw_color(surface, cam)
        self.draw_lines(surface, cam)

    def draw_color(self, surface, cam):
        rect = (cam.x(-self.half_w),
                cam.y(-self.half_h),
                self.w, self.h)
        surface.blit(self.color, rect)

    def draw_lines(self, surface, cam):
        x1, x2 = -self.half_w, self.half_w
        y1, y2 = -self.half_h, self.half_h
        tox = cam.x
        toy = cam.y
        for x in xrange(x1, x2 + 1, CELL_SIZE):
            vline(surface, tox(x), toy(y1), toy(y2), COLOR_GRID)
        for y in xrange(y1, y2 + 1, CELL_SIZE):
            hline(surface, tox(x1), tox(x2), toy(y), COLOR_GRID)

    def draw_limits(self, surface, cam):
        left_rect = (cam.x(-self.half_w - self.screen_w), 0,
                     self.screen_w, self.screen_h)
        right_rect = (cam.x(self.half_w), 0,
                      self.screen_w, self.screen_h)
        top_rect = (0, cam.y(-self.half_h - self.screen_h),
                    self.screen_w, self.screen_h)
        bottom_rect = (0, cam.y(self.half_h),
                       self.screen_w, self.screen_h)

        draw_rect(surface, COLOR_BACK, left_rect)
        draw_rect(surface, COLOR_BACK, right_rect)
        draw_rect(surface, COLOR_BACK, top_rect)
        draw_rect(surface, COLOR_BACK, bottom_rect)
