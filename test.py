import json

import requests

from tibiapy.character import parse_character

if __name__ == "__main__":
    r = requests.get("https://secure.tibia.com/community/?subtopic=characters&name=Galarzaa+Fidera")
    char = parse_character(r.text)
    with open("output.json", "w") as f:
        f.write(json.dumps(char, indent=4))
