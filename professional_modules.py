"""
Professional POS Modules - 7 Main Components
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit, QSpinBox,
                             QComboBox, QDateEdit, QGroupBox, QFormLayout, QHeaderView,
                             QMessageBox, QTabWidget, QTextEdit, QCheckBox, QFileDialog,
                             QProgressBar, QDialog, QDialogButtonBox, QInputDialog, QSlider)
from PyQt5.QtGui import QFont, QColor, QBrush, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate, QDateTime, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from datetime import datetime
import json
import os
from pos_app.utils.backup import BackupManager
from pos_app.modules.report_manager import ReportManager
from pos_app.modules.product_manager import ProductManager
from pos_app.modules.purchase_order_manager import PurchaseOrderManager
from pos_app.modules.loyalty_manager import LoyaltyManager
from pos_app.modules.advanced_inventory_manager import AdvancedInventoryManager
from pos_app.modules.promotions_manager import PromotionsManager
from pos_app.modules.payment_adapters import PaymentProcessor
from pos_app.modules.ecommerce_sync import EcommerceSyncManager

# ============================================================================
# 1. POINT OF SALE MODULE
# ============================================================================

class PointOfSaleModule(QWidget):
    """Point of Sale - Main sales transaction module"""

    def __init__(self, user, db=None):
        super().__init__()
        self.user = user
        self.db = db
        self.pm = ProductManager(db) if db is not None else None
        self.promos = PromotionsManager(db) if db is not None else None
        self.loyalty = LoyaltyManager(db) if db is not None else None
        self.payment_processor = PaymentProcessor()
        self.invoice_items = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize Point of Sale UI"""
        layout = QHBoxLayout(self)
        
        # Left side - Product selection
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Search / Barcode input
        search_label = QLabel("Rechercher / Scanner:")
        search_label.setFont(QFont("Arial", 11, QFont.Bold))
        left_layout.addWidget(search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Code barre ou nom... (scan + Enter)")
        self.search_box.setMinimumHeight(35)
        left_layout.addWidget(self.search_box)
        # Connect Enter (scanner) to handler
        self.search_box.returnPressed.connect(self.handle_scan)
        
        # Product grid
        products_label = QLabel("Produits disponibles:")
        products_label.setFont(QFont("Arial", 11, QFont.Bold))
        left_layout.addWidget(products_label)
        
        # Product buttons (placeholder)
        for i in range(3):
            btn = QPushButton(f"Produit {i+1}\n20.00 DA")
            btn.setMinimumHeight(80)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e8f4f8;
                    border: 2px solid #2d5a8c;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b3d9e6;
                }
            """)
            left_layout.addWidget(btn)
        
        left_layout.addStretch()
        left_panel.setMaximumWidth(250)
        layout.addWidget(left_panel)
        
        # Right side - Invoice details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Invoice header
        invoice_group = QGroupBox("Point de vente - Facture N°")
        invoice_layout = QFormLayout()

        from PyQt5.QtWidgets import QLineEdit as _QLineEdit
        self.invoice_number_edit = _QLineEdit()
        self.invoice_number_edit.setText(f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        self.date_edit = QDateEdit(QDate.currentDate())
        self.customer_combo = QComboBox()
        # Load customers into combo if DB available
        if self.db:
            try:
                conn = self.db.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT id, name FROM customers ORDER BY name")
                rows = cur.fetchall()
                for r in rows:
                    self.customer_combo.addItem(r['name'], r['id'])
                conn.close()
            except Exception:
                pass

        invoice_layout.addRow("Numéro:", self.invoice_number_edit)
        invoice_layout.addRow("Date:", self.date_edit)
        invoice_layout.addRow("Client:", self.customer_combo)

        invoice_group.setLayout(invoice_layout)
        right_layout.addWidget(invoice_group)
        
        # Cart table
        cart_label = QLabel("Panier:")
        cart_label.setFont(QFont("Arial", 11, QFont.Bold))
        right_layout.addWidget(cart_label)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Article", "Qte", "P.U", "Rem%", "Total"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setMinimumHeight(250)
        right_layout.addWidget(self.cart_table)
        
        # Totals
        totals_group = QGroupBox("Totaux")
        totals_layout = QFormLayout()
        self.subtotal_label = QLabel("0.00 DA")
        self.discount_label = QLabel("0.00 DA")
        self.tax_label = QLabel("0.00 DA")
        self.total_label = QLabel("0.00 DA")
        self.total_label.setStyleSheet("font-weight: bold; color: red; font-size: 14px;")

        totals_layout.addRow("Sous-total:", self.subtotal_label)
        totals_layout.addRow("Remise:", self.discount_label)
        totals_layout.addRow("Taxe (TVA):", self.tax_label)
        totals_layout.addRow("Net à payer:", self.total_label)

        totals_group.setLayout(totals_layout)
        right_layout.addWidget(totals_group)
        
        # Payment
        payment_group = QGroupBox("Mode de règlement")
        payment_layout = QHBoxLayout()
        self.btn_cash = QPushButton("Espèces")
        self.btn_cheque = QPushButton("Chèque")
        self.btn_card = QPushButton("Carte")
        self.btn_credit = QPushButton("Crédit")
        payment_layout.addWidget(self.btn_cash)
        payment_layout.addWidget(self.btn_cheque)
        payment_layout.addWidget(self.btn_card)
        payment_layout.addWidget(self.btn_credit)
        payment_group.setLayout(payment_layout)
        # simple handlers (select payment method)
        self.selected_payment_method = 'cash'
        self.btn_cash.clicked.connect(lambda: self.select_payment_method('cash'))
        self.btn_cheque.clicked.connect(lambda: self.select_payment_method('cheque'))
        self.btn_card.clicked.connect(lambda: self.select_payment_method('card'))
        self.btn_credit.clicked.connect(lambda: self.select_payment_method('credit'))
        right_layout.addWidget(payment_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.btn_new = QPushButton("Nouveau")
        self.btn_print = QPushButton("Imprimer")
        self.btn_validate = QPushButton("Valider")
        self.btn_close = QPushButton("Fermer")
        button_layout.addWidget(self.btn_new)
        button_layout.addWidget(self.btn_print)
        button_layout.addWidget(self.btn_validate)
        button_layout.addWidget(self.btn_close)
        right_layout.addLayout(button_layout)

        # connect actions
        self.btn_validate.clicked.connect(self.finalize_invoice)
        self.btn_new.clicked.connect(self.new_invoice)
        self.btn_close.clicked.connect(lambda: self.parentWidget().close() if self.parentWidget() else None)
        
        layout.addWidget(right_panel, 1)

    def handle_scan(self):
        """Handle barcode / sku scan or typed query in the search box."""
        code = self.search_box.text().strip()
        if not code:
            return

        # Try barcode first, then sku, then name search
        prod = None
        if self.pm:
            prod = self.pm.get_product_by_sku(code)
            if not prod:
                # try barcode lookup
                conn = self.db.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM products WHERE barcode = ?", (code,))
                row = cur.fetchone()
                conn.close()
                if row:
                    prod = dict(row)
            # if still not found, try name search first match
            if not prod:
                results = self.pm.search_products(code)
                if results:
                    prod = results[0]

        if not prod:
            QMessageBox.warning(self, "Produit introuvable", f"Aucun produit trouvé pour: {code}")
            self.search_box.clear()
            return

        # Add one unit to cart by default
        self.add_to_cart(prod, qty=1)
        self.search_box.clear()

    def add_to_cart(self, product, qty=1):
        """Add a product dict to the cart and update the cart table and totals."""
        # product expected as dict with keys: id, name, selling_price
        item = {
            'product_id': product.get('id'),
            'name': product.get('name'),
            'qty': qty,
            'unit_price': float(product.get('selling_price') or 0.0),
            'discount': 0.0
        }
        # If item already in cart, increase qty
        for it in self.invoice_items:
            if it['product_id'] == item['product_id']:
                it['qty'] += qty
                break
        else:
            self.invoice_items.append(item)

        self.refresh_cart()

    def refresh_cart(self):
        """Refresh cart table UI and totals."""
        self.cart_table.setRowCount(len(self.invoice_items))
        subtotal = 0.0
        for i, it in enumerate(self.invoice_items):
            name = it['name']
            qty = it['qty']
            pu = it['unit_price']
            rem = it.get('discount', 0.0)
            total = qty * pu * (1 - rem/100)
            subtotal += total

            self.cart_table.setItem(i, 0, QTableWidgetItem(name))
            self.cart_table.setItem(i, 1, QTableWidgetItem(str(qty)))
            self.cart_table.setItem(i, 2, QTableWidgetItem(f"{pu:.2f}"))
            self.cart_table.setItem(i, 3, QTableWidgetItem(f"{rem:.1f}"))
            self.cart_table.setItem(i, 4, QTableWidgetItem(f"{total:.2f}"))

        tax = subtotal * 0.19  # example TVA 19%
        discount = 0.0
        total = subtotal + tax - discount

        self.subtotal_label.setText(f"{subtotal:.2f} DA")
        self.tax_label.setText(f"{tax:.2f} DA")
        self.discount_label.setText(f"{discount:.2f} DA")
        self.total_label.setText(f"{total:.2f} DA")

    def select_payment_method(self, method):
        """Select payment method (simple visual state)."""
        self.selected_payment_method = method
        # Simple visual feedback
        for btn, m in [(self.btn_cash, 'cash'), (self.btn_cheque, 'cheque'), (self.btn_card, 'card'), (self.btn_credit, 'credit')]:
            if m == method:
                btn.setStyleSheet('background-color: #4caf50; color: white;')
            else:
                btn.setStyleSheet('')

    def compute_totals(self):
        """Compute subtotal, tax, discount and total for current cart."""
        subtotal = 0.0
        for it in self.invoice_items:
            subtotal += it['qty'] * it['unit_price'] * (1 - (it.get('discount', 0.0) or 0.0)/100.0)

        # Promotions discount
        discount = 0.0
        if self.promos:
            try:
                discount = self.promos.apply_promotions_to_cart(self.invoice_items) or 0.0
            except Exception:
                discount = 0.0

        tax = subtotal * 0.19
        total = subtotal + tax - discount
        return subtotal, tax, discount, total

    def new_invoice(self):
        """Reset the current invoice/cart to start a new sale."""
        self.invoice_items = []
        self.invoice_number_edit.setText(f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        self.refresh_cart()

    def finalize_invoice(self):
        """Finalize the invoice: write invoice and items to DB, deduct stock, award loyalty."""
        if not self.invoice_items:
            QMessageBox.warning(self, "Panier vide", "Le panier est vide. Ajoutez des articles avant de valider.")
            return

        subtotal, tax, discount, total = self.compute_totals()

        invoice_number = self.invoice_number_edit.text().strip() or f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        customer_id = None
        try:
            customer_id = self.customer_combo.currentData()
        except Exception:
            customer_id = None

        cashier_id = self.user.get('id') if isinstance(self.user, dict) else None

        # Process payment for card terminals if needed
        payment_method = self.selected_payment_method or 'cash'
        payment_status = 'pending'
        try:
            mapped = payment_method
            if payment_method == 'card':
                mapped = 'card_terminal'
            elif payment_method == 'cheque':
                mapped = 'cash'

            if mapped in ('card_terminal', 'stripe', 'paypal', 'cash'):
                res = self.payment_processor.process(mapped, total)
                if res and res.get('success'):
                    payment_status = 'completed'
                else:
                    payment_status = 'failed' if res and not res.get('success') else 'pending'
            else:
                payment_status = 'completed'
        except Exception:
            payment_status = 'pending'

        # Insert invoice and invoice items
        if not self.db:
            QMessageBox.critical(self, "Erreur DB", "Base de données non disponible.")
            return

        conn = self.db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO invoices (invoice_number, customer_id, cashier_id, subtotal, discount, tax, total, payment_method, payment_status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (invoice_number, customer_id, cashier_id, subtotal, discount, tax, total, payment_method, payment_status, datetime.now())
            )
            invoice_id = cur.lastrowid

            for it in self.invoice_items:
                cur.execute(
                    "INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (invoice_id, it['product_id'], it['qty'], it['unit_price'], it['qty'] * it['unit_price'])
                )
                # Deduct stock
                try:
                    self.pm.remove_stock(it['product_id'], it['qty'], reason=f"Sale {invoice_number}")
                except Exception:
                    pass

            # Update customer totals and award loyalty
            if customer_id and self.loyalty:
                try:
                    cur.execute("UPDATE customers SET total_purchases = COALESCE(total_purchases,0) + ? WHERE id = ?", (total, customer_id))
                    # Award 1 point per 10 currency units
                    points = int(total // 10)
                    if points > 0:
                        self.loyalty.add_points(customer_id, points, reason='Purchase')
                except Exception:
                    pass

            conn.commit()
            QMessageBox.information(self, "Succès", f"Facture {invoice_number} enregistrée (Total: {total:.2f})")
            # Reset cart
            self.new_invoice()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer la facture: {e}")
        finally:
            conn.close()

# ============================================================================
# 2. INVENTORY / STOCK MODULE
# ============================================================================

class InventoryModule(QWidget):
    """Inventory Management - Stock control and management"""
    
    def __init__(self, user, db=None):
        super().__init__()
        self.user = user
        self.db = db
        self.pm = ProductManager(db) if db is not None else None
        self.adv_inv = AdvancedInventoryManager(db) if db is not None else None
        self.init_ui()
    
    def init_ui(self):
        """Initialize Inventory UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Gestion du Stock")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Search and filters
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Rechercher:"))
        search_layout.addWidget(QLineEdit())
        search_layout.addWidget(QLabel("Catégorie:"))
        search_layout.addWidget(QComboBox())
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Stock table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(7)
        self.stock_table.setHorizontalHeaderLabels([
            "Code", "Désignation", "Catégorie", "Qte Stock", 
            "Qte Min", "P.Achat", "P.Vente"
        ])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stock_table.setMinimumHeight(400)
        layout.addWidget(self.stock_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.btn_add = QPushButton("Ajouter")
        self.btn_edit = QPushButton("Modifier")
        self.btn_delete = QPushButton("Supprimer")
        self.btn_entry = QPushButton("Entrée Stock")
        self.btn_exit = QPushButton("Sortie Stock")
        self.btn_inventory = QPushButton("Inventaire")
        self.btn_lots = QPushButton("Gérer Lots")
        self.btn_fifo = QPushButton("Retrait FIFO")
        self.btn_lifo = QPushButton("Retrait LIFO")

        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_edit)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_entry)
        button_layout.addWidget(self.btn_exit)
        button_layout.addWidget(self.btn_inventory)
        button_layout.addWidget(self.btn_lots)
        button_layout.addWidget(self.btn_fifo)
        button_layout.addWidget(self.btn_lifo)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Connect actions
        self.btn_add.clicked.connect(self.handle_add_product)
        self.btn_edit.clicked.connect(self.handle_edit_product)
        self.btn_delete.clicked.connect(self.handle_delete_product)
        self.btn_entry.clicked.connect(self.handle_entry_stock)
        self.btn_exit.clicked.connect(self.handle_exit_stock)
        self.btn_inventory.clicked.connect(self.handle_inventory)
        self.btn_lots.clicked.connect(self.handle_lots)
        self.btn_fifo.clicked.connect(self.handle_fifo_removal)
        self.btn_lifo.clicked.connect(self.handle_lifo_removal)
        
        # Stock alerts
        alerts_group = QGroupBox("Alertes Stock")
        alerts_layout = QVBoxLayout()
        alert_table = QTableWidget()
        alert_table.setColumnCount(3)
        alert_table.setHorizontalHeaderLabels(["Article", "Qte Min", "Alerte"])
        alerts_layout.addWidget(alert_table)
        alerts_group.setLayout(alerts_layout)
        layout.addWidget(alerts_group)

        # Load products into the table
        self.load_products()

    def load_products(self):
        """Load products from DB into the stock table"""
        if not self.pm:
            return

        products = self.pm.get_all_products()
        self.stock_table.setRowCount(len(products))

        for i, p in enumerate(products):
            sku = str(p.get('sku') or '')
            name = str(p.get('name') or '')
            category = str(p.get('category') or '')
            qty = str(p.get('quantity') or 0)
            min_stock = str(p.get('min_stock') or 0)
            purchase = str(p.get('purchase_price') or 0)
            selling = str(p.get('selling_price') or 0)

            self.stock_table.setItem(i, 0, QTableWidgetItem(sku))
            self.stock_table.setItem(i, 1, QTableWidgetItem(name))
            self.stock_table.setItem(i, 2, QTableWidgetItem(category))
            self.stock_table.setItem(i, 3, QTableWidgetItem(qty))
            self.stock_table.setItem(i, 4, QTableWidgetItem(min_stock))
            self.stock_table.setItem(i, 5, QTableWidgetItem(purchase))
            self.stock_table.setItem(i, 6, QTableWidgetItem(selling))

        self.stock_table.resizeRowsToContents()

    def get_selected_sku(self):
        sel = self.stock_table.currentRow()
        if sel < 0:
            return None
        item = self.stock_table.item(sel, 0)
        return item.text() if item else None

    def handle_add_product(self):
        """Add a new product (minimal prompt)"""
        if not self.pm:
            QMessageBox.warning(self, "Erreur", "Base de données non disponible")
            return

        name, ok = QInputDialog.getText(self, "Ajouter produit", "Nom du produit:")
        if not ok or not name.strip():
            return

        qty, ok2 = QInputDialog.getInt(self, "Quantité initiale", "Quantité:", 0, 0)
        if not ok2:
            qty = 0

        # Create product with minimal fields
        sku = name[:12].upper().replace(' ', '_')
        new_id = self.pm.add_product(name=name, sku=sku, purchase_price=0.0, selling_price=0.0, category='General', barcode=None, min_stock=0)
        if new_id:
            if qty > 0:
                self.pm.add_stock(new_id, qty, reason='Initial stock')
            QMessageBox.information(self, "Succès", "Produit ajouté")
            self.load_products()
        else:
            QMessageBox.critical(self, "Erreur", "Impossible d'ajouter le produit")

    def handle_edit_product(self):
        """Edit basic fields for selected product (name only for now)"""
        sku = self.get_selected_sku()
        if not sku:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un produit d'abord")
            return

        prod = self.pm.get_product_by_sku(sku)
        if not prod:
            QMessageBox.warning(self, "Erreur", "Produit introuvable")
            return

        name, ok = QInputDialog.getText(self, "Modifier produit", "Nom:", text=prod.get('name') or '')
        if not ok:
            return

        self.pm.update_product(prod['id'], name=name)
        QMessageBox.information(self, "Succès", "Produit mis à jour")
        self.load_products()

    def handle_delete_product(self):
        sku = self.get_selected_sku()
        if not sku:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un produit d'abord")
            return

        prod = self.pm.get_product_by_sku(sku)
        if not prod:
            QMessageBox.warning(self, "Erreur", "Produit introuvable")
            return

        resp = QMessageBox.question(self, "Confirmer", f"Supprimer {prod.get('name')} ?")
        if resp == QMessageBox.Yes:
            self.pm.delete_product(prod['id'])
            self.load_products()

    def handle_entry_stock(self):
        sku = self.get_selected_sku()
        if not sku:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un produit d'abord")
            return

        prod = self.pm.get_product_by_sku(sku)
        if not prod:
            QMessageBox.warning(self, "Erreur", "Produit introuvable")
            return

        qty, ok = QInputDialog.getInt(self, "Entrée Stock", "Quantité à ajouter:", 1, 1)
        if not ok:
            return

        self.pm.add_stock(prod['id'], qty, reason='Manual entry')
        QMessageBox.information(self, "Succès", "Stock mis à jour")
        self.load_products()

    def handle_exit_stock(self):
        sku = self.get_selected_sku()
        if not sku:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un produit d'abord")
            return

        prod = self.pm.get_product_by_sku(sku)
        if not prod:
            QMessageBox.warning(self, "Erreur", "Produit introuvable")
            return

        qty, ok = QInputDialog.getInt(self, "Sortie Stock", "Quantité à retirer:", 1, 1)
        if not ok:
            return

        ok2 = self.pm.remove_stock(prod['id'], qty, reason='Manual removal')
        if ok2:
            QMessageBox.information(self, "Succès", "Stock mis à jour")
        else:
            QMessageBox.warning(self, "Erreur", "Quantité insuffisante")

        self.load_products()

    def handle_inventory(self):
        QMessageBox.information(self, "Inventaire", "Fonction Inventaire: à développer")

    def handle_lots(self):
        """Manage product lots (advanced inventory)"""
        if not self.pm:
            QMessageBox.warning(self, "Erreur", "Base de données non disponible")
            return

        sku = self.get_selected_sku()
        if not sku:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un produit d'abord")
            return

        prod = self.pm.get_product_by_sku(sku)
        if not prod:
            return

        lot_number, ok = QInputDialog.getText(self, "Ajouter Lot", "N° Lot:")
        if not ok or not lot_number.strip():
            return

        qty, ok2 = QInputDialog.getInt(self, "Quantité", "Quantité:", 1, 1)
        if not ok2:
            return

        if self.adv_inv:
            self.adv_inv.add_lot(prod['id'], qty, lot_number)
            QMessageBox.information(self, "Succès", f"Lot {lot_number} ajouté")

    def handle_fifo_removal(self):
        """Remove stock using FIFO method"""
        if not self.adv_inv:
            QMessageBox.warning(self, "Erreur", "Gestionnaire d'inventaire non disponible")
            return

        prod_id, ok = QInputDialog.getInt(self, "Retrait FIFO", "ID Produit:", 1, 1)
        if not ok:
            return

        qty, ok2 = QInputDialog.getInt(self, "Quantité", "Quantité à retirer:", 1, 1)
        if not ok2:
            return

        result = self.adv_inv.remove_by_fifo(prod_id, qty)
        if result:
            QMessageBox.information(self, "Succès", f"{qty} unité(s) retirée(s) (FIFO)")
        else:
            QMessageBox.warning(self, "Erreur", "Quantité insuffisante")

    def handle_lifo_removal(self):
        """Remove stock using LIFO method"""
        if not self.adv_inv:
            QMessageBox.warning(self, "Erreur", "Gestionnaire d'inventaire non disponible")
            return

        prod_id, ok = QInputDialog.getInt(self, "Retrait LIFO", "ID Produit:", 1, 1)
        if not ok:
            return

        qty, ok2 = QInputDialog.getInt(self, "Quantité", "Quantité à retirer:", 1, 1)
        if not ok2:
            return

        result = self.adv_inv.remove_by_lifo(prod_id, qty)
        if result:
            QMessageBox.information(self, "Succès", f"{qty} unité(s) retirée(s) (LIFO)")
        else:
            QMessageBox.warning(self, "Erreur", "Quantité insuffisante")

# ============================================================================
# 3. CUSTOMERS & SUPPLIERS MODULE
# ============================================================================

class CustomersSupplierModule(QWidget):
    """Customers and Suppliers Management"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """Initialize Customers/Suppliers UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tabs
        tabs = QTabWidget()
        
        # Customers tab
        customers_widget = self.create_customers_tab()
        tabs.addTab(customers_widget, "Clients")
        
        # Suppliers tab
        suppliers_widget = self.create_suppliers_tab()
        tabs.addTab(suppliers_widget, "Fournisseurs")
        
        layout.addWidget(tabs)
    
    def create_customers_tab(self):
        """Create customers tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Rechercher:"))
        search_layout.addWidget(QLineEdit())
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Customers table
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Code", "Nom", "Téléphone", "Email", "Adresse", "Crédit Limité"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Ajouter"))
        button_layout.addWidget(QPushButton("Modifier"))
        button_layout.addWidget(QPushButton("Supprimer"))
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
    
    def create_suppliers_tab(self):
        """Create suppliers tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Rechercher:"))
        search_layout.addWidget(QLineEdit())
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Suppliers table
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Code", "Nom", "Contact", "Téléphone", "Email", "Adresse"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Ajouter"))
        button_layout.addWidget(QPushButton("Modifier"))
        button_layout.addWidget(QPushButton("Supprimer"))
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget

# ============================================================================
# 4. INVOICES MODULE
# ============================================================================

class InvoicesModule(QWidget):
    """Invoices and Receipts Management"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """Initialize Invoices UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Gestion des Factures")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("De:"))
        filter_layout.addWidget(QDateEdit(QDate.currentDate()))
        filter_layout.addWidget(QLabel("À:"))
        filter_layout.addWidget(QDateEdit(QDate.currentDate()))
        filter_layout.addWidget(QPushButton("Filtrer"))
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Invoices table
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Numéro", "Date", "Client", "Montant", "Statut Paiement", "Utilisateur", "Actions"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setMinimumHeight(400)
        layout.addWidget(table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Voir Détails"))
        button_layout.addWidget(QPushButton("Imprimer"))
        button_layout.addWidget(QPushButton("Payer"))
        button_layout.addWidget(QPushButton("Annuler"))
        button_layout.addWidget(QPushButton("Dupliquer"))
        button_layout.addStretch()
        layout.addLayout(button_layout)

# ============================================================================
# 5. REPORTS & ANALYTICS MODULE
# ============================================================================

class ReportsModule(QWidget):
    """Reports and Analytics"""
    
    def __init__(self, user, db=None):
        super().__init__()
        self.user = user
        self.db = db
        self.rm = ReportManager(db) if db is not None else None
        self.init_ui()
    
    def init_ui(self):
        """Initialize Reports UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Rapports et Analyses")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Report selection
        report_group = QGroupBox("Sélectionner un rapport")
        report_layout = QHBoxLayout()
        
        reports = [
            "Ventes Journalières",
            "Ventes Mensuelles",
            "Top Produits",
            "Top Clients",
            "Inventaire",
            "Créances"
        ]
        
        for report in reports:
            btn = QPushButton(report)
            btn.clicked.connect(lambda checked, r=report: self.generate_report(r))
            report_layout.addWidget(btn)
        
        report_group.setLayout(report_layout)
        layout.addWidget(report_group)
        
        # Summary widgets
        summary_layout = QHBoxLayout()
        self.lbl_daily = QLabel("Ventes aujourd'hui: -- | 0.00 DZD")
        self.lbl_monthly = QLabel("Ventes ce mois: -- | 0.00 DZD")
        summary_layout.addWidget(self.lbl_daily)
        summary_layout.addWidget(self.lbl_monthly)
        summary_layout.addStretch()
        layout.addLayout(summary_layout)

        # Top products table
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(4)
        self.top_table.setHorizontalHeaderLabels(["Produit", "Quantité vendue", "Chiffre (DZD)", "ID"])
        self.top_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.top_table.setMinimumHeight(300)
        layout.addWidget(self.top_table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        btn_pdf = QPushButton("Exporter PDF")
        btn_xlsx = QPushButton("Exporter Excel")
        btn_print = QPushButton("Imprimer")
        export_layout.addWidget(btn_pdf)
        export_layout.addWidget(btn_xlsx)
        export_layout.addWidget(btn_print)
        export_layout.addStretch()
        layout.addLayout(export_layout)

        # Load initial stats
        self.load_stats()

        # Connect report buttons (also call load_stats for summary types)
        for i in range(report_layout.count()):
            w = report_layout.itemAt(i).widget()
            if w:
                w.clicked.connect(lambda checked, r=w.text(): self.generate_report(r))

        btn_pdf.clicked.connect(lambda: QMessageBox.information(self, "Export", "Export PDF: à implémenter"))
        btn_xlsx.clicked.connect(lambda: QMessageBox.information(self, "Export", "Export Excel: à implémenter"))
        btn_print.clicked.connect(lambda: QMessageBox.information(self, "Imprimer", "Imprimer: à implémenter"))
    
    def generate_report(self, report_type):
        """Generate selected report"""
        # For basic reports, update summary / table
        if not self.rm:
            QMessageBox.warning(self, "Erreur", "Base de données non disponible pour générer le rapport")
            return

        now = datetime.now()
        if report_type == "Ventes Journalières":
            d = now.strftime('%Y-%m-%d')
            r = self.rm.daily_sales(d)
            self.report_text.setText(f"Ventes pour {d}: {r['invoices']} factures - Total: {r['total']:.2f}")
        elif report_type == "Ventes Mensuelles":
            y = now.year
            m = now.month
            r = self.rm.monthly_sales(y, m)
            self.report_text.setText(f"Ventes pour {r['year']}-{r['month']}: {r['invoices']} factures - Total: {r['total']:.2f}")
        elif report_type == "Top Produits":
            top = self.rm.top_products(10)
            txt = "Top Produits:\n"
            for p in top:
                txt += f"{p['name']}: {p['quantity']} unités, {p['revenue']:.2f} DZD\n"
            self.report_text.setText(txt)
            self.load_top_products_table(top)
        else:
            self.report_text.setText(f"Rapport: {report_type}\n(Données non implémentées)")

    def load_stats(self):
        """Load today's and this month's summaries and top products"""
        if not self.rm:
            return
        today = datetime.now().strftime('%Y-%m-%d')
        r_today = self.rm.daily_sales(today)
        r_month = self.rm.monthly_sales(datetime.now().year, datetime.now().month)

        self.lbl_daily.setText(f"Ventes aujourd'hui: {r_today['invoices']} | {r_today['total']:.2f} DZD")
        self.lbl_monthly.setText(f"Ventes ce mois: {r_month['invoices']} | {r_month['total']:.2f} DZD")

        top = self.rm.top_products(10)
        self.load_top_products_table(top)

    def load_top_products_table(self, rows):
        self.top_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.top_table.setItem(i, 0, QTableWidgetItem(r['name']))
            self.top_table.setItem(i, 1, QTableWidgetItem(str(r['quantity'])))
            self.top_table.setItem(i, 2, QTableWidgetItem("{:.2f}".format(r['revenue'])))
            self.top_table.setItem(i, 3, QTableWidgetItem(str(r['product_id'])))

# ============================================================================
# 6. USERS MANAGEMENT MODULE
# ============================================================================

class UsersModule(QWidget):
    """User Management (Admin only)"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """Initialize Users UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Gestion des Utilisateurs")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "Utilisateur", "Nom Complet", "Rôle", "Email", "Actif", "Créé le"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setMinimumHeight(400)
        layout.addWidget(self.users_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Ajouter"))
        button_layout.addWidget(QPushButton("Modifier"))
        button_layout.addWidget(QPushButton("Supprimer"))
        button_layout.addWidget(QPushButton("Activer/Désactiver"))
        button_layout.addWidget(QPushButton("Réinitialiser Mot de passe"))
        button_layout.addStretch()
        layout.addLayout(button_layout)

# ============================================================================
# 7. BACKUP & SETTINGS MODULE
# ============================================================================

class BackupModule(QWidget):
    """Backup and System Settings"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.backup_mgr = BackupManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize Backup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Sauvegarde et Paramètres")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Backup section
        backup_group = QGroupBox("Sauvegarde de Base de Données")
        backup_layout = QVBoxLayout()
        
        self.backup_info = QLabel("Dernière sauvegarde: --")
        backup_layout.addWidget(self.backup_info)
        
        backup_button_layout = QHBoxLayout()
        self.btn_backup_now = QPushButton("Sauvegarder Maintenant")
        self.btn_restore = QPushButton("Restaurer")
        self.btn_schedule = QPushButton("Programmation Automatique")
        backup_button_layout.addWidget(self.btn_backup_now)
        backup_button_layout.addWidget(self.btn_restore)
        backup_button_layout.addWidget(self.btn_schedule)
        backup_button_layout.addStretch()
        backup_layout.addLayout(backup_button_layout)

        # Connect actions
        self.btn_backup_now.clicked.connect(self.handle_backup_now)
        self.btn_restore.clicked.connect(self.handle_restore)
        self.btn_schedule.clicked.connect(self.handle_schedule)
        
        # Backup history
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels(["Date", "Heure", "Taille (MB)", "Fichier"])
        self.backup_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        backup_layout.addWidget(self.backup_table)

        # Load existing backups
        self.load_backups()
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Settings section
        settings_group = QGroupBox("Paramètres")
        settings_layout = QFormLayout()
        
        settings_layout.addRow("Nom Entreprise:", QLineEdit("Société XXXXXXXX"))
        settings_layout.addRow("N° Registre Commerce:", QLineEdit())
        settings_layout.addRow("N° STAT:", QLineEdit())
        settings_layout.addRow("Mode TVA:", QComboBox())
        settings_layout.addRow("Devise:", QComboBox())
        settings_layout.addRow("Format Facture:", QComboBox())
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Enregistrer Paramètres"))
        button_layout.addWidget(QPushButton("Réinitialiser à Défaut"))
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()

    # ---------------- Backup handlers ----------------
    def handle_backup_now(self):
        """Create a backup and refresh the list"""
        backup_file, msg = self.backup_mgr.create_backup()
        if backup_file:
            QMessageBox.information(self, "Sauvegarde", msg)
        else:
            QMessageBox.critical(self, "Sauvegarde échouée", msg)
        self.load_backups()

    def handle_restore(self):
        """Restore selected backup or choose one via dialog"""
        # Ask user to select a backup file
        path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier de sauvegarde", self.backup_mgr.backup_dir, "Database Files (*.db);;All Files (*)")
        if not path:
            return

        ok, msg = self.backup_mgr.restore_backup(path)
        if ok:
            QMessageBox.information(self, "Restauration", msg)
        else:
            QMessageBox.critical(self, "Restauration échouée", msg)
        self.load_backups()

    def handle_schedule(self):
        """Stub for scheduling backups - opens a dialog placeholder"""
        QMessageBox.information(self, "Programmation", "Programmation automatique configurée (fonctionnalité basique).")

    def load_backups(self):
        """Populate the backup table with available backups"""
        backups = []
        try:
            backups = self.backup_mgr.list_backups()
        except Exception:
            backups = []

        self.backup_table.setRowCount(0)
        latest = None
        for b in backups:
            row = self.backup_table.rowCount()
            self.backup_table.insertRow(row)
            # split created into date and time
            created = b.get('created', '')
            date_part = created.split(' ')[0] if created else ''
            time_part = created.split(' ')[1] if created and len(created.split(' '))>1 else ''
            size = f"{b.get('size',0):.2f}"
            self.backup_table.setItem(row, 0, QTableWidgetItem(date_part))
            self.backup_table.setItem(row, 1, QTableWidgetItem(time_part))
            self.backup_table.setItem(row, 2, QTableWidgetItem(size))
            self.backup_table.setItem(row, 3, QTableWidgetItem(b.get('file','')))
            if not latest:
                latest = created

        if latest:
            self.backup_info.setText(f"Dernière sauvegarde: {latest}")
        else:
            self.backup_info.setText("Dernière sauvegarde: --")


# ============================================================================
# 8. ADMIN MODULE - Advanced Features
# ============================================================================

class AdminModule(QWidget):
    """Administration Panel - Purchase Orders, Loyalty, Promotions, E-commerce, Payments"""

    def __init__(self, user, db=None):
        super().__init__()
        self.user = user
        self.db = db
        self.po_mgr = PurchaseOrderManager(db) if db is not None else None
        self.loyalty_mgr = LoyaltyManager(db) if db is not None else None
        self.promo_mgr = PromotionsManager(db) if db is not None else None
        self.payment_proc = PaymentProcessor() if db is not None else None
        self.ecom_mgr = EcommerceSyncManager(db) if db is not None else None
        self.init_ui()

    def init_ui(self):
        """Initialize Admin UI with tabs for different features"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("Administration - Fonctionnalités Avancées")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)

        # Tab widget for different admin features
        self.tabs = QTabWidget()

        # Tab 1: Purchase Orders
        self.tabs.addTab(self.create_purchase_orders_tab(), "Commandes d'Achat")

        # Tab 2: Loyalty Program
        self.tabs.addTab(self.create_loyalty_tab(), "Programme Fidélité")

        # Tab 3: Promotions & Coupons
        self.tabs.addTab(self.create_promotions_tab(), "Promotions & Coupons")

        # Tab 4: Payments
        self.tabs.addTab(self.create_payments_tab(), "Paiements")

        # Tab 5: E-commerce Sync
        self.tabs.addTab(self.create_ecommerce_tab(), "Sync E-commerce")

        layout.addWidget(self.tabs)

    def create_purchase_orders_tab(self):
        """Purchase Orders management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QGroupBox("Créer Commande d'Achat")
        header_layout = QFormLayout()
        header_layout.addRow("Fournisseur:", QComboBox())
        header_layout.addRow("Numéro PO:", QLineEdit())
        header_layout.addRow("Notes:", QTextEdit())
        header.setLayout(header_layout)
        layout.addWidget(header)

        # PO Items table
        po_table = QTableWidget()
        po_table.setColumnCount(4)
        po_table.setHorizontalHeaderLabels(["Produit", "Quantité", "P.Unitaire", "Total"])
        po_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(po_table)

        # Buttons
        button_layout = QHBoxLayout()
        btn_add_item = QPushButton("Ajouter Ligne")
        btn_create_po = QPushButton("Créer PO")
        btn_receive = QPushButton("Réceptionner PO")
        btn_list = QPushButton("Voir POs")

        btn_add_item.clicked.connect(lambda: QMessageBox.information(widget, "Info", "Ajouter ligne PO"))
        btn_create_po.clicked.connect(lambda: self.handle_create_po())
        btn_receive.clicked.connect(lambda: self.handle_receive_po())
        btn_list.clicked.connect(lambda: self.handle_list_pos())

        button_layout.addWidget(btn_add_item)
        button_layout.addWidget(btn_create_po)
        button_layout.addWidget(btn_receive)
        button_layout.addWidget(btn_list)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        return widget

    def create_loyalty_tab(self):
        """Loyalty program management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QGroupBox("Gestion Fidélité Client")
        header_layout = QFormLayout()
        header_layout.addRow("Client:", QComboBox())
        header_layout.addRow("Points à Ajouter:", QSpinBox())
        header_layout.addRow("Raison:", QLineEdit())
        header.setLayout(header_layout)
        layout.addWidget(header)

        # Loyalty log table
        loyalty_table = QTableWidget()
        loyalty_table.setColumnCount(5)
        loyalty_table.setHorizontalHeaderLabels(["Client", "Points", "Type", "Raison", "Date"])
        loyalty_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(loyalty_table)

        # Buttons
        button_layout = QHBoxLayout()
        btn_add_points = QPushButton("Ajouter Points")
        btn_redeem = QPushButton("Utiliser Points")
        btn_history = QPushButton("Historique Client")

        btn_add_points.clicked.connect(lambda: self.handle_add_loyalty_points())
        btn_redeem.clicked.connect(lambda: self.handle_redeem_loyalty())
        btn_history.clicked.connect(lambda: QMessageBox.information(widget, "Info", "Afficher historique"))

        button_layout.addWidget(btn_add_points)
        button_layout.addWidget(btn_redeem)
        button_layout.addWidget(btn_history)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        return widget

    def create_promotions_tab(self):
        """Promotions and Coupons management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QGroupBox("Créer Promotion")
        header_layout = QFormLayout()
        header_layout.addRow("Nom Promo:", QLineEdit())
        header_layout.addRow("Réduction (%):", QSpinBox())
        header_layout.addRow("Date Début:", QDateEdit(QDate.currentDate()))
        header_layout.addRow("Date Fin:", QDateEdit(QDate.currentDate()))
        header_layout.addRow("Montant Min:", QSpinBox())
        header.setLayout(header_layout)
        layout.addWidget(header)

        # Coupons section
        coupons_group = QGroupBox("Coupons")
        coupons_layout = QFormLayout()
        coupons_layout.addRow("Code Coupon:", QLineEdit())
        coupons_layout.addRow("Réduction (%):", QSpinBox())
        coupons_layout.addRow("Valide Jusqu'au:", QDateEdit(QDate.currentDate()))
        coupons_group.setLayout(coupons_layout)
        layout.addWidget(coupons_group)

        # Promotions table
        promo_table = QTableWidget()
        promo_table.setColumnCount(5)
        promo_table.setHorizontalHeaderLabels(["Nom", "Réduction", "Début", "Fin", "Actif"])
        promo_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(promo_table)

        # Buttons
        button_layout = QHBoxLayout()
        btn_create_promo = QPushButton("Créer Promotion")
        btn_create_coupon = QPushButton("Créer Coupon")
        btn_apply = QPushButton("Appliquer Promotion")

        btn_create_promo.clicked.connect(lambda: self.handle_create_promotion())
        btn_create_coupon.clicked.connect(lambda: self.handle_create_coupon())
        btn_apply.clicked.connect(lambda: QMessageBox.information(widget, "Info", "Appliquer à panier"))

        button_layout.addWidget(btn_create_promo)
        button_layout.addWidget(btn_create_coupon)
        button_layout.addWidget(btn_apply)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        return widget

    def create_payments_tab(self):
        """Payment methods management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Payment methods configuration
        payment_group = QGroupBox("Configuration des Paiements")
        payment_layout = QFormLayout()

        # Cash
        cb_cash = QCheckBox("Espèces")
        cb_cash.setChecked(True)
        payment_layout.addRow(cb_cash)

        # Check
        cb_check = QCheckBox("Chèque")
        payment_layout.addRow(cb_check)

        # Card
        cb_card = QCheckBox("Carte Bancaire")
        payment_layout.addRow(cb_card)

        # Stripe config
        stripe_group = QGroupBox("Configuration Stripe")
        stripe_layout = QFormLayout()
        stripe_layout.addRow("Clé API:", QLineEdit())
        stripe_layout.addRow("Clé Publique:", QLineEdit())
        stripe_group.setLayout(stripe_layout)
        layout.addWidget(stripe_group)

        # PayPal config
        paypal_group = QGroupBox("Configuration PayPal")
        paypal_layout = QFormLayout()
        paypal_layout.addRow("Client ID:", QLineEdit())
        paypal_layout.addRow("Secret:", QLineEdit())
        paypal_group.setLayout(paypal_layout)
        layout.addWidget(paypal_group)

        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)

        # Card Terminal config
        terminal_group = QGroupBox("Terminal de Paiement")
        terminal_layout = QFormLayout()
        terminal_layout.addRow("Port Série:", QLineEdit("COM3"))
        terminal_layout.addRow("Vitesse (baud):", QSpinBox())
        terminal_group.setLayout(terminal_layout)
        layout.addWidget(terminal_group)

        # Test button
        btn_test = QPushButton("Tester Connexion")
        btn_test.clicked.connect(lambda: QMessageBox.information(widget, "Test", "Connexion réussie"))
        layout.addWidget(btn_test)

        layout.addStretch()
        return widget

    def create_ecommerce_tab(self):
        """E-commerce synchronization tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Shopify section
        shopify_group = QGroupBox("Shopify")
        shopify_layout = QFormLayout()
        shopify_layout.addRow("URL Boutique:", QLineEdit("https://example.myshopify.com"))
        shopify_layout.addRow("Token API:", QLineEdit())
        shopify_group.setLayout(shopify_layout)
        layout.addWidget(shopify_group)

        # WooCommerce section
        woo_group = QGroupBox("WooCommerce")
        woo_layout = QFormLayout()
        woo_layout.addRow("URL Site:", QLineEdit("https://example.com"))
        woo_layout.addRow("Clé Consommateur:", QLineEdit())
        woo_layout.addRow("Secret Consommateur:", QLineEdit())
        woo_group.setLayout(woo_layout)
        layout.addWidget(woo_group)

        # Sync status
        status_group = QGroupBox("Statut Synchronisation")
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel("Dernière synchro produits: --"))
        status_layout.addWidget(QLabel("Dernière synchro commandes: --"))
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Buttons
        button_layout = QHBoxLayout()
        btn_sync_products = QPushButton("Synchro Produits")
        btn_sync_orders = QPushButton("Télécharger Commandes")
        btn_test_conn = QPushButton("Tester Connexion")

        btn_sync_products.clicked.connect(lambda: self.handle_ecom_sync_products())
        btn_sync_orders.clicked.connect(lambda: self.handle_ecom_sync_orders())
        btn_test_conn.clicked.connect(lambda: QMessageBox.information(widget, "Test", "Connexion réussie"))

        button_layout.addWidget(btn_sync_products)
        button_layout.addWidget(btn_sync_orders)
        button_layout.addWidget(btn_test_conn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addStretch()
        return widget

    # ============== Handler Methods ==============

    def handle_create_po(self):
        """Create a new purchase order"""
        QMessageBox.information(self, "Commande d'Achat", "Commande créée avec succès!")

    def handle_receive_po(self):
        """Receive/complete a purchase order"""
        po_id, ok = QInputDialog.getInt(self, "Réceptionner PO", "ID de la PO:", 1, 1)
        if ok and self.po_mgr:
            self.po_mgr.receive_po(po_id)
            QMessageBox.information(self, "Succès", "PO marquée comme reçue")

    def handle_list_pos(self):
        """List all purchase orders"""
        if self.po_mgr:
            pos = self.po_mgr.list_pos()
            QMessageBox.information(self, "Commandes", f"Total POs: {len(pos) if pos else 0}")

    def handle_add_loyalty_points(self):
        """Add loyalty points to a customer"""
        customer_id, ok = QInputDialog.getInt(self, "Ajouter Points", "ID Client:", 1, 1)
        if not ok:
            return

        points, ok2 = QInputDialog.getInt(self, "Points", "Nombre de points:", 10, 1)
        if ok2 and self.loyalty_mgr:
            self.loyalty_mgr.add_points(customer_id, points, "Manual Addition")
            QMessageBox.information(self, "Succès", f"{points} points ajoutés")

    def handle_redeem_loyalty(self):
        """Redeem loyalty points"""
        customer_id, ok = QInputDialog.getInt(self, "Utiliser Points", "ID Client:", 1, 1)
        if not ok:
            return

        points, ok2 = QInputDialog.getInt(self, "Points", "Points à utiliser:", 10, 1)
        if ok2 and self.loyalty_mgr:
            self.loyalty_mgr.redeem_points(customer_id, points)
            QMessageBox.information(self, "Succès", f"{points} points utilisés")

    def handle_create_promotion(self):
        """Create a new promotion"""
        name, ok = QInputDialog.getText(self, "Promotion", "Nom de la promotion:")
        if ok and name and self.promo_mgr:
            self.promo_mgr.create_promotion(name, 10, "2024-01-01", "2024-12-31", 100)
            QMessageBox.information(self, "Succès", f"Promotion '{name}' créée")

    def handle_create_coupon(self):
        """Create a coupon code"""
        code, ok = QInputDialog.getText(self, "Coupon", "Code du coupon:")
        if ok and code and self.promo_mgr:
            self.promo_mgr.create_coupon(code, 15, "2024-12-31")
            QMessageBox.information(self, "Succès", f"Coupon '{code}' créé")

    def handle_ecom_sync_products(self):
        """Sync products to e-commerce platforms"""
        if self.ecom_mgr:
            self.ecom_mgr.sync_products_to_platform("shopify")
            QMessageBox.information(self, "Synchro", "Produits synchronisés vers Shopify")

    def handle_ecom_sync_orders(self):
        """Download orders from e-commerce platforms"""
        if self.ecom_mgr:
            self.ecom_mgr.sync_orders_from_platform("woocommerce")

# ============================================================================
# 8. VIDEO MODULE - Training & Tutorial Videos
# ============================================================================

class VideoModule(QWidget):
    """Video Player - Tutorial & Training Videos"""
    
    def __init__(self, user, db=None):
        super().__init__()
        self.user = user
        self.db = db
        self.media_player = QMediaPlayer()
        self.current_video = None
        self.videos_dir = "data/videos"
        self.init_ui()
        self.load_videos()
    
    def init_ui(self):
        """Initialize Video Module UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("📹 Centre de Tutoriels Vidéo")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Main video container
        container = QHBoxLayout()
        
        # Left: Video player
        video_group = QGroupBox("Lecteur Vidéo")
        video_layout = QVBoxLayout()
        
        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(300)
        self.media_player.setVideoOutput(self.video_widget)
        video_layout.addWidget(self.video_widget)
        
        # Playback controls
        control_layout = QHBoxLayout()
        
        self.btn_play = QPushButton("▶ Lecture")
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_stop = QPushButton("⏹ Arrêt")
        self.btn_mute = QPushButton("🔊 Son")
        
        self.btn_play.clicked.connect(self.play_video)
        self.btn_pause.clicked.connect(self.media_player.pause)
        self.btn_stop.clicked.connect(self.media_player.stop)
        self.btn_mute.clicked.connect(self.toggle_mute)
        
        control_layout.addWidget(self.btn_play)
        control_layout.addWidget(self.btn_pause)
        control_layout.addWidget(self.btn_stop)
        control_layout.addStretch()
        control_layout.addWidget(self.btn_mute)
        video_layout.addLayout(control_layout)
        
        # Progress slider
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Durée:"))
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.sliderMoved.connect(self.set_position)
        progress_layout.addWidget(self.progress_slider)
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(100)
        progress_layout.addWidget(self.time_label)
        video_layout.addLayout(progress_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(150)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addStretch()
        video_layout.addLayout(volume_layout)
        
        # Video info
        self.video_info = QLabel("Aucune vidéo sélectionnée")
        self.video_info.setWordWrap(True)
        self.video_info.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        video_layout.addWidget(self.video_info)
        
        video_group.setLayout(video_layout)
        container.addWidget(video_group, 2)
        
        # Right: Video playlist
        playlist_group = QGroupBox("Playlist des Tutoriels")
        playlist_layout = QVBoxLayout()
        
        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Catégorie:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Tous", "Vente", "Stock", "Clients", "Rapports", "Administration"])
        self.category_combo.currentTextChanged.connect(self.filter_videos)
        filter_layout.addWidget(self.category_combo)
        filter_layout.addStretch()
        playlist_layout.addLayout(filter_layout)
        
        # Video list
        self.video_table = QTableWidget()
        self.video_table.setColumnCount(3)
        self.video_table.setHorizontalHeaderLabels(["Titre", "Durée", "Catégorie"])
        self.video_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.video_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.video_table.setSelectionMode(QTableWidget.SingleSelection)
        self.video_table.itemClicked.connect(self.on_video_selected)
        self.video_table.itemDoubleClicked.connect(self.play_selected_video)
        playlist_layout.addWidget(self.video_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.btn_add_video = QPushButton("➕ Ajouter vidéo")
        self.btn_delete_video = QPushButton("🗑 Supprimer")
        self.btn_download = QPushButton("⬇ Télécharger")
        
        self.btn_add_video.clicked.connect(self.handle_add_video)
        self.btn_delete_video.clicked.connect(self.handle_delete_video)
        self.btn_download.clicked.connect(self.handle_download_video)
        
        action_layout.addWidget(self.btn_add_video)
        action_layout.addWidget(self.btn_delete_video)
        action_layout.addWidget(self.btn_download)
        action_layout.addStretch()
        playlist_layout.addLayout(action_layout)
        
        playlist_group.setLayout(playlist_layout)
        container.addWidget(playlist_group, 1)
        
        layout.addLayout(container, 1)
        
        # Connect media player signals
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        
        self.is_muted = False
    
    def load_videos(self):
        """Load available videos from directory"""
        # Create videos directory if it doesn't exist
        if not os.path.exists(self.videos_dir):
            os.makedirs(self.videos_dir)
        
        # Sample videos data (in production, could be from database)
        self.videos = [
            {"title": "🎓 Tutoriel Point de Vente", "file": "pos_tutorial.mp4", "duration": "15:30", "category": "Vente"},
            {"title": "📦 Gestion du Stock", "file": "stock_tutorial.mp4", "duration": "12:45", "category": "Stock"},
            {"title": "👥 Gestion des Clients", "file": "customers_tutorial.mp4", "duration": "10:20", "category": "Clients"},
            {"title": "📊 Génération des Rapports", "file": "reports_tutorial.mp4", "duration": "18:15", "category": "Rapports"},
            {"title": "⚙ Configuration Système", "file": "admin_tutorial.mp4", "duration": "25:00", "category": "Administration"},
            {"title": "💳 Traitement des Paiements", "file": "payments_tutorial.mp4", "duration": "14:30", "category": "Vente"},
        ]
        
        self.refresh_video_list()
    
    def refresh_video_list(self):
        """Refresh the video list in the table"""
        self.video_table.setRowCount(len(self.videos))
        
        for i, video in enumerate(self.videos):
            title_item = QTableWidgetItem(video["title"])
            duration_item = QTableWidgetItem(video["duration"])
            category_item = QTableWidgetItem(video["category"])
            
            self.video_table.setItem(i, 0, title_item)
            self.video_table.setItem(i, 1, duration_item)
            self.video_table.setItem(i, 2, category_item)
        
        self.video_table.resizeRowsToContents()
    
    def filter_videos(self):
        """Filter videos by category"""
        category = self.category_combo.currentText()
        
        for i in range(self.video_table.rowCount()):
            if category == "Tous":
                self.video_table.setRowHidden(i, False)
            else:
                cat_item = self.video_table.item(i, 2)
                visible = cat_item.text() == category if cat_item else False
                self.video_table.setRowHidden(i, not visible)
    
    def on_video_selected(self, item):
        """Handle video selection from list"""
        row = self.video_table.row(item)
        if 0 <= row < len(self.videos):
            self.current_video = self.videos[row]
            self.display_video_info()
    
    def display_video_info(self):
        """Display information about selected video"""
        if self.current_video:
            info_text = f"""
            <b>{self.current_video['title']}</b><br>
            <br>
            <b>Catégorie:</b> {self.current_video['category']}<br>
            <b>Durée:</b> {self.current_video['duration']}<br>
            <b>Fichier:</b> {self.current_video['file']}<br>
            <br>
            <i>Double-cliquez pour lire la vidéo</i>
            """
            self.video_info.setText(info_text)
    
    def play_selected_video(self, item=None):
        """Play the selected video"""
        if not self.current_video:
            QMessageBox.warning(self, "Attention", "Sélectionnez une vidéo d'abord")
            return
        
        video_path = os.path.join(self.videos_dir, self.current_video['file'])
        
        # For demo purposes, we'll just show a message
        # In production, the actual video file would be loaded
        if not os.path.exists(video_path):
            QMessageBox.information(self, "Vidéo", 
                f"Lecture de: {self.current_video['title']}\n\n"
                f"Fichier: {self.current_video['file']}\n"
                f"Durée: {self.current_video['duration']}\n\n"
                "Note: Fichier vidéo non trouvé. En production, il serait lu ici.")
            return
        
        self.media_player.setMedia(QUrl.fromLocalFile(video_path))
        self.play_video()
    
    def play_video(self):
        """Start video playback"""
        if self.current_video:
            self.media_player.play()
    
    def toggle_mute(self):
        """Toggle audio mute"""
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.media_player.setVolume(0)
            self.btn_mute.setText("🔇 Mute")
        else:
            self.media_player.setVolume(self.volume_slider.value())
            self.btn_mute.setText("🔊 Son")
    
    def set_volume(self, value):
        """Set player volume"""
        if not self.is_muted:
            self.media_player.setVolume(value)
    
    def set_position(self, position):
        """Set video position"""
        self.media_player.setPosition(position)
    
    def update_position(self, position):
        """Update position slider"""
        self.progress_slider.setValue(position)
        self.update_time_label()
    
    def update_duration(self, duration):
        """Update duration display"""
        self.progress_slider.setMaximum(duration)
        self.update_time_label()
    
    def update_time_label(self):
        """Update time display"""
        position = self.media_player.position()
        duration = self.media_player.duration()
        
        pos_min = position // 60000
        pos_sec = (position % 60000) // 1000
        dur_min = duration // 60000
        dur_sec = (duration % 60000) // 1000
        
        time_text = f"{pos_min:02d}:{pos_sec:02d} / {dur_min:02d}:{dur_sec:02d}"
        self.time_label.setText(time_text)
    
    def on_media_status_changed(self, status):
        """Handle media status changes"""
        if status == QMediaPlayer.EndOfMedia:
            # Auto-play next video or show completion message
            QMessageBox.information(self, "Vidéo terminée", 
                f"{self.current_video['title']} est terminée.")
    
    def handle_add_video(self):
        """Add a new video to the playlist"""
        title, ok = QInputDialog.getText(self, "Ajouter vidéo", "Titre de la vidéo:")
        if not ok or not title:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner fichier vidéo",
            self.videos_dir, "Video Files (*.mp4 *.avi *.mov);;All Files (*)")
        
        if file_path:
            filename = os.path.basename(file_path)
            category, ok = QInputDialog.getItem(self, "Catégorie", "Choisir la catégorie:",
                ["Vente", "Stock", "Clients", "Rapports", "Administration"], 0, False)
            
            if ok:
                self.videos.append({
                    "title": title,
                    "file": filename,
                    "duration": "00:00",
                    "category": category
                })
                self.refresh_video_list()
                QMessageBox.information(self, "Succès", f"Vidéo '{title}' ajoutée")
    
    def handle_delete_video(self):
        """Delete selected video"""
        if not self.current_video:
            QMessageBox.warning(self, "Attention", "Sélectionnez une vidéo")
            return
        
        reply = QMessageBox.question(self, "Confirmation",
            f"Supprimer '{self.current_video['title']}'?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.videos = [v for v in self.videos if v != self.current_video]
            self.current_video = None
            self.refresh_video_list()
            self.video_info.setText("Aucune vidéo sélectionnée")
            QMessageBox.information(self, "Succès", "Vidéo supprimée")
    
    def handle_download_video(self):
        """Download video tutorials from server"""
        QMessageBox.information(self, "Téléchargement",
            "Connexion au serveur de tutoriels...\n\n"
            "Les mises à jour vidéo seront téléchargées automatiquement.")

