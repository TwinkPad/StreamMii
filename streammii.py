import os
import time

from config import script_dir, delete_originals
from logging_utils import (
    get_file_signature,
    read_processed_log,
    write_processed_log,
)
from ffmpeg_utils import process_video, process_audio
from organizer import sports_submenu, organize_media_by_type

ascii_art = r"""
   _____ __                            __  ____ _ 
  / ___// /_________  ____ _____ ___  /  |/  (_|_)
  \__ \/ __/ ___/ _ \/ __ `/ __ `__ \/ /|_/ / / / 
 ___/ / /_/ /  /  __/ /_/ / / / / / / /  / / / /  
/____/\__/_/   \___/\__,_/_/ /_/ /_/_/  /_/_/_/   
                                                  
  
  StreamMii (0.0.4) // STILL IN BETA
  
  CHANGELOG: [+] Added LGBT category for adult content.
             [+] Implemented Intel GPU support.
             [+] Refactored media organizer and automated empty folder/SRT removal.
             [+] Optimized output resolution (640w) and upgraded to Lanczos resampling.
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


def main():
    processed_sigs = read_processed_log()
    
    PURPLE = "\033[95m"
    RESET = "\033[0m"
    
    print(f"{PURPLE}{ascii_art}{RESET}")
    time.sleep(1)

    choice = ""
    while choice not in [str(i) for i in range(1, 8)]:
        print(menu_text)
        choice = input("> ").strip()

    sport = None
    adult_mode = None
    adult_data = None

    if choice == "3":
        sub = input("adult: 1=solo 2=group 3=hentai 4=jav 5=lgbt: ").strip()
        if sub == "1":
            adult_mode = "1"
            adult_data = input("creator: ").strip()
        elif sub == "2":
            adult_mode = "2"
            try:
                n = int(input("how many creators? ").strip())
            except ValueError:
                n = 0
            adult_data = []
            for i in range(n):
                adult_data.append(input(f"name {i + 1}: ").strip())
        elif sub in ["3", "4"]:
            adult_mode = sub
        elif sub == "5":
            lgbt_sub = input("lgbt: 1=solo 2=group: ").strip()
            if lgbt_sub == "1":
                adult_mode = "5_solo"
                adult_data = input("creator: ").strip()
            elif lgbt_sub == "2":
                adult_mode = "5_group"
                try:
                    n = int(input("how many creators? ").strip())
                except ValueError:
                    n = 0
                adult_data = []
                for i in range(n):
                    adult_data.append(input(f"name {i + 1}: ").strip())

    if choice == "7":
        sport = sports_submenu()

    for dp, _, files in os.walk(script_dir):
        # We removed the (wii) check, relying strictly on file signatures now

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