import logging

from tibiapy import abc, enums, utils
from tibiapy.house import *
from tibiapy.character import *
from tibiapy.creature import *
from tibiapy.event import *
from tibiapy.enums import *
from tibiapy.errors import *
from tibiapy.forum import *
from tibiapy.guild import *
from tibiapy.highscores import *
from tibiapy.kill_statistics import *
from tibiapy.news import *
from tibiapy.tournament import *
from tibiapy.world import *
from tibiapy.client import *

__version__ = '3.2.1'

from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
