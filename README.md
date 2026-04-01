# Windows Anti-Spyware & Update Manager 🛡️⚙️

![Platform: Windows 10 & 11](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue?style=flat-square)
![Language: Python 3](https://img.shields.io/badge/Language-Python%203-green?style=flat-square)
![Author](https://img.shields.io/badge/Author-Maximum%20Radikali-orange?style=flat-square)

An ultimate, aggressive Command Line Interface (CLI) tool designed to permanently disable (or fully restore) Windows Update and Windows Defender (Anti-Spyware) services.

If you are tired of Windows automatically restarting for updates or Defender deleting your files without permission, this tool is for you!

## ✨ Features

- **Force Disable Windows Update**: Fully stops and deletes update services, disables scheduled tasks, blocks update servers via the `hosts` file, and applies Group Policies to prevent any auto-updates.
- **Force Disable Windows Defender**: Shuts down `WinDefend`, `WdNisSvc`, and `Sense`. Applies registry rules to permanently turn off Anti-Spyware and Real-Time monitoring.
- **Defeats Windows Self-Healing**: Modifies `ImagePath` and service failure actions so Windows cannot automatically restart these services.
- **One-Click Restore**: Changed your mind? Use the "Enable ALL Revert Backup" option to restore everything back to normal.
- **Beginner Friendly**: Simple, color-coded interactive menu.

---

## 🚀 How to Use

### Prerequisites
Make sure you have [Python 3](https://www.python.org/downloads/) installed on your Windows machine. 

### Running the Tool
1. Download or clone this repository to your computer.
2. Right-click on **`set.bat`** and select **Run as Administrator** (or run `windows_update_manager.py` via an elevated CMD/PowerShell).
3. The script will automatically ask for Administrator rights if you forgot.
4. From the main menu, type your choice:
   - `[1]` to **Disable ALL** (Windows Update + Defender)
   - `[2]` to **Enable ALL Revert Backup** (Restore everything)
   - `[3]` to **Exit**

*Note: Changes made to Windows Defender might require a system restart to fully take effect.*

---

## ⚠️ Warning / Disclaimer

**Use at your own risk!**
Disabling Windows Update and Windows Defender will leave your computer highly vulnerable to malware, viruses, and emerging security threats. This tool is intended for advanced users, test environments, or offline machines. 

The author (**Maximum Radikali**) is not responsible for any damage, data loss, or issues that occur from using this script. 

---

## 👤 Author
Developed by **Maximum Radikali**.
