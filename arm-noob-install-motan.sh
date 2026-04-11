#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "[!] Requesting root privileges..."
    exec sudo bash "$0" "$@"
fi

#  detecting your architecture
ARCH=$(uname -m)
echo "[!] Detected architecture: $ARCH"

case "$ARCH" in
    x86_64)          ARCH_LABEL="x86_64 (64-bit PC)" ;;
    aarch64|arm64)   ARCH_LABEL="ARM64 (aarch64)" ;;
    armv7l|armv7)    ARCH_LABEL="ARM 32-bit (armv7)" ;;
    armv6l|armv6)    ARCH_LABEL="ARM 32-bit (armv6 — limited support)" ;;
    *)               ARCH_LABEL="Unknown ($ARCH)" ;;
esac
echo "[!] Architecture label: $ARCH_LABEL"

# warn early for armv6 packages may be missing on some distros
if [[ "$ARCH" == armv6* ]]; then
    echo
    echo "[!] WARNING: armv6 detected. Some packages may not be available"
    echo "    in official repos. Raspbian/Raspberry Pi OS is the most"
    echo "    supported distro for this architecture."
    echo
fi

#  detecting pgk mngDETECT PACKAGE MANAGER
detect_pkg_manager() {
    if   command -v apt-get &>/dev/null; then echo "apt"
    elif command -v dnf     &>/dev/null; then echo "dnf"
    elif command -v yum     &>/dev/null; then echo "yum"
    elif command -v pacman  &>/dev/null; then echo "pacman"
    elif command -v zypper  &>/dev/null; then echo "zypper"
    elif command -v apk     &>/dev/null; then echo "apk"
    else
        echo "[X] No supported package manager found." >&2
        exit 1
    fi
}

PKG_MGR=$(detect_pkg_manager)
echo "[!] Detected package manager: $PKG_MGR"

pkg_update() {
    case "$PKG_MGR" in
        apt)     apt-get update -qq ;;
        dnf|yum) "$PKG_MGR" check-update -q || true ;;
        pacman)  pacman -Sy --noconfirm ;;
        zypper)  zypper refresh ;;
        apk)     apk update ;;
    esac
}

pkg_install() {
    case "$PKG_MGR" in
        apt)     apt-get install -y "$@" ;;
        dnf|yum) "$PKG_MGR" install -y "$@" ;;
        pacman)  pacman -S --noconfirm "$@" ;;
        zypper)  zypper install -y "$@" ;;
        apk)     apk add --no-cache "$@" ;;
    esac
}

#  updating and installing python3
echo
echo "[!] Updating package lists..."
pkg_update

echo "[!] Installing Python 3 + pip + venv..."
case "$PKG_MGR" in
    apt)     pkg_install python3 python3-pip python3-venv ;;
    dnf|yum) pkg_install python3 python3-pip ;;
    pacman)  pkg_install python python-pip ;;
    zypper)  pkg_install python3 python3-pip ;;
    apk)     pkg_install python3 py3-pip ;;
esac

if   command -v python3 &>/dev/null; then PYTHON_EXE=python3
elif command -v python  &>/dev/null; then PYTHON_EXE=python
else
    echo "[X] Python not found after install." >&2
    exit 1
fi
echo "[!] Found Python: $PYTHON_EXE ($($PYTHON_EXE --version 2>&1))"

VENV_DIR="/opt/myapp-venv"
echo
echo "[!] Creating virtual environment at $VENV_DIR..."
$PYTHON_EXE -m venv "$VENV_DIR"

PYTHON_EXE="$VENV_DIR/bin/python"
PIP_EXE="$VENV_DIR/bin/pip"

echo "[!] Upgrading pip inside venv..."
$PIP_EXE install --upgrade pip

echo "[!] Installing Python packages..."
$PIP_EXE install \
    "requests>=2.31.0" \
    "guessit>=3.2.0"   \
    "colorama>=0.4.6"

#  installing your mother sorry ffmpeg 
echo
echo "[!] Installing FFmpeg..."

install_ffmpeg_apt() {
    if [[ "$ARCH" == armv6* ]]; then
        echo "[!] armv6 detected — enabling Raspbian contrib repo..."
        grep -q "contrib" /etc/apt/sources.list 2>/dev/null || \
            sed -i 's/main/main contrib non-free/g' /etc/apt/sources.list || true
        pkg_update
    fi
    pkg_install ffmpeg
}

install_ffmpeg_dnf() {
    if ! rpm -q rpmfusion-free-release &>/dev/null; then
        echo "[!] Enabling RPM Fusion (free) for full FFmpeg..."
        FEDORA_VER=$(rpm -E %fedora)
        case "$ARCH" in
            aarch64)
                RPMFUSION_URL="https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-${FEDORA_VER}.noarch.rpm"
                ;;
            armv7*)
                echo "[!] WARNING: Fedora 32-bit ARM support is very limited."
                RPMFUSION_URL="https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-${FEDORA_VER}.noarch.rpm"
                ;;
            *)
                RPMFUSION_URL="https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-${FEDORA_VER}.noarch.rpm"
                ;;
        esac
        dnf install -y "$RPMFUSION_URL" || true
    fi
    pkg_install ffmpeg
}

case "$PKG_MGR" in
    apt)    install_ffmpeg_apt ;;
    dnf)    install_ffmpeg_dnf ;;
    yum)    pkg_install ffmpeg ;;
    pacman) pkg_install ffmpeg ;;
    zypper) pkg_install ffmpeg ;;
    apk)    pkg_install ffmpeg ;;
esac

# verify ffmpeg actually installed as arm6 is really fucking shit
if ! command -v ffmpeg &>/dev/null; then
    echo
    echo "[X] FFmpeg not found after install."
    if [[ "$ARCH" == armv6* ]]; then
        echo "    armv6 may require building FFmpeg from source."
        echo "    See: https://trac.ffmpeg.org/wiki/CompilationGuide"
    fi
    exit 1
fi

echo
echo "════════════════ VERIFICATION ════════════════"

echo
echo "▸ Architecture : $ARCH_LABEL"

echo
echo "▸ Python (venv):"
$PYTHON_EXE --version

echo
echo "▸ Pip packages:"
for pkg in requests guessit colorama; do
    $PIP_EXE show "$pkg" 2>/dev/null | grep -E "^(Name|Version)" || \
        echo "  [X] $pkg — not found"
done

echo
echo "▸ FFmpeg:"
ffmpeg -version 2>&1 | head -1

echo
echo "════════════════ ALL DONE! ════════════════"
echo
read -rp "Press Enter to exit..."