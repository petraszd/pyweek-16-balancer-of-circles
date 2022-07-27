import random
from math import atan2, degrees

from pygame.image import load
from pygame.transform import rotozoom

from euclid import Vector2

from boc.mixins import RadiusMixin
from boc.music import music_mgr
from boc.config import (PL_IMG_DIM, PL_SPEED, PL_RADIUS, PL_BOUNCE_SPEED,
                        PL_BOUNCE_STEP, PL_AFTER_BOUNCE_STEP,
                        BULLET_SPEED)


HALF = PL_IMG_DIM / 2


PL_IMG = load('data/pl.png').convert_alpha()
PL_S_IMG = load('data/pl_s.png').convert_alpha()

PL_CENTER = PL_IMG.get_rect().center
PL_S_CENTER = PL_S_IMG.get_rect().center


STATE_KEYBOARD = 1
STATE_BOUNCE = 2
STATE_AFTER_BOUNCE = 3


def small_rand():
    return (random.random() - 0.5) * 0.3


class Player(RadiusMixin):
    def __init__(self, pos, screen_center):
        self.screen_center = screen_center
        self.pos = pos
        self.radius = PL_RADIUS

        self.bounce_dir = None
        self.bounce_counter = 0

        self.state = STATE_KEYBOARD
        self.next_state = None

        # Moving
        self.states = {
            STATE_KEYBOARD: self.update_keyboard_position,
            STATE_BOUNCE: self.update_bounce_position,
            STATE_AFTER_BOUNCE: self.update_after_bounce_position
        }

        # Rendering
        self.img = PL_IMG
        self.s_img = PL_S_IMG

        # Shooting
        self.mouse_pos = pos
        self.circle = None

        # Keyboard moving
        self.left = 0
        self.right = 0
        self.up = 0
        self.down = 0

    def bounce_wall(self, arena):
        x, y = self.pos
        x1, y1 = -arena.half_w, -arena.half_h
        x2, y2 = arena.half_w, arena.half_h

        if y + self.radius > y2:
            self.bounce(Vector2(small_rand(), -1 + small_rand()))
        elif y - self.radius < y1:
            self.bounce(Vector2(small_rand(), 1 + small_rand()))
        elif x + self.radius > x2:
            self.bounce(Vector2(-1 + small_rand(), small_rand()))
        elif x - self.radius < x1:
            self.bounce(Vector2(1 + small_rand(), small_rand()))

    def bounce_circle(self, circle):
        if self.is_collision(circle):
            is_small = circle.is_small()

            if self.circle is None and is_small:
                self.catch_circle(circle)
                return
            direction = circle.dir.copy() + (small_rand(), small_rand())
            circle.dir = -circle.dir + (small_rand(), small_rand())
            circle.dir.normalize()

            if not is_small:
                self.bounce(direction)
                circle.move_away_from(self)
                return

            if random.random() < 0.5:
                self.move_away_from(circle)
            else:
                circle.move_away_from(self)

    def bounce(self, direction):
        self.bounce_dir = direction.normalized()
        self.state = STATE_BOUNCE
        self.bounce_counter = PL_BOUNCE_STEP
        self.next_state = STATE_KEYBOARD

    def draw_shadow(self, surface, cam):
        rect = self.s_img.get_rect(center=PL_CENTER)
        x, y = self.pos - (HALF, HALF)
        rect.move_ip((cam.x(x), cam.y(y)))
        surface.blit(self.s_img, rect)

    def draw_figure(self, surface, cam):
        if self.circle:
            self.circle.draw_figure(surface, cam)

        rect = self.img.get_rect(center=PL_CENTER)
        x, y = self.pos - (HALF, HALF)
        rect.move_ip((cam.x(x), cam.y(y)))
        surface.blit(self.img, rect)

    def update(self, dt):
        self.states[self.state]()
        self.update_rotation()
        self.update_circle()

    def update_keyboard_position(self):
        direction = Vector2()
        if self.left:
            direction -= Vector2(1, 0)
        if self.right:
            direction += Vector2(1, 0)
        if self.down:
            direction += Vector2(0, 1)
        if self.up:
            direction -= Vector2(0, 1)
        direction.normalize()

        self.pos += direction * PL_SPEED

    def update_bounce_position(self):
        self.pos += self.bounce_dir * PL_BOUNCE_SPEED
        self.bounce_counter -= 1
        if self.bounce_counter < 0:
            self.bounce_counter = PL_AFTER_BOUNCE_STEP
            self.state = STATE_AFTER_BOUNCE

    def update_after_bounce_position(self):
        self.bounce_counter -= 1
        if self.bounce_counter < 0:
            self.state = self.next_state

    def update_rotation(self):
        x, y = self.screen_center - self.mouse_pos
        angle = degrees(atan2(x, y))
        self.img = rotozoom(PL_IMG, angle, 1.0)
        self.s_img = rotozoom(PL_S_IMG, angle, 1.0)

    def update_circle(self):
        if self.circle:
            self.circle.pos = self.pos * 0.6 + self.circle.pos * 0.4

    def catch_circle(self, circle):
        self.circle = circle
        self.circle.is_delete = True

    # Mouse events
    def on_mouse_move(self, mouse_pos):
        self.mouse_pos = mouse_pos

    def on_mouse_down(self, mouse_pos):
        if not self.circle:
            return

        self.circle.is_delete = False
        self.circle.is_bullet = True
        self.circle.timer = None
        self.circle.speed = BULLET_SPEED
        self.circle.dir = (mouse_pos - self.screen_center).normalized()

        music_mgr.play_shoot()

    # Keyboard events
    def on_left(self, on=1):
        self.left = on

    def on_right(self, on=1):
        self.right = on

    def on_up(self, on=1):
        self.up = on

    def on_down(self, on=1):
        self.down = on
