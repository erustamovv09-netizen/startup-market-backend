with open("core/settings.py", "r") as f:
    content = f.read()

certifi_patch = """
import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
"""
if "certifi.where()" not in content:
    content = certifi_patch + content

with open("core/settings.py", "w") as f:
    f.write(content)

