"""
i3-xfce core module
"""

import logging
from colorlog import ColoredFormatter

ROOTLOGGER = logging.getLogger("i3-xfce")

def init_loggers():
  """
  Function initialize loggers
  """
  formatter = ColoredFormatter("%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
                               datefmt=None,
                               reset=True,
                               log_colors={
                                   'DEBUG':    'cyan',
                                   'INFO':     'white',
                                   'WARNING':  'yellow',
                                   'ERROR':    'red',
                                   'CRITICAL': 'red,bg_white',
                               },
                               secondary_log_colors={},
                               style='%'
                              )

  handler = logging.StreamHandler()
  handler.setFormatter(formatter)

  ROOTLOGGER.addHandler(handler)

def set_log_level(lvl):
  """
  Function to set log level
  """
  ROOTLOGGER.setLevel(lvl)
