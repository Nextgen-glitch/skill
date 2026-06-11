"use client";

import { motion } from "framer-motion";
import { videos } from "@/lib/data";
import SectionHeading from "./SectionHeading";

export default function Videos() {
  return (
    <section id="videos" className="section-pad bg-ink-soft/40">
      <div className="container-x">
        <SectionHeading
          eyebrow="Watch"
          title={
            <>
              Videos & <span className="text-brand-blue-bright">Live Sets</span>
            </>
          }
          subtitle="Music videos and live performances. AI-generated cinematic clips drop in Phase 4."
        />

        <div className="mt-12 grid gap-6 sm:grid-cols-2">
          {videos.map((video, i) => (
            <motion.button
              key={video.id}
              type="button"
              aria-label={`Play ${video.title}`}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.45, delay: i * 0.06, ease: "easeOut" }}
              className="group relative aspect-video overflow-hidden rounded-2xl border border-border/70 bg-ink-card text-left"
            >
              {/* Placeholder backdrop */}
              <div className="absolute inset-0 bg-gradient-to-br from-brand-blue/25 via-ink to-brand-red/20 transition-transform duration-500 group-hover:scale-105" />

              {/* Play button */}
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-white/90 text-ink shadow-glow-blue transition-transform duration-200 group-hover:scale-110">
                  <svg className="ml-1 h-7 w-7" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </span>
              </div>

              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink to-transparent p-5">
                <p className="font-display text-lg text-brand-white">{video.title}</p>
              </div>
            </motion.button>
          ))}
        </div>
      </div>
    </section>
  );
}
