import os
import platform
import subprocess
import shutil
import sys
import importlib.util

# --- Configuration ---
APP_NAME = "Sagittarius-ENTJ"
ENTRY_POINT = os.path.join("src", "main.py")
THEMES_DIR = os.path.join("src", "themes")
DIST_DIR = "dist"
BUILD_DIR = "build"
# Optional: Specify an icon path. E.g., "assets/icon.ico" or "assets/icon.png"
ICON_PATH = None

def check_dependencies():
    """Checks if required build tools are installed in the current environment."""
    print("--- Checking for PyInstaller ---")
    pyinstaller_spec = importlib.util.find_spec("PyInstaller")
    if pyinstaller_spec is None:
        print("\n❌ ERROR: PyInstaller is not installed in the current Python environment.")
        print(f"   Current Python executable: {sys.executable}")
        print("\n   This can happen if you are not running from an activated virtual environment.")
        print("   Please ensure you have activated the correct environment and installed dependencies.")
        print("\n   To install dependencies, run:")
        print("   pip install -r requirements.txt")
        print("\n   To activate the virtual environment (if you have one):")
        print("   - On Windows: .venv\\Scripts\\activate")
        print("   - On Linux/macOS: source .venv/bin/activate")
        return False
    print("   PyInstaller found. Proceeding with build.")
    return True

def build():
    """
    Builds the application for the current platform using PyInstaller.
    """
    if not check_dependencies():
        return # Stop if dependencies are not met

    print(f"\n--- Starting build for {platform.system()} ---")

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
    add_data_arg = f"{THEMES_DIR}{os.pathsep}themes"
    command = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",
        "--windowed",
        "--add-data", add_data_arg,
    ]
    if ICON_PATH and os.path.exists(ICON_PATH):
        command.extend(["--icon", ICON_PATH])
    command.append(ENTRY_POINT)

    print(f"\n2. Running PyInstaller command:\n   {' '.join(command)}")

    # 3. Run the build command
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip())
        process.wait()

        if process.returncode != 0:
            print(f"\n--- PyInstaller Build Failed with return code {process.returncode} ---")
            print("   Please check the logs above for errors.")
            return

        print("\n--- PyInstaller build completed successfully! ---")
        print(f"Executable created in the '{os.path.abspath(DIST_DIR)}' directory.")

    except Exception as e:
        print(f"\n--- An unexpected error occurred: {e} ---")


if __name__ == "__main__":
    build()