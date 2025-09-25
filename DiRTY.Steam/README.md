# DiRTY Steam 🚀



**Download → Crack → Create //**

Download - Download Windows/Linux/MacOS games using steamcmd and game appid.

Crack - Crack each version using the Goldberg crack.  Backups cracked files.

Create - Create tor files for your favorite trackers.

---
## 📦 Requirements

- **Linux** (tested on Debian)
- **Python 3.8+**
- **SteamCMD**
  ```bash
  sudo apt update
  sudo apt install steamcmd
  ```
- **mktorrent** (for torrent creation)
  ```bash
  sudo apt install mktorrent
  ```

> The script exports `HOME` and `STEAMCMDDIR` so SteamCMD finds the same cached login (“sentry”) as your terminal sessions.

---

## 🗂️ Folder layout

```
project/
├─ dirty.steam.py
├─ games/
│  └─ <Game Name>/
│     ├─ <Game Name>-linux/
│     ├─ <Game Name>-windows/
│     └─ <Game Name>-macos/
├─ torrents/
└─ data/
   └─ steam_api_replacer.py  
   └─ trackers.json
```

---

## ▶️ Quick start

```bash
python3 dirty.steam.py
```

## 🎮 Step 1 — Download (steamcmd) 

The script builds **one SteamCMD command** like:

```
+login <user> [<pass>] [+set_steam_guard_code <code>]
+app_info_update 1
+app_info_print <AppID>             # parse the game "name"
# then, for each selected platform:
+@sSteamCmdForcePlatformType <linux|windows|macos>
+force_install_dir "<.../<Game Name>-<platform>>"
+app_update <AppID> validate
+quit
```

---

## 🧩 Step 2 — Crack (Goldberg)

If `./data/steam_api_replacer.py` exists, it’s run **per platform directory**:

```bash
python3 -u data/steam_api_replacer.py "<games/<Game Name>/<Game Name>-<platform>"
```

- Calls use **argument lists** (not `shell=True`), so paths with spaces are handled safely.

---

## 🌐 Step 3 — Create (.torrent)

Tracker list:

- **Trackers live in `trackers.json`** inside  `/data`, e.g.:
  ```json
  [
    { "name": "MyTracker",     "url": "https://announce.mytracker.tld/announce" },
    { "name": "BackupTracker", "url": "https://backup.example/announce" }
  ]
  ```
- **Menu options:**
  - `1–7` → use a single tracker
  - `8` → **All** trackers
  - `9` → **Add** (append a tracker to `trackers.json`)
  - `0` → **Manage** (delete trackers from `trackers.json`)

**Torrent build:** mirrors the transcoder:

```
mktorrent -p -a "<comma-separated-announce-urls>" -l 21 -o "<TorrentName>.torrent" "<PlatformFolder>"
```

- Torrents go to `./torrents/`
- Naming pattern:  
  `"<TrackerName>_<PlatformFolderName>.torrent"`  
  e.g., `MyTracker_NEXT_JUMP:_Shmup_Tactics-windows.torrent`

---


## 📝 Legal

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
