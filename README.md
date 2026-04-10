<p align="right">
  <a href="https://t.me/streammiii">
    <img src="https://img.shields.io/badge/JOIN%20TELEGRAM-26A6E1?style=for-the-badge&logo=telegram&logoColor=white" alt="Join Telegram">
  </a>
</p>

# StreamMii

A simple tool that converts media into Wii compatible formats for smooth playback.

---

## 🚀 Features

* **GPU Acceleration Support:**
    * **AMD**
    * **NVIDIA** (NVENC)
    * **Intel** (QSV)
    * **CPU fallback** (not recommended due to lower quality & performance)
* **Automatic media metadata handling**
---

## 🛠️ Output Settings

| Parameter | Configuration |
| :--- | :--- |
| **Resolution** | 640x360 or 640x480 depending on aspect ratio |
| **Scaling** | Lanczos resampling |
| **Bitrate** | 1000 kbps |
| **FPS** | **Usually** matches source media |

---

## 📁 Supported Media Types

* Movies
* TV Shows
* <details>
  <summary>Adult Content </summary>

  Solo, Group, JAV

  </details>
* Audio
* Documentaries
* K-Drama
* Anime
* <details>
  <summary>Sports </summary>

  Team Sports > Football, Basketball, Volleyball, Rugby, Baseball, Softball, Handball  
  Combat Sports > Boxing, MMA, Wrestling, Karate  
  Winter Sports > Skiing, Snowboarding, Ice Skating, Bobsledding  
  Water Sports > Surfing, Rowing, Kayaking, Synchronized Swimming  
  Motor Sports > F1, MotoGP  
  Individual Sports > Athletics (Track and Field), Tennis, Golf, Pool, Swimming, Badminton, Table Tennis, Cycling, Gymnastics  
  Equestrian > Show Jumping, Dressage  
  Other > Cricket, Hockey

  </details>

---

## 💻 System Requirements

* `ffmpeg` must be installed and available in your system `PATH`.

### Installing packages

```bash
pip install guessit requests colorama

```
### How to use the noob installer for Linux.
Works on Debian/Ubuntu/Mint, Fedora/RHEL/CentOS, Arch/Manjaro, openSUSE, Alpine.
```
sudo chmod +x noob-install-by-motanu.sh
./noob-install-by-motanu.sh
```
### Windows
```
Just run the executable either from release either from the repository, or if you're feeling freaky you can use the batch file.
```
### MacOS with Apple Silicon Processor
```
You are on your own but I will give you the sources you need.
There are multiple sources of ffmpeg for Apple Silicon, and each have their ups and downs,
it's up to you to use the best one for you.
1. https://github.com/Vargol/ffmpeg-apple-arm64-build?tab=readme-ov-file
2. https://gitlab.com/martinr92/ffmpeg
3. https://osxexperts.net/
Now you will need Python:
https://www.python.org/downloads/release/python-3144/
```

### MacOS with Intel Processor
```
You are on your own but I will give you the sources you need.
ffmpeg: https://evermeet.cx/ffmpeg/ffmpeg-123838-gb462674645.7z
python: https://www.python.org/downloads/release/python-3144/
