# TechHead Electronics

Premium e-commerce + repair-booking site for **TechHead Electronics** (Nassau) — gadget
sales (smartphones, tablets, smartwatches, audio, smart home, accessories) and certified
phone & computer repairs.

Built to be genuinely top-notch: a cinematic **Liquid Glass** dark + gold aesthetic, an
interactive 3D hero computer that deconstructs and reassembles on a loop, and motion on
nearly every element.

## Stack

- **Next.js 14** (App Router) + **TypeScript**
- **Tailwind CSS** — design tokens from the UI/UX Pro Max design system
- **Framer Motion** — scroll reveals, staggered grids, animated headline, count-ups
- **react-three-fiber + drei** — the exploding/reconstructing computer hero
- **JSON-file store + API routes** — powers the (upcoming) admin product upload panel

## Design system

| Token | Value |
|-------|-------|
| Style | Liquid Glass (premium glassmorphism) |
| Background | `#0c0a09` |
| Accent (gold) | `#d4922a` / soft `#f0b357` |
| Typography | Inter (300–700) |

See `tailwind.config.ts` and `src/app/globals.css`.

## Develop

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm start        # serve the production build
```

## Project structure

```
src/
  app/
    page.tsx              # Homepage (Hero + sections)
    layout.tsx            # Root layout, Inter font, navbar/footer
    api/products/         # GET/POST + [id] PUT/DELETE  (admin backend)
    shop|repairs|about|contact|admin/   # routes (built out next)
  components/
    Hero.tsx              # Animated hero + 3D computer
    three/ExplodingComputer.tsx   # react-three-fiber scene
    sections/             # CategoryBento, FeaturedProducts, RepairShowcase, Stats, WhyUs, Testimonials, CtaBanner
    Navbar, Footer, ProductCard, Reveal, ...
  lib/
    types.ts, store.ts, repairs.ts, format.ts, assets.ts
  data/products.json      # seed catalog / persisted store
```

## Notes

- **Hero brand visuals** were generated with AI in the brand's dark + gold language and are
  served from CDN. Product cards fall back to elegant category placeholders if an image is
  unavailable, so the UI never looks broken.
- The product store writes to `src/data/products.json`. For production, swap
  `src/lib/store.ts` for a real database (Postgres/SQLite).

## Roadmap

- [x] Homepage (hero, categories, featured, repairs, why-us, testimonials, CTA)
- [ ] Full shop with filters, search & product detail pages
- [ ] Online repair booking flow
- [ ] About & contact pages
- [ ] Admin panel — upload & manage products (API already in place)
