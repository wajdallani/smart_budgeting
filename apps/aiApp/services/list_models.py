import requests
from django.conf import settings

token = settings.GITHUB_TOKEN  # ✅ read from settings.py

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {token}",
    "X-GitHub-Api-Version": "2022-11-28",
}

r = requests.get(
    "https://models.github.ai/catalog/models",
    headers=headers,
    timeout=30
)

print("Status:", r.status_code)
print(r.text[:2000])  # first part is enough
