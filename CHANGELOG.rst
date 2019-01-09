=========
Changelog
=========

.. _v1.1.0:

1.1.0 (2019-01-09)
==================

- Parsing Highscores from Tibia.com and TibiaData.
- Some strings from TibiaData had unpredictable trailing whitespaces,
  all leading and trailing whitespaces are removed.
- Added type hints to many variables and methods.

.. _v1.0.0:

1.0.0 (2018-12-23)
==================

-  Added support for TibiaData JSON parsing. To have interoperability
   between Tibia.com and TibiaData.
-  Added support for parsing Houses, House lists, World and World list
-  Added support for many missing attributes in Character and Guilds.
-  All objects are now serializable to JSON strings.

.. _v0.1.0:

0.1.0 (2018-08-17)
==================

Initial release:

-  Parses content from tibia.com

   -  Character pages
   -  Guild pages
   -  Guild list pages

-  Parses content into JSON format strings.
-  Parses content into Python objects.