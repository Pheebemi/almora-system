# PythonAnywhere Deployment Guide

This guide will help you deploy your Almora Polytechnic Pantisawa Django application to PythonAnywhere.

## Prerequisites

1. A PythonAnywhere account (free tier available)
2. Your project code uploaded to a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Project

### 1.1 Create Environment Variables File

Create a `.env` file in your project root for production settings:

```bash
# Copy the sample environment file
cp env_sample.txt .env
```

Edit `.env` with your production values:

```env
DJANGO_SECRET_KEY=your-very-long-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=almorapoly.pythonanywhere.com
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
STATIC_URL=/static/
STATIC_ROOT=staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=media
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 1.2 Update Settings for Production

Your current `settings.py` is already configured for environment variables, which is perfect for PythonAnywhere.

### 1.3 Create Requirements File

Your `requirements.txt` should already be up to date. Make sure it includes all necessary packages.

## Step 2: Upload to PythonAnywhere

### 2.1 Create a New Web App

1. Log in to your PythonAnywhere account
2. Go to the **Web** tab
3. Click **Add a new web app**
4. Choose **Manual configuration**
5. Select **Python 3.10** (or the latest available version that matches your local setup)
6. Click **Next** until you reach the configuration page

### 2.2 Set Up Virtual Environment

1. In the **Web** tab, find your web app
2. Go to the **Virtualenv** section
3. Enter a path for your virtual environment: `/home/almora/.virtualenvs/almora_env`
4. Click **Create virtualenv**

### 2.3 Upload Your Code

#### Option A: Using Git (Recommended)

1. Go to the **Files** tab
2. Open a Bash console
3. Clone your repository:

```bash
git clone https://github.com/pheebemi/almora-system.git
cd almora-system
```

#### Option B: Manual Upload

1. In the **Files** tab, create a new directory for your project
2. Upload all your project files using the upload button
3. Extract if uploaded as a zip file

### 2.4 Install Dependencies

1. Open a Bash console in PythonAnywhere
2. Navigate to your project directory:

```bash
cd almora-system
```

3. Activate your virtual environment:

```bash
source /home/almora/.virtualenvs/almora_env/bin/activate
```

4. Install requirements:

```bash
pip install -r requirements.txt
```

## Step 3: Configure the Web App

### 3.1 Set Up WSGI File

1. In the **Web** tab, go to the **Code** section
2. Update the **Source code** path to point to your project directory
3. Update the **Working directory** to the same path

4. Create a WSGI configuration file. Go to the **WSGI configuration file** link and replace its contents with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/almora/almora-system'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'almora_project.settings'

# The virtual environment is already activated by PythonAnywhere
# No need to manually activate it here - just ensure the path is set correctly

# Import Django
import django
django.setup()

# Import the WSGI application
from almora_project.wsgi import application
```

**Important:** Replace `almora` and `almora-system` with your actual PythonAnywhere username and repository name.

### 3.2 Set Virtual Environment Path

In the **Web** tab, under **Virtualenv** section, make sure the path points to:
`/home/almora/.virtualenvs/almora_env`

### 3.3 Configure Static Files

1. In the **Web** tab, go to the **Static files** section
2. Add a new static files entry:
   - URL: `/static/`
   - Directory: `/home/almora/almora-system/staticfiles`

3. Add media files entry:
   - URL: `/media/`
   - Directory: `/home/almora/almora-system/media`

## Step 4: Database Setup

### 4.1 Run Migrations

1. Open a Bash console
2. Navigate to your project and activate virtualenv:

```bash
cd almora-system
source /home/almora/.virtualenvs/almora_env/bin/activate
```

3. Run Django migrations:

```bash
python manage.py migrate
```

### 4.2 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## Step 5: Environment Variables

### 5.1 Create .env file on PythonAnywhere

1. In the **Files** tab, create a `.env` file in your project root
2. Add your production environment variables (see Step 1.1)

### 5.2 Alternative: Set Environment Variables in WSGI

You can also set environment variables directly in your WSGI file:

```python
import os
import sys

# Set environment variables
os.environ['DJANGO_SECRET_KEY'] = 'your-secret-key'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'almorapoly.pythonanywhere.com'
# Add other required environment variables...

# Rest of the WSGI configuration...
```

## Step 6: Reload and Test

1. In the **Web** tab, click the **Reload** button for your web app
2. Visit your site at `https://almorapoly.pythonanywhere.com`
3. Check the server logs if you encounter any errors

## Troubleshooting

### Common Issues:

1. **Import Error**: Make sure your WSGI file paths are correct
2. **Static Files Not Loading**: Check static files configuration and run `collectstatic`
3. **Database Error**: Ensure your database file has correct permissions
4. **Environment Variables**: Verify all required environment variables are set

### Checking Logs:

- Go to the **Web** tab
- Click on the **Log files** section
- Check error.log and access.log for issues

### File Permissions:

SQLite database files need proper permissions:

```bash
chmod 664 db.sqlite3
```

## Additional Configuration

### Custom Domain (Optional)

If you want to use a custom domain:

1. Go to the **Web** tab
2. In the **Domains** section, add your custom domain
3. Configure DNS settings as instructed
4. Update `ALLOWED_HOSTS` in your settings

### SSL Certificate (Optional)

PythonAnywhere provides free SSL certificates:

1. In the **Web** tab, go to **SSL**
2. Click **Get it for free with Let's Encrypt**
3. Follow the instructions

## Maintenance

### Updating Your App:

1. Make changes to your code locally
2. Push to your Git repository
3. On PythonAnywhere, pull the changes:

```bash
cd almora-system
git pull origin main
```

4. Install any new requirements:

```bash
source /home/almora/.virtualenvs/almora_env/bin/activate
pip install -r requirements.txt
```

5. Run migrations if needed:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

6. Reload your web app

## Security Considerations

1. **Secret Key**: Use a long, random secret key in production
2. **Debug Mode**: Always set `DEBUG = False` in production
3. **Allowed Hosts**: Only allow your domain in `ALLOWED_HOSTS`
4. **Database**: Don't commit database files to version control
5. **Environment Variables**: Keep sensitive data in environment variables

## Support

If you encounter issues:

1. Check PythonAnywhere's documentation: https://help.pythonanywhere.com/
2. Check Django deployment documentation: https://docs.djangoproject.com/en/5.1/howto/deployment/
3. Review server logs for error messages

## Quick Reference Commands

```bash
# Activate virtual environment
source /home/almora/.virtualenvs/almora_env/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Check for issues
python manage.py check --deploy
```