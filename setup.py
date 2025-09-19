"""
CS2 Font Changer - Setup Module
Handles application setup, CS2 path detection, and first install logic
"""

import os
import re
import stat
import shutil
import filecmp
from pathlib import Path
from files import create_configuration_files

# Only import winreg on Windows
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False


def detect_cs2_install_path():
    """Automatically detect CS2 installation path"""
    possible_paths = []
    
    if os.name == 'nt' and WINREG_AVAILABLE:
        try:
            # Method 1: Check Steam registry (64-bit)
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as steam_key:
                steam_path = winreg.QueryValueEx(steam_key, "InstallPath")[0]
                cs2_path = Path(steam_path) / "steamapps" / "common" / "Counter-Strike Global Offensive"
                if cs2_path.exists():
                    possible_paths.append(cs2_path)
        except (OSError, FileNotFoundError, winreg.error):
            pass
        
        try:
            # Method 2: Check current user Steam registry  
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam") as steam_key:
                steam_path = winreg.QueryValueEx(steam_key, "SteamPath")[0]
                cs2_path = Path(steam_path) / "steamapps" / "common" / "Counter-Strike Global Offensive"
                if cs2_path.exists():
                    possible_paths.append(cs2_path)
        except (OSError, FileNotFoundError, winreg.error):
            pass
        
        try:
            # Method 3: Check Steam registry for library folders
            steam_config_path = None
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as steam_key:
                    steam_path = winreg.QueryValueEx(steam_key, "InstallPath")[0]
                    steam_config_path = Path(steam_path) / "config" / "libraryfolders.vdf"
            except:
                pass
                
            if not steam_config_path or not steam_config_path.exists():
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam") as steam_key:
                        steam_path = winreg.QueryValueEx(steam_key, "SteamPath")[0]
                        steam_config_path = Path(steam_path) / "config" / "libraryfolders.vdf"
                except:
                    pass
            
            if steam_config_path and steam_config_path.exists():
                with open(steam_config_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    library_paths = re.findall(r'"path"\s*"([^"]+)"', content)
                    for lib_path in library_paths:
                        # Normalize path separators
                        lib_path = lib_path.replace('\\\\', '/')
                        cs2_path = Path(lib_path) / "steamapps" / "common" / "Counter-Strike Global Offensive"
                        if cs2_path.exists():
                            possible_paths.append(cs2_path)
        except Exception:
            pass
    
    # Method 4: Check common Steam locations
    common_locations = [
        "C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive",
        "C:/Program Files/Steam/steamapps/common/Counter-Strike Global Offensive",
        "C:/Steam/steamapps/common/Counter-Strike Global Offensive",
        "C:/SteamLibrary/steamapps/common/Counter-Strike Global Offensive", 
        "D:/Program Files/Steam/steamapps/common/Counter-Strike Global Offensive",
        "D:/Steam/steamapps/common/Counter-Strike Global Offensive",
        "D:/SteamLibrary/steamapps/common/Counter-Strike Global Offensive",
        "E:/Program Files/Steam/steamapps/common/Counter-Strike Global Offensive",
        "E:/Steam/steamapps/common/Counter-Strike Global Offensive",
        "E:/SteamLibrary/steamapps/common/Counter-Strike Global Offensive",
        "F:/Program Files/Steam/steamapps/common/Counter-Strike Global Offensive",
        "F:/Steam/steamapps/common/Counter-Strike Global Offensive",
        "F:/SteamLibrary/steamapps/common/Counter-Strike Global Offensive",
    ]
    
    for path_str in common_locations:
        path = Path(path_str)
        if path.exists():
            possible_paths.append(path)
    
    # Method 5: Check user's documents for Steam library folders
    try:
        user_home = Path.home()
        possible_steam_configs = [
            user_home / "AppData" / "Local" / "Steam" / "config" / "libraryfolders.vdf",
            user_home / "Documents" / "Steam" / "config" / "libraryfolders.vdf",
        ]
        
        for config_path in possible_steam_configs:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    library_paths = re.findall(r'"path"\s*"([^"]+)"', content)
                    for lib_path in library_paths:
                        lib_path = lib_path.replace('\\\\', '/')
                        cs2_path = Path(lib_path) / "steamapps" / "common" / "Counter-Strike Global Offensive"
                        if cs2_path.exists():
                            possible_paths.append(cs2_path)
    except Exception:
        pass
    
    # Return the first valid path found, prefer paths with "game" subfolder structure
    if possible_paths:
        # Check for proper CS2 structure (should have game/csgo subdirectories)
        for path in possible_paths:
            if (path / "game" / "csgo").exists():
                print(f"Auto-detected CS2 path: {path}")
                return str(path)
        
        # Fallback to first found path
        print(f"Auto-detected CS2 path: {possible_paths[0]}")
        return str(possible_paths[0])
    
    print("Could not auto-detect CS2 installation path")
    return None


def remove_readonly(file_path):
    """Remove read-only attribute from file"""
    try:
        file_path = Path(file_path)
        if file_path.exists():
            current_perms = file_path.stat().st_mode
            file_path.chmod(current_perms | stat.S_IWRITE)
            return True
        return False
    except PermissionError as e:
        raise Exception(f"Cannot modify {file_path.name}. Make sure CS2 is closed and try running as administrator.")
    except Exception as e:
        print(f"Warning: Could not remove readonly from {file_path}: {e}")
        return False


def setup_application(app_dir):
    """Setup the application directory structure and configuration"""
    app_dir = Path(app_dir)
    
    print(f"Setting up application directory: {app_dir}")
    
    # Create required directories
    directories = ["dl", "auto", "fonts", "setup"]
    for dir_name in directories:
        dir_path = app_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Create configuration files in setup directory using files.py
    try:
        create_configuration_files(app_dir / "setup")
        print("Created configuration template files")
    except Exception as e:
        print(f"Warning: Could not create configuration files: {e}")
    
    # Check if path.txt exists, if not try to auto-detect
    path_file = app_dir / "setup" / "path.txt"
    if not path_file.exists():
        print("CS2 path not found, attempting auto-detection...")
        detected_path = detect_cs2_install_path()
        if detected_path:
            try:
                with open(path_file, 'w', encoding='utf-8') as f:
                    f.write(detected_path)
                print(f"Saved auto-detected CS2 path: {detected_path}")
            except Exception as e:
                print(f"Warning: Could not save CS2 path: {e}")
    
    # Check if first_install.txt exists
    first_install_file = app_dir / "setup" / "first_install.txt"
    if not first_install_file.exists():
        try:
            with open(first_install_file, 'w', encoding='utf-8') as f:
                f.write("TRUE")
            print("Created first_install.txt with TRUE")
        except Exception as e:
            print(f"Warning: Could not create first_install.txt: {e}")


def check_first_install(setup_dir):
    """Check if first install is needed"""
    try:
        first_install_file = Path(setup_dir) / "first_install.txt"
        
        if first_install_file.exists():
            with open(first_install_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            return content == "TRUE"
    except Exception as e:
        print(f"Warning: Could not check first install status: {e}")
    
    return False


def run_first_install(app_dir, cs2_path):
    """Run the first install process"""
    print("Starting first install process...")
    
    try:
        app_dir = Path(app_dir)
        cs2_path = Path(cs2_path)
        setup_dir = app_dir / "setup"
        
        # Validate CS2 path
        if not cs2_path.exists():
            raise Exception(f"CS2 path does not exist: {cs2_path}")
        
        # Save the CS2 path to path.txt
        path_file = setup_dir / "path.txt"
        with open(path_file, 'w', encoding='utf-8') as f:
            f.write(str(cs2_path))
        print(f"Saved CS2 path: {cs2_path}")
        
        # Define target paths in CS2 directory
        # Check if it's a "game" subfolder structure or direct structure
        if (cs2_path / "game").exists():
            fonts_conf_path = cs2_path / "game" / "csgo" / "panorama" / "fonts" / "fonts.conf"
            repl_global_path = cs2_path / "game" / "core" / "panorama" / "fonts" / "conf.d" / "42-repl-global.conf"
            stratum_path = cs2_path / "game" / "csgo" / "panorama" / "fonts" / "stratum2.uifont"
        else:
            fonts_conf_path = cs2_path / "csgo" / "panorama" / "fonts" / "fonts.conf"
            repl_global_path = cs2_path / "core" / "panorama" / "fonts" / "conf.d" / "42-repl-global.conf"
            stratum_path = cs2_path / "csgo" / "panorama" / "fonts" / "stratum2.uifont"
        
        # Ensure the target directories exist
        fonts_conf_path.parent.mkdir(parents=True, exist_ok=True)
        repl_global_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Ensured target directories exist")
        
        # Define source template paths
        fonts_template_path = setup_dir / "fonts.conf"
        repl_template_path = setup_dir / "42-repl-global.conf"
        
        # Backup existing files if they exist
        if fonts_conf_path.exists():
            backup_path = fonts_conf_path.with_suffix('.conf.old')
            remove_readonly(fonts_conf_path)
            shutil.copy2(fonts_conf_path, backup_path)
            print(f"Backed up existing fonts.conf")
        
        if repl_global_path.exists():
            backup_path = repl_global_path.with_suffix('.conf.old')
            remove_readonly(repl_global_path)
            shutil.copy2(repl_global_path, backup_path)
            print(f"Backed up existing 42-repl-global.conf")
        
        # Remove read-only from target files if they exist
        remove_readonly(fonts_conf_path)
        remove_readonly(repl_global_path)
        
        # Copy template files to CS2 directory
        if fonts_template_path.exists():
            shutil.copy2(fonts_template_path, fonts_conf_path)
            print(f"Copied fonts.conf to {fonts_conf_path}")
        else:
            raise Exception("fonts.conf template not found")
        
        if repl_template_path.exists():
            shutil.copy2(repl_template_path, repl_global_path)
            print(f"Copied 42-repl-global.conf to {repl_global_path}")
        else:
            raise Exception("42-repl-global.conf template not found")
        
        # Set files as read-only to prevent CS2 from overwriting them
        try:
            os.chmod(fonts_conf_path, stat.S_IREAD)
            os.chmod(repl_global_path, stat.S_IREAD)
            print("Set configuration files as read-only")
        except Exception as e:
            print(f"Warning: Could not set files as read-only: {e}")
        
        # Handle stratum2.uifont backup
        if stratum_path.exists():
            backup_stratum = stratum_path.with_suffix('.uifont.old')
            if backup_stratum.exists():
                remove_readonly(backup_stratum)
                backup_stratum.unlink()
            stratum_path.rename(backup_stratum)
            print("Backed up stratum2.uifont")
        
        # Set first_install.txt to FALSE after successful installation
        first_install_file = setup_dir / "first_install.txt"
        with open(first_install_file, 'w', encoding='utf-8') as f:
            f.write("FALSE")
        print("First install completed successfully")
        
        return True
        
    except Exception as e:
        print(f"Error during first install: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test the setup functionality
    test_app_dir = Path("./test_app_dir")
    setup_application(test_app_dir)
    print(f"Test setup completed in: {test_app_dir}")
    
    # Test path detection
    detected = detect_cs2_install_path()
    print(f"Detected CS2 path: {detected}")