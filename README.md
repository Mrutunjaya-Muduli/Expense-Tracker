# Smart Expense Tracker

A modern Django-based Expense Tracker application featuring budget planning, income/expense tracking, group sharing, reports, and visual dashboards.

## Features
- **Dashboard**: Track overall income, expenses, and budget balances with dynamic visual charts.
- **Budgeting**: Define monthly or category-wise budgets and get warnings when exceeding them.
- **Expenses/Income**: Track financial transactions categorized by custom types.
- **Groups**: Share expenses and split bills with friends or family.
- **Reports**: Generate PDF reports and filter transactions by date, categories, or groups.

---

## Local Setup & Development

### 1. Clone the Repository
```bash
git clone <repository-url>
cd EXPENCE-TRACKER
```

### 2. Create and Activate Virtual Environment
On Windows:
```powershell
python -m venv venv
venv\Scripts\activate
```
On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup (Default: SQLite)
Run migrations to set up the SQLite database:
```bash
python manage.py migrate
```

### 5. Seed Initial Data
To load pre-defined categories and initial data setups:
```bash
python manage.py seed_data
```

### 6. Create Superuser (Optional)
Create an admin account to manage records via Django Admin:
```bash
python manage.py createsuperuser
```

### 7. Run the Application
Start the development server:
```bash
python manage.py runserver
```
Visit the app in your browser at `http://127.0.0.1:8000/`.

---

## Hosting on Vercel with PostgreSQL

This project is prepared to deploy to Vercel and dynamically switch from a local SQLite database to PostgreSQL when a database environment variable is provided.

### 1. Push to GitHub
Commit all your local changes and push the repository to GitHub.

### 2. Connect Project to Vercel
1. Go to the [Vercel Dashboard](https://vercel.com).
2. Click **Add New** -> **Project**.
3. Select and import your GitHub repository.

### 3. Setup a PostgreSQL Database

#### Option A: Vercel Postgres (Recommended)
1. On your Vercel project page, navigate to the **Storage** tab.
2. Select **Postgres** and click **Connect/Create**.
3. Choose a region and finish the setup. Vercel will automatically inject variables like `POSTGRES_URL` to connect to your database.

#### Option B: External PostgreSQL (Neon.tech, Supabase, etc.)
1. Create a PostgreSQL instance on [Neon](https://neon.tech) or [Supabase](https://supabase.com).
2. Copy the connection string.
3. Go to Vercel **Project Settings** -> **Environment Variables** and add:
   - Key: `DATABASE_URL`
   - Value: `<your_database_connection_url>`

### 4. Configure Django Settings on Vercel
In Vercel **Environment Variables**, add:
- `DEBUG`: `False`
- `DJANGO_SECRET_KEY`: `<a_long_random_secret_string>`
- `ALLOWED_HOSTS`: `<your_vercel_subdomain>.vercel.app`

### 5. Run Database Migrations on Production
Because Vercel serverless builds run in an isolated environment, migrations should be triggered from your local workspace targeting the remote database:

Run the following in your terminal (replacing the placeholder URL with your remote database URL):

**On Windows (PowerShell):**
```powershell
$env:DATABASE_URL="your_production_postgres_url_here"
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py seed_data
```

**On macOS/Linux (Bash):**
```bash
DATABASE_URL="your_production_postgres_url_here" python manage.py migrate
DATABASE_URL="your_production_postgres_url_here" python manage.py seed_data
```
