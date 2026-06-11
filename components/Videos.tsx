"use client";

import { motion } from "framer-motion";
import { videos, featuredVideo } from "@/lib/data";
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
          subtitle="Straight from E. Ness. More music videos and live sets coming soon."
        />

        {/* Featured real clip — adaptive player handles any aspect ratio */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="mt-12 overflow-hidden rounded-2xl border border-border/70 bg-black shadow-glow-blue"
        >
          <video
            className="mx-auto max-h-[80vh] w-full object-contain"
            src={featuredVideo.src}
            controls
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
            aria-label={featuredVideo.title}
          />
        </motion.div>

        <div className="mt-6 grid gap-6 sm:grid-cols-2">
          {videos.map((video, i) => (
            <motion.div
              key={video.id}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.45, delay: i * 0.06, ease: "easeOut" }}
              className="group relative aspect-video overflow-hidden rounded-2xl border border-border/70 bg-ink-card"
            >
              {/* Placeholder backdrop */}
              <div className="absolute inset-0 bg-gradient-to-br from-brand-blue/25 via-ink to-brand-red/20" />

              <div className="absolute right-4 top-4 rounded-full border border-border bg-ink/70 px-3 py-1 text-xs font-medium uppercase tracking-wider text-brand-white/60 backdrop-blur">
                Coming soon
              </div>

              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink to-transparent p-5">
                <p className="font-display text-lg text-brand-white">{video.title}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
