import os
from config import log_file


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