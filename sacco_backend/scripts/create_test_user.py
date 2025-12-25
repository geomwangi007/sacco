
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
django.setup()

User = get_user_model()

if not User.objects.filter(email="admin@sacco.com").exists():
    User.objects.create_superuser(
        email="admin@sacco.com",
        password="password123",
        first_name="Admin",
        last_name="User",
        phone_number="+256700000000",
        national_id="CM00000000A"
    )
    print("Superuser created.")
else:
    print("Superuser already exists.")
