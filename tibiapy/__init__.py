"""Tibia.com parsing and fetching library."""
__version__ = '5.6.0'
__author__ = 'Allan Galarza'
__license__ = 'Apache-2.0 License'

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
from tibiapy.leaderboard import *
from tibiapy.news import *
from tibiapy.tournament import *
from tibiapy.world import *
from tibiapy.bazaar import *
from tibiapy.spell import *
from tibiapy.client import *

from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
