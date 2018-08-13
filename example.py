import time

import requests

import tibiapy

if __name__ == "__main__":
    r = requests.get(tibiapy.Character.get_url("Sindrum"))
    start = time.perf_counter()
    char = tibiapy.Character.from_content(r.text)
    dt = time.perf_counter() - start
    print("Parsed in {0:.2f} ms".format(dt))
    print("Character Information")
    print("=======================")
    if char is None:
        print("Character doesn't exist")
    else:
        print("Name:",char.name)
        if char.deletion_date:
            print("Scheduled for deletion:", char.deletion_date)
        if char.former_names:
            print("Former names:", ", ".join(char.former_names))
        print("Vocation:", char.vocation)
        print("Level:", char.level)
        print("Achievement Points:", char.achievement_points)
        print("World:", char.world)
        if char.former_world:
            print("Former world:", char.former_world)
        print("Residence:", char.residence)
        if  char.married_to:
            print("Married to:", char.married_to)
        if char.guild_membership:
            print("Guild membership:", "%s of the %s" % (char.guild_rank, char.guild_name))
        if char.last_login:
            print("Last login:", char.last_login)
        else:
            print("Last login:", "Never")
        if char.comment:
            print("Comment:", char.comment)
        print("Account status:", char.account_status)
        print("")
        if char.achievements:
            print("Account Achievements")
            print("--------------------")
            for achievement in char.achievements:
                print("\t- %s (Grade %d)" % (achievement["name"], achievement["grade"]))

        if char.deaths:
            print("Deaths")
            print("------")
            for death in char.deaths:
                print("\t- %s - Died at Level %d by %s" % (death.time, death.level, death.killer))

        if char.account_information:
            print("Account Information")
            print("-------------------")
            print("Loyalty Title:", char.account_information["loyalty_title"])
            print("Created:", char.account_information["created"])

        if char.other_characters:
            print("Other Characters")
            print("----------------")
            for other_char in char.other_characters:
                print("\t- %s - %s - %s" % (other_char.name, other_char.world, "online" if other_char.online else
                ("deleted" if other_char.deleted else "offline")))

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

    print("")