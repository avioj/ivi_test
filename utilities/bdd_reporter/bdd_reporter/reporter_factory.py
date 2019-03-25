from bdd_reporter.console_reporter import ConsoleReporter


class ReporterFactory:

    def __init__(self):
        pass

    @staticmethod
    def get(reporter_type='console', reporter_dir=None):
        if reporter_type == 'allure':
            try:
                import allure
            except ImportError:
                raise Exception('Install `pytest-allure-adaptor` package manually to use AllureReporter.')
            from bdd_reporter.allure_reporter import AllureReporter
            return AllureReporter(reporter_dir)
        return ConsoleReporter(reporter_dir)
