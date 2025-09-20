"""
CS2 Font Changer - Auto Updater
Automatically downloads and replaces EXE or source code
"""

import os
import sys
import json
import shutil
import zipfile
import tempfile
import subprocess
import threading
import re
import time
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


class AutoUpdater(QThread if QT_AVAILABLE else object):
    """Auto updater that replaces EXE or source code"""
    updateFound = pyqtSignal(dict) if QT_AVAILABLE else None
    
    def __init__(self):
        if QT_AVAILABLE:
            super().__init__()
        self.current_dir = Path(__file__).parent
        self.is_exe = self.detect_exe_environment()
        self.temp_dir = None
        
        # Get app data directory for persistent script storage
        if os.name == 'nt':  # Windows
            self.app_data_dir = Path(os.getenv('APPDATA')) / "cns" / "cs2-font-changer"
        else:
            self.app_data_dir = Path.home() / ".config" / "cs2-font-changer"
        
        self.setup_dir = self.app_data_dir / "setup"
        self.setup_dir.mkdir(parents=True, exist_ok=True)
        
    def detect_exe_environment(self):
        """Detect if running from EXE or source code - improved PyInstaller detection"""
        # Method 1: PyInstaller detection
        if getattr(sys, 'frozen', False):
            return True
        
        # Method 2: Check for _MEIPASS (PyInstaller specific)
        if hasattr(sys, '_MEIPASS'):
            return True
        
        # Method 3: Check if running from a .exe file
        if sys.argv[0].endswith('.exe'):
            return True
        
        # Method 4: Check for EXE files in current directory
        for exe_name in ["main.exe", "CS2FontChanger.exe", "cs2-font-changer.exe"]:
            if (self.current_dir / exe_name).exists():
                return True
        
        # Method 5: Check if current script path looks like a temporary extraction
        script_path = Path(__file__).resolve()
        if 'temp' in str(script_path).lower() or '_mei' in str(script_path).lower():
            return True
                
        return False
    
    def get_latest_release_info(self):
        """Get latest release information from GitHub API"""
        try:
            request = Request(GITHUB_API_URL)
            request.add_header('User-Agent', 'CS2FontChanger-AutoUpdater')
            
            with urlopen(request, timeout=15) as response:
                if response.status != 200:
                    return None
                
                data = json.loads(response.read().decode('utf-8'))
                
                latest_version = data['tag_name'].lstrip('v')
                source_url = data['zipball_url']
                exe_download_url = None
                
                # Look for EXE asset with priority
                assets = data.get('assets', [])
                
                for asset in assets:
                    asset_name = asset['name'].lower()
                    
                    # Priority: CS2FontChanger.exe > main.exe > any .exe
                    if 'cs2fontchanger' in asset_name and asset_name.endswith('.exe'):
                        exe_download_url = asset['browser_download_url']
                        break
                    elif 'main' in asset_name and asset_name.endswith('.exe'):
                        exe_download_url = asset['browser_download_url']
                        break
                    elif asset_name.endswith('.exe'):
                        exe_download_url = asset['browser_download_url']
                        # Continue looking for better match
                
                # If no direct EXE, look for ZIP with EXE
                if not exe_download_url:
                    for asset in assets:
                        asset_name = asset['name'].lower()
                        if ('exe' in asset_name or 'executable' in asset_name) and asset_name.endswith('.zip'):
                            exe_download_url = asset['browser_download_url']
                            break
                
                return {
                    'version': latest_version,
                    'current_version': CURRENT_VERSION,
                    'needs_update': self.compare_versions(CURRENT_VERSION, latest_version),
                    'source_url': source_url,
                    'exe_url': exe_download_url,
                    'release_notes': data.get('body', 'No release notes available.')
                }
                
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None
    
    def compare_versions(self, current, latest):
        """Compare version strings"""
        try:
            # Handle different version formats
            current_clean = re.sub(r'[^\d.]', '', current)
            latest_clean = re.sub(r'[^\d.]', '', latest)
            
            current_parts = [int(x) for x in current_clean.split('.') if x]
            latest_parts = [int(x) for x in latest_clean.split('.') if x]
            
            # Pad with zeros to same length
            max_len = max(len(current_parts), len(latest_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            
            return latest_parts > current_parts
        except ValueError:
            return current != latest
    
    def run(self):
        """Background thread execution"""
        release_info = self.get_latest_release_info()
        
        if release_info and release_info['needs_update']:
            if QT_AVAILABLE and self.updateFound:
                self.updateFound.emit(release_info)
            else:
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
    
    def download_file_with_progress(self, url, destination):
        """Download file with progress bar"""
        try:
            if QT_AVAILABLE:
                return self.download_with_gui_progress(url, destination)
            else:
                return self.download_with_console_progress(url, destination)
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    def download_with_gui_progress(self, url, destination):
        """Download with PyQt progress dialog"""
        from PyQt5.QtWidgets import QProgressDialog
        from PyQt5.QtCore import Qt
        import urllib.request
        
        # Create progress dialog
        progress = QProgressDialog("Downloading update...", "Cancel", 0, 100)
        progress.setWindowTitle("CS2 Font Changer Updater")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(int((downloaded / total_size) * 100), 100)
                progress.setValue(percent)
                progress.setLabelText(f"Downloading update... {percent}% ({downloaded // 1024} KB / {total_size // 1024} KB)")
                
                # Process events to keep GUI responsive
                QApplication.processEvents()
                
                # Check if user cancelled
                if progress.wasCanceled():
                    raise Exception("Download cancelled by user")
        
        try:
            print(f"Downloading from: {url}")
            urllib.request.urlretrieve(url, destination, progress_hook)
            progress.setValue(100)
            progress.close()
            print(f"Download completed: {destination}")
            return True
        except Exception as e:
            progress.close()
            if "cancelled" not in str(e).lower():
                if QT_AVAILABLE:
                    QMessageBox.critical(None, "Download Error", f"Failed to download update:\n{str(e)}")
            raise
    
    def download_with_console_progress(self, url, destination):
        """Download with console progress"""
        import urllib.request
        import sys
        
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(int((downloaded / total_size) * 100), 100)
                sys.stdout.write(f"\rDownloading: {percent}% ({downloaded // 1024} KB / {total_size // 1024} KB)")
                sys.stdout.flush()
        
        try:
            print(f"Downloading from: {url}")
            urllib.request.urlretrieve(url, destination, progress_hook)
            print(f"\nDownload completed: {destination}")
            return True
        except Exception as e:
            print(f"\nDownload failed: {e}")
            return False
    
    def perform_update(self, release_info):
        """Perform the actual update"""
        try:
            # Create backup directory
            backup_dir = self.current_dir / "backup_before_update"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            backup_dir.mkdir()
            print(f"Created backup directory: {backup_dir}")
            
            success = False
            if self.is_exe:
                print("Detected EXE environment - performing EXE update")
                success = self.update_exe_version(release_info, backup_dir)
            else:
                print("Detected source environment - performing source update")
                success = self.update_source_version(release_info, backup_dir)
            
            if not success:
                raise Exception("Update process failed")
                
        except Exception as e:
            error_msg = f"Update failed: {str(e)}"
            print(error_msg)
            if QT_AVAILABLE:
                QMessageBox.critical(None, "Update Failed", error_msg)
    
    def update_exe_version(self, release_info, backup_dir):
        """Update EXE version - downloads to temp folder and uses batch helper"""
        exe_url = release_info.get('exe_url')
        if not exe_url:
            error_msg = "No EXE download available for this release"
            print(error_msg)
            if QT_AVAILABLE:
                QMessageBox.warning(None, "Update Error", error_msg)
            return False
        
        try:
            # Find current executable with MEI path handling
            current_exe = self.find_current_executable()
            if not current_exe:
                raise Exception("Could not locate current executable")
            
            print(f"Current executable: {current_exe}")
            
            # Validate executable path
            if not current_exe.exists():
                raise Exception(f"Located executable does not exist: {current_exe}")
            
            if not current_exe.suffix.lower() == '.exe':
                raise Exception(f"Located file is not an executable: {current_exe}")
            
            # Additional MEI validation
            if hasattr(sys, '_MEIPASS'):
                mei_path = Path(sys._MEIPASS)
                if current_exe.is_relative_to(mei_path):
                    raise Exception(f"Found executable is in MEI temp directory: {current_exe}. Cannot update temp files.")
            
            # Create temp update directory in setup
            update_temp_dir = self.setup_dir / "update"
            if update_temp_dir.exists():
                shutil.rmtree(update_temp_dir)
            update_temp_dir.mkdir(parents=True)
            
            print(f"Created temp update directory: {update_temp_dir}")
            
            # Download new executable to temp directory
            if exe_url.endswith('.zip'):
                new_exe_path = self.download_and_extract_exe_to_temp(exe_url, update_temp_dir)
            else:
                new_exe_path = update_temp_dir / current_exe.name
                if not self.download_file_with_progress(exe_url, new_exe_path):
                    raise Exception("Failed to download new executable")
            
            if not new_exe_path or not new_exe_path.exists():
                raise Exception("Downloaded executable not found")
            
            print(f"Downloaded new executable to: {new_exe_path}")
            
            # Backup current executable
            backup_exe = backup_dir / current_exe.name
            shutil.copy2(current_exe, backup_exe)
            print(f"Backed up current executable to: {backup_exe}")
            
            # Create and execute helper batch script
            self.create_update_helper_batch(current_exe, new_exe_path, update_temp_dir, release_info['version'])
            
            return True
            
        except Exception as e:
            print(f"EXE update failed: {e}")
            raise
    
    def download_and_extract_exe_to_temp(self, zip_url, temp_dir):
        """Download ZIP and extract EXE to temp directory"""
        zip_path = temp_dir / "executable.zip"
        if not self.download_file_with_progress(zip_url, zip_path):
            return None
        
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(extract_dir)
        
        # Find EXE in extracted files
        exe_files = list(extract_dir.rglob("*.exe"))
        if not exe_files:
            return None
        
        # Prefer CS2FontChanger.exe or main.exe
        selected_exe = None
        for exe_file in exe_files:
            if 'cs2fontchanger' in exe_file.name.lower():
                selected_exe = exe_file
                break
            elif 'main' in exe_file.name.lower():
                selected_exe = exe_file
                break
        
        if not selected_exe:
            selected_exe = exe_files[0]  # Return first EXE found
        
        # Move EXE to temp root and clean up
        final_exe_path = temp_dir / selected_exe.name
        shutil.move(selected_exe, final_exe_path)
        
        # Clean up extraction
        shutil.rmtree(extract_dir)
        zip_path.unlink()
        
        return final_exe_path
    
    def create_update_helper_batch(self, current_exe, new_exe_path, update_temp_dir, version):
        """Create batch update script for EXE - no process killing, manual restart"""
        script_path = self.setup_dir / "update_helper.bat"
        
        # Convert to absolute paths
        abs_current_exe = current_exe.resolve()
        abs_new_exe = new_exe_path.resolve()
        abs_update_dir = update_temp_dir.resolve()
        
        script_content = f'''@echo off
echo CS2 Font Changer Auto-Updater
echo ===============================
echo Waiting for application to fully close...

timeout /t 3 /nobreak >nul

echo Replacing executable...
del "{abs_current_exe}"
move "{abs_new_exe}" "{abs_current_exe}"

echo Cleaning up temp files...
rmdir /s /q "{abs_update_dir}"

echo.
echo ===============================
echo UPDATE COMPLETED SUCCESSFULLY!
echo ===============================
echo Updated to version: {version}
echo.
echo Press any key to close this window...
pause >nul

del "%~f0"
'''
        
        try:
            # Write the batch script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print(f"Created batch update helper: {script_path}")
            
            # Show completion message for EXE update - manual restart required
            if QT_AVAILABLE:
                QMessageBox.information(None, "Update Ready", 
                                      f"Update downloaded successfully!\n\n"
                                      f"The application will now close and update to version {version}.\n\n"
                                      f"Update completed. Please relaunch the application")
                QApplication.quit()
            else:
                print("Starting update process...")
                print(f"After update, manually restart: {abs_current_exe}")
            
            # Start the batch script and exit
            subprocess.Popen([str(script_path)], shell=True, cwd=str(self.setup_dir))
            sys.exit(0)
                
        except Exception as e:
            error_msg = f"Failed to create batch update helper: {e}"
            print(error_msg)
            if QT_AVAILABLE:
                QMessageBox.critical(None, "Update Error", error_msg)
    
    def find_current_executable(self):
        """Find the current executable file - handles PyInstaller MEI paths"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable (PyInstaller)
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller bundle - sys.executable points to temp MEI directory
                # We need to find the actual .exe file location
                
                # Method 1: Try sys.argv[0] which should be the actual .exe path
                if sys.argv[0].endswith('.exe'):
                    exe_path = Path(sys.argv[0]).resolve()
                    if exe_path.exists():
                        return exe_path
                
                # Method 2: Look for .exe in parent directories of MEI temp
                mei_path = Path(sys._MEIPASS)
                
                # Common PyInstaller patterns - look in parent dirs
                search_paths = [
                    mei_path.parent,  # One level up from MEI
                    mei_path.parent.parent,  # Two levels up
                    Path.cwd(),  # Current working directory
                    Path(__file__).parent if not getattr(sys, 'frozen', False) else Path.cwd()
                ]
                
                exe_names = ["CS2FontChanger.exe", "main.exe", "cs2-font-changer.exe"]
                
                for search_path in search_paths:
                    if search_path.exists():
                        for exe_name in exe_names:
                            potential_exe = search_path / exe_name
                            if potential_exe.exists():
                                return potential_exe
                
                # Method 3: Use process information (Windows only)
                if os.name == 'nt':
                    try:
                        import psutil
                        current_process = psutil.Process()
                        exe_path = Path(current_process.exe())
                        if exe_path.exists() and exe_path.suffix.lower() == '.exe':
                            return exe_path
                    except ImportError:
                        pass
                    except Exception:
                        pass
                
                # Method 4: Fallback - search common locations
                common_locations = [
                    Path.home() / "Desktop",
                    Path.home() / "Downloads", 
                    Path("C:/") / "Program Files" / "CS2FontChanger",
                    Path("C:/") / "Program Files (x86)" / "CS2FontChanger"
                ]
                
                for location in common_locations:
                    if location.exists():
                        for exe_name in exe_names:
                            potential_exe = location / exe_name
                            if potential_exe.exists():
                                return potential_exe
            else:
                # Not PyInstaller, use sys.executable directly
                return Path(sys.executable)
        
        # Running as Python script - look for EXE files in current directory
        exe_names = ["CS2FontChanger.exe", "main.exe"]
        for exe_name in exe_names:
            exe_path = self.current_dir / exe_name
            if exe_path.exists():
                return exe_path
        
        return None
    
    def download_and_extract_exe(self, zip_url):
        """Download ZIP and extract EXE"""
        zip_path = self.temp_dir / "executable.zip"
        if not self.download_file_with_progress(zip_url, zip_path):
            return None
        
        extract_dir = self.temp_dir / "extracted"
        extract_dir.mkdir()
        
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(extract_dir)
        
        # Find EXE in extracted files
        exe_files = list(extract_dir.rglob("*.exe"))
        if not exe_files:
            return None
        
        # Prefer CS2FontChanger.exe or main.exe
        for exe_file in exe_files:
            if 'cs2fontchanger' in exe_file.name.lower():
                return exe_file
            elif 'main' in exe_file.name.lower():
                return exe_file
        
        return exe_files[0]  # Return first EXE found
    
    def create_replacement_script(self, current_exe, new_exe, version):
        """Create update script in AppData setup directory for reliable replacement"""
        # Store script in persistent AppData location
        script_path = self.setup_dir / "cs2_update_script.bat"
        log_path = self.setup_dir / "update_log.txt"
        
        # Create comprehensive update script
        script_content = f'''@echo off
cd /d "{self.setup_dir}"
echo CS2 Font Changer Auto-Updater > "{log_path}"
echo ================================ >> "{log_path}"
echo Update started at %date% %time% >> "{log_path}"
echo Current EXE: {current_exe} >> "{log_path}"
echo New EXE: {new_exe} >> "{log_path}"
echo Target Version: {version} >> "{log_path}"
echo. >> "{log_path}"

echo Waiting for CS2 Font Changer to close...
echo Waiting for application to close... >> "{log_path}"

REM Wait longer to ensure app is fully closed
timeout /t 5 /nobreak >nul

REM Kill any remaining processes
taskkill /f /im "CS2FontChanger.exe" >nul 2>&1
taskkill /f /im "main.exe" >nul 2>&1
timeout /t 2 /nobreak >nul

echo Attempting to replace executable... >> "{log_path}"
echo Replacing: "{current_exe}" >> "{log_path}"
echo With: "{new_exe}" >> "{log_path}"

REM Try multiple replacement methods
echo Method 1: Direct copy >> "{log_path}"
copy /y "{new_exe}" "{current_exe}" >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: Direct copy worked >> "{log_path}"
    goto :success
)

echo Method 1 failed, trying Method 2: Move and copy >> "{log_path}"
move "{current_exe}" "{current_exe}.old" >nul 2>&1
copy /y "{new_exe}" "{current_exe}" >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: Move and copy worked >> "{log_path}"
    del "{current_exe}.old" >nul 2>&1
    goto :success
)

echo Method 2 failed, trying Method 3: Robocopy >> "{log_path}"
robocopy "{Path(new_exe).parent}" "{current_exe.parent}" "{Path(new_exe).name}" /mov >nul 2>&1
if %errorlevel% lss 8 (
    echo SUCCESS: Robocopy worked >> "{log_path}"
    goto :success
)

echo ERROR: All replacement methods failed >> "{log_path}"
echo Update failed! Check permissions and try running as administrator. >> "{log_path}"
pause
goto :end

:success
echo Update completed successfully! >> "{log_path}"
echo Updated to version: {version} >> "{log_path}"
echo Restarting application... >> "{log_path}"

REM Verify the file was updated
if exist "{current_exe}" (
    echo Verified: Updated executable exists >> "{log_path}"
    timeout /t 1 /nobreak >nul
    
    REM Start the updated application
    echo Starting: "{current_exe}" >> "{log_path}"
    start "" "{current_exe}"
    
    if %errorlevel% equ 0 (
        echo SUCCESS: Application restarted >> "{log_path}"
    ) else (
        echo ERROR: Failed to restart application >> "{log_path}"
    )
) else (
    echo ERROR: Updated executable not found >> "{log_path}"
)

REM Cleanup
timeout /t 3 /nobreak >nul
echo Cleaning up temporary files... >> "{log_path}"
rmdir /s /q "{self.temp_dir}" >nul 2>&1
echo Cleanup completed >> "{log_path}"

:end
echo Update process finished at %date% %time% >> "{log_path}"
echo. >> "{log_path}"

REM Self-delete the script (optional - comment out for debugging)
REM (goto) 2>nul & del "%~f0"
'''
        
        try:
            # Write the script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print(f"Created update script: {script_path}")
            print(f"Update log will be at: {log_path}")
            
            # Make script executable and show completion message
            if QT_AVAILABLE:
                reply = QMessageBox.question(None, "Update Ready", 
                                          f"Update downloaded successfully!\n\n"
                                          f"The application will now close and update to version {version}.\n"
                                          f"The update script is located at:\n{script_path}\n\n"
                                          f"If the automatic restart fails, you can run the script manually.\n\n"
                                          f"Continue with update?",
                                          QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    QApplication.quit()
                    # Execute the script
                    subprocess.Popen([str(script_path)], shell=True, 
                                   creationflags=subprocess.CREATE_NEW_CONSOLE,
                                   cwd=str(self.setup_dir))
                    sys.exit(0)
                else:
                    print("Update cancelled by user")
                    return
            else:
                print("Starting update process...")
                subprocess.Popen([str(script_path)], shell=True, cwd=str(self.setup_dir))
                sys.exit(0)
                
        except Exception as e:
            error_msg = f"Failed to create update script: {e}"
            print(error_msg)
            if QT_AVAILABLE:
                QMessageBox.critical(None, "Update Error", error_msg)
    
    def update_source_version(self, release_info, backup_dir):
        """Update source code version - downloads entire source to temp folder and uses batch helper"""
        source_url = release_info['source_url']
        
        try:
            # Create temp update directory in setup
            update_temp_dir = self.setup_dir / "update"
            if update_temp_dir.exists():
                shutil.rmtree(update_temp_dir)
            update_temp_dir.mkdir(parents=True)
            
            print(f"Created temp update directory: {update_temp_dir}")
            
            # Download source ZIP to temp directory
            zip_path = update_temp_dir / "source.zip"
            if not self.download_file_with_progress(source_url, zip_path):
                raise Exception("Failed to download source code")
            
            # Extract source to temp directory
            extract_dir = update_temp_dir / "extracted"
            extract_dir.mkdir()
            
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                zip_file.extractall(extract_dir)
            
            repo_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
            if not repo_dirs:
                raise Exception("Invalid source package")
            
            source_dir = repo_dirs[0]
            print(f"Extracted source to: {source_dir}")
            
            # Move ALL source files and directories to update temp root
            files_to_update = []
            dirs_to_update = []
            
            # Get all items from source directory
            for item in source_dir.iterdir():
                if item.is_file():
                    dest_file = update_temp_dir / item.name
                    shutil.move(item, dest_file)
                    files_to_update.append(item.name)
                    print(f"Prepared file for update: {item.name}")
                elif item.is_dir():
                    dest_dir = update_temp_dir / item.name
                    shutil.move(item, dest_dir)
                    dirs_to_update.append(item.name)
                    print(f"Prepared directory for update: {item.name}")
            
            # Clean up extraction artifacts
            shutil.rmtree(extract_dir)
            zip_path.unlink()
            
            # Backup ALL existing files and directories that will be replaced
            for file_name in files_to_update:
                current_file = self.current_dir / file_name
                if current_file.exists():
                    backup_file = backup_dir / file_name
                    shutil.copy2(current_file, backup_file)
                    print(f"Backed up file: {file_name}")
            
            for dir_name in dirs_to_update:
                current_dir_path = self.current_dir / dir_name
                if current_dir_path.exists():
                    backup_dir_path = backup_dir / dir_name
                    shutil.copytree(current_dir_path, backup_dir_path)
                    print(f"Backed up directory: {dir_name}")
            
            print(f"Prepared {len(files_to_update)} files and {len(dirs_to_update)} directories for update")
            
            # Create and execute helper batch script for source update
            self.create_source_update_helper_batch(files_to_update, dirs_to_update, update_temp_dir, release_info['version'])
            
            return True
            
        except Exception as e:
            print(f"Source update failed: {e}")
            raise
    
    def create_source_update_helper_batch(self, files_to_update, dirs_to_update, update_temp_dir, version):
        """Create update_helper.bat script for source code update - handles all files and directories"""
        script_path = self.setup_dir / "update_helper.bat"
        
        # Build delete commands for current files
        delete_commands = []
        for file_name in files_to_update:
            current_file = self.current_dir / file_name
            delete_commands.append(f'del "{current_file}"')
        
        # Build rmdir commands for current directories
        for dir_name in dirs_to_update:
            current_dir_path = self.current_dir / dir_name
            delete_commands.append(f'rmdir /s /q "{current_dir_path}"')
        
        # Build move commands for new files
        move_commands = []
        for file_name in files_to_update:
            new_file = update_temp_dir / file_name
            current_file = self.current_dir / file_name
            move_commands.append(f'move "{new_file}" "{current_file}"')
        
        # Build move commands for new directories
        for dir_name in dirs_to_update:
            new_dir = update_temp_dir / dir_name
            current_dir_path = self.current_dir / dir_name
            move_commands.append(f'move "{new_dir}" "{current_dir_path}"')
        
        script_content = f'''@echo off
timeout /t 3 /nobreak >nul

{chr(10).join(delete_commands)}

{chr(10).join(move_commands)}

rmdir /s /q "{update_temp_dir}"

start "" python "{self.current_dir / "main.py"}"
del "%~f0"
'''
        
        try:
            # Write the script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print(f"Created source update helper: {script_path}")
            
            # Show completion message
            if QT_AVAILABLE:
                QMessageBox.information(None, "Update Ready", 
                                      f"Source code updated successfully!\n\n"
                                      f"The application will now close and update to version {version}.\n"
                                      f"It will restart automatically.")
                QApplication.quit()
            else:
                print("Starting source update process...")
            
            # Start the batch script and exit
            subprocess.Popen([str(script_path)], shell=True, cwd=str(self.setup_dir))
            sys.exit(0)
                
        except Exception as e:
            error_msg = f"Failed to create source update helper: {e}"
            print(error_msg)
            if QT_AVAILABLE:
                QMessageBox.critical(None, "Update Error", error_msg)
    
    def restart_application(self):
        """Restart the application"""
        try:
            if getattr(sys, 'frozen', False):
                # Compiled executable
                subprocess.Popen([sys.executable])
            else:
                # Python script
                subprocess.Popen([sys.executable, "main.py"])
            
            sys.exit(0)
        except Exception as e:
            print(f"Failed to restart application: {e}")
    
    def update_version_file(self, new_version):
        """Update version.py with new version"""
        try:
            version_file = self.current_dir / "version.py"
            
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update version
                updated_content = re.sub(
                    r'CURRENT_VERSION\s*=\s*["\'][^"\']*["\']',
                    f'CURRENT_VERSION = "{new_version}"',
                    content
                )
                
                with open(version_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"Updated version to: {new_version}")
            
        except Exception as e:
            print(f"Failed to update version file: {e}")


class UpdateManager:
    """Manages the update process with GUI integration"""
    
    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        self.updater = AutoUpdater()
        
        if QT_AVAILABLE and self.updater.updateFound:
            self.updater.updateFound.connect(self.show_update_dialog)
    
    def start_background_check(self):
        """Start background update check"""
        if QT_AVAILABLE:
            self.updater.start()
        else:
            thread = threading.Thread(target=self.updater.run, daemon=True)
            thread.start()
    
    def show_update_dialog(self, release_info):
        """Show update dialog when update is found"""
        if not QT_AVAILABLE:
            return
        
        # Check if running from EXE to adjust message
        is_exe = self.updater.is_exe
        
        if is_exe:
            info_text = (
                f"Current version: {release_info['current_version']}\n"
                f"Latest version: {release_info['version']}\n\n"
                f"The update will be downloaded and installed.\n"
                f"You will need to manually restart the application after the update."
            )
        else:
            info_text = (
                f"Current version: {release_info['current_version']}\n"
                f"Latest version: {release_info['version']}\n\n"
                f"The update will be downloaded and installed automatically.\n"
                f"The application will restart after the update."
            )
        
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("CS2 Font Changer Update Available")
        msg.setIcon(QMessageBox.Information)
        msg.setText("A new version is available!")
        msg.setInformativeText(info_text)
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
    
    updater = AutoUpdater()
    updater.run()
    
    if QT_AVAILABLE and QApplication.instance():
        QApplication.instance().quit()


if __name__ == "__main__":
    main()