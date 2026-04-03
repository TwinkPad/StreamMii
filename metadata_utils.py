import os
import re
import requests

from config import omdb_api_key

try:
    from guessit import guessit as guessit_parse
    GUESSIT_AVAILABLE = True
except ImportError:
    GUESSIT_AVAILABLE = False
    guessit_parse = None


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
        r = requests.get("http://www.omdbapi.com/", params=params, timeout=6)
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