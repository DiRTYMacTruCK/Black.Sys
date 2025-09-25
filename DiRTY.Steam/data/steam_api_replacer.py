#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

# Configuration: Map of platform/arch to replacement file paths
REPLACEMENT_FILES = {
    # Steam API files
    'win_32': os.path.join("win_32", "steam_api.dll"),
    'win_64': os.path.join("win_64", "steam_api64.dll"),
    'linux_32': os.path.join("linux_32", "libsteam_api.so"),
    'linux_64': os.path.join("linux_64", "libsteam_api.so"),
    'macos': os.path.join("macos", "libsteam_api.dylib"),
    # Steam Client files
    'steamclient_linux_32': os.path.join("linux_32", "steamclient.so"),
    'steamclient_linux_64': os.path.join("linux_64", "steamclient.so"),
    'steamclient_macos': os.path.join("macos", "steamclient.dylib")
}
# Ensure paths are absolute and relative to script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))
for key, value in REPLACEMENT_FILES.items():
    REPLACEMENT_FILES[key] = os.path.join(script_dir, value)

ARCH_32_HINTS = ['linux32', 'lib32', 'i386', 'i686', 'x86/', 'x86\\', '32bit', 'win32']
ARCH_64_HINTS = ['linux64', 'lib64', 'x86_64', 'amd64', 'x64/', 'x64\\', '64bit', 'win64']

def detect_linux_architecture(file_path):
    """
    Detect the architecture (32-bit or 64-bit) of a Linux file.
    Checks the file path and sibling files/directories for hints.
    Returns '32' or '64'.
    """
    path = Path(file_path)
    full_path = str(path.resolve()).lower()

    # Check the file's own path for architecture hints
    if any(x in full_path for x in ARCH_32_HINTS):
        return '32'
    elif any(x in full_path for x in ARCH_64_HINTS):
        return '64'

    # Check sibling files and directories for architecture hints
    parent_dir = path.parent
    siblings = list(parent_dir.iterdir())

    for sibling in siblings:
        sibling_name = sibling.name.lower()
        # Check if any architecture hint is in the sibling's name
        if any(hint in sibling_name for hint in ARCH_32_HINTS):
            print(f"  Found 32-bit hint in sibling: {sibling.name}")
            return '32'
        elif any(hint in sibling_name for hint in ARCH_64_HINTS):
            print(f"  Found 64-bit hint in sibling: {sibling.name}")
            return '64'

    # If we still can't determine, ask the user
    print(f"Warning: Could not determine architecture for {path}")
    print(f"  Full path: {full_path}")
    print(f"  Parent directory: {parent_dir}")

    while True:
        choice = input("Input 1 for 32-bit, 2 for 64-bit, o to open file explorer: ")
        if choice == 'o':
            os.system(f"xdg-open {parent_dir}")
        elif choice == '1':
            return '32'
        elif choice == '2':
            return '64'

def identify_steam_file(file_path):
    """
    Identify the type of Steam API/Client file based on filename and path.
    Returns a tuple of (file_type, full_path) or None if not a Steam file.
    """
    path = Path(file_path)
    filename = path.name.lower()

    # Windows Steam API files
    if filename == 'steam_api.dll':
        return ('win_32', path)
    elif filename == 'steam_api64.dll':
        return ('win_64', path)

    # Linux Steam API files
    elif filename == 'libsteam_api.so':
        arch = detect_linux_architecture(path)
        if arch == '32':
            return ('linux_32', path)
        else:  # arch == '64'
            return ('linux_64', path)

    # macOS Steam API files
    elif filename == 'libsteam_api.dylib':
        return ('macos', path)

    # Linux Steam Client files
    elif filename == 'steamclient.so':
        arch = detect_linux_architecture(path)
        if arch == '32':
            return ('steamclient_linux_32', path)
        else:  # arch == '64'
            return ('steamclient_linux_64', path)

    # macOS Steam Client files
    elif filename == 'steamclient.dylib':
        return ('steamclient_macos', path)

    return None

def replace_steam_files(search_dir, dry_run=False):
    """
    Search for and replace Steam API/Client files in the given directory.
    """
    search_path = Path(search_dir)
    if not search_path.exists():
        print(f"Error: Directory '{search_dir}' does not exist!")
        return

    # Check for replacement files and collect missing ones
    missing_replacements = []
    valid_replacements = {}
    for platform, replacement_path in REPLACEMENT_FILES.items():
        if Path(replacement_path).exists():
            valid_replacements[platform] = replacement_path
        else:
            missing_replacements.append((platform, replacement_path))

    if missing_replacements:
        print("Warning: The following replacement files are missing and will be skipped:")
        for platform, path in missing_replacements:
            print(f"  {platform}: {path}")
        if not valid_replacements:
            print("\nError: No valid replacement files found. Exiting.")
            return

    found_files = []
    replaced_files = []

    # Search for Steam files
    print(f"Searching in: {search_path.resolve()}")
    print("-" * 60)

    for root, dirs, files in os.walk(search_path):
        for file in files:
            file_path = Path(root) / file
            result = identify_steam_file(file_path)

            if result:
                file_type, path = result
                if file_type in valid_replacements:
                    found_files.append((file_type, path))
                    print(f"Found: {file_type} - {path}")

    if not found_files:
        print("No matching Steam API/Client files found for available replacements.")
        return

    # Replace files
    print("\n" + "-" * 60)
    if dry_run:
        print("DRY RUN MODE - No files will be replaced")
        print("-" * 60)

    for file_type, path in found_files:
        replacement_path = Path(valid_replacements[file_type])

        if dry_run:
            print(f"Would replace: {path}")
            print(f"         with: {file_type}")
        else:
            try:
                # Create backup
                backup_path = path.with_suffix(path.suffix + '.backup')
                if not backup_path.exists():
                    shutil.copy2(path, backup_path)
                    print(f"Created backup: {backup_path}")

                # Replace file
                shutil.copy2(replacement_path, path)
                replaced_files.append(path)
                print(f"Replaced: {path}")
                print(f"    with: {replacement_path}")
            except Exception as e:
                print(f"Error replacing {path}: {e}")

    # Summary
    print("\n" + "-" * 60)
    print(f"Summary: Found {len(found_files)} Steam file(s)")
    if not dry_run:
        print(f"Successfully replaced {len(replaced_files)} file(s)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python steam_api_replacer.py <directory> [--dry-run]")
        print("\nExample:")
        print("  python steam_api_replacer.py /path/to/game")
        print("  python steam_api_replacer.py /path/to/game --dry-run")
        return

    search_dir = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    print("Steam API/Client File Replacer")
    print("=" * 60)

    # Show current configuration
    print("\nConfigured replacement files:")
    print("\nSteam API files:")
    api_files = ['win_32', 'win_64', 'linux_32', 'linux_64', 'macos']
    for platform in api_files:
        path = REPLACEMENT_FILES[platform]
        exists = "✓" if Path(path).exists() else "✗"
        print(f"  {platform}: {exists} {path}")

    print("\nSteam Client files:")
    client_files = ['steamclient_linux_32', 'steamclient_linux_64', 'steamclient_macos']
    for platform in client_files:
        path = REPLACEMENT_FILES[platform]
        exists = "✓" if Path(path).exists() else "✗"
        print(f"  {platform}: {exists} {path}")
    print()

    replace_steam_files(search_dir, dry_run)

if __name__ == "__main__":
    main()
