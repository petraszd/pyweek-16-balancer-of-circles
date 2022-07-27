import pygame

from boc.events import EVENT_GEN_CIRCLE, EVENT_RULE_STEPUP
from boc.config import (RULES_INIT_STEP_UP_TIMEOUT,
                        RULES_INIT_CIRCLE_GEN_TIMEOUT,
                        RULES_INIT_SPEED,
                        RULES_MAX_SPEED,
                        RULES_SPEED_STEP_DELTA,
                        RULES_RADIUS_FROM,
                        RULES_RADIUS_TO,
                        RULES_RADIUS_STEP_DELTA,
                        RULES_STEP_UP_TIMEOUT_DELTA)


class Rules(object):
    def __init__(self):
        self.gen_circle_timeout = RULES_INIT_CIRCLE_GEN_TIMEOUT
        self.rule_step_up_timeout = RULES_INIT_STEP_UP_TIMEOUT
        self.speed = RULES_INIT_SPEED
        self.size_from = RULES_RADIUS_FROM
        self.size_to = RULES_RADIUS_TO

    def init_game_events(self):
        self.set_gen_circle_event()
        self.set_rule_stepup_event()

    def set_gen_circle_event(self):
        pygame.time.set_timer(EVENT_GEN_CIRCLE, self.gen_circle_timeout)

    def set_rule_stepup_event(self):
        pygame.time.set_timer(EVENT_RULE_STEPUP, self.rule_step_up_timeout)

    def clear_events(self):
        pygame.time.set_timer(EVENT_GEN_CIRCLE, 0)
        pygame.time.set_timer(EVENT_RULE_STEPUP, 0)

    def step_up(self):
        self.speed += RULES_SPEED_STEP_DELTA
        if self.speed > RULES_MAX_SPEED:
            self.speed = RULES_MAX_SPEED
        self.size_from += RULES_RADIUS_STEP_DELTA
        self.size_to += RULES_RADIUS_STEP_DELTA
        self.rule_step_up_timeout += RULES_STEP_UP_TIMEOUT_DELTA
