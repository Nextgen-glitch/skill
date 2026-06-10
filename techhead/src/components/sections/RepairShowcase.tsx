"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight, CheckCircle2 } from "lucide-react";
import { REPAIRS } from "@/lib/repairs";
import { ASSETS } from "@/lib/assets";
import { formatPrice } from "@/lib/format";
import { Reveal } from "../Reveal";

const easeOut = [0.16, 1, 0.3, 1] as const;

export function RepairShowcase() {
  const reduce = useReducedMotion();
  return (
    <section className="relative py-20 sm:py-28" id="repairs">
      <div className="container-px grid items-center gap-14 lg:grid-cols-2">
        {/* Visual */}
        <Reveal direction="right">
          <div className="relative">
            <motion.div
              initial={reduce ? false : { opacity: 0, scale: 1.06 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 1, ease: easeOut }}
              className="relative aspect-[4/3] overflow-hidden rounded-3xl border border-white/10 shadow-glass"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={ASSETS.repair}
                alt="A TechHead technician repairing a laptop motherboard"
                className="h-full w-full object-cover"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
            </motion.div>

            {/* floating stat chip */}
            <motion.div
              initial={reduce ? false : { opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.3, ease: easeOut }}
              className="glass-strong absolute -bottom-6 -left-2 rounded-2xl p-4 sm:-left-6"
            >
              <p className="text-2xl font-semibold text-accent-soft">12k+</p>
              <p className="text-xs text-secondary">devices revived</p>
            </motion.div>
            <motion.div
              animate={reduce ? {} : { y: [0, -10, 0] }}
              transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
              className="glass-strong absolute -right-2 top-6 flex items-center gap-2 rounded-full px-4 py-2 sm:-right-5"
            >
              <CheckCircle2 size={15} className="text-accent" />
              <span className="text-xs font-medium">90-day repair warranty</span>
            </motion.div>
          </div>
        </Reveal>

        {/* Copy + services */}
        <div>
          <span className="eyebrow">Repair lab</span>
          <h2 className="mt-4 text-balance text-3xl font-semibold tracking-tight sm:text-4xl lg:text-[2.75rem] lg:leading-[1.1]">
            Broken? Our certified techs{" "}
            <span className="text-gradient-gold">bring it back to life</span>
          </h2>
          <p className="mt-4 max-w-md text-base leading-relaxed text-secondary">
            Screens, batteries, water damage, slow laptops and stubborn viruses — we
            diagnose honestly, quote up front and fix it fast.
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            {REPAIRS.map((r, i) => (
              <Reveal key={r.id} delay={i * 0.06}>
                <div
                  id={r.id}
                  className="card-glass h-full scroll-mt-28 p-5"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-semibold">{r.title}</h3>
                    <span className="text-xs font-medium text-accent">{r.turnaround}</span>
                  </div>
                  <p className="mt-2 text-sm leading-relaxed text-secondary">{r.blurb}</p>
                  <p className="mt-3 text-sm font-semibold text-foreground">
                    from {formatPrice(r.from)}
                  </p>
                </div>
              </Reveal>
            ))}
          </div>

          <Link href="/repairs" className="btn-gold group mt-8">
            Book a repair
            <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
          </Link>
        </div>
      </div>
    </section>
  );
}
