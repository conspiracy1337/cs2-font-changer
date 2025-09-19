"""
CS2 Font Changer - Font Management Module
Handles font operations and CS2 configuration updates
"""

import os
import stat
import shutil
import filecmp
import re
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
    FONTTOOLS_AVAILABLE = True
except ImportError:
    FONTTOOLS_AVAILABLE = False
    print("Warning: fonttools library not available")


class FontManager:
    """Core font management functionality"""
    
    def __init__(self, app_dir, cs2_path=None):
        self.app_dir = Path(app_dir)
        self.cs2_path = Path(cs2_path) if cs2_path else None
        self.setup_dir = self.app_dir / "setup"
        self.fonts_dir = self.app_dir / "fonts"
        self.auto_dir = self.app_dir / "auto"
        self.dl_dir = self.app_dir / "dl"
        
        # Ignored system fonts that shouldn't be replaced
        self.ignored_fonts = {
            'Stratum2', 'Stratum2 Bold', 'Stratum2 Regular', 'Stratum2 Italic',
            'Stratum2 Bold Italic', 'Stratum2 Light', 'Stratum2 Medium', 'Stratum2 Black',
            'Stratum2 Thin', 'Stratum2 ExtraLight', 'Stratum2 SemiBold', 'Stratum2 ExtraBold',
            'Stratum2 Heavy', 'Stratum2 Condensed', 'Stratum2 Bold Condensed',
            'Stratum2 Regular Monodigit', 'Stratum2 Bold Monodigit'
        }
        
    def get_font_internal_name(self, ttf_path):
        """Get the internal font name from a TTF file using fonttools"""
        if not FONTTOOLS_AVAILABLE:
            print("Error: fonttools not available - cannot read font metadata")
            return None
            
        try:
            font = TTFont(ttf_path)
            name_table = font['name']
            
            # Try to get the font family name (nameID 1)
            for record in name_table.names:
                if record.nameID == 1 and record.platformID == 3:  # Microsoft platform
                    font_name = record.toUnicode()
                    return font_name
            
            # Fallback: try other name IDs
            for record in name_table.names:
                if record.nameID == 1:
                    try:
                        font_name = record.toUnicode()
                        return font_name
                    except:
                        continue
            
            return None
        except Exception as e:
            print(f"Error reading font metadata from {ttf_path}: {e}")
            return None
    
    def remove_readonly(self, file_path):
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
    
    def set_readonly(self, file_path):
        """Set read-only attribute on file"""
        try:
            file_path = Path(file_path)
            if file_path.exists():
                os.chmod(file_path, stat.S_IREAD)
                return True
        except Exception as e:
            print(f"Warning: Could not set readonly attribute on {file_path}: {e}")
            return False
    
    def get_cs2_paths(self):
        """Get CS2 configuration file paths based on directory structure"""
        if not self.cs2_path:
            raise Exception("CS2 path not set")
            
        # Check if it's a "game" subfolder structure or direct structure
        if (self.cs2_path / "game").exists():
            fonts_conf_path = self.cs2_path / "game" / "csgo" / "panorama" / "fonts" / "fonts.conf"
            repl_global_path = self.cs2_path / "game" / "core" / "panorama" / "fonts" / "conf.d" / "42-repl-global.conf"
            cs2_fonts_dir = self.cs2_path / "game" / "csgo" / "panorama" / "fonts"
        else:
            fonts_conf_path = self.cs2_path / "csgo" / "panorama" / "fonts" / "fonts.conf"
            repl_global_path = self.cs2_path / "core" / "panorama" / "fonts" / "conf.d" / "42-repl-global.conf"
            cs2_fonts_dir = self.cs2_path / "csgo" / "panorama" / "fonts"
            
        return fonts_conf_path, repl_global_path, cs2_fonts_dir
    
    def analyze_current_fonts(self, fonts_conf_path, repl_global_path):
        """Analyze current font configuration"""
        current_fonts = set()
        current_fontfiles = []
        
        # Analyze 42-repl-global.conf
        if repl_global_path.exists():
            try:
                with open(repl_global_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                assign_fonts = re.findall(r'<edit name="family" mode="assign">\s*<string>([^<]+)</string>', content)
                current_fonts.update(assign_fonts)
                
                prepend_fonts = re.findall(r'<edit name="family" mode="prepend" binding="strong">\s*<string>([^<]+)</string>', content)
                current_fonts.update(prepend_fonts)
            except Exception as e:
                print(f"Warning: Could not analyze {repl_global_path}: {e}")
        
        # Analyze fonts.conf
        if fonts_conf_path.exists():
            try:
                with open(fonts_conf_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                append_fonts = re.findall(r'<edit name="family" mode="append" binding="strong">\s*<string>([^<]+)</string>', content)
                current_fonts.update(append_fonts)
                
                all_fontpatterns = re.findall(r'<fontpattern>([^<]+)</fontpattern>', content)
                system_patterns = {'.uifont', 'Arial', 'notosans', 'notoserif', 'notomono-regular', '.ttf', '.otf'}
                custom_fontfiles = [f for f in all_fontpatterns if f not in system_patterns and (f.endswith('.ttf') or f.endswith('.otf'))]
                current_fontfiles.extend(custom_fontfiles)
            except Exception as e:
                print(f"Warning: Could not analyze {fonts_conf_path}: {e}")
        
        # Filter out ignored system fonts
        filtered_fonts = [font for font in current_fonts if font not in self.ignored_fonts]
        
        return filtered_fonts, current_fontfiles
    
    def replace_font_in_repl_global(self, file_path, current_font_names, new_font_name):
        """Replace font names in 42-repl-global.conf"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            replacements_made = 0
            
            def replace_assign(match):
                nonlocal replacements_made
                old_font = match.group(2)
                if old_font in current_font_names and old_font not in self.ignored_fonts:
                    replacements_made += 1
                    return match.group(1) + new_font_name + match.group(3)
                return match.group(0)
            
            pattern1 = r'(<edit name="family" mode="assign">\s*<string>)([^<]+)(</string>)'
            content = re.sub(pattern1, replace_assign, content)
            
            def replace_prepend(match):
                nonlocal replacements_made
                old_font = match.group(2)
                if old_font in current_font_names and old_font not in self.ignored_fonts:
                    replacements_made += 1
                    return match.group(1) + new_font_name + match.group(3)
                return match.group(0)
            
            pattern2 = r'(<edit name="family" mode="prepend" binding="strong">\s*<string>)([^<]+)(</string>)'
            content = re.sub(pattern2, replace_prepend, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return replacements_made
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return 0
    
    def replace_font_in_fonts_conf(self, file_path, current_font_names, current_fontfiles, new_font_name, new_font_filename):
        """Replace font names and filename in fonts.conf"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            font_replacements = 0
            file_replacements = 0
            
            def replace_append(match):
                nonlocal font_replacements
                old_font = match.group(2)
                if old_font in current_font_names and old_font not in self.ignored_fonts:
                    font_replacements += 1
                    return match.group(1) + new_font_name + match.group(3)
                return match.group(0)
            
            pattern1 = r'(<edit name="family" mode="append" binding="strong">\s*<string>)([^<]+)(</string>)'
            content = re.sub(pattern1, replace_append, content)
            
            # Replace custom font files in fontpattern
            for old_fontfile in current_fontfiles:
                old_pattern = f'<fontpattern>{old_fontfile}</fontpattern>'
                new_pattern = f'<fontpattern>{new_font_filename}</fontpattern>'
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    file_replacements += 1

            # Replace fontpattern entries that are font names
            try:
                fontpattern_entries = re.findall(r'(<fontpattern>)([^<]+)(</fontpattern>)', content)
                name_replacements = 0
                current_names_set = set(current_font_names)
                for full_open, fname, full_close in fontpattern_entries:
                    if fname in current_names_set and fname not in self.ignored_fonts:
                        old_pattern = f'{full_open}{fname}{full_close}'
                        new_pattern = f'{full_open}{new_font_name}{full_close}'
                        if old_pattern in content:
                            content = content.replace(old_pattern, new_pattern)
                            name_replacements += 1
                if name_replacements:
                    font_replacements += name_replacements
            except Exception as e:
                print(f"Warning: Could not replace font name patterns: {e}")

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return font_replacements, file_replacements
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return 0, 0
    
    def clean_cs2_fonts(self, cs2_fonts_dir):
        """Remove old custom fonts from CS2 directory that match fonts in /fonts/ directory"""
        try:
            if not cs2_fonts_dir.exists():
                return 0
                
            removed_count = 0
            
            # Get list of fonts in our /fonts/ directory
            our_fonts = set()
            for pattern in ["*.ttf", "*.TTF", "*.otf", "*.OTF"]:
                for font_file in self.fonts_dir.glob(pattern):
                    our_fonts.add(font_file.name.lower())
            
            # Remove matching fonts from CS2 directory (except system fonts)
            for pattern in ["*.ttf", "*.TTF", "*.otf", "*.OTF"]:
                for cs2_font in cs2_fonts_dir.glob(pattern):
                    # Skip system fonts like stratum2.uifont
                    if cs2_font.suffix.lower() == '.uifont':
                        continue
                        
                    if cs2_font.name.lower() in our_fonts:
                        try:
                            self.remove_readonly(cs2_font)
                            cs2_font.unlink()
                            removed_count += 1
                            print(f"Removed old font from CS2: {cs2_font.name}")
                        except Exception as e:
                            print(f"Warning: Could not remove {cs2_font.name}: {e}")
            
            return removed_count
        except Exception as e:
            print(f"Error during CS2 font cleanup: {e}")
            return 0
    
    def restore_defaults(self, setup_dir):
        """Restore CS2 to default fonts by copying original backups from setup directory"""
        if not self.cs2_path:
            raise Exception("CS2 path not set")
            
        # Get CS2 paths based on directory structure
        fonts_conf_path, repl_global_path, cs2_fonts_dir = self.get_cs2_paths()
        
        # Define backup paths from setup directory
        setup_dir = Path(setup_dir)
        fonts_conf_backup = setup_dir / "fonts.conf.old"
        repl_global_backup = setup_dir / "42-repl-global.conf.old"
        
        files_restored = 0
        
        # Remove current custom config files first
        for config_file in [fonts_conf_path, repl_global_path]:
            if config_file.exists():
                self.remove_readonly(config_file)
                config_file.unlink()
                print(f"Deleted custom config file: {config_file.name}")
        
        # Remove any existing .old files in CS2 directory
        fonts_conf_old = fonts_conf_path.with_suffix('.conf.old')
        repl_global_old = repl_global_path.with_suffix('.conf.old')
        
        for old_file in [fonts_conf_old, repl_global_old]:
            if old_file.exists():
                self.remove_readonly(old_file)
                old_file.unlink()
                print(f"Deleted existing .old file: {old_file.name}")
        
        # Restore fonts.conf from setup backup (without .old extension)
        if fonts_conf_backup.exists():
            fonts_conf_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fonts_conf_backup, fonts_conf_path)
            files_restored += 1
            print(f"Restored fonts.conf from setup backup")
        else:
            raise Exception("fonts.conf.old not found in setup directory")
        
        # Restore 42-repl-global.conf from setup backup (without .old extension)
        if repl_global_backup.exists():
            repl_global_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(repl_global_backup, repl_global_path)
            files_restored += 1
            print(f"Restored 42-repl-global.conf from setup backup")
        else:
            raise Exception("42-repl-global.conf.old not found in setup directory")
        
        # Handle stratum2.uifont restoration
        if (self.cs2_path / "game").exists():
            stratum_path = self.cs2_path / "game" / "csgo" / "panorama" / "fonts" / "stratum2.uifont"
        else:
            stratum_path = self.cs2_path / "csgo" / "panorama" / "fonts" / "stratum2.uifont"
            
        stratum_backup = stratum_path.with_suffix('.uifont.old')
        if stratum_backup.exists():
            if stratum_path.exists():
                self.remove_readonly(stratum_path)
                stratum_path.unlink()
            stratum_backup.rename(stratum_path)
            print("Restored stratum2.uifont from backup")
        
        # Clean up any custom font files from CS2 directory
        removed_fonts = self.clean_cs2_fonts(cs2_fonts_dir)
        if removed_fonts > 0:
            print(f"Removed {removed_fonts} custom font files from CS2 directory")
        
        # Reset first install flag
        first_install_file = setup_dir / "first_install.txt"
        try:
            with open(first_install_file, 'w', encoding='utf-8') as f:
                f.write("TRUE")
            print("Reset first install flag to TRUE")
        except Exception as e:
            print(f"Warning: Could not reset first install flag: {e}")
        
        return files_restored
    
    def apply_font_to_cs2(self, font_name, font_filename, font_path):
        """Apply font to CS2 configuration"""
        if not self.cs2_path:
            raise Exception("CS2 path not set")
            
        # Get CS2 paths based on directory structure
        fonts_conf_path, repl_global_path, cs2_fonts_dir = self.get_cs2_paths()
        
        # Ensure directories exist
        fonts_conf_path.parent.mkdir(parents=True, exist_ok=True)
        repl_global_path.parent.mkdir(parents=True, exist_ok=True)
        cs2_fonts_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean up old fonts from CS2 directory before applying new one
        removed_count = self.clean_cs2_fonts(cs2_fonts_dir)
        if removed_count > 0:
            print(f"Cleaned up {removed_count} old font files from CS2 directory")
        
        # Copy font file to CS2 fonts directory
        dest_font_path = cs2_fonts_dir / font_filename
        if dest_font_path.exists():
            self.remove_readonly(dest_font_path)
            dest_font_path.unlink()
        shutil.copy2(font_path, dest_font_path)
        print(f"Copied font file to CS2: {font_filename}")
        
        # Update extension pattern in fonts.conf if needed
        font_extension = font_path.suffix.lower()
        try:
            if fonts_conf_path.exists():
                with open(fonts_conf_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                extension_updated = False
                if font_extension == '.otf' and '<fontpattern>.ttf</fontpattern>' in content:
                    content = content.replace('<fontpattern>.ttf</fontpattern>', '<fontpattern>.otf</fontpattern>')
                    extension_updated = True
                elif font_extension == '.ttf' and '<fontpattern>.otf</fontpattern>' in content:
                    content = content.replace('<fontpattern>.otf</fontpattern>', '<fontpattern>.ttf</fontpattern>')
                    extension_updated = True
                
                if extension_updated:
                    self.remove_readonly(fonts_conf_path)
                    with open(fonts_conf_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated font extension pattern: {font_extension}")
                    
        except Exception as e:
            print(f"Warning: Could not update extension pattern: {e}")
        
        # Get current configuration for replacement
        current_font_names, current_fontfiles = self.analyze_current_fonts(fonts_conf_path, repl_global_path)
        
        # Update configuration files
        try:
            # Remove read-only attributes
            self.remove_readonly(fonts_conf_path)
            self.remove_readonly(repl_global_path)
            
            # Update files
            repl_replacements = self.replace_font_in_repl_global(repl_global_path, current_font_names, font_name)
            font_replacements, file_replacements = self.replace_font_in_fonts_conf(
                fonts_conf_path, current_font_names, current_fontfiles, font_name, font_filename
            )
            
            # Set files as read-only to prevent CS2 from overwriting them
            self.set_readonly(fonts_conf_path)
            self.set_readonly(repl_global_path)
            
            print(f"Font configuration updated:")
            print(f"  - 42-repl-global.conf: {repl_replacements} replacements")
            print(f"  - fonts.conf: {font_replacements} font names, {file_replacements} file patterns")
            
        except Exception as e:
            raise Exception(f"Failed to update font configuration: {e}")
        """Apply font to CS2 configuration"""
        if not self.cs2_path:
            raise Exception("CS2 path not set")
            
        # Get CS2 paths based on directory structure
        fonts_conf_path, repl_global_path, cs2_fonts_dir = self.get_cs2_paths()
        
        # Ensure directories exist
        fonts_conf_path.parent.mkdir(parents=True, exist_ok=True)
        repl_global_path.parent.mkdir(parents=True, exist_ok=True)
        cs2_fonts_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean up old fonts from CS2 directory before applying new one
        removed_count = self.clean_cs2_fonts(cs2_fonts_dir)
        if removed_count > 0:
            print(f"Cleaned up {removed_count} old font files from CS2 directory")
        
        # Copy font file to CS2 fonts directory
        dest_font_path = cs2_fonts_dir / font_filename
        if dest_font_path.exists():
            self.remove_readonly(dest_font_path)
            dest_font_path.unlink()
        shutil.copy2(font_path, dest_font_path)
        print(f"Copied font file to CS2: {font_filename}")
        
        # Update extension pattern in fonts.conf if needed
        font_extension = font_path.suffix.lower()
        try:
            if fonts_conf_path.exists():
                with open(fonts_conf_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                extension_updated = False
                if font_extension == '.otf' and '<fontpattern>.ttf</fontpattern>' in content:
                    content = content.replace('<fontpattern>.ttf</fontpattern>', '<fontpattern>.otf</fontpattern>')
                    extension_updated = True
                elif font_extension == '.ttf' and '<fontpattern>.otf</fontpattern>' in content:
                    content = content.replace('<fontpattern>.otf</fontpattern>', '<fontpattern>.ttf</fontpattern>')
                    extension_updated = True
                
                if extension_updated:
                    self.remove_readonly(fonts_conf_path)
                    with open(fonts_conf_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated font extension pattern: {font_extension}")
                    
        except Exception as e:
            print(f"Warning: Could not update extension pattern: {e}")
        
        # Get current configuration for replacement
        current_font_names, current_fontfiles = self.analyze_current_fonts(fonts_conf_path, repl_global_path)
        
        # Update configuration files
        try:
            # Remove read-only attributes
            self.remove_readonly(fonts_conf_path)
            self.remove_readonly(repl_global_path)
            
            # Update files
            repl_replacements = self.replace_font_in_repl_global(repl_global_path, current_font_names, font_name)
            font_replacements, file_replacements = self.replace_font_in_fonts_conf(
                fonts_conf_path, current_font_names, current_fontfiles, font_name, font_filename
            )
            
            # Set files as read-only to prevent CS2 from overwriting them
            self.set_readonly(fonts_conf_path)
            self.set_readonly(repl_global_path)
            
            print(f"Font configuration updated:")
            print(f"  - 42-repl-global.conf: {repl_replacements} replacements")
            print(f"  - fonts.conf: {font_replacements} font names, {file_replacements} file patterns")
            
        except Exception as e:
            raise Exception(f"Failed to update font configuration: {e}")


if __name__ == "__main__":
    # Test the font manager functionality
    test_app_dir = Path("./test_app_dir")
    test_cs2_path = Path("./test_cs2")
    
    font_manager = FontManager(test_app_dir, test_cs2_path)
    print(f"FontManager initialized with app_dir: {test_app_dir}, cs2_path: {test_cs2_path}")
    
    # Test path resolution
    try:
        paths = font_manager.get_cs2_paths()
        print(f"CS2 paths: {paths}")
    except Exception as e:
        print(f"Error getting CS2 paths: {e}")