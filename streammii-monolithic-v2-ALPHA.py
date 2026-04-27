import os
import re
import sys
import json
import time
import shutil
import subprocess

import requests

try:
    from guessit import guessit as guessit_parse
    GUESSIT_AVAILABLE = True
except ImportError:
    GUESSIT_AVAILABLE = False
    guessit_parse = None

# config

script_dir = os.path.dirname(os.path.abspath(__file__))

config_dir = os.path.join(os.path.expanduser("~"), "streammii")
config_file = os.path.join(config_dir, "config.json")
log_dir = os.path.join(config_dir, "logs")
log_file = os.path.join(log_dir, "processed.txt")
error_log_dir = os.path.join(log_dir, "errors")

os.makedirs(config_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)
os.makedirs(error_log_dir, exist_ok=True)


def safe_input(prompt=""):
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\naborted.")
        sys.exit(0)


# When I wrote this code, only God and I knew how it worked. Now, only God knows!
# By the end of trying to fix whatever was broken here, you might have developed several mental illnesses and you are king Terry Davis
def first_launch_setup():
    print("welcome to streammii setup!")
    gpu_choice = ""
    while gpu_choice not in ("1", "2", "3", "4"):
        print("select gpu type or cpu fallback:")
        print("1 -> amd")
        print("2 -> nvidia")
        print("3 -> cpu fallback")
        print("4 -> intel")
        gpu_choice = safe_input("> ").strip()

    delete_choice = ""
    while delete_choice.lower() not in ("y", "n"):
        delete_choice = safe_input("delete originals after re-encode? (y/n): ").strip()
    delete_originals = delete_choice.lower() == "y"

    print("optional: enter omdb api key (or just press enter to skip)")
    omdb_api_key = safe_input("> ").strip()

    cfg = {
        "gpu_choice": gpu_choice,
        "delete_originals": delete_originals,
        "omdb_api_key": omdb_api_key
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)
    return cfg


def load_config():
    if not os.path.exists(config_file):
        return first_launch_setup()
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"config file is unreadable ({e}). running setup again.")
        return first_launch_setup()


config = load_config()

gpu_choice = config.get("gpu_choice", "3")
delete_originals = config.get("delete_originals", True)
omdb_api_key = config.get("omdb_api_key", "").strip()

if gpu_choice == "1":
    hw_encoder, hw_accel = "amd", "d3d11va"
elif gpu_choice == "2":
    hw_encoder, hw_accel = "nvidia", "cuda"
elif gpu_choice == "4":
    hw_encoder, hw_accel = "intel", "qsv"
else:
    hw_encoder, hw_accel = "cpu", None


# utils

def get_file_signature(path):
    base = os.path.basename(path)
    try:
        size_bytes = os.path.getsize(path)
        size_kb = size_bytes // 1024
    except OSError:
        size_kb = -1
    return f"{base}|{size_kb}"


def read_processed_log():
    sigs = set()
    if not os.path.exists(log_file):
        return sigs
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "|" in line:
                name, size_str = line.rsplit("|", 1)
                if name and size_str and size_str.lstrip("-").isdigit():
                    sigs.add(line)
    return sigs


def write_processed_log(path, sig_set=None):
    sig = get_file_signature(path)
    if sig_set is not None and sig in sig_set:
        return
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(sig + "\n")
    if sig_set is not None:
        sig_set.add(sig)


# metadata

def safe_name(name, fallback="unknown"):
    if not isinstance(name, str):
        return fallback
    cleaned = re.sub(r'[<>:"/\\|?*]', "", name).strip()
    return cleaned or fallback


def classify_file_by_name(fn):
    n = os.path.basename(fn).lower()
    if re.search(r's\d{1,2}e\d{1,2}', n):
        return "tv"
    if re.search(r'\d{1,2}x\d{1,2}', n):
        return "tv"
    if re.search(r'(ep|episode)\s?\d{1,3}', n):
        return "tv"
    if re.search(r'(19\d{2}|20[0-2]\d)', n):
        return "movie"
    return "unknown"


def fetch_movie_metadata(title, year=None):
    if not omdb_api_key or not title:
        return None
    try:
        params = {"t": title, "apikey": omdb_api_key}
        if year:
            params["y"] = str(year)
        r = requests.get("https://www.omdbapi.com/", params=params, timeout=6)
        d = r.json()
        if d.get("Response") == "True":
            t = d.get("Title") or title
            y = d.get("Year")
            if y:
                return f"{t} ({y})"
            return t
    except Exception:
        pass
    return None


def guessit_info(filepath):
    if not GUESSIT_AVAILABLE or guessit_parse is None:
        return None
    try:
        return guessit_parse(os.path.basename(filepath))
    except Exception:
        return None


# ffmpeg

TEXT_SUB_CODECS = {
    "subrip", "ass", "ssa", "mov_text", "text", "webvtt",
    "microdvd", "subviewer", "subviewer1", "subviewer2",
    "mpl2", "pjs", "realtext", "sami", "stl", "vplayer"
}


def fmt_time(sec):
    if sec <= 0:
        return "00:00"
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"


def probe_video(infile):
    """Single ffprobe call returning (duration, aspect, subtitle_streams)."""
    duration = 0.0
    aspect = 16 / 9
    subs = []
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries",
            "format=duration:stream=index,codec_name,codec_type,width,height",
            "-of", "json", infile
        ]
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        data = json.loads(res.stdout or "{}")

        try:
            duration = float(data.get("format", {}).get("duration", 0) or 0)
        except (TypeError, ValueError):
            duration = 0.0

        for s in data.get("streams", []):
            ctype = (s.get("codec_type") or "").lower()
            if ctype == "video" and s.get("width") and s.get("height"):
                w, h = int(s["width"]), int(s["height"])
                if h > 0:
                    aspect = round(w / h, 3)
            elif ctype == "subtitle":
                subs.append({
                    "index": s.get("index"),
                    "codec_name": (s.get("codec_name") or "").lower(),
                    "codec_type": ctype,
                })
    except Exception:
        pass
    return duration, aspect, subs


def pick_scaling(aspect):
    """Map source aspect to (vf, aspect_flag, framerate) for Wii-friendly 640x480 output.

    4:3 sources are scaled to a true 4:3 frame, 16:9-ish sources are encoded
    anamorphic (640x480 with 16:9 DAR), and ultra-wide content keeps its
    aspect ratio at 640px wide.
    """
    if aspect < 1.5:
        return "scale=640:480:flags=lanczos", "4:3", 30
    if aspect <= 1.85:
        return "scale=640:480:flags=lanczos", "16:9", 30
    return "scale=640:-2:flags=lanczos", None, 25


def process_video(src_path):
    base_no_ext, _ = os.path.splitext(src_path)
    final_out = base_no_ext + ".mkv"
    tmp_out = base_no_ext + "_tmp.mkv"

    dur, aspect, internal_subs = probe_video(src_path)
    vf, aspect_flag, r = pick_scaling(aspect)

    if hw_encoder == "amd":
        enc_default = "h264_amf"
    elif hw_encoder == "nvidia":
        enc_default = "h264_nvenc"
    elif hw_encoder == "intel":
        enc_default = "h264_qsv"
    else:
        enc_default = "libxvid"

    srt = base_no_ext + ".srt"
    has_external_srt = os.path.exists(srt)

    output_subs_is_text = [
        s.get("codec_name", "") in TEXT_SUB_CODECS for s in internal_subs
    ]
    if has_external_srt:
        output_subs_is_text.append(True)

    def run(enc, acc, output):
        cmd = ["ffmpeg", "-y"]
        if acc:
            cmd += ["-hwaccel", acc]

        cmd += ["-i", src_path]
        if has_external_srt:
            cmd += ["-i", srt]

        cmd += [
            "-map", "0:v:0",
            "-map", "0:a?",
            "-map", "0:s?"
        ]
        if has_external_srt:
            cmd += ["-map", "1:0?"]

        cmd += [
            "-vf", vf,
            "-c:v", enc,
            "-b:v", "1000k",
            "-r", str(r),
            "-c:a", "aac",
            "-b:a", "128k",
        ]
        if enc != "libxvid":
            cmd += ["-pix_fmt", "yuv420p"]
        if aspect_flag and enc == "libxvid":
            cmd += ["-aspect", aspect_flag]

        for idx, is_text in enumerate(output_subs_is_text):
            codec = "srt" if is_text else "copy"
            cmd += [f"-c:s:{idx}", codec]

        cmd.append(output)

        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        start = time.time()
        logs = []

        while True:
            line = p.stderr.readline()
            if not line and p.poll() is not None:
                break
            if line:
                logs.append(line)
                if "time=" in line and dur > 0:
                    m = re.search(r'time=(\d+):(\d+):(\d+)\.(\d+)', line)
                    if m:
                        now = (
                            int(m.group(1)) * 3600
                            + int(m.group(2)) * 60
                            + int(m.group(3))
                            + int(m.group(4)) / 100
                        )
                        pct = min(100.0, (now / dur) * 100) if dur > 0 else 0.0
                        filled = int(pct / 2.5)
                        bar = "█" * filled + "-" * (40 - filled)
                        print(
                            f"Encoding [{bar}] {pct:.1f}% "
                            f"({fmt_time(now)} / {fmt_time(dur)})".ljust(80),
                            end="\r",
                        )

        p.wait()
        print()  # finish the progress line cleanly
        if p.returncode != 0:
            err_path = os.path.join(error_log_dir, os.path.basename(src_path) + ".log")
            try:
                with open(err_path, "w", encoding="utf-8") as f:
                    f.write("".join(logs))
            except Exception:
                pass
            print(f"failed: check {err_path}")
        return p.returncode

    rcode = run(enc_default, hw_accel, tmp_out)

    if rcode != 0 and enc_default != "libxvid":
        rcode = run("libxvid", None, tmp_out)

    if rcode == 0 and os.path.exists(tmp_out):
        try:
            os.replace(tmp_out, final_out)
        except OSError:
            try:
                os.remove(tmp_out)
            except OSError:
                pass
            return None
        return final_out

    if os.path.exists(tmp_out):
        try:
            os.remove(tmp_out)
        except OSError:
            pass
    return None


def process_audio(src_path):
    base_no_ext, _ = os.path.splitext(src_path)
    final_out = base_no_ext + ".mp3"
    tmp_out = base_no_ext + "_tmp.mp3"

    cmd = [
        "ffmpeg", "-y",
        "-i", src_path,
        "-b:a", "192k",
        tmp_out
    ]

    r = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    if r.returncode == 0 and os.path.exists(tmp_out):
        try:
            os.replace(tmp_out, final_out)
        except OSError:
            try:
                os.remove(tmp_out)
            except OSError:
                pass
            return None
        return final_out
    else:
        err = os.path.join(error_log_dir, os.path.basename(src_path) + ".log")
        try:
            with open(err, "w", encoding="utf-8") as f:
                f.write(r.stdout or "")
        except Exception:
            pass
        if os.path.exists(tmp_out):
            try:
                os.remove(tmp_out)
            except OSError:
                pass
        return None

# organizer

sports_categories = {
    "team sports": ["football", "basketball", "volleyball", "rugby", "baseball", "softball", "handball"],
    "combat sports": ["boxing", "mixed martial arts", "wrestling", "karate"],
    "winter sports": ["skiing", "snowboarding", "ice skating", "bobsledding"],
    "water sports": ["surfing", "rowing", "kayaking", "synchronized swimming"],
    "motor sports": ["formula 1", "motogp"],
    "individual sports": ["athletics (track and field)", "tennis", "golf", "pool", "swimming", "badminton", "table tennis", "cycling", "gymnastics"],
    "equestrian": ["show jumping", "dressage"],
    "other": ["cricket", "hockey"],
}

VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"}
SUB_EXTS = {".srt"}
MIN_JAV_SIZE = 50 * 1024 * 1024  # drop trailer/ad files smaller than this / 


def cleanup_single_folder(path):
    if not os.path.isdir(path):
        return
    # Never delete the working root or anything outside of it.
    abs_path = os.path.abspath(path)
    abs_root = os.path.abspath(script_dir)
    if abs_path == abs_root or not abs_path.startswith(abs_root + os.sep):
        return
    try:
        files = [f for f in os.listdir(path) if not f.startswith(".")]
    except OSError:
        return

    if not files:
        try:
            shutil.rmtree(path)
        except OSError:
            pass
        return

    has_vid = any(os.path.splitext(f)[1].lower() in VIDEO_EXTS for f in files)
    has_srt = any(os.path.splitext(f)[1].lower() in SUB_EXTS for f in files)
    # If there are SRTs but NO videos

    if not has_vid and has_srt:
        only_srts = all(os.path.splitext(f)[1].lower() in SUB_EXTS for f in files)
        if only_srts:
            shutil.rmtree(path)
        else:
            for f in files:
                if os.path.splitext(f)[1].lower() in SUB_EXTS:
                    try:
                        os.remove(os.path.join(path, f))
                    except OSError: # maybe try to have proper permissions next time, this is nasty...
                        pass


def cleanup_tree(root):
    for dirpath, _, _ in os.walk(root, topdown=False):
        cleanup_single_folder(dirpath)


def organize_media_by_type(fp, mode, sport_name=None, adult_mode=None, adult_data=None):
    if not os.path.isfile(fp):
        return

    base_name = os.path.basename(fp)
    src_dir = os.path.dirname(fp)

    def move_and_cleanup(dest):
        os.makedirs(dest, exist_ok=True)
        shutil.move(fp, os.path.join(dest, base_name))
        cleanup_single_folder(src_dir)

    if mode == "1":
        g = guessit_info(fp)
        if g and g.get("type") == "episode" and (g.get("series") or g.get("title")):
            series = safe_name(g.get("series") or g.get("title"), "unknown_show")
            season = g.get("season")
            if isinstance(season, int):
                season = f"{season:02d}"
            elif isinstance(season, str) and season.isdigit():
                season = f"{int(season):02d}"
            else:
                season = "01"
            dest = os.path.join(script_dir, "tv shows", series[0].upper(), series, f"season {season}")
            move_and_cleanup(dest)
            return

        elif g and g.get("type") == "movie" and g.get("title"):
            title = safe_name(g["title"], "unknown_movie")
            year = g.get("year")
            movie_dir = f"{title} ({year})" if year else title
            dest = os.path.join(script_dir, "movies", title[0].upper(), movie_dir)
            move_and_cleanup(dest)
            return

        else:
            kind = classify_file_by_name(base_name)
            if kind == "tv":
                s = re.search(r"s(\d{1,2})", base_name, re.I)
                season = s.group(1) if s else "01"
                raw = base_name.split(".")[0]
                show = safe_name(fetch_movie_metadata(raw) or raw, "unknown_show") # This is nasty, even though we have both guessit and OMDB API
                dest = os.path.join(script_dir, "tv shows", show[0].upper(), show, f"season {season}")
            else:
                y = re.search(r"(19\d{2}|20[0-2]\d)", base_name)
                year = y.group(0) if y else None
                guess = re.sub(r"[.\-_]", " ", base_name).strip()
                movie = safe_name(fetch_movie_metadata(guess, year) or guess, "unknown_movie")
                dest = os.path.join(script_dir, "movies", movie[0].upper(), movie)
            move_and_cleanup(dest)

    elif mode == "2":
        # audio mode, this is hacky but I found it works for most cases. There is an edge case where it'll make folders for every song if it starts with "1." or whatever number it might be.
        parent_folder = os.path.basename(src_dir)
        album = safe_name(parent_folder, "unknown_album")
        parts = base_name.rsplit(".", 1)[0].split(" - ")
        artist = safe_name(parts[0] if len(parts) >= 2 else parent_folder, "unknown_artist")
        dest = os.path.join(script_dir, "audio", artist[0].upper(), artist, album)
        move_and_cleanup(dest)

    elif mode == "3" and adult_mode:
        if adult_mode == "1":
            creator = safe_name(adult_data or "unknown_creator")
            dest = os.path.join(script_dir, "adult", "solo", creator[0].upper(), creator)
        elif adult_mode == "2":
            names = [safe_name(n, "unknown") for n in (adult_data or [])]
            dest = os.path.join(script_dir, "adult", "group", " + ".join(names) if names else "unknown_group")
        elif adult_mode == "3":
            dest = os.path.join(script_dir, "adult", "hentai", base_name[0].upper())
        elif adult_mode == "4":
            ext = os.path.splitext(base_name)[1].lower()
            if ext in VIDEO_EXTS:
                if os.path.getsize(fp) < MIN_JAV_SIZE:
                    os.remove(fp)
                    cleanup_single_folder(src_dir)
                    return
                if "@" in base_name:
                    clean_name = base_name.split("@")[-1]
                    new_fp = os.path.join(src_dir, clean_name)
                    os.rename(fp, new_fp)
                    fp = new_fp
                    base_name = clean_name
                    # This might try to move a nonexistent file...
            code = safe_name(os.path.splitext(base_name)[0], "uncategorized")
            dest = os.path.join(script_dir, "adult", "jav", code)
        elif adult_mode == "5_solo":
            # This is confusing and error prone.
            creator = safe_name(adult_data or "unknown_creator")
            dest = os.path.join(script_dir, "adult", "lgbt", "solo", creator[0].upper(), creator)
        elif adult_mode == "5_group":
            names = [safe_name(n, "unknown") for n in (adult_data or [])]
            dest = os.path.join(script_dir, "adult", "lgbt", "group", " + ".join(names) if names else "unknown_group")
        else:
            return
        move_and_cleanup(dest)

    elif mode == "4":
        dest = os.path.join(script_dir, "documentaries", base_name[0].upper())
        move_and_cleanup(dest)

    elif mode in ["5", "6"]:
        # I don't know much about k-dramas, I treat them just like movies and TV shows, except they're korean?? Makes no sense. 
        cats = {"5": "k-drama", "6": "anime"}
        # I believe this is easy work for animes, just treat them as TV shows...
        episodic = re.search(r"(s\d{1,2}e\d{1,2}|\d{1,2}x\d{1,2}|ep\s?\d{1,3}|\b\d{1,3}\b)", base_name, re.I)
        season = "01" if episodic else None
        parent_title = os.path.basename(src_dir)
        title = safe_name(parent_title or base_name, "unknown_series")
        dest = os.path.join(script_dir, cats[mode], title[0].upper(), title)
        if season:
            dest = os.path.join(dest, f"season {season}")
        move_and_cleanup(dest)

    elif mode == "7" and sport_name:
        sport = safe_name(sport_name, "unknown_sport")
        dest = os.path.join(script_dir, "sports", sport)
        move_and_cleanup(dest)


def sports_submenu():
    # there's so many here, I'm sorry if I missed some.
    print("pick a sport category:")
    cats = list(sports_categories.keys())
    for i, cat in enumerate(cats, 1):
        print(f"{i} -> {cat}")
    choice = ""
    while not choice.isdigit() or not (1 <= int(choice) <= len(cats)):
        choice = safe_input("> ").strip()
    cat = cats[int(choice) - 1]
    sports = sports_categories[cat]
    print(f"pick a sport from {cat}:")
    for i, s in enumerate(sports, 1):
        print(f"{i} -> {s}")
    choice = ""
    while not choice.isdigit() or not (1 <= int(choice) <= len(sports)):
        choice = safe_input("> ").strip()
    return sports[int(choice) - 1]


def finalize():
    cleanup_tree(script_dir)


# main

ascii_art = r"""
   _____ __                            __  ____ _ 
  / ___// /_________  ____ _____ ___  /  |/  (_|_)
  \__ \/ __/ ___/ _ \/ __ `/ __ `__ \/ /|_/ / / / 
 ___/ / /_/ /  /  __/ /_/ / / / / / / /  / / / /  
/____/\__/_/   \___/\__,_/_/ /_/ /_/_/  /_/_/_/   
                                                  
  
  StreamMii (0.0.4) // STILL IN BETA // Motanu version - ALPHA
  
  CHANGELOG: [+] Added LGBT category for adult content.
             [+] Implemented Intel GPU support.
             [+] Refactored media organizer and automated empty folder/SRT removal.
             [+] Optimized output resolution (640w) and upgraded to Lanczos resampling.
             [+] Motanu fixes and addons are below:
             [+] Bug fixes.
             [+] Perf-single ffprobe, basically 3x faster probing.
             [+] Smoothness for the H.264 encoders so non standard pixel formats dont ruin Wii and WiiMC playback.
"""

menu_text = """
choose a mode:
1 > movies/tv shows (auto detect)
2 > audio only
3 > adult
4 > documentaries
5 > k-drama
6 > anime
7 > sports
enter a number from 1 to 7: """

video_exts = (".mkv", ".mp4", ".avi", ".mov", ".flv", ".wmv", ".webm")
audio_exts = (".mp3", ".flac", ".wav", ".aac", ".m4a", ".ogg")


def check_dependencies():
    missing = [t for t in ("ffmpeg", "ffprobe") if shutil.which(t) is None]
    if missing:
        print(f"error: required tool(s) not found in PATH: {', '.join(missing)}")
        print("install ffmpeg (https://ffmpeg.org/download.html) and try again.")
        sys.exit(1)


def collect_creators(prompt_label):
    try:
        n = int(safe_input(f"how many {prompt_label}? ").strip())
    except ValueError:
        n = 0
    return [safe_input(f"name {i + 1}: ").strip() for i in range(n)]


def main():
    check_dependencies()
    processed_sigs = read_processed_log()

    PURPLE = "\033[95m"
    RESET = "\033[0m"

    print(f"{PURPLE}{ascii_art}{RESET}")
    time.sleep(1)

    choice = ""
    while choice not in [str(i) for i in range(1, 8)]:
        print(menu_text)
        choice = safe_input("> ").strip()

    sport = None
    adult_mode = None
    adult_data = None

    if choice == "3":
        sub = safe_input("adult: 1=solo 2=group 3=hentai 4=jav 5=lgbt: ").strip()
        if sub == "1":
            adult_mode = "1"
            adult_data = safe_input("creator: ").strip()
        elif sub == "2":
            adult_mode = "2"
            adult_data = collect_creators("creators")
        elif sub in ["3", "4"]:
            adult_mode = sub
        elif sub == "5":
            lgbt_sub = safe_input("lgbt: 1=solo 2=group: ").strip()
            if lgbt_sub == "1":
                adult_mode = "5_solo"
                adult_data = safe_input("creator: ").strip()
            elif lgbt_sub == "2":
                adult_mode = "5_group"
                adult_data = collect_creators("creators")

    if choice == "7":
        sport = sports_submenu()

    for dp, _, files in os.walk(script_dir):
        for f in files:
            src_path = os.path.normpath(os.path.join(dp, f))

            if os.path.abspath(src_path) == os.path.abspath(__file__):
                continue

            sig_now = get_file_signature(src_path)
            if sig_now in processed_sigs:
                continue

            low = f.lower()

            if low.endswith(video_exts) and choice in ["1", "3", "4", "5", "6", "7"]:
                out_path = process_video(src_path)
                if out_path:
                    write_processed_log(src_path, processed_sigs)
                    if os.path.abspath(out_path) != os.path.abspath(src_path):
                        write_processed_log(out_path, processed_sigs)

                    if delete_originals and os.path.abspath(out_path) != os.path.abspath(src_path):
                        try:
                            os.remove(src_path)
                        except OSError:
                            pass
                        base_no_ext, _ = os.path.splitext(src_path)
                        srt = base_no_ext + ".srt"
                        if os.path.exists(srt):
                            try:
                                os.remove(srt)
                            except OSError:
                                pass

                    organize_media_by_type(out_path, choice, sport, adult_mode, adult_data)

            elif low.endswith(audio_exts) and choice == "2":
                out_path = process_audio(src_path)
                if out_path:
                    write_processed_log(src_path, processed_sigs)
                    if os.path.abspath(out_path) != os.path.abspath(src_path):
                        write_processed_log(out_path, processed_sigs)

                    if delete_originals and os.path.abspath(out_path) != os.path.abspath(src_path):
                        try:
                            os.remove(src_path)
                        except OSError:
                            pass

                    organize_media_by_type(out_path, choice)

    print("all done! enjoy.".ljust(80))
    time.sleep(2)


if __name__ == "__main__":
    main()