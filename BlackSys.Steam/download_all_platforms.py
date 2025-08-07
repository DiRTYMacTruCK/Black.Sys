#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import requests
import shutil

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Download Steam games for multiple platforms")
    parser.add_argument("--appid", required=True, help="Steam App ID")
    parser.add_argument("--username", default="anonymous", help="Steam username (use 'anonymous' for games that support it)")
    args = parser.parse_args()

    steam_cmd_path = "/usr/games/steamcmd"  # Path for APT-installed SteamCMD
    games_root_folder = "/home/dirty/projects/BlackSys/BlackSys.Steam/games"  # Download directory

    # Check if SteamCMD exists
    if not os.path.exists(steam_cmd_path):
        print(f"\033[91mError: SteamCMD not found at {steam_cmd_path}\033[0m")
        print("Please ensure SteamCMD is installed (e.g., 'sudo apt install steamcmd').")
        exit(1)

    # Create Games folder if it doesn't exist
    os.makedirs(games_root_folder, exist_ok=True)

    print(f"\033[96mFetching game name for App ID: {args.appid}...\033[0m")

    # Fetch game name from Steam API
    game_name = f"AppID-{args.appid}"
    try:
        response = requests.get(f"https://store.steampowered.com/api/appdetails?appids={args.appid}")
        response.raise_for_status()
        data = response.json()
        if data[args.appid]["success"]:
            game_name = data[args.appid]["data"]["name"]
            print(f"\033[92mGame name: {game_name}\033[0m")
        else:
            print("\033[93mCould not fetch game name, using App ID as folder name.\033[0m")
    except requests.RequestException:
        print("\033[93mAPI call failed, using App ID as folder name.\033[0m")

    # Clean up game name for folder usage (remove invalid characters)
    game_name = re.sub(r'[<>:"/\\|?*]', '', game_name).strip()  # Remove invalid chars for Linux
    game_name = game_name.replace('\0', '')  # Remove null bytes

    # Create game directory inside Games folder
    game_folder = os.path.join(games_root_folder, game_name)
    os.makedirs(game_folder, exist_ok=True)

    print(f"\n\033[96mDownloading all platforms for: {game_name} (App ID: {args.appid})\033[0m")
    print(f"Using username: {args.username}\n")

    # Platform configurations
    platforms = [
        {"name": "Windows", "flag": "windows"},
        {"name": "Linux", "flag": "linux"},
        {"name": "macOS", "flag": "macos"}
    ]

    for platform in platforms:
        print("\033[90m" + "=" * 40 + "\033[0m")
        print(f"\033[93mDownloading {platform['name']} version...\033[0m")
        print("\033[90m" + "=" * 40 + "\033[0m")

        platform_folder = os.path.join(game_folder, f"{game_name}-{platform['name']}")
        absolute_platform_path = os.path.abspath(platform_folder)

        # Run SteamCMD
        arguments = [
            steam_cmd_path,
            "+@sSteamCmdForcePlatformType", platform["flag"],
            "+force_install_dir", absolute_platform_path,
            "+login", args.username,
            "+app_update", args.appid, "validate",
            "+quit"
        ]

        try:
            subprocess.run(arguments, check=True)
        except subprocess.CalledProcessError as e:
            print(f"\033[91mError downloading {platform['name']} version: {e}\033[0m")
            continue

        # Clean up steamapps directory
        steam_apps_path = os.path.join(platform_folder, "steamapps")
        if os.path.exists(steam_apps_path):
            print(f"\033[95mCleaning up {platform['name']} steamapps directory...\033[0m")
            shutil.rmtree(steam_apps_path, ignore_errors=True)

        print()

    print("\033[92m" + "=" * 40 + "\033[0m")
    print("\033[92mAll downloads complete and cleaned up!\033[0m")
    print(f"\033[92mFiles saved in: {game_folder}\033[0m")
    print("\033[92m" + "=" * 40 + "\033[0m")

if __name__ == "__main__":
    main()
