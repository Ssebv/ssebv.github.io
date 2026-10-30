/* Replays a terminal figure line by line when it scrolls into view. Without JS, or with
   reduced motion, the whole output is simply visible. */
(function(){
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      var lines = e.target.querySelectorAll('.term-body span');
      lines.forEach(function(l, i){ setTimeout(function(){ l.classList.add('on'); }, 220 * i); });
    });
  }, { threshold: .25 });
  document.querySelectorAll('.term[data-replay]').forEach(function(t){ t.classList.add('play'); io.observe(t); });
})();
