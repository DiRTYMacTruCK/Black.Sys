# BlackSys Steam 🚀

**Download → Crack → Create //**

This tool stitches your three workflows into a single, streamlined CLI. You decide what to run and what to skip — perfect for quick iteration or full pipeline runs.

## ✨ What’s new (highlights)
- **Single SteamCMD session per run:** one `+login` covers **all selected platforms** (Linux/Windows/macOS). No re-auth between platforms.
- **Cached-first login:** we try `+login <user>` first so your saved sentry/password is used; on failure we prompt **once** and continue the batch.
- **Auto game name from AppID:** pulled via `+app_info_print <AppID>` (no manual naming).
- **Safer subprocess calls:** robust path handling — **spaces are fine**, no hard-coded folder names.
- **FLAC-style torrent flow:** identical UX to your transcoder. **Trackers live in `trackers.json`** (Add / Manage / pick one / pick All). Torrents are built with **`mktorrent`** (no extra JSON manifests here).

> Script name: **`blacksys.steam.py`**

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
├─ trackers.json          # FLAC-style tracker config (name/url)
└─ data/
   └─ steam_api_replacer.py   # used by the Mass Crack step
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
   - If **Yes** → runs your `data/steam_api_replacer.py` **per platform folder** under that game.

3) **Do you want to create a .torrent?**  
   - If **Yes** → opens the **FLAC-style tracker picker/manager**.

---

## 🎮 Step 1 — Download (single session, auto game name)

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

## 🧩 Step 2 — Mass Crack

If `./data/steam_api_replacer.py` exists, it’s run **per platform directory**:

```bash
python3 -u data/steam_api_replacer.py "<games/<Game Name>/<Game Name>-<platform>"
```

- Calls use **argument lists** (not `shell=True`), so paths with spaces are handled safely.

---

## 🌐 Step 3 — Torrents (FLAC-style UX)

Exactly like your transcoder’s UI:

- **Trackers live in `trackers.json`** at repo root, e.g.:
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

## 🛠️ Tips & gotchas

- **Cached login works in terminal but not in script?**  
  The script sets `HOME` and `STEAMCMDDIR` to your user defaults so SteamCMD should pick up the same sentry/password. If you store SteamCMD data in a non-standard place, set them before running:
  ```bash
  export HOME=/your/home
  export STEAMCMDDIR=/your/home/.steam/steamcmd
  python3 blacksys.steam.py
  ```
- **“Please use force_install_dir before logon!”**  
  Benign in this flow. We keep one login for the entire batch; `force_install_dir` is set before each `app_update` and downloads succeed.
- **Windows/macOS depots**  
  Some apps depend on OS-specific depots. You might see “missing required app ######” warnings; main app depots generally still download.
- **Crack step appears to hang**  
  This version passes the directory as a single arg (no path splitting). If your replacer prompts per file, consider a non-interactive flag (if supported).

---

## ✅ Changelog (recent)

- Renamed script to **`blacksys.steam.py`**.
- **One SteamCMD session** per run; no re-auth between platforms.
- **Cached-first login** with seamless **once-only** fallback to password/guard.
- **Game name auto-detection** from `+app_info_print <AppID>`.
- **FLAC-style torrent workflow** using `trackers.json` (Add/Manage/All/Single) and `mktorrent`.
- Safer subprocess calls; **spaces in paths** handled everywhere.
- Cleans nested `steamapps/` from platform dirs after download.

---

## 📝 Legal

Only download/use content you own the rights to. Follow Valve/Steam and tracker policies/EULAs.
