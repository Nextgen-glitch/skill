"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Menu, X, ShoppingBag, Search } from "lucide-react";
import { Logo } from "./Logo";

const links = [
  { href: "/shop", label: "Shop" },
  { href: "/repairs", label: "Repairs" },
  { href: "/about", label: "About" },
  { href: "/contact", label: "Contact" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
  }, [open]);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-[100] transition-all duration-500 ${
        scrolled ? "py-2" : "py-4"
      }`}
    >
      <div className="container-px">
        <nav
          className={`flex items-center justify-between rounded-full px-4 py-2.5 transition-all duration-500 ${
            scrolled ? "glass-strong shadow-glass" : "border border-transparent"
          }`}
        >
          <Link href="/" aria-label="TechHead Electronics home" className="pl-1">
            <Logo />
          </Link>

          <div className="hidden items-center gap-1 md:flex">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className="rounded-full px-4 py-2 text-sm font-medium text-secondary transition-colors hover:text-foreground"
              >
                {l.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/shop"
              aria-label="Search products"
              className="hidden h-10 w-10 items-center justify-center rounded-full text-secondary transition-colors hover:bg-white/5 hover:text-foreground sm:flex"
            >
              <Search size={18} />
            </Link>
            <Link
              href="/shop"
              className="relative flex h-10 w-10 items-center justify-center rounded-full text-secondary transition-colors hover:bg-white/5 hover:text-foreground"
              aria-label="Cart"
            >
              <ShoppingBag size={18} />
              <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-accent text-[10px] font-bold text-[#1a1207]">
                0
              </span>
            </Link>
            <Link href="/admin" className="btn-gold ml-1 hidden px-5 py-2.5 text-sm sm:inline-flex">
              Sell on TechHead
            </Link>
            <button
              onClick={() => setOpen((v) => !v)}
              aria-label={open ? "Close menu" : "Open menu"}
              aria-expanded={open}
              className="flex h-10 w-10 items-center justify-center rounded-full text-foreground transition-colors hover:bg-white/5 md:hidden"
            >
              {open ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </nav>
      </div>

      {/* Mobile sheet */}
      <div
        className={`fixed inset-0 top-0 z-[-1] md:hidden ${open ? "" : "pointer-events-none"}`}
      >
        <div
          onClick={() => setOpen(false)}
          className={`absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity duration-300 ${
            open ? "opacity-100" : "opacity-0"
          }`}
        />
        <div
          className={`glass-strong absolute inset-x-3 top-20 rounded-3xl p-3 transition-all duration-300 ${
            open ? "translate-y-0 opacity-100" : "-translate-y-4 opacity-0"
          }`}
        >
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              className="block rounded-2xl px-4 py-3.5 text-base font-medium text-foreground transition-colors hover:bg-white/5"
            >
              {l.label}
            </Link>
          ))}
          <Link
            href="/admin"
            onClick={() => setOpen(false)}
            className="btn-gold mt-2 w-full"
          >
            Sell on TechHead
          </Link>
        </div>
      </div>
    </header>
  );
}
