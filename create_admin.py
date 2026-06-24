import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Set your desired credentials here
username = "admin"
email = "code247.me@gmail.com"
password = "admin123"  

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser: {username}...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created successfully!")
else:
    print(f"Superuser '{username}' already exists.")
