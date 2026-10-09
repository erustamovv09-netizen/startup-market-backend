with open("core/settings.py", "r") as f:
    content = f.read()

context_patch = "EMAIL_SSL_CONTEXT = ssl._create_unverified_context()\n"
if "EMAIL_SSL_CONTEXT" not in content:
    content = content.replace("EMAIL_USE_TLS = True", "EMAIL_USE_TLS = True\n" + context_patch)

with open("core/settings.py", "w") as f:
    f.write(content)

