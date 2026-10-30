// 540X Partners — header, menu, hero slideshow, scroll reveal, photo lightbox
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // header gets a line once you scroll
  const top = $(".top");
  const onScroll = () => top.classList.toggle("scrolled", scrollY > 40);
  addEventListener("scroll", onScroll, { passive: true }); onScroll();

  // phone menu
  const menu = $(".menu"), nav = $("#nav");
  menu.addEventListener("click", () => {
    const open = !nav.classList.contains("open");
    nav.classList.toggle("open", open); document.body.classList.toggle("menu-open", open);
    menu.setAttribute("aria-expanded", open);
  });

  // hero slideshow
  const slides = $$(".slide");
  if (slides.length > 1) {
    let i = 0;
    const count = $(".hero-ui .count b");
    setInterval(() => {
      slides[i].classList.remove("on");
      i = (i + 1) % slides.length;
      slides[i].classList.add("on");
      if (count) count.textContent = String(i + 1).padStart(2, "0");
    }, 5500);
  }

  // sections fade up as they come into view
  const io = "IntersectionObserver" in window ? new IntersectionObserver(es => es.forEach(en => {
    if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
  }), { rootMargin: "0px 0px -8% 0px" }) : null;
  $$(".reveal").forEach(el => io ? io.observe(el) : el.classList.add("in"));

  // full-screen photo viewer on project pages
  const lb = $(".lightbox");
  if (lb) {
    const pics = $$("img.zoom"), big = $("img", lb);
    let k = 0;
    const show = n => { k = (n + pics.length) % pics.length; big.src = pics[k].currentSrc || pics[k].src; lb.hidden = false; document.body.style.overflow = "hidden"; };
    const hide = () => { lb.hidden = true; document.body.style.overflow = ""; };
    pics.forEach((p, n) => p.addEventListener("click", () => show(n)));
    $(".lb-x", lb).onclick = hide; $(".lb-p", lb).onclick = () => show(k - 1); $(".lb-n", lb).onclick = () => show(k + 1);
    lb.addEventListener("click", ev => { if (ev.target === lb) hide(); });
    addEventListener("keydown", ev => {
      if (lb.hidden) return;
      if (ev.key === "Escape") hide(); if (ev.key === "ArrowLeft") show(k - 1); if (ev.key === "ArrowRight") show(k + 1);
    });
    let x0 = null;
    lb.addEventListener("touchstart", ev => { x0 = ev.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", ev => { if (x0 === null) return; const dx = ev.changedTouches[0].clientX - x0; if (Math.abs(dx) > 50) show(k + (dx < 0 ? 1 : -1)); x0 = null; });
  }
})();
