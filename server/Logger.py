import logging


class Logger(object):
    _logger = None

    def __init__(self, name):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s | %(name)s | '
                                      '%(levelname)s | %(message)s')
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def get(self):
        return self._logger
