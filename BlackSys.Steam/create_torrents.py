#!/usr/bin/env python3
import os
import zipfile
from pathlib import Path
import torf

# Torrent settings for GGn
TORRENT_SETTINGS = {
    'trackers': [
        'https://tracker.gazellegames.net/504ea84b11091401c516a272276adcd0/announce',
    ],
    'comment': None,
    'created_by': None,
    'source': 'GGn',
    'private': True,
    'piece_size': None,
}

def detect_platform(folder_name):
    folder_lower = folder_name.lower()
    if 'windows' in folder_lower or 'win' in folder_lower:
        return 'Windows'
    elif 'linux' in folder_lower:
        return 'Linux'
    elif 'macos' in folder_lower or 'mac' in folder_lower or 'osx' in folder_lower or 'darwin' in folder_lower:
        return 'MacOS'
    return None

def generate_name(parent_folder_name, subfolder_name):
    platform = detect_platform(subfolder_name)
    base_name = parent_folder_name.replace(' ', '.')
    if platform:
        return f"{base_name}.{platform}"
    else:
        print(f"  Warning: No platform detected in '{subfolder_name}'")
        return base_name

def create_zip(folder_path, zip_path, archive_folder_name):
    if zip_path.exists():
        print(f"  Skipping zip creation: {zip_path} already exists")
        return
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join(archive_folder_name, os.path.relpath(file_path, folder_path))
                zipf.write(file_path, arcname)
    print(f"Created zip: {zip_path}")

def create_torrent(file_path, torrent_path):
    if not file_path.exists():
        print(f"  Error: Cannot create torrent, file {file_path} does not exist")
        return
    if torrent_path.exists():
        print(f"  Skipping torrent creation: {torrent_path} already exists")
        return

    t = torf.Torrent()
    t.path = file_path
    t.trackers = TORRENT_SETTINGS['trackers']
    t.source = TORRENT_SETTINGS['source']
    t.private = TORRENT_SETTINGS['private']

    if TORRENT_SETTINGS['comment']:
        t.comment = TORRENT_SETTINGS['comment']
    if TORRENT_SETTINGS['created_by']:
        t.created_by = TORRENT_SETTINGS['created_by']
    if TORRENT_SETTINGS['piece_size']:
        t.piece_size = TORRENT_SETTINGS['piece_size']

    t.generate()
    t.write(torrent_path)

    print(f"Created torrent: {torrent_path}")
    print(f"  Info hash: {t.infohash}")
    print(f"  Piece size: {t.piece_size:,} bytes ({t.piece_size // 1024} KB)")
    print(f"  Private: {t.private}")
    print(f"  Source: {t.source}")

def process_subfolders(root_dir):
    root_dir = Path(root_dir)
    torrents_dir = Path("./torrents")
    torrents_dir.mkdir(parents=True, exist_ok=True)  # Create ./torrents if it doesn't exist

    processed_count = 0

    for folder in root_dir.iterdir():
        if folder.is_dir():
            for subfolder in folder.iterdir():
                if subfolder.is_dir() and any(subfolder.name.endswith(suffix) for suffix in ['-Linux', '-Windows', '-macOS']):
                    formatted_name = generate_name(folder.name, subfolder.name)
                    zip_name = f"{formatted_name}.zip"
                    torrent_name = f"{formatted_name}.torrent"
                    zip_path = subfolder.parent / zip_name
                    torrent_path = torrents_dir / torrent_name

                    print(f"\nProcessing: {subfolder}")
                    print(f"Parent folder: {subfolder.parent.name}")
                    print(f"Subfolder: {subfolder.name}")
                    print(f"Generated name: {formatted_name}")

                    create_zip(subfolder, zip_path, formatted_name)
                    create_torrent(zip_path, torrent_path)

                    processed_count += 1
                    print("-" * 60)

    return processed_count

def main():
    root_dir = "./games"
    print("GGn Torrent Creator")
    print("=" * 60)
    print(f"Working directory: {root_dir}")
    print(f"Tracker: {TORRENT_SETTINGS['trackers'][0]}")
    print(f"Source: {TORRENT_SETTINGS['source']}")
    print(f"Private: {TORRENT_SETTINGS['private']}")
    print("=" * 60)

    try:
        count = process_subfolders(root_dir)
        if count > 0:
            print(f"\nSuccessfully processed {count} subfolders!")
        else:
            print("\nNo platform-specific subfolders found to process.")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
