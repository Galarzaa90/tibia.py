.. currentmodule:: tibiapy

=============
API Reference
=============
This module implements a variety of classes used to hold the data parsed from Tibia.com.

Client
======

.. autoclass:: Client
    :members:

.. autopydantic_model:: tibiapy.models.TibiaResponse
   :inherited-members: BaseModel

.. currentmodule:: tibiapy.enums

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

Models
======
These are the classes that defined the models used by Tibia.py.

While it is possible to create instances of these models, their purpose is to be used as data containers.


Characters
----------
The `Character section`_ consists of the :class:`Character` class and its auxiliary classes used to hold its data.


.. _Character section: https://www.tibia.com/community/?subtopic=characters


.. autopydantic_model:: Character
   :inherited-members: BaseModel


.. autopydantic_model:: AccountBadge
   :inherited-members: BaseModel


.. autopydantic_model:: AccountInformation
   :inherited-members: BaseModel


.. autopydantic_model:: Achievement
   :inherited-members: BaseModel


.. autopydantic_model:: CharacterHouse
   :inherited-members: BaseModel


.. autopydantic_model:: Death
   :inherited-members: BaseModel


.. autopydantic_model:: GuildMembership
   :inherited-members: BaseModel


.. autopydantic_model:: DeathParticipant
   :inherited-members: BaseModel


.. autopydantic_model:: OtherCharacter
   :inherited-members: BaseModel

Worlds
------
Models related to `Tibia.com's World section`_. The :class:`WorldOverview` class contains the list of all worlds, while
the :class:`World` class contains the details of a single world.

.. _Tibia.com's World section: https://www.tibia.com/community/?subtopic=worlds


.. autopydantic_model:: WorldOverview
   :inherited-members: BaseModel


.. autopydantic_model:: WorldEntry
   :inherited-members: BaseModel


.. autopydantic_model:: World
   :inherited-members: BaseModel


.. autopydantic_model:: OnlineCharacter
   :inherited-members: BaseModel

Guilds
------
Models related to `Tibia.com's Guilds section`_. The main model is :class:`Guild`, while :class:`GuildEntry` is the
previewed information in the guild list of the :class:`GuildsSection`.

.. _Tibia.com's Guilds section: https://www.tibia.com/community/?subtopic=guilds

.. autopydantic_model:: GuildsSection
   :inherited-members: BaseModel


.. autopydantic_model:: Guild
   :inherited-members: BaseModel


.. autopydantic_model:: GuildEntry
   :inherited-members: BaseModel


.. autopydantic_model:: GuildInvite
  :inherited-members: BaseModel


.. autopydantic_model:: GuildHouse
   :inherited-members: BaseModel


.. autopydantic_model:: GuildMember
   :inherited-members: BaseModel


.. autopydantic_model:: GuildWars
   :inherited-members: BaseModel


.. autopydantic_model:: GuildWarEntry
   :inherited-members: BaseModel

Highscores
----------
Models related to `Tibia.com's Highscores section`_.

.. _Tibia.com's Highscores section: https://www.tibia.com/community/?subtopic=highscores


.. autopydantic_model:: Highscores
   :inherited-members: BaseModel


.. autopydantic_model:: HighscoresEntry
   :inherited-members: BaseModel


.. autopydantic_model:: LoyaltyHighscoresEntry
   :inherited-members: BaseModel

Houses
------
Models related to `Tibia.com's Houses section`_.

.. _Tibia.com's Houses section: https://www.tibia.com/community/?subtopic=houses


.. autopydantic_model:: HousesSection
   :inherited-members: BaseModel


.. autopydantic_model:: House
   :inherited-members: BaseModel


.. autopydantic_model:: HouseEntry
   :inherited-members: BaseModel

Leaderboard
-----------
Models related to `Tibia.com's Leaderboard section`_.

.. _Tibia.com's Leaderboard section: https://www.tibia.com/community/?subtopic=tournament


.. autopydantic_model:: Leaderboard
   :inherited-members: BaseModel


.. autopydantic_model:: LeaderboardRotation
   :inherited-members: BaseModel


.. autopydantic_model:: LeaderboardEntry
   :inherited-members: BaseModel

Forums
------
Models related to `Tibia.com's Forum section`_.

.. _Tibia.com's Forum section: https://www.tibia.com/community/?subtopic=worldboards


.. autopydantic_model:: CMPostArchive
   :inherited-members: BaseModel


.. autopydantic_model:: ForumSection
   :inherited-members: BaseModel


.. autopydantic_model:: ForumAnnouncement
   :inherited-members: BaseModel


.. autopydantic_model:: ForumBoard
   :inherited-members: BaseModel


.. autopydantic_model:: ForumPost
   :inherited-members: BaseModel


.. autopydantic_model:: ForumThread
   :inherited-members: BaseModel


.. autopydantic_model:: AnnouncementEntry
   :inherited-members: BaseModel


.. autopydantic_model:: BoardEntry
   :inherited-members: BaseModel


.. autopydantic_model:: ThreadEntry
   :inherited-members: BaseModel


.. autopydantic_model:: CMPost
   :inherited-members: BaseModel


.. autopydantic_model:: ForumAuthor
   :inherited-members: BaseModel



.. autopydantic_model:: ForumEmoticon
   :inherited-members: BaseModel


.. autopydantic_model:: LastPost
   :inherited-members: BaseModel


News
----
Models related to `Tibia.com's News section`_. This also contains the `Event Calendar`_

.. _Tibia.com's News section: https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades
.. _Event Calendar: https://www.tibia.com/news/?subtopic=eventcalendar


.. autopydantic_model:: NewsArchive
   :inherited-members: BaseModel


.. autopydantic_model:: News
   :inherited-members: BaseModel


.. autopydantic_model:: NewsEntry
   :inherited-members: BaseModel


.. autopydantic_model:: EventSchedule
   :inherited-members: BaseModel


.. autopydantic_model:: EventEntry
   :inherited-members: BaseModel

Bazaar
------
Models related to `Tibia.com's Bazaar section`_.

.. _Tibia.com's Bazaar section: https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades


.. autopydantic_model:: CharacterBazaar
   :inherited-members: BaseModel


.. autopydantic_model:: Auction
   :inherited-members: BaseModel


.. autopydantic_model:: AuctionDetails
   :inherited-members: BaseModel


.. autopydantic_model:: AchievementEntry
   :inherited-members: BaseModel


.. autopydantic_model:: AuctionFilters
   :inherited-members: BaseModel


.. autopydantic_model:: BestiaryEntry
   :inherited-members: BaseModel


.. autopydantic_model:: BlessingEntry
   :inherited-members: BaseModel


.. autopydantic_model:: CharmEntry
   :inherited-members: BaseModel


.. autopydantic_model:: FamiliarEntry
   :inherited-members: BaseModel


.. autopydantic_model:: ItemEntry
   :inherited-members: BaseModel


.. autopydantic_model:: MountEntry
   :inherited-members: BaseModel


.. autopydantic_model:: OutfitEntry
   :inherited-members: BaseModel


.. autopydantic_model:: Familiars
   :inherited-members: BaseModel


.. autopydantic_model:: ItemSummary
   :inherited-members: BaseModel


.. autopydantic_model:: Mounts
   :inherited-members: BaseModel


.. autopydantic_model:: OutfitImage
   :inherited-members: BaseModel


.. autopydantic_model:: Outfits
   :inherited-members: BaseModel


.. autopydantic_model:: SalesArgument
   :inherited-members: BaseModel


.. autopydantic_model:: SkillEntry
   :inherited-members: BaseModel


.. autopydantic_model:: RevealedGem
   :inherited-members: BaseModel


Kill Statistics
---------------


.. autopydantic_model:: KillStatistics
   :inherited-members: BaseModel


.. autopydantic_model:: RaceEntry
   :inherited-members: BaseModel

Library
-------


.. autopydantic_model:: CreaturesSection
   :inherited-members: BaseModel


.. autopydantic_model:: Creature
   :inherited-members: BaseModel


.. autopydantic_model:: CreatureEntry
   :inherited-members: BaseModel


.. autopydantic_model:: BoostableBosses
   :inherited-members: BaseModel


.. autopydantic_model:: BoostedCreatures
   :inherited-members: BaseModel


.. autopydantic_model:: BossEntry
   :inherited-members: BaseModel



.. autopydantic_model:: SpellsSection
   :inherited-members: BaseModel


.. autopydantic_model:: Spell
   :inherited-members: BaseModel


.. autopydantic_model:: Rune
   :inherited-members: BaseModel


.. autopydantic_model:: SpellEntry
   :inherited-members: BaseModel

Library
-------
.. autopydantic_model:: FansitesSection
   :inherited-members: BaseModel

.. autopydantic_model:: Fansite
   :inherited-members: BaseModel

.. autopydantic_model:: FansiteSocialMedia
   :inherited-members: BaseModel

.. autopydantic_model:: FansiteContent
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

.. _api_parsers:


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

.. autoclass:: tibiapy.parsers.FansitesSectionParser
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

