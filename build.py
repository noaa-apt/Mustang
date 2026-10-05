import os
import stat
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.join(ROOT, "src", "gui.py")
ASSETS_DIR = os.path.join(ROOT, "assets")
ICON_ICO = os.path.join(ASSETS_DIR, "mustang.ico")
ICON_PNG = os.path.join(ASSETS_DIR, "mustang.png")

MIME_XML = """<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-mustang">
    <comment>Mustang compiled file</comment>
    <glob pattern="*.mustang"/>
    <icon name="mustang-file"/>
  </mime-type>
</mime-info>
"""

DESKTOP_ENTRY = """[Desktop Entry]
Type=Application
Name=Mustang
Comment=Run Mustang compiled files
Exec={exec_cmd}
Icon=mustang-file
Terminal=true
MimeType=application/x-mustang;
NoDisplay=true
"""


def check_python():
    if sys.version_info < (3, 7):
        print("ERROR: Mustang requires Python 3.7 or newer.")
        print(f"       You are running Python {sys.version.split()[0]}.")
        sys.exit(1)
    print(f"[ok] Python {sys.version.split()[0]} detected.")


def check_tkinter():
    try:
        import tkinter  # noqa: F401
        print("[ok] tkinter is available.")
    except ImportError:
        print("ERROR: tkinter is not installed.")
        print("       Debian/Ubuntu : sudo apt install python3-tk")
        print("       Fedora        : sudo dnf install python3-tkinter")
        print("       Windows/macOS : tkinter ships with the standard installer.")
        sys.exit(1)


def check_gui_present():
    if not os.path.isfile(GUI_PATH):
        print(f"ERROR: Could not find {GUI_PATH}")
        print("       The package looks incomplete or was unzipped incorrectly.")
        sys.exit(1)
    print("[ok] Mustang GUI found.")


def write_launchers():
    bat_path = os.path.join(ROOT, "Windows_x64_Start.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write("@echo off\r\n")
        f.write(f'"{sys.executable}" "{GUI_PATH}"\r\n')
        f.write("pause\r\n")
    print(f"[ok] Created launcher: {os.path.basename(bat_path)}")

    sh_path = os.path.join(ROOT, "Linux_x64_Start.sh")
    with open(sh_path, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(f'"{sys.executable}" "{GUI_PATH}"\n')
    st = os.stat(sh_path)
    os.chmod(sh_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print(f"[ok] Created launcher: {os.path.basename(sh_path)}")


def register_windows():
    import winreg

    classes = r"Software\Classes"
    prog_id = "MustangFile"

    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{classes}\\.mustang") as k:
            winreg.SetValue(k, "", winreg.REG_SZ, prog_id)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{classes}\\{prog_id}") as k:
            winreg.SetValue(k, "", winreg.REG_SZ, "Mustang Compiled File")

        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER, f"{classes}\\{prog_id}\\DefaultIcon"
        ) as k:
            winreg.SetValue(k, "", winreg.REG_SZ, f"{ICON_ICO},0")

        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER, f"{classes}\\{prog_id}\\shell\\open\\command"
        ) as k:
            winreg.SetValue(k, "", winreg.REG_SZ, f'"{sys.executable}" "%1" %*')

        try:
            import ctypes
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
        except Exception:
            pass

        print("[ok] Registered .mustang file type (double click now runs it with Python).")
        print(f"[ok] File icon set from {os.path.basename(ICON_ICO)}.")
    except OSError as exc:
        print(f"[warn] Could not register .mustang file type: {exc}")
        print("       You can still run compiled files with: python file.mustang")


def _run_quiet(cmd):
    try:
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False


def register_linux():
    home = os.path.expanduser("~")

    mime_dir = os.path.join(home, ".local", "share", "mime", "packages")
    os.makedirs(mime_dir, exist_ok=True)
    with open(os.path.join(mime_dir, "mustang.xml"), "w", encoding="utf-8") as f:
        f.write(MIME_XML)

    apps_dir = os.path.join(home, ".local", "share", "applications")
    os.makedirs(apps_dir, exist_ok=True)
    desktop_path = os.path.join(apps_dir, "mustang.desktop")
    with open(desktop_path, "w", encoding="utf-8") as f:
        f.write(DESKTOP_ENTRY.format(exec_cmd=f'{sys.executable} "%f"'))
    os.chmod(desktop_path, 0o755)

    ok = True
    ok &= _run_quiet(["update-mime-database", os.path.join(home, ".local", "share", "mime")])
    ok &= _run_quiet(
        ["xdg-icon-resource", "install", "--mode", "user", "--novendor", "--size", "256",
         ICON_PNG, "mustang-file"]
    )
    ok &= _run_quiet(["update-desktop-database", apps_dir])
    ok &= _run_quiet(["xdg-mime", "default", "mustang.desktop", "application/x-mustang"])

    if ok:
        print("[ok] Registered .mustang file type (double click now runs it with Python).")
        print("[ok] File icon installed into your icon theme.")
    else:
        print("[warn] Some desktop integration tools were not found on this system.")
        print("       .mustang files will still run with: python3 file.mustang")
        print("       Double click behavior depends on your file manager/desktop.")


def register_file_type():
    if sys.platform.startswith("win"):
        register_windows()
    elif sys.platform.startswith("linux"):
        register_linux()
    else:
        print("[info] Automatic double click registration is not set up for this OS.")
        print("       .mustang files still run fine with: python3 file.mustang")


def main():
    print("Building Mustang...")
    print("-" * 42)
    check_python()
    check_tkinter()
    check_gui_present()
    write_launchers()
    register_file_type()
    print("-" * 42)
    print("Mustang is finished.")
    print("  Windows     : double click Windows_x64_Start.bat")
    print("  macOS & Linux : ./Linux_x64_Start.sh")
    print("  2026 Copyright noaa-apt")


if __name__ == "__main__":
    main()
