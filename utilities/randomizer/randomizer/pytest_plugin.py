import logging

import pytest
from randomizer.randomizer import Randomizer


@pytest.fixture(scope='session')
def randomizer(request):
    logging.info('Randomizer fixture setup.')
    return Randomizer()
