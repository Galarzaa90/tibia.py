.. currentmodule:: tibiapy

=============
API Reference
=============
This module implements a variety of classes used to hold the data parsed from Tibia.com.

These objects are generally obtained from their respective ``from_content`` methods.
It is possible to create and edit these objects as desired, but it may lead to unexpected behaviour if not done properly.

Main Models
===========
The following models all contain their respective ``from_content`` methods.
They all have their respective section in Tibia.com

Character
----------
.. autoclass:: Character
   :members:
   :inherited-members:

Guild
-----------
.. autoclass:: Guild
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

Death
-----------
.. autoclass:: Death
   :members:
   :inherited-members:

GuildInvite
-----------------
.. autoclass:: GuildInvite
   :members:
   :inherited-members:

GuildMember
-----------------
.. autoclass:: GuildMember
   :members:
   :inherited-members:

Killer
----------------
.. autoclass:: Killer
   :members:
   :inherited-members:

OnlineCharacter
----------------
.. autoclass:: OnlineCharacter
   :members:
   :inherited-members:

OtherCharacter
-----------------
.. autoclass:: OtherCharacter
   :members:
   :inherited-members:

Base Classes
============
The following classes are not meant to be used or instantiated, but are documented here for informational purposes.

They implement methods and properties that can be inherited by other classes to implement their functionality.

.. autoclass:: tibiapy.abc.Character
    :members:
    :inherited-members:

.. autoclass:: tibiapy.abc.Serializable
    :members:
    :inherited-members:

Utility functions
==================
.. automodule:: tibiapy.utils
   :members: