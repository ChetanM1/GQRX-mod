#!/usr/bin/env bash
set -euo pipefail

# Install build/runtime dependencies for Gqrx on Ubuntu/Debian.
# Usage:
#   ./tools/install_build_deps_ubuntu.sh [--with-portaudio] [--build]

WITH_PORTAUDIO=0
DO_BUILD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-portaudio)
      WITH_PORTAUDIO=1
      ;;
    --build)
      DO_BUILD=1
      ;;
    -h|--help)
      sed -n '1,25p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
  shift
done

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This script currently supports apt-based systems (Ubuntu/Debian)." >&2
  exit 1
fi

if [[ $EUID -ne 0 ]]; then
  SUDO=sudo
else
  SUDO=
fi

BASE_PKGS=(
  git
  build-essential
  cmake
  pkg-config
  python3
  python3-pip
)

QT_PKGS=(
  qtbase5-dev
  qtchooser
  qt5-qmake
  qtbase5-dev-tools
  libqt5svg5-dev
)

SDR_PKGS=(
  gnuradio
  gnuradio-dev
  gr-osmosdr
  libvolk-dev
  uhd-host
  libuhd-dev
  python3-uhd
)

PY_BACKEND_PKGS=(
  python3-numpy
  python3-scipy
  python3-matplotlib
)

AUDIO_PKGS=(
  libpulse-dev
  pulseaudio-utils
)

if [[ $WITH_PORTAUDIO -eq 1 ]]; then
  AUDIO_PKGS+=(portaudio19-dev)
fi

ALL_PKGS=("${BASE_PKGS[@]}" "${QT_PKGS[@]}" "${SDR_PKGS[@]}" "${PY_BACKEND_PKGS[@]}" "${AUDIO_PKGS[@]}")

AVAILABLE_PKGS=()
MISSING_PKGS=()
for pkg in "${ALL_PKGS[@]}"; do
  if apt-cache show "$pkg" >/dev/null 2>&1; then
    AVAILABLE_PKGS+=("$pkg")
  else
    MISSING_PKGS+=("$pkg")
  fi
done

echo "Updating apt index..."
$SUDO apt-get update

echo "Installing packages (${#AVAILABLE_PKGS[@]}): ${AVAILABLE_PKGS[*]}"
$SUDO apt-get install -y "${AVAILABLE_PKGS[@]}"

if [[ ${#MISSING_PKGS[@]} -gt 0 ]]; then
  echo "WARNING: Some packages were not found on this distro release:" >&2
  printf '  - %s\n' "${MISSING_PKGS[@]}" >&2
fi

if python3 -c "import sigmf" >/dev/null 2>&1; then
  echo "Python package 'sigmf' already installed."
else
  echo "Installing Python package 'sigmf' via pip..."
  python3 -m pip install --user sigmf
fi

if [[ $DO_BUILD -eq 1 ]]; then
  if [[ ! -f CMakeLists.txt ]]; then
    echo "Run this script from repository root when using --build." >&2
    exit 1
  fi

  echo "Configuring build..."
  cmake -S . -B build

  echo "Building..."
  cmake --build build -j"$(nproc)"

  echo "Build complete. Binary is typically at: ./build/src/gqrx"
fi

echo "Done."
