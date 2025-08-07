import os
import re
import json
import shutil
import subprocess
from pathlib import Path

# === CONFIG ===
FLAC2MP3_SCRIPT = './flac2mp3.pl'
INPUT_DIR = Path('../flac')
#OUTPUT_DIR = Path('../mp3')
OUTPUT_DIR = Path('/mnt/ggn_fl/red_uploads_dl')
TORRENT_DIR = Path('../torrents')
TRACKER_FILE = Path("trackers.json")

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
        if choice in ('1','2','3','4'):
            break
        print("Invalid, please enter 1, 2, 3, or 4")

    create_torrent = 'n'
    tracker_objs = []
    if choice in ('1','2','3'):
        while True:
            create_torrent = input("Do you want to create a .torrent? (y/n): ").lower()
            if create_torrent in ('y','n'):
                break
            print("Please enter y or n")
        if create_torrent == 'y':
            tracker_objs = select_trackers()

        while True:
            del_src = input("Do you want to delete the flac after transcoding? (y/n): ").lower()
            if del_src in ('y','n'):
                break
            print("Please enter y or n")
    else:
        del_src = 'n'

    return choice, del_src, create_torrent, tracker_objs

def run_command(command):
    result = subprocess.run(command, shell=True)
    return result.returncode == 0

def convert(flac_path, output_path, preset):
    cmd = f'"{FLAC2MP3_SCRIPT}" --preset={preset} "{flac_path}" "{output_path}"'
    print(f"Running: {cmd}")
    return run_command(cmd)

def copy_images(src, dest):
    for root, _, files in os.walk(src):
        for file in files:
            if file.lower().endswith(('.jpg', '.png')):
                rel_path = Path(root).relative_to(src)
                dest_dir = dest / rel_path
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy(Path(root) / file, dest_dir / file)

def create_torrent(folder_path, torrent_path, trackers):
    tracker_str = ",".join(t['url'] for t in trackers)
    cmd = f'mktorrent -p -a "{tracker_str}" -l 21 -o "{torrent_path}" "{folder_path}"'
    print(f"Creating torrent: {cmd}")
    return run_command(cmd)

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
        v0_path.mkdir(parents=True, exist_ok=True)
        print("Converting to MP3 V0...")
        v0_success = convert(flac_folder, v0_path, 'V0')

    if choice in ('2', '3'):
        mp3_320_path.mkdir(parents=True, exist_ok=True)
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

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TORRENT_DIR.mkdir(parents=True, exist_ok=True)

    if not Path(FLAC2MP3_SCRIPT).exists():
        print(f"Missing {FLAC2MP3_SCRIPT}")
        return
    if shutil.which("mktorrent") is None:
        print("Missing `mktorrent`. Install with: sudo apt install mktorrent")
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
