# Introduction

## Prerequisites

Tibia.py requires Python 3.6 or higher.
Dependencies are installed automatically when installing the package.

However, since it uses `lxml` for parsing, on Linux you may require to install libxml on your system.

```shell
sudo apt-get install libxml2-dev libxslt-dev python-dev
```

Windows users are usually safe from this. For more information check out [lxml installation page][lxml installation page].

## Installation

Tibia.py can be installed from [PyPi][PyPi] using:

```shell
python -m pip install tibia.py
```

## Usage

This library is composed of two parts, parsers and an asynchronous request client.

The asynchronous client ([`tibiapy.Client`][tibiapy.Client]) contains methods to obtain information from Tibia.com.

The parsing methods allow you to get Python objects given the HTML content of a page.

The `tibiapy.urls` package contains many methods to get URLs for Tibia.com.

With the URL, the HTML content can be fetched and then passed to the respective class from the available [Parsers](api/parsers.md).

This allows you to use any networking library (e.g. aiohttp, requests, httpx) to obtain the data, and use the library to parse it.

```python
import requests
import tibiapy
from tibiapy.parsers import CharacterParser

# Fetching a character using requests instead of aiohttp
def get_character(name):
    url = tibiapy.urls.get_character_url(name)

    r = requests.get(url)
    content = r.text
    return CharacterParser.from_content(content)
```

On the other hand, using the built-in asynchronous client you can do the fetching and parsing in one step:

```python
import asyncio
import tibiapy

async def main():
    client = tibiapy.Client()
    character = await client.fetch_character("Galarzaa Fidera")
    await client.session.close()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
```

## Supported Sections

| Section                                           | Parsing                                                                                                                  | Fetching                                                                                                                                                                                                                                                                                                                                 |
|---------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Boostable Bosses][Boostable Bosses] (List)       | [`tibiapy.parsers.BoostableBossesParser.from_content`][tibiapy.parsers.creature.BoostableBossesParser.from_content]      | [`Client.fetch_boostable_bosses`][tibiapy.Client.fetch_boostable_bosses]                                                                                                                                                                                                                                                                 |
| [Characters][Characters]                          | [`tibiapy.parsers.CharacterParser.from_content`][tibiapy.parsers.character.CharacterParser.from_content]                 | [`Client.fetch_character`][tibiapy.Client.fetch_character]                                                                                                                                                                                                                                                                               |
| [Character Bazaar][Character Bazaar] (Current)    | [`tibiapy.parsers.CharacterBazaarParser.from_content`][tibiapy.parsers.bazaar.CharacterBazaarParser.from_content]        | [`Client.fetch_current_auctions`][tibiapy.Client.fetch_current_auctions]                                                                                                                                                                                                                                                                 |
| [Character Bazaar][Character Bazaar] (History)    | [`tibiapy.parsers.CharacterBazaarParser.from_content`][tibiapy.parsers.bazaar.CharacterBazaarParser.from_content]        | [`Client.fetch_auction_history`][tibiapy.Client.fetch_auction_history]                                                                                                                                                                                                                                                                   |
| [Character Bazaar][Character Bazaar] (Detail)     | [`tibiapy.parsers.AuctionParser.from_content`][tibiapy.parsers.bazaar.AuctionParser.from_content]                        | [`Client.fetch_auction`][tibiapy.Client.fetch_auction]                                                                                                                                                                                                                                                                                   |
| [CM Post Archive][CM Post Archive]                | [`tibiapy.parsers.CMPostArchiveParser.from_content`][tibiapy.parsers.forum.CMPostArchiveParser.from_content]             | [`Client.fetch_cm_post_archive`][tibiapy.Client.fetch_cm_post_archive]                                                                                                                                                                                                                                                                   |
| [Creature Library][Creature Library] (List)       | [`tibiapy.parsers.CreaturesSectionParser.from_content`][tibiapy.parsers.creature.CreaturesSectionParser.from_content]    | [`Client.fetch_creatures`][tibiapy.Client.fetch_creatures]                                                                                                                                                                                                                                                                               |
| [Creature Library][Creature Library] (Individual) | [`tibiapy.parsers.CreatureParser.from_content`][tibiapy.parsers.creature.CreatureParser.from_content]                    | [`Client.fetch_creature`][tibiapy.Client.fetch_creature]                                                                                                                                                                                                                                                                                 |
| [Event Schedule][Event Schedule]                  | [`tibiapy.parsers.EventScheduleParser.from_content`][tibiapy.parsers.event.EventScheduleParser.from_content]             | [`Client.fetch_event_schedule`][tibiapy.Client.fetch_event_schedule]                                                                                                                                                                                                                                                                     |
| [Guilds][Guilds] (Individual)                     | [`tibiapy.parsers.GuildParser.from_content`][tibiapy.parsers.guild.GuildParser.from_content]                             | [`Client.fetch_guild`][tibiapy.Client.fetch_guild]                                                                                                                                                                                                                                                                                       |
| [Guilds][Guilds] (List)                           | [`tibiapy.parsers.GuildsSectionParser.from_content`][tibiapy.parsers.guild.GuildsSectionParser.from_content]             | [`Client.fetch_world_guilds`][tibiapy.Client.fetch_world_guilds]                                                                                                                                                                                                                                                                         |
| [Guilds][Guilds] (Wars)                           | [`tibiapy.parsers.GuildWarsParser.from_content`][tibiapy.parsers.guild.GuildWarsParser.from_content]                     | [`Client.fetch_guild_wars`][tibiapy.Client.fetch_guild_wars]                                                                                                                                                                                                                                                                             |
| [Fansites][Fansites]                              | [`tibiapy.parsers.FansitesSectionParser.from_content`][tibiapy.parsers.fansite.FansitesSectionParser.from_content]       | [`Client.fetch_fansites_section`][tibiapy.Client.fetch_fansites_section]                                                                                                                                                                                                                                                                 |
| [Forums][Forums] (Section)                        | [`tibiapy.parsers.ForumSectionParser.from_content`][tibiapy.parsers.forum.ForumSectionParser.from_content]               | [`Client.fetch_forum_world_boards`][tibiapy.Client.fetch_forum_world_boards]<br>[`Client.fetch_forum_trade_boards`][tibiapy.Client.fetch_forum_trade_boards]<br>[`Client.fetch_forum_community_boards`][tibiapy.Client.fetch_forum_community_boards]<br>[`Client.fetch_forum_support_boards`][tibiapy.Client.fetch_forum_support_boards] |
| [Forums][Forums] (Board)                          | [`tibiapy.parsers.ForumBoardParser.from_content`][tibiapy.parsers.forum.ForumBoardParser.from_content]                   | [`Client.fetch_forum_board`][tibiapy.Client.fetch_forum_board]                                                                                                                                                                                                                                                                           |
| [Forums][Forums] (Announcement)                   | [`tibiapy.parsers.ForumAnnouncementParser.from_content`][tibiapy.parsers.forum.ForumAnnouncementParser.from_content]     | [`Client.fetch_forum_announcement`][tibiapy.Client.fetch_forum_announcement]                                                                                                                                                                                                                                                             |
| [Forums][Forums] (Thread)                         | [`tibiapy.parsers.ForumThreadParser.from_content`][tibiapy.parsers.forum.ForumThreadParser.from_content]                 | [`Client.fetch_forum_thread`][tibiapy.Client.fetch_forum_thread]                                                                                                                                                                                                                                                                         |
| [Highscores][Highscores]                          | [`tibiapy.parsers.HighscoresParser.from_content`][tibiapy.parsers.highscores.HighscoresParser.from_content]              | [`Client.fetch_highscores_page`][tibiapy.Client.fetch_highscores_page]                                                                                                                                                                                                                                                                   |
| [Houses][Houses] (Individual)                     | [`tibiapy.parsers.HouseParser.from_content`][tibiapy.parsers.house.HouseParser.from_content]                             | [`Client.fetch_house`][tibiapy.Client.fetch_house]                                                                                                                                                                                                                                                                                       |
| [Houses][Houses] (List)                           | [`tibiapy.parsers.HousesSectionParser.from_content`][tibiapy.parsers.house.HousesSectionParser.from_content]             | [`Client.fetch_houses_section`][tibiapy.Client.fetch_houses_section]                                                                                                                                                                                                                                                                     |
| [Kill Statistics][Kill Statistics] (List)         | [`tibiapy.parsers.KillStatisticsParser.from_content`][tibiapy.parsers.kill_statistics.KillStatisticsParser.from_content] | [`Client.fetch_kill_statistics`][tibiapy.Client.fetch_kill_statistics]                                                                                                                                                                                                                                                                   |
| [Leaderboards][Leaderboards]                      | [`tibiapy.parsers.LeaderboardParser.from_content`][tibiapy.parsers.leaderboard.LeaderboardParser.from_content]           | [`Client.fetch_leaderboard`][tibiapy.Client.fetch_leaderboard]                                                                                                                                                                                                                                                                           |
| [News][News] (Individual)                         | [`tibiapy.parsers.NewsParser.from_content`][tibiapy.parsers.news.NewsParser.from_content]                                | [`Client.fetch_news`][tibiapy.Client.fetch_news]                                                                                                                                                                                                                                                                                         |
| [News][News] (List)                               | [`tibiapy.parsers.NewsArchiveParser.from_content`][tibiapy.parsers.news.NewsArchiveParser.from_content]                  | [`Client.fetch_news_archive`][tibiapy.Client.fetch_news_archive]<br>[`Client.fetch_news_archive_by_days`][tibiapy.Client.fetch_news_archive_by_days]                                                                                                                                                                                     |
| [Spell Library][Spell Library] (List)             | [`tibiapy.parsers.SpellsSectionParser.from_content`][tibiapy.parsers.spell.SpellsSectionParser.from_content]             | [`Client.fetch_spells`][tibiapy.Client.fetch_spells]                                                                                                                                                                                                                                                                                     |
| [Spell Library][Spell Library] (Individual)       | [`tibiapy.parsers.SpellParser.from_content`][tibiapy.parsers.spell.SpellParser.from_content]                             | [`Client.fetch_spell`][tibiapy.Client.fetch_spell]                                                                                                                                                                                                                                                                                       |
| [Worlds][Worlds] (Individual)                     | [`tibiapy.parsers.WorldParser.from_content`][tibiapy.parsers.world.WorldParser.from_content]                             | [`Client.fetch_world`][tibiapy.Client.fetch_world]                                                                                                                                                                                                                                                                                       |
| [Worlds][Worlds] (List)                           | [`tibiapy.parsers.WorldOverviewParser.from_content`][tibiapy.parsers.world.WorldOverviewParser.from_content]             | [`Client.fetch_world_overview`][tibiapy.Client.fetch_world_overview]                                                                                                                                                                                                                                                                     |

## Docker

A ready to use HTTP server is also available as a Docker image, allowing you to integrate tibia.py in projects using other languages other than Python.

The image can be pulled from [Docker Hub][Docker Hub]:

```sh
docker pull galarzaa90/tibia.py
```

Alternatively, the image can be built from the root of the project's source.

To run the image:

```sh
docker run \
    -p 8000:8000 \
    --rm -ti \
    galarzaa90/tibia.py
```

API documentation will be available at: `http://localhost:8000/docs`.

[lxml installation page]: https://lxml.de/installation.html
[PyPi]: https://pypi.org/
[Boostable Bosses]: https://www.tibia.com/library/?subtopic=boostablebosses
[Characters]: https://www.tibia.com/community/?subtopic=characters
[Character Bazaar]: https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades
[CM Post Archive]: https://www.tibia.com/forum/?subtopic=forum&action=cm_post_archive
[Creature Library]: https://www.tibia.com/library/?subtopic=creatures
[Event Schedule]: https://www.tibia.com/news/?subtopic=eventcalendar
[Guilds]: https://www.tibia.com/community/?subtopic=guilds
[Fansites]: https://www.tibia.com/community/?subtopic=fansites
[Forums]: https://www.tibia.com/community/?subtopic=forum
[Highscores]: https://www.tibia.com/community/?subtopic=highscores
[Houses]: https://www.tibia.com/community/?subtopic=houses
[Kill Statistics]: https://www.tibia.com/community/?subtopic=killstatistics
[Leaderboards]: https://www.tibia.com/community/?subtopic=leaderboards
[News]: https://www.tibia.com/news/?subtopic=newsarchive
[Worlds]: https://www.tibia.com/community/?subtopic=worlds
[Spell Library]: https://www.tibia.com/library/?subtopic=spells
[Docker Hub]: https://hub.docker.com/r/galarzaa90/tibia.py
