# Tibia.py
An API to parse Tibia.com content into object oriented data.

No fetching is done by this module, you must provide the html content.

![Travis (.org)](https://img.shields.io/travis/Galarzaa90/tibia.py.svg)
[![GitHub (pre-)release](https://img.shields.io/github/release/Galarzaa90/tibia.py/all.svg)](https://github.com/Galarzaa90/tibiawiki-sql/releases)
[![PyPI](https://img.shields.io/pypi/v/tibia.py.svg)](https://pypi.python.org/pypi/tibia.py/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tibia.py.svg)
![PyPI - License](https://img.shields.io/pypi/l/tibia.py.svg)

## Installing
Install and update using pip

```commandline
pip install tibia.py
```

## Usage
In order to use this library, you need to use an external library (`requests`, `aiohttp`) to fetch content from the website.

```python
import tibiapy

# Asynchronously
import aiohttp

async def get_character(name):
  url = tibiapy.Character.get_url(name)

  try:
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
  content = r.text()
  character = tibiapy.Character.from_content(content)
  return character
```

## Documentation
https://tibiapy.readthedocs.io/