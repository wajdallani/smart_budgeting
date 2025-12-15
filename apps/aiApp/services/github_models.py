from django.conf import settings
import requests

def github_chat(messages, temperature=0.4):
    url = f"{settings.GITHUB_MODELS_ENDPOINT}/chat/completions"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.GITHUB_MODEL,
        "messages": messages,
        "temperature": temperature,
    }

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    # r.raise_for_status()
    
    if r.status_code >= 400:
        raise RuntimeError(
            f"GitHub Models error {r.status_code}: {r.text}"
        )

    return r.json()["choices"][0]["message"]["content"]