"""
CS2 Font Changer - Main Application Entry Point
Handles application initialization and startup logic
"""

import os
import sys
import json
import threading
import platform
from pathlib import Path
from urllib.request import Request, urlopen

try:
    from fontTools.ttLib import TTFont
except ImportError:
    print("ERROR: fonttools library not found!")
    print("Please install it with: pip install fonttools")
    print("Also install: pip install requests PyQt5")
    input("Press Enter to exit...")
    exit(1)

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import QStandardPaths
    from PyQt5.QtGui import QIcon
except ImportError:
    print("ERROR: PyQt5 not found!")
    print("Please install it with: pip install PyQt5")
    exit(1)

from setup import setup_application, check_first_install, run_first_install, detect_cs2_install_path

def get_app_directory():
    """Get the application directory in AppData/Roaming"""
    if os.name == 'nt':  # Windows
        appdata_dir = Path(os.getenv('APPDATA'))
    else:
        # For non-Windows, use the Qt standard location
        appdata_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    
    app_dir = appdata_dir / "cns" / "cs2-font-changer"
    return app_dir


def show_first_install_dialog():
    """Show first install confirmation dialog"""
    msg = QMessageBox()
    msg.setWindowTitle("CS2 Font Changer - First Install")
    msg.setIcon(QMessageBox.Question)
    msg.setInformativeText(
        "This is the CS2 Font Changer first time setup.\n\n"
        "Would you like to install custom font support?\n\n"
        "This will backup your CS2 font configuration files.\n"
    )
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.Yes)
    
    return msg.exec_() == QMessageBox.Yes


# Analytics configuration
ANALYTICS_URL = "https://conspiracy.moe/cs2fc.php"
CURRENT_VERSION = "1.0"

def send_analytics():
    system = platform.system()
    release = platform.release()
    machine = platform.machine()
    pyver = f"Python/{platform.python_version()}"

    def analytics_request():
        try:
            # Determine if running from EXE
            is_exe = getattr(sys, 'frozen', False) or any(
                (Path(__file__).parent / exe_name).exists() 
                for exe_name in ["main.exe", "CS2FontChanger.exe"]
            )
            
            # Prepare analytics data
            analytics_data = {
                'version': CURRENT_VERSION,
                'platform': f"{system} {release}; {machine}",
                'python': f'{pyver}',
                'is_exe': "YES" if is_exe else "NO"
            }
            
            # Create request
            request = Request(
                ANALYTICS_URL,
                data=json.dumps(analytics_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json'
                }
            )
            
            with urlopen(request, timeout=5) as response:
                pass
                
        except Exception:
            pass
    
    # Run analytics in background thread
    thread = threading.Thread(target=analytics_request, daemon=True)
    thread.start()


def main():
    # Suppress Qt WebEngine console output completely
    os.environ['QT_LOGGING_RULES'] = '*=false'
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-logging --disable-gpu-sandbox --log-level=3 --silent'
    os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
    
    # Additional suppression for CSS warnings
    import sys
    from io import StringIO
    
    # Redirect stderr temporarily to suppress Qt warnings
    class SuppressOutput:
        def __init__(self):
            self.original_stderr = sys.stderr
            
        def __enter__(self):
            sys.stderr = StringIO()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stderr = self.original_stderr
    
    # Set Qt attribute for WebEngine before creating QApplication
    try:
        from PyQt5.QtCore import Qt, QCoreApplication
        QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    except:
        pass
        
    # Initialize QApplication first (needed for message boxes)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("CS2 Font Changer")
    app.setApplicationVersion("1.0")
    
    # Try to set taskbar icon on Windows
    try:
        if os.name == 'nt':  # Windows only
            import ctypes
            # Set application ID for Windows taskbar grouping
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cns.cs2fontchanger.1.0")
    except Exception:
        pass
    
    # Get directories
    work_dir = Path(__file__).parent  # Directory where main.py is located
    app_dir = get_app_directory()
    
    # Set application icon from work directory assets first, then from appdata assets
    try:
        icon_work_path = work_dir / "assets" / "icon.png"
        icon_assets_path = app_dir / "assets" / "icon.png"
        
        if icon_work_path.exists():
            app.setWindowIcon(QIcon(str(icon_work_path)))
        elif icon_assets_path.exists():
            app.setWindowIcon(QIcon(str(icon_assets_path)))
    except Exception as e:
        print(f"Warning: Could not set application icon: {e}")
    
    # Run setup to ensure everything is properly initialized (pass work_dir)
    setup_application(app_dir, work_dir)
    
    # Check for first install BEFORE creating GUI
    if check_first_install(app_dir / "setup"):
        # Show first install dialog
        if show_first_install_dialog():
            # User chose Yes - try to run first install
            
            # Try to detect CS2 path
            cs2_path = None
            path_file = app_dir / "setup" / "path.txt"
            if path_file.exists():
                try:
                    with open(path_file, 'r', encoding='utf-8') as f:
                        cs2_path = f.read().strip()
                except:
                    pass
            
            if not cs2_path:
                cs2_path = detect_cs2_install_path()
            
            if not cs2_path:
                # Ask user to manually select CS2 path
                from PyQt5.QtWidgets import QFileDialog
                cs2_path = QFileDialog.getExistingDirectory(
                    None, 
                    "Select CS2 Installation Directory",
                    "C:/Program Files (x86)/Steam/steamapps/common"
                )
                
                if not cs2_path:
                    QMessageBox.critical(None, "Setup Cancelled", 
                                       "CS2 installation path is required to continue.\nApplication will exit.")
                    sys.exit(0)
            
            # Run first install
            success = run_first_install(app_dir, cs2_path)
            
            if not success:
                QMessageBox.critical(None, "Installation Failed", 
                                   "Failed to complete first install setup.\nPlease check that CS2 is closed and try running as administrator.\n\nApplication will exit.")
                sys.exit(1)
            else:
                QMessageBox.information(None, "Installation Complete", 
                                      "Custom font support has been installed successfully!\n\n"
                                      "The Asimovian custom font has been applied to CS2.\n\n"
                                      "You can now use the font changer to apply other custom fonts.")
        else:
            # User chose No - exit immediately
            sys.exit(0)
    
    # Import GUI only after first install check
    from gui import CS2FontChangerGUI
    from updater import check_for_updates_silent
    
    # Create and show main window
    window = CS2FontChangerGUI(app_dir)
    
    # Start silent update check after window is created
    update_manager = check_for_updates_silent(window)
    
    window.show()
    
    # Send analytics after application is fully initialized
    send_analytics()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()