# Deploy Almora Polytechnic Pantisawa to cPanel (Step-by-Step)

You have pushed the project to GitHub. Follow these steps to deploy on cPanel.

---

## Before you start

- cPanel hosting with **Python 3.8+** and **Setup Python App** (or **Application Manager** / Passenger).
- Your **domain** or **subdomain** pointed to this hosting.
- **Git** available in cPanel (Terminal or Git Version Control), or use File Manager + upload.

---

## Step 1: Open cPanel and choose where the app will live

1. Log in to **cPanel**.
2. Decide the app directory. Examples:
   - `~/almora` (inside your home directory, not in `public_html`), or
   - `~/public_html/almora` (if you want the site at `yourdomain.com/almora`).
3. Create the folder if it doesn’t exist (e.g. **File Manager** → create `almora`).

---

## Step 2: Get the code from GitHub

**Option A – Using Terminal (if available)**

1. Go to **cPanel → Terminal** (or **Advanced → Terminal**).
2. Go to your home directory and clone the repo:

   ```bash
   cd ~
   git clone https://github.com/pheebemi/almora-system.git almora
   cd almora
   ```

   Replace `YOUR_USERNAME` and the repo name with your actual GitHub URL.

**Option B – Using File Manager**

1. On your computer, download the repo as ZIP from GitHub (Code → Download ZIP).
2. In cPanel **File Manager**, go to the folder you chose (e.g. `almora`).
3. Upload the ZIP and **Extract**.
4. If the ZIP created a subfolder (e.g. `almora-system-main`), move all its contents into `almora` so that `manage.py` is inside `almora/`.

---

## Step 3: Create the Python application in cPanel

1. In cPanel, open **Setup Python App** (or **Application Manager** / **Passenger**).
2. Click **Create Application**.
3. Set:
   - **Python version**: 3.8, 3.10, or 3.11 (whatever is available).
   - **Application root**: path to the folder that contains `manage.py`, e.g. `almora` or `public_html/almora`.
   - **Application URL**: your domain or subdomain (e.g. `yourdomain.com` or `app.yourdomain.com`).
   - **Application startup file**: `passenger_wsgi.py` (we’ll add this file in the next step).
4. Save/Create. cPanel will create a **virtual environment** (e.g. `~/almora/virtualenv`).

---

## Step 4: Add `passenger_wsgi.py` (if not already in the repo)

In the **same directory as `manage.py`** (your application root), create or edit `passenger_wsgi.py`:

```python
import sys
import os

# Use the virtualenv created by cPanel (adjust if your venv path is different)
INTERP = os.path.join(os.environ['HOME'], 'almora', 'virtualenv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almora_project.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

- If your app root is different (e.g. `public_html/almora`), change the path in `INTERP` to match, e.g. `os.path.join(os.environ['HOME'], 'public_html', 'almora', 'virtualenv', 'bin', 'python3')`.
- Some hosts set `VIRTUAL_ENV`; you can use that instead:  
  `INTERP = os.path.join(os.environ.get('VIRTUAL_ENV', os.environ['HOME'] + '/almora/virtualenv'), 'bin', 'python3')`.

---

## Step 5: Install dependencies

1. In **Setup Python App**, find your app and click **Open** (or use Terminal).
2. **Run pip install** (or in Terminal):

   ```bash
   cd ~/almora   # or your app path
   source virtualenv/bin/activate
   pip install -r requirements.txt
   ```

   If `requirements.txt` is missing or has encoding issues, install at least:

   ```bash
   pip install Django gunicorn python-dotenv Pillow requests
   ```

3. Install **Passenger/WSGI** dependency if the host requires it:

   ```bash
   pip install passenger
   ```

   (Only if your host’s docs say so.)

---

## Step 6: Environment variables and production settings

1. In the app root (same folder as `manage.py`), create a `.env` file (e.g. via File Manager or Terminal: `nano .env`).
2. Add at least:

   ```env
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=your-long-random-secret-key-here
   DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

   Generate a secret key (e.g. `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`).

3. For Paystack (payments), add:

   ```env
   PAYSTACK_SECRET_KEY=sk_live_xxxx
   PAYSTACK_PUBLIC_KEY=pk_live_xxxx
   ```

4. For production, use **MySQL** or **PostgreSQL** if your host provides it. Example for MySQL:

   - Create a MySQL database and user in cPanel.
   - In `.env`:

   ```env
   DATABASE_ENGINE=django.db.backends.mysql
   DATABASE_NAME=your_db_name
   DATABASE_USER=your_db_user
   DATABASE_PASSWORD=your_db_password
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   ```

   Then in `almora_project/settings.py`, ensure the `DATABASES` config reads these env vars (you may need to add `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT` if not already there).

5. Optional for HTTPS:

   ```env
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

---

## Step 7: Run migrations and create superuser

In Terminal (with virtualenv activated):

```bash
cd ~/almora
source virtualenv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

- If you use MySQL, install the driver first: `pip install mysqlclient`.
- If you use **PostgreSQL**, see the section below.

---

## Using PostgreSQL on cPanel

Do this **after** `pip install -r requirements.txt` and **before** `python manage.py migrate`.

### 1. Create the database in cPanel

1. In cPanel go to **PostgreSQL® Databases** (or **Databases** → PostgreSQL).
2. **Create a database** (e.g. `cpaneluser_almorapoly`). Note the full name (often `cpaneluser_dbname`).
3. **Create a user** and set a strong password. Note the username (often `cpaneluser_dbuser`).
4. **Add the user to the database** and grant **ALL PRIVILEGES**.
5. Note: **Host** is usually `localhost`; **Port** is usually `5432`.

### 2. Install the PostgreSQL adapter

With your virtualenv activated:

```bash
pip install psycopg2-binary
```

Or from the repo file:

```bash
pip install -r requirements-postgres.txt
```

### 3. Set `.env` for PostgreSQL

Edit the `.env` file in your app root (e.g. `/home/cpaneluser/almora/.env`) and set:

```env
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=cpaneluser_almorapoly
DATABASE_USER=cpaneluser_dbuser
DATABASE_PASSWORD=your_db_password_here
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

Use the **exact** database name and user from cPanel (including the prefix like `cpaneluser_`).

### 4. Run migrations

```bash
cd /home/cpaneluser/almora
source /home/cpaneluser/virtualenv/almora/3.11/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

Then restart the app in **Setup Python App**. Your site will now use PostgreSQL.

---

## Step 8: Static and media files

1. **collectstatic** (Step 7) puts static files in `STATIC_ROOT` (e.g. `staticfiles/`).
2. In cPanel **Setup Python App**, there is often an option to set **Static file URL** and **Static file path** (e.g. `/static` → `staticfiles`). If available, set:
   - URL: `/static`
   - Path: `staticfiles` (relative to app root) or full path to `staticfiles`.
3. For **media** uploads (e.g. profile pics), ensure `MEDIA_ROOT` and `MEDIA_URL` are set in settings (you already have them). You may need to add a rewrite rule or Alias in `.htaccess` so `/media/` is served from the `media` folder; many hosts document this for Django.

---

## Step 9: Restart the app and test

1. In **Setup Python App**, click **Restart** for your application.
2. Visit your domain. You should see the site.
3. Test:
   - `/admin/` (log in with the superuser you created).
   - Student login, staff login, and one payment flow if possible.

---

## Step 10: Updating the app after more pushes to GitHub

1. Pull the latest code:

   ```bash
   cd ~/almora
   git pull origin main
   ```

   (Use your default branch name if different.)

2. Activate venv, update deps, migrate, collectstatic, restart:

   ```bash
   source virtualenv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

3. Restart the app in **Setup Python App**.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| 500 error | Check **Error Log** in cPanel and the log path you set for the Python app. Fix `passenger_wsgi.py` path and `DJANGO_SETTINGS_MODULE`. |
| Static files 404 | Configure Static URL/path in Setup Python App, or add Alias for `/static` to `staticfiles` in `.htaccess`. |
| “DisallowedHost” | Add your domain to `DJANGO_ALLOWED_HOSTS` in `.env`. |
| Database error | Confirm `.env` DB vars and that the database and user exist in cPanel. Run `migrate` again. |
| Module not found | Activate the same virtualenv cPanel uses and run `pip install -r requirements.txt` in the app root. |

---

## Quick checklist

- [ ] Code in app root (e.g. `~/almora`) with `manage.py` and `passenger_wsgi.py`
- [ ] Python app created in cPanel with correct app root and startup file `passenger_wsgi.py`
- [ ] Virtualenv activated; `pip install -r requirements.txt` run
- [ ] `.env` with `DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS`, Paystack, and DB vars if needed
- [ ] `migrate` and `createsuperuser` run
- [ ] `collectstatic` run; static/media configured if required
- [ ] Application restarted and site tested

Once this is done, your Almora Polytechnic Pantisawa app is deployed on cPanel. For future updates, use Step 10.
