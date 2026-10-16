# Parsers

Parsers are used to convert to extract information from the HTML content of pages in Tibia.com.

The majority of users do not need to interact with these classes, but they can be used to provide alternate clients using other network libraries.

Most of the parsers support parsing the page displayed for no results (e.g. trying to parse the page for non-existent world [Fidera](https://www.tibia.com/community/?subtopic=worlds&world=Fidera)) by returning `None` instead of raising an exception.
Additionally, parsers attempt to detect when the HTML belongs to a different section by raising a [`InvalidContent`][tibiapy.InvalidContent] exception.

::: tibiapy.parsers