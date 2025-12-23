# 🕵️‍♂️ M3taHunterz

**Advanced OSINT & Anti-Forensics Utility**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Active-green?style=for-the-badge)


## 💀 Overview
M3taHunterz Lite is a GUI-based tool designed for **Open Source Intelligence (OSINT)** analysis and **Privacy Protection (Anti-Forensics)**. Unlike standard command-line tools, it provides a visual interface to extract, map, clean, and spoof metadata from digital imagery.

It features an **Offline-First** architecture, allowing investigators to map GPS coordinates without an active internet connection (after caching).

## ⚡ Features (Lite Version)

### 🔍 Analysis (Blue Team)
* **Deep Metadata Extraction:** View hidden EXIF tags (Software, Hardware, Dates).
* **Live Map & Preview:** Split-screen view showing the target image alongside its GPS location on an interactive map.
* **Smart Dashboard:** Double-click any metadata line to **Quick Edit** (Safe Mode automatically backs up original files).
* **Clipboard Support:** One-click "Copy All" button for easy reporting.

### 🛡️ Counter-Forensics (Red Team)
* **Evidence Scrubbing:** One-click removal of all metadata to sanitize files for safe sharing.
* **Advanced Spoofing:** Inject fake GPS coordinates and modify critical hardware IDs.
* **Tag Injection:** Plant false flags including:
    * `BodySerialNumber` (Fake specific device IDs)
    * `CameraOwnerName` (Impersonate ownership)
    * `LensMake` / `LensModel`

### 🎨 Customization
* **Theming:** Hacker-style dark UI with static logo positioning.
* **Privacy Mode:** Integrated history wiper to delete local map caches (`.db` files).

## 🛠️ Prerequisites & Installation

*Install Libraries*
```
pip install -r requirements.txt
```

### 🪟 Windows
```bash
# 1. Download
git clone https://github.com/FrhnIsml/M3taHunterz-Lite.git
cd M3taHunterz Lite

# 2. Install Requirements
pip install -r requirements.txt

# 3. Run
python m3tahunter.py
```

### 🐧 Linux (Terminal)

*Downloads*
```
git clone https://github.com/FrhnIsml/M3taHunterz-Lite.git
cd M3taHunterz Lite
```

```
sudo apt install python3.12-venv
```

```Bash
sudo apt-get update
sudo apt-get install python3-tk
```

*Create & Activate Virtual Environment:*
```Bash
# 1. Create the safe bubble (.venv)
python3 -m venv .venv

# 2. Enter the bubble
source .venv/bin/activate
#You will see (.venv) appear on the left side of your terminal line.

# 3. Install libraries safely inside
pip install -r requirements.txt

# 4. Run the tools
python m3tahunter.py
```

*If you want to open for next times. Use this commands" (Daily Use)*

Open your terminal and go to the folder:

```Bash
cd M3taHunterz Lite
source .venv/bin/activate
python m3tahunter.py
```


## 🚀 Usage

Run the main script:
```bash
python m3tahunter.py
```

## 🔄 Updating the Tool

If you already have M3taHunterz Lite installed and want to get the latest version:

1. Open your terminal and go to the folder:
   ```bash
   cd M3taHunterz Lite

2. Pull the latest changes from GitHub:
   ```Bash
   git pull

## 📥 Tools
<img width="1247" height="954" alt="image" src="https://github.com/user-attachments/assets/3119e0cb-41cd-490e-ad74-1a03055389d0" />







### *⚠️ Disclaimer*
FOR EDUCATIONAL AND PRIVACY PURPOSES ONLY.

This tool is designed for security research, CTF competitions, and personal privacy protection. The developers assume no liability and are not responsible for any misuse or damage caused by this program. Do not use this tool to frame individuals or obstruct legal investigations.

*🤝 Contributing*
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


### *👤Creator*

Farhan Ismail

Cybersecurity student | Osint Researcher | CTF Player


## 📄 License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.

You are free to use, study, and modify this code for educational purposes. However, if you distribute any modifications, they must also be open-source under the same license.

