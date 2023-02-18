=========
Changelog
=========

.. note::
    Due to this library relying on external content, older versions are not guaranteed to work.
    Try to always use the latest version.


.. v5.6.0

5.6.0 (2023-02-17)
==================
- Added ``tier`` to items in auctions.


.. v5.5.2

5.5.2 (2022-09-02)
==================
- Fixed Houses section not parsing due to a change in the filters table.
- Fixed status parameter not generating the correct URL in the houses section.

.. v5.5.1

5.5.1 (2022-08-02)
==================
- Adjusted parsing to support the changes related to mobile devices introduced on the day of this release. The following sections were affected:
    - Highscores
    - News
    - Forums
    - Spells

.. v5.5.0

5.5.0 (2022-07-27)
==================
- Added ``BOSS_POINTS`` to ``Category`` in highscores.


.. v5.4.0

5.4.0 (2022-07-23)
==================
- Added ``boss_points`` and ``bosstiary_progress`` to auctions.

.. v5.3.0

5.3.0 (2022-07-22)
==================
- Added support for Boostable Bosses.

.. v5.2.1

5.2.1 (2022-03-01)
==================
- Fixed bug in news ticker with a ``div`` tag failing to parse.
- Updated code to detect the discussion thread link.

.. v5.2.0

5.2.0 (2021-12-31)
==================
- Added ``exalted_dust`` and ``exalted_dust_limit`` attributes to auctions.


.. v5.1.0

5.1.0 (2021-09-16)
==================
- Added ``traded`` attribute to death killers, to indicate that the killer was traded after the death occurred.
- Properly handle deaths caused by summons of traded characters.

.. v5.0.1

5.0.1 (2021-08-26)
==================
- Fixed many sections not being parsed correctly due to changes to Tibia.com.
    - Houses list
    - News list
    - Spells section
    - Forums section
- Fixed character's houses failing to parse due to a bug in the display in Tibia.com.
    - Temporarily disabling this attribute.

.. v5.0.0

5.0.0 (2021-08-06)
==================
- Added parsing for Tibia Drome leaderboards, new ``Leaderboard`` class.
    - Auxiliary classes ``LeaderboardEntry`` and ``LeaderboardRotation`` were added as well.
    - New ``Client`` method: ``fetch_leaderboards``.
- Added parsing for Spells library, new ``SpellsSection`` class.
    - Auxiliary  classes ``Spell`` and ``SpellEntry``.
    - New ``Client`` methods: ``fetch_spell`` and ``fetch_spells``
- Fix last page of highscores having ``0`` as page value.
- Using the ``Client`` class, you can now fetch and parse content from the test version of www.tibia.com when available.
    - Note that if the test website has changes, parsing might not be possible.
    - Internal URL attributes might still point to the regular website.
- New ``HousesSection`` class, including the house filtering attributes.
- New ``NewsArchive`` class, including the news filtering attributes.
- New ``GuildsSection`` class, to replace the lists of ``GuildEntry``
- Many "ListedObject" classes were renamed to "ObjectEntry", for details check the breaking changes below.
- Fixed bug with other characters not being parsed.
- Added ``traded`` attribute to ``LastPost`` class.
- Added ``thread_starter_traded`` attribute to ``ThreadEntry``

**Breaking Changes**:

- Python 3.7 or higher is now required.
- House classes no longer have ``get_list_url`` and ``list_from_content`` methods.
- ``Client.fetch_world_houses`` now returns a ``HousesSection`` instance in its data attribute, instead of a list of ``ListedHouses``.
- ``ListedHouse.highest_bid`` attribute now may be ``None`` if the house's auction has not yet started.
- ``ListedHouse`` class renamed to ``HouseEntry``.
- Removed deprecated property ``AuctionFilters.item``.
- ``Client.fetch_news_archive``, ``Client.fetch_recent_news`` now returns an instance of ``NewsArchive`` in the ``data`` attribute.
- ``ListedNews`` class renamed to ``NewsEntry``.
- ``News`` and ``NewsEntry`` no longer have a ``get_list_url`` method.
- ``ListedBoard`` class renamed to ``BoardEntry``.
- ``ListedThread`` class renamed to ``ThreadEntry``.
- ``ListedAnnouncement`` class renamed to ``AnnouncementEntry``.
- ``ListedWorld`` class renamed to ``WorldEntry``.
- ``ListedAuction`` class renamed to ``AuctionEntry``.
- ``AuctionDetails`` class renamed to ``Auction``.
- ``ListedGuild`` class renamed to ``GuildEntry``.
- ``ListedTournament`` class renamed to ``TournamentEntry``.
- ``Creature`` class renamed to ``CreatureEntry``.
- ``CreatureDetail`` class renamed to ``Creature``.
- ``Guild`` and ``GuildEntry`` class no longer have a ``get_list_url`` method.
- Renamed ``begin_date`` parameter to ``start_date`` in ``fetch_news_archive``.
- Renamed ``race`` attribute of ``CreatureEntry`` and ``Creature`` to ``identifier``, method parameters renamed as well.
- ``CreaturesSection.from_boosted_creature_header`` renamed to ``CreaturesSection.boosted_creature_from_header``.


.. v4.1.7

4.1.7 (2021-06-30)
==================
- Fixed titles being parsed as part of the name for guild members with symbols in their name.

.. v4.1.6

4.1.6 (2021-06-28)
==================
- Fixed worlds not being parsed correctly again due to tournament worlds order changing. After this fix,
  the order should not matter anymore.

.. v4.1.5

4.1.5 (2021-06-25)
==================
- Fixed parsing bug on characters, returning an incorrect exception when a character doesn't exist.

.. v4.1.4

4.1.4 (2021-06-17)
==================
- Fixed worlds not being parsed correctly due to tournament worlds order changing.

.. v4.1.3

4.1.3 (2021-05-12)
==================
- Fixed house transfer date not being parsed properly.


.. v4.1.2

4.1.2 (2021-04-27)
==================
- Fixed parsing errors for forum posts that contained a copy of the signature separator in the signature.

.. v4.1.1

4.1.1 (2021-04-19)
==================
- Fixed bug with extraneous character in some item descriptions, causing auction to give a parsing error.

.. v4.1.0

4.1.0 (2021-03-30)
==================
- Added ``prey_wildcards`` attribute to ``AuctionDetails``.
- Added ``filters`` parameter to ``CharacterBazaar.get_auctions_history_url`` and ``Client.fetch_auction_history``.

.. v4.0.0:

4.0.0 (2021-03-10)
==================
- Breaking change: Removed ``BoostedCreature`` class, replaced by ``Creature`` class.
    - Attributes should be compatible, ``image_url`` is a property of ``Creature``, calculated from its ``race`` attribute.
- Added parsing and fetching for the Creature library section.
    - Added ``CreatureSection``, ``Creature``, and ``CreatureDetail`` classes.
- Added ``traded`` attribute to ``ForumAuthor``. Indicates if the author was a traded character.
    - Previously, it would mark the author as a deleted character and its name would include ``(traded)``.
- Fixed a bug with ``ForumBoards`` not parsing due to the cookies dialog that was added.
- Added ``battleye_type`` attribute to ``ListedWorld`` and ``World`` classes. Indicates the type of BattlEye protection the world has.
    - ``battleye_protected`` is now a property instead of an attribute.
- Added ``YELLOW`` and ``GREEN`` aliases to all BattlEye related enums.
- Fixed wrong timezone being used for forum related dates.

.. v3.7.1:

3.7.1 (2021-02-15)
==================

- Adjusted highscores parsing for upcoming Tibia.com changes.

.. v3.7.0:

3.7.0 (2021-02-09)
==================

- Parse familiars from auctions
- Updated the way tooltips in auctions are parsed, the format changed, resulting in the previous code not working anymore.
- Results count in bazaar pages are now properly parsed when there are comma thousand separators.
- Item amounts are now more accurate instead of being based from their indicator (which was grouping them in thousands)


.. v3.6.5:

3.6.5 (2021-01-27)
==================

- Fixed auction history parsing breaking due to the cookie consent dialog.

.. v3.6.4:

3.6.4 (2021-01-26)
==================

- Fixed world list parsing breaking due to the cookie consent dialog.

.. v3.6.3:

3.6.3 (2021-01-14)
==================

- Fixed bug in guild names being parsed with Non-Breaking spaces instead of a regular space.

.. v3.6.2:

3.6.2 (2021-01-01)
==================

- Fixed bug in Event Calendar parsing.

.. v3.6.1:

3.6.1 (2020-12-28)
==================

- Fixed guild information being parsed incorrectly for characters in guilds containing "of the" in their name.

.. v3.6.0:

3.6.0 (2020-12-12)
==================

- Added support for the new filtering options in Highscores
    - Added ``battleye_filter`` and ``pvp_types_filter`` attributes.
- Added ``get_page_url()`` instance method to ``Highscores`` class.
- Added ``previous_page_url`` and ``next_page_url`` properties.

.. v3.5.7:

3.5.7 (2020-12-04)
==================

- Fixed bug in Event Calendar parsing.


.. v3.5.6:

3.5.6 (2020-11-10)
==================

- Updated the URL used to fetch additional auction pages (items, mounts, outfits).

.. v3.5.5:

3.5.5 (2020-10-03)
==================

- Fixed charm expansion not being parsed correctly in auctions.

.. v3.5.4:

3.5.4 (2020-09-24)
==================

- Fetching auctions while skipping details is now faster.
- Fixed bug in tournaments parsing.

.. v3.5.3:

3.5.3 (2020-09-24)
==================

- Fixed bug with ascending ordering (lowest / earliest) not being passed to the request URL.

.. v3.5.2:

3.5.2 (2020-09-23)
==================

- Fixed bug with auctions with more than 10 charms failing to parse.

.. v3.5.1:

3.5.1 (2020-09-22)
==================

- Fixed bug with recently traded characters in "other characters" section not being properly parsed.

.. v3.5.0:

3.5.0 (2020-09-22)
==================

- Added support for the new filtering options added to current auctions:
    - Added new enumeration: ``AuctionSearchType``
    - Renamed ``AuctionFilters`` attribute ``item`` to ``search_string``.
      Property alias kept for backwards compatibility.
    - Added new attribute ``AuctionFilters.search_type``

.. v3.4.0:

3.4.0 (2020-09-19)
==================

- Added option to only parse the listed information of an auction, to skip the rest of the parsing.
- Fixed wrong type hint in ``ListedAuction`` for ``status``.

.. v3.3.0:

3.3.0 (2020-09-09)
==================

- Added support for the Character Bazaar
    - Added classes: ``CharacterBazaar``, ``ListedAuction`` and ``AuctionDetails`` and many auxiliary classes.
- Client methods throw a ``SiteMaintenanceError`` when Tibia.com is under maintenance, to be able to tell apart from
  other network errors.

.. v3.2.2:

3.2.2 (2020-08-27)
==================

- Properly parse the name of recently traded characters.
    - Added ``traded`` attribute to ``Character`` and ``OtherCharacter``.

.. v3.2.1:

3.2.1 (2020-08-25)
==================

- Fixed bug when parsing "other characters" from Tibia.com due to an unannounced change in the website.

.. v3.2.0:

3.2.0 (2020-08-10)
==================

- Added support for the new rules and score set added for the most recent Tournament.
    - Added ``ScoreSet.creature_kills``
    - Added ``ScoreSet.area_discovery``
    - Added ``ScoreSet.skill_gain_loss``
    - Added ``RuleSet.shared_xp_bonus``

.. v3.1.0:

3.1.0 (2020-07-29)
==================

- Added ``fetch_forum_post`` method to fetch a forum post directly.
- Fixed bug with forum posts made by tournament characters.

.. v3.0.3:

3.0.3 (2020-07-28)
==================

- Fixed bug with character title being parsed incorrectly when the character has no title selected and a single unlocked title.

.. v3.0.2:

3.0.2 (2020-07-14)
==================

- Fixed values being mapped incorrectly for highscores.
- ``ExpHighscoresEntry`` is now removed.

.. v3.0.1:

3.0.1 (2020-07-14)
==================

- ``Highscores.world`` is now ``None`` when the highscores are for all worlds.

.. v3.0.0:

3.0.0 (2020-07-13)
==================
- The ``Client`` class' methods now return their responses wrapped in a ``TibiaResponse`` object.
  This contains information about Tibia.com's cache.
- Added parsing for Guild wars.
    - Added class ``GuildWars``
    - Added class ``GuildWarsEntry``
    - Added ``url_wars`` property and ``get_url_wars`` class method to all Guild classes.
    - Added ``active_war`` attribute to ``Guild``.
- Added parsing for the Tibia forums: Boards, Threads, Posts, Announcements
    - Added classes ``ForumBoard`` and ``ListedBoard``
    - Added classes ``ForumThread`` and ``ListedThread``
    - Added classes ``ForumAnnouncement`` and ``ListedAnnouncement``
    - Added classes ``ForumPost``
    - Added auxiliary classes ``LastPost``,  ``ForumAuthor`` and ``ThreadStatus``.
    - Added property ``thread_url`` to ``News``.
- Updated highscores for Summer Update 2020:
    - ``page`` and ``total_pages`` are now fields instead of properties.
    - Added ``last_updated`` field.
    - Added ``Category.GOSHNARS_TAINT`` and ``Category.CHARM_POINTS``.
    - Added ``VocationFilter.NONE``.
- Removed deprecated property ``house`` from ``Character``, use ``houses`` instead.
- Removed support for Python 3.5.
- Changed the hierarchy of base classes. Base classes no longer implement ``Serializable``, ``Serializable`` is now
  directly implemented by most classes.
- Removed TibiaData functionality.

.. _v2.5.1:

2.5.1 (2020-05-27)
==================
- Fixed bed count not being parsed on houses.

.. _v2.5.0:

2.5.0 (2020-05-22)
==================
- Added parsing of Tournaments and Tournament Leaderboards.
- Fixed parsing errors with characters that had deaths by killers with "and" in their name.

.. _v2.4.3:

2.4.3 (2020-04-22)
==================
- Fixed an error when trying to parse a character with more deaths than what can be displayed in Tibia.com
    - ``Character.deaths_truncated`` field was added to keep track of this case.

.. _v2.4.2:

2.4.2 (2020-02-26)
==================
- Fixed exception when attempting to parse highscores with no results (e.g. a new world on its first day).

.. _v2.4.1:

2.4.1 (2019-11-20)
==================
- Fixed incorrect argument name (house) in ``Character`` constructor.

.. _v2.4.0:

2.4.0 (2019-11-20)
==================
- Added support for multiple houses per character. Accessible on ``Character.houses`` field.
- ``Character.house`` is now deprecated. It will contain the character's first house or ``None``.

.. _v2.3.4:

2.3.4 (2019-11-14)
==================
- Fixed bug with deaths not being parsed when a killer had ``and`` in their name.

.. _v2.3.3:

2.3.3 (2019-11-04)
==================
- Fixed bug with world parsing when there are more than 1000 players online.

.. _v2.3.2:

2.3.2 (2019-10-17)
==================
- Fixed incorrect highscores URL.

.. _v2.3.1:

2.3.1 (2019-10-06)
==================
- Fixed a bug with deaths not being parsed when a killer in assists had ``and`` in their name.

.. _v2.3.0:

2.3.0 (2019-09-16)
==================
- Added proxy option to client.

.. _v2.2.6:

2.2.6 (2019-09-01)
==================
- Fixed bug with account badges parsing failing when no badges were selected.

.. _v2.2.5:

2.2.5 (2019-08-22)
==================

- Fixed account badges parsing due to changes on the layout by CipSoft.

.. _v2.2.4:

2.2.4 (2019-08-20)
==================

- Disabled client compression for POST requests.

.. _v2.2.3:

2.2.3 (2019-08-17)
==================

- Enabled client side compression

.. _v2.2.2:

2.2.2 (2019-08-17)
==================

- Fixed killed by players and players kill stats being inverted for ``KillStatistics``

.. _v2.2.1:

2.2.1 (2019-08-10)
==================

- Fixed bug with character parsing failing when the guild rank is ``(member)``.

.. _v2.2.0:

2.2.0 (2019-08-08)
==================

- Added support for account badges and character titles.

.. _v2.1.0:

2.1.0 (2019-06-17)
==================

- Added ways to sort and filter House list results like in Tibia.com.
- Added support to get the Boosted Creature of the day.

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
