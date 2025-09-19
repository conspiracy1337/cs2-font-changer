#!/usr/bin/env python3
"""
CS2 Font Changer - Main Application Entry Point
Handles application initialization and startup logic
"""

import os
import sys
from pathlib import Path

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
    msg.setText("First Time Setup")
    msg.setInformativeText(
        "This appears to be the first time running CS2 Font Changer.\n\n"
        "Would you like to install custom font support?\n\n"
        "This will backup your current CS2 font configuration files\n"
        "and set up the system for custom fonts."
    )
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.Yes)
    
    return msg.exec_() == QMessageBox.Yes


def main():
    """Main function to run the application"""
    # Set Qt attribute for WebEngine before creating QApplication
    try:
        from PyQt5.QtCore import Qt, QCoreApplication
        QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    except:
        pass  # Ignore if Qt attributes aren't available
        
    # Initialize QApplication first (needed for message boxes)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("CS2 Font Changer")
    app.setApplicationVersion("3.0")
    
    # Get application directory
    app_dir = get_app_directory()
    
    # Run setup to ensure everything is properly initialized
    setup_application(app_dir)
    
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
                                      "Custom font support has been installed successfully!\n\nYou can now use the font changer to apply custom fonts to CS2.")
        else:
            # User chose No - exit immediately
            sys.exit(0)
    
    # Import GUI only after first install check
    from gui import CS2FontChangerGUI
    
    # Create and show main window
    window = CS2FontChangerGUI(app_dir)
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()