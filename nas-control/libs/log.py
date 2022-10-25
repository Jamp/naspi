from logging import getLogger, Formatter, handlers, INFO


LOG_FORMATTER = Formatter(
  '%(asctime)s [%(levelname)s] %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S')

logger = getLogger()
logger.setLevel(INFO)

infoLogHandler = handlers.TimedRotatingFileHandler(
  '/var/log/naspi.log',
  when='D',
  interval=1,
  backupCount=0)
infoLogHandler.setFormatter(LOG_FORMATTER)

logger.addHandler(infoLogHandler)
