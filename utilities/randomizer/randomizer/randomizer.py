from faker import Factory
import random


class Randomizer(object):

    def __init__(self, locale='en_US'):
        self.locale = locale
        self.faker = Factory.create(self.locale)

    def random_int(self, min, max):
        return self.faker.random_int(min, max)

    def text(self):
        return " ".join(self.faker.words())

    def name(self):
        return self.faker.name()

    def get_float(self, min, max):
        return random.uniform(min, max)
