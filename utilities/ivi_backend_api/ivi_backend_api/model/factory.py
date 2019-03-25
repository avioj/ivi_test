from utilities.ivi_backend_api.ivi_backend_api.model.character import Character

from randomizer.randomizer import Randomizer

randomizer = Randomizer()


def get_random_char():
    return Character(name=randomizer.name(), universe=randomizer.text(),
                     education=randomizer.text(), weight=randomizer.random_int(10, 100),
                     height=randomizer.get_float(10, 200), identity=randomizer.text(), other_aliases="None")
