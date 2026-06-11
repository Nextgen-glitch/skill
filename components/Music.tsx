"use client";

import { motion } from "framer-motion";
import { songs } from "@/lib/data";
import SectionHeading from "./SectionHeading";

export default function Music() {
  return (
    <section id="music" className="section-pad">
      <div className="container-x">
        <SectionHeading
          eyebrow="The Music"
          title={
            <>
              Tracks That Move <span className="text-brand-red-bright">The Crowd</span>
            </>
          }
          subtitle="A taste of the catalog. Full player with audio-reactive visuals arrives in the next build phase."
        />

        <ul className="mt-12 space-y-3">
          {songs.map((song, i) => (
            <motion.li
              key={song.id}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.4, delay: i * 0.04, ease: "easeOut" }}
            >
              <div className="group flex items-center gap-4 rounded-xl border border-border/70 bg-ink-card/60 p-4 transition-colors hover:border-brand-blue-bright/60 sm:gap-5 sm:p-5">
                <span className="w-6 text-center font-display text-lg text-brand-white/40">
                  {i + 1}
                </span>

                <button
                  type="button"
                  aria-label={`Play ${song.title}`}
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brand-blue text-brand-white transition-transform duration-200 group-hover:scale-105 group-hover:bg-brand-blue-bright"
                >
                  <svg className="ml-0.5 h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </button>

                <div className="min-w-0 flex-1">
                  <p className="truncate font-semibold text-brand-white">{song.title}</p>
                  <p className="text-sm text-brand-white/50">E. Ness · Ness Cheesecake</p>
                </div>

                {/* Static equalizer bars — become audio-reactive in Phase 3 */}
                <div className="hidden items-end gap-1 sm:flex" aria-hidden="true">
                  {[10, 18, 8, 22, 14].map((h, b) => (
                    <span
                      key={b}
                      className="w-1 rounded-full bg-brand-red/60"
                      style={{ height: `${h}px` }}
                    />
                  ))}
                </div>

                <span className="ml-2 w-12 text-right font-medium tabular-nums text-brand-white/50">
                  {song.length}
                </span>
              </div>
            </motion.li>
          ))}
        </ul>
      </div>
    </section>
  );
}
