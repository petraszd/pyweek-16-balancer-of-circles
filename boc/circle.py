import random
from math import sin, cos, sqrt, pi as PI

from pygame.gfxdraw import aacircle
from pygame.draw import aaline
from pygame.font import Font

from euclid import Vector2

from boc.config import (SHADOW_DELTA, EPSILON, SHADOW_DIVIDER,
                        CIRCLE_MIN_SIZE, CIRCLE_ADDED_RADIUS_DELTA,
                        PL_MAX_CIRCE_RADIUS, CIRCLE_BIG_RADIUS,
                        COLOR_LINES, COLOR_BIG_LINES,
                        CIRCLE_LINE_MULTIPLY, PL_LINE_MULTIPLY,
                        CIRCLE_SHADOW_RADIUS_MULTIPLY, COLOR_TEXT,
                        PL_TEXT_MULTIPLY, CIRCLE_TIMEOUT,
                        CIRCLE_HIT_WALL_MIN_R, COLOR_TEXT_END)
from boc.circlemanager import mgr, TYPE_SHADOW, NORMAL_TYPES
from boc.mixins import RadiusMixin


warning_font = Font(None, 24)


def to_rect(x, y, r):
    return (int(x - r), int(y - r), int(r * 2), int(r * 2))


class Circle(RadiusMixin):
    def __init__(self, pos, dir_, player, rules, radius=None, type_=None,
                 added_radius=None):
        self.pl = player
        self.rules = rules

        self.pos = pos
        self.dir = dir_
        self.speed = self.rules.speed
        self.reset_speed()

        if radius is not None:
            self.radius = radius
            self.added_radius = 0
        elif added_radius is not None:
            self.radius = 1
            self.added_radius = added_radius - 1
        else:
            self.radius = 1
            self.added_radius = random.randint(rules.size_from,
                                               rules.size_to)

        if type_ is None:
            self.type = NORMAL_TYPES[random.randint(0, len(NORMAL_TYPES) - 1)]
        else:
            self.type = type_

        self.color_img = None
        self.shadow_img = None
        self.update_imgs()

        self.to_generate = []
        self.is_delete = False
        self.is_bullet = False
        self.is_end = False

        self.timer = None

    @property
    def sradius(self):
        return self.radius * CIRCLE_SHADOW_RADIUS_MULTIPLY

    def update(self, dt):
        self.pos = self.pos + self.dir * self.speed
        if self.is_big():
            self.update_timer(dt)
        if self.added_radius:
            self.update_added_radius()

    def update_added_radius(self):
        delta = min(self.added_radius, CIRCLE_ADDED_RADIUS_DELTA)

        self.radius += delta
        self.update_imgs()

        self.added_radius -= CIRCLE_ADDED_RADIUS_DELTA
        if self.added_radius <= 0.0:
            self.added_radius = 0

    def update_timer(self, dt):
        if self.timer is None:
            self.timer = CIRCLE_TIMEOUT
            return
        if self.timer == 0:
            self.is_end = True
            return

        self.timer -= dt
        if self.timer < 0:
            self.timer = 0

    def pullout_from(self, circle):
        delta = (self.pos - circle.pos).magnitude()
        minus_amount = (self.radius + circle.radius - delta) / 2.0

        if circle.radius - minus_amount < CIRCLE_MIN_SIZE:
            add_amount = self.area_to_amount(
                circle.amount_to_area(circle.radius))
            circle.radius = 0
            circle.is_delete = True
        else:
            add_amount = self.area_to_amount(
                circle.amount_to_area(minus_amount))
            circle.radius -= minus_amount
            circle.update_imgs()

        self.radius += add_amount
        self.update_imgs()

    def hit_circle(self, other):
        if self.is_collision(other):
            self.is_delete = True
            if self.type == other.type:
                other.added_radius += other.area_to_amount(
                    other.amount_to_area(self.radius))
            else:  # Same Type
                other.on_hit()

    def bounce_circle(self, other):
        if self.is_collision(other):
            if self.type == other.type:
                if other.radius > self.radius:
                    other.pullout_from(self)
                else:
                    self.pullout_from(other)
            else:
                self.collide_with_circle(other)

    def collide_with_circle(self, circle):
        a = -self.dir
        b = circle.dir

        middle = ((a + b) / 2.0).normalized()
        self.dir = -(-self.dir).reflect(middle).normalized()
        circle.dir = -(-circle.dir).reflect(middle).normalized()

        if random.random() < 0.5:  # Random moving prevents
                                   # stucking between walls
            self.move_away_from(circle)
        else:
            circle.move_away_from(self)

    def bounce_wall(self, arena):
        x, y = self.pos
        r = self.radius
        x1, y1 = -arena.half_w, -arena.half_h
        x2, y2 = arena.half_w, arena.half_h

        if y + r > y2:
            self.pos.y = y2 - r - EPSILON
            self.dir = self.dir.reflect(Vector2(0, -1))
            self.on_hit_wall()
        elif y - r < y1:
            self.pos.y = y1 + r + EPSILON
            self.dir = self.dir.reflect(Vector2(0, 1))
            self.on_hit_wall()
        elif x + r > x2:
            self.pos.x = x2 - r - EPSILON
            self.dir = self.dir.reflect(Vector2(-1, 0))
            self.on_hit_wall()
        elif x - r < x1:
            self.pos.x = x1 + r + EPSILON
            self.dir = self.dir.reflect(Vector2(1, 0))
            self.on_hit_wall()

    def out_of_bounds(self, arena):
        x, y = self.pos
        r = self.radius
        x1, y1 = -arena.half_w, -arena.half_h
        x2, y2 = arena.half_w, arena.half_h

        if y - r - EPSILON > y2:
            self.is_delete = True
            return
        if y + r + EPSILON < y1:
            self.is_delete = True
            return
        if x - r - EPSILON > x2:
            self.is_delete = True
            return
        if x + r + EPSILON < x1:
            self.is_delete = True
            return

    def update_imgs(self):
        dim = int(self.radius * 2)
        self.color_img = mgr.surface(self.type, dim)

        dim = int(self.sradius * 2)
        self.shadow_img = mgr.surface(TYPE_SHADOW, dim)

    def is_small(self):
        return self.radius < PL_MAX_CIRCE_RADIUS

    def is_big(self):
        return self.radius > CIRCLE_BIG_RADIUS

    def draw_figure(self, surface, cam):
        x, y = self.pos
        r = self.radius
        surface.blit(self.color_img, to_rect(cam.x(x), cam.y(y), r))

    def get_direction_from_pl(self):
        if self.pos.y > self.pl.pos.y:
            return (self.pl.pos - self.pos).normalized()
        else:
            return -(self.pos - self.pl.pos).normalized()

    def draw_lines(self, surface, cam):
        if self.is_small():
            return
        if self.is_big():
            self.draw_lines_for_big(surface, cam)
        else:
            self.draw_lines_for_medium(surface, cam)

    def draw_lines_for_medium(self, surface, cam):
        x, y = self.pos
        r = int(self.radius * CIRCLE_LINE_MULTIPLY)
        aacircle(surface, cam.x(x) - 1, cam.y(y) + 1, r, COLOR_LINES)

    def draw_lines_for_big(self, surface, cam):
        r = int(self.radius * CIRCLE_LINE_MULTIPLY)

        conn = self.get_direction_from_pl()
        ax, ay = self.pos + conn * r

        pr = self.pl.radius * PL_LINE_MULTIPLY
        bx, by = self.pl.pos - conn * pr
        a = (cam.x(ax), cam.y(ay))
        b = (cam.x(bx), cam.y(by))
        aaline(surface, COLOR_BIG_LINES, a, b, True)
        aacircle(surface,
                 cam.x(self.pl.pos.x), cam.y(self.pl.pos.y),
                 int(pr), COLOR_BIG_LINES)

        x, y = self.pos
        aacircle(surface, cam.x(x) - 1, cam.y(y) + 1, r, COLOR_BIG_LINES)

        tx, ty = self.pl.pos - conn * (self.pl.radius * PL_TEXT_MULTIPLY)
        self.draw_text(surface, (cam.x(tx), cam.y(ty)))

    def draw_text(self, surface, position):
        if self.timer is None:
            return

        seconds = self.timer // 1000
        milisec = (self.timer - seconds * 1000) // 100

        if self.timer == 0:
            color = COLOR_TEXT_END
        else:
            color = COLOR_TEXT

        text = u'{:02d}.{:1d}s'.format(seconds, milisec)
        text_surface = warning_font.render(text, True, color)
        rect = text_surface.get_rect()
        rect.center = position
        surface.blit(text_surface, rect)

    def draw_shadow(self, surface, cam):
        sh_dir = self.pos - self.pl.pos
        delta = sh_dir.magnitude()
        sh_dir.normalize()
        r = self.sradius
        x, y = (self.pos +
                sh_dir * (delta / float(SHADOW_DIVIDER)) * SHADOW_DELTA)

        surface.blit(self.shadow_img, to_rect(cam.x(x), cam.y(y), r))

    def amount_to_area(self, amount):
        small_r = self.radius - amount
        return PI * (self.radius ** 2) - PI * (small_r ** 2)

    def area_to_amount(self, area):
        big_area = PI * (self.radius ** 2) + area
        return max(sqrt(max(big_area / PI, 0.0)) - self.radius, 0.0)

    def on_hit(self):
        self.to_generate = []

        if self.radius < CIRCLE_MIN_SIZE * 2:
            self.dir.x += (random.random() - 0.5) * 0.4
            self.dir.y += (random.random() - 0.5) * 0.4
            self.dir.normalize()
            return

        # Yay -- magic numbers. Yay!
        r1 = 0.4 * self.radius
        r2_min = 0.8 * self.radius

        if self.is_small():
            n = 3
        elif self.is_big():
            n = 7
        else:
            n = 5

        step = (2.0 * PI) / n
        for i in xrange(n):
            angle = i * step
            r2 = r2_min + 0.8 * random.random()
            direction = Vector2(cos(angle), sin(angle))
            self.to_generate.append(Circle(pos=self.pos + direction * r2,
                                           dir_=direction,
                                           player=self.pl,
                                           rules=self.rules,
                                           radius=max(r1, CIRCLE_MIN_SIZE),
                                           type_=self.type))

        self.is_delete = True

    def on_hit_wall(self):
        if self.radius < CIRCLE_HIT_WALL_MIN_R:
            self.is_delete = True
        self.reset_speed()

    def reset_speed(self):
        self.speed = self.rules.speed + (random.random() - 0.5) * 0.2
