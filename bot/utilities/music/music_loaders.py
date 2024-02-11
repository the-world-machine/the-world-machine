from lavalink.models import (DeferredAudioTrack, LoadResult, LoadType, PlaylistInfo, Source)

from utilities.music.spotify_api import Spotify
from config_loader import load_config

spotify = Spotify(client_id=load_config("SpotifyID"), secret=load_config("SpotifySecret"))




class CustomAudioTrack(DeferredAudioTrack):
    # A DeferredAudioTrack allows us to load metadata now, and a playback URL later.
    # This makes the DeferredAudioTrack highly efficient, particularly in cases
    # where large playlists are loaded.

    async def load(self, client):  # Load our 'actual' playback track using the metadata from this one.
        result: LoadResult = await client.get_tracks('ytsearch:{0.title} {0.author}'.format(self))  # Search for our track on YouTube.

        first_track = result.tracks[0]  # Grab the first track from the results.
        base64 = first_track.track  # Extract the base64 string from the track.
        self.track = base64  # We'll store this for later, as it allows us to save making network requests
        # if this track is re-used (e.g. repeat).

        return base64


class CustomSearch(Source):
    def __init__(self):
        super().__init__(name='custom')  # Initialising our custom source with the name 'custom'.

    async def load_item(self, client, query: str):
        if 'open.spotify.com' in query:

            load_type = LoadType.TRACK

            if 'playlist' in query or 'album' in query:
                tracks = await spotify.get_playlist(query)

                load_type = LoadType.PLAYLIST
            else:
                tracks = [await spotify.get_track(query)]

            get_tracks = []

            if tracks is None:
                return LoadResult(load_type, get_tracks, playlist_info=PlaylistInfo.none())

            for t in tracks:
                try:
                    get_tracks.append(
                        CustomAudioTrack({  # Create an instance of our CustomAudioTrack.
                            'identifier': t.album['images'][0]['url'],  # Fill it with metadata that we've obtained from our source's provider.
                            'isSeekable': True,
                            'author': t.artists,
                            'length': t.duration,
                            'isStream': False,
                            'title': t.name,
                            'uri': t.url
                            }, requester=0, extra={'cover_art': t.album['images'][0]['url']})
                        )  # Init requester with a default value.
                except:
                    pass # Incase there's a track that cannot be used.

            return LoadResult(load_type, get_tracks, playlist_info=PlaylistInfo.none())