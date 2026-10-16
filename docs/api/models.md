# Models

These are the classes that defined the models used by Tibia.py.

While it is possible to create instances of these models, their purpose is to be used as data containers.

## Characters

The [Character section][Character section] consists of the [`Character`][tibiapy.models.Character] class and its auxiliary classes used to hold its data.

::: tibiapy.models.Character


::: tibiapy.models.AccountBadge


::: tibiapy.models.AccountInformation


::: tibiapy.models.Achievement


::: tibiapy.models.CharacterHouse


::: tibiapy.models.Death


::: tibiapy.models.GuildMembership


::: tibiapy.models.DeathParticipant


::: tibiapy.models.OtherCharacter


## Worlds

Models related to [Tibia.com's World section][Tibia.com's World section]. The [`WorldOverview`][tibiapy.models.WorldOverview] class contains the list of all worlds, while
the [`World`][tibiapy.models.World] class contains the details of a single world.

::: tibiapy.models.WorldOverview


::: tibiapy.models.WorldEntry


::: tibiapy.models.World


::: tibiapy.models.OnlineCharacter


## Guilds

Models related to [Tibia.com's Guilds section][Tibia.com's Guilds section]. The main model is [`Guild`][tibiapy.models.Guild], while [`GuildEntry`][tibiapy.models.GuildEntry] is the
previewed information in the guild list of the [`GuildsSection`][tibiapy.models.GuildsSection].

::: tibiapy.models.GuildsSection


::: tibiapy.models.Guild


::: tibiapy.models.GuildEntry


::: tibiapy.models.GuildInvite


::: tibiapy.models.GuildHouse


::: tibiapy.models.GuildMember


::: tibiapy.models.GuildWars


::: tibiapy.models.GuildWarEntry


## Highscores

Models related to [Tibia.com's Highscores section][Tibia.com's Highscores section].

::: tibiapy.models.Highscores


::: tibiapy.models.HighscoresEntry


::: tibiapy.models.LoyaltyHighscoresEntry


## Houses

Models related to [Tibia.com's Houses section][Tibia.com's Houses section].

::: tibiapy.models.HousesSection


::: tibiapy.models.House


::: tibiapy.models.HouseEntry


## Leaderboard

Models related to [Tibia.com's Leaderboard section][Tibia.com's Leaderboard section].

::: tibiapy.models.Leaderboard


::: tibiapy.models.LeaderboardRotation


::: tibiapy.models.LeaderboardEntry


## Forums

Models related to [Tibia.com's Forum section][Tibia.com's Forum section].

::: tibiapy.models.CMPostArchive


::: tibiapy.models.ForumSection


::: tibiapy.models.ForumAnnouncement


::: tibiapy.models.ForumBoard


::: tibiapy.models.ForumPost


::: tibiapy.models.ForumThread


::: tibiapy.models.AnnouncementEntry


::: tibiapy.models.BoardEntry


::: tibiapy.models.ThreadEntry


::: tibiapy.models.CMPost


::: tibiapy.models.ForumAuthor


::: tibiapy.models.ForumEmoticon


::: tibiapy.models.LastPost


## News

Models related to [Tibia.com's News section][Tibia.com's News section]. This also contains the [Event Calendar][Event Calendar]

::: tibiapy.models.NewsArchive


::: tibiapy.models.News


::: tibiapy.models.NewsEntry


::: tibiapy.models.EventSchedule


::: tibiapy.models.EventEntry


## Bazaar

Models related to [Tibia.com's Bazaar section][Tibia.com's Bazaar section].

::: tibiapy.models.CharacterBazaar


::: tibiapy.models.Auction


::: tibiapy.models.AuctionDetails


::: tibiapy.models.AchievementEntry


::: tibiapy.models.AuctionFilters


::: tibiapy.models.BestiaryEntry


::: tibiapy.models.BlessingEntry


::: tibiapy.models.CharmEntry


::: tibiapy.models.FamiliarEntry


::: tibiapy.models.ItemEntry


::: tibiapy.models.MountEntry


::: tibiapy.models.OutfitEntry


::: tibiapy.models.Familiars


::: tibiapy.models.ItemSummary


::: tibiapy.models.Mounts


::: tibiapy.models.OutfitImage


::: tibiapy.models.Outfits


::: tibiapy.models.SalesArgument


::: tibiapy.models.SkillEntry


::: tibiapy.models.RevealedGem


## Kill Statistics

::: tibiapy.models.KillStatistics


::: tibiapy.models.RaceEntry


## Library

::: tibiapy.models.CreaturesSection


::: tibiapy.models.Creature


::: tibiapy.models.CreatureEntry


::: tibiapy.models.BoostableBosses


::: tibiapy.models.BoostedCreatures


::: tibiapy.models.BossEntry


::: tibiapy.models.SpellsSection


::: tibiapy.models.Spell


::: tibiapy.models.Rune


::: tibiapy.models.SpellEntry


## Fansites

::: tibiapy.models.FansitesSection


::: tibiapy.models.Fansite


::: tibiapy.models.FansiteSocialMedia


::: tibiapy.models.FansiteContent


[Character section]: https://www.tibia.com/community/?subtopic=characters

[Tibia.com's World section]: https://www.tibia.com/community/?subtopic=worlds

[Tibia.com's Guilds section]: https://www.tibia.com/community/?subtopic=guilds

[Tibia.com's Highscores section]: https://www.tibia.com/community/?subtopic=highscores

[Tibia.com's Houses section]: https://www.tibia.com/community/?subtopic=houses

[Tibia.com's Leaderboard section]: https://www.tibia.com/community/?subtopic=tournament

[Tibia.com's Forum section]: https://www.tibia.com/community/?subtopic=worldboards

[Tibia.com's News section]: https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades

[Event Calendar]: https://www.tibia.com/news/?subtopic=eventcalendar

[Tibia.com's Bazaar section]: https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades
