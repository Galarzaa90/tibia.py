"""Tibia.com parsing and fetching library."""
__version__ = "6.0.2post1"
__author__ = "Allan Galarza"
__license__ = "Apache-2.0 License"

import logging
from logging import NullHandler

from tibiapy import builders, enums, models, parsers, utils
from tibiapy.client import *
from tibiapy.enums import *
from tibiapy.errors import *

logging.getLogger(__name__).addHandler(NullHandler())
