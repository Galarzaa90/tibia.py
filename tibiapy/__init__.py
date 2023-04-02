"""Tibia.com parsing and fetching library."""
__version__ = '5.6.0'
__author__ = 'Allan Galarza'
__license__ = 'Apache-2.0 License'

import logging

from tibiapy import abc, enums, utils
from tibiapy.creature import *
from tibiapy.event import *
from tibiapy.enums import *
from tibiapy.errors import *
from tibiapy.forum import *
from tibiapy.bazaar import *
from tibiapy.client import *

from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
