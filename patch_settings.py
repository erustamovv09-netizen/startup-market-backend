import os

with open("core/settings.py", "r") as f:
    content = f.read()

# Add WhiteNoiseMiddleware
if "WhiteNoiseMiddleware" not in content:
    content = content.replace(
        "'django.middleware.security.SecurityMiddleware',",
        "'django.middleware.security.SecurityMiddleware',\n    'whitenoise.middleware.WhiteNoiseMiddleware',"
    )

# Add STATIC_ROOT
if "STATIC_ROOT" not in content:
    if "STATIC_URL = 'static/'" in content:
        content = content.replace(
            "STATIC_URL = 'static/'",
            "STATIC_URL = 'static/'\nSTATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')\n"
        )

with open("core/settings.py", "w") as f:
    f.write(content)

