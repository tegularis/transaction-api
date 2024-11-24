import datetime
import logging


class Logger:
    def __init__(self, name, filename, cfg):
        logger = logging.getLogger(name)
        file_handler = logging.FileHandler(filename)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        self.name = name
        self.logger = logger
        self.cfg = cfg

    def success(self, msg):
        msg = f"SUCCESS | {self.name} | {msg}"
        self.logger.info(msg)

    def info(self, msg):
        msg = f"INFO | {self.name} | {msg}"
        self.logger.info(msg)

    def error(self, msg):
        msg = f"ERROR | {self.name} | {msg}"
        self.logger.error(msg)

    def warning(self, msg):
        msg = f"WARNING | {self.name} | {msg}"
        self.logger.warning(msg)
