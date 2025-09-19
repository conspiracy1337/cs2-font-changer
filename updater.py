"""
CS2 Font Changer - Silent Auto Updater
Runs silently in background, checks for updates, and sends analytics
"""

import os
import sys
import json
import shutil
import zipfile
import tempfile
import subprocess
import threading
from pathlib import Path
from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError, HTTPError
from version import CURRENT_VERSION

# Configuration
GITHUB_REPO = "conspiracy1337/cs2-font-changer"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import QThread, pyqtSignal
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False


class SilentUpdater(QThread if QT_AVAILABLE else object):
    """Silent background updater thread"""
    updateFound = pyqtSignal(dict) if QT_AVAILABLE else None
    
    def __init__(self):
        if QT_AVAILABLE:
            super().__init__()
        self.current_dir = Path(__file__).parent
        self.is_exe = self.detect_exe_environment()
        self.temp_dir = None
        
    def detect_exe_environment(self):
        """Detect if running from EXE or source code"""
        if getattr(sys, 'frozen', False):
            return True
        
        for exe_name in ["main.exe", "CS2FontChanger.exe"]:
            if (self.current_dir / exe_name).exists():
                return True
                
        return False
    
    def get_latest_release_info(self):
        """Get latest release information from GitHub API"""
        try:
            with urlopen(GITHUB_API_URL, timeout=10) as response:
                if response.status != 200:
                    return None
                
                data = json.loads(response.read().decode('utf-8'))
                
                latest_version = data['tag_name'].lstrip('v')
                download_url = data['zipball_url']
                exe_download_url = None
                
                # Look for EXE asset in release
                for asset in data.get('assets', []):
                    if asset['name'].endswith('.exe'):
                        exe_download_url = asset['browser_download_url']
                        break
                    elif asset['name'].endswith('.zip') and 'exe' in asset['name'].lower():
                        exe_download_url = asset['browser_download_url']
                        break
                
                return {
                    'version': latest_version,
                    'current_version': CURRENT_VERSION,
                    'needs_update': self.compare_versions(CURRENT_VERSION, latest_version),
                    'source_url': download_url,
                    'exe_url': exe_download_url,
                    'release_notes': data.get('body', 'No release notes available.')
                }
                
        except Exception:
            return None
    
    def compare_versions(self, current, latest):
        """Compare version strings"""
        try:
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            max_len = max(len(current_parts), len(latest_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            
            return latest_parts > current_parts
        except ValueError:
            return current != latest
    
    def run(self):
        """Background thread execution"""
        # Check for updates (analytics removed - now handled in main.py)
        release_info = self.get_latest_release_info()
        
        if release_info and release_info['needs_update']:
            if QT_AVAILABLE and self.updateFound:
                self.updateFound.emit(release_info)
            else:
                # Fallback for non-Qt environments
                self.show_console_update_prompt(release_info)
    
    def show_console_update_prompt(self, release_info):
        """Show console-based update prompt"""
        print(f"\nCS2 Font Changer Update Available!")
        print(f"Current version: {release_info['current_version']}")
        print(f"Latest version: {release_info['version']}")
        print(f"\nRelease Notes:\n{release_info['release_notes']}")
        
        response = input("\nDo you want to update now? (y/N): ").strip().lower()
        if response == 'y':
            self.perform_update(release_info)
    
    def download_file_silent(self, url, destination):
        """Download file silently"""
        try:
            urlretrieve(url, destination)
            return True
        except Exception:
            return False
    
    def perform_update(self, release_info):
        """Perform the actual update"""
        try:
            # Create backup
            backup_dir = self.current_dir / "backup_before_update"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            backup_dir.mkdir()
            
            if self.is_exe:
                self.update_exe_version(release_info['exe_url'], backup_dir)
            else:
                self.update_source_version(release_info['source_url'], backup_dir)
                
        except Exception as e:
            if QT_AVAILABLE:
                QMessageBox.critical(None, "Update Failed", f"Update failed: {str(e)}")
            else:
                print(f"Update failed: {e}")
    
    def update_exe_version(self, exe_url, backup_dir):
        """Update EXE version"""
        if not exe_url:
            raise Exception("No EXE download available")
        
        self.temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Download new EXE
            if exe_url.endswith('.zip'):
                zip_path = self.temp_dir / "update.zip"
                if not self.download_file_silent(exe_url, zip_path):
                    raise Exception("Failed to download update")
                
                with zipfile.ZipFile(zip_path, 'r') as zip_file:
                    zip_file.extractall(self.temp_dir)
                
                exe_files = list(self.temp_dir.rglob("*.exe"))
                if not exe_files:
                    raise Exception("No EXE found in download")
                
                new_exe_path = exe_files[0]
            else:
                new_exe_path = self.temp_dir / "CS2FontChanger.exe"
                if not self.download_file_silent(exe_url, new_exe_path):
                    raise Exception("Failed to download update")
            
            # Find current EXE
            current_exe = None
            for exe_file in self.current_dir.glob("*.exe"):
                if exe_file.name not in ["updater.exe"]:
                    current_exe = exe_file
                    break
            
            if not current_exe:
                current_exe = self.current_dir / "CS2FontChanger.exe"
            
            # Backup current EXE
            shutil.copy2(current_exe, backup_dir / current_exe.name)
            
            # Create update script
            self.create_exe_update_script(new_exe_path, current_exe)
            
        finally:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
    
    def update_source_version(self, source_url, backup_dir):
        """Update source code version"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Download source ZIP
            zip_path = self.temp_dir / "source.zip"
            if not self.download_file_silent(source_url, zip_path):
                raise Exception("Failed to download source code")
            
            # Extract source code
            extract_dir = self.temp_dir / "extracted"
            extract_dir.mkdir()
            
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                zip_file.extractall(extract_dir)
            
            repo_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
            if not repo_dirs:
                raise Exception("Invalid source package")
            
            source_dir = repo_dirs[0]
            
            # Update source files
            source_files = ["main.py", "gui.py", "font.py", "browser.py", "setup.py", "files.py"]
            updated_files = []
            
            for file_name in source_files:
                source_file = source_dir / file_name
                target_file = self.current_dir / file_name
                
                if source_file.exists():
                    if target_file.exists():
                        # Backup current file
                        shutil.copy2(target_file, backup_dir / file_name)
                    
                    # Copy new file
                    shutil.copy2(source_file, target_file)
                    updated_files.append(file_name)
            
            if QT_AVAILABLE:
                QMessageBox.information(None, "Update Complete", 
                    f"Successfully updated {len(updated_files)} files.\nPlease restart the application.")
            else:
                print(f"Successfully updated {len(updated_files)} files. Please restart the application.")
            
        finally:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
    
    def create_exe_update_script(self, new_exe_path, current_exe_path):
        """Create update script for EXE replacement"""
        if os.name == 'nt':
            script_content = f'''@echo off
timeout /t 2 /nobreak >nul
copy /y "{new_exe_path}" "{current_exe_path}" >nul 2>&1
if %errorlevel% equ 0 (
    start "" "{current_exe_path}"
)
del "%~f0"
'''
            script_path = self.current_dir / "update_script.bat"
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            subprocess.Popen([str(script_path)], shell=True)
        else:
            script_content = f'''#!/bin/bash
sleep 2
cp "{new_exe_path}" "{current_exe_path}" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    "{current_exe_path}" &
fi
rm "$0"
'''
            script_path = self.current_dir / "update_script.sh"
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            subprocess.Popen([str(script_path)])


class UpdateManager:
    """Manages the update process with GUI integration"""
    
    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        self.updater = SilentUpdater()
        
        if QT_AVAILABLE and self.updater.updateFound:
            self.updater.updateFound.connect(self.show_update_dialog)
    
    def start_background_check(self):
        """Start background update check"""
        if QT_AVAILABLE:
            self.updater.start()
        else:
            # Run in separate thread for non-Qt environments
            thread = threading.Thread(target=self.updater.run, daemon=True)
            thread.start()
    
    def show_update_dialog(self, release_info):
        """Show update dialog when update is found"""
        if not QT_AVAILABLE:
            return
        
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("CS2 Font Changer Update Available")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"A new version is available!")
        msg.setInformativeText(
            f"Current version: {release_info['current_version']}\n"
            f"Latest version: {release_info['version']}\n\n"
            f"Would you like to update now?"
        )
        msg.setDetailedText(f"Release Notes:\n{release_info['release_notes']}")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec_() == QMessageBox.Yes:
            self.updater.perform_update(release_info)


def check_for_updates_silent(parent_widget=None):
    """Main function to call from your application"""
    update_manager = UpdateManager(parent_widget)
    update_manager.start_background_check()
    return update_manager


def main():
    """Standalone updater execution"""
    if QT_AVAILABLE:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
    
    updater = SilentUpdater()
    updater.run()
    
    if QT_AVAILABLE and QApplication.instance():
        QApplication.instance().quit()


if __name__ == "__main__":
    main()