# Ness Cheesecake — E. Ness Official Site

A premium, fully responsive artist website. Stream the music, watch the videos,
and **book E. Ness to perform live**. Built dark-mode-first with a brand
red/white/blue-on-black identity.

## Stack

- **Next.js 14** (App Router) + TypeScript
- **Tailwind CSS** — brand design tokens in `tailwind.config.ts`
- **Framer Motion** — scroll + entrance animations
- Fonts: **Righteous** (display) + **Poppins** (body) via `next/font`

## Getting started

```bash
npm install
npm run dev      # http://localhost:3000
```

## Project structure

```
app/
  layout.tsx        Root layout, fonts, metadata, viewport
  page.tsx          Assembles all sections
  globals.css       Tailwind + design tokens + reduced-motion
components/
  Navbar.tsx        Sticky nav + mobile menu
  Hero.tsx          Full-screen hero (3D placeholder)
  Music.tsx         Song list (audio-reactive viz placeholder)
  Videos.tsx        Video grid
  About.tsx         Bio + stats
  Booking.tsx       Booking form — the conversion goal
  Footer.tsx        Socials + links
lib/
  data.ts           Songs, videos, nav, artist info — single source of truth
```

## Build roadmap

| Phase | Status | What |
|-------|--------|------|
| 1. Skeleton | ✅ Done | Responsive Next.js shell, brand tokens, all sections, booking form UX |
| 2. Content | ⬜ Next | Real photos, logo, songs, videos, bio copy |
| 3. 3D + Motion | ⬜ | React Three Fiber hero, GSAP scroll, Lenis, audio-reactive viz |
| 4. AI assets | ⬜ | Higgsfield Anti-Gravity hero video + 3D object + clips |
| 5. Booking backend | ⬜ | `/api/book` → Google Calendar event + Gmail confirmation |
| 6. Polish & QA | ⬜ | A11y/perf pass, responsive QA at 375/768/1024/1440px |

## Design system

- **Background:** OLED black `#0F0F23`
- **Primary:** brand blue `#1d3a9e` / bright `#2f4fd6`
- **Accent:** brand red `#e23b2e` / bright `#ff4a3a`
- **CTA:** green `#22c55e` — reserved for "Book a Show" only
- Respects `prefers-reduced-motion`. Mobile-first, no horizontal scroll.
