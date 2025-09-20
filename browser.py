"""
CS2 Font Changer - Browser Component
Handles the web browser interface for downloading fonts
"""

import webbrowser
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

try:
    from PyQt5.QtWebEngineWidgets import *
    from PyQt5.QtWebEngineCore import *
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    print("Note: QtWebEngine not available. Install with: pip install PyQtWebEngine")


# Define classes conditionally
if WEBENGINE_AVAILABLE:
    class AdBlocker(QWebEngineUrlRequestInterceptor):
        """Simple adblocker using common ad domains"""
        def __init__(self, parent=None):
            super().__init__(parent)
            # Common ad domains to block
            self.blocked_domains = {
                'googleadservices.com', 'googlesyndication.com', 'googletagmanager.com',
                'doubleclick.net', 'amazon-adsystem.com', 'facebook.com/tr',
                'google-analytics.com', 'googletagservices.com', 'adsystem.amazon.com',
                'ads.yahoo.com', 'advertising.com', 'adsystem.amazon.co.uk',
                'outbrain.com', 'taboola.com', 'revcontent.com', 'content.ad',
                'popads.net', 'popcash.net', 'propellerads.com', 'exoclick.com',
                'adnxs.com', 'rubiconproject.com', 'openx.net', 'pubmatic.com',
                'criteo.com', 'adsystem.amazon.ca', 'adsystem.amazon.de'
            }
            
            # Common ad URL patterns
            self.blocked_patterns = [
                'ads', 'advertisement', 'popup', 'banner', 'sponsor',
                '/ads/', '/ad/', 'advert', 'promo', 'tracking'
            ]
            
        def interceptRequest(self, info):
            url = info.requestUrl().toString()
            host = info.requestUrl().host()
            
            # Block known ad domains
            for domain in self.blocked_domains:
                if domain in host:
                    info.block(True)
                    return
            
            # Block common ad patterns
            url_lower = url.lower()
            for pattern in self.blocked_patterns:
                if pattern in url_lower:
                    info.block(True)
                    return

    class DownloadManager(QObject):
        """Handle file downloads from the web browser"""
        downloadFinished = pyqtSignal(str)
        downloadStarted = pyqtSignal(str)
        
        def __init__(self, download_dir):
            super().__init__()
            self.download_dir = Path(download_dir)
            self.download_dir.mkdir(exist_ok=True)
            
        def handle_download(self, download_item):
            """Handle a download item from the browser"""
            # Get filename from download
            filename = download_item.suggestedFileName()
            if not filename:
                filename = "downloaded_font"
                
            # Ensure we only download font-related files
            allowed_extensions = ['.ttf', '.otf', '.zip', '.rar', '.7z']
            if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
                download_item.cancel()
                return
                
            # Set download path
            file_path = self.download_dir / filename
            download_item.setPath(str(file_path))
            
            # Emit started signal
            self.downloadStarted.emit(filename)
            
            # Connect signals
            download_item.finished.connect(lambda: self.on_download_finished(str(file_path), filename))
            download_item.accept()
            
        def on_download_finished(self, file_path, filename):
            """Called when download is finished"""
            self.downloadFinished.emit(file_path)
            # Also update parent status if available
            if hasattr(self, '_parent') and self._parent:
                self._parent.update_download_status(f"📥 Downloaded: {filename}")

else:
    # Dummy classes when WebEngine is not available
    class AdBlocker:
        def __init__(self, parent=None):
            pass
    
    class DownloadManager(QObject):
        downloadFinished = pyqtSignal(str)
        downloadStarted = pyqtSignal(str)
        
        def __init__(self, download_dir):
            super().__init__()
            self.download_dir = Path(download_dir)


class BrowserWindow(QMainWindow):
    """Separate browser window with adblocker"""
    downloadCompleted = pyqtSignal(str)
    downloadStarted = pyqtSignal(str)
    windowClosed = pyqtSignal()  # Signal when window is closed
    
    def __init__(self, download_dir):
        super().__init__()
        self.download_dir = download_dir
        self.setWindowTitle("Font Browser - CS2 Font Downloader")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Persistent download status with timer
        self.last_download_status = ""
        self.download_status_timer = QTimer()
        self.download_status_timer.setSingleShot(True)
        self.download_status_timer.timeout.connect(self.allow_status_clear)
        self.status_clear_allowed = True
        
        # Set window icon and styling
        self.setup_window_style()
        self.setup_ui()
        
    def closeEvent(self, event):
        """Handle window close event"""
        self.windowClosed.emit()  # Emit signal when window is closed
        event.accept()  # Accept the close event
        
    def setup_window_style(self):
        """Setup window styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3e3e3e, stop:1 #2d2d2d);
                border-bottom: 2px solid #0d7377;
                spacing: 3px;
                padding: 5px;
            }
            QToolBar QToolButton {
                background: #4e4e4e;
                color: white;
                border: 1px solid #666666;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                margin: 2px;
            }
            QToolBar QToolButton:hover {
                background: #5e5e5e;
                border-color: #0d7377;
            }
            QToolBar QLineEdit {
                background: #2d2d2d;
                color: #888888;
                border: 2px solid #444444;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-height: 20px;
            }
            QStatusBar {
                background: #2d2d2d;
                color: #b0b0b0;
                border-top: 1px solid #555555;
            }
        """)
        
    def setup_ui(self):
        """Setup the browser UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if WEBENGINE_AVAILABLE:
            # Create custom profile with adblocker
            self.profile = QWebEngineProfile()
            
            # Setup adblocker
            self.ad_blocker = AdBlocker()
            self.profile.setUrlRequestInterceptor(self.ad_blocker)
            
            # Create browser with custom profile
            self.browser = QWebEngineView()
            self.page = QWebEnginePage(self.profile, self.browser)
            self.browser.setPage(self.page)
            
            # Setup download manager
            self.download_manager = DownloadManager(self.download_dir)
            self.download_manager._parent = self  # Set parent reference
            self.download_manager.downloadFinished.connect(self.downloadCompleted.emit)
            self.download_manager.downloadStarted.connect(self.downloadStarted.emit)
            self.profile.downloadRequested.connect(self.download_manager.handle_download)
            
            # Setup toolbar
            self.create_toolbar()
            
            # Add browser to layout
            layout.addWidget(self.browser)
            
            # Load Google Fonts as default
            self.browser.load(QUrl("https://fonts.google.com"))
            
            # Setup status bar
            self.status_label = QLabel(self.last_download_status)
            self.status_label.setStyleSheet("color: #f39c12")
            self.statusBar().addWidget(self.status_label)
            
            # Connect page signals
            self.browser.loadStarted.connect(self.on_load_started)
            self.browser.loadProgress.connect(self.on_load_progress)
            self.browser.loadFinished.connect(self.on_load_finished)
            self.browser.urlChanged.connect(self.on_url_changed)
            
            # Auto-accept cookies
            self.setup_cookie_auto_accept()
            
        else:
            # Fallback message
            label = QLabel("Web engine not available.\nPlease install PyQtWebEngine for browser functionality.")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #ffffff; font-size: 16px;")
            layout.addWidget(label)
            
    def on_url_changed(self, url):
        """Handle URL changes - only clear download status if timer allows"""
        if hasattr(self, 'status_label') and self.status_clear_allowed:
            self.last_download_status = ""
            self.status_label.setText(self.last_download_status)
            
    def update_download_status(self, message):
        """Update the status bar with download information (persistent for 5 seconds)"""
        if hasattr(self, 'status_label'):
            self.last_download_status = message
            self.status_label.setText(message)
            
            # Prevent status clearing for 5 seconds
            self.status_clear_allowed = False
            self.download_status_timer.stop()  # Stop any existing timer
            self.download_status_timer.start(5000)  # Start 5-second timer
            
    def allow_status_clear(self):
        """Called by timer after 5 seconds to allow status clearing"""
        self.status_clear_allowed = True
            
    def create_toolbar(self):
        """Create browser toolbar"""
        if not WEBENGINE_AVAILABLE:
            return
            
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Back button
        back_action = toolbar.addAction("←")
        back_action.setToolTip("Go Back")
        back_action.triggered.connect(lambda: [self.browser.back(), self._clear_processed_urls()])
        
        # Forward button
        forward_action = toolbar.addAction("→")
        forward_action.setToolTip("Go Forward")
        forward_action.triggered.connect(lambda: [self.browser.forward(), self._clear_processed_urls()])
        
        toolbar.addSeparator()
        
        # URL bar (read-only)
        self.url_bar = QLineEdit()
        self.url_bar.setReadOnly(True)
        self.url_bar.setPlaceholderText("Current URL (read-only)")
        toolbar.addWidget(self.url_bar)
        
        # Font sites dropdown menu
        self.create_font_sites_menu(toolbar)
        
        toolbar.addSeparator()
        
        # Download info
        download_label = QLabel("📥 Downloads → /DL/ | 🔒 URL: Read-only")
        download_label.setStyleSheet("color: #b0b0b0; font-size: 12px; padding: 5px;")
        toolbar.addWidget(download_label)
        
    def navigate_to_url(self):
        """Navigate to URL from address bar"""
        if not WEBENGINE_AVAILABLE:
            return
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.browser.load(QUrl(url))
        
    def on_load_started(self):
        """Called when page loading starts"""
        pass
        
    def on_load_progress(self, progress):
        """Called during page loading"""
        pass
        
    def on_load_finished(self, success):
        """Called when page loading finishes"""
        if success:
            # Update URL bar
            if hasattr(self, 'url_bar') and hasattr(self, 'browser'):
                current_url = self.browser.url().toString()
                self.url_bar.setText(current_url)
            # Auto-accept cookies after page loads
            self.auto_accept_cookies()
            
    def setup_cookie_auto_accept(self):
        """Setup automatic cookie acceptance"""
        # This will be called after page loads
        pass
        
    def auto_accept_cookies(self):
        """Automatically accept cookies on the current page - targeted approach"""
        if not WEBENGINE_AVAILABLE or not hasattr(self, 'browser'):
            return
            
        # Only run on initial page load, not on every page change
        current_url = self.browser.url().toString()
        if not hasattr(self, '_processed_urls'):
            self._processed_urls = set()
        
        # Don't process the same URL multiple times
        if current_url in self._processed_urls:
            return
            
        self._processed_urls.add(current_url)
        
        # Targeted cookie acceptance script for specific font sites only
        cookie_script = """
        (function() {
            // Specific selectors for known font sites only
            var cookieSelectors = [
                // Google Fonts
                'a[class*="callout"][class*="link"]',
                'a[*ngcontent*][class*="gf-label-large"]',
                
                // DaFont
                'button.sd-cmp-1bquj',
                'button[class*="sd-cmp"]',
                
                // FontGet
                '#accept-choices',
                'div.sn-b-def.sn-three-btn',
                
                // 1001Fonts
                '#accept-btn',
                'button[mode="primary"][id="accept-btn"]',
                
                // Font Squirrel
                'button.cky-btn.cky-btn-accept',
                'button[data-cky-tag="accept-button"]'
            ];
            
            var clicked = false;
            
            // Try specific selectors only
            for (var i = 0; i < cookieSelectors.length && !clicked; i++) {
                try {
                    var elements = document.querySelectorAll(cookieSelectors[i]);
                    for (var j = 0; j < elements.length && !clicked; j++) {
                        var element = elements[j];
                        if (element && element.offsetParent !== null && 
                            element.style.display !== 'none' && !element.disabled &&
                            element.style.visibility !== 'hidden') {
                            
                            var text = element.textContent.toLowerCase().trim();
                            
                            // Only click if text contains expected cookie acceptance terms
                            if (text.includes('dismiss') || text.includes('accept') || 
                                text.includes('agree') || text.includes('visit')) {
                                
                                // Handle special div elements (FontGet)
                                if (element.tagName.toLowerCase() === 'div') {
                                    var event = new MouseEvent('click', {
                                        bubbles: true,
                                        cancelable: true,
                                        view: window
                                    });
                                    element.dispatchEvent(event);
                                    
                                    if (typeof element.click === 'function') {
                                        element.click();
                                    }
                                } else {
                                    element.click();
                                }
                                
                                clicked = true;
                            }
                        }
                    }
                } catch (e) {
                    // Silently continue on error
                }
            }
        })();
        """
        
        # Execute with delay for DOM to be ready
        QTimer.singleShot(500, lambda: self.browser.page().runJavaScript(cookie_script))
        
    def _clear_processed_urls(self):
        """Clear processed URLs to allow cookie acceptance on manual navigation"""
        if hasattr(self, '_processed_urls'):
            self._processed_urls.clear()
            
    def create_font_sites_menu(self, toolbar):
        """Create font sites dropdown menu"""
        if not WEBENGINE_AVAILABLE:
            return
            
        font_sites_btn = QPushButton("🏠 Font Sites ▼")
        font_sites_btn.setToolTip("Select font website to browse")
        font_sites_btn.setStyleSheet("""
            QPushButton {
                background: #4e4e4e;
                color: white;
                border: 1px solid #666666;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                margin: 2px;
            }
            QPushButton:hover {
                background: #5e5e5e;
                border-color: #0d7377;
            }
            QPushButton::menu-indicator {
                width: 0px; /* Hide default arrow */
            }
        """)
        
        # Create menu
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: #3e3e3e;
                color: white;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                background: transparent;
                padding: 8px 20px;
                margin: 2px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #0d7377;
            }
        """)
        
        # Add font sites with Google Fonts first
        sites = [
            ("🎨 Google Fonts", "https://fonts.google.com"),
            ("🏠 DaFont", "https://www.dafont.com"),
            ("📚 FontGet", "https://www.fontget.com"),
            ("📥 1001 Fonts", "https://www.1001fonts.com"),
            ("✨ Font Squirrel", "https://www.fontsquirrel.com"),
        ]
        
        for name, url in sites:
            action = menu.addAction(name)
            action.triggered.connect(lambda checked, u=url, n=name: [
                self.browser.load(QUrl(u)), 
                self._clear_processed_urls(),
                self.setWindowTitle(f"{n} Browser - CS2 Font Downloader")
            ])
        
        font_sites_btn.setMenu(menu)
        toolbar.addWidget(font_sites_btn)