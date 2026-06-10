import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TechHead Electronics — Gadgets & Expert Repairs in Nassau",
  description:
    "Premium smartphones, tablets, smartwatches, earbuds and smart-home gadgets — plus certified phone & computer repair. Quality sourced, expertly serviced.",
  keywords: [
    "electronics Nassau",
    "phone repair",
    "computer repair",
    "smartphones",
    "smartwatches",
    "wireless earbuds",
    "TechHead Electronics",
  ],
  openGraph: {
    title: "TechHead Electronics — Gadgets & Expert Repairs",
    description:
      "Where technology meets convenience. Shop premium gadgets and book certified repairs.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[200] focus:rounded-full focus:bg-accent focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-[#1a1207]"
        >
          Skip to content
        </a>
        <Navbar />
        <main id="main">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
