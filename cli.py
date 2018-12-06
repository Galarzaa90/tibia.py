import time

from tibiapy import Character, Guild, World, __version__

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
def char(name, tibiadata):
    """Displays information about a Tibia character."""
    name = " ".join(name)
    if tibiadata:
        r = requests.get(Character.get_url_tibiadata(name))
        char = Character.from_tibiadata(r.text)
    else:
        r = requests.get(Character.get_url(name))
        char = Character.from_content(r.text)
    start = time.perf_counter()
    dt = time.perf_counter() - start
    print("Parsed in {0:.2f} ms".format(dt))
    char_content = print_character(char)
    print(char_content)

@cli.command(name="guild")
@click.argument('name', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
def guild(name, tibiadata):
    """Displays information about a Tibia guild."""
    name = " ".join(name)
    if tibiadata:
        r = requests.get(Guild.get_url_tibiadata(name))
        guild = Guild.from_tibiadata(r.text)
    else:
        r = requests.get(Guild.get_url(name))
        guild = Guild.from_content(r.text)
    start = time.perf_counter()
    dt = time.perf_counter() - start
    print("Parsed in {0:.2f} ms".format(dt))
    guild_content = print_guild(guild)
    print(guild_content)

@cli.command(name="guilds")
@click.argument('world', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
def guilds(world, tibiadata):
    """Displays the list of guilds for a specific world"""
    world = " ".join(world)
    if tibiadata:
        r = requests.get(Guild.get_world_list_url_tibiadata(world))
        guilds = Guild.list_from_tibiadata(r.text)
    else:
        r = requests.get(Guild.get_world_list_url(world))
        guilds = Guild.list_from_content(r.text)
    start = time.perf_counter()
    dt = time.perf_counter() - start
    print("Parsed in {0:.2f} ms".format(dt))
    guild_content = print_guilds(guilds)
    print(guild_content)

@cli.command(name="world")
@click.argument('name', nargs=-1)
def world(name):
    name = " ".join(name)
    r = requests.get(World.get_url(name))
    world = World.from_content(r.text)
    start = time.perf_counter()
    dt = time.perf_counter() - start
    print("Parsed in {0:.2f} ms".format(dt))
    world_content = print_world(world)
    print(world_content)

def get_field(field, content):
    return "{0}{1}:{2} {3}\n".format(BOLD, field, CEND, content)

def build_header(title, separator="-"):
    return "{2}{0}\n{1}\n{3}".format(title, len(title)*separator, BOLD, CEND)


def print_character(character: Character):
    content = build_header("Character", "=")
    if character is None:
        content += "{0}Character doesn't exist{1}".format(RED, CEND)
        return content

    content += get_field("Name", character.name)
    if character.deletion_date:
        content += get_field("Scheduled for deletion", character.deletion_date)
    if character.former_names:
        content += get_field("Former names", ",".join(character.former_names))
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

def print_guild(guild):
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

def print_guilds(guilds):
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


if __name__ == "__main__":
    cli()