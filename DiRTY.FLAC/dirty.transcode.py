import os
import re
import json
import shutil
import subprocess
from pathlib import Path
import tempfile
import mutagen
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TPE2, TALB, TCOM, TCON, TRCK, TPOS, TYER, TSRC, TPUB, COMM, TEXT, TBPM, TXXX, UFID

# === CONFIG ===
INPUT_DIR = Path('./flac')
OUTPUT_DIR = Path('./mp3')
TORRENT_DIR = Path('./torrents')
TRACKER_FILE = Path("trackers.json")
FLAC_CMD = 'flac'
LAME_CMD = 'lame'
FFMPEG_CMD = 'ffmpeg'

# LAME encoding presets
PRESETS = {
    'V0': ['--noreplaygain', '--vbr-new', '-V', '0', '-h', '--nohist', '--quiet'],
    'V2': ['--noreplaygain', '--vbr-new', '-V', '2', '-h', '--nohist', '--quiet'],
    '320': ['--noreplaygain', '-b', '320', '-h', '--nohist', '--quiet']
}

# Mapping of FLAC tags to MP3 ID3 frames
MP3_FRAMES = {
    'ALBUM': 'TALB',
    'ALBUMARTIST': 'TPE2',
    'ARTIST': 'TPE1',
    'BAND': 'TPE2',
    'BPM': 'TBPM',
    'COMMENT': 'COMM',
    'COMPILATION': 'TCMP',
    'COMPOSER': 'TCOM',
    'CONDUCTOR': 'TPE3',
    'DATE': 'TYER',
    'DISCNUMBER': 'TPOS',
    'GENRE': 'TCON',
    'ISRC': 'TSRC',
    'LYRICIST': 'TEXT',
    'PUBLISHER': 'TPUB',
    'TITLE': 'TIT2',
    'TRACKNUMBER': 'TRCK',
    'MUSICBRAINZ_ALBUMID': 'TXXX',
    'MUSICBRAINZ_ALBUMSTATUS': 'TXXX',
    'MUSICBRAINZ_ALBUMTYPE': 'TXXX',
    'MUSICBRAINZ_ARTISTID': 'TXXX',
    'MUSICBRAINZ_SORTNAME': 'TXXX',
    'MUSICBRAINZ_TRACKID': 'UFID',
    'MUSICBRAINZ_TRMID': 'TXXX',
    'MD5': 'TXXX',
    'REPLAYGAIN_TRACK_PEAK': 'TXXX',
    'REPLAYGAIN_TRACK_GAIN': 'TXXX',
    'REPLAYGAIN_ALBUM_PEAK': 'TXXX',
    'REPLAYGAIN_ALBUM_GAIN': 'TXXX',
}

MP3_FRAME_TEXTS = {
    'COMMENT': '',
    'MD5': 'MD5',
    'MUSICBRAINZ_ALBUMARTISTID': 'MusicBrainz Album Artist Id',
    'MUSICBRAINZ_ALBUMID': 'MusicBrainz Album Id',
    'MUSICBRAINZ_ALBUMSTATUS': 'MusicBrainz Album Status',
    'MUSICBRAINZ_ALBUMTYPE': 'MusicBrainz Album Type',
    'MUSICBRAINZ_ARTISTID': 'MusicBrainz Artist Id',
    'MUSICBRAINZ_SORTNAME': 'MusicBrainz Sortname',
    'MUSICBRAINZ_TRACKID': 'MusicBrainz Trackid',
    'MUSICBRAINZ_TRMID': 'MusicBrainz TRM Id',
    'REPLAYGAIN_TRACK_PEAK': 'REPLAYGAIN_TRACK_PEAK',
    'REPLAYGAIN_TRACK_GAIN': 'REPLAYGAIN_TRACK_GAIN',
    'REPLAYGAIN_ALBUM_PEAK': 'REPLAYGAIN_ALBUM_PEAK',
    'REPLAYGAIN_ALBUM_GAIN': 'REPLAYGAIN_ALBUM_GAIN',
}


# === TRACKER UTILS ===
def load_trackers():
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE, "r") as f:
            return sorted(json.load(f), key=lambda t: t['name'].lower())
    return []


def save_trackers(trackers):
    with open(TRACKER_FILE, "w") as f:
        json.dump(trackers, f, indent=2)


def add_tracker():
    name = input("Tracker name: ").strip()
    url = input("Announce URL: ").strip()
    trackers = load_trackers()
    trackers.append({"name": name, "url": url})
    save_trackers(trackers)
    print(f"Tracker '{name}' added.")


def manage_trackers():
    while True:
        trackers = load_trackers()
        if not trackers:
            print("No trackers available.")
            return
        print("\nManage Trackers:")
        for i, t in enumerate(trackers, 1):
            print(f"{i} - {t['name']} ({t['url']})")
        print("0 - Back")
        choice = input("Enter number to delete or 0 to go back: ").strip()
        if choice == "0":
            break
        if choice.isdigit() and 1 <= int(choice) <= len(trackers):
            removed = trackers.pop(int(choice) - 1)
            save_trackers(trackers)
            print(f"Deleted tracker: {removed['name']}")


def select_trackers():
    while True:
        trackers = load_trackers()
        print("\nTrackers:")
        for i, t in enumerate(trackers[:7], 1):
            print(f"{i} - {t['name']}")
        print("8 - All")
        print("9 - Add")
        print("0 - Manage")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            manage_trackers()
        elif choice == "9":
            add_tracker()
        elif choice == "8":
            return trackers
        elif choice.isdigit() and 1 <= int(choice) <= len(trackers[:7]):
            return [trackers[int(choice) - 1]]
        else:
            print("Invalid option.")


# === TRANSCODE UTILS ===
def prompt_conversion_choice(folder_name):
    print(f"\nAlbum: {folder_name}")
    print("Transcoding format:")
    print(" 1. V0 Only")
    print(" 2. 320 Only")
    print(" 3. Both")
    print(" 4. Skip")
    while True:
        choice = input("Enter choice [1-4]: ").strip()
        if choice in ('1', '2', '3', '4'):
            break
        print("Invalid, please enter 1, 2, 3, or 4")

    create_torrent = 'n'
    tracker_objs = []
    if choice in ('1', '2', '3'):
        while True:
            create_torrent = input("Do you want to create a .torrent? (y/n): ").lower()
            if create_torrent in ('y', 'n'):
                break
            print("Please enter y or n")
        if create_torrent == 'y':
            tracker_objs = select_trackers()

        while True:
            del_src = input("Do you want to delete the flac after transcoding? (y/n): ").lower()
            if del_src in ('y', 'n'):
                break
            print("Please enter y or n")
    else:
        del_src = 'n'

    return choice, del_src, create_torrent, tracker_objs


def run_command(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {command}\nError: {result.stderr}")
        return False, result.stderr
    print(f"Command succeeded: {command}")
    return True, result.stdout


def extract_image_with_ffmpeg(flac_file, temp_dir):
    """Extract embedded image from FLAC using ffmpeg, return image path."""
    temp_image = temp_dir / "cover.jpg"
    cmd = f'{FFMPEG_CMD} -i "{flac_file}" -an -vcodec copy "{temp_image}" -y -loglevel error'
    success, _ = run_command(cmd)
    if success and temp_image.exists() and temp_image.stat().st_size > 0:
        print(f"Extracted image from {flac_file} to {temp_image} ({temp_image.stat().st_size} bytes)")
        return temp_image
    print(f"No image extracted from {flac_file}")
    return None


def embed_image_with_ffmpeg(mp3_file, image_file):
    """Embed image into MP3 using ffmpeg."""
    temp_mp3 = mp3_file.with_suffix('.temp.mp3')
    cmd = f'{FFMPEG_CMD} -i "{mp3_file}" -i "{image_file}" -c:a copy -c:v copy -map 0:a -map 1:v -metadata:s:v title="Cover (front)" -id3v2_version 3 "{temp_mp3}" -y -loglevel error'
    success, _ = run_command(cmd)
    if success and temp_mp3.exists() and temp_mp3.stat().st_size > 0:
        shutil.move(temp_mp3, mp3_file)
        print(f"Embedded image into {mp3_file} ({image_file.stat().st_size} bytes)")
        return True
    print(f"Failed to embed image into {mp3_file}")
    if temp_mp3.exists():
        temp_mp3.unlink()
    return False


def get_album_image(flac_folder):
    """Find a single album image from embedded FLAC images or folder."""
    flac_files = [f for f in flac_folder.glob('*.flac') if f.is_file()]
    image_file = None

    # Try extracting from the first FLAC file
    if flac_files:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            image_file = extract_image_with_ffmpeg(flac_files[0], temp_dir)
            if image_file:
                # Copy to FLAC folder as cover.jpg for consistency
                dest_image = flac_folder / 'cover.jpg'
                shutil.copy(image_file, dest_image)
                print(f"Copied extracted image to {dest_image} ({dest_image.stat().st_size} bytes)")
                image_file = dest_image

    # Fallback to folder images
    if not image_file:
        image_files = [f for f in flac_folder.glob('*.{jpg,jpeg,png,JPG,JPEG,PNG}') if f.is_file()]
        if image_files:
            image_file = image_files[0]
            print(f"Using folder image: {image_file} ({image_file.stat().st_size} bytes)")
            if image_file.suffix.lower() != '.jpg':
                dest_image = flac_folder / 'cover.jpg'
                shutil.copy(image_file, dest_image)
                image_file = dest_image
                print(f"Converted to {dest_image}")

    if not image_file:
        print(f"No image found in {flac_folder} or embedded in FLAC files")

    return image_file


def read_flac_tags(flac_file):
    try:
        audio = FLAC(flac_file)
        tags = {}
        if audio.tags:
            for k, v in audio.tags:
                tags[k.upper()] = v[0] if isinstance(v, list) and v else str(v)

        # Get MD5 checksum
        tags['MD5'] = audio.info.md5_signature.to_bytes(16, 'big').hex().upper()

        # Image handled separately in convert()
        print(f"FLAC tags for {flac_file}: {tags}")
        return tags
    except Exception as e:
        print(f"Error reading tags from {flac_file}: {e}")
        return {}


def preprocess_flac_tags(tags, flac_folder):
    tags_to_update = {}
    for frame, value in tags.items():
        if frame in MP3_FRAMES:
            if isinstance(value, list):
                value = '/'.join(str(v) for v in value if v)
            if value:
                tags_to_update[frame] = str(value).strip()

    # Ensure ALBUM and TITLE are present
    folder_name = Path(flac_folder).name
    if 'ALBUM' not in tags_to_update or not tags_to_update.get('ALBUM'):
        match = re.match(r'.*?-\s*(.*?)\s*\(\d{4}\)\s*\[FLAC\]', folder_name)
        album_name = match.group(1) if match else folder_name.replace('[FLAC]', '').strip()
        tags_to_update['ALBUM'] = album_name
        print(f"Warning: ALBUM tag missing or empty, using folder-derived name: {album_name}")
    if 'TITLE' not in tags_to_update or not tags_to_update.get('TITLE'):
        filename = Path(tags.get('FILEPATH', 'Unknown')).stem
        filename = re.sub(r'^\d+\s*[.-]\s*', '', filename)
        tags_to_update['TITLE'] = filename
        print(f"Warning: TITLE tag missing or empty, using filename: {filename}")

    # Fix track number
    if 'TRACKNUMBER' in tags_to_update:
        track_num = tags_to_update['TRACKNUMBER']
        try:
            track_num = int(track_num)
            tags_to_update['TRACKNUMBER'] = f"{track_num:02d}"
        except ValueError:
            print(f"Non-numeric TRACKNUMBER: {track_num}")
            tags_to_update['TRACKNUMBER'] = '01'  # Fallback

    return tags_to_update


def write_mp3_tags(mp3_file, tags_to_update):
    try:
        mp3 = MP3(mp3_file, ID3=ID3)
        if mp3.tags is None:
            mp3.add_tags()

        # Clear existing ID3 tags
        mp3.tags.clear()

        for frame, value in tags_to_update.items():
            if frame not in MP3_FRAMES:
                continue

            frame_id = MP3_FRAMES[frame]
            frame_text = MP3_FRAME_TEXTS.get(frame, '')

            print(f"Writing {frame_id} ({frame}): {value}")

            if frame_id == 'TIT2':
                mp3.tags.add(mutagen.id3.TIT2(encoding=3, text=value))
            elif frame_id == 'COMM':
                mp3.tags.add(COMM(encoding=3, lang='eng', desc=frame_text, text=value))
            elif frame_id == 'TXXX':
                mp3.tags.add(TXXX(encoding=3, desc=frame_text or frame, text=value))
            elif frame_id == 'UFID':
                mp3.tags.add(UFID(owner=frame_text, data=value.encode()))
            elif frame_id == 'TPE1':
                mp3.tags.add(TPE1(encoding=3, text=value))
            elif frame_id == 'TPE2':
                mp3.tags.add(TPE2(encoding=3, text=value))
            elif frame_id == 'TALB':
                mp3.tags.add(TALB(encoding=3, text=value))
            elif frame_id == 'TCOM':
                mp3.tags.add(TCOM(encoding=3, text=value))
            elif frame_id == 'TCON':
                mp3.tags.add(TCON(encoding=3, text=value))
            elif frame_id == 'TRCK':
                mp3.tags.add(TRCK(encoding=3, text=value))
            elif frame_id == 'TPOS':
                mp3.tags.add(TPOS(encoding=3, text=value))
            elif frame_id == 'TYER':
                mp3.tags.add(TYER(encoding=3, text=value))
            elif frame_id == 'TSRC':
                mp3.tags.add(TSRC(encoding=3, text=value))
            elif frame_id == 'TPUB':
                mp3.tags.add(TPUB(encoding=3, text=value))
            elif frame_id == 'TEXT':
                mp3.tags.add(TEXT(encoding=3, text=value))
            elif frame_id == 'TBPM':
                mp3.tags.add(TBPM(encoding=3, text=value))

        mp3.save(v2_version=3)
        print(f"Tags written to {mp3_file}")
        return True
    except Exception as e:
        print(f"Error writing tags to {mp3_file}: {e}")
        return False


def convert(flac_path, output_path, preset):
    flac_path = Path(flac_path)
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    flac_files = [f for f in flac_path.glob('*.flac') if f.is_file()]
    if not flac_files:
        print(f"No FLAC files found in {flac_path}")
        return False

    # Get single album image
    album_image = get_album_image(flac_path)

    success = True
    for flac_file in flac_files:
        rel_path = flac_file.relative_to(flac_path)
        mp3_file = output_path / rel_path.with_suffix('.mp3')
        mp3_file.parent.mkdir(parents=True, exist_ok=True)

        # Store filepath for TITLE fallback
        tags = read_flac_tags(flac_file)
        tags['FILEPATH'] = str(flac_file)
        tags_to_update = preprocess_flac_tags(tags, flac_path)

        # Transcode using flac | lame pipeline
        flac_cmd = [FLAC_CMD, '--decode', '--stdout', '--silent', str(flac_file)]
        lame_cmd = [LAME_CMD] + PRESETS[preset] + ['-', str(mp3_file)]

        print(f"Transcoding: {flac_file} -> {mp3_file}")
        try:
            with subprocess.Popen(flac_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as flac_proc:
                with subprocess.Popen(lame_cmd, stdin=flac_proc.stdout, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE) as lame_proc:
                    flac_proc.stdout.close()
                    _, flac_err = flac_proc.communicate()
                    _, lame_err = lame_proc.communicate()

                if flac_proc.returncode != 0:
                    print(f"FLAC decode failed: {flac_err.decode()}")
                    success = False
                    continue
                if lame_proc.returncode != 0:
                    print(f"LAME encode failed: {lame_err.decode()}")
                    success = False
                    continue

                if not mp3_file.exists() or mp3_file.stat().st_size == 0:
                    print(f"MP3 file {mp3_file} was not created or is empty")
                    success = False
                    continue

                # Write tags
                if not write_mp3_tags(mp3_file, tags_to_update):
                    success = False
                    continue

                # Embed image if available
                if album_image and album_image.exists():
                    if not embed_image_with_ffmpeg(mp3_file, album_image):
                        success = False
                        continue
                else:
                    print(f"No image available for {mp3_file}")

        except Exception as e:
            print(f"Error transcoding {flac_file}: {e}")
            success = False
            continue

    return success


def copy_images(src, dest):
    for root, _, files in os.walk(src):
        for file in files:
            if file.lower().endswith(('.jpg', '.png')):
                rel_path = Path(root).relative_to(src)
                dest_dir = dest / rel_path
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy(Path(root) / file, dest_dir / file)
                print(f"Copied {file} to {dest_dir / file}")


def create_torrent(folder_path, torrent_path, trackers):
    tracker_str = ",".join(t['url'] for t in trackers)
    cmd = f'mktorrent -p -a "{tracker_str}" -l 21 -o "{torrent_path}" "{folder_path}"'
    print(f"Creating torrent: {cmd}")
    return run_command(cmd)[0]


def process_album(flac_folder: Path, choice, del_src, create_torrent_flag, tracker_objs):
    folder_name = flac_folder.name
    v0_folder = re.sub(r'flac', 'MP3 V0', folder_name, flags=re.IGNORECASE)
    mp3_320_folder = re.sub(r'flac', 'MP3 320', folder_name, flags=re.IGNORECASE)

    v0_path = OUTPUT_DIR / v0_folder
    mp3_320_path = OUTPUT_DIR / mp3_320_folder

    tracker_name_prefix = tracker_objs[0]['name'].replace(" ", "_") if tracker_objs else "NoTracker"

    if choice == '4':
        print(f"Skipping: {folder_name}")
        return

    v0_success = mp3_320_success = False

    if choice in ('1', '3'):
        print("Converting to MP3 V0...")
        v0_success = convert(flac_folder, v0_path, 'V0')

    if choice in ('2', '3'):
        print("Converting to MP3 320...")
        mp3_320_success = convert(flac_folder, mp3_320_path, '320')

    if create_torrent_flag == 'y':
        if choice in ('1', '3') and v0_success:
            print("Copying images to V0 folder...")
            copy_images(flac_folder, v0_path)
            torrent_file = TORRENT_DIR / f"{tracker_name_prefix}_{v0_folder.replace(' ', '_')}.torrent"
            create_torrent(v0_path, torrent_file, tracker_objs)

        if choice in ('2', '3') and mp3_320_success:
            print("Copying images to 320 folder...")
            copy_images(flac_folder, mp3_320_path)
            torrent_file = TORRENT_DIR / f"{tracker_name_prefix}_{mp3_320_folder.replace(' ', '_')}.torrent"
            create_torrent(mp3_320_path, torrent_file, tracker_objs)

    if ((choice == '1' and v0_success) or
            (choice == '2' and mp3_320_success) or
            (choice == '3' and v0_success and mp3_320_success)):
        if del_src == 'y':
            print(f"Deleting source folder: {flac_folder}")
            shutil.rmtree(flac_folder)


def main():
    print("Welcome to DiRTY Transcode:")
    print("Transcode your FLAC to MP3 with one easy click.")
    print("FLAC folders must have 'flac' in the folder name.")
    print("You can also create a .torrent for your transcodes.\n")
    print("Note: Ensure a 'cover.jpg' or 'cover.png' is in the FLAC folder if no embedded images exist.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TORRENT_DIR.mkdir(parents=True, exist_ok=True)

    if shutil.which(FLAC_CMD) is None:
        print(f"Missing {FLAC_CMD}. Install with: sudo apt install flac")
        return
    if shutil.which(LAME_CMD) is None:
        print(f"Missing {LAME_CMD}. Install with: sudo apt install lame")
        return
    if shutil.which("mktorrent") is None:
        print("Missing `mktorrent`. Install with: sudo apt install mktorrent")
        return
    if shutil.which(FFMPEG_CMD) is None:
        print(f"Missing {FFMPEG_CMD}. Install with: sudo apt install ffmpeg")
        return

    flac_folders = [p for p in INPUT_DIR.iterdir() if p.is_dir() and re.search(r'flac', p.name, re.IGNORECASE)]
    if not flac_folders:
        print("No FLAC folders found.")
        return

    choices_dict = {}
    for flac_folder in flac_folders:
        choice, del_src, create_torrent, tracker_objs = prompt_conversion_choice(flac_folder.name)
        choices_dict[flac_folder] = (choice, del_src, create_torrent, tracker_objs)

    for flac_folder, (choice, del_src, create_torrent, tracker_objs) in choices_dict.items():
        process_album(flac_folder, choice, del_src, create_torrent, tracker_objs)

    print("\nAll done.")


if __name__ == "__main__":
    main()
