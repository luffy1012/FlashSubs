Hello World!

This is a python program that manages our media library i.e. it can automatically
download subtitles and other information(Correct Title, IMDB rating, Plot Summary etc.)
for movies and TV Series in our computer.

Install:
python -r Requirements.txt
	OR
./flashsubs install

Usage:

./flashsubs <'path to directory containing media'>
(for additional options see-> ./flashsubs --help)

OR

It can be started in Interactive mode by running without command line arguments, like
./flashsubs

Subtitles are searched using-
	1. Subdb database (hash)
	2. Opensubtitles database (hash)
	3. Opensubtitles database (name)
	4. Bing (name)
Thus, the probability of finding the subtitles become quite high.

Info is gathered using omdb api to fetch IMDB info for a given imdb id.

WARNING:
Does not work well with japanese Anime or any video other than Movies and English TV Series
and thus should not be run on a folder containing these items.
Doing so may result in improper renaming and will cause a mess.

Program only recognises files greater than 60MB to avoid files which are neither TV shows or Movies.
All changes are stored in a file name log.txt in the folder containing the program
which is deleted after its size reaches 10MB.

TODO: Add GUI and Undo feature
