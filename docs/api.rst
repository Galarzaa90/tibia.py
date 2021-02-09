.. currentmodule:: tibiapy

=============
API Reference
=============
This module implements a variety of classes used to hold the data parsed from Tibia.com.

These objects are generally obtained from their respective ``from_content`` methods.
It is possible to create and edit these objects as desired, but it may lead to unexpected behaviour if not done properly.

Client
======

.. autoclass:: Client
    :members:

.. autoclass:: TibiaResponse
    :members:

Enumerations
============
Enumerations are provided for various values in order to avoid depending on strings.

.. autoclass:: AccountStatus
    :members:
    :undoc-members:

.. autoclass:: AuctionOrder
    :members:
    :undoc-members:

.. autoclass:: AuctionOrderBy
    :members:
    :undoc-members:

.. autoclass:: AuctionSearchType
    :members:
    :undoc-members:

.. autoclass:: AuctionStatus
    :members:
    :undoc-members:

.. autoclass:: BattlEyeHighscoresFilter
    :members:
    :undoc-members:

.. autoclass:: BattlEyeTypeFilter
    :members:
    :undoc-members:

.. autoclass:: BazaarType
    :members:
    :undoc-members:

.. autoclass:: BidType
    :members:
    :undoc-members:

.. autoclass:: Category
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

.. autoclass:: PvpTypeFilter
    :members:
    :undoc-members:

.. autoclass:: PvpType
    :members:
    :undoc-members:

.. autoclass:: Sex
    :members:
    :undoc-members:

.. autoclass:: SkillFilter
    :members:
    :undoc-members:

.. autoclass:: ThreadStatus
    :members:
    :undoc-members:

.. autoclass:: TournamentWorldType
    :members:
    :undoc-members:

.. autoclass:: TournamentPhase
    :members:
    :undoc-members:

.. autoclass:: TransferType
    :members:
    :undoc-members:

.. autoclass:: Vocation
    :members:
    :undoc-members:

.. autoclass:: VocationAuctionFilter
    :members:
    :undoc-members:

.. autoclass:: VocationFilter
    :members:
    :undoc-members:

.. autoclass:: WorldLocation
    :members:
    :undoc-members:


Characters
===========
The `Character section`_ consists of the :class:`Character` class and its auxiliary classes used to hold its data.

The entry points for this are:

- :meth:`Character.from_content` - Parsing a character's content.
- :meth:`Client.fetch_character` - Fetching and parsing a character's content.

.. _Character section: https://www.tibia.com/community/?subtopic=characters

Character
---------
.. autoclass:: Character
   :members:
   :inherited-members:

Auxiliary Classes
-----------------

AccountBadge
~~~~~~~~~~~~
.. autoclass:: AccountBadge
   :members:
   :inherited-members:

AccountInformation
~~~~~~~~~~~~~~~~~~
.. autoclass:: AccountInformation
   :members:
   :inherited-members:

Achievement
~~~~~~~~~~~
.. autoclass:: Achievement
   :members:
   :inherited-members:

CharacterHouse
~~~~~~~~~~~~~~
.. autoclass:: CharacterHouse
   :members:
   :inherited-members:

Death
~~~~~
.. autoclass:: Death
   :members:
   :inherited-members:

GuildMembership
~~~~~~~~~~~~~~~
.. autoclass:: GuildMembership
   :members:
   :inherited-members:

Killer
~~~~~~
.. autoclass:: Killer
   :members:
   :inherited-members:

OtherCharacter
~~~~~~~~~~~~~~
.. autoclass:: OtherCharacter
   :members:
   :inherited-members:

Worlds
======
Models related to `Tibia.com's World section`_. The :class:`WorldOverview` class contains the list of all worlds, while
the :class:`World` class contains the details of a single world.

.. _Tibia.com's World section: https://www.tibia.com/community/?subtopic=worlds

WorldOverview
-------------
.. autoclass:: WorldOverview
   :members:
   :inherited-members:

ListedWorld
-----------
.. autoclass:: ListedWorld
   :members:
   :inherited-members:

World
-----
.. autoclass:: World
   :members:
   :inherited-members:

OnlineCharacter
---------------
.. autoclass:: OnlineCharacter
   :members:
   :inherited-members:

Guilds
======
Models related to `Tibia.com's Guilds section`_. The main model is :class:`Guild`, while :class:`ListedGuild` is the
previewed information in the guild list.

.. _Tibia.com's Guilds section: https://www.tibia.com/community/?subtopic=guilds

Guild
-----
.. autoclass:: Guild
   :members:
   :inherited-members:

ListedGuild
-----------
.. autoclass:: ListedGuild
   :members:
   :inherited-members:

Auxiliary Classes
-----------------
GuildInvite
~~~~~~~~~~~
.. autoclass:: GuildInvite
   :members:
   :inherited-members:

GuildHouse
~~~~~~~~~~
.. autoclass:: GuildHouse
   :members:
   :inherited-members:

GuildMember
~~~~~~~~~~~
.. autoclass:: GuildMember
   :members:
   :inherited-members:

GuildWars
~~~~~~~~~
.. autoclass:: GuildWars
   :members:
   :inherited-members:

GuildWarEntry
~~~~~~~~~~~~~
.. autoclass:: GuildWarEntry
   :members:
   :inherited-members:

Highscores
==========
Models related to `Tibia.com's Highscores section`_.

.. _Tibia.com's Highscores section: https://www.tibia.com/community/?subtopic=highscores

Highscores
----------
.. autoclass:: Highscores
   :members:
   :inherited-members:

HighscoresEntry
---------------
.. autoclass:: HighscoresEntry
   :members:
   :inherited-members:

LoyaltyHighscoresEntry
----------------------
.. autoclass:: LoyaltyHighscoresEntry
   :members:
   :inherited-members:

Houses
======
Models related to `Tibia.com's Houses section`_.

.. _Tibia.com's Houses section: https://www.tibia.com/community/?subtopic=houses

House
-----
.. autoclass:: House
   :members:
   :inherited-members:

ListedHouse
-----------
.. autoclass:: ListedHouse
   :members:
   :inherited-members:

Tournaments
===========
Models related to `Tibia.com's Tournaments section`_.

.. _Tibia.com's Tournaments section: https://www.tibia.com/community/?subtopic=tournament

Tournament
----------
.. autoclass:: Tournament
   :members:
   :inherited-members:

TournamentLeaderboard
---------------------
.. autoclass:: TournamentLeaderboard
   :members:
   :inherited-members:

Auxiliary Classes
-----------------

ListedTournament
~~~~~~~~~~~~~~~~
.. autoclass:: ListedTournament
   :members:
   :inherited-members:

LeaderboardEntry
~~~~~~~~~~~~~~~~
.. autoclass:: LeaderboardEntry
   :members:
   :inherited-members:

RewardEntry
~~~~~~~~~~~
.. autoclass:: RewardEntry
   :members:
   :inherited-members:


RuleSet
~~~~~~~
.. autoclass:: RuleSet
   :members:
   :inherited-members:

ScoreSet
~~~~~~~~
.. autoclass:: ScoreSet
   :members:
   :inherited-members:

Forums
======
Models related to `Tibia.com's Forum section`_.

.. _Tibia.com's Forum section: https://www.tibia.com/community/?subtopic=worldboards

CMPostArchive
-------------
.. autoclass:: CMPostArchive
   :members:
   :inherited-members:

ForumAnnouncement
-----------------
.. autoclass:: ForumAnnouncement
    :members:
    :inherited-members:

ForumBoard
----------
.. autoclass:: ForumBoard
    :members:
    :inherited-members:

ForumPost
---------
.. autoclass:: ForumPost
    :members:
    :inherited-members:

ForumThread
-----------
.. autoclass:: ForumThread
    :members:
    :inherited-members:

ListedAnnouncement
------------------
.. autoclass:: ListedAnnouncement
    :members:
    :inherited-members:

ListedBoard
-----------
.. autoclass:: ListedBoard
    :members:
    :inherited-members:

ListedThread
------------
.. autoclass:: ListedThread
    :members:
    :inherited-members:

Auxiliary Classes
-----------------
CMPost
~~~~~~
.. autoclass:: CMPost
   :members:
   :inherited-members:

ForumAuthor
~~~~~~~~~~~
.. autoclass:: ForumAuthor
    :members:
    :inherited-members:

ForumEmoticon
~~~~~~~~~~~~~
.. autoclass:: ForumEmoticon
    :members:
    :inherited-members:

LastPost
~~~~~~~~
.. autoclass:: LastPost
    :members:
    :inherited-members:


News
=======
Models related to `Tibia.com's News section`_.

.. _Tibia.com's News section: https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades

News
---------
.. autoclass:: News
   :members:
   :inherited-members:


ListedNews
-----------
.. autoclass:: ListedNews
   :members:
   :inherited-members:

EventSchedule
-------------
.. autoclass:: EventSchedule
   :members:
   :inherited-members:

EventEntry
-------------
.. autoclass:: EventEntry
   :members:
   :inherited-members:

Bazaar
======
Models related to `Tibia.com's Bazaar section`_.

.. _Tibia.com's Bazaar section: https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades

CharacterBazaar
---------------
.. autoclass:: CharacterBazaar
   :members:
   :inherited-members:

ListedAuction
-------------
.. autoclass:: ListedAuction
    :members:
    :inherited-members:

AuctionDetails
---------------
.. autoclass:: AuctionDetails
   :members:
   :inherited-members:

Auxiliary Classes
-----------------

AchievementEntry
~~~~~~~~~~~~~~~~
.. autoclass:: AchievementEntry
   :members:
   :inherited-members:

AuctionFilters
~~~~~~~~~~~~~~
.. autoclass:: AuctionFilters
   :members:
   :inherited-members:


BestiaryEntry
~~~~~~~~~~~~~
.. autoclass:: BestiaryEntry
   :members:
   :inherited-members:

BlessingEntry
~~~~~~~~~~~~~
.. autoclass:: BlessingEntry
   :members:
   :inherited-members:

CharmsEntry
~~~~~~~~~~~
.. autoclass:: CharmEntry
   :members:
   :inherited-members:

DisplayFamiliar
~~~~~~~~~~~~~~~
.. autoclass:: DisplayFamiliar
   :members:
   :inherited-members:

DisplayItem
~~~~~~~~~~~
.. autoclass:: DisplayItem
   :members:
   :inherited-members:

DisplayMount
~~~~~~~~~~~~
.. autoclass:: DisplayMount
   :members:
   :inherited-members:

DisplayOutfit
~~~~~~~~~~~~~
.. autoclass:: DisplayOutfit
   :members:
   :inherited-members:

Familiars
~~~~~~~~~
.. autoclass:: Familiars
   :members:
   :inherited-members:

ItemSummary
~~~~~~~~~~~
.. autoclass:: ItemSummary
   :members:
   :inherited-members:

Mounts
~~~~~~~~~~~
.. autoclass:: Mounts
   :members:
   :inherited-members:

OutfitImage
~~~~~~~~~~~
.. autoclass:: OutfitImage
   :members:
   :inherited-members:

Outfits
~~~~~~~
.. autoclass:: Outfits
   :members:
   :inherited-members:

SalesArgument
~~~~~~~~~~~~~~
.. autoclass:: SalesArgument
   :members:
   :inherited-members:

SkillEntry
~~~~~~~~~~
.. autoclass:: SkillEntry
   :members:
   :inherited-members:

Kill Statistics
===============

KillStatistics
--------------
.. autoclass:: KillStatistics
   :members:
   :inherited-members:

RaceEntry
---------
.. autoclass:: RaceEntry
   :members:
   :inherited-members:

Other
=====

BoostedCreature
---------------
.. autoclass:: BoostedCreature
   :members:
   :inherited-members:


Base Classes
============
The following classes are not meant to be used or instantiated, but are documented here for informational purposes.

They implement methods and properties that can be inherited by other classes to implement their functionality.


.. autoclass:: tibiapy.abc.BaseAnnouncement
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseBoard
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseCharacter
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseGuild
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseHouse
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.HouseWithId
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseNews
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BasePost
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseThread
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseTournament
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseWorld
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.Serializable
    :members:
    :inherited-members:

Exceptions
==========
.. autoclass:: TibiapyException

.. autoclass:: InvalidContent

.. autoclass:: NetworkError

.. autoclass:: SiteMaintenanceError

.. autoclass:: Forbidden

Utility functions
==================
These are functions used thorough the module that may not be intended for public use.

.. automodule:: tibiapy.utils
   :members:

