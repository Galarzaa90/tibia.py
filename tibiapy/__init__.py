"""Tibia.com parsing and fetching library."""
__version__ = "6.2.0"
__author__ = "Allan Galarza"
__license__ = "Apache-2.0 License"

import logging
from logging import NullHandler

from tibiapy.errors import *
from tibiapy import models, enums, client, utils, parsers, urls
from tibiapy.client import *


logging.getLogger(__name__).addHandler(NullHandler())
