# BlackSys Steam 🚀



**Download → Crack → Create //**

Download - Download Windows/Linux/MacOS games using steamcmd and game appid.

Crack - Crack each version using the Goldberg crack.  Backups cracked files.

Create - Create tor files for your favorite trackers.

## ✨ What’s new 
- **Fixed steamcmd login:** one `+login` covers **all selected platforms** (Linux/Windows/macOS). No re-auth between platforms.
- **Cached-first login:** we try `+login <user>` first so your saved sentry/password is used; on failure we prompt **once** and continue the batch.
- **Auto game name from AppID:** pulled via `+app_info_print <AppID>`.

---
## 📦 Requirements

- **Linux** (tested on Mint/Ubuntu)
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
├─ blacksys.steam.py
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
python3 blacksys.steam.py
```

You’ll see three simple menus:

1) **Are we downloading games from Steam today?**  
   - If **Yes** → choose **Linux only / Windows only / macOS only / All**, then enter **AppID** and **username**.  
     - The script attempts **cached login** (`+login <user>`) first (no password/2FA).  
     - If cached login isn’t available, it prompts **once** for password (and optional guard), then runs **all platform downloads in a single SteamCMD session**.
   - If **No** → pick an **existing game** under `./games` and continue.

2) **Are we running the crack today?**  
   - If **Yes** → runs `data/steam_api_replacer.py` 

3) **Do you want to create a .torrent?**  
   - If **Yes** → opens the **tracker picker/manager**.

---

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
