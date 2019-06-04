=========
Changelog
=========

.. note::
    Due to this library relying on external content, older versions are not guaranteed to work.
    Try to always use the latest version.

.. _v2.0.1:

2.0.1 (2019-06-04)
==================

- Replaced references to ``secure.tibia.com`` with ``www.tibia.com`` as the former always redirects to the front page.

.. _v2.0.0:

2.0.0 (2019-06-03)
==================

- Added asynchronous client to fetch and parse Tibia.com sections.
- Added news parsing.
- Added kill statistics parsing.
- Added support for tournament worlds.
- Added support for house prices with 'k' suffixes.

.. _v1.1.3:

1.1.3 (2019-01-29)
==================

- Fixed incorrect parsing of deaths with summons involved when parsing characters from TibiaData.

.. _v1.1.2:

1.1.2 (2019-01-22)
==================

- Fixed TibiaData URLs of tibia characters with special characters in their names. (e.g Himmelhüpferin)

.. _v1.1.1:

1.1.1 (2019-01-09)
==================

- Fixed character houses having attributes mixed up.

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
