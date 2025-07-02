"""Simple logging utilities."""

import sys

class Log:
    """
    Log is a generic logging class that can write to anything with
    a `write` function. The recommended use of this class is to log
    to the standard output (stdout) and to a file, e.g.:
    logger = Log()
    logger.register_logger(sys.stdout)
    logger.register_logger(open('mylog.log', 'w'))
    """

    def __init__(self, *loggers):
        """Create a new ``Log`` instance and register ``loggers`` if provided."""

        self.loggers = list(loggers)

    def register_logger(self, logger):
        """Register a single ``logger`` object."""

        self.loggers.append(logger)

    def register_loggers(self, loggers):
        """Register multiple ``loggers`` objects."""

        for logger in loggers:
            self.register_logger(logger)

    def write(self, *args):
        """Write ``args`` to all registered loggers."""

        message = " ".join(args)
        for logger in self.loggers:
            logger.write(f"{message}\n")

    def fatal(self, *args):
        """Log ``args`` as a failure and terminate the program."""

        self.fail(*args)
        sys.exit(1)

    def fail(self, *args):
        """Log ``args`` as an error."""

        self.write("\033[0;31m", *args, "\033[0;00m")

    def warn(self, *args):
        """Log ``args`` as a warning."""

        self.write("\033[1;33m", *args, "\033[0;00m")

    def success(self, *args):
        """Log ``args`` as a success message."""

        self.write("\033[0;32m", *args, "\033[0;00m")

    def info(self, *args):
        """Log ``args`` as an informational message."""

        self.write("\033[1;35m", *args, "\033[0;00m")

    def close(self):
        """Close all registered loggers."""

        for logger in self.loggers:
            logger.close()

    def __del__(self):
        """Ensure all loggers are closed when this object is destroyed."""

        self.close()
