# 📂 Smart Desktop Organizer v5.0

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat&logo=windows)

**Smart Desktop Organizer** is an advanced Python-based automation tool with a modern interface that automatically organizes your desktop and downloads folder. It categorizes complex file piles in seconds and saves you time.

---

## 🚀 Features

This project has the following capabilities in version **v5.0**:

* **📂 Multi-Folder Tracking:** Monitors your Downloads, Desktop, or any folder you choose simultaneously.
* **☁️ Cloud Backup:** Automatically backs up files to your Google Drive or OneDrive folder while organizing them.
* **🎨 Modern Interface:** Developed with CustomTkinter, featuring a stylish settings menu with **Dark Mode** support.
* **⚡ Auto-Start:** Starts silently at Windows startup (System Tray integration).
* **📦 Smart Zip Extractor:** Automatically extracts downloaded `.zip` files to the relevant folder.
* **↩️ Undo:** Restores misplaced files with a single click.
* **📊 Statistics:** Reports how many files of each type were processed and the time saved.
* **📜 Live Log:** You can monitor the operations performed in real-time from the interface.

---

## 🛠️ Installation

Clone the project to your computer and install the required libraries.

```bash
# Clone the repository
git clone [https://github.com/KULLANICI_ADINIZ/Smart-Desktop-Organizer.git](https://github.com/KULLANICI_ADINIZ/Smart-Desktop-Organizer.git)

# Enter the project directory
cd Smart-Desktop-Organizer

# Install requirements
pip install -r requirements.txt
▶️ Usage
To launch the application, run the following command in the terminal:

Bash

python main.py
When the application starts, it will reside in the System Tray (icons next to the clock). It runs silently in the background.

Right-Click Menu: Access Settings, Undo, and Exit options here.

Settings: Change rules, add new folders to monitor (.odp, .jpg, etc.), and view statistics.

⚙️ Configuration
The program creates a settings.json file on first launch. You can easily manage the following via the interface:

File Rules: Specify which extension (e.g., .pdf, .odp, .jpg, .mp4) should be moved to which subfolder.

Theme: Choose between Dark / Light mode.

Extra Features: Enable or disable options such as automatic cleanup, date-based foldering, etc.

🏗️ Technologies Used
Python 3: The main programming language.

Watchdog: For live monitoring of file system events.

CustomTkinter: For a modern GUI interface.

Pystray: To run in the background (System Tray).

Plyer: For desktop notifications.

🤝 Contributing
Pull requests are welcome. For major changes, please start a discussion (issue) first. We welcome all contributions!

📄 License

This project is licensed under the MIT License.

Translated with DeepL.com (free version)
