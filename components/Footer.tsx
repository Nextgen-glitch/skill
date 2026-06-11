import { artist, navLinks } from "@/lib/data";

const socialLinks = [
  { label: "Instagram", href: artist.socials.instagram },
  { label: "Facebook", href: artist.socials.facebook },
];

export default function Footer() {
  return (
    <footer className="border-t border-border/60 bg-ink">
      <div className="container-x py-14">
        <div className="grid gap-10 md:grid-cols-3">
          <div>
            <p className="font-display text-xl">
              <span className="text-brand-red-bright">NESS</span>{" "}
              <span className="text-brand-blue-bright">CHEESECAKE</span>
            </p>
            <p className="mt-3 max-w-xs text-sm text-brand-white/55">
              {artist.tagline}. Booking E. Ness for live performances nationwide.
            </p>
          </div>

          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-brand-white/50">
              Explore
            </h3>
            <ul className="mt-4 space-y-2">
              {navLinks.map((l) => (
                <li key={l.href}>
                  <a href={l.href} className="text-sm text-brand-white/70 transition-colors hover:text-brand-white">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-brand-white/50">
              Connect
            </h3>
            <ul className="mt-4 space-y-2">
              {socialLinks.map((s) => (
                <li key={s.label}>
                  <a
                    href={s.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-brand-white/70 transition-colors hover:text-brand-white"
                  >
                    {s.label}
                  </a>
                </li>
              ))}
              <li>
                <a href={`mailto:${artist.bookingEmail}`} className="text-sm text-cta transition-colors hover:text-brand-white">
                  {artist.bookingEmail}
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-3 border-t border-border/50 pt-6 sm:flex-row">
          <p className="text-xs text-brand-white/40">
            © {new Date().getFullYear()} {artist.brand}. All rights reserved.
          </p>
          <p className="text-xs text-brand-white/40">Made with brotherly love in Philadelphia.</p>
        </div>
      </div>
    </footer>
  );
}
