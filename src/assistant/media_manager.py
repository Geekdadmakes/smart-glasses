"""
Media Manager - Enhanced music search, podcast control, volume, Spotify/YouTube
"""

import os
import json
import logging
import subprocess
import requests

logger = logging.getLogger(__name__)


class MediaManager:
    """Manage enhanced media features"""

    def __init__(self):
        """Initialize media manager"""

        # Spotify API credentials (optional)
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.spotify_token = None

        # YouTube API key (optional)
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')

        logger.info("Media Manager initialized")

    def search_song(self, query):
        """Search for a song using iTunes API (free, no auth needed)"""
        try:
            # iTunes Search API
            url = "https://itunes.apple.com/search"
            params = {
                'term': query,
                'media': 'music',
                'entity': 'song',
                'limit': 5
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('resultCount', 0) == 0:
                return f"No songs found for '{query}'"

            # Get top results
            results = data.get('results', [])[:3]

            result_text = f"Found {len(results)} songs for '{query}': "
            for i, song in enumerate(results, 1):
                artist = song.get('artistName', 'Unknown')
                track = song.get('trackName', 'Unknown')
                album = song.get('collectionName', '')
                result_text += f"{i}. {track} by {artist}"
                if album:
                    result_text += f" from {album}"
                result_text += ". "

            logger.info(f"Song search: {query}")
            return result_text.strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Song search error: {e}")
            return f"Couldn't search for songs. Check your internet connection."

    def search_artist(self, artist_name):
        """Search for an artist and their popular songs"""
        try:
            # iTunes Search API
            url = "https://itunes.apple.com/search"
            params = {
                'term': artist_name,
                'media': 'music',
                'entity': 'song',
                'limit': 5,
                'attribute': 'artistTerm'
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('resultCount', 0) == 0:
                return f"No songs found for artist '{artist_name}'"

            results = data.get('results', [])[:3]

            if results:
                artist = results[0].get('artistName', artist_name)
                result_text = f"Popular songs by {artist}: "

                for i, song in enumerate(results, 1):
                    track = song.get('trackName', 'Unknown')
                    result_text += f"{i}. {track}. "

                logger.info(f"Artist search: {artist_name}")
                return result_text.strip()

            return f"No songs found for '{artist_name}'"

        except requests.exceptions.RequestException as e:
            logger.error(f"Artist search error: {e}")
            return "Couldn't search for artist."

    def search_album(self, album_name):
        """Search for an album"""
        try:
            url = "https://itunes.apple.com/search"
            params = {
                'term': album_name,
                'media': 'music',
                'entity': 'album',
                'limit': 3
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('resultCount', 0) == 0:
                return f"No albums found for '{album_name}'"

            results = data.get('results', [])[:3]

            result_text = f"Found {len(results)} albums: "
            for i, album in enumerate(results, 1):
                artist = album.get('artistName', 'Unknown')
                name = album.get('collectionName', 'Unknown')
                year = album.get('releaseDate', '')[:4] if album.get('releaseDate') else ''
                track_count = album.get('trackCount', '')

                result_text += f"{i}. {name} by {artist}"
                if year:
                    result_text += f" ({year})"
                if track_count:
                    result_text += f", {track_count} tracks"
                result_text += ". "

            logger.info(f"Album search: {album_name}")
            return result_text.strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Album search error: {e}")
            return "Couldn't search for album."

    def search_podcast(self, query):
        """Search for podcasts using iTunes API"""
        try:
            url = "https://itunes.apple.com/search"
            params = {
                'term': query,
                'media': 'podcast',
                'entity': 'podcast',
                'limit': 5
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('resultCount', 0) == 0:
                return f"No podcasts found for '{query}'"

            results = data.get('results', [])[:3]

            result_text = f"Found {len(results)} podcasts: "
            for i, podcast in enumerate(results, 1):
                name = podcast.get('collectionName', 'Unknown')
                artist = podcast.get('artistName', 'Unknown')
                result_text += f"{i}. {name} by {artist}. "

            logger.info(f"Podcast search: {query}")
            return result_text.strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Podcast search error: {e}")
            return "Couldn't search for podcasts."

    def get_volume(self):
        """Get current system volume (Linux/ALSA)"""
        try:
            # Use amixer to get volume
            result = subprocess.run(
                ['amixer', 'get', 'Master'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                output = result.stdout
                # Parse volume percentage
                import re
                match = re.search(r'\[(\d+)%\]', output)
                if match:
                    volume = match.group(1)
                    logger.info(f"Current volume: {volume}%")
                    return f"Volume is at {volume} percent"

            return "Couldn't get volume"

        except Exception as e:
            logger.error(f"Get volume error: {e}")
            return "Couldn't get volume"

    def set_volume(self, level):
        """Set system volume (0-100)"""
        try:
            # Ensure level is between 0-100
            level = max(0, min(100, int(level)))

            # Use amixer to set volume
            result = subprocess.run(
                ['amixer', 'set', 'Master', f'{level}%'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                logger.info(f"Volume set to {level}%")
                return f"Volume set to {level} percent"
            else:
                return "Couldn't set volume"

        except Exception as e:
            logger.error(f"Set volume error: {e}")
            return "Couldn't set volume"

    def volume_up(self, amount=10):
        """Increase volume by specified amount"""
        try:
            amount = max(1, min(100, int(amount)))

            result = subprocess.run(
                ['amixer', 'set', 'Master', f'{amount}%+'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                logger.info(f"Volume increased by {amount}%")
                return f"Volume increased by {amount} percent"
            else:
                return "Couldn't increase volume"

        except Exception as e:
            logger.error(f"Volume up error: {e}")
            return "Couldn't increase volume"

    def volume_down(self, amount=10):
        """Decrease volume by specified amount"""
        try:
            amount = max(1, min(100, int(amount)))

            result = subprocess.run(
                ['amixer', 'set', 'Master', f'{amount}%-'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                logger.info(f"Volume decreased by {amount}%")
                return f"Volume decreased by {amount} percent"
            else:
                return "Couldn't decrease volume"

        except Exception as e:
            logger.error(f"Volume down error: {e}")
            return "Couldn't decrease volume"

    def mute_audio(self):
        """Mute audio"""
        try:
            result = subprocess.run(
                ['amixer', 'set', 'Master', 'mute'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                logger.info("Audio muted")
                return "Audio muted"
            else:
                return "Couldn't mute audio"

        except Exception as e:
            logger.error(f"Mute error: {e}")
            return "Couldn't mute audio"

    def unmute_audio(self):
        """Unmute audio"""
        try:
            result = subprocess.run(
                ['amixer', 'set', 'Master', 'unmute'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                logger.info("Audio unmuted")
                return "Audio unmuted"
            else:
                return "Couldn't unmute audio"

        except Exception as e:
            logger.error(f"Unmute error: {e}")
            return "Couldn't unmute audio"

    def search_youtube(self, query):
        """Search YouTube for videos (requires YouTube API key)"""
        if not self.youtube_api_key:
            return "YouTube search not configured. Set YOUTUBE_API_KEY environment variable."

        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': query,
                'key': self.youtube_api_key,
                'type': 'video',
                'maxResults': 3,
                'videoCategoryId': '10'  # Music category
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if 'items' not in data or len(data['items']) == 0:
                return f"No YouTube videos found for '{query}'"

            results = data['items'][:3]

            result_text = f"Found {len(results)} YouTube videos: "
            for i, video in enumerate(results, 1):
                title = video['snippet']['title']
                channel = video['snippet']['channelTitle']
                result_text += f"{i}. {title} by {channel}. "

            logger.info(f"YouTube search: {query}")
            return result_text.strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube search error: {e}")
            return "Couldn't search YouTube."

    def get_spotify_token(self):
        """Get Spotify access token using client credentials flow"""
        if not self.spotify_client_id or not self.spotify_client_secret:
            return None

        try:
            import base64

            # Encode credentials
            credentials = f"{self.spotify_client_id}:{self.spotify_client_secret}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()

            # Request token
            url = "https://accounts.spotify.com/api/token"
            headers = {
                'Authorization': f'Basic {credentials_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {'grant_type': 'client_credentials'}

            response = requests.post(url, headers=headers, data=data, timeout=5)
            response.raise_for_status()

            token_data = response.json()
            self.spotify_token = token_data.get('access_token')

            logger.info("Spotify token acquired")
            return self.spotify_token

        except Exception as e:
            logger.error(f"Spotify token error: {e}")
            return None

    def search_spotify(self, query, search_type='track'):
        """Search Spotify (requires Spotify API credentials)"""
        if not self.spotify_client_id or not self.spotify_client_secret:
            return "Spotify search not configured. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET."

        # Get token if we don't have one
        if not self.spotify_token:
            self.get_spotify_token()

        if not self.spotify_token:
            return "Couldn't authenticate with Spotify."

        try:
            url = "https://api.spotify.com/v1/search"
            headers = {'Authorization': f'Bearer {self.spotify_token}'}
            params = {
                'q': query,
                'type': search_type,
                'limit': 3
            }

            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if search_type == 'track':
                tracks = data.get('tracks', {}).get('items', [])
                if not tracks:
                    return f"No Spotify tracks found for '{query}'"

                result_text = f"Found {len(tracks)} Spotify tracks: "
                for i, track in enumerate(tracks, 1):
                    name = track['name']
                    artists = ', '.join([artist['name'] for artist in track['artists']])
                    result_text += f"{i}. {name} by {artists}. "

                logger.info(f"Spotify search: {query}")
                return result_text.strip()

            elif search_type == 'artist':
                artists = data.get('artists', {}).get('items', [])
                if not artists:
                    return f"No Spotify artists found for '{query}'"

                result_text = f"Found {len(artists)} Spotify artists: "
                for i, artist in enumerate(artists, 1):
                    name = artist['name']
                    genres = ', '.join(artist.get('genres', [])[:2])
                    result_text += f"{i}. {name}"
                    if genres:
                        result_text += f" ({genres})"
                    result_text += ". "

                return result_text.strip()

            return "Search completed"

        except requests.exceptions.RequestException as e:
            logger.error(f"Spotify search error: {e}")
            return "Couldn't search Spotify."
