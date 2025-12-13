# apps/depenseApp/utils.py
import re
from decimal import Decimal
from typing import Optional, Dict

from PIL import Image
import pytesseract
from pytesseract import TesseractError, TesseractNotFoundError
from datetime import datetime as dt  # pour la date

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_invoice_data_from_file(file_obj) -> Dict[str, Optional[str]]:
    """
    Utilise l'OCR sur un fichier image et tente d'extraire
    un montant et une date pertinents (évite les numéros de téléphone, etc.).
    Retourne :
      - amount : string avec 2 décimales ("4050.00") ou None
      - date   : string "YYYY-MM-DD" ou None (compatible <input type="date">)
    """
    try:
        img = Image.open(file_obj)
    except Exception:
        return {"amount": None, "date": None}

    # un peu de pré-traitement
    img = img.convert("L")
    w, h = img.size
    if w < 1500:
        img = img.resize((w * 2, h * 2))

    try:
        text = pytesseract.image_to_string(img, config="--psm 6")
    except (TesseractError, TesseractNotFoundError):
        return {"amount": None, "date": None}

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    lines_lower = [l.lower() for l in lines]

    detected_amount = None
    detected_date_raw = None

    amount_pattern = r'\d{1,3}(?:[\s.,]\d{3})*(?:[.,]\d{2})?'  # 4 050,000 / 8100 / 3 999,780...

    def normalize_amount(s: str) -> Decimal:
        s = s.replace(" ", "")
        if "," in s and "." in s:
            if s.find(",") > s.find("."):
                s = s.replace(".", "").replace(",", ".")
        elif "," in s and "." not in s:
            s = s.replace(",", ".")
        return Decimal(s)

    # --- 1) Chercher sur les lignes avec mots-clés liés à l'argent ---
    keywords = ["montant", "total", "reste à payer", "reste a payer", "encours", "eur"]

    candidates = []
    for raw, low in zip(lines, lines_lower):
        if any(k in low for k in keywords):
            nums = re.findall(amount_pattern, raw)
            for n in nums:
                try:
                    dec = normalize_amount(n)
                except Exception:
                    continue
                # filtre anti "téléphone"
                if "." not in str(dec) and dec > 999999:
                    continue
                candidates.append((n, dec))

    if candidates:
        n, dec = max(candidates, key=lambda x: x[1])
        detected_amount = f"{dec:.2f}"
    else:
        all_nums = re.findall(amount_pattern, " ".join(lines))
        possible = []
        for n in all_nums:
            try:
                dec = normalize_amount(n)
            except Exception:
                continue
            if "." not in str(dec) and dec > 999999:
                continue
            possible.append((n, dec))
        if possible:
            n, dec = max(possible, key=lambda x: x[1])
            detected_amount = f"{dec:.2f}"

    # --- 2) Date ---
       # --- 2) Date (formats classiques + année sur 2 chiffres) ---
    text_clean = " ".join(lines)

    # On capte :
    #  - 02/02/2025
    #  - 02-02-2025
    #  - 2025-02-02
    #  - 06/05/25
    #  - 06-05-25
    date_patterns = [
        r'\b(\d{2}/\d{2}/\d{4})\b',  # 02/02/2025
        r'\b(\d{2}-\d{2}-\d{4})\b',  # 02-02-2025
        r'\b(\d{4}-\d{2}-\d{2})\b',  # 2025-02-02
        r'\b(\d{2}/\d{2}/\d{2})\b',  # 06/05/25
        r'\b(\d{2}-\d{2}-\d{2})\b',  # 06-05-25
    ]

    detected_date_raw = None
    for pattern in date_patterns:
        m = re.search(pattern, text_clean)
        if m:
            detected_date_raw = m.group(1)
            break

    detected_date_normalized = None
    if detected_date_raw:
        # On essaie plusieurs formats possibles
        possible_formats = [
            "%Y-%m-%d",  # 2025-05-06
            "%d/%m/%Y",  # 06/05/2025
            "%d-%m-%Y",  # 06-05-2025
            "%d/%m/%y",  # 06/05/25
            "%d-%m-%y",  # 06-05-25
        ]
        from datetime import datetime as dt
        for fmt in possible_formats:
            try:
                d = dt.strptime(detected_date_raw, fmt).date()
                # Si année à 2 chiffres et Python l'interprète genre 1925,
                # on peut décider de forcer > 2000 pour ton cas d’usage.
                if d.year < 2000:
                    d = d.replace(year=d.year + 100)
                detected_date_normalized = d.strftime("%Y-%m-%d")
                break
            except ValueError:
                continue

    return {
        "amount": detected_amount,
        "date": detected_date_normalized,
    }
