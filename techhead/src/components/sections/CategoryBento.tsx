import Link from "next/link";
import { Smartphone, Watch, Headphones, Home, Tablet, Cable, ArrowUpRight } from "lucide-react";
import { SectionHeading } from "../SectionHeading";
import { Stagger, StaggerItem } from "../Reveal";

const cats = [
  { name: "Smartphones", icon: Smartphone, span: "md:col-span-2 md:row-span-2", blurb: "Flagships, mid-range & certified refurbished", count: "120+ models" },
  { name: "Smartwatches", icon: Watch, span: "", blurb: "Track every beat", count: "Wearables" },
  { name: "Audio", icon: Headphones, span: "", blurb: "ANC earbuds & speakers", count: "Sound" },
  { name: "Smart Home", icon: Home, span: "md:col-span-2", blurb: "Hubs, lights & sensors that just work together", count: "Matter-ready" },
  { name: "Tablets", icon: Tablet, span: "", blurb: "Work & play", count: "Slates" },
  { name: "Accessories", icon: Cable, span: "", blurb: "Chargers & cables", count: "Add-ons" },
];

export function CategoryBento() {
  return (
    <section className="container-px py-20 sm:py-28" id="categories">
      <SectionHeading
        eyebrow="Browse the store"
        title={<>Everything tech, <span className="text-gradient-gold">one place</span></>}
        subtitle="From the phone in your pocket to the hub running your home — carefully sourced for quality and compatibility."
      />

      <Stagger className="mt-12 grid auto-rows-[180px] grid-cols-2 gap-4 md:grid-cols-4" gap={0.06}>
        {cats.map((c) => {
          const Icon = c.icon;
          return (
            <StaggerItem key={c.name} className={c.span}>
              <Link
                href={`/shop?category=${encodeURIComponent(c.name)}`}
                className="card-glass group flex h-full flex-col justify-between p-6"
              >
                <div className="flex items-start justify-between">
                  <span className="flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-white/[0.03] text-accent transition-colors group-hover:border-accent/50 group-hover:bg-accent/10">
                    <Icon size={22} strokeWidth={1.6} />
                  </span>
                  <ArrowUpRight
                    size={20}
                    className="text-secondary transition-all duration-300 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-accent"
                  />
                </div>
                <div>
                  <p className="text-[11px] font-medium uppercase tracking-wider text-accent/80">
                    {c.count}
                  </p>
                  <h3 className="mt-1 text-lg font-semibold">{c.name}</h3>
                  <p className="mt-1 text-sm text-secondary">{c.blurb}</p>
                </div>
              </Link>
            </StaggerItem>
          );
        })}
      </Stagger>
    </section>
  );
}
