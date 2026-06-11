"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { eventTypes } from "@/lib/data";
import SectionHeading from "./SectionHeading";

type Status = "idle" | "submitting" | "success" | "error";

const inputBase =
  "w-full rounded-xl border border-border bg-ink/70 px-4 py-3 text-brand-white placeholder:text-brand-white/35 outline-none transition-colors focus:border-brand-blue-bright focus:ring-2 focus:ring-brand-blue-bright/30";

export default function Booking() {
  const [status, setStatus] = useState<Status>("idle");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setStatus("submitting");

    // Phase 5: POST to /api/book -> Google Calendar event + Gmail confirmation.
    // For now we simulate a successful request so the UX is complete.
    try {
      await new Promise((r) => setTimeout(r, 900));
      setStatus("success");
      e.currentTarget.reset();
    } catch {
      setStatus("error");
    }
  }

  return (
    <section id="book" className="section-pad bg-ink-soft/40">
      <div className="container-x grid items-start gap-12 lg:grid-cols-2">
        <div className="lg:sticky lg:top-28">
          <SectionHeading
            eyebrow="Book The Show"
            title={
              <>
                Bring E. Ness To <span className="text-cta">Your Event</span>
              </>
            }
            subtitle="Parties, clubs, corporate events, festivals — tell us about your event and the team will get back to you within 48 hours."
          />

          <ul className="mt-8 space-y-4 text-brand-white/70">
            {[
              "Live performance tailored to your event",
              "Flexible packages for any venue size",
              "Fast response — usually within 48 hours",
            ].map((item) => (
              <li key={item} className="flex items-start gap-3">
                <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-cta/20 text-cta">
                  <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="glass rounded-3xl p-6 sm:p-8"
        >
          {status === "success" ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-cta/20 text-cta shadow-glow-cta">
                <svg className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="mt-5 font-display text-2xl text-brand-white">Request Sent!</h3>
              <p className="mt-2 max-w-sm text-brand-white/65">
                Thanks for reaching out. The team will get back to you within 48 hours to lock in your date.
              </p>
              <button
                type="button"
                onClick={() => setStatus("idle")}
                className="mt-6 rounded-full border border-border px-6 py-2.5 text-sm font-semibold text-brand-white transition-colors hover:bg-white/5"
              >
                Send another request
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5" noValidate>
              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="name" className="mb-1.5 block text-sm font-medium text-brand-white/80">
                    Your name <span className="text-brand-red-bright">*</span>
                  </label>
                  <input id="name" name="name" type="text" required autoComplete="name" placeholder="Jane Doe" className={inputBase} />
                </div>
                <div>
                  <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-brand-white/80">
                    Email <span className="text-brand-red-bright">*</span>
                  </label>
                  <input id="email" name="email" type="email" required autoComplete="email" placeholder="jane@email.com" className={inputBase} />
                </div>
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="date" className="mb-1.5 block text-sm font-medium text-brand-white/80">
                    Event date <span className="text-brand-red-bright">*</span>
                  </label>
                  <input id="date" name="date" type="date" required className={inputBase} />
                </div>
                <div>
                  <label htmlFor="type" className="mb-1.5 block text-sm font-medium text-brand-white/80">
                    Event type
                  </label>
                  <select id="type" name="type" className={inputBase} defaultValue="">
                    <option value="" disabled>
                      Select…
                    </option>
                    {eventTypes.map((t) => (
                      <option key={t} value={t} className="bg-ink">
                        {t}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label htmlFor="message" className="mb-1.5 block text-sm font-medium text-brand-white/80">
                  Tell us about your event
                </label>
                <textarea id="message" name="message" rows={4} placeholder="Venue, city, expected guests, budget range…" className={`${inputBase} resize-none`} />
              </div>

              {status === "error" && (
                <p role="alert" className="text-sm text-brand-red-bright">
                  Something went wrong. Please try again or email us directly.
                </p>
              )}

              <button
                type="submit"
                disabled={status === "submitting"}
                className="flex w-full items-center justify-center gap-2 rounded-full bg-cta px-6 py-4 text-base font-semibold text-ink shadow-glow-cta transition-transform duration-200 hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {status === "submitting" ? (
                  <>
                    <span className="h-5 w-5 animate-spin rounded-full border-2 border-ink/30 border-t-ink" />
                    Sending…
                  </>
                ) : (
                  "Request Booking"
                )}
              </button>
              <p className="text-center text-xs text-brand-white/40">
                No spam, ever. Your details are only used to respond to this request.
              </p>
            </form>
          )}
        </motion.div>
      </div>
    </section>
  );
}
