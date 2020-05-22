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

Enumerations
============
Enumerations are provided for various values in order to avoid depending on strings.


.. autoclass:: AccountStatus
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

.. autoclass:: PvpType
    :members:
    :undoc-members:

.. autoclass:: Sex
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

.. autoclass:: VocationFilter
    :members:
    :undoc-members:

    .. automethod:: VocationFilter.from_name

.. autoclass:: WorldLocation
    :members:
    :undoc-members:

Main Models
===========
The following models all contain their respective ``from_content`` methods.
They all have their respective section in Tibia.com

BoostedCreature
---------------
.. autoclass:: BoostedCreature
   :members:
   :inherited-members:

Character
---------
.. autoclass:: Character
   :members:
   :inherited-members:

Guild
-----
.. autoclass:: Guild
   :members:
   :inherited-members:

Highscores
----------
.. autoclass:: Highscores
   :members:
   :inherited-members:

House
-----
.. autoclass:: House
   :members:
   :inherited-members:

KillStatistics
--------------
.. autoclass:: KillStatistics
   :members:
   :inherited-members:

ListedGuild
-----------
.. autoclass:: ListedGuild
   :members:
   :inherited-members:

ListedHouse
-----------
.. autoclass:: ListedHouse
   :members:
   :inherited-members:

ListedNews
-----------
.. autoclass:: ListedNews
   :members:
   :inherited-members:

ListedTournament
-----------------------
.. autoclass:: ListedTournament
   :members:
   :inherited-members:

ListedWorld
-----------
.. autoclass:: ListedWorld
   :members:
   :inherited-members:

News
---------
.. autoclass:: News
   :members:
   :inherited-members:

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

World
-----
.. autoclass:: World
   :members:
   :inherited-members:

WorldOverview
-------------
.. autoclass:: WorldOverview
   :members:
   :inherited-members:

Auxiliary Classes
=================
Auxiliary classes are used to hold certain data in a standardized way, in some cases, introducing additional methods
and properties for their use.

AccountBadge
------------------
.. autoclass:: AccountBadge
   :members:
   :inherited-members:

AccountInformation
------------------
.. autoclass:: AccountInformation
   :members:
   :inherited-members:

Achievement
--------------
.. autoclass:: Achievement
   :members:
   :inherited-members:

CharacterHouse
--------------
.. autoclass:: CharacterHouse
   :members:
   :inherited-members:

ExpHighscoresEntry
-------------------------
.. autoclass:: ExpHighscoresEntry
   :members:
   :inherited-members:

Death
-----
.. autoclass:: Death
   :members:
   :inherited-members:

GuildHouse
----------
.. autoclass:: GuildHouse
   :members:
   :inherited-members:

GuildInvite
-----------
.. autoclass:: GuildInvite
   :members:
   :inherited-members:

GuildMember
-----------
.. autoclass:: GuildMember
   :members:
   :inherited-members:

GuildMembership
---------------
.. autoclass:: GuildMembership
   :members:
   :inherited-members:


HighscoresEntry
---------------
.. autoclass:: HighscoresEntry
   :members:
   :inherited-members:

Killer
------
.. autoclass:: Killer
   :members:
   :inherited-members:

LeaderboardEntry
----------------
.. autoclass:: LeaderboardEntry
   :members:
   :inherited-members:

LoyaltyHighscoresEntry
----------------------
.. autoclass:: LoyaltyHighscoresEntry
   :members:
   :inherited-members:

OnlineCharacter
---------------
.. autoclass:: OnlineCharacter
   :members:
   :inherited-members:

OtherCharacter
--------------
.. autoclass:: OtherCharacter
   :members:
   :inherited-members:

RaceEntry
---------
.. autoclass:: RaceEntry
   :members:
   :inherited-members:

RewardEntry
-----------
.. autoclass:: RewardEntry
   :members:
   :inherited-members:

RuleSet
-------
.. autoclass:: RuleSet
   :members:
   :inherited-members:

ScoreSet
--------
.. autoclass:: ScoreSet
   :members:
   :inherited-members:

Base Classes
============
The following classes are not meant to be used or instantiated, but are documented here for informational purposes.

They implement methods and properties that can be inherited by other classes to implement their functionality.

.. autoclass:: tibiapy.abc.BaseCharacter
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseGuild
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseHouse
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseHouseWithId
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.BaseNews
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

.. autoclass:: Forbidden

Utility functions
==================
These are functions used thorough the module that may not be intended for public use.

.. automodule:: tibiapy.utils
   :members:

