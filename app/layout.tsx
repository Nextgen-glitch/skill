import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DELIX COSMETICS AGENT",
  description:
    "AI agents for social media posting, Shopify sync, and Facebook/TikTok DM replies.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="border-b border-delix-rose/30 bg-delix-mist">
          <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
            <div>
              <h1 className="font-display text-2xl tracking-wide">
                DELIX <span className="text-delix-gold">COSMETICS</span> AGENT
              </h1>
              <p className="text-xs uppercase tracking-widest text-delix-ink/60">
                AI agents for your store
              </p>
            </div>
            <nav className="flex gap-6 text-sm">
              <a href="/" className="hover:text-delix-gold">Dashboard</a>
              <a href="/social" className="hover:text-delix-gold">Social</a>
              <a href="/shopify" className="hover:text-delix-gold">Shopify</a>
              <a href="/inbox" className="hover:text-delix-gold">Inbox</a>
            </nav>
          </div>
        </header>
        <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
        <footer className="border-t border-delix-rose/20 mt-12 py-6 text-center text-xs text-delix-ink/50">
          DELIX COSMETICS AGENT &middot; powered by Claude
        </footer>
      </body>
    </html>
  );
}
