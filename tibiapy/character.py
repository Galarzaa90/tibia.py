import json
import urllib.parse
import re

from bs4 import BeautifulSoup, SoupStrainer

death_regexp = re.compile(r'Level (\d+) by ([^.]+)')
house_regexp = re.compile(r'paid until (.*)')
guild_regexp = re.compile(r'([\s\w]+)\sof the\s(.+)')


class Character:
    def __init__(self, name, world, **kwargs):
        self.name = name
        self.world = world

    @staticmethod
    def _parse(content):
        parsed_content = BeautifulSoup(content, 'html.parser', parse_only=SoupStrainer("div", class_="BoxContent"))
        tables = parsed_content.find_all('table', attrs={"width": "100%"})
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
                        house_text = value
                        paid_until = house_regexp.search(house_text).group(1)
                        house_link = cols_raw[1].find('a')
                        url = urllib.parse.urlparse(house_link["href"])
                        query = urllib.parse.parse_qs(url.query)
                        char["house"] = {
                            "town": query["town"][0],
                            "id": int(query["houseid"][0]),
                            "name": house_link.text.strip(),
                            "paid_until": paid_until
                        }
                        continue
                    char[field] = value
            elif "Achievements" in header.text:
                char["achievements"] = []
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) != 2:
                        continue
                    field, value = cols
                    grade = str(field).count("achievement-grade-symbol")
                    achievement = value.text.strip()
                    char["achievements"].append({
                        "grade": grade,
                        "name": achievement
                    })
            elif "Deaths" in header.text:
                char["deaths"] = []
                for row in rows:
                    cols_raw = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols_raw]
                    if len(cols) != 2:
                        continue
                    death_time, death = cols
                    death_time = death_time.replace("\xa0", " ")
                    death_info = death_regexp.search(death)
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
                char["account_information"] = {}
                for row in rows:
                    cols_raw = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols_raw]
                    if len(cols) != 2:
                        continue
                    field, value = cols
                    field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
                    value = value.replace("\xa0", " ")
                    char["account_information"][field] = value
            elif "Characters" in header.text:
                char["chars"] = []
                for row in rows:
                    cols_raw = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols_raw]
                    if len(cols) != 5:
                        continue
                    _name, world, status, __, __ = cols
                    _name = _name.replace("\xa0", " ").split(". ")[1]
                    char['chars'].append({'name': _name, 'world': world, 'status': "offline" if not status else status})
        # Converting values to int
        char["level"] = int(char["level"])
        char["achievement_points"] = int(char["achievement_points"])
        if "guild_membership" in char:
            m = guild_regexp.match(char["guild_membership"])
            char["guild_membership"] = {
                'rank': m.group(1),
                'guild': m.group(2)
            }
        return char

    @staticmethod
    def parse_to_json(content, indent=None):
        char_dict = Character._parse(content)
        return json.dumps(char_dict, indent=indent)

    @staticmethod
    def from_content(content):
        char = Character._parse(content)
        try:
            character = Character(char["name"], char["world"])
        except KeyError:
            return None

        return character

