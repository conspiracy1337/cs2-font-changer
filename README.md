# CS2 Font Changer v1.0

A modern GUI application for changing fonts in Counter-Strike 2. This tool provides automatic CS2 path detection, built-in font browser, and comprehensive font management with a high-quality font included.

<img width="1102" height="982" alt="image" src="https://github.com/user-attachments/assets/55f9088e-c291-4257-988a-fc13afe8a9f9" />


## Features

- **Default Font Included**: Ships with Asimovian-Regular font for immediate use
- **Automatic CS2 Detection**: Automatically finds your CS2 installation path
- **Font Browser**: Built-in web browser with ad-blocking for downloading fonts
- **Font Preview**: Live preview of selected fonts in the interface
- **Modern GUI**: Dark theme with improved usability
- **Font Deletion**: Delete fonts with confirmation and automatic CS2 cleanup
- **Backup System**: Automatic backup and restoration of original font configurations

## Project Structure

The application has been structured into the following modules:

```
cs2-font-changer/
├── main.py                 # Application entry point
├── gui.py                  # Main GUI interface
├── font.py                 # Font Management logic
├── browser.py              # Font browser component
├── setup.py                # Setup, path detection, and first install logic
├── files.py                # Configuration file templates
├── updater.py              # Automatic Update scanning
└── assets/                 # Application assets (moved to appdata on first run)
    ├── icon.png            # Application icon
    ├── Asimovian-Regular.ttf # Default font
    └── stratum2.uifont     # CS2 default font backup

AppData/Roaming/cns/cs2-font-changer/
├── dl/                     # Downloaded fonts directory
├── fonts/                  # Active fonts directory
├── assets/                 # Application assets (icon, default font)
│   ├── icon.png            # Application icon
│   └── Asimovian-Regular.ttf # Default font
└── setup/                  # Configuration and setup files
    ├── path.txt            # CS2 installation path
    ├── first_install.txt   # First install flag (TRUE/FALSE)
    ├── fonts.conf          # Font configuration template
    ├── fonts.conf.old      # Original font configuration backup
    ├── 42-repl-global.conf # Global font replacement template
    ├── 42-repl-global.conf.old # Original global replacement backup
    └── stratum2.uifont     # CS2 default font backup
```

## Modules

### main.py
- Application entry point and startup logic

### gui.py
- Main GUI interface and user interactions
- Font selection with status indicators and preview functionality
- Font deletion with confirmation dialogs

### font.py
- FontManager class with core font swapping logic
- Font metadata reading and processing
- Configuration file updates and currently installed font detection

### browser.py
- Web browser component with ad-blocking
- Font download management
- Targeted cookie auto-acceptance for font sites

### setup.py
- Automatic CS2 path detection
- First install logic and file processing
- Directory structure creation with asset management
- Application initialization with default font installation

### files.py
- Template creation for all .conf files
- Preserved original formatting and content

### updater.py
- Automatically checks for new releases on GitHub
- Asks User to update

## Installation

### Requirements

```bash
pip install fonttools PyQt5
```

Optional for browser functionality:
```bash
pip install PyQtWebEngine
```

### Setup

1. Ensure you have the following files in your project directory:
   - `main.py`, `gui.py`, `font.py`, `browser.py`, `setup.py`, `files.py`, `updater.py`
   - `assets/icon.png` (application icon)
   - `assets/Asimovian-Regular.ttf` (custom font)
   - `assets/stratum2.uifont` (CS2 default font backup)

2. Run the application:

```bash
python main.py
```

### Building a .exe file

To create a standalone executable (.exe) for CS2FontChanger follow these instructions:

#### Build Files

Ensure you have these build files in your project directory:

1. **CS2FontChanger.spec** - PyInstaller specification file
2. **build_exe.bat** - Automated build script  
3. **version_info.txt** - Windows executable metadata (optional)

#### Build Process

**Option 1: Using the build script (recommended)**

Simply double-click or run:
```bash
build_exe.bat
```

**Option 2: Manual build**

Build with PyInstaller
```bash
pyinstaller CS2FontChanger.spec
```

#### Output

The executable will be created at:
```
dist/CS2FontChanger.exe
```

This is a standalone executable (~110MB) that includes all dependencies and can run on systems without Python installed.

### First Time Setup

On first launch, the application will:

1. **Auto-detect CS2 Path**: Automatically search for your CS2 installation
2. **Create Directory Structure**: Set up all required folders in `AppData/Roaming/cns/cs2-font-changer/`
3. **Move Assets**: Transfer icon, default font, and backup files to appropriate directories
4. **Generate Configuration Files**: Create necessary `.conf` and backup files
5. **Install Default Font**: Automatically apply Asimovian-Regular as the custom font
6. **Initialize Settings**: Set up first install flag and basic configuration

If auto-detection fails, you'll be prompted to manually select your CS2 installation directory.

## Usage

### Main Interface

The application features a clean, modern interface with:

- **CS2 Path Configuration**: Set your CS2 installation directory with buttons
- **Font Browser**: Access built-in browser for downloading fonts
- **Font Selection**: Choose fonts from available directories
- **Font Preview**: See selected fonts applied to the interface title
- **Font Management**: Apply, delete, and restore fonts with dedicated buttons
- **Activity Logs**: Real-time logging of all operations with clear functionality

### Font Status Indicators

- **✅ [installed]**: Currently installed font in CS2 with filename (always first in list)
- **⭐ [assets]**: Asimovian custom font from assets directory
- **📁 [fonts]**: Active fonts ready for application
- **📥 [dl]**: Recently downloaded fonts

### Font Management Workflow

1. **Download Fonts**:
   - Click "Open Font Browser" to access the built-in browser
   - Navigate to font websites (Google Fonts, DaFont, FontGet, 1001Fonts, etc.)
   - Download fonts directly to the `/dl/` directory
   - Downloaded fonts are automatically selected in the font list

2. **Apply Fonts**:
   - Select a font from the dropdown menu
   - Click "Apply Selected Font"
   - Fonts are automatically copied to the active fonts directory
   - Configuration files are updated with proper font references

3. **Delete Fonts**:
   - Select any font (except protected Asimovian)
   - Click the trashbin button to delete with confirmation
   - Installed fonts are removed from CS2 and reverted to Asimovian
   - Duplicate prevention ensures clean font management

4. **Font Preview**:
   - Selected fonts automatically preview in the application title
   - See how fonts will look before applying to CS2
   - Asimovian custom font used when no selection was made

### Restore Defaults

The "Restore Defaults" button will:
- Restore original CS2 font configuration files
- Handle stratum2.uifont restoration (from CS2 backup or setup directory)
- Remove custom font references
- Clean up backup files
- Reset to default CS2 fonts and close application

## Browser Features

The built-in browser includes:

- **Ad Blocking**: Automatically blocks common advertisement domains and patterns
- **Targeted Cookie Auto-Accept**: Automatically accepts cookie consent dialogs on font sites
- **Download Management**: Handles font file downloads to the correct directory

### Supported Font Sites

- Google Fonts
- DaFont
- FontGet  
- 1001 Fonts
- Font Squirrel

## Technical Details

### Font Processing

1. **Font Extraction**: .ttf/.otf fonts are extracted from ZIP archives
2. **Metadata Reading**: Font internal names are read using fontTools
3. **Configuration Updates**: Both font configuration files are updated
4. **File Management**: Font files are copied to CS2 fonts directory
5. **Permission Handling**: Read-only attributes are managed automatically
6. **Status Detection**: Currently installed fonts are detected and displayed
7. **Duplicate Prevention**: Smart filtering prevents duplicate entries

### Path Detection

The application uses multiple methods to find CS2:

1. **Steam Registry**: Windows registry entries for Steam installation
2. **Common Locations**: Standard Steam installation directories
3. **Library Folders**: Steam library configuration parsing
4. **Manual Selection**: Fallback to user directory selection

### Font Restoration Logic

Enhanced stratum2.uifont restoration:
1. **Check CS2 Directory**: Look for `.uifont.old` backup in CS2 directory first
2. **Rename Backup**: If found, rename to `stratum2.uifont`
3. **Setup Fallback**: If no CS2 backup, copy from `/setup/` directory
4. **Clean Restoration**: Ensures complete restoration of original font

## Troubleshooting

### Common Issues

**CS2 Path Not Found**:
- Ensure CS2 is installed via Steam
- Try manual path selection via Browse button
- Check that CS2 is in a standard Steam library location

**Permission Denied**:
- Close CS2 completely before applying fonts
- Run application as Administrator if needed

**Font Not Applying**:
- Restart CS2 after applying fonts
- Verify font file is valid .ttf/.otf format
- Check that CS2 path is correctly set

**Browser Not Working**:
- Install PyQtWebEngine: `pip install PyQtWebEngine`
- Check internet connection
- Fonts can still be manually placed in directories

**Default Font Issues**:
- Ensure assets folder contains Asimovian-Regular.ttf
- Check `/assets/` directory in both work and appdata locations
- Verify font file is not corrupted

### File Locations

All application data is stored in:
```
%APPDATA%\cns\cs2-font-changer\
```

You can access this folder using the "Open Data Folder" button in the application.

## Development

### Adding Font Sites

To add new font sites to the browser:

1. Edit `browser.py`
2. Add site to the `sites` list in `create_font_sites_menu()`
3. Update cookie selectors in `auto_accept_cookies()` if needed

## License

This project is open source. See the original CS2 Font Changer project for license details.

## Contributing

Contributions are welcome! Please ensure:
- Code follows the modular structure
- Error handling is comprehensive
- Documentation is updated for new features
- Asset management is properly handled
- UI consistency is maintained

## Support

For issues and support:
- Check the troubleshooting section
- Verify CS2 path and permissions
- Ensure all dependencies are installed
- Test with different font formats
- Check that required assets are present in assets/ folder

---

**CS2 Font Changer v1.0** - Modern font management for Counter-Strike 2 with comprehensive font deletion and management capabilities