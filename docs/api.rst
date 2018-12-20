.. currentmodule:: tibiapy

=============
API Reference
=============
This module implements a variety of classes used to hold the data parsed from Tibia.com.

These objects are generally obtained from their respective ``from_content`` methods.
It is possible to create and edit these objects as desired, but it may lead to unexpected behaviour if not done properly.

Enumerations
============
Enumerations are provided for various values in order to avoid depending on strings.

.. autoclass:: HouseType
    :members:
    :undoc-members:

.. autoclass:: AccountStatus
    :members:
    :undoc-members:

.. autoclass:: HouseStatus
    :members:
    :undoc-members:

.. autoclass:: PvpType
    :members:
    :undoc-members:

.. autoclass:: Sex
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

Main Models
===========
The following models all contain their respective ``from_content`` methods.
They all have their respective section in Tibia.com

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

House
-----
.. autoclass:: House
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

WorldOverview
-------------
.. autoclass:: WorldOverview
   :members:
   :inherited-members:

Auxiliary Classes
=================
Auxiliary classes are used to hold certain data in a standardized way, in some cases, introducing additional methods
and properties for their use.

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

Killer
------
.. autoclass:: Killer
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

Utility functions
==================
.. automodule:: tibiapy.utils
   :members:

