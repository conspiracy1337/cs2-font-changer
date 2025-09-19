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
            
            # Load DaFont
            self.browser.load(QUrl("https://www.dafont.com"))
            
            # Setup status bar
            self.status_label = QLabel("Ready - Adblocker enabled | Cookie auto-accept active")
            self.status_label.setStyleSheet("color: #f39c12")
            self.statusBar().addWidget(self.status_label)
            
            # Connect page signals
            self.browser.loadStarted.connect(self.on_load_started)
            self.browser.loadProgress.connect(self.on_load_progress)
            self.browser.loadFinished.connect(self.on_load_finished)
            
            # Auto-accept cookies
            self.setup_cookie_auto_accept()
            
        else:
            # Fallback message
            label = QLabel("Web engine not available.\nPlease install PyQtWebEngine for browser functionality.")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #ffffff; font-size: 16px;")
            layout.addWidget(label)
            
    def update_download_status(self, message):
        """Update the status bar with download information"""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
            # Auto-reset status after 3 seconds
            QTimer.singleShot(3000, lambda: self.status_label.setText("Ready - Adblocker enabled | Cookie auto-accept active"))
            
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
        download_label = QLabel("🔥 Downloads → /DL/ | 🔒 URL: Read-only")
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
        if hasattr(self, 'status_label'):
            self.status_label.setText("Loading...")
        
    def on_load_progress(self, progress):
        """Called during page loading"""
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Loading... {progress}%")
        
    def on_load_finished(self, success):
        """Called when page loading finishes"""
        if hasattr(self, 'status_label'):
            if success:
                self.status_label.setText("Ready - Adblocker enabled | Cookie auto-accept active")
                # Update URL bar
                if hasattr(self, 'url_bar') and hasattr(self, 'browser'):
                    current_url = self.browser.url().toString()
                    self.url_bar.setText(current_url)
                # Auto-accept cookies after page loads
                self.auto_accept_cookies()
            else:
                self.status_label.setText("Failed to load page")
            
    def setup_cookie_auto_accept(self):
        """Setup automatic cookie acceptance"""
        # This will be called after page loads
        pass
        
    def auto_accept_cookies(self):
        """Automatically accept cookies on the current page - enhanced for multiple sites"""
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
        
        # Enhanced cookie acceptance script for multiple font sites
        cookie_script = """
        (function() {
            // Enhanced cookie consent selectors for various font sites
            var cookieSelectors = [
                // FontGet specific selectors - PRIORITY
                '#accept-choices',
                '.sn-b-def.sn-three-btn.sn-adj-fnt.sn-blue',
                'div[id="accept-choices"]',
                'div.sn-b-def',
                
                // General cookie consent selectors
                '#cookie-accept', '.cookie-accept', '#accept-cookies', '.accept-cookies',
                '#cookie-consent-accept', '.cookie-consent-accept', '#gdpr-accept', '.gdpr-accept',
                '#cookies-accept', '.cookies-accept', '#consent-accept', '.consent-accept',
                
                // Other font sites specific selectors
                '.cookie-consent button', '.cookie-banner button', '#cookieConsent button',
                '[data-dismiss="cookie"]', '.cookie-notice button', '.gdpr-banner button',
                '.privacy-overlay button', '.consent-overlay button', '#consent-popup button',
                '.popup-consent button', '[class*="popup"] button[class*="accept"]',
                '.modal-consent button', '#privacy-popup button', '.privacy-modal button',
                
                // 1001Fonts specific selectors
                '.cookie-policy button', '.privacy-notice button', '#privacy-policy button',
                '.consent-banner button', '.cookie-bar button', '#cookie-bar button',
                
                // Font Squirrel and other sites
                '.privacy-popup button', '.consent-popup button', '.cookie-popup button',
                '#consent-banner button', '.gdpr-popup button', '#privacy-banner button',
                
                // Button-specific selectors for cookies
                'button[id*="cookie"][id*="accept"]', 'button[class*="cookie"][class*="accept"]',
                'button[id*="consent"][id*="accept"]', 'button[class*="consent"][class*="accept"]',
                'button[id="cookieAccept"]', 'button[class="cookieAccept"]',
                'button[id="acceptCookies"]', 'button[class="acceptCookies"]',
                'button[id*="gdpr"]', 'button[class*="gdpr"]',
                'button[id*="privacy"]', 'button[class*="privacy"]',
                
                // Link-specific selectors
                'a[id*="cookie"][id*="accept"]', 'a[class*="cookie"][class*="accept"]',
                'a[id="cookieAccept"]', 'a[class="cookieAccept"]',
                'a[href*="accept"]', 'a[href*="cookie"]',
                
                // Data attributes for cookie consent
                '[data-cookie="accept"]', '[data-cookie-accept]', '[data-accept-cookies]',
                '[data-gdpr="accept"]', '[data-consent="accept"]', '[data-dismiss="cookies"]',
                '[data-action="accept"]', '[data-cookie-consent="accept"]'
            ];
            
            var clicked = false;
            console.log('Starting cookie acceptance script...');
            
            // Try specific selectors first
            for (var i = 0; i < cookieSelectors.length && !clicked; i++) {
                try {
                    var elements = document.querySelectorAll(cookieSelectors[i]);
                    for (var j = 0; j < elements.length && !clicked; j++) {
                        var element = elements[j];
                        if (element && element.offsetParent !== null && 
                            element.style.display !== 'none' && !element.disabled &&
                            element.style.visibility !== 'hidden') {
                            
                            console.log('Found element:', element, 'Selector:', cookieSelectors[i]);
                            console.log('Element text:', element.textContent);
                            console.log('Element HTML:', element.outerHTML);
                            
                            // For FontGet div elements that aren't buttons, create a click event
                            if (element.id === 'accept-choices' || element.className.includes('sn-b-def')) {
                                // Simulate a proper click event for div elements
                                var event = new MouseEvent('click', {
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                });
                                element.dispatchEvent(event);
                                
                                // Also try direct click
                                if (typeof element.click === 'function') {
                                    element.click();
                                }
                                
                                console.log('Auto-accepted FontGet cookies via specific selector:', cookieSelectors[i], element);
                                clicked = true;
                            } else {
                                // Regular click for other elements
                                element.click();
                                console.log('Auto-accepted cookies via specific selector:', cookieSelectors[i], element);
                                clicked = true;
                            }
                        }
                    }
                } catch (e) {
                    console.log('Error with selector', cookieSelectors[i], ':', e);
                }
            }
            
            // If no specific selectors worked, try comprehensive text-based matching
            if (!clicked) {
                var clickableElements = document.querySelectorAll('button, a, [role="button"], input[type="button"], input[type="submit"], div[id*="accept"], div[class*="accept"]');
                console.log('Trying text-based matching on', clickableElements.length, 'elements');
                
                for (var k = 0; k < clickableElements.length && !clicked; k++) {
                    var elem = clickableElements[k];
                    if (elem && elem.offsetParent !== null && elem.style.display !== 'none' &&
                        elem.style.visibility !== 'hidden' && !elem.disabled) {
                        
                        var text = elem.textContent.toLowerCase().trim();
                        var isReasonablySmall = text.length <= 35;
                        
                        // Log potential matches for debugging
                        if (text.includes('accept') || text.includes('cookie') || text.includes('visit')) {
                            console.log('Found potential cookie element:', elem.tagName, 'Text:', text, 'Length:', text.length, 'ID:', elem.id, 'Classes:', elem.className);
                        }
                        
                        // Enhanced text patterns for cookie acceptance - prioritize FontGet
                        var isCookieElement = (
                            // FontGet specific text - check first
                            text === 'accept all & visit the site' ||
                            text.includes('accept all & visit') ||
                            text.includes('accept all and visit') ||
                            text === 'accept all and visit the site' ||
                            
                            // Basic acceptance terms
                            (text === 'accept' && isReasonablySmall) ||
                            (text === 'ok' && isReasonablySmall) ||
                            (text === 'got it' && isReasonablySmall) ||
                            (text === 'allow' && isReasonablySmall) ||
                            (text === 'agree' && isReasonablySmall) ||
                            (text === 'yes' && isReasonablySmall) ||
                            
                            // Cookie-specific terms
                            text === 'accept cookies' ||
                            text === 'accept all cookies' ||
                            text === 'accept all' ||
                            text === 'allow cookies' ||
                            text === 'allow all' ||
                            text === 'i agree' ||
                            text === 'i accept' ||
                            text === 'continue' ||
                            text === 'dismiss' ||
                            text === 'close' ||
                            
                            // GDPR and privacy terms
                            text === 'accept privacy policy' ||
                            text === 'accept terms' ||
                            text === 'agree to cookies' ||
                            text === 'consent' ||
                            text.includes('accept') && text.includes('cookie') ||
                            text.includes('accept') && text.includes('privacy') ||
                            text.includes('accept') && text.includes('terms') ||
                            text.includes('accept') && text.includes('visit')
                        );
                        
                        if (isCookieElement) {
                            // Enhanced context checking - look at more parent elements
                            var hasContext = false;
                            var contextTerms = ['cookie', 'consent', 'privacy', 'gdpr', 'policy', 'notice', 'banner', 'popup'];
                            
                            // Check element's own attributes and classes
                            var elemContext = (elem.className + ' ' + elem.id + ' ' + (elem.getAttribute('data-') || '')).toLowerCase();
                            for (var ct = 0; ct < contextTerms.length; ct++) {
                                if (elemContext.includes(contextTerms[ct])) {
                                    hasContext = true;
                                    break;
                                }
                            }
                            
                            // Check parent elements (up to 5 levels)
                            if (!hasContext) {
                                var parentText = '';
                                var parent = elem.parentElement;
                                for (var p = 0; p < 5 && parent && !hasContext; p++) {
                                    var parentContext = parent.textContent.toLowerCase() + ' ' + 
                                                      parent.className.toLowerCase() + ' ' + 
                                                      parent.id.toLowerCase();
                                    parentText += parentContext;
                                    
                                    for (var ct = 0; ct < contextTerms.length; ct++) {
                                        if (parentContext.includes(contextTerms[ct])) {
                                            hasContext = true;
                                            break;
                                        }
                                    }
                                    parent = parent.parentElement;
                                }
                            }
                            
                            // If we found cookie context or it's a very obvious element or FontGet specific, click it
                            if (hasContext || 
                                text === 'accept' || text === 'ok' || text === 'got it' ||
                                text.includes('accept all & visit') || text.includes('accept all and visit')) {
                                
                                // Special handling for div elements (like FontGet)
                                if (elem.tagName.toLowerCase() === 'div') {
                                    var event = new MouseEvent('click', {
                                        bubbles: true,
                                        cancelable: true,
                                        view: window
                                    });
                                    elem.dispatchEvent(event);
                                    
                                    if (typeof elem.click === 'function') {
                                        elem.click();
                                    }
                                } else {
                                    elem.click();
                                }
                                
                                console.log('Auto-accepted cookies via enhanced text matching:', elem, 'Text:', text);
                                clicked = true;
                            }
                        }
                    }
                }
            }
            
            if (clicked) {
                console.log('Successfully auto-accepted cookies');
            } else {
                console.log('No cookie consent elements found');
            }
        })();
        """
        
        # Execute almost instantly - just enough delay for DOM to be ready
        QTimer.singleShot(300, lambda: self.browser.page().runJavaScript(cookie_script))
        
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
        
        # Add font sites
        sites = [
            ("🏠 DaFont", "https://www.dafont.com"),
            ("📚 FontGet", "https://www.fontget.com"),
            ("🔥 1001 Fonts", "https://www.1001fonts.com"),
            ("✨ Font Squirrel", "https://www.fontsquirrel.com"),
            ("🎨 Google Fonts", "https://fonts.google.com"),
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