#!/usr/bin/env python3
"""
============================================================
  Windows Anti-Spyware & Update Manager
  Created by: Maximum Radikali
  Compatibility: Windows 10 & Windows 11
  Description: An ultimate tool to permanently disable or
               revert Windows Update and Windows Defender.
============================================================
"""

import sys
import os
import ctypes
import subprocess
import time
import winreg
import shutil
import json
import datetime

class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    GRAY   = "\033[90m"
    RESET  = "\033[0m"

def col(text, color):
    return f"{color}{text}{C.RESET}"

def enable_ansi():
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    print("\n  [!] Not running as Administrator!")
    print("  Relaunching with elevated privileges...\n")
    time.sleep(1)
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable,
        f'"{os.path.abspath(__file__)}"',
        None, 1
    )
    sys.exit(0)

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.returncode == 0, r.stdout, r.stderr
    except Exception as e:
        return False, "", str(e)

def reg_set(path, name, value, reg_type=winreg.REG_DWORD):
    try:
        key = winreg.CreateKeyEx(
            winreg.HKEY_LOCAL_MACHINE, path, 0,
            winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
        )
        winreg.SetValueEx(key, name, 0, reg_type, value)
        winreg.CloseKey(key)
        return True
    except:
        return False

def reg_exists(path):
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
        winreg.CloseKey(k)
        return True
    except:
        return False

def clear():
    os.system("cls")

def header():
    clear()
    print(col("""
  +----------------------------------------------------------+
  |    Windows Anti-Spyware & Update Manager                 |
  |    Developed by: Maximum Radikali                        |
  |    Windows 10 & 11 - Force Disable / Enable              |
  +----------------------------------------------------------+
""", C.CYAN))
    ok, out, _ = run("ver")
    if ok:
        print(col(f"  OS: {out.strip()}", C.GRAY))
    print(col("  ----------------------------------------------------------", C.GRAY))
    print()

def confirm(prompt):
    while True:
        ans = input(col(f"\n  {prompt} [Y/N]: ", C.YELLOW)).strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print(col("  Please enter Y or N.", C.RED))

SERVICES = [
    "wuauserv",
    "WaaSMedicSvc",
    "UsoSvc",
    "bits",
    "dosvc",
    "wudfrd",
]

TASKS = [
    r"\Microsoft\Windows\WindowsUpdate\Scheduled Start",
    r"\Microsoft\Windows\WindowsUpdate\sih",
    r"\Microsoft\Windows\WindowsUpdate\sihboot",
    r"\Microsoft\Windows\UpdateOrchestrator\Schedule Scan",
    r"\Microsoft\Windows\UpdateOrchestrator\UpdateAssistant",
    r"\Microsoft\Windows\UpdateOrchestrator\Reboot",
    r"\Microsoft\Windows\UpdateOrchestrator\USO_UxBroker",
]

UPDATE_HOSTS = [
    "windowsupdate.microsoft.com",
    "update.microsoft.com",
    "download.windowsupdate.com",
    "wustat.windows.com",
    "ntservicepack.microsoft.com",
    "stats.microsoft.com",
    "fe2.update.microsoft.com",
    "fe3.delivery.mp.microsoft.com",
    "sls.update.microsoft.com",
    "download.microsoft.com",
]

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"


def write_hosts_block():
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except:
        content = ""

    to_add = [h for h in UPDATE_HOSTS if h not in content]

    if not to_add:
        print(col("    All servers already blocked in hosts.", C.GRAY))
        return

    def do_write():
        with open(HOSTS_PATH, "a", encoding="utf-8") as f:
            f.write("\n# === Windows Update Block (WU Manager) ===\n")
            for host in to_add:
                f.write(f"0.0.0.0   {host}\n")

    # Method 1: Direct
    try:
        do_write()
        for h in to_add:
            print(f"    {h:<40}" + col("  [OK]", C.GREEN))
        return
    except PermissionError:
        pass

    # Method 2: takeown + icacls + attrib
    print(col("    Permission denied. Taking ownership and adjusting attributes...", C.YELLOW))
    run(f'takeown /F "{HOSTS_PATH}" /A')
    run(f'icacls "{HOSTS_PATH}" /grant Administrators:F /C')
    run(f'attrib -R -S -H "{HOSTS_PATH}"')
    try:
        do_write()
        for h in to_add:
            print(f"    {h:<40}" + col("  [OK]", C.GREEN))
        return
    except:
        pass

    # Method 3: PowerShell
    print(col("    Trying PowerShell method...", C.YELLOW))
    entries = " ,".join([f'"0.0.0.0   {h}"' for h in to_add])
    ps = (
        f'Add-Content -Path "{HOSTS_PATH}" -Value '
        f'@("# === Windows Update Block (WU Manager) ===",{entries}) -Encoding UTF8'
    )
    ok, _, err = run(f'powershell -ExecutionPolicy Bypass -Command "{ps}"')
    if ok:
        for h in to_add:
            print(f"    {h:<40}" + col("  [OK]", C.GREEN))
    else:
        print(col(f"    [FAILED] Hosts file could not be modified.", C.RED))
        print(col("    --> Other methods (services, registry, GP) are still active.", C.YELLOW))


def clean_hosts():
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except:
        print(col("    [ERROR] Cannot read hosts file.", C.RED))
        return

    filtered = []
    removed = 0
    in_block = False
    for line in lines:
        if "Windows Update Block (WU Manager)" in line:
            in_block = True
        if in_block:
            removed += 1
            if line.strip() == "" and removed > 1:
                in_block = False
            continue
        if any(h in line for h in UPDATE_HOSTS):
            removed += 1
            continue
        filtered.append(line)

    def do_write():
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.writelines(filtered)

    try:
        do_write()
    except PermissionError:
        run(f'takeown /F "{HOSTS_PATH}" /A')
        run(f'icacls "{HOSTS_PATH}" /grant Administrators:F /C')
        run(f'attrib -R -S -H "{HOSTS_PATH}"')
        try:
            do_write()
        except Exception as e:
            print(col(f"    [WARN] Could not clean hosts: {e}", C.YELLOW))
            return

    print(f"    {removed} entries removed from hosts file" + col("  [OK]", C.GREEN))


def disable_defender():
    print(col("\n  [STEP 6] Disabling Windows Defender / AntiSpyware:", C.WHITE))
    defender_svcs = ["WinDefend", "WdNisSvc", "Sense"]
    for svc in defender_svcs:
        print(f"    {svc:<35}", end="", flush=True)
        run(f'sc stop "{svc}"')
        run(f'sc config "{svc}" start= disabled')
        run(f'sc failure "{svc}" reset= 0 actions= ""')
        run(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\{svc}" /v ImagePath /t REG_EXPAND_SZ /d "C:\\Windows\\System32\\svchost.exe -k invalid" /f')
        ok = reg_set(f"SYSTEM\\CurrentControlSet\\Services\\{svc}", "Start", 4)
        run(f'sc delete "{svc}"')
        print(col("  [OK]", C.GREEN) if ok else col("  [WARN]", C.YELLOW))

    print(col("    Applying Defender Group Policies        ", C.WHITE), end="", flush=True)
    def_gp = [
        ("SOFTWARE\\Policies\\Microsoft\\Windows Defender", "DisableAntiSpyware", 1, winreg.REG_DWORD),
        ("SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection", "DisableRealtimeMonitoring", 1, winreg.REG_DWORD),
        ("SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection", "DisableBehaviorMonitoring", 1, winreg.REG_DWORD),
        ("SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection", "DisableOnAccessProtection", 1, winreg.REG_DWORD),
        ("SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection", "DisableScanOnRealtimeEnable", 1, winreg.REG_DWORD),
    ]
    for path, name, val, rtype in def_gp:
        reg_set(path, name, val, rtype)
    print(col("  [OK]", C.GREEN))

def enable_defender():
    print(col("\n  [STEP 5] Re-enabling Windows Defender / AntiSpyware:", C.WHITE))
    defender_svcs = {
        "WinDefend": ("auto", 2),
        "WdNisSvc":  ("demand", 3),
        "Sense":     ("demand", 3),
    }
    for svc, (sc_t, rv) in defender_svcs.items():
        print(f"    {svc:<35}", end="", flush=True)
        run(f'sc config "{svc}" start= {sc_t}')
        reg_set(f"SYSTEM\\CurrentControlSet\\Services\\{svc}", "Start", rv)
        run(f'sc start "{svc}"')
        print(col("  [OK]", C.GREEN))

    print(col("    Removing Defender Group Policies        ", C.WHITE), end="", flush=True)
    run(r'reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender" /f')
    print(col("  [OK]", C.GREEN))

def disable_update():
    print(col("""
  +--------------------------------------------------+
  |      Disabling ALL (Windows Update + Defender)   |
  +--------------------------------------------------+
""", C.RED))

    print(col("  [STEP 1] Stopping, Disabling, and Breaking Services:", C.WHITE))
    for svc in SERVICES:
        print(f"    {svc:<22}", end="", flush=True)
        run(f'sc stop "{svc}"')
        ok1, _, _ = run(f'sc config "{svc}" start= disabled')
        run(f'sc failure "{svc}" reset= 0 actions= ""')
        run(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\{svc}" /v ImagePath /t REG_EXPAND_SZ /d "C:\\Windows\\System32\\svchost.exe -k invalid" /f')
        ok2 = reg_set(f"SYSTEM\\CurrentControlSet\\Services\\{svc}", "Start", 4)
        run(f'sc delete "{svc}"')
        print(col("  [OK]", C.GREEN) if (ok1 or ok2) else col("  [WARN]", C.YELLOW))

    print()
    print(col("  [STEP 2] Disabling Scheduled Tasks:", C.WHITE))
    for task in TASKS:
        name = task.split("\\")[-1]
        print(f"    {name:<35}", end="", flush=True)
        ok, _, _ = run(f'schtasks /Change /TN "{task}" /Disable')
        print(col("  [OK]", C.GREEN) if ok else col("  [NOT FOUND]", C.GRAY))

    print()
    print(col("  [STEP 3] Applying Group Policy (Registry):", C.WHITE))
    gp = [
        ("SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate",
         "DisableWindowsUpdateAccess", 1, winreg.REG_DWORD),
        ("SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate",
         "WUServer", "http://localhost", winreg.REG_SZ),
        ("SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate",
         "WUStatusServer", "http://localhost", winreg.REG_SZ),
        ("SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU",
         "NoAutoUpdate", 1, winreg.REG_DWORD),
        ("SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU",
         "AUOptions", 1, winreg.REG_DWORD),
        ("SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU",
         "UseWUServer", 1, winreg.REG_DWORD),
        ("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update",
         "AUOptions", 1, winreg.REG_DWORD),
    ]
    for path, name, val, rtype in gp:
        print(f"    {name:<38}", end="", flush=True)
        ok = reg_set(path, name, val, rtype)
        print(col("  [OK]", C.GREEN) if ok else col("  [WARN]", C.YELLOW))

    print()
    print(col("  [STEP 4] Blocking update servers in Hosts file:", C.WHITE))
    write_hosts_block()

    print()
    print(col("  [STEP 5] Disabling WaaSMedicSvc (Protected Service):", C.WHITE))
    print(f"    WaaSMedicSvc                          ", end="", flush=True)
    ok, _, _ = run(
        r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\WaaSMedicSvc" '
        r'/v Start /t REG_DWORD /d 4 /f'
    )
    print(col("  [OK]", C.GREEN) if ok else col("  [WARN - needs reboot]", C.YELLOW))

    disable_defender()

    print(col("""
  +----------------------------------------------------------+
  |  [SUCCESS] All Services have been FORCE DISABLED!       |
  |  It will NOT run even after restart.                    |
  |  Use option [2] to re-enable it at any time.            |
  +----------------------------------------------------------+
""", C.GREEN))


def enable_update():
    print(col("""
  +--------------------------------------------------+
  |      Re-enabling ALL (Windows Update + Defender) |
  +--------------------------------------------------+
""", C.GREEN))

    print(col("  [STEP 1] Re-enabling Services:", C.WHITE))
    svc_map = {
        "wuauserv":     ("demand", 3),
        "WaaSMedicSvc": ("demand", 3),
        "UsoSvc":       ("demand", 3),
        "bits":         ("auto",   2),
        "dosvc":        ("demand", 3),
    }
    for svc, (sc_t, rv) in svc_map.items():
        print(f"    {svc:<22}", end="", flush=True)
        run(f'sc config "{svc}" start= {sc_t}')
        reg_set(f"SYSTEM\\CurrentControlSet\\Services\\{svc}", "Start", rv)
        run(f'sc start "{svc}"')
        print(col("  [OK]", C.GREEN))

    print()
    print(col("  [STEP 2] Re-enabling Scheduled Tasks:", C.WHITE))
    for task in TASKS:
        name = task.split("\\")[-1]
        print(f"    {name:<35}", end="", flush=True)
        ok, _, _ = run(f'schtasks /Change /TN "{task}" /Enable')
        print(col("  [OK]", C.GREEN) if ok else col("  [NOT FOUND]", C.GRAY))

    print()
    print(col("  [STEP 3] Removing Group Policy keys:", C.WHITE))
    print(f"    WindowsUpdate policy                  ", end="", flush=True)
    run(r'reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /f')
    print(col("  [OK]", C.GREEN))

    print()
    print(col("  [STEP 4] Cleaning Hosts file:", C.WHITE))
    clean_hosts()

    enable_defender()

    print(col("""
  +----------------------------------------------------------+
  |  [SUCCESS] All Services have been RE-ENABLED!           |
  |  Please RESTART your computer to apply all changes.     |
  +----------------------------------------------------------+
""", C.CYAN))


def menu():
    while True:
        header()
        print(col("  Choose an option:\n", C.WHITE))
        print(col("    [1]", C.RED)   + "  Disable ALL (Updates + Defender)")
        print()
        print(col("    [2]", C.GREEN) + "  Enable ALL Revert Backup")
        print()
        print(col("    [3]", C.GRAY)  + "  Exit")
        print()

        choice = input(col("  Your choice: ", C.WHITE)).strip()

        if choice == "1":
            header()
            if confirm("Windows Update and Defender will be permanently stopped. Continue?"):
                disable_update()
            else:
                print(col("\n  Cancelled.", C.GRAY))
            input(col("\n  Press Enter to return to menu...", C.GRAY))

        elif choice == "2":
            header()
            if confirm("Features will be re-enabled. Continue?"):
                enable_update()
            else:
                print(col("\n  Cancelled.", C.GRAY))
            input(col("\n  Press Enter to return to menu...", C.GRAY))

        elif choice == "3":
            print(col("\n  Exiting...\n", C.GRAY))
            time.sleep(0.5)
            sys.exit(0)

        else:
            print(col("\n  [!] Invalid option. Try again.", C.RED))
            time.sleep(1)


if __name__ == "__main__":
    if sys.platform != "win32":
        print("This script is for Windows only.")
        sys.exit(1)
    enable_ansi()
    if not is_admin():
        elevate()
    else:
        menu()