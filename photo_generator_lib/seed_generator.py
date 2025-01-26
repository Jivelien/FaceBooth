import random


class SeedGenerator:
    def __init__(self, min: int = 0, max: int = 65255):
        self.min = min
        self.max = max
        self.seed = self._generate_random()

    def _generate_random(self):
        return random.randint(self.min, self.max)

    def randomize(self):
        self.seed = self._generate_random()

    def actual_seed(self):
        return self.seed
