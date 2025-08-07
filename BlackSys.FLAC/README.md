# Black.Sys.FLAC

A simple Python script to transcode FLAC albums to MP3 formats (320kbps or V0) and optionally create torrent files for sharing. Streamline your music conversion process with ease and flexibility.

## Features

- **Transcode FLAC to MP3**: Convert albums in the `flac` folder to either MP3 320kbps, MP3 V0, or both.
- **Automatic Folder Detection**: Recognizes folders containing "flac" in their names for processing.
- **Torrent Creation**: Optionally generate `.torrent` files for each album with customizable trackers.
- **Cleanup Option**: Choose to delete original FLAC files after successful transcoding.
- **User-Friendly CLI**: Interactive prompts guide you through the transcoding and torrent creation process.

## Requirements

- **Python 3.x**
- **mktorrent**: Required for generating `.torrent` files.
- **FFmpeg**: Required for audio transcoding (ensure it's installed and accessible in your system path).

Install dependencies (example for Ubuntu/Debian):
```bash
sudo apt-get install mktorrent ffmpeg
```

## Installation

1. Clone or download this repository:
   ```bash
   git clone https://github.com/yourusername/Black.Sys.FLAC.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Black.Sys.FLAC
   ```
3. Ensure `mktorrent` and `FFmpeg` are installed (see Requirements).

## Usage

1. Place your FLAC albums in a folder named `flac` (or include "flac" in the folder name).
2. Run the script:
   ```bash
   python dirty.transcode.py
   ```
3. Follow the prompts to:
   - Choose MP3 format: 320kbps, V0, or both.
   - Create `.torrent` files (optional) and specify trackers.
   - Delete FLAC files after transcoding (optional).

Example folder structure:
```
Black.Sys.FLAC/
├── flac/
│   ├── Album_Name_FLAC/
│   └── Another_Album_flac/
├── dirty.transcode.py
└── README.md
```

## Notes

- Ensure folder names include "flac" (case-insensitive) for the script to detect them.
- Transcoded MP3 files will be saved in folders with "FLAC" replaced by "MP3 320" or "MP3 V0".
- Verify that `mktorrent` and `FFmpeg` are in your system path before running the script.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss improvements or bugs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.