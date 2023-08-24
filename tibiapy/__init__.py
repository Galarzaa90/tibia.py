"""Tibia.com parsing and fetching library."""
__version__ = "6.0.0"
__author__ = "Allan Galarza"
__license__ = "Apache-2.0 License"

import logging
from logging import NullHandler

from tibiapy import enums, utils
from tibiapy.enums import *
from tibiapy.errors import *
from tibiapy.client import *

logging.getLogger(__name__).addHandler(NullHandler())
