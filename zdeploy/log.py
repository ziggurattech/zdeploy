class Log:
    '''
    Log is a generic logging class that can write to anything with
    a `write` function. The recommended use of this class is to log
    to the standard output (stdout) and to a file, e.g.:
    logger = Log()
    logger.register_logger(sys.stdout)
    logger.register_logger(open('mylog.log', 'w'))
    '''
    def __init__(self, *loggers):
        self.loggers = list(loggers)
    def register_logger(self, logger):
        self.loggers.append(logger)
    def register_loggers(self, loggers):
        for logger in loggers:
            self.register_logger(logger)
    def write(self, *args):
        message = ' '.join(args)
        for logger in self.loggers:
            logger.write('%s\n' % message)
    def fatal(self, *args):
        self.fail(*args)
        exit(1)
    def fail(self, *args):
        self.write('\033[0;31m', *args, '\033[0;00m')
    def warn(self, *args):
        self.write('\033[1;33m', *args, '\033[0;00m')
    def success(self, *args):
        self.write('\033[0;32m', *args, '\033[0;00m')
    def info(self, *args):
        self.write('\033[1;35m', *args, '\033[0;00m')
    def close(self):
        for logger in self.loggers:
            logger.close()
    def __del__(self):
        self.close()