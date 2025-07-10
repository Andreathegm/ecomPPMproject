# 🛒 ShopFrontier - E-Commerce Platform

[![Python](https://img.shields.io/badge/python-3.12.11-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2.3-green)](https://www.djangoproject.com/)

A modular, production-ready e‑commerce web application built with Django and Bootstrap for university coursework. Features include product management, shopping cart, user authentication, order processing, reviews, and administrative tools.

**🌐 Live Demo:** [ShopFrontier Platform](DEPLOYMENT_LINK_HERE)

---

## 📋 Table of Contents

1. [Features](#-features)
2. [Tech Stack](#-tech-stack)
3. [Getting Started](#-getting-started)
4. [Local Navigation Guide](#-local-navigation-guide)
5. [Project Structure](#-project-structure)
6. [Admin Panel](#-admin-panel)
7. [Deployment](#-deployment)
8. [Future Enhancements](#-future-enhancements)
9. [License](#-license)

---

## 🔥 Features

### 👥 **User Features**
* **Landing Page:** Top picks and top commented products showcase
* **Product Browsing:** Browse by categories with advanced filtering and search
* **Product Details:** Comprehensive product information and image gallery
* **Shopping Cart:** Full cart management (add/remove items, quantity updates)
* **Order Processing:** Complete checkout flow with order confirmation
* **Order History:** View past orders with detailed item breakdown
* **Reviews & Ratings:** Leave and modify reviews after purchase completion
* **Discount System:** Apply discounts during checkout

### 🛠️ **Manager Features**
* **Product Management:** Add, delete, and modify products
* **Category Management:** Full CRUD operations for product categories
* **Order Management:** Change order status and track fulfillment
* **Enhanced Admin Panel:** Customized Django admin interface with inline editing

---

## 🛠️ Tech Stack

| Layer         | Technologies                                                                                   |
| ------------- | ---------------------------------------------------------------------------------------------- |
| **Backend**   | Python 3.12.11, Django 5.2.3, Supabase (PostgreSQL), dj-database-url, python-decouple |
| **Storage**   | Cloudinary (media files), WhiteNoise (static files)                                           |
| **Frontend**  | Django Templates, Bootstrap 5, Vanilla JS, Django Crispy Forms                                 |
| **Database**  | Supabase (production), SQLite3 (local development)                                            |
| **Server**    | Gunicorn, Render.com                                                                           |
| **Dev Tools** | Git, GitHub, build.sh                                                                          |

---

## 🏁 Getting Started

### ✅ Prerequisites

* Git
* Virtual environment manager (venv, conda, etc.)

### 📥 Quick Installation (3 Steps!)

```bash
# 1. Clone repository
git clone https://github.com/your-username/shopfrontier.git
cd shopfrontier

# 2. Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### ⚙️ Environment Variables (Development)

**For local development, simply configure these 4 variables:**

Rename `example.env` to `.env` and set:

```env
ENV=development
DJANGO_SECRET_KEY='your-secret-key-here'
DEBUG=False
USE_CLOUDINARY=False
PYTHON_VERSION=3.12.11
```

> **💡 Secret Key:** You can generate one at [Django Secret Key Generator](https://djecrety.ir/) or use: `django-insecure-local-development-key-123456789`

### 🗄️ Database Setup

**No database setup required!** The repository includes:
- ✅ Pre-populated SQLite3 database with sample data
- ✅ Ready-to-use product catalog
- ✅ Sample user accounts (see below)

### 🚀 Running Locally

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

### 👥 Pre-loaded User Accounts

| Role           | Username        | Password      | Access Level            |
|----------------|-----------------|---------------|------------------------|
| **Store Manager** | `manager`       | `test123`     | Product & Order Management |
| **Customer**      | `customer`      | `test123`     | Shopping & Reviews      |
| **Admin**         | `admin`         | `admin123`    | Full Admin Panel        |

---

## 🌐 Production Configuration

**For production deployment, additional variables are required:**

| Variable                | Description                          | Example                                                                                                                        |
|-------------------------| ------------------------------------ |--------------------------------------------------------------------------------------------------------------------------------|
| `ENV`                   | Environment setting                  | `production`                                                                                                                   |
| `DJANGO_SECRET_KEY`     | Django secret key                    | `your-django-secret-key`                                                                                                      |
| `DEBUG`                 | Enable debug mode (`True`/`False`)   | `False`                                                                                                                        |
| `USE_CLOUDINARY`        | Enable Cloudinary storage            | `True`                                                                                                                         |
| `DATABASE_URL`          | DB connection (Supabase)             | `postgresql://postgres.name_account:db-password@aws-0-eu-central-2.pooler.supabase.com:port/postgres`                       |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name                | `your-cloudinary-name`                                                                                                         |
| `CLOUDINARY_API_KEY`    | Cloudinary API key                   | `your-cloudinary-api-key`                                                                                                      |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret                | `your-cloudinary-api-secret`                                                                                                   |

---

## 🧭 Local Navigation Guide

### 🏠 **Getting Started with Local Development**

1. **Setup:** Follow the installation steps above, ensuring you rename `example.env` to `.env`
2. **Database:** The project includes a pre-configured SQLite3 database with sample data
3. **Media Files:** Local media folder is included for development purposes

### 🎯 **Site Navigation**

#### **Customer Journey:**
1. **Homepage (`/`)** - Browse top picks and most commented products
2. **Products (`/products/`)** - Use filters and search to find items
3. **Product Detail** - Click any product to view details and add to cart
4. **Shopping Cart (`/cart/`)** - Manage items and proceed to checkout
5. **Checkout** - Complete order with shipping details
6. **Order History (`/orders/`)** - View past orders and manage reviews

#### **Manager Access:**
1. **Admin Panel (`/admin/`)** - Login with superuser credentials
2. **Product Management** - Add, edit, or delete products and categories
3. **Order Management** - Update order statuses and track fulfillment

### 🔑 **Default Credentials**
- **Admin User:** Create during `createsuperuser` step
- **Sample Users:** Available in the included database

---

## 📂 Project Structure

```
shopfrontier/
├── build.sh            # Deployment script
├── ecommerce_core/     # Django project settings & URLs
├── mainapp/            # Homepage, landing page, static pages
├── products/           # Product models, views, templates
├── cart/               # Cart logic & session management
├── orders/             # Order processing & history
├── users/              # Custom user model & authentication
├── media/              # Local media files (development)
├── db.sqlite3          # Local development database
├── requirements.txt    # Python dependencies
├── example.env         # Environment variables template
└── .env               # Your configuration (rename from example.env)
```

---

## 🔐 Admin Panel

Access at `/admin/` with your superuser credentials. The admin interface has been customized with:

* **Enhanced Product Management:** Inline editing for product variants and images
* **Category Organization:** Hierarchical category management
* **Order Tracking:** Streamlined order status updates
* **User Management:** Customer account oversight
* **Review Moderation:** Manage customer reviews and ratings

### 🛠️ **Manager Capabilities:**
- Add new products with multiple images
- Organize products into categories
- Update order statuses (Pending → Processing → Shipped → Delivered)
- Monitor customer reviews and ratings
- Generate basic reports on sales and inventory

---

## ☁️ Deployment

**Live Application:** [ShopFrontier Platform](DEPLOYMENT_LINK_HERE)

### Production Setup:
- **Hosting:** Render.com
- **Database:** Supabase (PostgreSQL)
- **Media Storage:** Cloudinary
- **Static Files:** WhiteNoise

### Build Process:
```bash
chmod a+x build.sh && ./build.sh
```

### Environment:
Production environment variables are configured in Render dashboard with Supabase and Cloudinary credentials.


## 🎓 Academic Context

This project was developed as part of a university examination, demonstrating:
- **Full-stack web development** with Django
- **User authentication** and authorization
- **File upload** and media management
- **E-commerce** business logic implementation

---

## 🛠️ Common Django Commands

```bash
# Make migrations for model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files (production)
python manage.py collectstatic

# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser
```

---
