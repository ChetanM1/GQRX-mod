Gqrx
====

[![CI](https://github.com/gqrx-sdr/gqrx/workflows/CI/badge.svg)](https://github.com/gqrx-sdr/gqrx/actions?query=workflow%3ACI+branch%3Amaster)
[![Build](https://github.com/gqrx-sdr/gqrx/workflows/Build/badge.svg)](https://github.com/gqrx-sdr/gqrx/actions?query=workflow%3ABuild+branch%3Amaster)

Gqrx is an open source software defined radio (SDR) receiver implemented using
[GNU Radio](https://gnuradio.org) and the [Qt GUI toolkit](https://www.qt.io/).
Currently it works on Linux and Mac with hardware supported by gr-osmosdr,
including Funcube Dongle, RTL-SDR, Airspy, HackRF, BladeRF, RFSpace, USRP and
SoapySDR.

Gqrx can operate as an AM/FM/SSB receiver with audio output or as an FFT-only
instrument. There are also various hooks for interacting with external
applications using network sockets.

![Screenshot of the main Gqrx window](resources/screenshots/gqrx-main.png)


Download
--------

Gqrx is distributed as a source code package and binaries for Linux and Mac.
Many Linux distributions provide gqrx in their package repositories.
Alternate Mac support is available through [MacPorts](https://ports.macports.org/port/gqrx/summary) and [Homebrew](https://formulae.brew.sh/cask/gqrx).
Windows support is available through [radioconda](https://github.com/ryanvolz/radioconda#radioconda).

* [Official releases](https://github.com/gqrx-sdr/gqrx/releases)
* [Pre-release builds](https://github.com/gqrx-sdr/gqrx/actions?query=workflow%3ABuild+branch%3Amaster)

Usage
-----

It is strongly recommended to run the `volk_profile` utility before
running gqrx. This will detect and enable processor-specific optimisations and
will in many cases give a significant performance boost.

The first time you start gqrx it will open a device configuration dialog.
Supported devices that are connected to the computer are discovered
automatically and you can select any of them in the drop-down list.

If you don't see your device listed in the drop-down list it could be because:
- The driver has not been included in a binary distribution
- The udev rule has not been properly configured
- Linux kernel driver is blocking access to the device

You can test your device using device specific tools, such as rtl_test,
airspy_rx, hackrf_transfer, qthid, etc.

Gqrx supports multiple configurations and sessions if you have several devices
or if you want to use the same device under different configurations. You can
load a configuration from the GUI or using the `-c` command line argument. See
`gqrx --help` for a complete list of command line arguments.

Tutorials and howtos are being written and published on the website
https://gqrx.dk/


Python backend + Fit Signal quick guide
--------------------------------------

This repository includes optional GUI extensions for:

- **Run Capture** (live external Python capture)
- **Process Recorded Data** (offline external Python plotting)
- **USRP/LNB Flow** (single launcher for live capture, offline processing, or `demo.py`)
- **Fit Signal** (auto-zoom around strongest FFT signal)

### Where to access in the GUI

- **Run Capture**:
  - `Tools -> Run Capture`
  - Toolbar button (play icon) near I/O controls
  - Shortcut: `Ctrl+Shift+R`
- **Process SigMF/Raw Data**:
  - `Tools -> Process SigMF/Raw Data`
  - Toolbar button (open icon)
  - Shortcut: `Ctrl+Shift+O`
- **USRP/LNB Flow**:
  - `Tools -> USRP/LNB Flow`
  - Toolbar button (clock icon)
  - Shortcut: `Ctrl+Shift+U`
  - Opens chooser for:
    - `Run Live Capture`
    - `Process SigMF/Raw`
    - `Open demo.py GUI`
- **Fit Signal**:
  - Open the FFT settings dock (`FFT Set...`)
  - Click the **Fit Signal** button

### Live capture flow (GUI -> capture.py -> optional plotting.py)

```mermaid
flowchart LR
    A[Run Capture action] --> B[Read current SDR params from Gqrx]
    B --> C[Launch capture.py via QProcess]
    C --> D{Capture success?}
    D -- Yes --> E[Prompt to run plotting.py]
    E --> F[Launch plotting.py]
    F --> G[Detect output path]
    G --> H[Show image preview or open output]
    D -- No --> I[Show error/log message]
```

### Offline flow (recorded SigMF/raw IQ -> plotting.py)

```mermaid
flowchart LR
    A[Process Recorded Data action] --> B[File picker]
    B --> C[Optional directory picker fallback]
    C --> D[Launch plotting.py with selected input]
    D --> E[Detect generated output path]
    E --> F[Show image preview or open output]
```

### Fit Signal flow (existing FFT/waterfall untouched)

```mermaid
flowchart LR
    A[Fit Signal button] --> B[Analyze current FFT in dB]
    B --> C[Estimate noise floor + peak bounds]
    C --> D[Adjust FFT center/span]
    D --> E[Emit new zoom level]
```

### Demo data and helper tools

- Generate synthetic IQ demo file:
  - `python3 tools/generate_fit_demo_iq.py ./fit_demo.cfile --sample-rate 1000000 --seconds 12`
- Install common Ubuntu build/runtime deps:
  - `./tools/install_build_deps_ubuntu.sh`
  - `./tools/install_build_deps_ubuntu.sh --build`
- Install Python backend deps only (works on non-Ubuntu too):
  - `./tools/install_python_backend_deps.sh`

> Notes:
> - These additions do **not** replace the native Gqrx FFT/waterfall renderer.
> - They extend the GUI and invoke external scripts through `QProcess`.
> - Offline processing supports direct selection of `.sigmf-meta` / `.sigmf-data` as well as raw IQ files.
> - If Python backend actions fail with `No module named ...`, run `./tools/install_python_backend_deps.sh`.


Known problems
--------------

See the bug tracker on Github: https://github.com/gqrx-sdr/gqrx/issues


Getting help and reporting bugs
-------------------------------

There is a Google group for discussing anything related to Gqrx:
https://groups.google.com/g/gqrx
This includes getting help with installation and troubleshooting. Please
remember to provide detailed description of your problem, your setup, what
steps you followed, etc.

Please stick around and help others with their problems. Otherwise, if only
developers provide user support there will be no more time for further
development.


Installation from source
------------------------

The source code is hosted on Github: https://github.com/gqrx-sdr/gqrx

To compile gqrx from source you need the following dependencies:
- GNU Radio 3.8, 3.9, or 3.10 with the following components:
    - gnuradio-runtime
    - gnuradio-analog
    - gnuradio-audio
    - gnuradio-blocks
    - gnuradio-digital
    - gnuradio-fft
    - gnuradio-filter
    - gnuradio-network (GNU Radio 3.10 only)
    - gnuradio-pmt
- The gr-iqbalance library (optional)
- Drivers for the hardware you want to have support for:
    - UHD driver via gr-uhd
    - FUNcube Dongle and FUNcube Dongle Pro+ driver from https://github.com/dl1ksv/gr-funcube
    - RTL-SDR driver from https://gitea.osmocom.org/sdr/rtl-sdr
    - HackRF driver from https://github.com/mossmann/hackrf
    - Airspy driver from https://github.com/airspy/airspyone_host
    - SoapySDR from https://github.com/pothosware/SoapySDR
    - RFSpace driver is built in
- gnuradio-osmosdr from https://gitea.osmocom.org/sdr/gr-osmosdr
- pulseaudio or portaudio (Linux-only and optional)
- Qt 5 or Qt 6 with the following components:
    - Core
    - GUI
    - Network
    - Widgets
    - Svg (runtime-only)
- cmake version >= 3.5.0

Gqrx can be compiled from within Qt Creator or in a terminal:

For command line builds:
<pre>
$ git clone https://github.com/gqrx-sdr/gqrx.git gqrx.git
$ cd gqrx.git
$ ./tools/install_build_deps_ubuntu.sh
$ mkdir build
$ cd build
$ cmake ..
$ make
</pre>
If CMake reports `Qt5Config.cmake`/`qt5-config.cmake` missing, install Qt dev packages first (Ubuntu/Debian):
<pre>
$ ./tools/install_build_deps_ubuntu.sh
</pre>
On some systems, the default cmake release builds are "over-optimized" and
perform poorly. In that case try forcing -O2 using
<pre>
export CXXFLAGS=-O2
</pre>
before the cmake step.

For Qt Creator builds:
<pre>
$ git clone https://github.com/gqrx-sdr/gqrx.git gqrx.git
$ cd gqrx.git
$ mkdir build
Start Qt Creator
Open gqrx.git/CMakeLists.txt file
At the dialog asking for build location, select gqrx.git/build
click continue
If asked to choose cmake executable, do so
click continue
click the run cmake button
click done
optionally, on the Projects page, under Build Steps/Make/Additional arguments,
	enter -j4 (replacing 4 with the number of cores in your CPU).
Use Qt Creator as before
</pre>


Debugging
---------

Debug logging can be enabled by setting the `QT_LOGGING_RULES` environment
variable:

```
QT_LOGGING_RULES="*.debug=true;plotter.debug=false;qt.*.debug=false" gqrx
```

To turn on plotter debugging as well, use the following command:

```
QT_LOGGING_RULES="*.debug=true;qt.*.debug=false" gqrx
```


Credits and License
-------------------

Gqrx is designed and written by Alexandru Csete OZ9AEC, and it is licensed
under the GNU General Public License.

Some of the source files were adapted from Cutesdr by Moe Weatley and these
come with a Simplified BSD license.

The following people and organisations have contributed to gqrx:

* Alex Grinkov
* Alexander Fasching
* Andrea Merello
* Andrea Montefusco, IW0HDV
* Andy Sloane
* Anthony Willard
* Anton Blanchard
* AsciiWolf
* Bastian Bloessl
* Ben Reese
* Bob McGwier, N4HY
* Brandonn Etheve
* charlylima
* Chris Kuethe
* Christian Lindner, DL2VCL
* Clayton Smith, VE3IRR
* Dallas Epperson
* Daniil Cherednik
* Darin Franklin
* Davide Gerhard
* Dominic Chen
* Doron Behar
* Doug Hammond
* Edouard Lafargue
* Elias Önal
* Federico Fuga
* Frank Brickle, AB2KT
* Frank Werner-Krippendorf, HB9FXQ
* Ganael Laplanche
* Gisle Vanem
* Göran Weinholt, SA6CJK
* Grigory Shipunov
* Gwenhael Goavec-Merou
* Herman Semenov
* James Yuzawa
* Jaroslav Škarvada
* Jeff Long
* Jiawei Chen
* Jiří Pinkava
* Joachim Schueth, DL2KCD
* Jon Bergli Heier
* Josh Blum
* Kate Adams
* Kenji Rikitake, JJ1BDX
* Kitware Inc.
* Konrad Beckmann
* Luna Gräfje
* luzpaz
* Marco Savelli
* Markus Kolb
* Michael Dickens
* Michael Lass
* Michael Tatarinov
* Moe Weatley
* Nadeem Hasan
* Nate Temple
* Nick Robinson, KE5YWP
* Nokia
* Oliver Grossmann, DH2WQ
* Pavel Milanes, CO7WT
* Pavel Stano
* Phil Vachon
* Radoslav Gerganov
* Rob Frohne
* Ron Economos, W6RZ
* Ruslan Migirov
* Russell Dwarshuis, KB8U
* Ryan Volz
* Shuyuan Liu
* Stefano Leucci
* Sultan Qasim Khan
* Sylvain Munaut
* Tarmo Tanilsoo
* Tomasz Lemiech
* Timothy Reaves
* Valentin Ochs
* Vesa Solonen
* Vincent Pelletier
* Vladisslav P
* Will Scales
* Wolfgang Fritz, DK7OB
* Youssef Touil
* Zero_Chaos

Some of the icons are from:
- The GNOME icon theme CC-SA 3.0 by GNOME icon artists
- Tango icon theme, Public Domain by The people from the Tango! project
- Mint-X icon theme, GPL by Clement Lefebvre

Also thanks to Volker Schroer and Alexey Bazhin for bringing Funcube Dongle
Pro+ support to GNU Radio and Gqrx.

Let me know if somebody is missing from the list.

Alex OZ9AEC
