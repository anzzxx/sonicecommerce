# 🛒 Sonic – Full-Stack E-Commerce Platform

**Sonic** is a full-featured e-commerce web application designed to sell and manage products with role-based access for users and admins. It supports secure checkout, wishlist, wallet, coupons, order tracking, and real-time sales reporting.

---

## 🚀 Features

### 👤 User Features
- Signup/Login with Session Authentication
- View and search products with category and variant filters
- Add to Cart, Wishlist, and manage addresses
- Secure Checkout using **PayPal**
- Apply Coupons and Offers
- View Order History and Order Tracking
- Wallet for refunds and cashbacks

### 🛠 Admin Features
- Admin dashboard with charts and analytics
- Product, Category, and Variant Management
- Offer & Coupon Management
- Image Upload with Cropping (no quality loss)
- Order Management and Status Update
- Sales Reporting and Export

---

## 🔧 Tech Stack

| Layer       | Technology                     |
|------------|---------------------------------|
| Backend     | Django, Django ORM              |
| Frontend    | HTML, CSS, JS (Jinja templates) |
| Database    | PostgreSQL                      |
| Auth        | Django Session Auth             |
| Payment     | PayPal                          |
| Media       | Cloudinary                      |
| Deployment  | AWS EC2 (Ubuntu), Nginx, Certbot|
| Others      | Chart.js (Admin dashboard)      |

---

## 📦 Installation

### Backend

```bash
git clone https://github.com/anzzxx/sonic-ecommerce.git
cd sonic-ecommerce
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
