from pathlib import Path, PosixPath
import logging
import requests
from mutagen.oggopus import OggOpus


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("download_lyrics.log"),
            logging.StreamHandler(),
        ],
    )


class LyricsDownloader:
    def __init__(self, directory_path: str):
        self.path = Path(directory_path)
        self.base_url = "https://lrclib.net/api"

    def run(self):
        for file_path in self.path.glob("*.opus"):
            self.process_song(file_path)

    def process_song(self, file_path: Path):
        audio: OggOpus = OggOpus(file_path)
        tags = audio.tags
        title = tags.get("title", [""])[0]
        artist = tags.get("artist", [""])[0]
        album = tags.get("album", [""])[0]

        if not all([title, artist, album]):
            logging.warning(
                f"Some tags are missing, skipping this song: {title} - {artist} - {album}"
            )
            return

        duration = audio.info.length
        logging.info(
            f"Title: {title}, Artist: {artist}, Album: {album}, Duration: {duration:.2f} seconds"
        )

        synced_lyrics = self.fetch_lyrics(title, artist, album, duration)
        if synced_lyrics:
            self.save_lyrics(file_path, synced_lyrics, duration, title, artist, album)

    def fetch_lyrics(self, title: str, artist: str, album: str, duration: float):
        query_params = {
            "track_name": title,
            "artist_name": artist,
            "album_name": album,
            "duration": int(duration),
        }
        response = requests.get(f"{self.base_url}/get", params=query_params)
        if response.status_code != 200:
            logging.error(f"Error fetching lyrics: {response.status_code}")
            return None
        
        data = response.json()
        synced_lyrics = data.get("syncedLyrics", [])
        if not synced_lyrics:
            logging.info("No synced lyrics found.")
            return None
        return synced_lyrics

    def save_lyrics(self, file_path: Path, synced_lyrics: str, duration: float, title: str, artist: str, album: str):
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


def main():
    setup_logging()
    full_path = f"{Path.home()}/Music/4now"
    downloader = LyricsDownloader(full_path)
    downloader.run()


if __name__ == "__main__":
    main()
