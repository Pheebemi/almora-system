import sys
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(APP_DIR, '.env'))
except Exception:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakeView_project.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
