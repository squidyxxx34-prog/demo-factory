#!/usr/bin/env python3
"""Génère un site démo par prospect (data/prospects.json -> docs/<slug>/index.html)
+ la liste des mails de prospection (data/outreach.csv)."""
import csv, html, json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = (ROOT / "templates" / "site.html").read_text(encoding="utf-8")
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

THEMES = {
    "restaurant": ("#b4532a", "#2b1a12", "Restaurant", "Une cuisine généreuse, faite maison, dans une ambiance chaleureuse."),
    "cafe": ("#8a5a3b", "#241812", "Café", "Le bon café, des douceurs maison et un lieu où l'on se sent bien."),
    "fast_food": ("#d9822b", "#1f1a14", "Restauration rapide", "Rapide, gourmand et préparé à la minute."),
    "bar": ("#7a3b69", "#1a1220", "Bar", "Un comptoir convivial, de bons verres et une ambiance qui donne envie de rester."),
    "hairdresser": ("#a8657a", "#1e1418", "Coiffeur", "Coupes, couleurs et soins par des passionnés, à votre écoute."),
    "beauty": ("#b07d8c", "#1f1619", "Institut de beauté", "Un moment pour vous : soins, beauté et bien-être."),
    "bakery": ("#c08a3e", "#241b10", "Boulangerie", "Pains au levain, viennoiseries et pâtisseries faits chaque matin."),
    "butcher": ("#9c2f2f", "#1c1010", "Boucherie", "Viandes sélectionnées avec soin, conseils de vrais artisans."),
    "florist": ("#5b8a5a", "#121c13", "Fleuriste", "Bouquets de saison et compositions sur mesure pour chaque occasion."),
}
CUISINE_FR = {"italian": "italienne", "pizza": "pizzeria", "french": "française", "japanese": "japonaise",
    "sushi": "sushi", "chinese": "chinoise", "indian": "indienne", "kebab": "kebab", "burger": "burgers",
    "thai": "thaïlandaise", "lebanese": "libanaise", "vietnamese": "vietnamienne", "mexican": "mexicaine",
    "regional": "régionale", "crepe": "crêperie", "asian": "asiatique", "moroccan": "marocaine",
    "spanish": "espagnole", "greek": "grecque", "turkish": "turque", "seafood": "fruits de mer",
    "coffee_shop": "coffee shop", "sandwich": "sandwichs", "tapas": "tapas", "korean": "coréenne", "breakfast": "petit-déj", "salad": "salades", "pasta": "pâtes", "noodle": "nouilles", "international": "du monde"}
DAYS = {"Mo": "Lun", "Tu": "Mar", "We": "Mer", "Th": "Jeu", "Fr": "Ven", "Sa": "Sam", "Su": "Dim", "PH": "Fériés", "off": "fermé"}


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:50] or "commerce"


def hours_html(oh):
    if not oh:
        return "<p class='muted'>Horaires sur demande — appelez-nous.</p>"
    rows = []
    for part in oh.split(";"):
        part = part.strip()
        for k, v in DAYS.items():
            part = re.sub(rf"\b{k}\b", v, part)
        if part:
            rows.append(f"<li>{html.escape(part)}</li>")
    return f"<ul class='hours'>{''.join(rows)}</ul>"


def build(p):
    t = p["tags"]
    kind = t.get("amenity") or t.get("shop") or "restaurant"
    accent, dark, label, pitch = THEMES.get(kind, THEMES["restaurant"])
    name = t["name"]
    cuisines = [CUISINE_FR.get(c.strip(), c.strip()) for c in t.get("cuisine", "").split(";") if c.strip()]
    if cuisines and kind in ("restaurant", "fast_food"):
        label = f"{label} · cuisine {', '.join(cuisines[:2])}"
    street = " ".join(x for x in [t.get("addr:housenumber", ""), t.get("addr:street", "")] if x).strip()
    city = t.get("addr:city") or CFG["city"]
    addr = ", ".join(x for x in [street, f"{t.get('addr:postcode', '')} {city}".strip()] if x)
    phone = t.get("phone") or t.get("contact:phone") or ""
    lat, lon = p.get("lat") or p.get("center", {}).get("lat"), p.get("lon") or p.get("center", {}).get("lon")
    slug = f"{slugify(name)}-{p['id'] % 10000}"
    feats = []
    if t.get("outdoor_seating") == "yes": feats.append("Terrasse")
    if t.get("takeaway") in ("yes", "only"): feats.append("À emporter")
    if t.get("delivery") == "yes": feats.append("Livraison")
    if t.get("wheelchair") == "yes": feats.append("Accès PMR")
    if t.get("diet:vegetarian") in ("yes", "only"): feats.append("Options végétariennes")
    feats = feats or ["Accueil chaleureux", "Produits de qualité", "Au cœur de " + city]
    bbox = f"{lon-0.004},{lat-0.0025},{lon+0.004},{lat+0.0025}" if lat else ""
    rep = {
        "{{NAME}}": html.escape(name), "{{LABEL}}": html.escape(label), "{{PITCH}}": html.escape(pitch),
        "{{ACCENT}}": accent, "{{DARK}}": dark, "{{ADDR}}": html.escape(addr or city),
        "{{PHONE}}": html.escape(phone), "{{TEL}}": re.sub(r"[^\d+]", "", phone),
        "{{PHONE_DISPLAY}}": "" if phone else "hidden", "{{HOURS}}": hours_html(t.get("opening_hours", "")),
        "{{FEATURES}}": "".join(f"<li>{html.escape(f)}</li>" for f in feats),
        "{{MAP}}": f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat},{lon}" if lat else "",
        "{{CITY}}": html.escape(city), "{{PRICE}}": str(CFG["price"]), "{{PAY}}": CFG["payment_link"],
        "{{CONTACT}}": CFG["contact_email"], "{{BRAND}}": CFG["brand"], "{{SLUG}}": slug,
    }
    out = TPL
    for k, v in rep.items():
        out = out.replace(k, v)
    d = ROOT / "docs" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(out, encoding="utf-8")
    return slug, name, kind, t.get("email") or t.get("contact:email") or "", phone, addr


def main():
    prospects = json.loads((ROOT / "data" / "prospects.json").read_text(encoding="utf-8"))
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(prospects)
    rows = []
    for p in prospects[:limit]:
        if not p.get("tags", {}).get("name"):
            continue
        slug, name, kind, email, phone, addr = build(p)
        url = f"{CFG['base_url']}/{slug}/"
        rows.append({"slug": slug, "name": name, "kind": kind, "email": email, "phone": phone, "addr": addr, "url": url,
                     "subject": f"{name} : votre site internet est prêt",
                     "body": CFG["email_template"].format(name=name, url=url, price=CFG["price"], pay=CFG["payment_link"], brand=CFG["brand"], sender=CFG["sender_name"])})
    with open(ROOT / "data" / "outreach.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    idx = "".join(f"<li><a href='{r['slug']}/'>{html.escape(r['name'])}</a> — {html.escape(r['kind'])}</li>" for r in rows)
    (ROOT / "docs" / "index.html").write_text(f"<!doctype html><meta charset=utf-8><meta name=robots content=noindex><title>Démos</title><body style='font-family:system-ui;max-width:700px;margin:40px auto'><h1>Démos ({len(rows)})</h1><ul>{idx}</ul>", encoding="utf-8")
    print(f"{len(rows)} sites générés, {sum(1 for r in rows if r['email'])} avec email")


if __name__ == "__main__":
    main()
