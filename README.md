# 🏥 MediStock - Medical Inventory Management System

![MediStock Dashboard Screenshot](https://via.placeholder.com/900x300?text=MediStock+Dashboard+Preview)

## 🚀 Overview

**MediStock** is a modern, responsive web application for managing medical inventory in pharmacies, clinics, or hospitals.  
It helps you track products, vendors, orders, sales, and stock levels with an intuitive dashboard.

---

## ✨ Features

- 📦 **Product Management:** Add, edit, and monitor medicines with expiry and stock alerts.
- 📊 **Dashboard Analytics:** Real-time stats for profit, inventory, out-of-stock, and expired products.
- 🏆 **Most Selling Medicines:** See your top-selling products at a glance.
- 🔔 **Smart Alerts:** Low stock and expiry notifications.
- 🛒 **Quick Sell:** Sell products directly from the dashboard and auto-update stock.
- 🔍 **Search & Filter:** Instantly find products and filter by stock, price, or expiry.
- 👥 **Vendor Management:** Track suppliers and their products.
- 📑 **Order & Transaction History:** View all sales and purchase records.
- 📱 **Responsive Design:** Works beautifully on desktop and mobile.

---

## 🖥️ Screenshots

| Dashboard | Product Card | Sell Modal |
|-----------|--------------|------------|
| ![Dashboard](https://via.placeholder.com/300x180?text=Dashboard) | ![Product Card](https://via.placeholder.com/300x180?text=Product+Card) | ![Sell Modal](https://via.placeholder.com/300x180?text=Sell+Modal) |

---

## ⚙️ Tech Stack

- **Backend:** Django, PostgreSQL
- **Frontend:** HTML5, CSS3, JavaScript, [Font Awesome](https://fontawesome.com/)
- **Other:** Django ORM, Bootstrap (optional for rapid UI)

---

## 🛠️ Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/medistock.git
   cd medistock
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your database in `settings.py`** (PostgreSQL recommended).

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the app:**  
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 📋 Usage Tips

- Use the **dashboard** for a quick overview and to sell products.
- Add or edit products, vendors, and transactions via the Django admin panel.
- Use the search and filter options to quickly find medicines.
- Watch for **low stock** and **expiry** badges to avoid shortages and losses.

---

## 🤝 Contributing

Pull requests are welcome!  
For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [Django](https://www.djangoproject.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Font Awesome](https://fontawesome.com/)
- [Unsplash](https://unsplash.com/) for placeholder images

---

> **MediStock** – Making medical inventory management simple,