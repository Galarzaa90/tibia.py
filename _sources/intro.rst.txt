============
Introduction
============

Prerequisites
=============
Tibia.py requires Python 3.5 or higher.
Dependencies are installed automatically when installing the package.

However, since it uses ``lxml`` for parsing, on Linux you may require to install libxml on your system.


.. code-block:: shell

    sudo apt-get install libxml2-dev libxslt-dev python-dev

Windows users are usually safe from this. For more information check out `lxml installation page`_
.



Installation
============
Tibia.py can be installed from `PyPi`_ using:

.. code-block:: shell

    python -m pip install tibia.py

.. _lxml installation page: https://lxml.de/installation.html
.. _PyPi: https://pypi.org/

Usage
=====
This library only performs parsing, to fetch content you need to use external libraries.

The main models have a ``get_url``/``get_url_tibiadata`` method that can be used to get their Tibia.com/TibiaData.com page.
With the url, the html/json content can be fetched and then passed to their ``from_content``/``from_tibiadata`` methods.

.. code-block:: python

   import aiohttp
   import requests
   import tibiapy

   # Asynchronously
   async def get_character(name):
      url = tibiapy.Character.get_url(name)

      try:
         async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
               content = await resp.text()
      character = tibiapy.Character.from_content(content)
      return character

   # Synchronously
   def get_character_sync(name):
      url = tibiapy.Character.get_url(name)

      r = requests.get(url)
      content = r.text
      character = tibiapy.Character.from_content(content)
      return character
