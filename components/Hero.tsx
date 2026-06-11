"use client";

import { motion } from "framer-motion";
import { artist } from "@/lib/data";

const container = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const item = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } },
};

export default function Hero() {
  return (
    <section
      id="home"
      className="relative flex min-h-dvh items-center overflow-hidden pt-16 sm:pt-20"
    >
      {/* Ambient brand glow — placeholder for the Phase 3 WebGL / Phase 4 Higgsfield video */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute left-1/2 top-1/3 h-[40rem] w-[40rem] -translate-x-1/2 rounded-full bg-brand-blue/20 blur-[120px]" />
        <div className="absolute right-[10%] top-[20%] h-[26rem] w-[26rem] rounded-full bg-brand-red/20 blur-[120px]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,rgba(15,15,35,0)_0%,#0F0F23_75%)]" />
      </div>

      {/* Floating placeholder for the 3D medallion (Phase 3) */}
      <div className="pointer-events-none absolute right-[6%] top-1/2 hidden -translate-y-1/2 lg:block">
        <div className="h-64 w-64 animate-floaty rounded-full border border-border/60 bg-gradient-to-br from-brand-blue/30 to-brand-red/30 shadow-glow-blue backdrop-blur-sm" />
      </div>

      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="container-x relative"
      >
        <motion.span variants={item} className="eyebrow">
          {artist.city}
        </motion.span>

        <motion.h1
          variants={item}
          className="heading-xl mt-4 max-w-3xl font-display"
        >
          <span className="glow-text text-brand-white">The Philly Battle</span>
          <br />
          <span className="text-brand-red-bright">Rap</span>{" "}
          <span className="text-brand-blue-bright">Legend</span>
        </motion.h1>

        <motion.p
          variants={item}
          className="mt-6 max-w-xl text-base text-brand-white/70 sm:text-lg"
        >
          E. Ness brings street cadence and raw energy to the stage. Stream the
          music, watch the videos, and book him live for your next party, club
          night, or event.
        </motion.p>

        <motion.div variants={item} className="mt-9 flex flex-wrap items-center gap-4">
          <a
            href="#book"
            className="rounded-full bg-cta px-7 py-3.5 text-base font-semibold text-ink shadow-glow-cta transition-transform duration-200 hover:scale-[1.04]"
          >
            Book a Show
          </a>
          <a
            href="#music"
            className="rounded-full border border-border bg-white/[0.03] px-7 py-3.5 text-base font-semibold text-brand-white backdrop-blur transition-colors duration-200 hover:bg-white/[0.07]"
          >
            Listen Now
          </a>
        </motion.div>

        <motion.p
          variants={item}
          className="mt-10 font-display text-sm uppercase tracking-[0.3em] text-brand-white/40"
        >
          {artist.tagline}
        </motion.p>
      </motion.div>

      {/* Scroll cue */}
      <div className="absolute inset-x-0 bottom-6 flex justify-center">
        <a href="#music" aria-label="Scroll to music" className="group">
          <svg
            className="h-6 w-6 animate-bounce text-brand-white/50 transition-colors group-hover:text-brand-white"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </a>
      </div>
    </section>
  );
}
