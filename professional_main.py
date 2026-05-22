"""
AGAMART - Professional ERP System
Modern SaaS ERP Platform with Complete Business Management
"""
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QToolBar, QAction, QPushButton, QLabel, QStatusBar,
                             QStackedWidget, QStyle)
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer, QDateTime
from datetime import datetime

# Import all modules
from pos_app.ui.professional_modules import (
    PointOfSaleModule, 
    InventoryModule, 
    CustomersSupplierModule,
    InvoicesModule, 
    ReportsModule, 
    UsersModule, 
    BackupModule,
    AdminModule
)
from pos_app.ui.erp_dashboard import ERPDashboard
from pos_app.ui.tools_module import ToolsModule
from pos_app.ui.web_dashboard import WebStyleDashboard

class ProfessionalPOSMain(QMainWindow):
    """Professional POS Application Main Window"""
    
    def __init__(self, user, db=None):
        super().__init__()
        self.user = user
        self.db = db
        self.current_module = None
        self.nav_buttons = {}
        self.init_ui()
        self.update_time()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("AGAMART - Plateforme ERP Professionnelle")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(self.get_stylesheet())
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left sidebar with module buttons
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Right panel with module content
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)
        
        # Add all modules to stacked widget
        self.modules = {
            'dashboard': WebStyleDashboard(self.user, db=self.db),  # Web-style dashboard
            'dashboard_old': ERPDashboard(self.user, db=self.db),  # Keep old dashboard
            'stock': InventoryModule(self.user, db=self.db),
            'sales': PointOfSaleModule(self.user, db=self.db),
            'purchases': CustomersSupplierModule(self.user),  # Using customers module for purchases
            'accounting': InvoicesModule(self.user),
            'pos': PointOfSaleModule(self.user, db=self.db),  # Duplicate for POS navigation
            'hr': UsersModule(self.user),
            'projects': ReportsModule(self.user, db=self.db),  # Using reports for projects
            'manufacturing': AdminModule(self.user, db=self.db),  # Using admin for manufacturing
            'tools': ToolsModule(self.user, db=self.db),  # AGAMART Tools
            # Legacy modules
            'inventory': InventoryModule(self.user, db=self.db),
            'customers': CustomersSupplierModule(self.user),
            'invoices': InvoicesModule(self.user),
            'reports': ReportsModule(self.user, db=self.db),
            'users': UsersModule(self.user),
            'backup': BackupModule(self.user),
            'admin': AdminModule(self.user, db=self.db),
        }
        
        for module in self.modules.values():
            self.stacked_widget.addWidget(module)
        
        # Show dashboard first
        self.show_module('dashboard')
        
        # Create status bar
        self.create_status_bar()
        
        # Create menu bar
        self.create_menu_bar()
        
    def create_left_panel(self):
        """Create left sidebar with module navigation - Modern ERP style"""
        left_widget = QWidget()
        left_widget.setMaximumWidth(260)
        left_widget.setMinimumWidth(260)
        left_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #1e293b);
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout = QVBoxLayout(left_widget)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(8)
        
        # Logo/Header
        header = QLabel("AGAMART")
        header.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                padding: 15px 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Module buttons - Modern ERP navigation
        modules_data = [
            ("📊", "Tableau de Bord", "dashboard"),
            ("📦", "Stock", "stock"),
            ("💰", "Ventes", "sales"),
            ("🛒", "Achats", "purchases"),
            ("📄", "Comptabilité", "accounting"),
            ("🏪", "Point de Vente", "pos"),
            ("👥", "Ressources Humaines", "hr"),
            ("📋", "Projets", "projects"),
            ("🏭", "Fabrication", "manufacturing"),
            ("🛠️", "Outils AGAMART", "tools"),
        ]
        
        self.nav_buttons = {}
        for icon, text, module_key in modules_data:
            btn = QPushButton("{}  {}".format(icon, text))
            btn.setMinimumHeight(48)
            # Set dashboard as active initially
            is_active = (module_key == 'dashboard')
            btn.setStyleSheet(self.get_modern_button_stylesheet(active=is_active))
            btn.clicked.connect(lambda checked, m=module_key: self.show_module(m))
            self.nav_buttons[module_key] = btn
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # User info card
        user_card = QWidget()
        user_card.setStyleSheet("""
            QWidget {
                background-color: rgba(51, 65, 85, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 10px;
            }
        """)
        user_layout = QVBoxLayout(user_card)
        user_layout.setContentsMargins(12, 12, 12, 12)
        
        user_name = QLabel(f"👤 {self.user.get('full_name', self.user['username'])}")
        user_name.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        user_layout.addWidget(user_name)
        
        user_role = QLabel(f"Rôle: {self.user['role'].upper()}")
        user_role.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 11px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        user_layout.addWidget(user_role)
        
        layout.addWidget(user_card)
        
        return left_widget
    
    def show_module(self, module_key):
        """Show specific module"""
        if module_key in self.modules:
            self.stacked_widget.setCurrentWidget(self.modules[module_key])
            self.current_module = module_key
            self.statusBar().showMessage(f"Module: {module_key.upper()}")
            
            # Update button styles (highlight active)
            if hasattr(self, 'nav_buttons') and self.nav_buttons:
                for key, btn in self.nav_buttons.items():
                    if key == module_key:
                        btn.setStyleSheet(self.get_modern_button_stylesheet(active=True))
                    else:
                        btn.setStyleSheet(self.get_modern_button_stylesheet(active=False))
    
    def create_status_bar(self):
        """Create status bar with time and user info"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: rgba(15, 23, 42, 0.9);
                color: rgba(255, 255, 255, 0.8);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        
        # Time label
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                padding-right: 20px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        status_bar.addPermanentWidget(self.time_label)
        
        # Update time every second
        timer = QTimer()
        timer.timeout.connect(self.update_time)
        timer.start(1000)
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2d5a8c;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #1e3a5f;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("Fichier")
        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Aide")
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def update_time(self):
        """Update time in status bar"""
        current_time = QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm:ss")
        self.time_label.setText(f"Session: {self.user['username']} | {current_time}")
    
    def show_about(self):
        """Show about dialog"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "À propos", 
            "AGAMART - Plateforme ERP Professionnelle\n\n"
            "Système de Gestion Complet pour Entreprises\n"
            "Version 1.0.0\n\n"
            "© 2024 AGAMART - Tous droits réservés")
    
    def get_button_stylesheet(self):
        """Get stylesheet for navigation buttons (legacy)"""
        return """
            QPushButton {
                background-color: #2d5a8c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                text-align: left;
                font-size: 12px;
                font-weight: bold;
                margin: 0px 10px;
            }
            QPushButton:hover {
                background-color: #3d7aac;
            }
            QPushButton:pressed {
                background-color: #1e3a5f;
            }
        """
    
    def get_modern_button_stylesheet(self, active=False):
        """Get modern stylesheet for navigation buttons with glassmorphism"""
        if active:
            return """
                QPushButton {
                    background-color: rgba(51, 65, 85, 0.6);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 12px;
                    padding: 12px 15px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }
                QPushButton:hover {
                    background-color: rgba(51, 65, 85, 0.8);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
            """
        else:
            return """
                QPushButton {
                    background-color: rgba(51, 65, 85, 0.2);
                    color: rgba(255, 255, 255, 0.8);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    padding: 12px 15px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 500;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }
                QPushButton:hover {
                    background-color: rgba(51, 65, 85, 0.4);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    color: white;
                }
            """
    
    def get_stylesheet(self):
        """Get main application stylesheet - Modern dark theme"""
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #334155);
            }
            QMenuBar {
                background-color: rgba(15, 23, 42, 0.8);
                color: white;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QMenuBar::item:selected {
                background-color: rgba(51, 65, 85, 0.5);
                border-radius: 4px;
            }
            QStatusBar {
                background-color: rgba(15, 23, 42, 0.9);
                color: rgba(255, 255, 255, 0.8);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """
