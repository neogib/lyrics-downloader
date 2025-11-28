import logging
from pathlib import Path

import mutagen
import requests
from mutagen import FileType

logger = logging.getLogger(__name__)


class LyricsDownloader:
    def __init__(self):
        self.base_url = "https://lrclib.net/api"
        self.supported_extensions = {".opus", ".m4a", ".mp3"}
        self.proccessed_songs = 0

    def run(self, paths: list[str]):
        for path_str in paths:
            path = Path(path_str)
            if path.is_dir():
                for file_path in path.iterdir():
                    if (
                        file_path.is_file()
                        and file_path.suffix.lower() in self.supported_extensions
                    ):
                        self.process_song(file_path)

            elif path.is_file() and path.suffix.lower() in self.supported_extensions:
                self.process_song(path)
            else:
                logger.warning(f"Skipping invalid path or unsupported file: {path}")

        logger.info(f"Processed {self.proccessed_songs} songs.")

    def process_song(self, file_path: Path):
        try:
            audio: FileType = mutagen.File(file_path)
            if audio is None:
                logger.warning(f"Could not read tags from {file_path}")
                return
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return

        logging.info(audio.pprint())

        title = self._get_tag(audio, ["title", "TIT2", "\xa9nam"])
        artist = self._get_tag(audio, ["artist", "TPE1", "\xa9ART"])
        album = self._get_tag(audio, ["album", "TALB", "\xa9alb"])

        if not all([title, artist, album]):
            logger.warning(
                f"Some tags are missing, skipping this song: {title} - {artist} - {album} ({file_path.name})"
            )
            return

        duration = audio.info.length
        logger.info(
            f"Title: {title}, Artist: {artist}, Album: {album}, Duration: {duration:.2f} seconds"
        )

        synced_lyrics = self.fetch_lyrics(title, artist, album, duration)
        if synced_lyrics:
            self.save_lyrics(file_path, synced_lyrics, duration, title, artist, album)
            self.proccessed_songs += 1

    def _get_tag(self, audio, keys: list[str]) -> str:
        for key in keys:
            if key in audio:
                val = audio[key]
                if isinstance(val, list):
                    return str(val[0])
                return str(val)
        return ""

    def fetch_lyrics(self, title: str, artist: str, album: str, duration: float):
        query_params = {
            "track_name": title,
            "artist_name": artist,
            "album_name": album,
            "duration": int(duration),
        }
        response = requests.get(f"{self.base_url}/get", params=query_params)
        if response.status_code != 200:
            logger.error(f"Error fetching lyrics: {response.status_code}")
            return None

        data = response.json()
        synced_lyrics = data.get("syncedLyrics", [])
        if not synced_lyrics:
            logger.info("No synced lyrics found.")
            return None
        return synced_lyrics

    def save_lyrics(
        self,
        file_path: Path,
        synced_lyrics: str,
        duration: float,
        title: str,
        artist: str,
        album: str,
    ):
        with open(file_path.with_suffix(".lrc"), "w", encoding="utf-8") as lrc_file:
            minutes = int(duration // 60)
            secs = int(duration % 60)
            cent = int((duration - int(duration)) * 100)  # hundredths
            time_format = f"{minutes:02d}:{secs:02d}:{cent:02d}"
            metadata = (
                f"[ti:{title}]\n[ar:{artist}]\n[al:{album}]\n[length:{time_format}]\n\n"
            )

            lrc_file.write(metadata)
            lrc_file.write(synced_lyrics)
