# ShopFrontier - E-Commerce Platform

[![Python](https://img.shields.io/badge/python-3.12.11-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2.3-green)](https://www.djangoproject.com/)

A modular, production-ready e‑commerce web application built with Django and Bootstrap for university coursework. Features include product management, shopping cart, user authentication, order processing, reviews, and administrative tools.

**🌐 Live Demo:** [ShopFrontier](https://ecomppmproject.onrender.com)


---

## 📋 Table of Contents

1. [Features](#-features)
2. [Tech Stack](#-tech-stack)
3. [Project - setup (locally)](#project---setup-locally)
4. [Local Navigation Guide](#-local-navigation-guide)
5. [Project Structure](#-project-structure)
7. [Deployment](#-deployment)

---

##  Features

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

| Layer         | Technologies                                                                          |
| ------------- |---------------------------------------------------------------------------------------|
| **Backend**   | Python 3.12.11, Django 5.2.3, Supabase (PostgreSQL), dj-database-url, python-decouple |
| **Storage**   | Cloudinary (media files), WhiteNoise (static files)                                   |
| **Frontend**  | Django Templates, Bootstrap 5, Javascript, Django Crispy Forms                        |
| **Database**  | Supabase (production), SQLite3 (local development)                                    |
| **Server**    | Gunicorn, Render.com                                                                  |
| **Dev Tools** | Git, GitHub, build.sh                                                                 |

---

## Project - setup (locally)

### ✅ Prerequisites
* Python
* Git
* Virtual environment manager (venv, conda, etc.)

### Installation

```bash
#1. Create a working directory
mkdir myshop-env
cd myshop-env

# 2. Clone repository
git clone https://github.com/Andreathegm/ecomPPMproject.git
cd ecommerce_core
# now you are in /myshop-env/ecommerce_core

# 3. Create & activate virtual environment
conda create --name shop-env python=3.11
conda activate shop-env
#you should se something like (shop-env)../myshope-env/ecommerce_core in your terminal prompt

# 4. Install dependencies
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

> **💡 Secret Key:** You can generate one at [Django Secret Key Generator](https://djecrety.ir/) or use the original to maintain access to simulated user accounts.
> `DJANGO_SECRET_KEY= @)cb8+*#rb^bgas=uxor*42^h6cj(6-*b&sjyr*@v&%xsfov5k`
> I shouldn't leak the secret key, but this is just for educational purposes.

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

| Role           | Username       | Password    | Access Level                         |
|----------------|----------------|-------------|--------------------------------------|
| **Store Manager** | `managertest`  | `manag3r1_` | Product, Category & Order Management |
| **Customer**      | `customertest` | `custum3r1_` | Shopping & Reviews                   |
| **Admin**         | `admin`        | `admin`     | Full Admin Panel                     |

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
4. **Shopping Cart (`/cart/`)** - Manage items and proceed to checkout (adding to cart is also permitted to anonymous users through session_key)
5. **Checkout** - Complete order with shipping details
6. **Order History (`/orders/history`)** - View past orders and manage reviews on purchased products

#### **Manager Access:**
1. **Manger Panel/Catalog (`/manage_catalog/`)** - Login with superuser credentials
2. **Product Management** - Add, edit, or delete products and categories
3. **Order Management** - Update order statuses and track fulfillment
### 🛠️ **Manager Capabilities:**
- Add new products with multiple images as well as categories
- Organize products into categories
- Update order statuses (Pending → Processing → Shipped → Delivered or even Cancelled)


#### **Admin Access:**
1. **Admin Panel (`/admin/`)** - Login with admin credentials
2. Can manage **all aspects** of the site

---

## 📂 Project Structure

```
ecommerce_core/
├── build.sh            # Deployment script
├── ecommerce_core/     # Django project settings & URLs
├── mainapp/            # Landing page
├── products/           # Product models, views, templates
├── cart/               # Cart logic & session management
├── orders/             # Order processing & history
├── users/              # Custom user model & authentication
├── media/ 
├──static/
|     ├──css # Local media files (development)
|     ├──js  # Local static files (development)
|     └──images # Local images (development)
├── templates/          # HTML templates for all apps
├── db.sqlite3          # Local development database
├── requirements.txt    # Python dependencies
├── example.env         # Environment variables template(rename to .env and follow the above instruction)
└── .env               # Your deploy environment variables (not included in repo)
```
---


## ☁️ Deployment

**Live Application:** [ShopFrontier](https://ecomppmproject.onrender.com)

### Production Setup:
- **Hosting:** Render.com
- **Database:** Supabase (PostgreSQL)
- **Media Storage:** Cloudinary
- **Static Files:** WhiteNoise

### Build Process Guide

To run the `build.sh` script correctly across all platforms, follow the steps below.

---

#### 1. Ensure Correct Line Endings (LF Only)

If you're on **Windows**, your `build.sh` file might have `CRLF` line endings, which can cause issues when running the script on Unix-based systems like Linux or macOS.

**How to convert to Unix-style LF endings:**

* **In VS Code or on your code editor**:

    * Click on `CRLF` in the bottom-right corner.
    * Select `LF` from the list.
    * Save the file.

* **Using the Terminal**:

  ```bash
  sed -i 's/\r$//' build.sh       # On Linux/macOS
  # OR (if available)
  dos2unix build.sh
  ```

---

#### 2. Make the Script Executable and Run It

Use the following command to make `build.sh` executable and run it in a single step:

```bash
chmod a+x build.sh && ./build.sh
```

This command does two things:

* `chmod a+x build.sh`: Grants execution permission to all users.
* `./build.sh`: Executes the script.

---

### ✅ Notes

* This guide ensures compatibility when switching between Windows and Unix environments.
* If you're not on Windows, you can skip step 1.
* You can re-run the `chmod` step anytime without harm.

---

By following this process, you avoid common script execution issues caused by incorrect line endings or missing permissions.


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
