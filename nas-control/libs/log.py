from logging import getLogger, Formatter, handlers, INFO, ERROR

LOG_FORMATTER = Formatter(
  '%(asctime)s [%(levelname)s] %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S')

logger = getLogger()

infoLogHandler = handlers.TimedRotatingFileHandler(
  '/var/log/naspi.log',
  when='M',
  interval=1,
  backupCount=0)
infoLogHandler.setLevel(INFO)
infoLogHandler.setFormatter(LOG_FORMATTER)

errorLogHandler = handlers.RotatingFileHandler(
  '/var/log/naspi.error.log',
  maxBytes=5000,
  backupCount=2
)
errorLogHandler.setLevel(ERROR)
errorLogHandler.setFormatter(LOG_FORMATTER)

logger.addHandler(infoLogHandler)
logger.addHandler(errorLogHandler)
