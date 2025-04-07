import logging

logging.basicConfig(
    filename="main.log",
    filemode="a",
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(filename)s: %(levelname)s: %(funcName)s(): %(lineno)d:\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
logger_streamhandler = logging.StreamHandler()
logger_streamhandler.level = logging.DEBUG
logger.addHandler(logger_streamhandler)
