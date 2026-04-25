/* =============================================
   SocraticRL – Landing Page JavaScript
   Animations, interactions, scroll effects
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {

  // ---- Navbar scroll effect ----
  const navbar = document.getElementById('navbar');
  let lastScroll = 0;

  window.addEventListener('scroll', () => {
    const currentScroll = window.scrollY;
    if (currentScroll > 60) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
    lastScroll = currentScroll;
  });

  // ---- Hamburger menu ----
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('nav-links');
  hamburger?.addEventListener('click', () => {
    navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
    navLinks.style.flexDirection = 'column';
    navLinks.style.position = 'absolute';
    navLinks.style.top = '70px';
    navLinks.style.left = '0';
    navLinks.style.right = '0';
    navLinks.style.background = 'rgba(8, 3, 15, 0.95)';
    navLinks.style.backdropFilter = 'blur(20px)';
    navLinks.style.padding = '20px 24px';
    navLinks.style.borderBottom = '1px solid rgba(168, 85, 247, 0.12)';
    navLinks.style.zIndex = '999';
  });

  // ---- Understanding bar animation ----
  const ubFill = document.getElementById('ub-fill');
  const ubCounter = document.getElementById('ub-counter');

  function animateUnderstanding(targetPct, duration = 2500) {
    let start = null;
    const startVal = parseFloat(ubFill.style.width) || 0;
    const endVal = targetPct;

    function step(ts) {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      const current = startVal + (endVal - startVal) * eased;
      ubFill.style.width = current + '%';
      ubCounter.textContent = Math.round(current) + '%';
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // ---- Intersection Observer for reveal animations ----
  const revealEls = document.querySelectorAll(
    '.metric-card, .feature-card, .step, .scenario-card, .section-header'
  );

  revealEls.forEach(el => el.classList.add('reveal'));

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');

        // Trigger understanding bar when hero card is visible
        if (entry.target.closest('.hero-visual')) {
          setTimeout(() => animateUnderstanding(74, 2500), 400);
        }
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });

  revealEls.forEach(el => revealObserver.observe(el));

  // ---- Hero visual observer ----
  const heroVisual = document.getElementById('hero-visual');
  if (heroVisual) {
    const heroObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setTimeout(() => animateUnderstanding(74, 2500), 300);
          heroObs.disconnect();
        }
      });
    }, { threshold: 0.3 });
    heroObs.observe(heroVisual);
  }

  // ---- Understanding bar cycling ----
  let cycles = 0;
  const ubValues = [74, 0, 45, 91];
  setInterval(() => {
    cycles = (cycles + 1) % ubValues.length;
    const target = ubValues[cycles];
    animateUnderstanding(target, 1800);
  }, 5000);

  // ---- Staggered reveal for grid items ----
  const staggerGroups = [
    { selector: '.metric-card', delay: 120 },
    { selector: '.feature-card', delay: 100 },
    { selector: '.scenario-card', delay: 100 },
    { selector: '.step', delay: 150 },
  ];

  staggerGroups.forEach(({ selector, delay }) => {
    const items = document.querySelectorAll(selector);
    const groupObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const allItems = [...items];
          const idx = allItems.indexOf(entry.target);
          setTimeout(() => {
            entry.target.classList.add('visible');
          }, idx * delay);
          groupObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    items.forEach(el => groupObserver.observe(el));
  });

  // ---- Section header reveals ----
  document.querySelectorAll('.section-header').forEach((el, i) => {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.2 });
    obs.observe(el);
  });

  // ---- Smooth number counters for stats ----
  function animateNumber(el, from, to, duration, suffix = '') {
    let start = null;
    function step(ts) {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const val = from + (to - from) * eased;
      el.textContent = (Number.isInteger(to) ? Math.round(val) : val.toFixed(1)) + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // ---- Stats counter on hero visibility ----
  const statsObs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        statsObs.disconnect();
        // Nothing to do here since they're static — 
        // but add a "count-up" if desired
      }
    });
  }, { threshold: 0.5 });

  const heroStats = document.getElementById('hero-stats');
  if (heroStats) statsObs.observe(heroStats);

  // ---- Student profile chip toggle ----
  const chips = document.querySelectorAll('.sp-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
    });
  });

  // ---- Copy install commands on click ----
  const cmdEls = document.querySelectorAll('.cmd');
  cmdEls.forEach(el => {
    el.style.cursor = 'pointer';
    el.title = 'Click to copy';
    el.addEventListener('click', () => {
      navigator.clipboard?.writeText(el.textContent).then(() => {
        const orig = el.textContent;
        el.textContent = '✓ Copied!';
        el.style.color = 'var(--green-400)';
        setTimeout(() => {
          el.textContent = orig;
          el.style.color = '';
        }, 2000);
      });
    });
  });

  // ---- Smooth scroll for nav links ----
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Close mobile menu if open
        if (navLinks && window.innerWidth < 768) {
          navLinks.style.display = 'none';
        }
      }
    });
  });

  // ---- Parallax on orbs ----
  window.addEventListener('mousemove', (e) => {
    const orbs = document.querySelectorAll('.hero-orb');
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    const dx = (e.clientX - centerX) / centerX;
    const dy = (e.clientY - centerY) / centerY;

    orbs.forEach((orb, i) => {
      const factor = (i + 1) * 12;
      orb.style.transform = `translate(${dx * factor}px, ${dy * factor}px)`;
    });
  });

  // ---- Floating badges entrance animation ----
  setTimeout(() => {
    document.querySelectorAll('.floating-badge').forEach((badge, i) => {
      badge.style.opacity = '0';
      badge.style.transform = 'translateY(20px)';
      setTimeout(() => {
        badge.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        badge.style.opacity = '1';
        badge.style.transform = 'translateY(0)';
      }, 800 + i * 200);
    });
  }, 200);

  // ---- Initial understanding bar ----
  setTimeout(() => {
    animateUnderstanding(74, 2000);
  }, 1200);

  // ---- Turn ring progress animation ----
  const turnProg = document.querySelector('.turn-prog');
  if (turnProg) {
    // 6/15 turns = 40% = 40 of 100
    setTimeout(() => {
      turnProg.style.strokeDasharray = '40 60';
    }, 1000);
  }

  console.log('%c🔷 SocraticRL UI Loaded', 'color: #A855F7; font-size: 16px; font-weight: bold;');
  console.log('%cAI that teaches through questions, not answers.', 'color: #6b5f8a; font-size: 12px;');
});
