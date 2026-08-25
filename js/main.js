document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('.header');
  const burger = document.querySelector('.burger');
  const nav = document.querySelector('.nav');
  const backToTop = document.querySelector('.back-to-top');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  let scrollTicking = false;
  function updateScrollUI() {
    scrollTicking = false;
    if (header) header.classList.toggle('scrolled', window.scrollY > 50);
    if (backToTop) {
      backToTop.classList.toggle('visible', window.scrollY > 400);
    }
  }

  window.addEventListener('scroll', () => {
    if (!scrollTicking) {
      scrollTicking = true;
      requestAnimationFrame(updateScrollUI);
    }
  }, { passive: true });

  updateScrollUI();

  function closeMenu() {
    burger.classList.remove('active');
    nav.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
  }

  if (burger && nav) {
    burger.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      burger.classList.toggle('active', open);
      burger.setAttribute('aria-expanded', String(open));
    });

    nav.addEventListener('click', (e) => {
      if (e.target.closest('a')) closeMenu();
    });

    document.addEventListener('click', (e) => {
      if (!burger.contains(e.target) && !nav.contains(e.target)) closeMenu();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        closeMenu();
        burger.focus();
      }
    });
  }

  window.addEventListener('resize', () => {
    if (window.innerWidth > 768 && burger && nav) {
      closeMenu();
    }
  });

  if (backToTop) {
    backToTop.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: reduceMotion.matches ? 'auto' : 'smooth'
      });
    });
  }

  const fadeEls = document.querySelectorAll('.fade-in');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, i * 80);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  fadeEls.forEach(el => observer.observe(el));

  const searchInput = document.querySelector('.search-bar input');
  const resultsBox = document.getElementById('search-results');
  const museumsIndex = Array.isArray(window.MUSEUMS_INDEX) ? window.MUSEUMS_INDEX : [];

  if (searchInput && resultsBox && museumsIndex.length) {
    let activeIndex = -1;

    function debounce(fn, ms) {
      let t;
      return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
    }

    function closeResults() {
      resultsBox.hidden = true;
      resultsBox.innerHTML = '';
      activeIndex = -1;
      searchInput.setAttribute('aria-expanded', 'false');
    }

    function setActive(items, idx) {
      activeIndex = idx;
      items.forEach((el, i) => el.classList.toggle('active', i === activeIndex));
      if (items[activeIndex]) items[activeIndex].scrollIntoView({ block: 'nearest' });
    }

    searchInput.addEventListener('input', debounce(() => {
      const q = searchInput.value.toLowerCase().trim();
      if (!q) {
        closeResults();
        return;
      }
      const matches = museumsIndex
        .filter(m => (m.name + ' ' + m.city + ' ' + m.country).toLowerCase().includes(q))
        .slice(0, 8);

      resultsBox.innerHTML = '';
      if (!matches.length) {
        const nothing = document.createElement('p');
        nothing.className = 'search-nothing';
        nothing.textContent = 'Ничего не найдено';
        resultsBox.appendChild(nothing);
      } else {
        matches.forEach(m => {
          const link = document.createElement('a');
          link.className = 'search-result';
          link.href = m.url;
          link.setAttribute('role', 'option');
          const name = document.createElement('span');
          name.className = 'search-name';
          name.textContent = m.name;
          const meta = document.createElement('span');
          meta.className = 'search-meta';
          meta.textContent = m.city + ', ' + m.country;
          link.append(name, meta);
          resultsBox.appendChild(link);
        });
      }
      resultsBox.hidden = false;
      searchInput.setAttribute('aria-expanded', 'true');
      setActive([...resultsBox.querySelectorAll('.search-result')], -1);
    }, 150));

    searchInput.addEventListener('keydown', (e) => {
      const items = [...resultsBox.querySelectorAll('.search-result')];
      if (e.key === 'Escape') {
        closeResults();
        return;
      }
      if (resultsBox.hidden || !items.length) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        const delta = e.key === 'ArrowDown' ? 1 : -1;
        setActive(items, Math.max(-1, Math.min(items.length - 1, activeIndex + delta)));
      } else if (e.key === 'Enter' && activeIndex >= 0) {
        e.preventDefault();
        window.location.href = items[activeIndex].href;
      }
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search-bar')) closeResults();
    });
  }

  function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-target'), 10);
    if (reduceMotion.matches) {
      el.textContent = target;
      return;
    }
    const duration = 1200;
    const start = performance.now();
    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  const counters = document.querySelectorAll('.stat-number');
  if (counters.length) {
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(c => counterObserver.observe(c));
  }
});
