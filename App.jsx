import React, { useEffect, useRef, useState, useCallback } from "react";

/* ============================================================================
   EcommMax — animated electronics marketplace homepage (single-file React)
   Motion: antigravity hero float + pointer parallax, scroll-reveal stagger,
   premium hover/press feedback. All motion respects prefers-reduced-motion.
   Pure React + Tailwind. No extra deps. Drop in as App.jsx.
   ========================================================================== */

/* ---------- inline SVG icons (no dependency) ---------- */
const Icon = {
  Search: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>),
  Cart: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>),
  Heart: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.29 1.51 4.04 3 5.5l7 7Z"/></svg>),
  Bolt: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg>),
  Truck: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.62l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>),
  Shield: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>),
  Phone: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/></svg>),
  Watch: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="12" cy="12" r="6"/><path d="M12 10v2l1 1"/><path d="m16.13 7.66-.81-4.05a2 2 0 0 0-2-1.61h-2.68a2 2 0 0 0-2 1.61l-.78 4.05M7.88 16.36l.8 4a2 2 0 0 0 2 1.61h2.72a2 2 0 0 0 2-1.61l.81-4.05"/></svg>),
  Gamepad: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><line x1="15" y1="13" x2="15.01" y2="13"/><line x1="18" y1="11" x2="18.01" y2="11"/><rect x="2" y="6" width="20" height="12" rx="2"/></svg>),
  Home: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>),
  Headphones: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-5a9 9 0 0 1 18 0v5a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/></svg>),
  Camera: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>),
  Star: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" stroke="none" {...p}><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>),
};

/* ---------- reduced-motion hook ---------- */
function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduced(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);
  return reduced;
}

/* ---------- scroll-reveal hook (IntersectionObserver) ---------- */
function useReveal() {
  const ref = useRef(null);
  const [shown, setShown] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && setShown(true)),
      { threshold: 0.15 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return [ref, shown];
}

/* Reveal wrapper: fade + translateY, with optional stagger via index */
function Reveal({ children, i = 0, as: Tag = "div", className = "" }) {
  const [ref, shown] = useReveal();
  return (
    <Tag
      ref={ref}
      className={className}
      style={{
        opacity: shown ? 1 : 0,
        transform: shown ? "translateY(0)" : "translateY(40px)",
        transition: "opacity .5s ease-out, transform .5s ease-out",
        transitionDelay: `${i * 40}ms`,
      }}
    >
      {children}
    </Tag>
  );
}

/* ---------- count-up on reveal ---------- */
function CountUp({ end, prefix = "", suffix = "" }) {
  const [ref, shown] = useReveal();
  const [val, setVal] = useState(0);
  const reduced = useReducedMotion();
  useEffect(() => {
    if (!shown) return;
    if (reduced) { setVal(end); return; }
    let raf, start;
    const dur = 1200;
    const tick = (t) => {
      if (!start) start = t;
      const p = Math.min((t - start) / dur, 1);
      setVal(Math.round((1 - Math.pow(1 - p, 3)) * end)); // ease-out cubic
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [shown, end, reduced]);
  return <span ref={ref}>{prefix}{val.toLocaleString()}{suffix}</span>;
}

/* ============================ DATA ============================ */
const CATEGORIES = [
  { name: "Smartphones", icon: Icon.Phone, sub: "Apple · Samsung · Poco" },
  { name: "Audio", icon: Icon.Headphones, sub: "Earbuds · Speakers" },
  { name: "Smartwatch", icon: Icon.Watch, sub: "Fitness · Premium" },
  { name: "Gaming", icon: Icon.Gamepad, sub: "Consoles · Controllers" },
  { name: "Smart Home", icon: Icon.Home, sub: "Cameras · Sensors" },
  { name: "Cameras", icon: Icon.Camera, sub: "DSLR · Action" },
];

const DEALS = [
  { name: "Vivax Ultra OLED Android Phone", price: 180, was: 260, rating: 4.5, sold: 64, tag: "Smartphones" },
  { name: "Smart Watch with Ultra Display", price: 156, was: 210, rating: 4.7, sold: 41, tag: "Wearables" },
  { name: "Premium Apple GT Cyber Watch", price: 150, was: 199, rating: 4.8, sold: 88, tag: "Wearables" },
  { name: "Aurora Pro Wireless Earbuds", price: 79, was: 129, rating: 4.6, sold: 120, tag: "Audio" },
];

const BRANDS = ["Apple", "Samsung", "Sony", "Poco", "Anker", "JBL", "Bose", "Xiaomi"];

/* ============================ CARDS ============================ */
function ProductCard({ p, i }) {
  const [added, setAdded] = useState(false);
  const off = Math.round((1 - p.price / p.was) * 100);
  return (
    <Reveal i={i} className="group relative">
      <div className="card-lift flex h-full flex-col rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 shadow-sm">
        {/* image frame */}
        <div className="relative mb-4 overflow-hidden rounded-xl bg-[var(--muted-bg)]">
          <span className="absolute left-3 top-3 z-10 rounded-full bg-[var(--accent)] px-2.5 py-1 text-xs font-semibold text-white">-{off}%</span>
          <button aria-label="Add to wishlist" className="absolute right-3 top-3 z-10 grid h-9 w-9 place-items-center rounded-full bg-white/90 text-[var(--muted)] shadow-sm transition hover:text-[var(--accent)] active:scale-90">
            <Icon.Heart className="h-4 w-4" />
          </button>
          <div className="img-zoom grid aspect-square place-items-center text-[var(--muted)]">
            <Icon.Phone className="h-20 w-20 opacity-30" />
          </div>
        </div>
        <span className="text-xs font-medium text-[var(--accent)]">{p.tag}</span>
        <h3 className="mt-1 line-clamp-2 min-h-[2.5rem] font-semibold leading-snug text-[var(--fg)]">{p.name}</h3>
        <div className="mt-2 flex items-center gap-1 text-amber-400">
          {[...Array(5)].map((_, s) => <Icon.Star key={s} className={`h-3.5 w-3.5 ${s < Math.round(p.rating) ? "" : "opacity-25"}`} />)}
          <span className="ml-1 text-xs text-[var(--muted)]">({p.rating})</span>
        </div>
        {/* stock bar */}
        <div className="mt-3">
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-[var(--muted-bg)]">
            <div className="h-full rounded-full bg-[var(--primary)]" style={{ width: `${Math.min(p.sold, 100)}%` }} />
          </div>
          <p className="mt-1 text-xs text-[var(--muted)]">Sold: <CountUp end={p.sold} /> units</p>
        </div>
        <div className="mt-4 flex items-end justify-between">
          <div>
            <span className="text-lg font-bold text-[var(--fg)]">${p.price}</span>
            <span className="ml-2 text-sm text-[var(--muted)] line-through">${p.was}</span>
          </div>
        </div>
        <button
          onClick={() => { setAdded(true); setTimeout(() => setAdded(false), 1400); }}
          className="btn-sweep mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-white"
        >
          <Icon.Cart className="icon-nudge h-4 w-4" />
          {added ? "Added ✓" : "Add to Cart"}
        </button>
      </div>
    </Reveal>
  );
}

function CategoryTile({ c, i }) {
  const I = c.icon;
  return (
    <Reveal i={i}>
      <button className="cat-tile flex w-full flex-col items-center gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 text-center">
        <span className="cat-ico grid h-14 w-14 place-items-center rounded-2xl bg-[var(--primary-50)] text-[var(--primary)]">
          <I className="h-7 w-7" />
        </span>
        <span className="font-semibold text-[var(--fg)]">{c.name}</span>
        <span className="text-xs text-[var(--muted)]">{c.sub}</span>
      </button>
    </Reveal>
  );
}

/* ============================ HERO ============================ */
function Hero() {
  const reduced = useReducedMotion();
  const [parallax, setParallax] = useState({ x: 0, y: 0 });
  const onMove = useCallback((e) => {
    if (reduced) return;
    const r = e.currentTarget.getBoundingClientRect();
    const nx = (e.clientX - r.left) / r.width - 0.5;
    const ny = (e.clientY - r.top) / r.height - 0.5;
    setParallax((s) => ({ x: s.x + (nx - s.x) * 0.15, y: s.y + (ny - s.y) * 0.15 })); // damped lerp
  }, [reduced]);

  return (
    <section
      onMouseMove={onMove}
      onMouseLeave={() => setParallax({ x: 0, y: 0 })}
      className="relative overflow-hidden bg-gradient-to-br from-[var(--primary-50)] via-[var(--surface)] to-[var(--primary-50)]"
    >
      {/* floating background blobs */}
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <div className="blob float-slow absolute -left-20 top-10 h-64 w-64 rounded-full bg-[var(--primary)]/20"
             style={{ transform: `translate(${parallax.x * -30}px, ${parallax.y * -30}px)` }} />
        <div className="blob float-slow absolute -right-10 bottom-0 h-72 w-72 rounded-full bg-[var(--accent)]/15"
             style={{ transform: `translate(${parallax.x * 40}px, ${parallax.y * 40}px)`, animationDelay: "1.5s" }} />
      </div>

      <div className="relative mx-auto grid max-w-7xl items-center gap-10 px-6 py-16 md:grid-cols-2 md:py-24">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full bg-[var(--primary)] px-3 py-1 text-xs font-semibold text-white">
            <Icon.Bolt className="h-3.5 w-3.5" /> 20MP Triple Camera
          </span>
          <h1 className="hero-rise mt-5 text-4xl font-extrabold leading-tight tracking-tight text-[var(--fg)] md:text-6xl">
            EcommMax<br />Ultra Phone
          </h1>
          <p className="mt-4 max-w-md text-[var(--muted)]">
            The flagship that floats above the rest. Edge OLED, all-day battery, and pro-grade optics — now at a launch price.
          </p>
          {/* search = primary CTA (marketplace pattern) */}
          <div className="mt-7 flex max-w-md items-center gap-2 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-2 shadow-sm focus-within:ring-2 focus-within:ring-[var(--primary)]">
            <Icon.Search className="ml-2 h-5 w-5 text-[var(--muted)]" />
            <input className="flex-1 bg-transparent px-1 py-2 text-sm outline-none" placeholder="Search 50,000+ products…" aria-label="Search products" />
            <button className="btn-sweep rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-semibold text-white">Search</button>
          </div>
          <div className="mt-6 flex gap-8 text-sm">
            <div><div className="text-2xl font-bold text-[var(--fg)]"><CountUp end={50} suffix="k+" /></div><div className="text-[var(--muted)]">Products</div></div>
            <div><div className="text-2xl font-bold text-[var(--fg)]"><CountUp end={98} suffix="%" /></div><div className="text-[var(--muted)]">Happy buyers</div></div>
            <div><div className="text-2xl font-bold text-[var(--fg)]"><CountUp end={24} suffix="h" /></div><div className="text-[var(--muted)]">Fast delivery</div></div>
          </div>
        </div>

        {/* antigravity floating product */}
        <div className="relative grid place-items-center">
          <div
            className="phone-float"
            style={{ transform: `translate(${parallax.x * 25}px, ${parallax.y * 25}px)` }}
          >
            <div className="relative grid h-72 w-44 place-items-center rounded-[2.2rem] border-4 border-[var(--fg)]/80 bg-gradient-to-b from-slate-800 to-slate-950 shadow-2xl md:h-96 md:w-60">
              <Icon.Phone className="h-24 w-24 text-white/20" />
              <span className="absolute inset-x-6 top-6 rounded-full bg-white/10 py-6" />
            </div>
            {/* weightless shadow */}
            <div aria-hidden className="shadow-pulse mx-auto mt-4 h-4 w-40 rounded-full bg-black/30 blur-xl md:w-52" />
          </div>
        </div>
      </div>
    </section>
  );
}

/* ============================ APP ============================ */
export default function App() {
  return (
    <div className="min-h-screen bg-[var(--bg)] font-body text-[var(--fg)]">
      <StyleTag />

      {/* utility bar */}
      <div className="bg-[var(--primary-dark)] text-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-2 text-xs">
          <span className="flex items-center gap-2"><Icon.Truck className="h-4 w-4" /> Free shipping on orders over $50</span>
          <span className="hidden sm:block">Help · Track Order · Store Locator</span>
        </div>
      </div>

      {/* navbar */}
      <header className="sticky top-0 z-40 border-b border-[var(--border)] bg-[var(--primary)] text-white backdrop-blur">
        <nav className="mx-auto flex max-w-7xl items-center gap-6 px-6 py-3">
          <a href="#" className="text-xl font-extrabold font-head">Ecomm<span className="text-[var(--primary-50)]">Max</span></a>
          <div className="hidden flex-1 items-center gap-2 rounded-xl bg-white/15 px-3 py-2 md:flex">
            <Icon.Search className="h-4 w-4 text-white/80" />
            <input className="flex-1 bg-transparent text-sm text-white placeholder-white/70 outline-none" placeholder="Search for products, brands and more" aria-label="Search" />
          </div>
          <div className="ml-auto flex items-center gap-4">
            <button className="relative grid h-10 w-10 place-items-center rounded-full transition hover:bg-white/15 active:scale-90" aria-label="Wishlist"><Icon.Heart className="h-5 w-5" /></button>
            <button className="relative grid h-10 w-10 place-items-center rounded-full transition hover:bg-white/15 active:scale-90" aria-label="Cart">
              <Icon.Cart className="h-5 w-5" />
              <span className="absolute -right-0.5 -top-0.5 grid h-5 w-5 place-items-center rounded-full bg-[var(--accent)] text-[10px] font-bold">3</span>
            </button>
            <button className="rounded-xl bg-white px-4 py-2 text-sm font-semibold text-[var(--primary)] transition hover:bg-[var(--primary-50)] active:scale-95">Sign in</button>
          </div>
        </nav>
      </header>

      <main>
        <Hero />

        {/* categories */}
        <section className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          <Reveal><SectionHead kicker="Browse" title="Shop by Category" /></Reveal>
          <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            {CATEGORIES.map((c, i) => <CategoryTile key={c.name} c={c} i={i} />)}
          </div>
        </section>

        {/* deals */}
        <section className="bg-[var(--surface)] py-16 md:py-20">
          <div className="mx-auto max-w-7xl px-6">
            <Reveal>
              <div className="flex items-end justify-between">
                <SectionHead kicker="Limited time" title="Deals of the Day" />
                <span className="hidden rounded-full bg-[var(--accent)]/10 px-4 py-2 text-sm font-semibold text-[var(--accent)] sm:block">Ends in 08:42:15</span>
              </div>
            </Reveal>
            <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {DEALS.map((p, i) => <ProductCard key={p.name} p={p} i={i} />)}
            </div>
          </div>
        </section>

        {/* brand marquee */}
        <section className="overflow-hidden border-y border-[var(--border)] bg-[var(--bg)] py-8">
          <div className="marquee flex w-max gap-16 px-6">
            {[...BRANDS, ...BRANDS].map((b, i) => (
              <span key={i} className="text-2xl font-bold text-[var(--muted)] opacity-60">{b}</span>
            ))}
          </div>
        </section>

        {/* best sellers */}
        <section className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          <Reveal><SectionHead kicker="This week" title="Top 20 Best Sellers" /></Reveal>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[...DEALS].reverse().map((p, i) => <ProductCard key={"bs" + p.name} p={p} i={i} />)}
          </div>
        </section>

        {/* trust + newsletter CTA */}
        <section className="bg-[var(--primary)] py-16 text-white md:py-20">
          <div className="mx-auto max-w-7xl px-6">
            <div className="grid gap-8 md:grid-cols-3">
              {[
                { I: Icon.Truck, t: "Fast & Free Delivery", d: "Free 24h shipping on orders over $50." },
                { I: Icon.Shield, t: "2-Year Warranty", d: "Every device covered, hassle-free returns." },
                { I: Icon.Bolt, t: "Best Price Promise", d: "Found it cheaper? We'll match it instantly." },
              ].map((f, i) => (
                <Reveal i={i} key={f.t}>
                  <div className="flex items-start gap-4 rounded-2xl bg-white/10 p-6">
                    <f.I className="h-8 w-8 shrink-0" />
                    <div><h3 className="font-semibold">{f.t}</h3><p className="mt-1 text-sm text-white/80">{f.d}</p></div>
                  </div>
                </Reveal>
              ))}
            </div>
            <Reveal>
              <div className="mt-12 text-center">
                <h2 className="text-3xl font-extrabold font-head md:text-4xl">Get exclusive drops & deals</h2>
                <p className="mt-2 text-white/80">Join 50,000+ shoppers. No spam, unsubscribe anytime.</p>
                <form className="mx-auto mt-6 flex max-w-md gap-2 rounded-2xl bg-white p-2" onSubmit={(e) => e.preventDefault()}>
                  <input type="email" required className="flex-1 rounded-xl bg-transparent px-3 py-2 text-sm text-[var(--fg)] outline-none" placeholder="you@email.com" aria-label="Email address" />
                  <button className="btn-sweep rounded-xl bg-[var(--accent)] px-5 py-2.5 text-sm font-semibold">Subscribe</button>
                </form>
              </div>
            </Reveal>
          </div>
        </section>
      </main>

      <footer className="bg-[var(--primary-dark)] py-8 text-center text-sm text-white/70">
        © 2026 EcommMax — Built with motion & care.
      </footer>
    </div>
  );
}

function SectionHead({ kicker, title }) {
  return (
    <div>
      <span className="text-sm font-semibold uppercase tracking-wider text-[var(--primary)]">{kicker}</span>
      <h2 className="mt-1 text-3xl font-extrabold tracking-tight font-head md:text-4xl">{title}</h2>
    </div>
  );
}

/* ---------- design tokens, keyframes & motion (scoped, no external CSS) ---------- */
function StyleTag() {
  return (
    <style>{`
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap');
      :root{
        --primary:#16A34A; --primary-dark:#15803D; --primary-50:#DCFCE7;
        --accent:#2563EB; --bg:#F8FAFC; --surface:#FFFFFF; --muted-bg:#F1F5F9;
        --fg:#0F172A; --muted:#64748B; --border:#E2E8F0;
      }
      .font-head{font-family:'Space Grotesk',sans-serif}
      .font-body{font-family:'DM Sans',sans-serif}
      body{font-family:'DM Sans',sans-serif}

      /* antigravity float */
      @keyframes phoneFloat{0%,100%{transform:translateY(0) rotate(-1.5deg)}50%{transform:translateY(-14px) rotate(1.5deg)}}
      @keyframes shadowPulse{0%,100%{opacity:.35;transform:scale(1)}50%{opacity:.2;transform:scale(.85)}}
      @keyframes floatSlow{0%,100%{transform:translateY(0)}50%{transform:translateY(-22px)}}
      .phone-float{animation:phoneFloat 4s ease-in-out infinite}
      .shadow-pulse{animation:shadowPulse 4s ease-in-out infinite}
      .float-slow{animation:floatSlow 7s ease-in-out infinite}
      .blob{filter:blur(8px)}

      /* hover lift + image zoom */
      .card-lift{transition:transform .2s ease-out, box-shadow .2s ease-out}
      @media(hover:hover){.card-lift:hover{transform:translateY(-8px) scale(1.02);box-shadow:0 20px 40px -12px rgba(2,6,23,.18)}}
      .card-lift:active{transform:translateY(-2px) scale(.99)}
      .img-zoom{transition:transform .4s ease-out}
      @media(hover:hover){.group:hover .img-zoom{transform:scale(1.06)}}

      /* category tile */
      .cat-tile{transition:transform .2s ease-out, border-color .2s, box-shadow .2s; cursor:pointer}
      @media(hover:hover){.cat-tile:hover{transform:translateY(-6px);border-color:var(--primary);box-shadow:0 14px 30px -14px rgba(22,163,74,.4)}}
      .cat-tile:active{transform:scale(.97)}
      .cat-ico{transition:transform .25s ease-out, background-color .25s}
      @media(hover:hover){.cat-tile:hover .cat-ico{transform:scale(1.12) rotate(-6deg);background:var(--primary);color:#fff}}

      /* button sweep + icon nudge */
      .btn-sweep{position:relative;overflow:hidden;cursor:pointer;transition:transform .15s ease-out}
      .btn-sweep::after{content:"";position:absolute;inset:0;background:rgba(255,255,255,.22);transform:translateX(-100%);transition:transform .35s ease-out}
      @media(hover:hover){.btn-sweep:hover::after{transform:translateX(0)}}
      .btn-sweep:active{transform:scale(.96)}
      .icon-nudge{transition:transform .2s ease-out}
      @media(hover:hover){.btn-sweep:hover .icon-nudge{transform:translateX(3px)}}

      /* marquee */
      @keyframes marquee{from{transform:translateX(0)}to{transform:translateX(-50%)}}
      .marquee{animation:marquee 22s linear infinite}
      @media(hover:hover){.marquee:hover{animation-play-state:paused}}

      /* RESPECT reduced motion — kill all motion, snap to final */
      @media(prefers-reduced-motion:reduce){
        .phone-float,.shadow-pulse,.float-slow,.marquee{animation:none!important}
        .card-lift,.cat-tile,.btn-sweep,.img-zoom,.cat-ico,.icon-nudge{transition:none!important}
        *{scroll-behavior:auto!important}
      }
      html{scroll-behavior:smooth}
    `}</style>
  );
}
