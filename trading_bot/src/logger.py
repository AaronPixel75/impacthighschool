import logging
import os
from datetime import datetime
import sys

class Logger:
    _instance = None

    def __new__(cls, log_level="INFO", log_dir="logs"):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.setup_logger(log_level, log_dir)
        return cls._instance

    def setup_logger(self, log_level, log_dir):
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_filename = datetime.now().strftime("%Y-%m-%d_trading_bot.log")
        log_path = os.path.join(log_dir, log_filename)

        self.logger = logging.getLogger("TradingBot")
        self.logger.setLevel(log_level)
        self.logger.handlers = [] # Clear existing handlers

        # File Handler
        file_handler = logging.FileHandler(log_path)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

def setup_logging(config):
    log_level = config.get('system', {}).get('log_level', 'INFO')
    return Logger(log_level).get_logger()
