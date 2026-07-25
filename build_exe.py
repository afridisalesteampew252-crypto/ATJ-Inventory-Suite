"""
Convenience build script: installs dependencies (if needed) and runs
PyInstaller against ATJCatalogGenerator.spec to produce a standalone EXE.

Usage (Windows, from project root, inside your venv):
    python build_exe.py

Output: dist/ATJCatalogGenerator.exe
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SPEC_FILE = PROJECT_ROOT / "ATJCatalogGenerator.spec"


def run(cmd: list[str]):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"\n\u274c Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def main():
    print("=" * 60)
    print("Building ATJ Catalog Generator EXE")
    print("=" * 60)

    if not SPEC_FILE.exists():
        print(f"\u274c Spec file not found: {SPEC_FILE}")
        sys.exit(1)

    print("\n[1/2] Ensuring PyInstaller is installed...")
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"])

    print("\n[2/2] Running PyInstaller build...")
    run([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(SPEC_FILE)])

    exe_name = "ATJCatalogGenerator.exe" if sys.platform.startswith("win") else "ATJCatalogGenerator"
    exe_path = PROJECT_ROOT / "dist" / exe_name

    print("\n" + "=" * 60)
    if exe_path.exists():
        print(f"\u2705 Build succeeded: {exe_path}")
    else:
        print("\u26A0\uFE0F  Build finished but expected output was not found. Check the dist/ folder.")
    print("=" * 60)


if __name__ == "__main__":
    main()
