import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import AnonymousUser
from django.db.models import Sum
from groq import Groq
from decouple import config

from apps.depenseApp.models import Depense
from apps.revenueApp.models import Revenue
from apps.objectifsEpargnesApp.models import ObjEpargne

def detect_intent(message: str) -> str:
    msg = message.lower()

    if any(w in msg for w in ["dépense", "dépenser", "achat", "payer"]):
        return "DEPENSE"

    if any(w in msg for w in ["objectif", "épargne", "économiser", "save"]):
        return "EPARGNE"

    if any(w in msg for w in ["revenu", "salaire", "gain"]):
        return "REVENU"

    return "GLOBAL"
@csrf_exempt
@require_http_methods(["GET", "POST"])
def ai_chat(request):

    if request.method == "GET":
        return JsonResponse({
            "status": "OK",
            "message": "AI Chat ready"
        })

    try:
        data = json.loads(request.body or "{}")
        user_query = data.get("message", "").strip()

        if not user_query:
            return JsonResponse({"error": "Message vide"}, status=400)

        intent = detect_intent(user_query)

        is_authenticated = (
            hasattr(request, "user")
            and request.user.is_authenticated
            and not isinstance(request.user, AnonymousUser)
        )

        # =====================
        # USER CONNECTÉ
        # =====================
        if is_authenticated:
            user = request.user
            firstname = user.firstname or "Utilisateur"

            depenses = Depense.objects.filter(user=user)
            revenus = Revenue.objects.filter(user=user)
            objectifs = ObjEpargne.objects.filter(user=user)

            total_depenses = depenses.aggregate(
                total=Sum("amount")
            )["total"] or 0

            total_revenus = revenus.aggregate(
                total=Sum("amount")
            )["total"] or 0

            objectifs_info = [
                f"{o.name}: {o.total_contributed}/{o.target_amount} DT ({o.progress_percentage}%)"
                for o in objectifs
            ] or ["Aucun objectif d’épargne"]

            # 🎯 CONTEXTE SELON L’INTENTION
            if intent == "DEPENSE":
                context = f"Dépenses totales : {total_depenses} DT"
            elif intent == "REVENU":
                context = f"Revenus totaux : {total_revenus} DT"
            elif intent == "EPARGNE":
                context = " | ".join(objectifs_info)
            else:
                context = (
                    f"Revenus : {total_revenus} DT\n"
                    f"Dépenses : {total_depenses} DT\n"
                    f"Objectifs : {', '.join(objectifs_info)}"
                )

            prompt = f"""
Tu es Smart Coach, un assistant financier personnel intelligent.

Utilisateur : {firstname}
Contexte financier :
{context}

Question :
"{user_query}"

Règles :
- Réponds en français
- 2 à 3 phrases max
- Donne un conseil concret si possible
- Ton motivant, humain et professionnel
            """.strip()

        # =====================
        # USER NON CONNECTÉ
        # =====================
        else:
            prompt = f"""
Tu es Smart Coach, l’assistant de Smart Budgeting.
Explique la finance personnelle ou présente l'application.
Réponse simple et pédagogique.

Question :
"{user_query}"
            """.strip()

        # =====================
        # APPEL LLM
        # =====================
        client = Groq(api_key=config("GROQ_API_KEY"))
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un excellent coach financier."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=200,
        )

        return JsonResponse({
            "response": completion.choices[0].message.content.strip()
        })

    except Exception as e:
        return JsonResponse(
            {"error": "Erreur interne : " + str(e)},
            status=500
        )
