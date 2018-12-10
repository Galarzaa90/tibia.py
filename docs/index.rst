.. Tibia.py documentation master file, created by
   sphinx-quickstart on Mon Aug  6 17:46:14 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
.. currentmodule:: tibiapy

.. toctree::
   :hidden:
   :maxdepth: 3

   api

========
Tibia.py
========


Tibia.py is a library for parsing HTML content from Tibia.com_. into python objects.

This library only performs parsing, to fetch content you need to use external libraries.

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
      content = r.text()
      character = tibiapy.Character.from_content(content)
      return character



.. _Tibia.com: https://www.tibia.com/news/?subtopic=latestnews





Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


