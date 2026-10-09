import re

with open("market/views.py", "r") as f:
    content = f.read()

# Replace noreply@startupp.shop with settings.EMAIL_HOST_USER
if '"noreply@startupp.shop"' in content:
    content = content.replace('"noreply@startupp.shop"', 'os.environ.get("EMAIL_HOST_USER", "noreply@startupp.shop")')
    if "import os" not in content:
        content = "import os\n" + content

with open("market/views.py", "w") as f:
    f.write(content)

