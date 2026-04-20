<p align="center">
  <a href="https://t.me/streammiii">
    <img src="https://img.shields.io/badge/JOIN%20TELEGRAM-26A6E1?style=for-the-badge&logo=telegram&logoColor=white" alt="Join Telegram">
  </a>
</p>

---

# StreamMii

**A simple tool that converts media into Wii compatible formats for smooth playback.**

---

## 🚀 Features:

* **GPU Acceleration Support:**
    * **AMD.**
    * **NVIDIA** (NVENC).
    * **Intel** (QSV).
    * **CPU fallback** (not recommended due to lower quality & performance).
* **Automatic media metadata handling.**
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
Just run the executable either from release either from the repository.
Or if you are feeling freaky you can use the batch file.

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
### StreamMii-Monolithic
```
The same StreamMii but now it is monolithic. What does that mean? Instead of downloading 6 files you download 1 file, which is easier to manage. INSTALLER IS NOT INCLUDED IN IT!
To get it started now you need to download the monolithic StreamMii and your respective OS n00b installer, run the installler and then StreamMii-Monolithic.
```
