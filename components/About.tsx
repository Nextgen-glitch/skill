"use client";

import { motion } from "framer-motion";
import SectionHeading from "./SectionHeading";

const stats = [
  { value: "20+", label: "Years On The Mic" },
  { value: "100+", label: "Live Shows" },
  { value: "1", label: "City Of Brotherly Love" },
];

export default function About() {
  return (
    <section id="about" className="section-pad">
      <div className="container-x grid items-center gap-12 lg:grid-cols-2">
        {/* Portrait placeholder — your provided artist photo drops in here (Phase 2) */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className="relative aspect-[4/5] overflow-hidden rounded-3xl border border-border/70"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-brand-blue/40 via-ink to-brand-red/30" />
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="font-display text-2xl text-brand-white/40">Artist Photo</span>
          </div>
        </motion.div>

        <div>
          <SectionHeading
            eyebrow="The Story"
            title={
              <>
                Made With <span className="text-brand-red-bright">Brotherly Love</span>
              </>
            }
          />
          <div className="mt-6 space-y-4 text-base text-brand-white/70 sm:text-lg">
            <p>
              E. Ness is a Philadelphia battle rap legend who helped bring raw
              street cadence to the mainstream. From the corners of Philly to
              stages across the country, his energy is unmatched.
            </p>
            <p>
              Now performing live for parties, clubs, and events — bringing that
              same authentic fire everywhere he goes.
            </p>
          </div>

          <dl className="mt-10 grid grid-cols-3 gap-4">
            {stats.map((s) => (
              <div key={s.label} className="rounded-xl border border-border/70 bg-ink-card/50 p-4 text-center">
                <dt className="font-display text-2xl text-brand-blue-bright sm:text-3xl">
                  {s.value}
                </dt>
                <dd className="mt-1 text-xs text-brand-white/55">{s.label}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
}
