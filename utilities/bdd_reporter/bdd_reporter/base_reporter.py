import os
import traceback
import logging


class BaseReporter(object):

    def __init__(self, output_dir=None):
        self.output_dir = output_dir

    def is_case_failed(self):
        raise NotImplementedError("Class %s doesn't implement abstract method()" % self.__class__.__name__)

    def start_step(self, message):
        raise NotImplementedError("Class %s doesn't implement abstract method()" % self.__class__.__name__)

    def finish_step(self, error_type, error_message, error_traceback):
        raise NotImplementedError("Class %s doesn't implement abstract method()" % self.__class__.__name__)

    def start_suite(self, suite_name):
        raise NotImplementedError("Class %s doesn't implement abstract method()" % self.__class__.__name__)

    def finish_suite(self):
        raise NotImplementedError("Class %s doesn't implement abstract method()" % self.__class__.__name__)

    def start_case(self, case_name, labels=None, description=None, should_fail=False):
        raise NotImplementedError("Class %s doesn't implement abstract method()" % self.__class__.__name__)

    def finish_case(self):
        raise NotImplementedError("Class %s doesn't implement abstract method()" % self.__class__.__name__)

    def set_environment(self, parameters):
        raise NotImplementedError("Class %s doesn't implement abstract method()" % self.__class__.__name__)

    def finish_reporting(self):
        raise NotImplementedError("Class %s doesn't implement abstract method()" % self.__class__.__name__)

    def step(self, message):
        return LazyInitStepContext(self.start_step, self.finish_step, message)

    def _get_output_dir(self, make_if_not_exists=True):
        """
        Get directory for reporter output.

        Returns (str): output directory
        """
        if self.output_dir is None:
            directory = os.path.join(os.path.dirname(__file__), 'output')
            directory = os.path.join(directory, self.__class__.__name__)
        else:
            directory = os.path.join(self.output_dir, self.__class__.__name__)
        if make_if_not_exists:
            try:
                os.makedirs(directory)
                logging.info('Output directory created: %s.' % directory)
            except OSError as msg:
                if not os.path.isdir(directory):
                    raise
                logging.info('Failed to make dir: {}'.format(msg))
        return directory

    def _clear_output_dir(self):
        directory = os.path.normpath(os.path.abspath(os.path.expanduser(os.path.expandvars(self._get_output_dir()))))
        # Delete all files in report directory
        for directory_file in os.listdir(directory):
            directory_file = os.path.join(directory, directory_file)
            if os.path.isfile(directory_file):
                try:
                    os.unlink(directory_file)
                except OSError as error:
                    logging.error('Failed to unlink: %s. %s' % (directory_file, error))


class LazyInitStepContext:

    def __init__(self, start_step_callback, stop_step_callback, message):
        self.message = message
        self.start_step_callback = start_step_callback
        self.stop_step_callback = stop_step_callback

    def __enter__(self):
        self.start_step_callback(self.message)

    def __exit__(self, error_type, value, err_traceback):
        error_traceback = None
        error_message = None
        if error_type is not None:
            error_traceback = traceback.format_tb(err_traceback)
            error_message = '%s (%s: %s)' % (self.message, error_type.__name__, value)
        self.stop_step_callback(error_type, error_message, error_traceback)
