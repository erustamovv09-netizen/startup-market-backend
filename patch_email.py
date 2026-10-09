import os

with open("core/settings.py", "r") as f:
    content = f.read()

old_backend = "EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'"

new_email_config = """
# E-mail settings (Real SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')  # pochtangiz
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')  # app password
"""

if old_backend in content:
    content = content.replace(
        "# E-mail settings\n" + old_backend,
        new_email_config
    )
elif "EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'" not in content:
    content += new_email_config

with open("core/settings.py", "w") as f:
    f.write(content)

