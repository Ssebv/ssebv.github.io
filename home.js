/* Home page only: hero figures, technology ribbon, card spotlight, experience timeline
   and the copy button in the contact block. Everything here is an enhancement: without JS
   the page shows the same content, static. */
(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var es = document.documentElement.lang === 'es';
  var hasIO = 'IntersectionObserver' in window;

  /* --- Hero figures. Each digit rises into place, staggered. The real number is the only
     one ever drawn: counting up from zero would show "1 companies supported" for most of a
     second, and these are the strongest claims on the page. Screen readers get the plain
     number from a visually hidden copy. --- */
  var stats = document.querySelector('.stats');
  if (stats && !reduce && hasIO) {
    [].forEach.call(stats.querySelectorAll('.stat-n'), function (n, si) {
      var txt = n.textContent.trim();
      n.textContent = '';
      var sr = document.createElement('span');
      sr.className = 'vh';
      sr.textContent = txt;
      var roll = document.createElement('span');
      roll.className = 'roll';
      roll.setAttribute('aria-hidden', 'true');
      txt.split('').forEach(function (ch, ci) {
        var m = document.createElement('span');
        var c = document.createElement('span');
        m.className = 'roll-m';
        c.className = 'roll-c';
        c.setAttribute('data-ch', ch); /* drawn by CSS, so the DOM text stays the real number once */
        c.style.transitionDelay = (250 + si * 110 + ci * 70) + 'ms';
        m.appendChild(c);
        roll.appendChild(m);
      });
      n.appendChild(sr);
      n.appendChild(roll);
    });
    stats.classList.add('roll-ready');
    var sio = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      stats.classList.add('rolled');
      sio.disconnect();
    }, { threshold: 0.4 });
    sio.observe(stats);
  }

  /* --- Technology ribbon: a second, hidden copy makes the loop seamless. It pauses on
     hover and focus, and has its own pause button (WCAG 2.2.2). --- */
  var ribbon = document.querySelector('.ribbon');
  if (ribbon && !reduce) {
    var list = ribbon.querySelector('.ribbon-list');
    var copy = list.cloneNode(true);
    copy.removeAttribute('aria-label');
    copy.setAttribute('aria-hidden', 'true');
    list.parentNode.appendChild(copy);
    ribbon.classList.add('is-moving');

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'ribbon-toggle';
    btn.setAttribute('aria-pressed', 'false');
    btn.setAttribute('aria-label', es ? 'Pausar la cinta de tecnologías' : 'Pause the technology ribbon');
    btn.innerHTML =
      '<svg class="pause" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>' +
      '<svg class="play" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15a1 1 0 0 0 1.5.86l12-7.5a1 1 0 0 0 0-1.72l-12-7.5A1 1 0 0 0 7 4.5z"/></svg>';
    btn.addEventListener('click', function () {
      var paused = ribbon.classList.toggle('is-paused');
      btn.setAttribute('aria-pressed', paused ? 'true' : 'false');
    });
    ribbon.appendChild(btn);
  }

  /* --- Cursor spotlight on cards: only where there is a real hover. --- */
  if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
    var cards = document.querySelectorAll('.feature, .proj:not(.proj-static), .path, .cta');
    [].forEach.call(cards, function (c) { c.classList.add('spot'); });
    var last = null, pending = false;
    var paint = function () {
      pending = false;
      var c = last.target.closest && last.target.closest('.spot');
      if (!c) return;
      var r = c.getBoundingClientRect();
      c.style.setProperty('--mx', (last.clientX - r.left) + 'px');
      c.style.setProperty('--my', (last.clientY - r.top) + 'px');
    };
    document.addEventListener('pointermove', function (e) {
      last = e;
      if (!pending) { pending = true; requestAnimationFrame(paint); }
    }, { passive: true });
  }

  /* --- Experience timeline: the rail fills with scroll and lights each role it reaches.
     With reduced motion the rail stays plain; the current role is marked either way. --- */
  var tl = document.querySelector('.timeline');
  if (tl && !reduce) {
    var jobs = [].slice.call(tl.querySelectorAll('.job'));
    var queued = false;
    /* Reads first, writes after: one layout per frame. The rail is drawn from 10px to
       height - 10px, so the fill is measured over that span and ends exactly at the probe
       line that lights each node (node centre = job top + 14px). */
    var update = function () {
      queued = false;
      var r = tl.getBoundingClientRect();
      var tops = jobs.map(function (j) { return j.getBoundingClientRect().top; });
      var probe = window.innerHeight * 0.62;
      var p = Math.max(0, Math.min(1, (probe - r.top - 10) / (r.height - 20)));
      tl.style.setProperty('--tl', p.toFixed(4));
      jobs.forEach(function (j, i) { j.classList.toggle('lit', tops[i] + 14 <= probe); });
    };
    var queue = function () { if (!queued) { queued = true; requestAnimationFrame(update); } };
    var listening = false;
    var listen = function (on) {
      if (on === listening) return;
      listening = on;
      var m = on ? 'addEventListener' : 'removeEventListener';
      window[m]('scroll', queue, { passive: true });
      window[m]('resize', queue);
    };
    if (hasIO) {
      new IntersectionObserver(function (entries) {
        listen(entries[0].isIntersecting);
        queue();
      }, { rootMargin: '25% 0px 25% 0px' }).observe(tl);
    } else {
      listen(true);
    }
    update();
  }

  /* --- Copy the address. Shown only where the Clipboard API exists (HTTPS or localhost). --- */
  var cp = document.querySelector('.copy[data-copy]');
  if (cp && navigator.clipboard && window.isSecureContext) {
    var msg = cp.parentNode.querySelector('.copy-msg');
    var timer;
    cp.hidden = false;
    cp.addEventListener('click', function () {
      var say = function (text) {
        msg.textContent = text;
        clearTimeout(timer);
        timer = setTimeout(function () { msg.textContent = ''; }, 2500);
      };
      navigator.clipboard.writeText(cp.getAttribute('data-copy')).then(function () {
        say(es ? 'Correo copiado' : 'Address copied');
      }, function () {
        say(es ? 'No se pudo copiar' : 'Could not copy');
      });
    });
  }
})();
