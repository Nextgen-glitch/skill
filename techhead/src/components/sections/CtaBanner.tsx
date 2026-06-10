import Link from "next/link";
import { ArrowRight, Wrench } from "lucide-react";
import { Reveal } from "../Reveal";

export function CtaBanner() {
  return (
    <section className="container-px py-20 sm:py-28">
      <Reveal>
        <div className="relative overflow-hidden rounded-[2rem] border border-white/10 px-7 py-16 text-center sm:px-12 sm:py-20">
          {/* glow backdrop */}
          <div className="absolute inset-0 -z-10 bg-[radial-gradient(70%_120%_at_50%_0%,rgba(212,146,42,0.22),transparent_60%)]" />
          <div className="absolute inset-0 -z-10 bg-gradient-to-b from-[#1a1612]/80 to-[#0c0a09]/80" />
          <div className="absolute -left-20 -top-20 -z-10 h-72 w-72 rounded-full bg-accent/15 blur-[100px]" />

          <span className="eyebrow">Ready when you are</span>
          <h2 className="mx-auto mt-5 max-w-2xl text-balance text-3xl font-semibold tracking-tight sm:text-4xl lg:text-5xl">
            Upgrade your tech or revive what you{" "}
            <span className="text-gradient-gold">already love</span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-base leading-relaxed text-secondary">
            Shop the latest gadgets or book a repair in minutes. Real people, real
            warranties, right here in Nassau.
          </p>
          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <Link href="/shop" className="btn-gold group">
              Start shopping
              <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
            </Link>
            <Link href="/repairs" className="btn-ghost">
              <Wrench size={16} className="text-accent" />
              Book a repair
            </Link>
          </div>
        </div>
      </Reveal>
    </section>
  );
}
