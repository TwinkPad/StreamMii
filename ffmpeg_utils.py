import os
import subprocess
import json
import time
import re

from config import error_log_dir, hw_accel, hw_encoder

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


def get_video_duration(infile):
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json", infile
        ]
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        data = json.loads(res.stdout or "{}")
        return float(data.get("format", {}).get("duration", 0))
    except Exception:
        return 0.0


def get_video_aspect_ratio(infile):
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json", infile
        ]
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        data = json.loads(res.stdout or "{}")
        w = int(data["streams"][0]["width"])
        h = int(data["streams"][0]["height"])
        if h == 0:
            return 16 / 9
        return round(w / h, 3)
    except Exception:
        return 16 / 9


def get_subtitle_streams(infile):
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "s",
            "-show_entries", "stream=index,codec_name,codec_type",
            "-of", "json", infile
        ]
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        data = json.loads(res.stdout or "{}")
        streams = data.get("streams", [])
        out = []
        for s in streams:
            out.append({
                "index": s.get("index"),
                "codec_name": (s.get("codec_name") or "").lower(),
                "codec_type": (s.get("codec_type") or "").lower()
            })
        return out
    except Exception:
        return []


def process_video(src_path):
    base_no_ext, _ = os.path.splitext(src_path)
    final_out = base_no_ext + ".mkv"
    tmp_out = base_no_ext + "_tmp.mkv"

    dur = get_video_duration(src_path)
    aspect = get_video_aspect_ratio(src_path)

    # Standardized to 640 width with Lanczos
    if 1.3 < aspect < 1.8:
        if aspect > 1.4:
            vf = "scale=640:-2:flags=lanczos"
            aspect_flag = None
        else:
            vf = "scale=640:480:flags=lanczos"
            aspect_flag = "16:9"
        r = 25
    else:
        if aspect < 1.4:
            vf = "scale=640:-2:flags=lanczos"
            aspect_flag = None
        else:
            vf = "scale=640:480:flags=lanczos"
            aspect_flag = "4:3"
        r = 25
        
    if vf.endswith("480:flags=lanczos"):
        r = 30

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

    internal_subs = get_subtitle_streams(src_path)
    output_subs_is_text = []

    for s in internal_subs:
        codec = s.get("codec_name", "").lower()
        is_text = codec in TEXT_SUB_CODECS
        output_subs_is_text.append(is_text)

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
                        # ljust(80) ensures leftover text from previous lines is overwritten
                        print(
                            f"Encoding [{bar}] {pct:.1f}% "
                            f"({fmt_time(now)} / {fmt_time(dur)})".ljust(80),
                            end="\r",
                        )

        p.wait()
        if p.returncode != 0:
            err_path = os.path.join(error_log_dir, os.path.basename(src_path) + ".log")
            try:
                with open(err_path, "w", encoding="utf-8") as f:
                    f.write("".join(logs))
            except Exception:
                pass
            print(f"\nfailed: check {err_path}".ljust(80))
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