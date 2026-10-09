import re

with open('market/views.py', 'r') as f:
    content = f.read()

# I will replace everything starting from `@receiver(reset_password_token_created)` to the end.
# Then I'll properly format it.
import os

lines = content.split('\n')
clean_lines = []
skip = False
for line in lines:
    if "@receiver(reset_password_token_created)" in line:
        skip = True
    if "from django.dispatch import receiver" in line:
        skip = True
    if not skip:
        clean_lines.append(line)

clean_content = '\n'.join(clean_lines)

signal_code = """
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    reset_url = f"http://127.0.0.1:3000/reset-password?token={reset_password_token.key}"
    
    email_plaintext_message = f"Salom,\\n\\nParolingizni tiklash uchun quyidagi havolaga kiring:\\n{reset_url}"
    
    send_mail(
        "Parolni tiklash so'rovi",
        email_plaintext_message,
        "noreply@startupp.shop",
        [reset_password_token.user.email]
    )
"""

with open('market/views.py', 'w') as f:
    f.write(clean_content + signal_code)
