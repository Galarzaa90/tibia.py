# Tibia.py
An API to parse Tibia.com content into object oriented data.

No fetching is done by this module, you must provide the html content.

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Galarzaa90/tibia.py/Build%20Package)
[![codecov](https://codecov.io/gh/Galarzaa90/tibia.py/branch/master/graph/badge.svg?token=mS9Wxv6O2F)](https://codecov.io/gh/Galarzaa90/tibia.py)
[![PyPI](https://img.shields.io/pypi/v/tibia.py.svg)](https://pypi.python.org/pypi/tibia.py/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tibia.py.svg)
![PyPI - License](https://img.shields.io/pypi/l/tibia.py.svg)


**Features:**

- Converts data into well-structured Python objects.
- Type consistent attributes.
- All objects can be converted to JSON strings.
- Can be used with any networking library.
- Support for characters, guilds, houses and worlds, tournaments, forums, etc.

## Installing
Install and update using pip

```commandline
pip install tibia.py
```

Installing the latest version form GitHub

```commandline
pip install git+https://github.com/Galarzaa90/tibia.py.git -U
```

## Usage
This library is composed of two parts, parsers and an asynchronous request client.

The asynchronous client (`tibiapy.Client`) contains methods to obtain information from Tibia.com.

The parsing methods allow you to get Python objects given the html content of a page.

```python
import tibiapy

# Asynchronously
import aiohttp

async def get_character(name):
    url = tibiapy.Character.get_url(name)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            content = await resp.text()
    character = tibiapy.Character.from_content(content)
    return character

# Synchronously
import requests

def get_character_sync(name):
    url = tibiapy.Character.get_url(name)
    
    r = requests.get(url)
    content = r.text
    character = tibiapy.Character.from_content(content)
    return character

```

## Documentation
https://tibiapy.readthedocs.io/
