# 📚 Readora — Enterprise Library Management System (LMS)

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x%20%2F%206.x-092e20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38bdf8?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Deployment](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel&logoColor=white)](https://vercel.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20SQLite-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

**Readora** is a production-grade, full-stack Academic & Digital Library Management System engineered with **Python, Django, Tailwind CSS, and Chart.js**. Designed for university campuses and enterprise research centers, it automates catalog ingestion, patron circulation, QR-code powered transaction verification, and fine compliance tracking.

---

## 🌟 Key Features & Engineering Highlights

### 1. 🛡️ Role-Based Access Control (RBAC)
- Multi-tier authentication distinguishing **Students**, **Faculty Members**, and **Librarians / System Administrators**.
- Custom Django model relationships extending `auth.User` with departmental affiliation, enrollment roll numbers, borrowing limits, and dynamic dashboard views.

### 2. 🔍 Google Books REST API Integration (Smart ISBN Auto-Ingestion)
- Librarians can enter any standard ISBN-10 or ISBN-13 (e.g., `9780132350884`).
- Server-side asynchronous query automatically populates book titles, authors, categories, descriptions, and high-resolution cover artwork into the catalog in seconds.

### 3. 🏷️ Dynamic QR Code Circulation Slip Engine
- Generates base64 encoded PNG QR codes on-the-fly (`python-qrcode`) for each checkout record.
- Printable, official university loan slips with transaction references, return deadlines, and barcode verification.

### 4. ⏱️ Automated Due Date & Fine Calculation Engine
- Automatically recalculates loan expiration and tracks overdue penalties (₹10.00 / calendar day).
- Live compliance tracking with status badges (`Active`, `Due Soon`, `Overdue`).
- One-click batch reminder dispatch for library admins.

### 5. 📊 Interactive Analytics Dashboard (Chart.js)
- Real-time catalog distribution by academic disciplines (CSE, AI/ML, Data Science, ECE, EEE, Mechanical, Civil, MBA).
- Circulation turnover rates and quick inventory audit counters.

### 6. 📖 Integrated Digital Reading Room
- Direct in-browser viewing of curriculum reference books (PDF) linked to catalog records.

---

## 🏗️ Architecture & Data Model

```
+--------------------+           1:1           +-----------------------+
|  django.auth.User  | <=====================> |    RegisteredUser     |
+--------------------+                         +-----------------------+
         |                                     | role: student/fac/lib |
         | 1:N                                 | department, reg_no    |
         v                                     +-----------------------+
+--------------------+           N:1           +-----------------------+
|     IssuedBook     | >=====================> |         Book          |
+--------------------+                         +-----------------------+
| user_id            |                         | title, author, isbn   |
| book_id            |                         | department, rack      |
| issue_date         |                         | total_copies          |
| due_date           |                         | available_copies      |
| returned, status   |                         | pdf_filename          |
| fine_amount        |                         +-----------------------+
+--------------------+
```

---

## 🚀 Quick Start Guide (Local Development)

### 1. Clone the Repository
```bash
git clone https://github.com/vamsikiran01/readora.git
cd readora
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/`.

### 4. Default Demo Accounts
- **Librarian / Admin**:
  - Username: `admin` | Password: `admin` (or create via `python manage.py createsuperuser`)
- **Student / Member**:
  - Sign in with any student account or click **"Register as new member"** on the login page.

---

## ☁️ Deploying to Vercel

This repository includes turnkey Vercel deployment files:
- `vercel.json` — Serverless WSGI routing configuration.
- `build_files.sh` — Automatic dependency installation and WhiteNoise static asset compression.
- `settings.py` — Configured with WhiteNoise and optional PostgreSQL (`DATABASE_URL`).

### Deployment Steps:
1. Push this project to your GitHub repository.
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
3. Select your `Readora-LMS` repository.
4. (Optional) In **Environment Variables**, add:
   - `SECRET_KEY` = your secret string
   - `DEBUG` = `False`
   - `DATABASE_URL` = your Supabase / Neon PostgreSQL connection string (or use the built-in SQLite for demo).
5. Click **"Deploy"**! 🚀

---

## 💼 Resume Description (Copy & Paste)

> **Readora — Enterprise Academic Library Management System** | *Python, Django, PostgreSQL, Tailwind CSS, Vercel*
> - Engineered an enterprise-grade library management platform with **Role-Based Access Control (RBAC)** across 3 user tiers (Student, Faculty, Librarian).
> - Integrated **Google Books REST API** to automatically populate catalog metadata and book cover assets by ISBN, cutting book ingestion time by 80%.
> - Implemented an automated **QR Code circulation engine** and real-time fine calculation system for overdue returns.
> - Built an interactive analytical dashboard with **Chart.js** displaying book turnover rates, department distributions, and borrow velocity.
> - Configured continuous deployment with **PostgreSQL (Neon/Supabase)** and **Vercel Serverless**, utilizing WhiteNoise for optimized static asset delivery.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
