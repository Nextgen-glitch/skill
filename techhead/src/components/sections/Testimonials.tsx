import { Star, Quote } from "lucide-react";
import { SectionHeading } from "../SectionHeading";
import { Stagger, StaggerItem } from "../Reveal";

const reviews = [
  {
    name: "Marcia D.",
    role: "Nassau",
    text: "Cracked my screen on a Friday, walked out fixed within the hour. Honest pricing and the phone looks brand new.",
  },
  {
    name: "Andre P.",
    role: "Paradise Island",
    text: "Bought a refurbished phone here — genuinely couldn't tell it wasn't new. Battery health was 100%. Will be back.",
  },
  {
    name: "Keisha B.",
    role: "Cable Beach",
    text: "They saved my laptop after a virus took over. Backed up my files, cleaned it up and it's faster than ever.",
  },
];

export function Testimonials() {
  return (
    <section className="container-px py-20 sm:py-28">
      <SectionHeading
        eyebrow="Loved locally"
        title={<>What customers <span className="text-gradient-gold">are saying</span></>}
        align="center"
      />
      <Stagger className="mt-14 grid gap-5 md:grid-cols-3">
        {reviews.map((r) => (
          <StaggerItem key={r.name}>
            <figure className="card-glass flex h-full flex-col p-7">
              <Quote size={28} className="text-accent/40" />
              <div className="mt-3 flex gap-0.5">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={15} className="fill-accent text-accent" />
                ))}
              </div>
              <blockquote className="mt-4 flex-1 text-sm leading-relaxed text-foreground/90">
                “{r.text}”
              </blockquote>
              <figcaption className="mt-6 flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-accent-soft to-accent text-sm font-bold text-[#1a1207]">
                  {r.name.charAt(0)}
                </span>
                <div>
                  <p className="text-sm font-semibold">{r.name}</p>
                  <p className="text-xs text-secondary">{r.role}</p>
                </div>
              </figcaption>
            </figure>
          </StaggerItem>
        ))}
      </Stagger>
    </section>
  );
}
