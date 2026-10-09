import re

with open("core/settings.py", "r") as f:
    content = f.read()

if "FRONTEND_URL =" not in content:
    content += "\nFRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://127.0.0.1:3000')\n"
    with open("core/settings.py", "w") as f:
        f.write(content)

with open("market/views.py", "r") as f:
    views_content = f.read()

if "http://127.0.0.1:3000/reset-password" in views_content:
    views_content = views_content.replace(
        'f"http://127.0.0.1:3000/reset-password?token={reset_password_token.key}"',
        'f"{settings.FRONTEND_URL}/reset-password?token={reset_password_token.key}"'
    )
    if "from django.conf import settings" not in views_content:
        views_content = "from django.conf import settings\n" + views_content
    with open("market/views.py", "w") as f:
        f.write(views_content)

