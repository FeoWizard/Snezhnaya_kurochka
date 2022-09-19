#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
import sys
from datetime import datetime


def get_time_delta(logger: logging.getLoggerClass(), start_time, reason: str = ""):
    end_time = datetime.now()
    delta    = end_time - start_time
    logger.info(msg = reason + str(delta))
    return None

# Уровни тревожности в логгировании
# CRITICAL = 50
# FATAL    = CRITICAL
# ERROR    = 40
# WARNING  = 30
# WARN     = WARNING
# INFO     = 20
# DEBUG    = 10
# NOTSET   = 0


# "tele_crawler"
class Logger_Factory:
    STD_FORMAT_STRING = None


    def __init__(self, bot_name, logs_path: str = "", multithreading: bool = False, multiprocessing: bool = False):

        self.STD_FORMAT_STRING = "%(name)15s: %(levelname)8s: %(asctime)s;" \
                            " Module: %(module)17s; Function: %(funcName)25s; Line_number: %(lineno)4d ===> %(message)s"

        if (multithreading):
            self.STD_FORMAT_STRING = "%(name)15s: %(levelname)8s: %(asctime)s; %(threadName)14s;" \
                                " Module: %(module)17s; Function: %(funcName)25s; Line_number: %(lineno)4d ===> %(message)s"

        if (multiprocessing):
            self.STD_FORMAT_STRING = "%(name)15s: %(levelname)8s: %(asctime)s; %(processName)10s;" \
                                " Module: %(module)17s; Function: %(funcName)25s; Line_number: %(lineno)4d ===> %(message)s"

        if (multithreading) and (multiprocessing):
            self.STD_FORMAT_STRING = "%(name)15s: %(levelname)8s: %(asctime)s; %(threadName)14s; %(processName)10s;" \
                                " Module: %(module)17s; Function: %(funcName)25s; Line_number: %(lineno)4d ===> %(message)s"

        if (logs_path != ""):
            logs_path = logs_path + "/"

        self.BOT_NAME  = bot_name
        self.LOGS_PATH = "logs/" + logs_path
        self.DATE      = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if (not os.path.exists(self.LOGS_PATH)):
            os.mkdir(self.LOGS_PATH)

    def get_log_file_name(self, file_name: str, file_path: str = "", insert_date: bool = False):
        if (insert_date):
            LOG_FILE = self.LOGS_PATH + file_path + file_name + "_" + self.DATE + ".log"
        else:
            LOG_FILE = self.LOGS_PATH + file_path + file_name + ".log"

        return LOG_FILE

    def get_logger(self, logger_name: str, date: bool = False):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        log_format = logging.Formatter(self.STD_FORMAT_STRING)

        LOG_FILE         = self.get_log_file_name(self.BOT_NAME, insert_date = date)
        log_file_handler = logging.FileHandler(LOG_FILE, encoding = "utf-8")
        log_file_handler.setFormatter(log_format)

        log_stream_handler = logging.StreamHandler(sys.stderr)
        log_stream_handler.setFormatter(log_format)

        logger.addHandler(log_file_handler)
        logger.addHandler(log_stream_handler)
        return logger

    def get_file_logger(self, logger_name: str, file_name: str, file_path: str = "",
                        datetime_output: bool = False, log_format: str = "", date: bool = False):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        if (datetime_output):
            datetime_string = str(datetime.now())[:-3] + " //:> "
            format_string   = datetime_string + log_format + "%(message)s"
        else:
            format_string = log_format + "%(message)s"

        log_format       = logging.Formatter(format_string)
        log_file         = self.get_log_file_name(file_name, file_path, insert_date = date)
        log_file_handler = logging.FileHandler(log_file)

        log_file_handler.setFormatter(log_format)
        logger.addHandler(log_file_handler)
        return logger

    def add_logger_file_handler(self, logger: logging.getLoggerClass(), log_level: int, file_name: str,
                                file_path: str = "", format_string: str = STD_FORMAT_STRING, date: bool = False):

        log_formatter = logging.Formatter(format_string)
        log_file      = self.get_log_file_name(file_name, file_path, insert_date = date)
        log_file_handler = logging.FileHandler(log_file)
        log_file_handler.setFormatter(log_formatter)
        log_file_handler.setLevel(log_level)
        logger.addHandler(log_file_handler)

    def add_logger_stream_handler(self, logger: logging.getLoggerClass(), log_level: int, stream = sys.stderr, format_string: str = STD_FORMAT_STRING):
        log_formatter      = logging.Formatter(format_string)
        log_stream_handler = logging.StreamHandler(stream)
        log_stream_handler.setFormatter(log_formatter)
        log_stream_handler.setLevel(log_level)
        logger.addHandler(log_stream_handler)

