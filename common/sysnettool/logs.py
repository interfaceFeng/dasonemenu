# -*- coding: utf-8 -*-

import logging
import logging.handlers
import functools

LOGSIZE=10*1024*1024
# decorator
def log(log_file, log_name=None):
    # create and configurate logger
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.INFO)

    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=LOGSIZE)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)-8s - %(log_name)s - %(message)s',
        datefmt='%H:%M:%S %Y-%m-%d')

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # run func
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:

                name = func.__name__ if log_name is None else log_name
                extra = {'log_name':name}
                logger.info('start', extra=extra)
                func(*args, **kwargs)
                logger.info('finish', extra=extra)
            except Exception as e:
                logger.error(type(e).__name__ + ': ' + e.message, extra=extra)
                raise e
        return wrapper
    return decorator



