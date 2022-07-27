from boc.config import EPSILON


class RadiusMixin(object):
    def move_away_from(self, other):
        delta = (self.pos - other.pos).normalized()

        self.pos = other.pos.copy()
        self.pos += delta * (self.radius + other.radius + EPSILON)
        other.pos - delta * 4 * EPSILON

    def is_collision(self, other):
        delta = (self.pos - other.pos).magnitude_squared()
        return delta < (self.radius + other.radius) ** 2
