import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))

config_dir = os.path.join(os.path.expanduser("~"), "streammii")
config_file = os.path.join(config_dir, "config.json")
log_dir = os.path.join(config_dir, "logs")
log_file = os.path.join(log_dir, "processed.txt")
error_log_dir = os.path.join(log_dir, "errors")

os.makedirs(config_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)
os.makedirs(error_log_dir, exist_ok=True)


def first_launch_setup():
    print("yo welcome to streammii setup!")
    gpu_choice = ""
    while gpu_choice not in ("1", "2", "3", "4"):
        print("select gpu type or cpu fallback:")
        print("1 -> amd")
        print("2 -> nvidia")
        print("3 -> cpu fallback")
        print("4 -> intel")
        gpu_choice = input("> ").strip()

    delete_choice = ""
    while delete_choice.lower() not in ("y", "n"):
        delete_choice = input("delete originals after re-encode? (y/n): ").strip()
    delete_originals = delete_choice.lower() == "y"

    print("optional: enter omdb api key (or just press enter to skip)")
    omdb_api_key = input("> ").strip()

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
        cfg = first_launch_setup()
    else:
        with open(config_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    return cfg


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