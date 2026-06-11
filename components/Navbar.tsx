"use client";

import { useEffect, useState } from "react";
import { navLinks, artist } from "@/lib/data";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-colors duration-300 ${
        scrolled ? "bg-ink/85 backdrop-blur-md border-b border-border/60" : "bg-transparent"
      }`}
    >
      <nav className="container-x flex h-16 items-center justify-between sm:h-20">
        <a href="#home" className="flex items-center gap-2" aria-label={`${artist.brand} home`}>
          <span className="font-display text-xl tracking-wide text-brand-white sm:text-2xl">
            <span className="text-brand-red-bright">NESS</span>{" "}
            <span className="text-brand-blue-bright">CHEESECAKE</span>
          </span>
        </a>

        {/* Desktop nav */}
        <ul className="hidden items-center gap-8 md:flex">
          {navLinks.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm font-medium text-brand-white/80 transition-colors hover:text-brand-white"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="hidden md:block">
          <a
            href="#book"
            className="rounded-full bg-cta px-5 py-2.5 text-sm font-semibold text-ink shadow-glow-cta transition-transform duration-200 hover:scale-[1.04]"
          >
            Book a Show
          </a>
        </div>

        {/* Mobile toggle */}
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
          className="flex h-11 w-11 items-center justify-center rounded-lg text-brand-white md:hidden"
        >
          <div className="space-y-1.5">
            <span
              className={`block h-0.5 w-6 bg-current transition-transform ${
                open ? "translate-y-2 rotate-45" : ""
              }`}
            />
            <span
              className={`block h-0.5 w-6 bg-current transition-opacity ${
                open ? "opacity-0" : ""
              }`}
            />
            <span
              className={`block h-0.5 w-6 bg-current transition-transform ${
                open ? "-translate-y-2 -rotate-45" : ""
              }`}
            />
          </div>
        </button>
      </nav>

      {/* Mobile menu */}
      {open && (
        <div className="border-t border-border/60 bg-ink/95 backdrop-blur-md md:hidden">
          <ul className="container-x flex flex-col gap-1 py-4">
            {navLinks.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="block rounded-lg px-3 py-3 text-base font-medium text-brand-white/85 hover:bg-white/5"
                >
                  {link.label}
                </a>
              </li>
            ))}
            <li className="pt-2">
              <a
                href="#book"
                onClick={() => setOpen(false)}
                className="block rounded-full bg-cta px-5 py-3 text-center text-base font-semibold text-ink shadow-glow-cta"
              >
                Book a Show
              </a>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
}
