import pytest

from ivi_backend_api.ivi_backend_api.backend_api import BackendApi


def pytest_addoption(parser):
    parser.addoption('--login', action='store')
    parser.addoption('--password', action='store')


def pytest_configure(config):
    config.login = config.getoption('--login')
    config.password = config.getoption('--password')


@pytest.fixture(scope='session')
def backend(request):
    _backend = BackendApi(request.config.host)
    _backend.authorize(request.config.login, request.config.password)
    return _backend
