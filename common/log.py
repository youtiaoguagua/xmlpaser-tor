import logging

import colorlog

logger = logging.getLogger("language")

formatter = colorlog.ColoredFormatter(
	"%(cyan)s%(name)-5s %(purple)s%(asctime)s %(log_color)s%(levelname)-5s%(reset)s %(blue)s%(message)s",
	datefmt=None,
	reset=True,
	style='%'
)
stream_handler = colorlog.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

__all__ = ['logger']