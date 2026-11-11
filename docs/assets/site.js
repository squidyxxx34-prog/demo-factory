(function () {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.documentElement.classList.add('js');

  // Titre principal : découpage en mots pour une apparition en cascade
  document.querySelectorAll('.hero h1').forEach(h => {
    const words = h.textContent.trim().split(/\s+/);
    h.innerHTML = words.map((w, i) => `<span class="w"><span style="--d:${0.15 + i * 0.09}s">${w}</span></span>`).join(' ');
  });

  // Éléments révélés au défilement (avec décalage entre enfants)
  const groups = ['.quick > div', '.dishes .dish', '.gallery img', '.menu-sec .item', '.cgrid .card', '.tags li', '.hours li', '.footer-col'];
  groups.forEach(sel => {
    const els = document.querySelectorAll(sel);
    els.forEach((el, i) => { el.classList.add('rv'); el.style.setProperty('--d', (i % 8) * 0.07 + 's'); });
  });
  document.querySelectorAll('section h2, section .label, section .lead, .split img, .visit > *, .cta > *, .menu-sec h2, .note')
    .forEach(el => el.classList.add('rv'));

  if (reduce || !('IntersectionObserver' in window)) {
    document.querySelectorAll('.rv').forEach(el => el.classList.add('in'));
  } else {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    document.querySelectorAll('.rv').forEach(el => {
      if (el.tagName === 'IMG' && el.parentElement) {
        // les images à « clip-path » ne sont pas détectées : on observe leur conteneur
        const p = el.parentElement;
        if (!p._rvObs) {
          p._rvObs = true;
          new IntersectionObserver((es, o) => es.forEach(e => {
            if (e.isIntersecting) { p.querySelectorAll('img.rv').forEach(i => i.classList.add('in')); o.disconnect(); }
          }), { threshold: 0.15 }).observe(p);
        }
      } else io.observe(el);
    });
  }

  // Parallaxe douce sur la photo d'en-tête + navigation compacte au défilement
  const heroOf = () => document.querySelector('.view.on .hero img');
  const nav = document.querySelector('header.nav');
  let ticking = false;
  addEventListener('scroll', () => {
    if (ticking) return; ticking = true;
    requestAnimationFrame(() => {
      const y = scrollY;
      const hi = heroOf(); if (hi && !reduce && y < innerHeight * 1.2) hi.style.setProperty('--py', (y * 0.28) + 'px');
      if (nav) nav.classList.toggle('scrolled', y > 40);
      ticking = false;
    });
  }, { passive: true });

  // Barre de progression de lecture
  const bar = document.createElement('div'); bar.className = 'progress'; document.body.appendChild(bar);
  addEventListener('scroll', () => {
    const h = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = `scaleX(${h > 0 ? scrollY / h : 0})`;
  }, { passive: true });

  // Effet magnétique léger sur les boutons principaux
  if (!reduce && matchMedia('(pointer:fine)').matches) {
    document.querySelectorAll('.btn.p, .btn.d').forEach(b => {
      b.addEventListener('pointermove', e => {
        const r = b.getBoundingClientRect();
        b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.12}px,${(e.clientY - r.top - r.height / 2) * 0.2}px)`;
      });
      b.addEventListener('pointerleave', () => { b.style.transform = ''; });
    });
  }
})();

// Menu plein écran (bouton trois barres)
(function () {
  const b = document.querySelector('.burger'), ov = document.getElementById('menu');
  if (!b || !ov) return;
  const set = open => {
    document.documentElement.classList.toggle('menu-open', open);
    b.setAttribute('aria-expanded', open); b.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
    ov.setAttribute('aria-hidden', !open);
  };
  b.addEventListener('click', () => set(!document.documentElement.classList.contains('menu-open')));
  ov.querySelectorAll('a').forEach(a => a.addEventListener('click', () => set(false)));
  addEventListener('keydown', e => { if (e.key === 'Escape') set(false); });
})();

// Navigation instantanée entre les vues (tout est déjà chargé, une seule URL)
(function () {
  const views = [...document.querySelectorAll('.view')];
  if (!views.length) return;
  const names = views.map(v => v.dataset.view);
  const show = (name, scrollId) => {
    if (!names.includes(name)) name = 'accueil';
    const swap = () => {
      views.forEach(v => v.classList.toggle('on', v.dataset.view === name));
      document.querySelectorAll('header.nav nav a, .menu-ov a.big').forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + name));
      const t = scrollId && document.getElementById(scrollId);
      if (t) t.scrollIntoView({ block: 'start' }); else scrollTo(0, 0);
    };
    const cur = document.querySelector('.view.on');
    if (cur && cur.dataset.view === name) { swap(); return; }
    if (document.startViewTransition) document.startViewTransition(swap); else swap();
  };
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href^="#"]'); if (!a) return;
    const h = a.getAttribute('href').slice(1);
    if (names.includes(h)) {
      e.preventDefault();
      if (location.hash !== '#' + h) history.pushState(null, '', h === 'accueil' ? location.pathname : '#' + h);
      show(h, a.dataset.scroll);
    } else if (/^s\d+$/.test(h)) {
      e.preventDefault();
      const t = document.getElementById(h); if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
  addEventListener('popstate', () => show(location.hash.slice(1) || 'accueil'));
  if (location.hash.length > 1) show(location.hash.slice(1));
  // précharge les images des autres vues dès que l'accueil est affiché
  addEventListener('load', () => document.querySelectorAll('.view:not(.on) img').forEach(i => { i.loading = 'eager'; }));
})();
