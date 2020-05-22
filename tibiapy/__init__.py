import logging

from tibiapy import abc, enums, utils
from tibiapy.character import *
from tibiapy.enums import *
from tibiapy.errors import *
from tibiapy.guild import *
from tibiapy.highscores import *
from tibiapy.house import *
from tibiapy.kill_statistics import *
from tibiapy.news import *
from tibiapy.world import *
from tibiapy.creature import *
from tibiapy.tournament import *
from tibiapy.client import *

__version__ = '2.5.0'

from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
