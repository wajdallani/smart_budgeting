

# Create your views here.
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from groq import Groq
from decouple import config

# @login_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def ai_chat(request):
    if request.method == 'GET':
        return JsonResponse({
            "status": "OK",
            "message": "AI Chat is ready. Send POST with {\"message\": \"...\"}"
        })

    try:
        data = json.loads(request.body)
        user_query = data.get("message", "").strip()

        if not user_query:
            return JsonResponse({"error": "Message vide"}, status=400)

        # 👤 Optional user name
        mock_user_firstname = getattr(request.user, 'first_name', 'Utilisateur')

        # 🧠 Build prompt for free conversation
        prompt = f"""
Tu es *Smart Coach*, un assistant financier et éducatif intelligent.
Réponds en *français*, de façon *claire, concise et utile* (2–3 phrases max).
Tu peux discuter de *finance personnelle, finance globale, économie, investissement*, ou toute question liée à l'argent.

Question de l'utilisateur : "{user_query}"
        """.strip()

        # 🚀 Call Groq LLM
        try:
            client = Groq(api_key=config('GROQ_API_KEY'))
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Tu es un coach financier utile et clair, capable de parler de tout."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=200
            )
            response_text = chat_completion.choices[0].message.content.strip()

        except Exception:
            # Fallback if Groq fails
            response_text = f"Bonjour {mock_user_firstname} ! Je suis Smart Coach. Pose-moi une question sur la finance ou l'économie, et je ferai de mon mieux pour y répondre."

        return JsonResponse({"response": response_text})

    except Exception as e:
        return JsonResponse({"error": "Erreur interne : " + str(e)}, status=500)