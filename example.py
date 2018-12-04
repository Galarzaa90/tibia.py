import time

import requests

import tibiapy

if __name__ == "__main__":
    r = requests.get(tibiapy.Character.get_url_tibiadata("Sindrum"))
    start = time.perf_counter()
    char = tibiapy.Character.from_tibiadata(r.text)
    dt = time.perf_counter() - start


    r = requests.get(tibiapy.Guild.get_url("Redd Alliance"))
    start = time.perf_counter()
    guild = tibiapy.Guild.from_content(r.text)
    dt = time.perf_counter() - start
    print()
    print("Parsed in {0:.2f} ms".format(dt))
    print("Guild Information")
    print("==================")
    if guild is None:
        print("Guild doesn't exist")
    else:
        print("Name:", guild.name)
        print("World", guild.world)
        print("Logo URL:", guild.logo_url)
        print("Founded:", guild.founded)
        if guild.active:
            if guild.disband_date is not None:
                print("Status: Active, but it will be deleted on %s if %s" % (guild.disband_date, guild.disband_condition))
        else:
            print("Status:", "In formation")
        print("Open applications:", "Yes" if guild.open_applications else "No")
        if guild.guildhall:
            print("Guildhall: %s, paid until %s" % (guild.guildhall["name"], guild.guildhall["paid_until"]))
        if guild.description:
            print("Description:", guild.description)
        print("Ranks:", ", ".join(guild.ranks))


        print("Members")
        print("--------")
        print("Online: %d/%d" % (len(guild.online_members), guild.member_count))
        for member in guild.members:
            print("\t- %s - %s%s - %s %d - %s" % (member.rank, member.name,
                                                  "" if not member.title else " (%s)" % member.title,
                                                  member.vocation, member.level, member.joined))

        print("Invites")
        print("-------")
        if guild.invites:
            for invite in guild.invites:
                print("\t- %s - %s" % (invite.name, invite.date))
        else:
            print("There are currently no invited characters.")

    world = "Gladera"
    r = requests.get(tibiapy.Guild.get_world_list_url(world))
    start = time.perf_counter()
    guilds = tibiapy.Guild.list_from_content(r.text, True)
    print("Guilds in Gladera")
    print("=================")
    for g in guilds:
        print("\tName: %s" % g.name)
        print("\tStatus: %s" % ("Active" if g.active else "In formation"))
        if g.description:
            print("\t%s" % g.description)
        print()
    dt = time.perf_counter() - start