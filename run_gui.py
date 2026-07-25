"""
Root-level launcher for the desktop GUI.
This is the recommended PyInstaller entry point (keeps import paths simple
when the app is frozen into a single EXE).
"""
from gui.main_window import launch

if __name__ == "__main__":
    launch()
