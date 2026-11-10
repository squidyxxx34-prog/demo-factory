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
U = "https://images.unsplash.com/photo-{}?auto=format&fit=crop&w=2000&q=80"
IMGS = {
    "restaurant": ["1517248135467-4c7edcad34c4", "1414235077428-338989a2e8c0", "1667388969250-1c7220bf3f37"],
    "cafe": ["1554118811-1e0d58224f24", "1502462041640-b3d7e50d0662", "1445116572660-236099ec97a0"],
    "fast_food": ["1628324716243-0c9c29971a58", "1471110338536-858caa3dbe45", "1589778314823-d1c2bde0a31b"],
    "bar": ["1605270012917-bf157c5a9541", "1566417713940-fe7c737a9ef2", "1623408859815-22534357b3db"],
    "hairdresser": ["1600948836101-f9ffda59d250", "1626379501846-0df4067b8bb9", "1626383137804-ff908d2753a2"],
    "beauty": ["1600948836101-f9ffda59d250", "1626379501846-0df4067b8bb9", "1626383137804-ff908d2753a2"],
    "bakery": ["1509440159596-0249088772ff", "1599819055803-717bba43890f", "1509440159596-0249088772ff"],
    "butcher": ["1625643269470-5d3e7b69fa34", "1615937662601-4724eceda00f", "1767491654834-13bf58ed9522"],
    "pizza": ["1579751626657-72bc17010498", "1622880833523-7cf1c0bd4296", "1763647836753-e06fe1f8707b"],
    "burger": ["1568901346375-23c9450c58cd", "1572802419224-296b0aeee0d9", "1667388969250-1c7220bf3f37"],
    "chinese": ["1623341214825-9f4f963727da", "1638866281450-3933540af86a", "1414235077428-338989a2e8c0"],
    "seafood": ["1606850780554-b55ea4dd0b70", "1559339352-11d035aa65de", "1618055301293-494ab4c71f9f"],
    "mexican": ["1628324716243-0c9c29971a58", "1471110338536-858caa3dbe45", "1589778314823-d1c2bde0a31b"],
    "spanish": ["1656423521731-9665583f100c", "1609950547346-a4f431435b2b", "1559339352-11d035aa65de"],
    "french": ["1580654842920-37b786f32bfc", "1579027989536-b7b1f875659b", "1667388969250-1c7220bf3f37"],
    "italian": ["1498579150354-977475b7ea0b", "1598720290281-9f26ae6d6f81", "1414235077428-338989a2e8c0"],
    "sandwich": ["1621523133136-cea844f32bdf", "1621523131496-0a1af8e2b20c", "1554118811-1e0d58224f24"],
}


def images(kind, cuisine):
    for c in cuisine.split(";"):
        c = c.strip()
        key = {"noodle": "chinese", "ramen": "chinese", "tapas": "spanish", "breakfast": "sandwich", "fish": "seafood"}.get(c, c)
        if key in IMGS:
            return [U.format(i) for i in IMGS[key]]
    return [U.format(i) for i in IMGS.get(kind, IMGS["restaurant"])]


def name_html(name):
    w = name.split()
    if len(w) < 2:
        return html.escape(name)
    return html.escape(" ".join(w[:-1])) + " <em>" + html.escape(w[-1]) + "</em>"


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
    imgs = images(kind, t.get("cuisine", ""))
    bbox = f"{lon-0.004},{lat-0.0025},{lon+0.004},{lat+0.0025}" if lat else ""
    rep = {
        "{{NAME}}": html.escape(name), "{{LABEL}}": html.escape(label), "{{PITCH}}": html.escape(pitch),
        "{{ACCENT}}": accent, "{{DARK}}": dark, "{{ADDR}}": html.escape(addr or city),
        "{{PHONE}}": html.escape(phone), "{{TEL}}": re.sub(r"[^\d+]", "", phone),
        "{{PHONE_DISPLAY}}": "" if phone else "hidden", "{{HOURS}}": hours_html(t.get("opening_hours", "")),
        "{{FEATURES}}": "".join(f"<li class='glass pill'>{html.escape(f)}</li>" for f in feats),
        "{{MAP}}": f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat},{lon}" if lat else "",
        "{{CITY}}": html.escape(city), "{{NAME_HTML}}": name_html(name),
        "{{OH_JSON}}": json.dumps(t.get("opening_hours") or None), "{{LAT}}": str(lat), "{{LON}}": str(lon),
        "{{IMG1}}": imgs[0], "{{IMG2}}": imgs[1], "{{IMG3}}": imgs[2], "{{PRICE}}": str(CFG["price"]), "{{PAY}}": CFG["payment_link"],
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
