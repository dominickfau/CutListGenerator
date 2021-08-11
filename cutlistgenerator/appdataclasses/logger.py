import logging

from cutlistgenerator import log_file_path

def get_logger(logger_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    format_handler = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
    file_handler.setFormatter(format_handler)
    logger.addHandler(file_handler)
    return logger