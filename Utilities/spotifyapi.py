import aiohttp


class Track:
    def __init__(self, name, artists, album, url, duration, uri):
        self.name = name
        self.artists = artists
        self.album = album
        self.url = url
        self.duration = duration
        self.uri = uri


def create_track(data: dict):
    return Track(
        name=data['name'],
        artists=data['artists'][0]['name'],
        album=data['album'],
        url=data['external_urls']['spotify'],
        duration=data['duration_ms'],
        uri=data['id']
    )

class Spotify:
    def __init__(self, client_id, secret):
        self.client_id = client_id
        self.secret = secret

    async def get_access_token(self):
        auth_url = "https://accounts.spotify.com/api/token"

        # Your client_id and secret
        client_id = self.client_id
        secret = self.secret

        # Define the headers for the token request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # Define the data for the token request
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': secret,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, headers=headers, data=data) as resp:
                response_data = await resp.json()
                # The access token is in response_data['access_token']
                return response_data['access_token']

    async def get_track(self, query):
        access_token = await self.get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'}

        if 'open.spotify.com/track/' in query:

            query = query.replace('https://open.spotify.com/track/', '')

            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.spotify.com/v1/tracks/{query}/", headers=headers) as resp:
                    data = await resp.json()
                    return create_track(data)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1",
                                       headers=headers) as resp:
                    data = await resp.json()
                    track = data['tracks']['items'][0]
                    return create_track(track)
    async def get_playlist(self, url):
        access_token = await self.get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'}

        if 'open.spotify.com/playlist/' in url:
            url = url.replace('https://open.spotify.com/playlist/', '')
            async with aiohttp.ClientSession() as session:

                url = f"https://api.spotify.com/v1/playlists/{url}/tracks"
                tracks = []

                while True:
                    async with session.get(url, headers=headers) as resp:
                        data = await resp.json()

                        for item in data['items']:
                            track = create_track(item['track'])

                            tracks.append(track)

                        url = data['next']

                        if url is None:
                            break

                return tracks
        else:
            async with aiohttp.ClientSession() as session:
                url = url.replace('https://open.spotify.com/album/', '')
                async with session.get(f"https://api.spotify.com/v1/albums/{url}", headers=headers) as resp:
                    data = await resp.json()

                    tracks = []

                    for item in data['tracks']['items']:
                        track = Track(
                            name=item['name'],
                            artists=item["artists"][0]["name"],
                            album=data,
                            url=item['external_urls']['spotify'],
                            duration=item['duration_ms'],
                            uri=item['id']
                        )

                        tracks.append(track)

                    return tracks

    async def search(self, query, limit=25, type='track'):
        access_token = await self.get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.spotify.com/v1/search?q={query}&type={type}&limit={limit}",
                                   headers=headers) as resp:
                data = await resp.json()
                return data
