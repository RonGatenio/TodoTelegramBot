import logging

def init_logger(name, level=logging.DEBUG):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add console handler
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger

def log_exceptions(logger):
    def log_exceptions_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                logger.exception('Failed to execute {}'.format(func.__name__))
                raise
        return wrapper
    return log_exceptions_decorator
