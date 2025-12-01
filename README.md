# Clothing Store Mobile Manager

A comprehensive mobile application for clothing store management, featuring inventory tracking, billing, trial item ledger (try-before-buy), vendor management, and sales reports. Designed for Android using Python with a modern Material Design UI. Fully offline with SQLite database.

## 🚀 Features

- **User Authentication**: Secure login with roles.
- **Dashboard**: Quick overview of stock, sales, trials.
- **Inventory Management**: Add/search products by barcode, name, size/color. Linked to vendors.
- **Billing**: Scan/add items, calculate totals, generate PDF invoices.
- **Trial Ledger**: Track customer trials – checkout items without sale, mark as returned or purchased.
- **Vendor Reports**: Analyze sales by vendor to identify top performers.
- **Touch-Friendly UI**: Responsive Material Design for mobile screens.
- **Offline-First**: SQLite database, no internet required.
- **PDF Export**: Professional invoices.
- **Android Ready**: Permissions for camera/storage, easy APK build.

## 🛠️ Tech Stack

| Component       | Technology          | Purpose |
|-----------------|---------------------|---------|
| **Frontend**    | [KivyMD](https://kivymd.readthedocs.io/) | Material Design UI for Android/iOS |
| **Backend**     | Python 3, SQLite    | Modular OOP logic, local DB |
| **Packaging**   | [Buildozer](https://buildozer.readthedocs.io/) | Compile to APK |
| **PDF**         | ReportLab           | Invoice generation |
| **Permissions** | Plyer               | Android camera/storage access |
| **Models**      | Pydantic/SQLAlchemy | Data validation & ORM-like |

## 📁 Project Structure

```
Clothing_Store_Mobile/
│
├── main.py                   # KivyMD App entrypoint
├── assets/                   # Images, fonts, icons
│
├── database/
│   ├── db_handler.py         # DB connection & schema init
│   └── queries.py            # CRUD operations
│
├── models/
│   ├── product.py            # Product model
│   ├── vendor.py             # Vendor model
│   └── trial_ledger.py       # Trial tracking model
│
├── screens/                  # KivyMD screens (.py + .kv)
│   ├── login_screen.py       # / login.kv
│   ├── dashboard.py          # / dashboard.kv
│   ├── billing_screen.py     # / billing.kv
│   ├── inventory.py          # / inventory.kv
│   ├── ledger_screen.py      # / ledger.kv
│   └── reports_screen.py     # / reports.kv
│
└── utils/
    ├── pdf_generator.py      # Invoice PDFs
    └── permissions.py        # Android permissions
```

## 🏗️ Database Schema

```sql
-- users: Authentication
CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT);

-- vendors: Suppliers
CREATE TABLE vendors (id INTEGER PRIMARY KEY, name TEXT, contact_info TEXT, total_items_supplied INTEGER);

-- products: Clothing items (linked to vendor)
CREATE TABLE products (id INTEGER PRIMARY KEY, vendor_id INTEGER, name TEXT, barcode TEXT UNIQUE, size TEXT, color TEXT, buy_price REAL, sell_price REAL, stock_quantity INTEGER);

-- invoices: Sales records
CREATE TABLE invoices (id INTEGER PRIMARY KEY, invoice_number TEXT UNIQUE, date TEXT, cashier_name TEXT, total_amount REAL);

-- invoice_items: Line items
CREATE TABLE invoice_items (id INTEGER PRIMARY KEY, invoice_id INTEGER, product_id INTEGER, quantity INTEGER, price_at_sale REAL);

-- trial_ledger: Try-before-buy tracking
CREATE TABLE trial_ledger (id INTEGER PRIMARY KEY, customer_name TEXT, customer_phone TEXT, product_id INTEGER, date_taken TEXT, status TEXT);  -- 'On_Trial', 'Returned', 'Purchased'
```

## 🚀 Quick Start (Desktop Development)

1. **Clone & Install Dependencies**:
   ```bash
   git clone <repo>
   cd Clothing_Store_Mobile
   pip install kivy kivymd plyer reportlab
   ```

2. **Run App**:
   ```bash
   python main.py
   ```

   Database auto-initializes on first run.

## 📱 Building Android APK

1. **Install Buildozer** (Linux/WSL recommended for Windows):
   ```bash
   pip install buildozer cython
   ```

2. **Init & Configure**:
   ```bash
   buildozer init
   ```
   Edit [`buildozer.spec`](buildozer.spec) :
   ```
   [app]
   requirements = python3,kivy,kivymd,plyer,reportlab,pillow

   android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
   ```

3. **Build & Install**:
   ```bash
   buildozer android debug
   ```
   APK in `bin/` folder. Install via `adb install`.

## 📖 Usage Guide

### 1. **Login**
- Default: `admin` / `admin123` (hash protected).

### 2. **Dashboard**
- Stats: Total stock, pending trials, today's sales.

### 3. **Inventory**
- Add products: Select vendor, enter details (barcode auto-generates if empty).
- Search: By barcode/name/size.

### 4. **Billing**
- Enter barcode → Add to cart.
- FAB: Finalize → Generate PDF invoice.

### 5. **Trial Ledger** (New Feature)
- **Checkout Trial**: Select product → Enter customer details → Stock decrements, status 'On_Trial'.
- List shows: Customer, Item, Date.
- Tap item → Dialog: "Returned" (stock++) or "Sold" (create invoice).

### 6. **Reports**
- Vendor sales summary: Items sold per vendor.

## 🔄 Key Workflows

### Trial (Try-Before-Buy)
1. Checkout: `checkout_for_trial()` → Stock--, Ledger 'On_Trial'.
2. Return: `return_from_trial()` → Stock++, 'Returned'.
3. Purchase: `convert_trial_to_sale()` → Invoice created, 'Purchased'.

### Vendor Tracking
- Products FK to `vendor_id`.
- Reports: `SUM(quantity) GROUP BY vendor_id`.

## 🐛 Troubleshooting

- **KivyMD Icons Missing**: Ensure `kivymd==1.1.1+` in requirements.
- **Buildozer Errors**: Check `adb logcat | grep python`.
- **DB Issues**: Delete `store.db` to reinitialize.

## 🚀 Future Enhancements
- Camera barcode scanner (Plyer).
- Cloud sync (Firebase).
- Push notifications for low stock.
- Multi-store support.

## 🤝 Contributing
1. Fork & PR.
2. Follow PEP8.
3. Add tests.

## 📄 License
MIT License - Free to use/modify.

## 🙏 Acknowledgments
Built with [KivyMD](https://kivymd.readthedocs.io/), inspired by FMCG inventory pivoted to clothing mobile.

---
*Version 1.0 | Built for Android Clothing Stores*