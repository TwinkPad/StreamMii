import os
import re
import shutil
# This has a couple destructive edge cases and some really bad choices. I would say the code is a bit brittle.
# title[0].upper() may cause a crash if it returns ""
from config import script_dir
from metadata_utils import (
    safe_name,
    guessit_info,
    classify_file_by_name,
    fetch_movie_metadata,
)
# Just a wee word of warning here...
# When I wrote this code, only God and I knew how it worked. Now, only God knows!
# By the end of trying to fix whatever was broken here, you might have developed
# several mental illnesses.
# If you manage to fix this, you deserve a medal and an extra coffee.
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
# again, really sorry if I missed any, and you are free to report any missing sports as an issue.
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"}
SUB_EXTS = {".srt"}
MIN_JAV_SIZE = 50 * 1024 * 1024 # For example, torrents from OneJAV sometimes have a small MP4 file which is usually just an ad for whatever. I raised this to account for any edge cases in which there could be "collateral victims" as I would say. This deletes all files under 50MB.


def cleanup_single_folder(path):
    if not os.path.isdir(path):
        return
    try:
        files = [f for f in os.listdir(path) if not f.startswith(".")]
    except OSError:
        return

    # If folder is completely empty, delete it
    if not files:
        shutil.rmtree(path)
        return

    has_vid = any(os.path.splitext(f)[1].lower() in VIDEO_EXTS for f in files)
    has_srt = any(os.path.splitext(f)[1].lower() in SUB_EXTS for f in files)

    # If there are SRTs but NO videos
    if not has_vid and has_srt:
        only_srts = all(os.path.splitext(f)[1].lower() in SUB_EXTS for f in files)
        # This is too aggressive, will try to fix in next release.
        if only_srts:
            # ONLY srts exist, delete the entire folder
            shutil.rmtree(path)
        else:
            # Other stuff exists alongside SRTs, just delete the SRTs
            for f in files:
                if os.path.splitext(f)[1].lower() in SUB_EXTS:
                    try:
                        os.remove(os.path.join(path, f))
                    except OSError:
                        # maybe try to have proper permissions next time, this is nasty...
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
                show = safe_name(fetch_movie_metadata(raw) or raw, "unknown_show") #This is nasty, even though we have both guessit and OMDB API
                dest = os.path.join(script_dir, "tv shows", show[0].upper(), show, f"season {season}")
            else:
                y = re.search(r"(19\d{2}|20[0-2]\d)", base_name)
                year = y.group(0) if y else None
                guess = re.sub(r"[.\-_]", " ", base_name).strip()
                # This leaves garbage names if metadata fetch fails, will try to find a less barbaric method.
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
        choice = input("> ").strip()
    cat = cats[int(choice) - 1]
    sports = sports_categories[cat]
    print(f"pick a sport from {cat}:")
    for i, s in enumerate(sports, 1):
        print(f"{i} -> {s}")
    choice = ""
    while not choice.isdigit() or not (1 <= int(choice) <= len(sports)):
        choice = input("> ").strip()
    return sports[int(choice) - 1]

def finalize():
    cleanup_tree(script_dir)
