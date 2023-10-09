.. currentmodule:: tibiapy

=============
API Reference
=============
This module implements a variety of classes used to hold the data parsed from Tibia.com.

These objects are generally obtained from their respective ``from_content`` methods.
It is possible to create and edit these objects as desired, but it may lead to unexpected behaviour if not done properly.

Client
======

.. autopydantic_model:: tibiapy.models.TibiaResponse
   :inherited-members: BaseModel

.. autoclass:: Client
    :members:

Enumerations
============
Enumerations are provided for various values in order to avoid depending on strings.

Many of these enumerations correspond to available options in forms in Tibia.com

.. autoclass:: AuctionBattlEyeFilter
    :members:
    :undoc-members:

.. autoclass:: AuctionOrderBy
    :members:
    :undoc-members:

.. autoclass:: AuctionOrderDirection
    :members:
    :undoc-members:

.. autoclass:: AuctionSearchType
    :members:
    :undoc-members:

.. autoclass:: AuctionSkillFilter
    :members:
    :undoc-members:

.. autoclass:: AuctionStatus
    :members:
    :undoc-members:

.. autoclass:: AuctionVocationFilter
    :members:
    :undoc-members:

.. autoclass:: AvailableForumSection
    :members:
    :undoc-members:

.. autoclass:: BattlEyeType
    :members:
    :undoc-members:

.. autoclass:: BazaarType
    :members:
    :undoc-members:

.. autoclass:: BidType
    :members:
    :undoc-members:

.. autoclass:: HighscoresBattlEyeType
    :members:
    :undoc-members:

.. autoclass:: HighscoresCategory
    :members:
    :undoc-members:

.. autoclass:: HighscoresProfession
    :members:
    :undoc-members:

.. autoclass:: HouseOrder
    :members:
    :undoc-members:

.. autoclass:: HouseStatus
    :members:
    :undoc-members:

.. autoclass:: HouseType
    :members:
    :undoc-members:

.. autoclass:: NewsCategory
    :members:
    :undoc-members:

.. autoclass:: NewsType
    :members:
    :undoc-members:

.. autoclass:: PvpType
    :members:
    :undoc-members:

.. autoclass:: PvpTypeFilter
    :members:
    :undoc-members:

.. autoclass:: Sex
    :members:
    :undoc-members:

.. autoclass:: SpellGroup
    :members:
    :undoc-members:

.. autoclass:: SpellSorting
    :members:
    :undoc-members:

.. autoclass:: SpellType
    :members:
    :undoc-members:

.. autoclass:: SpellVocationFilter
    :members:
    :undoc-members:

.. autoclass:: ThreadStatus
    :members:
    :undoc-members:

.. autoclass:: TransferType
    :members:
    :undoc-members:

.. autoclass:: Vocation
    :members:
    :undoc-members:

.. autoclass:: WorldLocation
    :members:
    :undoc-members:


.. currentmodule:: tibiapy.models

Characters
===========
The `Character section`_ consists of the :class:`Character` class and its auxiliary classes used to hold its data.

The entry points for this are:

- :meth:`.CharacterParser.from_content` - Parsing a character's content.
- :meth:`.Client.fetch_character` - Fetching and parsing a character's content.

.. _Character section: https://www.tibia.com/community/?subtopic=characters

Character
---------
.. autopydantic_model:: Character
   :inherited-members: BaseModel

Auxiliary Classes
-----------------

AccountBadge
~~~~~~~~~~~~
.. autopydantic_model:: AccountBadge
   :inherited-members: BaseModel

AccountInformation
~~~~~~~~~~~~~~~~~~
.. autopydantic_model:: AccountInformation
   :inherited-members: BaseModel

Achievement
~~~~~~~~~~~
.. autopydantic_model:: Achievement
   :inherited-members: BaseModel

CharacterHouse
~~~~~~~~~~~~~~
.. autopydantic_model:: CharacterHouse
   :inherited-members: BaseModel

Death
~~~~~
.. autopydantic_model:: Death
   :inherited-members: BaseModel

GuildMembership
~~~~~~~~~~~~~~~
.. autopydantic_model:: GuildMembership
   :inherited-members: BaseModel

DeathParticipant
~~~~~~~~~~~~~~~~
.. autopydantic_model:: DeathParticipant
   :inherited-members: BaseModel

OtherCharacter
~~~~~~~~~~~~~~
.. autopydantic_model:: OtherCharacter
   :inherited-members: BaseModel

Worlds
======
Models related to `Tibia.com's World section`_. The :class:`WorldOverview` class contains the list of all worlds, while
the :class:`World` class contains the details of a single world.

.. _Tibia.com's World section: https://www.tibia.com/community/?subtopic=worlds

WorldOverview
-------------
.. autopydantic_model:: WorldOverview
   :inherited-members: BaseModel

WorldEntry
-----------
.. autopydantic_model:: WorldEntry
   :inherited-members: BaseModel

World
-----
.. autopydantic_model:: World
   :inherited-members: BaseModel

OnlineCharacter
---------------
.. autopydantic_model:: OnlineCharacter
   :inherited-members: BaseModel

Guilds
======
Models related to `Tibia.com's Guilds section`_. The main model is :class:`Guild`, while :class:`GuildEntry` is the
previewed information in the guild list of the :class:`GuildsSection`.

.. _Tibia.com's Guilds section: https://www.tibia.com/community/?subtopic=guilds

GuildsSection
-------------
.. autopydantic_model:: GuildsSection
   :inherited-members: BaseModel

Guild
-----
.. autopydantic_model:: Guild
   :inherited-members: BaseModel

GuildEntry
----------
.. autopydantic_model:: GuildEntry
   :inherited-members: BaseModel

Auxiliary Classes
-----------------
GuildInvite
~~~~~~~~~~~
.. autopydantic_model:: GuildInvite
   :inherited-members: BaseModel

GuildHouse
~~~~~~~~~~
.. autopydantic_model:: GuildHouse
   :inherited-members: BaseModel

GuildMember
~~~~~~~~~~~
.. autopydantic_model:: GuildMember
   :inherited-members: BaseModel

GuildWars
~~~~~~~~~
.. autopydantic_model:: GuildWars
   :inherited-members: BaseModel

GuildWarEntry
~~~~~~~~~~~~~
.. autopydantic_model:: GuildWarEntry
   :inherited-members: BaseModel

Highscores
==========
Models related to `Tibia.com's Highscores section`_.

.. _Tibia.com's Highscores section: https://www.tibia.com/community/?subtopic=highscores

Highscores
----------
.. autopydantic_model:: Highscores
   :inherited-members: BaseModel

HighscoresEntry
---------------
.. autopydantic_model:: HighscoresEntry
   :inherited-members: BaseModel

LoyaltyHighscoresEntry
----------------------
.. autopydantic_model:: LoyaltyHighscoresEntry
   :inherited-members: BaseModel

Houses
======
Models related to `Tibia.com's Houses section`_.

.. _Tibia.com's Houses section: https://www.tibia.com/community/?subtopic=houses

HousesSection
-------------
.. autopydantic_model:: HousesSection
   :inherited-members: BaseModel

House
-----
.. autopydantic_model:: House
   :inherited-members: BaseModel

HouseEntry
----------
.. autopydantic_model:: HouseEntry
   :inherited-members: BaseModel

Leaderboard
===========
Models related to `Tibia.com's Leaderboard section`_.

.. _Tibia.com's Leaderboard section: https://www.tibia.com/community/?subtopic=tournament

Leaderboard
-----------
.. autopydantic_model:: Leaderboard
   :inherited-members: BaseModel

Auxiliary Classes
-----------------

LeaderboardRotation
~~~~~~~~~~~~~~~~~~~
.. autopydantic_model:: LeaderboardRotation
   :inherited-members: BaseModel

LeaderboardEntry
~~~~~~~~~~~~~~~~
.. autopydantic_model:: LeaderboardEntry
   :inherited-members: BaseModel

Forums
======
Models related to `Tibia.com's Forum section`_.

.. _Tibia.com's Forum section: https://www.tibia.com/community/?subtopic=worldboards

CMPostArchive
-------------
.. autopydantic_model:: CMPostArchive
   :inherited-members: BaseModel


ForumSection
------------
.. autopydantic_model:: ForumSection
    :inherited-members: BaseModel


ForumAnnouncement
-----------------
.. autopydantic_model:: ForumAnnouncement
    :inherited-members: BaseModel

ForumBoard
----------
.. autopydantic_model:: ForumBoard
    :inherited-members: BaseModel

ForumPost
---------
.. autopydantic_model:: ForumPost
    :inherited-members: BaseModel

ForumThread
-----------
.. autopydantic_model:: ForumThread
    :inherited-members: BaseModel

AnnouncementEntry
------------------
.. autopydantic_model:: AnnouncementEntry
    :inherited-members: BaseModel

BoardEntry
----------
.. autopydantic_model:: BoardEntry
    :inherited-members: BaseModel

ThreadEntry
-----------
.. autopydantic_model:: ThreadEntry
    :inherited-members: BaseModel

Auxiliary Classes
-----------------
CMPost
~~~~~~
.. autopydantic_model:: CMPost
   :inherited-members: BaseModel

ForumAuthor
~~~~~~~~~~~
.. autopydantic_model:: ForumAuthor
    :inherited-members: BaseModel

ForumEmoticon
~~~~~~~~~~~~~
.. autopydantic_model:: ForumEmoticon
    :inherited-members: BaseModel

LastPost
~~~~~~~~
.. autopydantic_model:: LastPost
    :inherited-members: BaseModel


News
=======
Models related to `Tibia.com's News section`_. This also contains the `Event Calendar`_

.. _Tibia.com's News section: https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades
.. _Event Calendar: https://www.tibia.com/news/?subtopic=eventcalendar

NewsArchive
-----------
.. autopydantic_model:: NewsArchive
   :inherited-members: BaseModel

News
---------
.. autopydantic_model:: News
   :inherited-members: BaseModel

NewsEntry
-----------
.. autopydantic_model:: NewsEntry
   :inherited-members: BaseModel

EventSchedule
-------------
.. autopydantic_model:: EventSchedule
   :inherited-members: BaseModel

EventEntry
-------------
.. autopydantic_model:: EventEntry
   :inherited-members: BaseModel

Bazaar
======
Models related to `Tibia.com's Bazaar section`_.

.. _Tibia.com's Bazaar section: https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades

CharacterBazaar
---------------
.. autopydantic_model:: CharacterBazaar
   :inherited-members: BaseModel

Auction
------------
.. autopydantic_model:: Auction
    :inherited-members: BaseModel

AuctionDetails
--------------
.. autopydantic_model:: AuctionDetails
   :inherited-members: BaseModel

Auxiliary Classes
-----------------

AchievementEntry
~~~~~~~~~~~~~~~~
.. autopydantic_model:: AchievementEntry
   :inherited-members: BaseModel

AuctionFilters
~~~~~~~~~~~~~~
.. autopydantic_model:: AuctionFilters
   :inherited-members: BaseModel


BestiaryEntry
~~~~~~~~~~~~~
.. autopydantic_model:: BestiaryEntry
   :inherited-members: BaseModel

BlessingEntry
~~~~~~~~~~~~~
.. autopydantic_model:: BlessingEntry
   :inherited-members: BaseModel

CharmsEntry
~~~~~~~~~~~
.. autopydantic_model:: CharmEntry
   :inherited-members: BaseModel

FamiliarEntry
~~~~~~~~~~~~~
.. autopydantic_model:: FamiliarEntry
   :inherited-members: BaseModel

ItemEntry
~~~~~~~~~
.. autopydantic_model:: ItemEntry
   :inherited-members: BaseModel

MountEntry
~~~~~~~~~~
.. autopydantic_model:: MountEntry
   :inherited-members: BaseModel

OutfitEntry
~~~~~~~~~~~
.. autopydantic_model:: OutfitEntry
   :inherited-members: BaseModel

Familiars
~~~~~~~~~
.. autopydantic_model:: Familiars
   :inherited-members: BaseModel

ItemSummary
~~~~~~~~~~~
.. autopydantic_model:: ItemSummary
   :inherited-members: BaseModel

Mounts
~~~~~~~~~~~
.. autopydantic_model:: Mounts
   :inherited-members: BaseModel

OutfitImage
~~~~~~~~~~~
.. autopydantic_model:: OutfitImage
   :inherited-members: BaseModel

Outfits
~~~~~~~
.. autopydantic_model:: Outfits
   :inherited-members: BaseModel

SalesArgument
~~~~~~~~~~~~~~
.. autopydantic_model:: SalesArgument
   :inherited-members: BaseModel

SkillEntry
~~~~~~~~~~
.. autopydantic_model:: SkillEntry
   :inherited-members: BaseModel

Kill Statistics
===============

KillStatistics
--------------
.. autopydantic_model:: KillStatistics
   :inherited-members: BaseModel

RaceEntry
---------
.. autopydantic_model:: RaceEntry
   :inherited-members: BaseModel

Library
=======

CreaturesSection
----------------
.. autopydantic_model:: CreaturesSection
   :inherited-members: BaseModel

Creature
--------
.. autopydantic_model:: Creature
   :inherited-members: BaseModel

CreatureEntry
-------------
.. autopydantic_model:: CreatureEntry
   :inherited-members: BaseModel

BoostableBosses
----------------
.. autopydantic_model:: BoostableBosses
   :inherited-members: BaseModel

BoostedCreatures
----------------
.. autopydantic_model:: BoostedCreatures
   :inherited-members: BaseModel

BossEntry
-------------
.. autopydantic_model:: BossEntry
   :inherited-members: BaseModel


SpellsSection
-------------
.. autopydantic_model:: SpellsSection
   :inherited-members: BaseModel

Spell
-----
.. autopydantic_model:: Spell
   :inherited-members: BaseModel

Rune
----------
.. autopydantic_model:: Rune
   :inherited-members: BaseModel

SpellEntry
----------
.. autopydantic_model:: SpellEntry
   :inherited-members: BaseModel

Base Classes
============
The following classes are not meant to be used or instantiated, but are documented here for informational purposes.

They implement methods and properties that can be inherited by other classes to implement their functionality.


.. autopydantic_model:: BaseModel
    :inherited-members:

.. autopydantic_model:: BaseAnnouncement
    :inherited-members: BaseModel

.. autopydantic_model:: BaseBoard
    :inherited-members: BaseModel

.. autopydantic_model:: BaseCharacter
    :inherited-members: BaseModel

.. autopydantic_model:: BaseGuild
    :inherited-members: BaseModel

.. autopydantic_model:: BaseHouse
    :inherited-members: BaseModel

.. autopydantic_model:: HouseWithId
    :inherited-members: BaseModel

.. autopydantic_model:: BaseNews
    :inherited-members: BaseModel

.. autopydantic_model:: BasePost
    :inherited-members: BaseModel

.. autopydantic_model:: BaseThread
    :inherited-members: BaseModel

.. autopydantic_model:: BaseWorld
    :inherited-members: BaseModel

.. currentmodule:: tibiapy.models.pagination

.. autopydantic_model:: Paginated
    :inherited-members: BaseModel

.. autopydantic_model:: PaginatedWithUrl
    :inherited-members: BaseModel

.. autopydantic_model:: AjaxPaginator
    :inherited-members: BaseModel

Parsers
=======
Parsers are used to convert to extract information from the HTML content of pages in Tibia.com.

The majority of users do not need to interact with these classes, but they can be used to provide alternate clients using other network libraries.

Most of the parsers support parsing the page displayed for no results (e.g. trying to parse the page for non-existent world `Fidera <https://www.tibia.com/community/?subtopic=worlds&world=Fidera>`_) by returning :obj:`None` instead of raising an exception.
Additionally, parsers attempt to detect when the HTML belongs to a different section by raising a :class:`.InvalidContent` exception.

.. currentmodule:: tibiapy

.. autoclass:: tibiapy.parsers.AuctionParser
    :members:

.. autoclass:: tibiapy.parsers.CharacterBazaarParser
    :members:

.. autoclass:: tibiapy.parsers.CharacterParser
   :members:

.. autoclass:: tibiapy.parsers.BoostableBossesParser
   :members:

.. autoclass:: tibiapy.parsers.BoostedCreaturesParser
   :members:

.. autoclass:: tibiapy.parsers.CreatureParser
   :members:

.. autoclass:: tibiapy.parsers.CreaturesSectionParser
   :members:

.. autoclass:: tibiapy.parsers.EventScheduleParser
   :members:

.. autoclass:: tibiapy.parsers.CMPostArchiveParser
   :members:

.. autoclass:: tibiapy.parsers.ForumAnnouncementParser
   :members:

.. autoclass:: tibiapy.parsers.ForumBoardParser
   :members:

.. autoclass:: tibiapy.parsers.ForumSectionParser
   :members:

.. autoclass:: tibiapy.parsers.ForumThreadParser
   :members:

.. autoclass:: tibiapy.parsers.GuildParser
   :members:

.. autoclass:: tibiapy.parsers.GuildsSectionParser
   :members:

.. autoclass:: tibiapy.parsers.GuildWarsParser
   :members:

.. autoclass:: tibiapy.parsers.HighscoresParser
   :members:

.. autoclass:: tibiapy.parsers.HousesSectionParser
   :members:

.. autoclass:: tibiapy.parsers.HouseParser
   :members:

.. autoclass:: tibiapy.parsers.KillStatisticsParser
   :members:

.. autoclass:: tibiapy.parsers.LeaderboardParser
   :members:

.. autoclass:: tibiapy.parsers.NewsArchiveParser
   :members:

.. autoclass:: tibiapy.parsers.NewsParser
   :members:

.. autoclass:: tibiapy.parsers.SpellsSectionParser
   :members:

.. autoclass:: tibiapy.parsers.SpellParser
   :members:

.. autoclass:: tibiapy.parsers.WorldParser
   :members:

.. autoclass:: tibiapy.parsers.WorldOverviewParser
   :members:

Exceptions
==========
.. currentmodule:: tibiapy

.. autoclass:: TibiapyException

.. autoclass:: InvalidContent

.. autoclass:: NetworkError

.. autoclass:: SiteMaintenanceError

.. autoclass:: Forbidden


Utility functions
==================

.. automodule:: tibiapy.utils
   :members:

URL functions
==================

.. automodule:: tibiapy.urls
   :members:

