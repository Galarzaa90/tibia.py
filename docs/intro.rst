.. currentmodule:: tibiapy

============
Introduction
============

Prerequisites
=============
Tibia.py requires Python 3.6 or higher.
Dependencies are installed automatically when installing the package.

However, since it uses ``lxml`` for parsing, on Linux you may require to install libxml on your system.


.. code-block:: shell

    sudo apt-get install libxml2-dev libxslt-dev python-dev

Windows users are usually safe from this. For more information check out `lxml installation page`_.



Installation
============
Tibia.py can be installed from `PyPi`_ using:

.. code-block:: shell

    python -m pip install tibia.py

.. _lxml installation page: https://lxml.de/installation.html
.. _PyPi: https://pypi.org/

Usage
=====
This library is composed of two parts, parsers and an asynchronous request client.

The asynchronous client (:class:`tibiapy.Client`) contains methods to obtain information from Tibia.com.

The parsing methods allow you to get Python objects given the HTML content of a page.

The ``tibiapy.urls`` package contains many methods to get URLs for Tibia.com.

With the URL, the HTML content can be fetched and then passed to the respective class from the available :ref:`api_parsers`.

This allows you to use any networking library (e.g. aiohttp, requests, httpx) to obtain the data, and use the library to parse it.

.. code-block:: python

    import requests
    import tibiapy
    from tibiapy.parsers import CharacterParser

    # Fetching a character using requests instead of aiohttp
    def get_character(name):
        url = tibiapy.urls.get_character_url(name)

        r = requests.get(url)
        content = r.text
        return CharacterParser.from_content(content)

On the other hand, using the built-in asynchronous client you can do the fetching and parsing in one step:

.. code-block:: python

    import asyncio
    import tibiapy

    async def main():
        client = tibiapy.Client()
        character = await client.fetch_character("Galarzaa Fidera")
        await client.session.close()

    if __name__ == "__main__":
        asyncio.get_event_loop().run_until_complete(main())


Supported Sections
==================

.. currentmodule:: tibiapy

+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
|             Section              |                           Parsing                            |                  Fetching                   |
+==================================+==============================================================+=============================================+
| `Boostable Bosses`_ (List)       | :meth:`tibiapy.parsers.BoostableBossesParser.from_content`   | :meth:`Client.fetch_boostable_bosses`       |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Characters_                      | :meth:`tibiapy.parsers.CharacterParser.from_content`         | :meth:`Client.fetch_character`              |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| `Character Bazaar`_ (Current)    | :meth:`tibiapy.parsers.CharacterBazaarParser.from_content`   | :meth:`Client.fetch_current_auctions`       |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| `Character Bazaar`_ (History)    | :meth:`tibiapy.parsers.CharacterBazaarParser.from_content`   | :meth:`Client.fetch_auction_history`        |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| `Character Bazaar`_ (Detail)     | :meth:`tibiapy.parsers.AuctionParser.from_content`           | :meth:`Client.fetch_auction`                |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| `CM Post Archive`_               | :meth:`tibiapy.parsers.CMPostArchiveParser.from_content`     | :meth:`Client.fetch_cm_post_archive`        |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| `Creature Library`_ (List)       | :meth:`tibiapy.parsers.CreaturesSectionParser.from_content`  | :meth:`Client.fetch_creatures`              |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| `Creature Library`_ (Individual) | :meth:`tibiapy.parsers.CreatureParser.from_content`          | :meth:`Client.fetch_creature`               |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| `Event Schedule`_                | :meth:`tibiapy.parsers.EventScheduleParser.from_content`     | :meth:`Client.fetch_event_schedule`         |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Guilds_ (Individual)             | :meth:`tibiapy.parsers.GuildParser.from_content`             | :meth:`Client.fetch_guild`                  |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Guilds_ (List)                   | :meth:`tibiapy.parsers.GuildsSectionParser.from_content`     | :meth:`Client.fetch_world_guilds`           |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Guilds_ (Wars)                   | :meth:`tibiapy.parsers.GuildWarsParser.from_content`         | :meth:`Client.fetch_guild_wars`             |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Fansites_                        | :meth:`tibiapy.parsers.FansitesSectionParser.from_content`   | :meth:`Client.fetch_fansites_section`       |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Forums_ (Section)                | :meth:`tibiapy.parsers.ForumSectionParser.from_content`      | :meth:`Client.fetch_forum_world_boards`     |
|                                  |                                                              | :meth:`Client.fetch_forum_trade_boards`     |
|                                  |                                                              | :meth:`Client.fetch_forum_community_boards` |
|                                  |                                                              | :meth:`Client.fetch_forum_support_boards`   |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Forums_ (Board)                  | :meth:`tibiapy.parsers.ForumBoardParser.from_content`        | :meth:`Client.fetch_forum_board`            |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Forums_ (Announcement)           | :meth:`tibiapy.parsers.ForumAnnouncementParser.from_content` | :meth:`Client.fetch_forum_announcement`     |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Forums_ (Thread)                 | :meth:`tibiapy.parsers.ForumThreadParser.from_content`       | :meth:`Client.fetch_forum_thread`           |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Highscores_                      | :meth:`tibiapy.parsers.HighscoresParser.from_content`        | :meth:`Client.fetch_highscores_page`        |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Houses_ (Individual)             | :meth:`tibiapy.parsers.HouseParser.from_content`             | :meth:`Client.fetch_house`                  |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Houses_ (List)                   | :meth:`tibiapy.parsers.HousesSectionParser.from_content`     | :meth:`Client.fetch_houses_section`         |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| `Kill Statistics`_ (List)        | :meth:`tibiapy.parsers.KillStatisticsParser.from_content`    | :meth:`Client.fetch_kill_statistics`        |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Leaderboards_                    | :meth:`tibiapy.parsers.LeaderboardParser.from_content`       | :meth:`Client.fetch_leaderboard`            |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| News_ (Individual)               | :meth:`tibiapy.parsers.NewsParser.from_content`              | :meth:`Client.fetch_news`                   |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| News_ (List)                     | :meth:`tibiapy.parsers.NewsArchiveParser.from_content`       | :meth:`Client.fetch_news_archive`           |
|                                  |                                                              | :meth:`Client.fetch_news_archive_by_days`   |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| `Spell Library`_ (List)          | :meth:`tibiapy.parsers.SpellsSectionParser.from_content`     | :meth:`Client.fetch_spells`                 |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| `Spell Library`_ (Individual)    | :meth:`tibiapy.parsers.SpellParser.from_content`             | :meth:`Client.fetch_spell`                  |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Worlds_ (Individual)             | :meth:`tibiapy.parsers.WorldParser.from_content`             | :meth:`Client.fetch_world`                  |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+
| Worlds_ (List)                   | :meth:`tibiapy.parsers.WorldOverviewParser.from_content`     | :meth:`Client.fetch_world_overview`         |
+----------------------------------+--------------------------------------------------------------+---------------------------------------------+


.. _Boostable Bosses: https://www.tibia.com/library/?subtopic=boostablebosses
.. _Characters: https://www.tibia.com/community/?subtopic=characters
.. _Character Bazaar: https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades
.. _CM Post Archive: https://www.tibia.com/forum/?subtopic=forum&action=cm_post_archive
.. _Creature Library: https://www.tibia.com/library/?subtopic=creatures
.. _Event Schedule: https://www.tibia.com/news/?subtopic=eventcalendar
.. _Guilds: https://www.tibia.com/community/?subtopic=guilds
.. _Fansites: https://www.tibia.com/community/?subtopic=fansites
.. _Forums: https://www.tibia.com/community/?subtopic=forum
.. _Highscores: https://www.tibia.com/community/?subtopic=highscores
.. _Houses: https://www.tibia.com/community/?subtopic=houses
.. _Kill Statistics: https://www.tibia.com/community/?subtopic=killstatistics
.. _Leaderboards: https://www.tibia.com/community/?subtopic=leaderboards
.. _News: https://www.tibia.com/news/?subtopic=newsarchive
.. _Worlds: https://www.tibia.com/community/?subtopic=worlds
.. _Spell Library: https://www.tibia.com/library/?subtopic=spells


Docker
======
A ready to use HTTP server is also available as a Docker image, allowing you to integrate tibia.py in projects using other languages other than Python.

The image can be pulled from `Docker Hub`_:

.. code-block:: sh

    docker pull galarzaa90/tibia.py

Alternatively, the image can be built from the root of the project's source.

To run the image:

.. code-block:: sh

    docker run \
        -p 8000:8000 \
        --rm -ti \
        galarzaa90/tibia.py

API documentation will be available at: `http://localhost:8000/docs`.

.. _Docker Hub: https://hub.docker.com/r/galarzaa90/tibia.py
