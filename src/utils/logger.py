import logging
import sys

class Logger():
    """
    A custom class to handle all the logging needs.

    Params:
    name (str): name for the logger,you should pass __name__ generally.
    std_out (bool): Logs the message to the stdout (console) also if set True.
    log_file (str): custom log file to log all the messages, defaults to debug.log
    """

    DEFAULT_LOG_FILE = 'debug.log'

    def __init__(self, name, std_out=False ,log_file=None):

        self.log_file = self.DEFAULT_LOG_FILE if log_file is None else log_file

        logging.basicConfig(
            level=logging.DEBUG,
            filemode='a',
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            filename=self.log_file,
        )

        if std_out:
            logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        self._logger = logging.getLogger(name)

    def info(self, msg: str):
        self._logger.info(msg)

    def debug(self, msg: str):
        self._logger.debug(msg)

    def error(self, msg: str):
        self._logger.error(msg)

    def warning(self, msg: str):
        self._logger.warning(msg)