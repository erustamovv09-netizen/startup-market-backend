with open("core/settings.py", "r") as f:
    content = f.read()

ssl_patch = "import ssl\nssl._create_default_https_context = ssl._create_unverified_context\n"
if "ssl._create_unverified_context" not in content:
    content = ssl_patch + content

with open("core/settings.py", "w") as f:
    f.write(content)

