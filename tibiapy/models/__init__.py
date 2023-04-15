import pydantic

from tibiapy.models.house import *
from tibiapy.models.character import *
from tibiapy.models.creature import *
from tibiapy.models.event import *
from tibiapy.models.forum import *
from tibiapy.models.guild import *
from tibiapy.models.highscores import *
from tibiapy.models.kill_statistics import *
from tibiapy.models.leaderboards import *
from tibiapy.models.news import *
from tibiapy.models.spell import *
from tibiapy.models.bazaar import *
from tibiapy.models.world import *


class BaseModel(pydantic.BaseModel):

    class Config:
        json_encoders = {BattlEyeType: lambda g: g.name}
