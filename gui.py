"""
CS2 Font Changer - Main GUI Interface
Contains the primary user interface components
"""

import os
import re
import shutil
import zipfile
import sys
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from browser import BrowserWindow
from font import FontManager


class ModernButton(QPushButton):
    """Custom modern button with hover effects"""
    def __init__(self, text, icon=None, button_type="normal", size="normal"):
        super().__init__(text)
        self.button_type = button_type
        self.size = size
        self.setup_style()
        
    def setup_style(self):
        padding = "15px 30px" if self.size == "large" else ("12px 24px" if self.size == "medium" else "8px 16px")
        font_size = "16px" if self.size == "large" else ("14px" if self.size == "medium" else "12px")
        
        if self.button_type == "primary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0d7377, stop:1 #14a085);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: {padding};
                    font-size: {font_size};
                    font-weight: bold;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #14a085, stop:1 #0d7377);
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    background: #0a5d61;
                }}
            """)
        elif self.button_type == "success":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #27ae60, stop:1 #2ecc71);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: {padding};
                    font-size: {font_size};
                    font-weight: bold;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2ecc71, stop:1 #27ae60);
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    background: #229954;
                }}
            """)
        elif self.button_type == "danger":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e74c3c, stop:1 #c0392b);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: {padding};
                    font-size: {font_size};
                    font-weight: bold;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #c0392b, stop:1 #e74c3c);
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    background: #a93226;
                }}
            """)
        else:  # normal
            self.setStyleSheet(f"""
                QPushButton {{
                    background: #4e4e4e;
                    color: white;
                    border: 1px solid #666666;
                    border-radius: 6px;
                    padding: {padding};
                    font-size: {font_size};
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background: #5e5e5e;
                    border-color: #777777;
                }}
                QPushButton:pressed {{
                    background: #3e3e3e;
                }}
            """)


class CS2FontChangerGUI(QMainWindow):
    def __init__(self, app_dir):
        super().__init__()
        self.setWindowTitle("CS2 Font Changer v1.0 by cns")
        self.setMinimumSize(1000, 950)
        self.resize(1100, 950)
        
        # Initialize paths
        self.app_dir = Path(app_dir)
        self.dl_dir = self.app_dir / "dl"
        self.fonts_dir = self.app_dir / "fonts"
        self.setup_dir = self.app_dir / "setup"
        self.assets_dir = self.app_dir / "assets"
        
        # Variables
        self.cs2_path = None
        self.browser_window = None
        self.font_manager = None
        self.default_font_family = None
        
        # Set application icon
        self.setup_app_icon()
        
        self.setup_ui()
        self.setup_style()
        self.load_cs2_path()
        
        # Load default font (Asimovian)
        self.load_default_font()
        
        # Initial font list refresh
        self.refresh_font_list()
        
    def setup_app_icon(self):
        """Setup application icon from assets directory"""
        try:
            icon_path = self.assets_dir / "icon.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            print(f"Warning: Could not set application icon: {e}")
        
    def closeEvent(self, event):
        """Handle main window close event - terminate entire application"""
        try:
            # Close browser window if it exists
            if self.browser_window and self.browser_window.isVisible():
                self.browser_window.close()
                self.browser_window = None
            
            # Accept the close event and quit the application
            event.accept()
            QApplication.quit()
        except Exception as e:
            print(f"Error during application shutdown: {e}")
            event.accept()
            QApplication.quit()
        
    def closeEvent(self, event):
        """Handle main window close event - terminate entire application"""
        try:
            # Close browser window if it exists
            if self.browser_window and self.browser_window.isVisible():
                self.browser_window.close()
                self.browser_window = None
            
            # Accept the close event and quit the application
            event.accept()
            QApplication.quit()
        except Exception as e:
            print(f"Error during application shutdown: {e}")
            event.accept()
            QApplication.quit()
        """Setup application icon from assets directory"""
        try:
            icon_path = self.assets_dir / "icon.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            print(f"Warning: Could not set application icon: {e}")
        
    def load_default_font(self):
        """Load the default Asimovian font from assets"""
        try:
            asimovian_path = self.assets_dir / "Asimovian-Regular.ttf"
            if asimovian_path.exists():
                font_id = QFontDatabase.addApplicationFont(str(asimovian_path))
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        self.default_font_family = font_families[0]
                        print(f"Loaded default font: {self.default_font_family}")
                        # Apply to title immediately
                        self.update_title_font()
        except Exception as e:
            print(f"Warning: Could not load default font: {e}")
            
    def update_title_font(self, custom_font=None):
        """Update title with specified font or default"""
        font_family = custom_font or self.default_font_family or "Arial"
        
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: #ffffff;
                font-size: 44px;
                font-weight: bold;
                font-family: "{font_family}";
                margin: 2px;  /* Reduced from 5px */
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0d7377, stop:0.5 #14a085, stop:1 #0d7377);
                -webkit-background-clip: text;
                padding: 10px 15px;  /* Reduced vertical padding from 15px to 10px */
            }}
        """)
        
        self.preview_label.setStyleSheet(f"""
            QLabel {{
                color: #b0b0b0;
                font-size: 18px;
                font-family: "{font_family}";
                margin: 5px;
                padding: 10px;
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
            }}
            QLabel a {{
                color: #b0b0b0;
                text-decoration: none;
                font-family: "{font_family}";
            }}
            QLabel a:hover {{
                color: #14a085;
                text-decoration: underline;
            }}
        """)
        
    def setup_ui(self):
        """Setup the main UI with better proportions"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with better spacing
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Title section
        title_widget = self.create_title_section()
        layout.addWidget(title_widget)
        
        # CS2 Path section
        path_widget = self.create_path_section()
        layout.addWidget(path_widget)
        
        # Main content grid
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Left panel (controls) - 40% width
        left_panel = self.create_left_panel()
        left_panel.setMaximumWidth(400)
        left_panel.setMinimumWidth(350)
        content_layout.addWidget(left_panel)
        
        # Right panel (status) - 60% width
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 1)  # stretch factor 1
        
        layout.addLayout(content_layout, 1)  # stretch factor 1
        
        # Status bar
        self.statusBar().showMessage("Ready - CS2 Font Changer loaded")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #1e1e1e);
                color: #b0b0b0;
                border-top: 2px solid #0d7377;
                padding: 8px 15px;
                font-size: 12px;
            }
        """)
        
    def create_title_section(self):
        """Create the title section with better spacing and font preview"""
        widget = QWidget()
        widget.setMaximumHeight(160)  # Increased from 160
        widget.setMinimumHeight(160)  # Increased from 160
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 10, 0, 10)
        
        self.title_label = QLabel("CS2 Font Changer")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setMinimumHeight(80)  # Increased from 80
        self.title_label.setMaximumHeight(80)  # Increased from 80
        
        # Clickable GitHub link
        self.preview_label = QLabel('<a href="https://github.com/conspiracy1337/cs2-font-changer" style="color: #b0b0b0; text-decoration: none;">github.com/conspiracy1337/cs2-font-changer</a>')
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(60)
        self.preview_label.setMaximumHeight(60)
        self.preview_label.setOpenExternalLinks(True)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.preview_label)
        return widget
        
    def create_path_section(self):
        """Create CS2 path section with better proportions"""
        group = QGroupBox("CS2 Installation Path")
        group.setMaximumHeight(100)
        layout = QHBoxLayout(group)
        layout.setSpacing(15)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select your CS2 installation directory...")
        self.path_edit.setMinimumHeight(40)
        self.path_edit.returnPressed.connect(self.save_path_from_textbox)  # Save on Enter
        
        browse_btn = ModernButton("Browse", button_type="normal", size="medium")
        browse_btn.setMinimumWidth(120)
        browse_btn.setMaximumWidth(120)
        browse_btn.clicked.connect(self.browse_cs2_path)
        
        open_btn = ModernButton("Open", button_type="normal", size="medium")
        open_btn.setMinimumWidth(120)
        open_btn.setMaximumWidth(120)
        open_btn.clicked.connect(self.open_cs2_path)
        
        layout.addWidget(self.path_edit, 1)
        layout.addWidget(browse_btn)
        layout.addWidget(open_btn)
        
        return group
        
    def create_left_panel(self):
        """Create the left control panel with better spacing"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(25)
        
        # Download section
        download_group = QGroupBox("Font Downloader")
        download_layout = QVBoxLayout(download_group)
        download_layout.setSpacing(15)
        
        self.download_btn = ModernButton("🌐 Open Font Browser", button_type="primary", size="large")
        self.download_btn.clicked.connect(self.toggle_browser)
        
        self.download_status = QLabel("Click to open font browser")
        self.download_status.setWordWrap(True)
        self.download_status.setStyleSheet("""
            QLabel {
                color: #b0b0b0; 
                font-size: 12px;
                padding: 10px;
                background: #2d2d2d;
                border-radius: 5px;
                border-left: 3px solid #0d7377;
            }
        """)
        
        download_layout.addWidget(self.download_btn)
        download_layout.addWidget(self.download_status)
        
        # Font selection section
        selection_group = QGroupBox("Font Selection")
        selection_layout = QVBoxLayout(selection_group)
        selection_layout.setSpacing(20)
        
        # Font selection
        font_section = QWidget()
        font_layout = QVBoxLayout(font_section)
        font_layout.setSpacing(10)
        
        font_label = QLabel("Select Font:")
        font_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        font_row = QHBoxLayout()
        font_row.setSpacing(10)
        
        self.font_combo = QComboBox()
        self.font_combo.setMinimumHeight(43)
        self.font_combo.setMaximumHeight(43)  # Fix height to prevent shifting
        self.font_combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.font_combo.setMinimumContentsLength(30)  # Ensure consistent width
        self.font_combo.currentTextChanged.connect(self.update_font_preview)
        self.font_combo.currentTextChanged.connect(self.update_delete_button_state)
        self.font_combo.setStyleSheet("""
            QComboBox {
                font-size: 13px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4e4e4e, stop:1 #3e3e3e);
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 12px 15px;
                color: #ffffff;
                min-height: 43px;
                max-height: 43px;
                line-height: 20px;
            }
            QComboBox:focus {
                border-color: #0d7377;
            }
            QComboBox::drop-down {
                border: none;
                width: 0px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4e4e4e, stop:1 #3e3e3e);
                color: #ffffff;
                selection-background-color: #0d7377;
                border: 2px solid #555555;
                border-radius: 5px;
                outline: none;
                max-height: 200px;
                margin: 0px;
                padding: 0px;
            }
            QComboBox QAbstractItemView::item {
                padding: 10px 12px;
                border-bottom: 1px solid #555555;
                min-height: 25px;
                height: 30px;
                margin: 0px;
                line-height: 20px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #0d7377;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #14a085;
            }
            QScrollBar:vertical {
                background: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #0d7377;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        font_row.addWidget(self.font_combo, 1)
        
        # Button column for refresh and delete
        button_column = QVBoxLayout()
        button_column.setSpacing(5)
        button_column.setAlignment(Qt.AlignVCenter)  # Center vertically
        
        refresh_btn = ModernButton("🔄", button_type="normal")
        refresh_btn.setMaximumWidth(80)
        refresh_btn.setMinimumHeight(19)  # Half of combo box height minus spacing
        refresh_btn.clicked.connect(self.refresh_font_list)
        refresh_btn.setToolTip("Refresh font list")
        
        delete_btn = ModernButton("🗑️", button_type="danger")
        delete_btn.setMaximumWidth(80)
        delete_btn.setMinimumHeight(19)  # Half of combo box height minus spacing
        delete_btn.clicked.connect(self.delete_selected_font)
        delete_btn.setToolTip("Delete selected font")
        self.delete_btn = delete_btn  # Store reference for enabling/disabling
        
        button_column.addWidget(refresh_btn)
        button_column.addWidget(delete_btn)
        
        font_row.addLayout(button_column)
        
        font_layout.addWidget(font_label)
        font_layout.addLayout(font_row)
        
        selection_layout.addWidget(font_section)
        
        # Action buttons
        action_section = QWidget()
        action_layout = QVBoxLayout(action_section)
        action_layout.setSpacing(15)
        
        self.apply_btn = ModernButton("✨ Apply Selected Font", button_type="normal", size="medium")
        self.apply_btn.setMinimumHeight(45)  # Add 1 extra pixel
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: 1px solid #1e8449;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: #2ecc71;
                border-color: #27ae60;
            }
            QPushButton:pressed {
                background: #219a52;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_selected_font)
        
        restore_btn = ModernButton("🔄 Restore Defaults", button_type="normal", size="medium")
        restore_btn.setMinimumHeight(45)  # Add 1 extra pixel
        restore_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: #ec7063;
                border-color: #e74c3c;
            }
            QPushButton:pressed {
                background: #c0392b;
            }
        """)
        restore_btn.clicked.connect(self.restore_defaults)
        
        # New folder button
        folder_btn = ModernButton("📁 Open Data Folder", button_type="normal", size="medium")
        folder_btn.setMinimumHeight(45)  # Add 1 extra pixel
        folder_btn.clicked.connect(self.open_app_folder)
        
        action_layout.addWidget(self.apply_btn)
        action_layout.addWidget(restore_btn)
        action_layout.addWidget(folder_btn)
        
        selection_layout.addWidget(action_section)
        
        # Add sections to left panel
        layout.addWidget(download_group)
        layout.addWidget(selection_group)
        layout.addStretch()
        
        return widget
        
    def create_right_panel(self):
        """Create the right panel (status logs)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Activity Logs group box
        logs_group = QGroupBox("Activity Logs")
        logs_layout = QVBoxLayout(logs_group)
        logs_layout.setSpacing(15)
        
        # Log area with better styling
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #1e1e1e);
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 10px;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.5;
                selection-background-color: #0d7377;
            }
        """)
        
        # Clear button at bottom center
        clear_btn = ModernButton("Clear", button_type="normal")
        clear_btn.setMaximumWidth(100)
        clear_btn.clicked.connect(self.clear_logs)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #666666;
                color: white;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: #777777;
                border-color: #666666;
            }
            QPushButton:pressed {
                background: #555555;
            }
        """)
        
        # Center the clear button
        clear_layout = QHBoxLayout()
        clear_layout.addStretch()
        clear_layout.addWidget(clear_btn)
        clear_layout.addStretch()
        
        logs_layout.addWidget(self.log_text, 1)
        logs_layout.addLayout(clear_layout)
        
        layout.addWidget(logs_group, 1)
        
        return widget
        
    def setup_style(self):
        """Setup the application style with improved aesthetics"""
        dark_style = """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e1e1e, stop:1 #0f0f0f);
            color: #ffffff;
        }
        
        QWidget {
            background-color: transparent;
            color: #ffffff;
        }
        
        QGroupBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3e3e3e, stop:1 #2d2d2d);
            border: 2px solid #555555;
            border-radius: 12px;
            margin-top: 15px;
            padding-top: 15px;
            font-size: 14px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 8px 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0d7377, stop:1 #14a085);
            color: white;
            border-radius: 6px;
            font-weight: bold;
        }
        
        QLineEdit {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4e4e4e, stop:1 #3e3e3e);
            border: 2px solid #555555;
            border-radius: 8px;
            padding: 12px 15px;
            font-size: 13px;
            color: #ffffff;
        }
        
        QLineEdit:focus {
            border-color: #0d7377;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5e5e5e, stop:1 #4e4e4e);
        }
        
        QLabel {
            color: #ffffff;
            font-size: 13px;
        }
        """
        
        self.setStyleSheet(dark_style)
        
    def clear_logs(self):
        """Clear the log text area"""
        self.log_text.clear()
        self.log_message("<span style='color: #3498db'>Clear</span> Logs cleared")
        
    def log_message(self, message):
        """Add a message to the log with better formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"<div style='margin: 5px 0; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 5px;'><span style='color: #666666; font-size: 11px;'>[{timestamp}]</span> {message}</div>"
        
        self.log_text.append(formatted_message)
        
        # Update status bar with last message (without HTML)
        plain_message = re.sub('<[^<]+?>', '', message)
        self.statusBar().showMessage(plain_message[:100] + "..." if len(plain_message) > 100 else plain_message)
        
        # Auto scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def load_cs2_path(self):
        """Load CS2 path from path.txt"""
        path_file = self.setup_dir / "path.txt"
        try:
            if path_file.exists():
                with open(path_file, 'r', encoding='utf-8') as f:
                    path = f.read().strip()
                if path and Path(path).exists():
                    self.path_edit.setText(path)
                    self.cs2_path = Path(path)
                    self.font_manager = FontManager(self.app_dir, self.cs2_path)
                    self.log_message(f"<span style='color: #2ecc71'>Success</span> CS2 path loaded: <code>{path}</code>")
                else:
                    self.log_message("<span style='color: #f39c12'>Warning</span> Invalid path in path.txt file")
        except Exception as e:
            self.log_message(f"<span style='color: #e74c3c'>Error</span> Error loading CS2 path: {e}")
            
    def save_path_from_textbox(self):
        """Save CS2 path when Enter is pressed in textbox"""
        path = self.path_edit.text().strip()
        if path and Path(path).exists():
            self.cs2_path = Path(path)
            self.font_manager = FontManager(self.app_dir, self.cs2_path)
            # Save to path.txt
            try:
                with open(self.setup_dir / "path.txt", 'w', encoding='utf-8') as f:
                    f.write(path)
                self.log_message(f"<span style='color: #f39c12'>Updated</span> CS2 path saved: <code>{path}</code>")
            except Exception as e:
                self.log_message(f"<span style='color: #e74c3c'>Error</span> Error saving CS2 path: {e}")
        elif path:
            self.log_message(f"<span style='color: #f39c12'>Warning</span> Invalid CS2 path: <code>{path}</code>")
        
    def open_cs2_path(self):
        """Open the CS2 directory in file explorer"""
        try:
            path = self.path_edit.text().strip()
            if not path:
                QMessageBox.warning(self, "No Path", "Please set a CS2 installation path first")
                return
                
            cs2_path = Path(path)
            if not cs2_path.exists():
                QMessageBox.warning(self, "Invalid Path", f"The specified CS2 path does not exist:\n{path}")
                return
                
            if os.name == 'nt':  # Windows
                os.startfile(str(cs2_path))
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{cs2_path}"' if sys.platform == 'darwin' else f'xdg-open "{cs2_path}"')
            self.log_message(f"<span style='color: #3498db'>Open</span> Opened CS2 directory: <code>{path}</code>")
        except Exception as e:
            self.log_message(f"<span style='color: #e74c3c'>Error</span> Could not open CS2 directory: {e}")
            
    def browse_cs2_path(self):
        """Browse for CS2 path starting from current path"""
        # Get starting directory from current path or default
        start_dir = ""
        current_path = self.path_edit.text().strip()
        if current_path and Path(current_path).exists():
            start_dir = current_path
        else:
            # Try to read from path.txt
            try:
                path_file = self.setup_dir / "path.txt"
                if path_file.exists():
                    with open(path_file, 'r', encoding='utf-8') as f:
                        saved_path = f.read().strip()
                        if saved_path and Path(saved_path).exists():
                            start_dir = saved_path
            except:
                pass
            
            # Fallback to common Steam location
            if not start_dir:
                start_dir = "C:/Program Files (x86)/Steam/steamapps/common"
        
        path = QFileDialog.getExistingDirectory(self, "Select CS2 Installation Directory", start_dir)
        if path:
            self.path_edit.setText(path)
            self.cs2_path = Path(path)
            self.font_manager = FontManager(self.app_dir, self.cs2_path)
            # Save to path.txt
            try:
                with open(self.setup_dir / "path.txt", 'w', encoding='utf-8') as f:
                    f.write(path)
                self.log_message(f"<span style='color: #f39c12'>Updated</span> CS2 path updated: <code>{path}</code>")
            except Exception as e:
                self.log_message(f"<span style='color: #e74c3c'>Error</span> Error saving CS2 path: {e}")
                
    def toggle_browser(self):
        """Toggle browser window"""
        try:
            if self.browser_window is None or not self.browser_window.isVisible():
                # Create and show browser window
                self.browser_window = BrowserWindow(self.dl_dir)
                self.browser_window.downloadCompleted.connect(self.on_download_completed)
                self.browser_window.downloadStarted.connect(self.on_download_started)
                self.browser_window.windowClosed.connect(self.on_browser_window_closed)
                self.browser_window.show()
                
                self.download_btn.setText("🔴 Close Browser")
                self.download_btn.button_type = "danger"
                self.download_btn.setup_style()
                self.download_status.setText("Browser window is open")
                self.log_message("<span style='color: #3498db'>Browser</span> Font browser window opened")
            else:
                # Close browser window
                if self.browser_window:
                    self.browser_window.close()
                    self.browser_window = None
                
                self.download_btn.setText("🌐 Open Font Browser")
                self.download_btn.button_type = "primary"
                self.download_btn.setup_style()
                self.download_status.setText("Click to open font browser")
                self.log_message("<span style='color: #e74c3c'>Closed</span> Browser window closed")
                self.refresh_font_list()
        except Exception as e:
            self.log_message(f"<span style='color: #e74c3c'>Error</span> Browser error: {e}")
            
    def on_download_started(self, filename):
        """Handle download started"""
        self.log_message(f"<span style='color: #f39c12'>Download</span> Download started: <strong>{filename}</strong>")
        
    def on_download_completed(self, file_path):
        """Handle completed download"""
        file_path = Path(file_path)
        self.log_message(f"<span style='color: #2ecc71'>Success</span> Download completed: <strong>{file_path.name}</strong>")
        
        # Process the file
        self.process_downloaded_file(file_path)
        
        # Auto-refresh font list and select the downloaded font
        self.refresh_font_list()
        
        # Try to auto-select the downloaded font
        for i in range(self.font_combo.count()):
            item_text = self.font_combo.itemText(i)
            if file_path.stem.lower() in item_text.lower():
                self.font_combo.setCurrentIndex(i)
                self.log_message(f"<span style='color: #3498db'>Auto-Select</span> Selected downloaded font: <strong>{file_path.name}</strong>")
                break
        
    def on_browser_window_closed(self):
        """Handle when browser window is closed manually"""
        self.browser_window = None
        self.download_btn.setText("🌐 Open Font Browser")
        self.download_btn.button_type = "primary"
        self.download_btn.setup_style()
        self.download_status.setText("Click to open font browser")
        self.log_message("<span style='color: #e74c3c'>Closed</span> Browser window closed manually")
        self.refresh_font_list()
        
    def process_downloaded_file(self, file_path):
        """Process a downloaded font file"""
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.zip':
                self.log_message(f"<span style='color: #f39c12'>Archive</span> Extracting ZIP archive: <strong>{file_path.name}</strong>")
                
                # Extract zip file with improved directory handling
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    extracted_fonts = 0
                    for file in zip_ref.namelist():
                        if file.lower().endswith(('.ttf', '.otf')) and not file.startswith('__MACOSX/'):
                            # Extract font file to temp location first
                            zip_ref.extract(file, self.dl_dir)
                            extracted_path = self.dl_dir / file
                            
                            # Always move to root of dl directory, flattening structure
                            final_path = self.dl_dir / Path(file).name
                            
                            # Handle file conflicts
                            counter = 1
                            original_final_path = final_path
                            while final_path.exists():
                                stem = original_final_path.stem
                                suffix = original_final_path.suffix
                                final_path = self.dl_dir / f"{stem}_{counter}{suffix}"
                                counter += 1
                            
                            # Move file to final location
                            if extracted_path != final_path:
                                shutil.move(extracted_path, final_path)
                                
                            extracted_fonts += 1
                            self.log_message(f"<span style='color: #2ecc71'>  Font</span> Extracted font: <code>{final_path.name}</code>")
                
                if extracted_fonts > 0:
                    self.log_message(f"<span style='color: #2ecc71'>Success</span> Successfully extracted <strong>{extracted_fonts}</strong> font file(s)")
                    # Remove zip file
                    file_path.unlink()
                    
                    # Clean up empty directories created during extraction
                    self.cleanup_empty_dirs(self.dl_dir)
                                
                    self.refresh_font_list()
                else:
                    self.log_message(f"<span style='color: #f39c12'>Warning</span> No font files found in <code>{file_path.name}</code>")
                    
            elif file_path.suffix.lower() in ['.ttf', '.otf']:
                self.log_message(f"<span style='color: #2ecc71'>Font</span> Font file ready: <strong>{file_path.name}</strong>")
                self.refresh_font_list()
                
        except Exception as e:
            self.log_message(f"<span style='color: #e74c3c'>Error</span> Error processing download: {e}")
            
    def cleanup_empty_dirs(self, directory):
        """Recursively remove empty directories"""
        try:
            for root, dirs, files in os.walk(directory, topdown=False):
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    try:
                        # Only remove if empty and not the main /dl/ directory
                        if dir_path != directory and not any(dir_path.iterdir()):
                            dir_path.rmdir()
                            self.log_message(f"<span style='color: #3498db'>Cleanup</span> Removed empty directory: <code>{dir_name}</code>")
                    except:
                        pass
        except Exception as e:
            self.log_message(f"<span style='color: #f39c12'>Warning</span> Warning during directory cleanup: {e}")
            
    def refresh_font_list(self):
        """Refresh the font selection dropdown with currently installed font first"""
        fonts = []
        added_files = set()  # Track added filenames to avoid duplicates
        
        # Get currently installed font from CS2
        current_installed_font = None
        current_installed_filename = None
        if self.font_manager:
            current_installed_font = self.font_manager.get_currently_installed_font()
            
            # Try to find the filename for the installed font
            if current_installed_font:
                for check_dir in [self.fonts_dir, self.assets_dir]:
                    for pattern in ["*.ttf", "*.TTF", "*.otf", "*.OTF"]:
                        for font_file in check_dir.glob(pattern):
                            if self.font_manager.get_font_internal_name(font_file) == current_installed_font:
                                current_installed_filename = font_file.name
                                added_files.add(font_file.name.lower())  # Mark as added to avoid duplicates
                                break
                        if current_installed_filename:
                            break
                    if current_installed_filename:
                        break
        
        # First, add currently installed font with checkmark and filename
        if current_installed_font and current_installed_filename:
            fonts.append(f"✅ [installed] {current_installed_filename}")
            self.log_message(f"<span style='color: #5FE3B1'>Info</span> Currently installed font: <strong>{current_installed_font}</strong>")
        
        # Second, add Asimovian font from assets (if not currently installed)
        asimovian_path = self.assets_dir / "Asimovian-Regular.ttf"
        if asimovian_path.exists():
            asimovian_name = "Asimovian-Regular.ttf"
            if asimovian_name.lower() not in added_files:
                fonts.append(f"⭐ [assets] {asimovian_name}")
                added_files.add(asimovian_name.lower())
        
        # Third, add fonts from /fonts/ directory (skip if already installed)
        if self.fonts_dir.exists():
            for pattern in ["*.ttf", "*.TTF", "*.otf", "*.OTF"]:
                for font_file in self.fonts_dir.glob(pattern):
                    if font_file.name.lower() not in added_files:
                        fonts.append(f"📁 [fonts] {font_file.name}")
                        added_files.add(font_file.name.lower())
        
        # Fourth, add fonts from /dl/ directory
        if self.dl_dir.exists():
            for pattern in ["*.ttf", "*.TTF", "*.otf", "*.OTF"]:
                for font_file in self.dl_dir.glob(pattern):
                    if font_file.name.lower() not in added_files:
                        fonts.append(f"📥 [dl] {font_file.name}")
                        added_files.add(font_file.name.lower())
        
        # Update combo box
        # Temporarily disconnect signals to prevent double preview updates
        self.font_combo.currentTextChanged.disconnect()
        
        self.font_combo.clear()
        if fonts:
            self.font_combo.addItems(fonts)
            
            # Reconnect signals
            self.font_combo.currentTextChanged.connect(self.update_font_preview)
            self.font_combo.currentTextChanged.connect(self.update_delete_button_state)
            
            # Update once after reconnecting
            self.update_font_preview()
            self.update_delete_button_state()
            
            self.log_message(f"<span style='color: #3498db'>Refresh</span> Font list refreshed - Found <strong>{len(fonts)}</strong> available fonts")
        else:
            self.font_combo.addItem("No fonts available")
            
            # Reconnect signals
            self.font_combo.currentTextChanged.connect(self.update_font_preview)
            self.font_combo.currentTextChanged.connect(self.update_delete_button_state)
            
            self.update_delete_button_state()  # Disable delete button for no fonts
            self.log_message(f"<span style='color: #f39c12'>Warning</span> No font files found in any directories")
        
    def apply_selected_font(self):
        """Apply the selected font"""
        if not self.cs2_path:
            QMessageBox.warning(self, "Path Required", "Please set your CS2 installation path first")
            return
            
        if not self.font_manager:
            QMessageBox.warning(self, "Font Manager Error", "Font manager not initialized")
            return
            
        selected = self.font_combo.currentText()
        if not selected or selected == "No fonts available":
            QMessageBox.warning(self, "Font Required", "Please select a font to apply")
            return
        
        # Check if currently installed font is selected
        if selected.startswith("✅ [installed]"):
            QMessageBox.information(self, "Already Installed", "This font is already installed in CS2.")
            return
            
        try:
            # Parse selection to determine source directory
            if selected.startswith("⭐ [assets]"):
                source_dir = self.assets_dir
                filename = selected.replace("⭐ [assets] ", "")
            elif selected.startswith("✅ [installed]"):
                source_dir = self.fonts_dir  # Installed fonts are in fonts directory
                filename = selected.replace("✅ [installed] ", "")
            elif selected.startswith("📥 [dl]"):
                source_dir = self.dl_dir
                filename = selected.replace("📥 [dl] ", "")
            else:
                source_dir = self.fonts_dir
                filename = selected.replace("📁 [fonts] ", "")
                
            font_path = source_dir / filename
            
            if not font_path.exists():
                QMessageBox.critical(self, "File Error", f"Font file not found: {filename}")
                return
            
            # If not from fonts directory, copy it there first
            if source_dir != self.fonts_dir:
                dest_path = self.fonts_dir / filename
                if dest_path.exists():
                    dest_path.unlink()
                shutil.copy2(font_path, dest_path)
                self.log_message(f"<span style='color: #3498db'>Copy</span> Font copied to /fonts/: <code>{filename}</code>")
                
                # Remove from original location (except assets)
                if source_dir != self.assets_dir:
                    try:
                        font_path.unlink()
                        self.log_message(f"<span style='color: #2ecc71'>Cleanup</span> Removed from source directory")
                        self.refresh_font_list()
                    except Exception as e:
                        self.log_message(f"<span style='color: #f39c12'>Warning</span> Could not remove from source: {e}")
                        
                font_path = dest_path
                
            # Get font internal name
            internal_name = self.font_manager.get_font_internal_name(font_path)
            if not internal_name:
                QMessageBox.critical(self, "Font Error", f"Could not read font metadata from: {filename}")
                return
                
            self.log_message(f"<span style='color: #f39c12'>Updated</span> Applying font: <strong>{internal_name}</strong> (<code>{filename}</code>)")
            
            # Apply the font using font manager
            self.font_manager.apply_font_to_cs2(internal_name, filename, font_path)
            
            self.log_message(f"<span style='color: #2ecc71'>Success</span> Font applied successfully!")
            
            # Refresh font list to update currently installed status BEFORE showing success dialog
            self.refresh_font_list()
            
            # Show success dialog last
            QMessageBox.information(self, "Success!", f"Font '{internal_name}' has been applied successfully!\n\nRestart CS2 to see the changes.")
            
        except Exception as e:
            self.log_message(f"<span style='color: #e74c3c'>Error</span> Error applying font: {e}")
            QMessageBox.critical(self, "Application Error", f"Failed to apply font:\n\n{str(e)}")
            
    def update_font_preview(self):
        """Update font preview with selected font"""
        try:
            selected = self.font_combo.currentText()
            if not selected or selected == "No fonts available":
                # Use default font if no selection
                self.update_title_font()
                return
            
            # Parse selection to get font file path
            font_path = None
            if selected.startswith("✅ [installed]"):
                # For installed font, look for the filename in fonts directory
                filename = selected.replace("✅ [installed] ", "")
                font_path = self.fonts_dir / filename
                # If not in fonts, check assets
                if not font_path.exists():
                    font_path = self.assets_dir / filename
            elif selected.startswith("⭐ [assets]"):
                filename = selected.replace("⭐ [assets] ", "")
                font_path = self.assets_dir / filename
            elif selected.startswith("📁 [fonts]"):
                filename = selected.replace("📁 [fonts] ", "")
                font_path = self.fonts_dir / filename
            elif selected.startswith("📥 [dl]"):
                filename = selected.replace("📥 [dl] ", "")
                font_path = self.dl_dir / filename
            
            if font_path and font_path.exists():
                # Load font into Qt font database
                font_id = QFontDatabase.addApplicationFont(str(font_path))
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        font_family = font_families[0]
                        self.update_title_font(font_family)
                        self.log_message(f"<span style='color: #f39c12'>Updated</span> Font preview updated: <strong>{font_family}</strong>")
                        
        except Exception as e:
            self.log_message(f"<span style='color: #f39c12'>⚠️</span> Could not update font preview: {e}")
            # Fallback to default font
            self.update_title_font()
    
    def update_delete_button_state(self):
        """Update delete button state based on selected font"""
        selected = self.font_combo.currentText()
        
        # Disable for Asimovian font (any variant) or no selection
        is_asimovian = (selected.startswith("⭐ [assets]") or 
                       (selected.startswith("✅ [installed]") and "Asimovian" in selected) or
                       selected.endswith("Asimovian-Regular.ttf"))
        
        should_disable = (not selected or 
                         selected == "No fonts available" or 
                         is_asimovian)
        
        if should_disable:
            self.delete_btn.setEnabled(False)
            self.delete_btn.setStyleSheet("""
                QPushButton {
                    background: #262626;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 12px;
                    min-height: 19px;
                    max-height: 19px;
                }
            """)
            self.delete_btn.setToolTip("Cannot delete default Asimovian font")
        else:
            self.delete_btn.setEnabled(True)
            self.delete_btn.setStyleSheet("""
                QPushButton {
                    background: #e74c3c;
                    color: #ffffff;
                    border: 1px solid #c0392b;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 12px;
                    min-height: 19px;
                    max-height: 19px;
                }
            """)
            self.delete_btn.setToolTip("Delete selected font")
            
    def delete_selected_font(self):
        """Delete the selected font with confirmation"""
        selected = self.font_combo.currentText()
        if not selected or selected == "No fonts available":
            QMessageBox.warning(self, "No Selection", "Please select a font to delete")
            return
            
        # Extract font information
        font_name = ""
        source_dir = None
        filename = ""
        is_installed = selected.startswith("✅ [installed]")
        
        if is_installed:
            font_name = selected.replace("✅ [installed] ", "")
            # Find the font file in fonts directory
            for pattern in ["*.ttf", "*.TTF", "*.otf", "*.OTF"]:
                for font_file in self.fonts_dir.glob(pattern):
                    if self.font_manager and self.font_manager.get_font_internal_name(font_file) == font_name:
                        source_dir = self.fonts_dir
                        filename = font_file.name
                        break
                if filename:
                    break
        elif selected.startswith("📁 [fonts]"):
            source_dir = self.fonts_dir
            filename = selected.replace("📁 [fonts] ", "")
        elif selected.startswith("📥 [dl]"):
            source_dir = self.dl_dir
            filename = selected.replace("📥 [dl] ", "")
        
        if not filename:
            QMessageBox.warning(self, "Error", "Could not locate font file to delete")
            return
            
        # Confirmation dialog
        if is_installed:
            reply = QMessageBox.question(self, "Delete Installed Font", 
                                       f"This will delete the currently installed font '{font_name}' and revert CS2 to the Asimovian font.\n\n"
                                       f"Are you sure you want to continue?",
                                       QMessageBox.Yes | QMessageBox.No)
        else:
            reply = QMessageBox.question(self, "Delete Font", 
                                       f"Are you sure you want to delete '{filename}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
            
        try:
            # Delete from source directory
            font_path = source_dir / filename
            if font_path.exists():
                font_path.unlink()
                self.log_message(f"<span style='color: #e74c3c'>Deleted</span> Removed font file: <code>{filename}</code>")
            
            # If it was the installed font, revert to Asimovian
            if is_installed and self.font_manager:
                # Delete from CS2 directory
                fonts_conf_path, repl_global_path, cs2_fonts_dir = self.font_manager.get_cs2_paths()
                cs2_font_path = cs2_fonts_dir / filename
                if cs2_font_path.exists():
                    self.font_manager.remove_readonly(cs2_font_path)
                    cs2_font_path.unlink()
                    self.log_message(f"<span style='color: #e74c3c'>Deleted</span> Removed font from CS2: <code>{filename}</code>")
                
                # Apply Asimovian as default
                asimovian_path = self.assets_dir / "Asimovian-Regular.ttf"
                if asimovian_path.exists():
                    # Get font internal name
                    internal_name = self.font_manager.get_font_internal_name(asimovian_path)
                    if internal_name:
                        # Copy to fonts directory if not already there
                        dest_path = self.fonts_dir / "Asimovian-Regular.ttf"
                        if not dest_path.exists():
                            shutil.copy2(asimovian_path, dest_path)
                            
                        # Apply the font
                        self.font_manager.apply_font_to_cs2(internal_name, "Asimovian-Regular.ttf", asimovian_path)
                        self.log_message(f"<span style='color: #f39c12'>Updated</span> Reverted to Asimovian font")
                        
                        # Update GUI preview
                        self.update_title_font(self.default_font_family)
                        
            # Refresh font list
            self.refresh_font_list()
            
        except Exception as e:
            self.log_message(f"<span style='color: #e74c3c'>Error</span> Error deleting font: {e}")
            QMessageBox.critical(self, "Delete Error", f"Failed to delete font:\n\n{str(e)}")
            
    def open_app_folder(self):
        """Open the application folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(self.app_dir))
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{self.app_dir}"' if sys.platform == 'darwin' else f'xdg-open "{self.app_dir}"')
            self.log_message("<span style='color: #3498db'>Folder</span> Opened application folder")
        except Exception as e:
            self.log_message(f"<span style='color: #e74c3c'>Error</span> Could not open folder: {e}")

    def restore_defaults(self):
        """Restore CS2 to default fonts"""
        if not self.cs2_path:
            QMessageBox.warning(self, "Path Required", "Please set your CS2 installation path first")
            return
            
        if not self.font_manager:
            QMessageBox.warning(self, "Font Manager Error", "Font manager not initialized")
            return
            
        reply = QMessageBox.question(self, "Restore Defaults", 
                                   "This will restore CS2 to default fonts.\n\nAre you sure you want to continue?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
            
        self.log_message("<span style='color: #f39c12'>Restore</span> Starting default restoration process...")
        
        try:
            # Use FontManager to handle all restore logic
            files_restored = self.font_manager.restore_defaults(self.setup_dir)
            
            self.log_message(f"<span style='color: #2ecc71'>Success</span> Restoration completed - {files_restored} files restored")
            
            # Show success message and exit application
            result = QMessageBox.information(self, "Restoration Complete", 
                                  f"Default fonts have been restored successfully!\n\n"
                                  f"Restored {files_restored} configuration file(s) from backups.\n\n"
                                  f"Restart CS2 to see the default fonts.\n\n"
                                  f"The application will now close.",
                                  QMessageBox.Ok)
            
            # Close the application after user clicks OK
            if result == QMessageBox.Ok:
                self.log_message("<span style='color: #3498db'>Exit</span> Application closing after restore completion...")
                QApplication.quit()
            
        except Exception as e:
            self.log_message(f"<span style='color: #e74c3c'>Error</span> Error during restoration: {e}")
            QMessageBox.critical(self, "Restoration Error", f"Failed to restore defaults:\n\n{str(e)}")