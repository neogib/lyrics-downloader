# Lyrics Fetcher

A simple Python script to automatically download synced lyrics (`.lrc` files) for your local music library. It scans directories for audio files, fetches lyrics from [Lrclib](https://lrclib.net/), and saves them alongside the audio files.

> [!WARNING]
> Audio files need to include metadata for `artist`, `title`, `album`, and `duration` in order to be extracted. Lyrics will only be downloaded if this metadata is present. Only synced lyrics are downloaded.

## Features

- **Recursive Scanning**: Scans provided directories recursively for supported audio files.
- **Metadata Extraction**: Uses `tinytag` to read artist, title, album, and duration from audio files.
- **Synced Lyrics**: Fetches time-synced lyrics from Lrclib.
- **LRC File Generation**: Creates `.lrc` files with standard metadata headers.
- **Rich Logging**: Uses `rich` for beautiful console logging.

## Requirements

- Python 3.13 or higher
- Dependencies:
  - `requests`
  - `rich`
  - `tinytag`

## Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/neogib/lyrics-downloader.git
    cd lyrics-downloader
    ```

2.  Install dependencies (using `uv` or `pip`):

    ```bash
    # If using uv (recommended)
    uv sync

    # Or using pip
    pip install -r requirements.txt
    ```

## Usage

Run the script by providing one or more file or directory paths:

```bash
python main.py /path/to/music/folder /path/to/another/song.mp3
```

The script will:

1.  Find all supported audio files in the given paths.
2.  Extract metadata for each file.
3.  Query the Lrclib API.
4.  Save a `.lrc` file in the same directory as the audio file if lyrics are found.

## Supported Formats

The script supports all file formats supported by `tinytag`, including:

- MP3
- M4A
- FLAC
- OGG
- OPUS
- WAV
- and more...

## Logging

Logs are output to the console and saved to `download_lyrics.log`.
