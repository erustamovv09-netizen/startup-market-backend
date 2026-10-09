import os

with open("core/settings.py", "r") as f:
    content = f.read()

# Add to INSTALLED_APPS
if "django_rest_passwordreset" not in content:
    content = content.replace(
        "'rest_framework_simplejwt',",
        "'rest_framework_simplejwt',\n    'django_rest_passwordreset',"
    )

# Add Email Backend config
if "EMAIL_BACKEND" not in content:
    content += "\n\n# E-mail settings\nEMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'\n"

with open("core/settings.py", "w") as f:
    f.write(content)

