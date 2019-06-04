.. currentmodule:: tibiapy

============
Introduction
============

Prerequisites
=============
Tibia.py requires Python 3.5 or higher.
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

The parsing methods allow you to get Python objects given the html content of a page.

The main models have a ``get_url``/``get_url_tibiadata`` method that can be used to get their Tibia.com/TibiaData.com page.
With the url, the html/json content can be fetched and then passed to their ``from_content``/``from_tibiadata`` methods.

This allows you to use any networking module to obtain the data, and use the library to parse it.

.. code-block:: python

    import requests
    import tibiapy

    # Fetching a character using requests instead of aiohttp
    def get_character(name):
        url = tibiapy.Character.get_url(name)

        r = requests.get(url)
        content = r.text
        character = tibiapy.Character.from_content(content)
        return character


Supported Sections
==================

+---------------------------+---------------------------------------+--------------------------------------+
|          Section          |                Parsing                |               Fetching               |
+===========================+=======================================+======================================+
| Characters_               | :meth:`Character.from_content`        | :meth:`Client.fetch_character`       |
+---------------------------+---------------------------------------+--------------------------------------+
| Guilds_ (Individual)      | :meth:`Guild.from_content`            | :meth:`Client.fetch_guild`           |
+---------------------------+---------------------------------------+--------------------------------------+
| Guilds_ (List)            | :meth:`ListedGuild.list_from_content` | :meth:`Client.fetch_world_guilds`    |
+---------------------------+---------------------------------------+--------------------------------------+
| Highscores_               | :meth:`Highscores.from_content`       | :meth:`Client.fetch_highscores_page` |
+---------------------------+---------------------------------------+--------------------------------------+
| Houses_ (Individual)      | :meth:`House.from_content`            | :meth:`Client.fetch_house`           |
+---------------------------+---------------------------------------+--------------------------------------+
| Houses_ (List)            | :meth:`ListedHouse.list_from_content` | :meth:`Client.fetch_world_houses`    |
+---------------------------+---------------------------------------+--------------------------------------+
| `Kill Statistics`_ (List) | :meth:`KillStatistics.from_content`   | :meth:`Client.fetch_kill_statistics` |
+---------------------------+---------------------------------------+--------------------------------------+
| News_ (Individual)        | :meth:`News.from_content`             | :meth:`Client.fetch_news`            |
+---------------------------+---------------------------------------+--------------------------------------+
| News_ (List)              | :meth:`ListedNews.list_from_content`  | :meth:`Client.fetch_news_archive`    |
|                           |                                       | :meth:`Client.fetch_recent_news`     |
+---------------------------+---------------------------------------+--------------------------------------+
| Worlds_ (Individual)      | :meth:`World.from_content`            | :meth:`Client.fetch_world`           |
+---------------------------+---------------------------------------+--------------------------------------+
| Worlds_ (List)            | :meth:`WorldOverview.from_content`    | :meth:`Client.fetch_world_list`      |
+---------------------------+---------------------------------------+--------------------------------------+


.. _Characters: https://secure.tibia.com/community/?subtopic=characters
.. _Guilds: https://secure.tibia.com/community/?subtopic=guilds
.. _Highscores: https://secure.tibia.com/community/?subtopic=highscores
.. _Houses: https://secure.tibia.com/community/?subtopic=houses
.. _Kill Statistics: https://secure.tibia.com/community/?subtopic=killstatistics
.. _News: https://www.tibia.com/news/?subtopic=newsarchive
.. _Worlds: https://www.tibia.com/community/?subtopic=worlds