import logging
from logging.handlers import BufferingHandler
import pytest
from bdd_reporter.reporter_factory import ReporterFactory


def pytest_addoption(parser):
    parser.addoption('--bdd-reporter', action='store', dest='bdd_reporter', default='console')
    parser.addoption('--bdd-reporter-dir', action='store', dest='bdd_reporter_dir', default=None)


def pytest_configure(config):
    config.reporter = config.getoption('bdd_reporter')
    config.reporter_dir = config.getoption('bdd_reporter_dir')


@pytest.fixture(scope='function')
def reporter(request, __reporter_class):
    test_name = request.node.name
    if hasattr(request.config, 'bdd_reporter_case_name_suffix'):
        test_name = '%s (%s)' % (test_name, request.config.bdd_reporter_case_name_suffix)
    labels = []
    description = request.node.function.__doc__
    case_owner = request.node.get_marker('case_owner')
    if case_owner is not None:
        description = 'Case owner: %s\nDescription: %s' % (case_owner.args[0], description)
    available_severity_marks = ['blocker', 'critical', 'normal', 'minor', 'trivial']
    for mark in available_severity_marks:
        severity = request.node.get_marker(mark)
        if severity is not None:
            label = {
                'name': 'severity',
                'value': severity.name
            }
            labels.append(label)

    __reporter_class.start_case(test_name, labels=labels, description=description)
    logging.info('Test case "{}" started.'.format(test_name))

    def finish_report_case():
        logging.info('Test case "{}" finished.'.format(test_name))
        __reporter_class.finish_case()

    request.addfinalizer(finish_report_case)
    return __reporter_class


@pytest.fixture(scope='class')
def __reporter_class(request, __reporter_session):
    class_name = request.node.name
    __reporter_session.start_suite(class_name)

    def finish_report_suite():
        __reporter_session.finish_suite()

    request.addfinalizer(finish_report_suite)
    return __reporter_session


@pytest.fixture(scope='session')
def __reporter_session(request):
    logging.info('Reporter fixture setup.')
    reporter_object = ReporterFactory.get(request.config.reporter, request.config.reporter_dir)
    if hasattr(request.config, 'test_environment'):
        reporter_object.set_environment(request.config.test_environment)

    def finish_reporting():
        reporter_object.finish_reporting()
        logging.info('Reporting finished.')

    request.addfinalizer(finish_reporting)

    return reporter_object


@pytest.fixture(scope='function', autouse=True)
def report_local_logs(request, reporter):
    """Attach all python logging records to report"""
    record_format = '%(asctime)s %(message)s'
    date_format = '%d/%m/%y %H:%M:%S'
    formatter = logging.Formatter(record_format, date_format)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.root.handlers = []
    is_bulk_flush = True
    if request.config.reporter == 'console':
        is_bulk_flush = False
    logger_reporter = LoggerReporterHandler(reporter, is_bulk_flush)
    logger_reporter.setFormatter(formatter)
    logging.root.addHandler(logger_reporter)

    def attach_logs():
        logger_reporter.flush()
        logger.root.removeHandler(logger_reporter)

    request.addfinalizer(attach_logs)


class LoggerReporterHandler(BufferingHandler):

    def __init__(self, reporter, is_bulk_flush=True):
        BufferingHandler.__init__(self, 1000)
        self.reporter = reporter
        self.is_bulk_flush = is_bulk_flush

    def shouldFlush(self, record):
        return not self.is_bulk_flush

    def flush(self):
        logs = []
        for record in self.buffer:
            logs.append(self.format(record))
        self.reporter.attach_html('Local Logs', '<br>'.join(logs))
        super(LoggerReporterHandler, self).flush()
