Hello World!

This is a python program that manages our media library i.e. it can automatically
download subtitles and other information(Correct Title, IMDB rating, Plot Summary etc.)
 for movies and TV Series in our computer.

Usage:
python flashsub.py <'path to directory containing media'> [--proxy=proxy_server:port]

Requires Beautiful Soup Module to work (Though not crucial. Modifications are welcome to
make it run without this module)

A local module is given if BeautifulSoup module is not found on the system.
Latest bs4 module can be found at - https://github.com/bdoms/beautifulsoup