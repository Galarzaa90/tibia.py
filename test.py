import json
import time

import requests

from tibiapy.character import parse_character

if __name__ == "__main__":
    r = requests.get("https://secure.tibia.com/community/?subtopic=characters&name=Ondskan")
    start = time.perf_counter()
    char = parse_character(r.text)
    dt = (time.perf_counter() - start) * 1000.0
    with open("output.json", "w") as f:
        f.write(json.dumps(char, indent=4))

    print("Parsed in {0:2f} ms".format(dt))