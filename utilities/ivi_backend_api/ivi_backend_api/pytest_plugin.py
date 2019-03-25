import pytest
from ivi_backend_api.backend_api import BackendApi


def pytest_addoption(parser):
    parser.addoption('--host', action='store', default='http')


def pytest_configure(config):
    config.host = config.getoption("host")


@pytest.fixture(scope='session')
def backend_api(request):
    return BackendApi(request.config.host)
