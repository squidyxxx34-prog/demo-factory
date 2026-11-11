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
  const heroImg = document.querySelector('.hero img');
  const nav = document.querySelector('header.nav');
  let ticking = false;
  addEventListener('scroll', () => {
    if (ticking) return; ticking = true;
    requestAnimationFrame(() => {
      const y = scrollY;
      if (heroImg && !reduce && y < innerHeight * 1.2) heroImg.style.transform = `translate3d(0,${y * 0.28}px,0) scale(1.06)`;
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
