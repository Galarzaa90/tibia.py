# Tibia.py
An API to parse Tibia.com content into object oriented data.

No fetching is done by this module, you must provide the html content.

[![PyPI](https://img.shields.io/pypi/v/tibia.py.svg)](https://pypi.python.org/pypi/tibia.py/)
![GitHub commits since latest release (branch)](https://img.shields.io/github/commits-since/Galarzaa90/tibia.py/latest/main)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tibia.py.svg)
![PyPI - License](https://img.shields.io/pypi/l/tibia.py.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/tibia.py)

[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Galarzaa90_tibia.py&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=Galarzaa90_tibia.py)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Galarzaa90_tibia.py&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Galarzaa90_tibia.py)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=Galarzaa90_tibia.py&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=Galarzaa90_tibia.py)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Galarzaa90_tibia.py&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Galarzaa90_tibia.py)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=Galarzaa90_tibia.py&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=Galarzaa90_tibia.py)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Galarzaa90_tibia.py&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Galarzaa90_tibia.py)

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
    url = tibiapy.urls.get_character_url(name)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            content = await resp.text()
    character = tibiapy.Character.from_content(content)
    return character

# Synchronously
import requests

def get_character_sync(name):
    url = tibiapy.urls.get_character_url(name)
    
    r = requests.get(url)
    content = r.text
    character = tibiapy.Character.from_content(content)
    return character

```

## Documentation
https://tibiapy.readthedocs.io/
