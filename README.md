# StreamMii-Monolithic

**A simple tool that converts media into Wii compatible formats for smooth playback.**

---

### 🤘 How to use:
```
Put StreamMii in / next to your media, run it, pick a category, confirm. Done.

  python streammii-monolithic-v(most recent).py

It now asks before doing anything, and KEEPS your originals by default.

Optional flags:
  --path DIR         scan DIR instead of the script's own folder
  --dry-run          show exactly what it would do, change nothing
  -y / --yes         skip the confirmation prompt (for scripts)
  --no-delete        never delete originals (overrides config)
  --force-reencode   re encode even files that are already Wii ready

By default it now SKIPS files that are already Wii ready, remuxes when only the
container is wrong, and re encodes audio only when the video's already fine 
so re runs are way faster. Set "skip_compliant": false in ~/streammii/config.json
to force a full re encode pass. Output audio is downmixed to AAC stereo.
```

## 🚀 Features:

* **GPU Acceleration Support:**
    * **AMD.**
    * **NVIDIA** (NVENC).
    * **Intel** (QSV).
    * **CPU fallback** (not recommended due to lower quality & performance).
* **Automatic media metadata handling.**

### 🛠️ Now you can use flags:
```
--path DIR         scan DIR instead of the script's folder
--dry-run          plan only, change nothing
-y / --yes         skip the confirmation prompt
--no-delete        never delete originals (overrides config)
--force-reencode   re encode even files that are already Wii ready
```

---

## 🛠️ Output Settings:

| Parameters: | Configurations: |
| :--- | :--- |
| **Resolution:** | 640x360 or 640x480 depending on aspect ratio. |
| **Scaling:** | Lanczos resampling. |
| **Bitrate:** | 1000 kbps. |
| **FPS:** | **Usually** matches source media. |

---

## 📁 Supported Media Types:

* Movies.
* TV Shows.
* <details>
  <summary>Adult Content. </summary>

  Solo, Group, JAV.

  </details>
* Audio.
* Documentaries.
* K-Drama.
* Anime.
* <details>
  <summary>Sports. </summary>

  Team Sports > Football, Basketball, Volleyball, Rugby, Baseball, Softball, Handball.
  
  Combat Sports > Boxing, MMA, Wrestling, Karate.
  
  Winter Sports > Skiing, Snowboarding, Ice Skating, Bobsledding.
  
  Water Sports > Surfing, Rowing, Kayaking, Synchronized Swimming.
  
  Motor Sports > F1, MotoGP.
  
  Individual Sports > Athletics (Track and Field), Tennis, Golf, Pool, Swimming, Badminton, Table Tennis, Cycling, Gymnastics.
  
  Equestrian > Show Jumping, Dressage.
  
  Other > Cricket, Hockey.

  </details>

---

## 💻 System Requirements:

* `ffmpeg` must be installed and available in your system `PATH`.
* `python` must be installed and available in your system `PATH`.

### 🔨 Installing packages:

```bash
# pinned + hash verified install: (recommended)
pip install --require-hashes -r requirements.txt
# Old method: (not recommended)
pip install guessit requests colorama
```
### 🔨 How to use the noob installer for Linux:
```
sudo chmod +x noob-install-by-motanu.sh
./noob-install-by-motanu.sh
Works and tested on Debian/Ubuntu/Mint, Fedora/RHEL/CentOS, Arch/Manjaro, openSUSE, Alpine.

Or if you use arm...

sudo chmod +x arm-noob-install-motan.sh
./arm-noob-install-motan.sh

AARCH64 should work fine on these:
- Ubuntu (22.04 & 24.04).
- Linux Mint (21 & 22 & 22.3).
- Debian (11 & 12).
- Raspberry Pi OS (Bookworm and Bullseye).
- Arch linux.
- Manjaro.
- Fedora (38 & 39 & 40).
- openSUSE (Leap & Tumbleweed).
- Alpine 3.18+

ARMV6 & ARMV7 should work fine on these:
- Raspberry Pi OS (Bookworm and Bullseye).
- Debian (11 & 12).

❗ Partially working / limited: ❗
- Fedora on armv7 (Fedora dropped 32-bit arm since F37).
- Alpine on armv6 (build FFmpeg from source).
- RHEL & CentOS (needs EPEL + RPM Fusion added manually).
- Ubuntu 20.04 (python3-venv may need manual install).

❌ !!!! NOT COMPATIBLE WITH Gentoo, NixOS, Void Linux, Slackware, Android (Termux) !!!! ❌
❌ !!!! We will not provide support for issues you will encounter on aarch64 & armv6 & armv7 !!!! ❌
```
### 🔨 Windows:
```
Run the executable from the release/repo(depricated), OR use the batch installer (recommeded).

The batch installer (NOOB_SETUP_WINGET.bat) now uses winget, which verifies every
download against MicroSLOP's signed manifest before installing and no more
unverified downloads or piped scripts. winget ships by default on Win10 1809+
and Win11. No winget? The installer prints manual steps instead of running
anything unverified (install "App Installer" from the MS Store to get winget).

As you know me, i dont remove old methods or versions, you are free to use the old installers,
but you are not as safe as with the new installers...

Or if you use arm...
❗ You are on your own but we will give you the sources you need. ❗
❌ We can not help you with any issues that you will encounter. ❌

ffmpeg: https://github.com/tordona/ffmpeg-win-arm64
python: https://www.python.org/downloads/release/python-31313/
```
### 🔨 MacOS with Apple Silicon SoC:
```
❗ You are on your own but we will give you the sources you need. ❗
❌ We can not help you with any issues that you will encounter. ❌

There are multiple sources of ffmpeg for Apple Silicon, and each have their ups and downs, it's up to you to use the best one for you.
1. https://github.com/Vargol/ffmpeg-apple-arm64-build?tab=readme-ov-file
2. https://gitlab.com/martinr92/ffmpeg
3. https://osxexperts.net/

Now you will need Python:
https://www.python.org/downloads/release/python-3144/

❗❗❗❗ Note: We do not know how any of this will work with the new MacBook Neo, because it is slighty diffrent from their M SoC series, and we do not own one so we can not test ❗❗❗❗
```

### 🔨 MacOS with Intel CPU:
```
❗ You are on your own but we will give you the sources you need. ❗
❌ We can not help you with any issues that you will encounter. ❌

ffmpeg: https://evermeet.cx/ffmpeg/ffmpeg-123838-gb462674645.7z
python: https://www.python.org/downloads/release/python-3144/

❗❗❗❗ Note: Hackintosh not tested yet. ❗❗❗❗
```
### 🤘 Why StreamMii-Monolithic?
```
The same StreamMii but now it is monolithic. What does that mean? Instead of downloading 6 files you download 1 file, which is easier to manage. INSTALLER IS NOT INCLUDED IN IT!
To get it started now you need to download the monolithic StreamMii and your respective OS n00b installer, run the installler and then StreamMii-Monolithic.
Changes:
> 3x Times faster probing! (than monolithic v1 and cucu-labs version)
> When fails, now it fails with a clean error instead of crashing! (monolithic v1 and cucu-labs version were crashing on fail)
> New H.264 encoder for non standard pixel formats that will not ruin the playback! (monolithic v1 and cucu-labs version do not have this feature)
> Also its now more safe to run it, it won't delete itself or delete anything else or outside of it. (The monolithic v1 version and cucu-labs version may delete itself or files around it!)
> Bug fixes! (that were in monolithic v1 and cucu-labs version)
> Secure IMDB! (monolithic v1 and cucu-labs version did not have)
> V3 RELASED AND OUT!!!!!!!!!!!!! SEE BELOW FOR THE FULL PATCH NOTES AND ADDONS!!!!
> V3: security hardening (verified installers, no piped scripts), skips
  already converted files, audio only fast path, stereo downmix, smoother
  playback (bitrate cap), keeps originals by default, --dry-run + flags.
```

### Behavior changes to know about
- The processed log signature changed from `name|size_kb` to
  `name|size_bytes|mtime` (kills collisions). Existing `processed.txt` entries
  won't match, so files get re checked once  but the new skip if compliant logic
  means already encoded outputs are skipped, not re encoded, so it's cheap.
- Originals are kept by default now. Pass `--delete`-equivalent via config
  (`delete_originals: true`) or just answer the prompt.

### V3 Release:
- **Skip already Wii ready files.** v2 and v1 re encoded *everything* unconditionally.
  v3 probes codec/res/pix_fmt/channels and:
  - **skip** if it's already H.264 ≤640×480 yuv420p with AAC ≤2ch in an `.mkv`,
  - **remux** (stream copy, no re encode) if it's compliant but in another container,
  - **audio only** re encode (copy video, fix audio) if only the audio is wrong  
    huge win on good-video / 5.1-audio files,
  - **full encode** otherwise.
  Toggle off with `skip_compliant: false` in config, or `--force-reencode`.
- **Stereo downmix** (`-ac 2`) WiiMC is stereo; 5.1 sources no longer play wrong
  or waste bitrate.
- **VBV cap** (`-maxrate 1200k -bufsize 2000k`, H.264 encoders only) stops
  bitrate spikes that stutter on the Wii's small decode buffer.
- **Don't re transcode existing `.mp3`** in audio mode (avoids generational loss).
- **`--dry-run`** — shows exactly what would happen to each file, touches nothing.
- **Pre run summary + end-of-run summary** (`processed / skipped / failed`).
- **colorama** is now actually initialized (it was a listed but unused dep) so the
  pink ANSI output renders on legacy Windows consoles.
- **ETA** on the encode progress bar.
- .bat installer downloaded the Python installer with no integrity check **and** piped Chocolatey's install.ps1 into iex (RCE as admin) I rewrote on **winget**, which verifies each package's SHA256 against MicroSLOP's signed manifest before running. No unverified downloads, no piped scripts. If winget is absent it prints manual install steps and exits instead of running anything unverified. Chocolatey dropped entirely.
- All three installers `pip install`ed with `>=` floors -> silent dependency substitution / typosquat exposure and generated a fully pinned, fully hashed `requirements.txt` (whole transitive tree). Installers now run `pip install --require-hashes -r requirements.txt`; pip refuses any package whose hash doesn't match. Falls back to exact `==` pins if the file is missing.
- `delete_originals` defaulted **True** (a config missing the key would silently delete), and it always operated on the script's own folder and default is now **False** (destructive ops fail safe). Added a pre run summary + `y/N` confirmation (default **No**). New `--path` lets you point it at any folder instead of dumping the script into your media. New `--no-delete` hard-override.
- JAV mode silently deleted `<50MB` files, and a name like `foo@` produced an empty target -> uncaught `os.rename` crash and an sub 50mb drops now print what they delete. The `@`-rename guards empty/`.`/`..` results, checks the destination doesn't already exist, and is wrapped in try/except.
-  ARM installer did `sed -i 's/main/main contrib non-free/g' sources.list` I rewrote **every** line containing "main" (URLs, comments) and could corrupt the file and replaced with an anchored, idempotent edit that only appends to Raspbian `deb` lines lacking `contrib`. Verified it leaves comments / other repos untouched and is safe to run twice.
- OMDB API key written to `config.json` world readable and `config.json` is now `chmod 600` on write.
- `safe_name()` didn't neutralize `.` / `..` / leading dots (titles come from guessit/OMDB = untrusted) and strips leading/trailing dots and rejects `.`/`..` -> fallback name. 
- rmtree guard used `abspath` (symlinks could dodge it) and uses `realpath` for the containment check. 
- Tree was mutated mid `os.walk` (created output dirs got rewalked) and file list is **snapshotted up front** before any processing.
- `finalize()` / empty-folder cleanup existed but was never called and now called at end of `main()`.
- Two same named files in different folders clobbered each other's error log and eror log filename now includes an 8char hash of the full path.
- Best effort RPM Fusion step (`|| true`) could fail silently on the non ARM installer and i added a hard `ffmpeg` presence check after install on both installers.

### ⭐ FAQ:

Why is there two or more versions of monolithic StreamMii in the repo?

> It's your fallback if the current version is unstable for you or does not work.

> To see the changes from version to version.

> And overall a backup of everything that i made.

### Dedicated StreamMii-Monolithic Github Page:

<a href="https://github.com/motan1337/StreamMii-Monolithic">
- I will leave this here because its getting very cluttery and the dedicated page for monolithic is easier for me to controll...
- Better README.md is there, all files you need are there, no unneeded files exist, or diffrent types of streammii (just old monolithic
versions).
