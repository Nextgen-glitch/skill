import Link from "next/link";
import { MapPin, Phone, Mail, Instagram, Facebook } from "lucide-react";
import { Logo } from "./Logo";

const cols = [
  {
    title: "Shop",
    links: [
      { label: "Smartphones", href: "/shop?category=Smartphones" },
      { label: "Smartwatches", href: "/shop?category=Smartwatches" },
      { label: "Audio", href: "/shop?category=Audio" },
      { label: "Smart Home", href: "/shop?category=Smart+Home" },
      { label: "Refurbished", href: "/shop?condition=Refurbished" },
    ],
  },
  {
    title: "Services",
    links: [
      { label: "Phone Repair", href: "/repairs#phone" },
      { label: "Computer Repair", href: "/repairs#computer" },
      { label: "Battery Service", href: "/repairs#battery" },
      { label: "Diagnostics", href: "/repairs#diagnostics" },
      { label: "Book a Repair", href: "/repairs" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About Us", href: "/about" },
      { label: "Contact", href: "/contact" },
      { label: "Sell on TechHead", href: "/admin" },
      { label: "Warranty", href: "/about#warranty" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="relative mt-24 border-t border-border/60">
      <div className="hairline h-px w-full" />
      <div className="container-px py-16">
        <div className="grid gap-12 lg:grid-cols-[1.4fr_1fr_1fr_1fr]">
          <div>
            <Logo />
            <p className="mt-5 max-w-xs text-sm leading-relaxed text-secondary">
              Where technology meets convenience. Premium gadgets, certified repairs and real
              human support — proudly serving Nassau and beyond.
            </p>
            <div className="mt-6 space-y-2.5 text-sm text-secondary">
              <p className="flex items-center gap-2.5">
                <MapPin size={15} className="text-accent" /> Nassau, The Bahamas
              </p>
              <p className="flex items-center gap-2.5">
                <Phone size={15} className="text-accent" /> +1 (242) 000-0000
              </p>
              <p className="flex items-center gap-2.5">
                <Mail size={15} className="text-accent" /> hello@techheadelectronics.com
              </p>
            </div>
          </div>

          {cols.map((col) => (
            <div key={col.title}>
              <h4 className="text-sm font-semibold text-foreground">{col.title}</h4>
              <ul className="mt-4 space-y-3">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      href={l.href}
                      className="text-sm text-secondary transition-colors hover:text-accent"
                    >
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-14 flex flex-col items-center justify-between gap-4 border-t border-border/60 pt-8 sm:flex-row">
          <p className="text-xs text-secondary">
            © {new Date().getFullYear()} TechHead Electronics. All rights reserved.
          </p>
          <div className="flex items-center gap-3">
            <a
              href="https://www.facebook.com/TechHeadElectronics/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="TechHead on Facebook"
              className="flex h-9 w-9 items-center justify-center rounded-full border border-border text-secondary transition-colors hover:border-accent hover:text-accent"
            >
              <Facebook size={16} />
            </a>
            <a
              href="https://www.instagram.com/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="TechHead on Instagram"
              className="flex h-9 w-9 items-center justify-center rounded-full border border-border text-secondary transition-colors hover:border-accent hover:text-accent"
            >
              <Instagram size={16} />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
