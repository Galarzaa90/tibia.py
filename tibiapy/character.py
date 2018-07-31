import urllib.parse
import re

from bs4 import BeautifulSoup, SoupStrainer

def parse_character(content):
    parsed_content = BeautifulSoup(content, 'html.parser', parse_only=SoupStrainer("div", class_="BoxContent"))
    tables = parsed_content.find_all('table')
    char = {}
    for table in tables:
        header = table.find('td')
        rows = table.find_all('tr')
        if "Could not find" in header.text:
            return None
        if "Character Information" in header.text:
            for row in rows:
                cols_raw = row.find_all('td')
                cols = [ele.text.strip() for ele in cols_raw]
                if len(cols) != 2:
                    continue
                field, value = cols
                field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
                value = value.replace("\xa0", " ")
                # This is a special case cause we need to see the link
                if field == "house":
                    house = cols_raw[1].find('a')
                    url = urllib.parse.urlparse(house["href"])
                    query = urllib.parse.parse_qs(url.query)
                    char["house_town"] = query["town"][0]
                    char["house_id"] = query["houseid"][0]
                    char["house"] = house.text.strip()
                    continue
                char[field] = value
        elif "Achievements" in header.text:
            char["displayed_achievements"] = []
            for row in rows:
                cols_raw = row.find_all('td')
                cols = [ele.text.strip() for ele in cols_raw]
                if len(cols) != 2:
                    continue
                field, value = cols
                char["displayed_achievements"].append(value)
        elif "Deaths" in header.text:
            char["deaths"] = []
            for row in rows:
                cols_raw = row.find_all('td')
                cols = [ele.text.strip() for ele in cols_raw]
                if len(cols) != 2:
                    continue
                death_time, death = cols
                death_time = death_time.replace("\xa0", " ")
                regex_death = r'Level (\d+) by ([^.]+)'
                pattern = re.compile(regex_death)
                death_info = re.search(pattern, death)
                if death_info:
                    level = death_info.group(1)
                    killer = death_info.group(2)
                else:
                    continue
                death_link = cols_raw[1].find('a')
                death_player = False
                if death_link:
                    death_player = True
                    killer = death_link.text.strip().replace("\xa0", " ")
                try:
                    char["deaths"].append({'time': death_time, 'level': int(level), 'killer': killer,
                                           'is_player': death_player})
                except ValueError:
                    # Some pvp deaths have no level, so they are raising a ValueError, they will be ignored for now.
                    continue
        elif "Account Information" in header.text:
            for row in rows:
                cols_raw = row.find_all('td')
                cols = [ele.text.strip() for ele in cols_raw]
                if len(cols) != 2:
                    continue
                field, value = cols
                field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
                value = value.replace("\xa0", " ")
                char[field] = value
        elif "Characters" in header.text:
            char["chars"] = []
            for row in rows:
                cols_raw = row.find_all('td')
                cols = [ele.text.strip() for ele in cols_raw]
                if len(cols) != 5:
                    continue
                _name, world, status, __, __ = cols
                _name = _name.replace("\xa0", " ").split(". ")[1]
                char['chars'].append({'name': _name, 'world': world, 'status': status})

    # Formatting special fields:
    try:
        if "," in char["name"]:
            char["name"], _ = char["name"].split(",", 1)
            char["deleted"] = True
        char["premium"] = ("Premium" in char["account_status"])
        char.pop("account_status")
        if "former_names" in char:
            char["former_names"] = char["former_names"].split(", ")
        char["level"] = int(char["level"])
        char["achievement_points"] = int(char["achievement_points"])
        char["guild"] = None
        if "guild_membership" in char:
            char["rank"], char["guild"] = char["guild_membership"].split(" of the ")
            char.pop("guild_membership")
        if "never" in char["last_login"]:
            char["last_login"] = None
    except:
        return None
    return char


class Character:
    pass