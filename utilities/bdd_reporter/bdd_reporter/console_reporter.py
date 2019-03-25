from bdd_reporter.base_reporter import BaseReporter


class ConsoleReporter(BaseReporter):

    colors = {
        'header': '\033[95m',
        'info': '\033[94m',
        'success': '\033[92m',
        'warning': '\033[93m',
        'fail': '\033[91m',
        'end': '\033[0m'
    }

    def __init__(self, output_dir=None):
        super(ConsoleReporter, self).__init__(output_dir)
        self._clear_output_dir()
        self.case_failed = False
        self.current_step_message = None

    def is_case_failed(self):
        return self.case_failed

    def console_print(self, message, color=None):
        if color is not None:
            message = color + message + self.colors['end']
        print(message)

    def start_suite(self, suite_name):
        self.console_print('Start Test Suite: %s.' % suite_name, self.colors['warning'])

    def finish_suite(self):
        self.console_print('Finish Test Suite.')

    def start_case(self, case_name, labels=None, description=None, should_fail=False):
        self.case_failed = False
        self.current_step_message = None
        self.console_print('Start Test Case: %s.' % case_name, self.colors['header'])
        if labels is not None:
            for label in labels:
                self.console_print('%s: %s.' % (label['name'], label['value']), self.colors['info'])
        if description is not None:
            self.console_print(description, self.colors['info'])

    def finish_case(self):
        self.console_print('Finish Test Case', self.colors['header'])

    def start_step(self, message):
        self.current_step_message = message

    def finish_step(self, error_type, error_message, error_traceback):
        color = self.colors['success']
        if error_type is not None:
                self.case_failed = True
                color = self.colors['fail']
        self.console_print('Step: %s.' % self.current_step_message, color)

    def finish_reporting(self):
        pass

    def attach_text(self, title, data):  # for support attach text in allure report
        self.console_print('%s: %s' % (title, data), self.colors['info'])

    def set_environment(self, parameters):
        output = ''
        for key, value in parameters.iteritems():
            output = '%s %s - %s \n' % (output, key, value)
        message = 'Environment:\n%s' % output
        self.console_print(message, self.colors['info'])

    def attach_html(self, title, html):
        self.console_print('%s: %s' % (title, html), self.colors['info'])
