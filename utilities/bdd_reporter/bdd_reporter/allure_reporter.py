from allure.common import AllureImpl
from allure.structure import TestLabel
from allure.constants import Status, AttachmentType

from bdd_reporter.base_reporter import BaseReporter


class AllureReporter(BaseReporter):

    def __init__(self, output_dir=None):
        super(AllureReporter, self).__init__(output_dir)
        self.allure = AllureImpl(self._get_output_dir(False))
        self.case_status = None
        self.error_trace = None
        self.error_message = None

    def is_case_failed(self):
        return self.case_status == Status.FAILED

    def start_suite(self, suite_name):
        self.allure.start_suite(suite_name)

    def finish_suite(self):
        self.allure.stop_suite()

    def start_case(self, case_name, labels=None, description=None, should_fail=False):
        # New cases are failed by default. Any successful steps set it to passed.
        self.case_status = Status.FAILED if not should_fail else Status.PENDING
        self.error_trace = None
        self.error_message = None
        allure_labels = []
        if labels is not None:
            for item in labels:
                allure_labels.append(TestLabel(name=item['name'], value=item['value']))
        self.allure.start_case(case_name, labels=allure_labels, description=description)

    def finish_case(self):
        self.allure.stop_case(self.case_status, message=self.error_message, trace=self.error_trace)

    def start_step(self, message):
        self.allure.start_step(message)

    def finish_step(self, error_type, error_message, error_traceback):
        if self.case_status is not Status.PENDING:
            status = Status.PASSED
            if error_type is not None:
                status = Status.FAILED
            self.case_status = status
        if error_message is not None:
            self.error_message = '%s: %s' % (self.case_status, error_message)
        if error_traceback is not None:
            self.error_trace = error_traceback
        self.allure.stop_step()

    def finish_reporting(self):
        pass

    def attach_text(self, title, data):
        self.allure.attach(title, str(data), AttachmentType.TEXT)

    def attach_html(self, title, html):
        self.allure.attach(title, html, AttachmentType.HTML)

    def set_environment(self, parameters):
        self.allure.environment = parameters
        self.allure.store_environment()
