import time

from tibiapy import Character, Guild, House, World, WorldOverview, __version__
from tibiapy.enums import HouseType
from tibiapy.house import ListedHouse

try:
    import click
    import requests
    import colorama
    colorama.init()
except ImportError:
    print("Use as a command-line interface requires optional dependencies: click, requests and colorama")
    exit()

RED = '\033[91m'
BOLD = '\033[1m'
CEND = '\033[0m'


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
    start = time.perf_counter()
    if tibiadata:
        r = requests.get(Character.get_url_tibiadata(name))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        char = Character.from_tibiadata(r.text)
    else:
        r = requests.get(Character.get_url(name))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        char = Character.from_content(r.text)
    dt = (time.perf_counter() - start) * 1000.0
    print("Parsed in {0:.2f} ms".format(dt))
    if json:
        print(char.to_json(indent=2))
    else:
        print(build_character(char))


@cli.command(name="guild")
@click.argument('name', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_guild(name, tibiadata, json):
    """Displays information about a Tibia guild."""
    name = " ".join(name)
    start = time.perf_counter()
    if tibiadata:
        r = requests.get(Guild.get_url_tibiadata(name))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        guild = Guild.from_tibiadata(r.text)
    else:
        r = requests.get(Guild.get_url(name))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        guild = Guild.from_content(r.text)
    dt = (time.perf_counter() - start) * 1000.0
    print("Parsed in {0:.2f} ms".format(dt))
    if json:
        print(guild.to_json(indent=2))
    else:
        print(build_guild(guild))


@cli.command(name="guilds")
@click.argument('world', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_guilds(world, tibiadata, json):
    """Displays the list of guilds for a specific world"""
    world = " ".join(world)
    start = time.perf_counter()
    if tibiadata:
        r = requests.get(Guild.get_world_list_url_tibiadata(world))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        guilds = Guild.list_from_tibiadata(r.text)
    else:
        r = requests.get(Guild.get_world_list_url(world))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        guilds = Guild.list_from_content(r.text)
    dt = (time.perf_counter() - start) * 1000.0
    print("Parsed in {0:.2f} ms".format(dt))
    if json:
        import json as _json
        print(_json.dumps(guilds, default=dict, indent=2))
    else:
        print(get_guilds_string(guilds))


@cli.command(name="world")
@click.argument('name', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_world(name, tibiadata, json):
    name = " ".join(name)
    start = time.perf_counter()
    if tibiadata:
        r = requests.get(World.get_url_tibiadata(name))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        world = World.from_tibiadata(r.text)
    else:
        r = requests.get(World.get_url(name))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        world = World.from_content(r.text)
    dt = (time.perf_counter() - start) * 1000.0
    print("Parsed in {0:.2f} ms".format(dt))
    if json:
        print(world.to_json(indent=2))
    else:
        print(print_world(world))


@cli.command(name="worlds")
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_worlds(tibiadata, json):
    start = time.perf_counter()
    if tibiadata:
        r = requests.get(WorldOverview.get_url_tibiadata())
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        worlds = WorldOverview.from_tibiadata(r.text)
    else:
        r = requests.get(WorldOverview.get_url())
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        worlds = WorldOverview.from_content(r.text)
    dt = (time.perf_counter() - start) * 1000.0
    print("Parsed in {0:.2f} ms".format(dt))
    if json:
        print(worlds.to_json(indent=2))
    else:
        print(print_world_overview(worlds))


@cli.command(name="house")
@click.argument('id')
@click.argument('world')
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
def cli_house(id, world, tibiadata, json):
    start = time.perf_counter()
    if tibiadata:
        r = requests.get(House.get_url_tibiadata(int(id), world))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        house = House.from_tibiadata(r.text)
    else:
        r = requests.get(House.get_url(int(id), world))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        house = House.from_content(r.text)
    dt = (time.perf_counter() - start) * 1000.0
    print("Parsed in {0:.2f} ms".format(dt))
    if json:
        print(house.to_json(indent=2))
    else:
        print(print_house(house))

@cli.command(name="houses")
@click.argument('world')
@click.argument('town', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
@click.option("-js", "--json", default=False, is_flag=True)
@click.option("-gh", "--guildhalls", default=False, is_flag=True)
def cli_houses(world, town, tibiadata, json, guildhalls):
    town = " ".join(town)
    start = time.perf_counter()
    house_type = HouseType.GUILDHALL if guildhalls else HouseType.HOUSE
    if tibiadata:
        # r = requests.get(ListedHouse.get_url_tibiadata(int(id), world))
        # dt = (time.perf_counter() - start) * 1000.0
        # print("Fetched in {0:.2f} ms".format(dt))
        # start = time.perf_counter()
        # house = ListedHouse.from_tibiadata(r.text)
        return
    else:
        r = requests.get(ListedHouse.get_list_url(world, town, house_type))
        dt = (time.perf_counter() - start) * 1000.0
        print("Fetched in {0:.2f} ms".format(dt))
        start = time.perf_counter()
        houses = ListedHouse.list_from_content(r.text)
    dt = (time.perf_counter() - start) * 1000.0
    print("Parsed in {0:.2f} ms".format(dt))
    # if json:
    #     print(house.to_json(indent=2))
    # else:
    #     print(print_house(house))


def get_field(field, content):
    return "{0}{1}:{2} {3}\n".format(BOLD, field, CEND, content)


def build_header(title, separator="-"):
    return "{2}{0}\n{1}\n{3}".format(title, len(title)*separator, BOLD, CEND)


def build_character(character: Character):  # NOSONAR
    content = build_header("Character", "=")
    if character is None:
        content += "{0}Character doesn't exist{1}".format(RED, CEND)
        return content

    content += get_field("Name", character.name)
    if character.deletion_date:
        content += get_field("Scheduled for deletion", character.deletion_date)
    if character.former_names:
        content += get_field("Former names", ",".join(character.former_names))
    content += get_field("Sex", character.sex)
    content += get_field("Vocation", character.vocation)
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
    content += get_field("Account status", character.account_status)
    if character.achievements:
        content += "\n"
        content += build_header("Account Achievements")
        for achievement in character.achievements:
            content += "- %s (Grade %d)\n" % (achievement["name"], achievement["grade"])

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
        content += get_field("Loyalty Title", character.account_information["loyalty_title"])
        content += get_field("Created", character.account_information["created"])
        content += get_field("Position", character.account_information.get("position", "None"))

    if character.other_characters:
        content += "\n"
        content+= build_header("Other Characters")
        for other_char in character.other_characters:
            content += "- %s - %s - %s\n" % (other_char.name, other_char.world, "online" if other_char.online else
            ("deleted" if other_char.deleted else "offline"))
    return content


def build_guild(guild):  # NOSONAR
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
        content += get_field("Guildhall", "%s, paid until %s" % (guild.guildhall["name"], guild.guildhall["paid_until"]))
    if guild.description:
        content += get_field("Description", guild.description)
    content += get_field("Ranks", ", ".join(guild.ranks))

    content += build_header("Members")
    content += get_field("Online", "%d/%d" % (len(guild.online_members), guild.member_count))
    for member in guild.members:
        content += "- %s - %s%s - %s %d - %s\n" % (member.rank, member.name,
                                              "" if not member.title else " (%s)" % member.title,
                                              member.vocation, member.level, member.joined)

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


def print_world(world):
    content = build_header("World", "=")
    if world is None:
        content += "World doesn't exist."
        return content
    content += get_field("Name", world.name)
    content += get_field("Status", world.status)
    content += get_field("Online count", world.online_count)
    content += get_field("Online record", "%d players on %s" % (world.record_count, world.record_date))
    content += get_field("Creation Date", world.creation_date)
    content += get_field("Location", world.location)
    content += get_field("PvP Type", world.pvp_type)
    content += get_field("Transfer Type", world.transfer_type)
    content += get_field("World Type", world.type)
    content += get_field("Premium Only", "Yes" if world.premium_only else "No")
    if not world.battleye_protected:
        content += get_field("Battleye Protected", "Not protected")
    else:
        content += get_field("Battleye Protected", "Protected since %s." % (world.battleye_date or "release"))
    if world.world_quest_titles:
        content += build_header("World Quest Titles")
        for quest in world.world_quest_titles:
            content += "- %s\n" % quest

    content += build_header("Players Online")
    for player in world.players_online:
        content += "- %s - Level %d %s\n" % (player.name, player.level, player.vocation)
    return content


def print_world_overview(world_overview):
    content = build_header("Game World Overview", "=")
    content += get_field("Total online", world_overview.total_online)
    content += get_field("Overall Maximum", "%d players on %s" % (world_overview.record_count,
                                                                  world_overview.record_date))

    content += build_header("Worlds")
    for world in world_overview.worlds:
        content += "%s - %d Online - %s - %s\n" % (world.name, world.online_count, world.location, world.pvp_type)
    return content


def print_house(house):
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


if __name__ == "__main__":
    cli()