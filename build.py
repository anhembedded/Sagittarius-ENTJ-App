import os
import platform
import subprocess
import shutil

# --- Configuration ---
APP_NAME = "Sagittarius-ENTJ"
ENTRY_POINT = os.path.join("src", "main.py")
THEMES_DIR = os.path.join("src", "themes")
DIST_DIR = "dist"
BUILD_DIR = "build"
# Optional: Specify an icon path. E.g., "assets/icon.ico" or "assets/icon.png"
ICON_PATH = None

def build():
    """
    Builds the application for the current platform using PyInstaller.
    """
    print(f"--- Starting build for {platform.system()} ---")

    # 1. Clean up previous builds
    print("1. Cleaning up previous build artifacts...")
    for d in [DIST_DIR, BUILD_DIR]:
        if os.path.isdir(d):
            print(f"   Removing directory: {d}")
            shutil.rmtree(d)
    spec_file = f"{APP_NAME}.spec"
    if os.path.exists(spec_file):
        print(f"   Removing file: {spec_file}")
        os.remove(spec_file)
    print("   Cleanup complete.")

    # 2. Construct PyInstaller command
    # Use os.pathsep for platform-correct path separation in --add-data (';' on Win, ':' on Linux/macOS)
    add_data_arg = f"{THEMES_DIR}{os.pathsep}themes"

    command = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",      # Create a single-file executable
        "--windowed",     # No console window in the final application
        "--add-data", add_data_arg,
    ]

    # Add an icon if specified and it exists
    if ICON_PATH and os.path.exists(ICON_PATH):
        print(f"   Adding icon: {ICON_PATH}")
        command.extend(["--icon", ICON_PATH])

    command.append(ENTRY_POINT)

    print(f"\n2. Running PyInstaller command:\n   {' '.join(command)}")

    # 3. Run the build command
    try:
        # Run and stream output to the console in real-time
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')

        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip())

        process.wait()

        if process.returncode != 0:
            print(f"\n--- PyInstaller Build Failed with return code {process.returncode} ---")
            return

        print("\n--- PyInstaller build completed successfully! ---")
        print(f"Executable created in the '{os.path.abspath(DIST_DIR)}' directory.")

    except FileNotFoundError:
        print("\n--- Build Failed ---")
        print("Error: 'pyinstaller' command not found.")
        print("Please ensure PyInstaller is installed and in your system's PATH.")
        print(f"You can install it using: pip install -r requirements.txt")
    except Exception as e:
        print(f"\n--- An unexpected error occurred: {e} ---")


if __name__ == "__main__":
    build()