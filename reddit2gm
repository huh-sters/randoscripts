#!/usr/bin/env python3
import click
import requests
from bs4 import BeautifulSoup
from pyyoutube import Api
from gmusicapi import Mobileclient

"""
Read a Reddit thread of music tracks, find all Youtube links, 
find the Google Music version and create a playlist. Only tested in
Python 3. Requires the following packages:

pip install click dataclasses-json python-youtube beautifulsoup4 requests marshmallow gmusicapi

For this you will require Google credentials. Usage:

python ./create.py <Reddit URL> "<New playlist name>"

First run will prompt for permission at Google Music, follow the instructions.

Bear in mind that Youtube rate limits calls to their API to 10,000 a day
and this script can easily eat up the call count.

"""


EXIT_OK = 0
EXIT_PARAM_ERROR = 1
EXIT_OTHER_ERROR = 2

YOUTUBE_API_KEY = "electricboogaloo"


@click.command()
@click.argument("REDDIT_URL")
@click.argument("PLAYLIST_NAME", default="New Playlist")
def main(reddit_url, playlist_name):
    """
    Grab the contents of the URL
    Find all Youtube URL's
    Read the metadata from the video
    Figure out the artist/track names
    Search google music for the artist/track
    Make a playlist
    :param reddit_url:
    :return:
    """
    results = requests.get(
        reddit_url,
        headers={
            "User-Agent": "reddit_youtube_gmusic_playlister"
        }
    )
    if results.status_code != 200:
        click.echo(f"ERROR: {results.status_code}, probably rate limited")
        raise click.exceptions.Exit(EXIT_OTHER_ERROR)

    html = results.content

    soup = BeautifulSoup(html, "html.parser")

    links = list()

    for link in soup.find_all("a"):
        url = link.get("href")

        if url is None:
            continue

        if url.startswith((
                "https://www.youtube.com/watch?v=",
                "https://youtu.be/",
                "http://www.youtube.com/watch?v=",
                "http://youtu.be/"
        )):
            links.append(url)

    click.echo(f"Found {len(links)} Youtube links")

    api = Api(api_key=YOUTUBE_API_KEY)

    titles = list()

    for link in links:
        video_id = link.replace("https://youtu.be/", "")
        video_id = video_id.replace("https://www.youtube.com/watch?v=", "")
        video_id = video_id.replace("http://www.youtube.com/watch?v=", "")
        video_id = video_id.replace("https://youtu.be/", "")
        meta = api.get_video_by_id(video_id=video_id)
        for item in meta.items:
            artist, _, track = item.snippet.title.partition(" - ")
            if (artist, track) not in titles:
                # De-dupe
                titles.append((artist, track))

    click.echo(f"Found {len(titles)} unique Youtube links")

    api = Mobileclient()
    result = api.oauth_login(Mobileclient.FROM_MAC_ADDRESS)
    if not result:
        credentials = api.perform_oauth()

        result = api.oauth_login(
            device_id=Mobileclient.FROM_MAC_ADDRESS,
            oauth_credentials=credentials
        )
        if not result:
            click.echo("Google Music auth error")
            raise click.exceptions.Exit(EXIT_OTHER_ERROR)

    song_ids = list()

    for title in titles:
        """
        Now go find the artist/track in Google Music
        """
        results = api.search(f"{title[0]}, {title[1]}")
        for song in results["song_hits"]:
            song_ids.append(song["track"]["storeId"])
            break

    click.echo(f"Creating playlist '{playlist_name}'")
    playlist_id = api.create_playlist(playlist_name)
    click.echo(f"Adding {len(song_ids)} found songs from Google Music")
    api.add_songs_to_playlist(playlist_id, song_ids)

    click.echo("Complete")
    raise click.exceptions.Exit(EXIT_OK)


if __name__ == "__main__":
    main()
