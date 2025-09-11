#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BlackSys.Steam - Download with steamcmd, crack with Goldberg, create with mktorrent.

"""

import os, json, shutil, subprocess, sys
from pathlib import Path
from typing import Optional, Tuple, List

# ---------------- paths & consts ----------------
SCRIPT_DIR   = Path(__file__).resolve().parent
REPLACER     = SCRIPT_DIR / "data" / "steam_api_replacer.py"
GAMES_ROOT   = SCRIPT_DIR / "games"
TORRENTS_DIR = SCRIPT_DIR / "torrents"
TRACKER_FILE = SCRIPT_DIR / "data" / "trackers.json"
STEAMCMD_BIN = shutil.which("steamcmd") or "/usr/games/steamcmd"

PLATFORM_LABELS = {"linux": "Linux", "windows": "Windows", "macos": "macOS"}

# ---------------- generic helpers ----------------
def shlex_quote(s: str) -> str:
    if not s or any(c.isspace() for c in s) or any(c in s for c in "\"'`$"):
        return '"' + s.replace('"', '\\"') + '"'
    return s

def steam_env() -> dict:
    env = os.environ.copy()
    env.setdefault("HOME", str(Path.home()))
    env.setdefault("STEAMCMDDIR", str(Path.home() / ".steam" / "steamcmd"))
    return env

def run_capture(cmd: List[str]) -> Tuple[int, str]:
    print("Executing:", " ".join(shlex_quote(a) for a in cmd))
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, env=steam_env())
        return 0, out
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output

def run(cmd: List[str]) -> int:
    print("Executing:", " ".join(shlex_quote(a) for a in cmd))
    try:
        proc = subprocess.run(cmd, check=False, env=steam_env())
        return proc.returncode
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 127

def prompt_yn(prompt: str, default: bool = True) -> bool:
    d = "Y/n" if default else "y/N"
    ans = input(f"{prompt} [{d}]: ").strip().lower()
    if not ans:
        return default
    return ans.startswith("y")

def prompt_choice(prompt: str, choices: List[str], default_index: int = 0) -> int:
    print(prompt)
    for i, c in enumerate(choices, start=1):
        marker = " (default)" if i-1 == default_index else ""
        print(f"  {i}. {c}{marker}")
    raw = input(f"Select (1-{len(choices)}): ").strip()
    if not raw:
        return default_index
    try:
        v = int(raw)
        return max(0, min(len(choices)-1, v-1))
    except ValueError:
        return default_index

# ---------------- steam: download ----------------
def build_batch_cmd(app_id: str, login_args: List[str], plan: List[Tuple[str, Path]]) -> List[str]:
    cmd: List[str] = [STEAMCMD_BIN] + login_args
    cmd += ["+app_info_update", "1", "+app_info_print", app_id]
    for plat_key, install_dir in plan:
        cmd += [
            "+@sSteamCmdForcePlatformType", plat_key,
            "+force_install_dir", str(install_dir),
            "+app_update", app_id, "validate"
        ]
    cmd += ["+quit"]
    return cmd

def parse_game_name(app_output: str, app_id: str) -> str:
    for line in app_output.splitlines():
        line = line.strip()
        if line.startswith('"name"'):
            parts = line.split('"')
            if len(parts) >= 4:
                name = parts[3]
                print(f"[INFO] Detected game name: {name}")
                return name
    print("[WARN] Could not parse game name; using fallback.")
    return f"App {app_id}"

def looks_like_guard_or_login_prompt(text: str) -> bool:
    t = (text or "").lower()
    return ("steam guard" in t) or ("confirm the login" in t) or ("login failure" in t)

# ---------------- crack step ----------------
def mass_crack(target_dir: Path) -> bool:
    if not REPLACER.exists():
        print(f"[ERROR] Missing replacer script: {REPLACER}")
        return False
    if not target_dir.exists():
        print(f"[ERROR] Target does not exist: {target_dir}")
        return False
    print(f"\n[CRACK] Running replacer on: {target_dir}")
    return run(["python3", "-u", str(REPLACER), str(target_dir)]) == 0

# Trackers JSON
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
    url  = input("Announce URL: ").strip()
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

def run_shell(command: str) -> bool:
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {command}\nError: {result.stderr}")
        return False
    print(f"Command succeeded: {command}")
    return True

def create_torrent(folder_path: Path, torrent_path: Path, trackers: List[dict]) -> bool:
    tracker_str = ",".join(t['url'] for t in trackers)
    cmd = f'mktorrent -p -a "{tracker_str}" -l 21 -o "{torrent_path}" "{folder_path}"'
    return run_shell(cmd)


# ---------------- main ----------------
def main() -> int:
    print("=" * 72)
    print(" BlackSys Suite — Single Login (Cached-first FULL batch) + FLAC-style Torrents")
    print("=" * 72)

    cracked_dirs: List[Path] = []
    title_root: Optional[Path] = None
    app_id: Optional[str] = None
    game_name: Optional[str] = None

    # 1) Download?
    if prompt_yn("Are we downloading games from Steam today?", default=True):
        which = prompt_choice(
            "Which platform(s) to download?",
            ["Linux only", "Windows only", "macOS only", "All"],
            default_index=3
        )
        selected_platforms = (
            ["linux", "windows", "macos"] if which == 3
            else ["linux"] if which == 0
            else ["windows"] if which == 1
            else ["macos"]
        )

        app_id = input("Enter Steam App ID: ").strip()
        if not app_id.isdigit():
            print("[ERROR] App ID must be numeric.")
            return 2
        username = input("Steam username: ").strip()

        # Prepare temp plan/dirs (rename after we learn the proper game name)
        tmp_name   = f"App_{app_id}"
        title_root = GAMES_ROOT / tmp_name
        title_root.mkdir(parents=True, exist_ok=True)
        plan: List[Tuple[str, Path]] = []
        for pk in selected_platforms:
            d = title_root / f"{tmp_name}-{pk}"
            d.mkdir(parents=True, exist_ok=True)
            plan.append((pk, d))

        # Try FULL BATCH with cached login first
        cached_cmd = build_batch_cmd(app_id, ["+login", username], plan)
        code, out = run_capture(cached_cmd)

        if code == 0 and not looks_like_guard_or_login_prompt(out):
            print("[INFO] Cached login worked; proceeding without password.")
            batch_output = out
        else:
            print("[INFO] Cached login not available. Enter credentials once.")
            password = input("Steam password: ").strip()
            guard = None
            if prompt_yn("Provide Steam Guard code now? (optional)", default=False):
                guard = input("Steam Guard code (e.g., ABCDE): ").strip()
            login_args = ["+login", username, password] + (["+set_steam_guard_code", guard] if guard else [])
            pw_cmd = build_batch_cmd(app_id, login_args, plan)
            code, out = run_capture(pw_cmd)
            if code != 0:
                print("[ERROR] steamcmd session failed.")
                return code
            batch_output = out

        # Parse proper game name; rename folders if needed
        game_name = parse_game_name(batch_output, app_id)
        real_root = GAMES_ROOT / game_name
        if real_root != title_root:
            real_root.mkdir(parents=True, exist_ok=True)
            for pk, old_dir in plan:
                new_dir = real_root / f"{game_name}-{pk}"
                if old_dir.exists():
                    new_dir.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        old_dir.rename(new_dir)
                    except OSError:
                        shutil.copytree(old_dir, new_dir, dirs_exist_ok=True)
                        shutil.rmtree(old_dir, ignore_errors=True)
            try:
                title_root.rmdir()
            except Exception:
                pass
            title_root = real_root

        print("\n[INFO] Downloaded directories:")
        for pk in selected_platforms:
            print("  -", title_root / f"{game_name}-{pk}")

        # Clean steamapps folders
        for pk in selected_platforms:
            sa = (title_root / f"{game_name}-{pk}") / "steamapps"
            if sa.exists():
                shutil.rmtree(sa, ignore_errors=True)

    else:
        print("[SKIP] Download step skipped.")
        titles = [p for p in GAMES_ROOT.iterdir() if p.is_dir()]
        if not titles:
            print("[INFO] No existing games under 'games/'. Nothing to crack/torrent.")
            return 0
        idx = prompt_choice("Select an existing game folder to work on:", [t.name for t in titles], default_index=0)
        title_root = titles[idx]
        app_id = None
        game_name = title_root.name

    # 2) Crack?
    if title_root and prompt_yn("\nAre we running the crack today?", default=True):
        platform_dirs = [p for p in title_root.iterdir() if p.is_dir()]
        if not platform_dirs:
            print("[WARN] No platform directories under", title_root)
        for pd in platform_dirs:
            if mass_crack(pd):
                cracked_dirs.append(pd)
    else:
        print("[SKIP] Crack step skipped.")

    # 3) Torrents? 
    if cracked_dirs and prompt_yn("\nDo you want to create a .torrent? (y/n)", default=True):
        trackers = select_trackers()  
        if not trackers:
            print("No trackers selected; skipping torrent creation.")
        else:
            TORRENTS_DIR.mkdir(parents=True, exist_ok=True)
            tracker_name_prefix = trackers[0]['name'].replace(" ", "_") if trackers else "NoTracker"
            for game_dir in cracked_dirs:
                torrent_name = f"{tracker_name_prefix}_{game_dir.name.replace(' ', '_')}.torrent"
                torrent_path = TORRENTS_DIR / torrent_name
                print(f"\n[TORRENT] Creating: {torrent_path}")
                ok = create_torrent(game_dir, torrent_path, trackers)
                if not ok:
                    print("[WARN] Torrent creation failed for:", game_dir)
    elif not cracked_dirs:
        print("[INFO] No cracked folders in this run; skipping torrent prompt.")
    else:
        print("[SKIP] Torrent creation skipped.")

    print("\n[DONE] BlackSys Suite finished.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPTED]")
        sys.exit(130)
