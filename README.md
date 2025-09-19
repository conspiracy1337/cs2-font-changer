# CS2 Font Changer v1.0

A modern, modular GUI application for changing fonts in Counter-Strike 2. This tool provides automatic CS2 path detection, built-in font browser, and comprehensive font management with a default high-quality font included.

## Features

- **Default Font Included**: Ships with Asimovian-Regular font for immediate use
- **Automatic CS2 Detection**: Automatically finds your CS2 installation path
- **Font Browser**: Built-in web browser with ad-blocking for downloading fonts
- **Font Preview**: Live preview of selected fonts in the interface
- **Modern GUI**: Dark theme with improved usability and custom application icon
- **Smart Font Management**: Organize fonts across different directories with status indicators
- **Backup System**: Automatic backup and restoration of original font configurations
- **Auto-Selection**: Downloaded fonts are automatically selected for immediate application

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
├── icon.png                # Application icon (moved to assets on first run)
├── Asimovian-Regular.ttf   # Default font (moved to assets on first run)
└── stratum2.uifont         # CS2 default font backup (moved to setup on first run)

AppData/Roaming/cns/cs2-font-changer/
├── dl/                     # Downloaded fonts directory
├── auto/                   # Auto-processed fonts directory
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

## Module Responsibilities

### main.py
- Application entry point and startup logic
- Asset management (icon, default font, stratum backup)
- First install workflow coordination

### gui.py
- Main GUI interface and user interactions
- ModernButton class for styled buttons
- Font selection with status indicators and preview functionality
- Application workflow management with auto-selection of downloaded fonts

### font.py
- FontManager class with core font swapping logic
- Font metadata reading and processing
- Configuration file updates and currently installed font detection

### browser.py
- Web browser component with ad-blocking
- Font download management with persistent status
- Cookie auto-acceptance and Google Fonts default
- Multiple font site integration

### setup.py
- Automatic CS2 path detection
- First install logic and file processing
- Directory structure creation with asset management
- Application initialization with default font installation

### files.py
- Template creation for all .conf and .old files
- Preserves original formatting and content

## Installation

### Requirements

```bash
pip install fonttools PyQt5 requests
```

Optional for browser functionality:
```bash
pip install PyQtWebEngine
```

### Setup

1. Ensure you have the following files in your project directory:
   - `main.py`, `gui.py`, `font.py`, `browser.py`, `setup.py`, `files.py`
   - `icon.png` (application icon)
   - `Asimovian-Regular.ttf` (default font)
   - `stratum2.uifont` (CS2 default font backup)

2. Run the application:

```bash
python main.py
```

### First Time Setup

On first launch, the application will:

1. **Auto-detect CS2 Path**: Automatically search for your CS2 installation
2. **Create Directory Structure**: Set up all required folders in `AppData/Roaming/cns/cs2-font-changer/`
3. **Move Assets**: Transfer icon, default font, and backup files to appropriate directories
4. **Generate Configuration Files**: Create necessary `.conf` and backup files
5. **Install Default Font**: Automatically apply Asimovian-Regular as the default font
6. **Initialize Settings**: Set up first install flag and basic configuration

If auto-detection fails, you'll be prompted to manually select your CS2 installation directory.

## Usage

### Main Interface

The application features a clean, modern interface with:

- **CS2 Path Configuration**: Set your CS2 installation directory
- **Font Browser**: Access built-in browser for downloading fonts (Google Fonts default)
- **Font Selection**: Choose fonts from available directories with status indicators
- **Font Preview**: See selected fonts applied to the interface title
- **Action Buttons**: Apply fonts, restore defaults, open font folder

### Font Status Indicators

- **✅ [installed]**: Currently installed font in CS2 (always first in list)
- **⭐ [assets]**: Default Asimovian font (always second if not installed)
- **⚡ [auto]**: Fonts in auto-processing directory
- **📁 [fonts]**: Active fonts ready for application
- **📥 [dl]**: Recently downloaded fonts

### Font Management Workflow

1. **Download Fonts**:
   - Click "Open Font Browser" to access the built-in browser
   - Navigate to font websites (Google Fonts, DaFont, FontGet, 1001Fonts, etc.)
   - Download fonts directly to the `/dl/` directory
   - Downloaded fonts are automatically selected in the font list

2. **Organize Fonts**:
   - **Assets Directory**: Contains the default Asimovian font and application icon
   - **Auto Directory**: Place a font here for automatic processing
   - **Fonts Directory**: Active fonts ready for application to CS2
   - **Downloads Directory**: Recently downloaded fonts

3. **Apply Fonts**:
   - Select a font from the dropdown menu (with status indicators)
   - Click "Apply Selected Font"
   - Fonts are automatically copied to the active fonts directory
   - Configuration files are updated with proper font references

4. **Font Preview**:
   - Selected fonts automatically preview in the application title
   - See how fonts will look before applying to CS2
   - Default Asimovian font used when no selection

### Directory Behavior

- **Assets Directory**: Contains application resources (icon, default font)
- **Auto Directory**: Fonts placed here are processed automatically and moved to fonts directory
- **Downloads Directory**: Temporary storage for downloaded fonts with auto-selection
- **Fonts Directory**: Active fonts available for application to CS2

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
- **Cookie Auto-Accept**: Automatically accepts cookie consent dialogs
- **Download Management**: Handles font file downloads to the correct directory
- **Persistent Status**: Download status remains until new URL or download
- **Google Fonts Default**: Opens to Google Fonts by default

### Supported Font Sites

- **Google Fonts** (default, first in menu)
- DaFont
- FontGet  
- 1001 Fonts
- Font Squirrel

## Configuration Files

### fonts.conf
Main font configuration file with:
- Font directory mappings
- Font pattern definitions
- Custom font replacements
- Size adjustments and fallbacks

### 42-repl-global.conf
Global font replacement configuration:
- System font replacements
- Font family mappings
- Priority font selections

### Template System

Configuration files use placeholder templates:
- `FONTNAME`: Replaced with selected font's internal name
- `FONTFILENAME`: Replaced with selected font's filename

## Technical Details

### Asset Management

1. **Icon Handling**: Application icon moved from work directory to `/assets/` on first run
2. **Default Font**: Asimovian-Regular.ttf moved to `/assets/` and automatically installed
3. **Backup Management**: stratum2.uifont moved to `/setup/` for restoration purposes

### Font Processing

1. **Font Extraction**: .ttf/.otf fonts are extracted from ZIP archives
2. **Metadata Reading**: Font internal names are read using fontTools
3. **Configuration Updates**: Both font configuration files are updated
4. **File Management**: Font files are copied to CS2 fonts directory
5. **Permission Handling**: Read-only attributes are managed automatically
6. **Status Detection**: Currently installed fonts are detected and displayed

### Path Detection

The application uses multiple methods to find CS2:

1. **Steam Registry**: Windows registry entries for Steam installation
2. **Common Locations**: Standard Steam installation directories
3. **Library Folders**: Steam library configuration parsing
4. **Manual Selection**: Fallback to user directory selection

### Font Restoration Logic

Enhanced stratum2.uifont restoration:
1. **Check CS2 Directory**: Look for `.uifont.old` backup in CS2 directory first
2. **Rename Backup**: If found, rename to `stratum2.uifont` (original CS2 method)
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
- Ensure Asimovian-Regular.ttf is in work directory on first run
- Check `/assets/` directory contains the default font
- Verify font file is not corrupted

### File Locations

All application data is stored in:
```
%APPDATA%\cns\cs2-font-changer\
```

You can access this folder using the "Open Data Folder" button in the application.

## Development

### Module Structure

- **main.py**: Entry point, asset management, program startup
- **gui.py**: Main GUI, event handling, font preview
- **font.py**: Font management logic, FontManager class
- **browser.py**: Web browser, download manager, ad blocker
- **setup.py**: Path detection, first install logic, asset handling
- **files.py**: CS2 .conf file and backup generation

### Adding Font Sites

To add new font sites to the browser:

1. Edit `browser.py`
2. Add site to the `sites` list in `create_font_sites_menu()`
3. Update cookie selectors if needed for auto-acceptance

## Version History

### v1.0
- Initial release with complete modular architecture
- Default Asimovian font included
- Enhanced font status indicators and auto-selection
- Google Fonts as default browser site
- Persistent browser download status
- Application icon and asset management
- Improved stratum2.uifont restoration logic

## License

This project is open source. See the original CS2 Font Changer project for license details.

## Contributing

Contributions are welcome! Please ensure:
- Code follows the modular structure
- Error handling is comprehensive
- Documentation is updated for new features
- Asset management is properly handled

## Support

For issues and support:
- Check the troubleshooting section
- Verify CS2 path and permissions
- Ensure all dependencies are installed
- Test with different font formats
- Check that required assets are present

---

**CS2 Font Changer v1.0** - Modern font management for Counter-Strike 2 with default high-quality font included