# DiRTY.FLAC

A simple Python script to transcode FLAC albums to MP3 formats (320kbps or V0) and optionally create torrent files for sharing. 

## ✨ Features

- 🎵 **Transcode FLAC to MP3**: Convert albums in the `flac` folder to either MP3 320kbps, MP3 V0, or both.
- 📂 **Automatic Folder Detection**: Recognizes folders containing "flac" in their names for processing.
- 🌐 **Torrent Creation**: Optionally generate `.torrent` files for each album with customizable trackers.
- 🧹 **Cleanup Option**: Choose to delete original FLAC files after successful transcoding.
- 🖥️ **User-Friendly CLI**: Interactive prompts guide you through the transcoding and torrent creation process.

### todo:

- **Flac** - Convert 24bit to 16bit.

## ⚙️ Requirements

- **Python 3.x**
- **FFmpeg** – used for extracting/embedding cover art and some metadata handling.
- **LAME** – encoder required for MP3 conversion.
- **FLAC** – decoder required for reading source `.flac` files.
- **mktorrent** – required for generating `.torrent` files.

Install dependencies:
```bash
sudo apt-get install ffmpeg lame flac mktorrent
```

## ▶️ Usage

1. Place your FLAC albums in a folder named `flac` (include "flac" in the folder name).
2. Run the script:
   ```bash
   python3 dirty.flac.py
   ```
3. Follow the prompts to:
   - Choose MP3 format: 320kbps, V0, or both.
   - Create `.torrent` files (optional) and specify trackers.
   - Delete FLAC files after transcoding (optional).

### Example folder structure:
```
DiRTY.FLAC/
├── flac/
│   ├── Album_Name_FLAC/
│   └── Another_Album_flac/
├── mp3/
│   ├── Album_Name_MP3_320/
│   └── Another_Album_MP3_V0/
├── torrents/
├── dirty.flac.py
└── README.md
```

## 📝 Notes

- Ensure folder names include "flac" (case-insensitive) for the script to detect them.
- Transcoded MP3 files will be saved in folders with "FLAC" replaced by "MP3 320" or "MP3 V0".
- Verify that `ffmpeg`, `lame`, `flac`, and `mktorrent` are in your system path before running the script.

## 🤝 Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss improvements or bugs.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
