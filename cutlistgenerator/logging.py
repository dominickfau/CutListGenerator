import logging, os

LOG_FILE_NAME = "cutlistgenerator.log"
LOG_FILE_PATH = os.path.join(os.path.dirname("Cut_List"), LOG_FILE_NAME)

class FileLogger:
    """Creates a logger."""

    def __init__(self, name, file_name=None) -> None:
        """Create a new logger with the given name. Defaults to log level INFO."""

        self._logger =  logging.getLogger(name)  # Create python logger
        self._logger.setLevel(logging.INFO)

        # Do not try to save to the app dir as it may not be writeable or may not be the right
        # location to save the log file. Instead, try and save in the settings location since
        # that should be writeable.
        if file_name is None:
            file_name = LOG_FILE_PATH
        self.set_file_name(file_name)

    def set_file_name(self, file_name) -> None:
        """Set the file name of the log file."""
        if ".log" in file_name:
            file_handler = logging.FileHandler(file_name, encoding = "utf-8")
            format_handler = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
            file_handler.setFormatter(format_handler)
            self._logger.addHandler(file_handler)
        else:
            pass  # TODO, add handling
    
    def set_level(self, level) -> None:
        """Set the logging level of this logger. level must be an int or a str."""
        self._logger.setLevel(level)

    def debug(self, message: str, *args, **kwargs) -> None:
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs) -> None:
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """Convenience method for logging an ERROR with exception information."""
        self._logger.exception(message, *args, **kwargs)