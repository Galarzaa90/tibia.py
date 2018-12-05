import time

from tibiapy import Character, Guild, __version__

try:
    import click
    import requests
    import colorama
    colorama.init()
except ImportError:
    print("Use as a command-line interface requires optional dependencies: click and requests")
    exit()

RED = '\033[91m'
BOLD = '\033[1m'
CEND = '\033[0m'

@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    pass

@cli.command(name="char")
@click.argument('name', nargs=-1)
@click.option("-td", "--tibiadata", default=False, is_flag=True)
def char(name, tibiadata):
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

if __name__ == '__main__':  # pragma: no cover
    cli()