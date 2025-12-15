import json
from .github_models import github_chat

def generate_recommendations(summary: dict) -> list[dict]:
    system = (
        "You are a budgeting assistant. "
        "Give short, actionable, neutral recommendations. "
        "Do not judge the user. "
        "Base advice ONLY on the provided JSON. "
        "Return ONLY valid JSON."
    )

    user = (
        "Here is the user's spending summary as JSON:\n"
        f"{json.dumps(summary, ensure_ascii=False)}\n\n"
        "Return 3 to 5 recommendations as JSON with this format:\n"
        "{ \"recommendations\": ["
        "{ \"title\": \"...\", \"insight\": \"...\", \"action\": \"...\", \"priority\": \"LOW|MEDIUM|HIGH\" }"
        "] }"
    )

    text = github_chat([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

    data = json.loads(text)  # if JSON is invalid, it will raise an error
    return data.get("recommendations", [])