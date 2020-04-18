import time

from tibiapy import Character, Guild, House, ListedGuild, ListedWorld, Tournament, World, WorldOverview, __version__
from tibiapy.enums import HouseType
from tibiapy.house import ListedHouse

try:
    import click
    import requests
    import colorama
    colorama.init()
except ImportError:
    click = None
    requests = None
    colorama = None
    print("Use as a command-line interface requires optional dependencies: click, requests and colorama")
    exit()

RED = '\033[91m'
BOLD = '\033[1m'
CEND = '\033[0m'


def _fetch_and_parse(regular_url, regular_parse, tibiadata_url=None, tibiadata_parse=None, tibiadata: bool=False,
                     *args):
    url = regular_url(*args) if not tibiadata else tibiadata_url(*args)
    parse_func = regular_parse if not tibiadata else tibiadata_parse
    start = time.perf_counter()
    r = requests.get(url)
    dt = (time.perf_counter() - start) * 1000.0
    print("Fetched in {0:.2f} ms | {1}".format(dt, url))
    start = time.perf_counter()
    results = parse_func(r.text)
    dt = (time.perf_counter() - start) * 1000.0
    print("Parsed in {0:.2f} ms".format(dt))
    return results


@click.group(context_settings={'help_option_names': ['-h', '--hel']})
@click.version_option(__version__, '-V', '--version')
def cli():
    pass


@cli.command(name="char")
@click.argument('name', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_char(name, tibiadata, json):
    """Displays information about a Tibia character."""
    name = " ".join(name)
    char = _fetch_and_parse(Character.get_url, Character.from_content,
                            Character.get_url_tibiadata, Character.from_tibiadata,
                            tibiadata, name)
    if json and char:
        print(char.to_json(indent=2))
        return
    print(get_character_string(char))


@cli.command(name="guild")
@click.argument('name', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_guild(name, tibiadata, json):
    """Displays information about a Tibia guild."""
    name = " ".join(name)
    guild = _fetch_and_parse(Guild.get_url, Guild.from_content,
                             Guild.get_url_tibiadata, Guild.from_tibiadata,
                             tibiadata, name)
    if json and guild:
        print(guild.to_json(indent=2))
        return
    print(get_guild_string(guild))


@cli.command(name="guilds")
@click.argument('world', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_guilds(world, tibiadata, json):
    """Displays the list of guilds for a specific world"""
    world = " ".join(world)
    guilds = _fetch_and_parse(ListedGuild.get_world_list_url, ListedGuild.list_from_content,
                              ListedGuild.get_world_list_url_tibiadata, ListedGuild.list_from_tibiadata,
                              tibiadata, world)
    if json and guilds:
        import json as _json
        print(_json.dumps(guilds, default=dict, indent=2))
        return
    print(get_guilds_string(guilds))


@cli.command(name="world")
@click.argument('name', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_world(name, tibiadata, json):
    name = " ".join(name)
    world = _fetch_and_parse(World.get_url, World.from_content,
                             World.get_url_tibiadata, World.from_tibiadata,
                             tibiadata, name)
    if json and world:
        print(world.to_json(indent=2))
        return
    print(print_world(world))


@cli.command(name="worlds")
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_worlds(tibiadata, json):
    """Displays the list of worlds and their data."""
    worlds = _fetch_and_parse(ListedWorld.get_list_url, ListedWorld.list_from_content,
                              ListedWorld.get_list_url_tibiadata, ListedWorld.list_from_tibiadata,
                              tibiadata)
    if json and worlds:
        if isinstance(worlds, WorldOverview):
            print(worlds.to_json(indent=2))
        else:
            import json as _json
            print(_json.dumps(worlds, default=ListedWorld._try_dict, indent=2))
        return
    print(print_world_list(worlds))


@cli.command(name="house")
@click.argument('house_id')
@click.argument('world')
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_house(house_id, world, tibiadata, json):
    """Displays information about a house."""
    house = _fetch_and_parse(House.get_url, House.from_content,
                             House.get_url_tibiadata, House.from_tibiadata,
                             tibiadata, house_id, world)
    if json and house:
        print(house.to_json(indent=2))
        return
    print(get_house_string(house))


@cli.command(name="houses")
@click.argument('world')
@click.argument('town', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
@click.option("-gh", "--guildhalls", default=False, is_flag=True)
def cli_houses(world, town, tibiadata, json, guildhalls):
    """Displays the list of houses of a world."""
    town = " ".join(town)
    house_type = HouseType.GUILDHALL if guildhalls else HouseType.HOUSE
    houses = _fetch_and_parse(ListedHouse.get_list_url, ListedHouse.list_from_content,
                              ListedHouse.get_list_url_tibiadata, ListedHouse.list_from_tibiadata,
                              tibiadata, world, town, house_type)
    if json and houses:
        import json as _json
        print(_json.dumps(houses, default=House._try_dict, indent=2))
        return
    print(get_houses_string(houses))


@cli.command(name="tournament")
@click.argument('cycle', default=0)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_tournaments(json, cycle):
    """Displays the list of houses of a world."""
    tournament = _fetch_and_parse(Tournament.get_url, Tournament.from_content, None, None, False, cycle)
    if json and tournament or True:
        print(tournament.to_json(indent=2))


def get_field(field, content):
    return "{0}{1}:{2} {3}\n".format(BOLD, field, CEND, content)


def build_header(title, separator="-"):
    return "{2}{0}\n{1}\n{3}".format(title, len(title)*separator, BOLD, CEND)


def get_character_string(character: Character):  # NOSONAR
    content = build_header("Character", "=")
    if character is None:
        content += "{0}Character doesn't exist{1}".format(RED, CEND)
        return content

    content += get_field("Name", character.name)
    if character.deletion_date:
        content += get_field("Scheduled for deletion", character.deletion_date)
    if character.former_names:
        content += get_field("Former names", ",".join(character.former_names))
    content += get_field("Sex", character.sex.value)
    content += get_field("Vocation", character.vocation.value)
    content += get_field("Level", character.level)
    content += get_field("Achievement Points", character.achievement_points)
    content += get_field("World", character.world)
    if character.former_world:
        content += get_field("Former world", character.former_world)
    content += get_field("Residence", character.residence)
    if character.married_to:
        content += get_field("Married to", character.married_to)
    if character.guild_membership:
        content += get_field("Guild membership", "%s of the %s" % (character.guild_rank, character.guild_name))
    if character.last_login:
        content += get_field("Last login", character.last_login)
    else:
        content += get_field("Last login", "Never")
    if character.comment:
        content += get_field("Comment", character.comment)
    content += get_field("Account status", character.account_status.value)
    if character.achievements:
        content += "\n"
        content += build_header("Account Achievements")
        for achievement in character.achievements:
            content += "- %s (Grade %d)\n" % (achievement.name, achievement.grade)

    if character.deaths:
        content += "\n"
        content += build_header("Deaths")
        for death in character.deaths:
            if len(death.killers) == 1:
                content += "- %s - Died at Level %d by %s\n" % (death.time, death.level, death.killer.name)
            else:
                content += "- %s - Died at Level %d by:\n" % (death.time, death.level)
                for killer in death.killers:
                    content += "  - %s\n" % killer.name

    if character.account_information:
        content += "\n"
        content += build_header("Account Information")
        content += get_field("Loyalty Title", character.account_information.loyalty_title)
        content += get_field("Created", character.account_information.created)
        if character.account_information.position:
            content += get_field("Position", character.account_information.position)

    if character.other_characters:
        content += "\n"
        content += build_header("Other Characters")
        for other_char in character.other_characters:
            content += "- %s - %s - %s\n" % (other_char.name, other_char.world, "online" if other_char.online else
                                             ("deleted" if other_char.deleted else "offline"))
    return content


def get_guild_string(guild):  # NOSONAR
    content = build_header("Guild Information", "=")
    if guild is None:
        content += "{0}Guild doesn't exist{1}".format(RED, CEND)
        return content
    content += get_field("Name", guild.name)
    content += get_field("World", guild.world)
    content += get_field("Logo URL", guild.logo_url)
    content += get_field("Founded", guild.founded)
    if guild.homepage:
        content += get_field("Homepage", guild.homepage)
    if guild.active:
        if guild.disband_date is not None:
            content += get_field("Status", "Active, but it will be deleted on %s %s" %
                                 (guild.disband_date, guild.disband_condition))
    else:
        content += get_field("Status", "In formation, it will be disbanded on %s %s" %
                             (guild.disband_date, guild.disband_condition))
    content += get_field("Open applications", "Yes" if guild.open_applications else "No")
    if guild.guildhall:
        content += get_field("Guildhall", "%s, paid until %s" % (guild.guildhall.name, guild.guildhall.paid_until_date))
    if guild.description:
        content += get_field("Description", guild.description)
    content += get_field("Ranks", ", ".join(guild.ranks))

    content += build_header("Members")
    content += get_field("Online", "%d/%d" % (len(guild.online_members), guild.member_count))
    for member in guild.members:
        title = "" if not member.title else " (%s)" % member.title
        content += "- %s - %s%s - %s Lvl %d - %s\n" % (member.rank, member.name, title, member.vocation.value,
                                                       member.level, member.joined)

    content += build_header("Invites")
    if guild.invites:
        for invite in guild.invites:
            content += "- %s - %s\n" % (invite.name, invite.date)
    else:
        content += "There are currently no invited characters."
    return content


def get_guilds_string(guilds):
    content = build_header("Guild List", "=")
    if guilds is None:
        content += "No guilds."
        return content
    for g in guilds:
        content += get_field("Name", g.name)
        content += get_field("Status", "Active" if g.active else "In formation")
        content += get_field("Logo URL", g.logo_url)
        if g.description:
            content += get_field("Description", g.description)
        content += "-----\n"
    return content


def print_world(world: World):
    content = build_header("World", "=")
    if world is None:
        content += "World doesn't exist."
        return content
    content += get_field("Name", world.name)
    content += get_field("Status", world.status)
    content += get_field("Online count", world.online_count)
    content += get_field("Online record", "%d players on %s" % (world.record_count, world.record_date))
    content += get_field("Creation Date", world.creation_date)
    content += get_field("Location", world.location.value)
    content += get_field("PvP Type", world.pvp_type.value)
    content += get_field("Transfer Type", world.transfer_type.value)
    content += get_field("World Type", "Regular" if not world.experimental else "Experimental")
    content += get_field("Premium Only", "Yes" if world.premium_only else "No")
    if not world.battleye_protected:
        content += get_field("BattlEye Protected", "Not protected")
    else:
        content += get_field("BattlEye Protected", "Protected since %s." % (world.battleye_date or "release"))
    if world.world_quest_titles:
        content += build_header("World Quest Titles")
        for quest in world.world_quest_titles:
            content += "- %s\n" % quest

    content += build_header("Players Online")
    for player in world.online_players:
        content += "- %s - Level %d %s\n" % (player.name, player.level, player.vocation.value)
    return content


def print_world_list(world_list):
    content = build_header("Game World Overview", "=")
    content += get_field("Total online", sum(w.online_count for w in world_list))

    content += build_header("Worlds")
    for world in world_list:
        content += "%s - %d Online - %s - %s\n" % (world.name, world.online_count, world.location, world.pvp_type)
    return content


def get_house_string(house):
    content = build_header("House", "=")
    content += get_field("Name", house.name)
    content += get_field("World", house.world)
    content += get_field("Beds", house.beds)
    content += get_field("Size", "%d SQM" % house.size)
    content += get_field("Rent", "%d gold monthly" % house.rent)
    content += get_field("Type", house.type.title())
    content += get_field("Status", house.status)
    if house.status == "auctioned":
        content += get_field("Highest bid", "%d gold by %s, auction ends on %s" %
                                            (house.highest_bid, house.highest_bidder, house.auction_end)
                             if house.highest_bidder else "None")
    else:
        content += get_field("Rented by", "%s, paid until %s" % (house.owner, house.paid_until))
        if house.transfer_date:
            transfer = "Moving out on %s" % house.transfer_date
            if house.transferee:
                transfer += " and transfering to %s for %d gold" % (house.transferee, house.transfer_price)
                if house.transfer_accepted:
                    transfer += "."
                else:
                    transfer += ", if accepted."
            content += get_field("Moving", transfer)
    return content


def get_houses_string(houses):
    content = build_header("House List", "=")
    if not houses:
        content += "No houses."
        return content
    for h in houses:
        content += get_field("Name", h.name)
        content += get_field("ID", h.id)
        content += get_field("Rent", h.rent)
        content += get_field("Status", h.status.value)
        content += "-----\n"
    return content


if __name__ == "__main__":
    cli()
