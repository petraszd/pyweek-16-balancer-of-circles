import sys
from random import randint, random

import pygame

from euclid import Vector2

from boc.config import (FPS, COLOR_BACK, CIRCLE_MIN_DISTANCE_FROM_PL,
                        GAME_INIT_CIRCLES, ARENA_W, ARENA_H)

from boc.player import Player
from boc.circle import Circle
from boc.camera import Camera
from boc.arena import Arena
from boc.timer import Timer
from boc.rules import Rules
from boc.music import music_mgr
from boc.events import (EVENT_RULE_STEPUP,
                        EVENT_GEN_CIRCLE,
                        EVENT_ALLOW_RESTART)


end_time_font = pygame.font.Font('data/venus_rising.ttf', 32)


class Game(object):
    def __init__(self, screen):
        self.start_scene_img = (pygame.image.load('data/start_scene.png')
                                .convert_alpha())
        self.end_scene_img = (pygame.image.load('data/end_scene.png')
                              .convert_alpha())

        self.screen = screen

        w, h = self.screen.get_size()
        self.screen_center = Vector2(w / 2.0, h / 2.0)

    def init_game_objects(self):
        w, h = self.screen.get_size()
        self.rules = Rules()

        self.pl = Player(Vector2(0, 0), self.screen_center)
        self.camera = Camera(self.pl, self.screen_center)

        self.arena = Arena(ARENA_W, ARENA_H, w, h)

        self.circles = []
        self.bullets = []
        self.init_circles()
        self.end_circle = None

        self.timer = Timer()

    def init_circles(self):
        for i in xrange(GAME_INIT_CIRCLES):
            self.create_circle()

    def create_circle(self):
        for x in xrange(20):
            x = randint(-self.arena.half_w, self.arena.half_w)
            y = randint(-self.arena.half_h, self.arena.half_h)
            pos = Vector2(x, y)
            min_squared = CIRCLE_MIN_DISTANCE_FROM_PL ** 2
            if (pos - self.pl.pos).magnitude_squared() > min_squared:
                continue
        self.circles.append(Circle(
            pos=pos,
            rules=self.rules,
            dir_=Vector2(random() - 0.5, random() - 0.5).normalized(),
            player=self.pl
        ))

    def run(self):
        scene = self.start_scene
        #scene = self.game_scene
        while True:
            scene = scene()

    def start_scene(self):
        # This method is ugly and I know it
        clock = pygame.time.Clock()

        w, h = self.screen.get_size()
        rect = self.start_scene_img.get_rect()
        imgw, imgh = self.start_scene_img.get_size()
        rect.move_ip((w - imgw) / 2, (h - imgh) / 2)
        # pl and camera are needed by arena. They are not used
        # and DO NOT CALL update on them
        pl = Player(Vector2(0, 0), self.screen_center)
        camera = Camera(pl, self.screen_center)

        arena = Arena(ARENA_W, ARENA_H, w, h)

        while True:
            clock.tick(FPS)
            for event in pygame.event.get():
                etype = event.type
                if etype is pygame.KEYDOWN:
                    k = event.key
                    if k in [pygame.K_ESCAPE, pygame.K_q]:
                        sys.exit()
                    else:
                        return self.game_scene
                elif etype is pygame.QUIT:
                    sys.exit()
                elif etype is pygame.MOUSEBUTTONDOWN:
                    return self.game_scene
            self.screen.fill(COLOR_BACK)
            arena.draw(self.screen, camera)

            self.screen.blit(self.start_scene_img, rect)

            pygame.display.flip()
        return self.end_scene

    def end_scene(self):
        # This method is ugly and I know it
        pygame.time.set_timer(EVENT_ALLOW_RESTART, 500)

        allow_restart = False

        self.rules.clear_events()

        w, h = self.screen.get_size()
        img_rect = self.end_scene_img.get_rect()
        imgw, imgh = self.end_scene_img.get_size()
        img_rect.move_ip((w - imgw) / 2, (h - imgh) / 2)

        end_str = u'Your Time is  {}'.format(self.timer.get_str())
        text_surface = end_time_font.render(end_str, True, (0, 0, 0))
        txt_rect = text_surface.get_rect()
        txtw, txth = text_surface.get_size()
        txt_rect.move_ip((w - txtw) / 2, (h - txth) / 2 - 60)

        clock = pygame.time.Clock()
        while True:
            clock.tick(FPS)
            #dt = clock.get_time()
            for event in pygame.event.get():
                etype = event.type
                if etype is pygame.KEYDOWN:
                    k = event.key
                    if k in [pygame.K_ESCAPE, pygame.K_q]:
                        sys.exit()
                    elif allow_restart:
                        return self.game_scene
                elif etype is pygame.MOUSEBUTTONDOWN and allow_restart:
                    return self.game_scene
                elif etype is pygame.QUIT:
                    sys.exit()
                elif etype is EVENT_ALLOW_RESTART:
                    pygame.time.set_timer(EVENT_ALLOW_RESTART, 0)
                    allow_restart = True

            self.draw_game_objects()

            self.screen.blit(self.end_scene_img, img_rect)
            self.screen.blit(text_surface, txt_rect)

            pygame.display.flip()
        return self.end_scene

    def game_scene(self):
        self.init_game_objects()
        self.rules.init_game_events()

        dt = 0
        clock = pygame.time.Clock()
        while True:
            clock.tick(FPS)
            dt = clock.get_time()

            self.generate_circles(self.circles)

            self.circles = self.clean_circles(self.circles)
            self.bullets = self.clean_bullets(self.bullets)

            if self.pl.circle and self.pl.circle.is_bullet:
                self.bullets.append(self.pl.circle)
                self.pl.circle = None
            self.proccess_game_events()

            # Updates
            self.timer.update(dt)
            self.pl.update(dt)
            self.camera.update(dt)
            for c in self.circles:
                c.update(dt)
                if c.is_end:
                    self.end_circle = c
                    music_mgr.play_over()
                    return self.end_scene
            for b in self.bullets:
                b.update(dt)

            # Collisions
            self.pl.bounce_wall(self.arena)

            for c in self.circles:
                self.pl.bounce_circle(c)
                for b in self.bullets:
                    b.hit_circle(c)
                    b.out_of_bounds(self.arena)
                c.bounce_wall(self.arena)

            n_circles = len(self.circles)
            for i in xrange(0, n_circles):
                a = self.circles[i]
                for j in xrange(i + 1, n_circles):
                    b = self.circles[j]
                    a.bounce_circle(b)

            # Draw everything
            self.draw_game_objects()
            self.timer.draw(self.screen)
            pygame.display.flip()

    def draw_game_objects(self):
        self.screen.fill(COLOR_BACK)

        self.arena.draw(self.screen, self.camera)
        for b in self.bullets:
            b.draw_figure(self.screen, self.camera)

        for c in self.circles:
            c.draw_shadow(self.screen, self.camera)

        self.pl.draw_shadow(self.screen, self.camera)

        for c in self.circles:
            c.draw_figure(self.screen, self.camera)

        self.pl.draw_figure(self.screen, self.camera)

        for c in self.circles:
            c.draw_lines(self.screen, self.camera)

        self.arena.draw_limits(self.screen, self.camera)

    def proccess_game_events(self):
        pl = self.pl

        for event in pygame.event.get():
            etype = event.type
            if etype is pygame.KEYDOWN:
                k = event.key

                if k in [pygame.K_a, pygame.K_LEFT]:
                    pl.on_left(1)
                if k in [pygame.K_d, pygame.K_RIGHT]:
                    pl.on_right(1)
                if k in [pygame.K_s, pygame.K_DOWN]:
                    pl.on_down(1)
                if k in [pygame.K_w, pygame.K_UP]:
                    pl.on_up(1)
                if k in [pygame.K_ESCAPE, pygame.K_q]:
                    sys.exit()
            if etype is pygame.KEYUP:
                k = event.key
                if k in [pygame.K_a, pygame.K_LEFT]:
                    pl.on_left(0)
                if k in [pygame.K_d, pygame.K_RIGHT]:
                    pl.on_right(0)
                if k in [pygame.K_s, pygame.K_DOWN]:
                    pl.on_down(0)
                if k in [pygame.K_w, pygame.K_UP]:
                    pl.on_up(0)
            elif etype is pygame.MOUSEMOTION:
                pl.on_mouse_move(Vector2(*event.pos))
            elif etype is pygame.MOUSEBUTTONDOWN:
                pl.on_mouse_down(Vector2(*event.pos))
            elif etype is EVENT_GEN_CIRCLE:
                self.create_circle()
                self.rules.set_gen_circle_event()
            elif etype is EVENT_RULE_STEPUP:
                self.rules.step_up()
                self.rules.set_rule_stepup_event()
            elif etype is pygame.QUIT:
                sys.exit()

    def clean_circles(self, circles):
        return [c for c in circles if not c.is_delete]

    def clean_bullets(self, bullets):
        return [b for b in bullets if not b.is_delete]

    def generate_circles(self, circles):
        for c in circles:
            if c.is_delete and c.to_generate:
                for new_c in c.to_generate:
                    self.circles.append(new_c)
