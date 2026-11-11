"""Gabarit multi-pages (accueil, carte, contact) pour les sites démo."""
import html, json
from urllib.parse import quote

E = html.escape
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'

HOURS_JS = r"""
<script>
(function(){
 const OH=%s; const D=['Mo','Tu','We','Th','Fr','Sa','Su'],N=['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche'];
 const week=D.map(()=>null);
 if(OH){OH.split(';').map(s=>s.trim()).filter(Boolean).forEach(rule=>{
  let m=rule.match(/^((?:[A-Z][a-z](?:-[A-Z][a-z])?,?)+)\s+(.*)$/),days=[...D.keys()],t=rule;
  if(m){days=[];m[1].split(',').filter(Boolean).forEach(p=>{const [a,b]=p.split('-');let i=D.indexOf(a),j=b?D.indexOf(b):i;if(i<0)return;do{days.push(i);i=(i+1)%%7}while(i!==(j+1)%%7)});t=m[2]}
  const r=/off|closed/.test(t)?[]:(t.match(/\d{1,2}:\d{2}-\d{1,2}:\d{2}/g)||[]); days.forEach(d=>week[d]=r)})}
 const now=new Date(),di=(now.getDay()+6)%%7,mins=now.getHours()*60+now.getMinutes(),toM=s=>{const [h,m]=s.split(':').map(Number);return h*60+m};
 const fmt=r=>r===null?'—':r.length?r.join(' · ').replace(/-/g,' – '):'Fermé';
 document.querySelectorAll('[data-hours]').forEach(ul=>{ if(OH) ul.innerHTML=week.map((r,i)=>`<li class="${i===di?'today':''}"><span>${N[i]}</span><span>${fmt(r)}</span></li>`).join('')});
 const t=week[di]||[];let open=false,until='',next='';
 t.forEach(r=>{let [a,b]=r.split('-').map(toM);if(b<=a)b+=1440;if(mins>=a&&mins<b){open=true;until=r.split('-')[1]}else if(mins<a&&!next)next=r.split('-')[0]});
 const txt=!OH?'Horaires sur demande':open?'Ouvert · jusqu’à '+until:next?'Fermé · ouvre à '+next:'Fermé aujourd’hui';
 document.querySelectorAll('[data-status]').forEach(e=>e.textContent=txt);
 document.querySelectorAll('[data-dot]').forEach(e=>e.classList.toggle('off',!open));
 document.querySelectorAll('[data-today]').forEach(e=>e.textContent=OH?fmt(t):'Sur demande');
})();
</script>"""


def price(p):
    return (f"{p:.2f}".replace(".", ",") if isinstance(p, float) else str(p)) + " €"


def render(c):
    """c : dict avec name, label, pitch, accent, addr, city, phone, tel, email, oh, lat, lon, imgs, gallery, feats, menu, slug, pay, price, brand, contact"""
    tel_ok = bool(c["tel"])
    call = f'<a class="btn p" href="tel:{c["tel"]}">Appeler</a>' if tel_ok else ""
    itin = f'https://www.openstreetmap.org/directions?to={c["lat"]}%2C{c["lon"]}'
    mapsrc = (f'https://www.openstreetmap.org/export/embed.html?bbox={c["lon"]-0.004},{c["lat"]-0.0025},{c["lon"]+0.004},{c["lat"]+0.0025}'
              f'&layer=mapnik&marker={c["lat"]},{c["lon"]}')

    def head(title, desc):
        return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                f'<meta name="robots" content="noindex"><title>{E(title)}</title><meta name="description" content="{E(desc)}">{FONTS}'
                f'<link rel="stylesheet" href="/assets/site.css"><style>:root{{--a:{c["accent"]}}}</style></head><body>')

    def top(active):
        nav = "".join(f'<a href="{h}" class="{"on" if k == active else ""}">{t}</a>' for k, h, t in
                      [("home", f'/{c["slug"]}/', "Accueil"), ("carte", f'/{c["slug"]}/carte/', "La carte"), ("contact", f'/{c["slug"]}/contact/', "Contact & accès")])
        return (f'<div class="demo">Aperçu créé pour <b>{E(c["name"])}</b> par {c["brand"]} — ce site peut être le vôtre dès aujourd’hui'
                f'<a href="{c["pay"]}?client_reference_id={c["slug"]}">Je le veux · {c["price"]} €</a></div>'
                f'<div class="topbar"><div class="wrap"><span><i class="dot" data-dot></i><span data-status>…</span></span>'
                f'<span class="hide-m">📍 {E(c["addr"])}</span>'
                + (f'<span>📞 <a href="tel:{c["tel"]}">{E(c["phone"])}</a></span>' if tel_ok else "") +
                f'</div></div><header class="nav"><div class="wrap"><a class="brand" href="/{c["slug"]}/">{E(c["name"])}</a><nav>{nav}</nav>'
                + (f'<a class="btn d" href="/{c["slug"]}/contact/#reserver">Réserver</a>' if c["kind"] in ("restaurant", "bar", "cafe") else call) +
                '</div></header>')

    def foot():
        return (f'<footer><div class="wrap"><div class="cols"><div><h4>{E(c["name"])}</h4><p>{E(c["pitch"])}</p><p style="margin-top:12px">{E(c["addr"])}</p>'
                + (f'<p><a href="tel:{c["tel"]}">{E(c["phone"])}</a></p>' if tel_ok else "") +
                f'</div><div><h4>Pages</h4><p><a href="/{c["slug"]}/">Accueil</a></p><p><a href="/{c["slug"]}/carte/">La carte</a></p><p><a href="/{c["slug"]}/contact/">Contact & accès</a></p></div>'
                f'<div><h4>Aujourd’hui</h4><p data-today>…</p><p style="margin-top:10px"><a href="{itin}" target="_blank" rel="noopener">Itinéraire →</a></p></div></div>'
                f'<div class="legal">© {E(c["name"])} · {E(c["city"])} — Site de démonstration réalisé par {c["brand"]}. Photos et carte d’illustration, remplacées par les vôtres. '
                f'<a href="mailto:{c["contact"]}?subject=STOP%20{c["slug"]}" style="text-decoration:underline">Ne plus être contacté</a></div></div></footer>'
                f'<div class="mbar">' + (f'<a href="tel:{c["tel"]}"><span>📞</span>Appeler</a>' if tel_ok else f'<a href="/{c["slug"]}/contact/"><span>✉️</span>Contact</a>') +
                f'<a href="{itin}" target="_blank" rel="noopener"><span>📍</span>Itinéraire</a><a href="/{c["slug"]}/carte/"><span>📖</span>La carte</a></div>'
                + HOURS_JS % json.dumps(c["oh"] or None) + '<script src="/assets/site.js" defer></script></body></html>')

    _mq = c["feats"] + [c["city"], c["label"].split(' · ')[0], 'Bienvenue']
    marquee = '<div class="marquee" aria-hidden="true"><div class="tr">' + ''.join(f'<span>{E(x)}</span>' for x in _mq * 4) + '</div></div>'
    menu_title = "Nos produits" if c["kind"] == "bakery" else "La carte"
    # ---------- Accueil ----------
    picks = [(sec, d) for sec, items in c["menu"] for d in items[:1]][:3]
    dishes = "".join(f'<div class="dish"><small>{E(sec)}</small><h3>{E(n)}</h3><p>{E(desc) or "&nbsp;"}</p><div class="pr">{price(p)}</div></div>'
                     for sec, (n, desc, p) in picks)
    gal = "".join(f'<img src="{u}" alt="" loading="lazy">' for u in c["gallery"][:5])
    feats = "".join(f"<li>{E(f)}</li>" for f in c["feats"])
    home = (head(f'{c["name"]} — {c["label"]} à {c["city"]}', f'{c["name"]}, {c["label"]} à {c["city"]}. {c["pitch"]}') + top("home") +
            f'<div class="hero"><img src="{c["imgs"][0]}" alt=""><div class="wrap"><div class="kicker">{E(c["label"])} · {E(c["city"])}</div>'
            f'<h1>{E(c["name"])}</h1><p>{E(c["pitch"])}</p><div class="btns"><a class="btn p" href="/{c["slug"]}/carte/">Voir {menu_title.lower()}</a>'
            + (f'<a class="btn o" href="tel:{c["tel"]}">📞 <span class="num">{E(c["phone"])}</span><span class="lbl">Appeler</span></a>' if tel_ok else f'<a class="btn o" href="/{c["slug"]}/contact/">Nous contacter</a>') +
            f'</div></div></div>'
            f'<div class="wrap"><div class="quick"><div><small>Aujourd’hui</small><b data-today>…</b></div><div><small>Adresse</small><b>{E(c["addr"])}</b><br><a href="{itin}" target="_blank" rel="noopener">Itinéraire →</a></div>'
            f'<div><small>Téléphone</small>' + (f'<b><a href="tel:{c["tel"]}">{E(c["phone"])}</a></b>' if tel_ok else '<b>Par message</b>') + '</div></div></div>'
            + marquee + f'<section><div class="wrap split"><div><div class="label">La maison</div><h2>Bienvenue chez {E(c["name"])}</h2>'
            f'<p class="lead">{E(c["pitch"])} Une adresse de quartier à {E(c["city"])}, où l’on vient pour bien manger et passer un bon moment.</p><ul class="tags">{feats}</ul></div>'
            f'<img src="{c["imgs"][1]}" alt="" loading="lazy"></div></section>'
            f'<section class="menu-prev"><div class="wrap"><div class="label" style="color:#ffd36b">{menu_title}</div><h2>Un aperçu de ce qui vous attend</h2>'
            f'<div class="dishes">{dishes}</div><p style="margin-top:30px"><a class="btn p" href="/{c["slug"]}/carte/">Toute {menu_title.lower()} →</a></p>'
            f'<p class="note">Carte indicative de démonstration : votre vraie carte et vos prix sont intégrés à la mise en ligne.</p></div></section>'
            f'<section><div class="wrap"><div class="label">En images</div><h2>L’ambiance</h2><div class="gallery">{gal}</div></div></section>'
            f'<section style="padding-top:0"><div class="wrap"><div class="label">Nous rendre visite</div><h2>Horaires & accès</h2><div class="visit">'
            f'<div class="card"><h3>Horaires</h3><ul class="hours" data-hours><li><span>Horaires sur demande</span></li></ul></div>'
            f'<div class="map"><iframe loading="lazy" src="{mapsrc}" title="Plan"></iframe></div></div></div></section>'
            f'<div class="cta"><h2>On vous garde une place ?</h2><p>{E(c["addr"])}</p>'
            + (f'<a class="btn" href="tel:{c["tel"]}">Appeler {E(c["name"])}</a>' if tel_ok else f'<a class="btn" href="/{c["slug"]}/contact/">Nous contacter</a>') +
            '</div>' + foot())

    # ---------- Carte ----------
    tabs = "".join(f'<a href="#s{i}">{E(sec)}</a>' for i, (sec, _) in enumerate(c["menu"]))
    secs = "".join(
        f'<div class="menu-sec" id="s{i}"><div class="wrap"><h2>{E(sec)}</h2>' +
        "".join(f'<div class="item"><div><div class="n">{E(n)}</div>' + (f'<div class="d">{E(d)}</div>' if d else "") +
                f'</div><div class="lead-dots"></div><div class="p">{price(p)}</div></div>' for n, d, p in items) +
        '</div></div>' for i, (sec, items) in enumerate(c["menu"]))
    carte = (head(f'{menu_title} — {c["name"]}', f'{menu_title} de {c["name"]} à {c["city"]}') + top("carte") +
             f'<div class="hero page-hero"><img src="{c["imgs"][2]}" alt=""><div class="wrap"><div class="kicker">{E(c["name"])}</div><h1>{menu_title}</h1></div></div>'
             f'<div class="menu-tabs"><div class="wrap">{tabs}</div></div>{secs}'
             f'<div class="wrap"><p class="note" style="padding:30px 0 70px">Carte indicative de démonstration. Prix TTC, service compris. Votre carte réelle est intégrée à la mise en ligne.</p></div>'
             + foot())

    # ---------- Contact ----------
    mail_to = c["email"] or c["contact"]
    contact = (head(f'Contact & accès — {c["name"]}', f'Contacter {c["name"]} à {c["city"]} : téléphone, adresse, horaires') + top("contact") +
               f'<div class="hero page-hero"><img src="{c["imgs"][1]}" alt=""><div class="wrap"><div class="kicker">{E(c["name"])}</div><h1>Contact & accès</h1></div></div>'
               f'<section><div class="wrap"><div class="cgrid">'
               + (f'<a class="card" href="tel:{c["tel"]}"><div class="ic">📞</div>Téléphone<b>{E(c["phone"])}</b></a>' if tel_ok else '') +
               f'<a class="card" href="{itin}" target="_blank" rel="noopener"><div class="ic">📍</div>Adresse<b>{E(c["addr"])}</b></a>'
               f'<div class="card"><div class="ic">🕒</div>Aujourd’hui<b data-today>…</b></div></div>'
               f'<div class="visit"><div class="card" id="reserver"><h3>{"Réserver une table" if c["kind"] in ("restaurant", "bar", "cafe") else "Nous écrire"}</h3>'
               f'<p style="color:var(--ink2);font-size:15px">Envoyez votre demande, nous vous confirmons rapidement.</p>'
               f'<form class="resa" onsubmit="event.preventDefault();const f=new FormData(this);location.href=\'mailto:{mail_to}?subject=\'+encodeURIComponent(\'Demande — \'+f.get(\'nom\'))+\'&body=\'+encodeURIComponent([...f].map(([k,v])=>k+\' : \'+v).join(\'\\n\'))">'
               f'<label>Nom<input name="nom" required></label><label>Téléphone<input name="telephone" type="tel"></label>'
               f'<label>Date<input name="date" type="date"></label><label>Heure<input name="heure" type="time"></label>'
               f'<label class="full">Nombre de personnes<select name="personnes"><option>1</option><option selected>2</option><option>3</option><option>4</option><option>5</option><option>6+</option></select></label>'
               f'<label class="full">Message<textarea name="message" rows="3"></textarea></label><button class="btn p">Envoyer la demande</button></form></div>'
               f'<div class="map"><iframe loading="lazy" src="{mapsrc}" title="Plan"></iframe></div></div>'
               f'<div class="card" style="margin-top:28px"><h3>Horaires d’ouverture</h3><ul class="hours" data-hours><li><span>Horaires sur demande</span></li></ul></div>'
               f'</div></section>' + foot())
    return {"": home, "carte": carte, "contact": contact}
