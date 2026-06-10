"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight, Wrench, ShieldCheck, Truck } from "lucide-react";

const ExplodingComputer = dynamic(
  () => import("./three/ExplodingComputer"),
  {
    ssr: false,
    loading: () => (
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="h-40 w-40 animate-spin-slow rounded-full border-2 border-accent/20 border-t-accent/70" />
      </div>
    ),
  },
);

const easeOut = [0.16, 1, 0.3, 1] as const;

const headline = ["Gadgets", "that", "wow.", "Repairs", "you", "trust."];

export function Hero() {
  const reduce = useReducedMotion();

  return (
    <section className="relative min-h-[100svh] overflow-hidden pt-28">
      {/* 3D canvas layer */}
      <div className="pointer-events-none absolute inset-0 lg:left-[42%]">
        <div className="absolute inset-0 [mask-image:radial-gradient(70%_70%_at_50%_45%,black,transparent)]">
          <ExplodingComputer />
        </div>
      </div>

      {/* soft gold orb behind text */}
      <div className="absolute -left-40 top-40 h-[34rem] w-[34rem] rounded-full bg-accent/10 blur-[120px]" />

      <div className="container-px relative grid min-h-[calc(100svh-7rem)] items-center">
        <div className="max-w-2xl py-16">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: easeOut }}
          >
            <span className="eyebrow">
              <span className="h-1.5 w-1.5 rounded-full bg-accent" />
              Nassau&apos;s gadget &amp; repair HQ
            </span>
          </motion.div>

          <h1 className="mt-6 text-balance text-5xl font-semibold leading-[1.04] tracking-tight sm:text-6xl lg:text-7xl">
            {headline.map((word, i) => (
              <motion.span
                key={i}
                className="mr-[0.25em] inline-block"
                initial={reduce ? false : { opacity: 0, y: 28, rotateX: -40 }}
                animate={{ opacity: 1, y: 0, rotateX: 0 }}
                transition={{ duration: 0.7, ease: easeOut, delay: 0.15 + i * 0.09 }}
              >
                {word === "wow." || word === "trust." ? (
                  <span className="text-gradient-gold">{word}</span>
                ) : (
                  word
                )}
              </motion.span>
            ))}
          </h1>

          <motion.p
            className="mt-6 max-w-lg text-lg leading-relaxed text-secondary"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: easeOut, delay: 0.7 }}
          >
            Shop premium smartphones, smartwatches, audio and smart-home tech — then
            keep them running with certified phone &amp; computer repairs. Quality
            sourced, expertly serviced.
          </motion.p>

          <motion.div
            className="mt-9 flex flex-wrap items-center gap-3"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: easeOut, delay: 0.85 }}
          >
            <Link href="/shop" className="btn-gold group">
              Shop gadgets
              <ArrowRight
                size={17}
                className="transition-transform duration-300 group-hover:translate-x-1"
              />
            </Link>
            <Link href="/repairs" className="btn-ghost group">
              <Wrench size={16} className="text-accent" />
              Book a repair
            </Link>
          </motion.div>

          <motion.div
            className="mt-12 flex flex-wrap gap-x-8 gap-y-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1 }}
          >
            {[
              { icon: ShieldCheck, label: "12-month warranty" },
              { icon: Truck, label: "Island-wide delivery" },
              { icon: Wrench, label: "Certified technicians" },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-2.5 text-sm text-secondary">
                <Icon size={16} className="text-accent" />
                {label}
              </div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* scroll cue */}
      <motion.div
        className="absolute bottom-6 left-1/2 hidden -translate-x-1/2 lg:block"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.4 }}
      >
        <div className="flex h-10 w-6 items-start justify-center rounded-full border border-border p-1.5">
          <motion.div
            className="h-2 w-1 rounded-full bg-accent"
            animate={reduce ? {} : { y: [0, 10, 0] }}
            transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>
      </motion.div>
    </section>
  );
}
