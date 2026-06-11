import type { Metadata, Viewport } from "next";
import { Righteous, Poppins } from "next/font/google";
import "./globals.css";

const righteous = Righteous({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-righteous",
  display: "swap",
});

const poppins = Poppins({
  weight: ["300", "400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "E. Ness · Ness Cheesecake — Book The Philly Battle Rap Legend",
  description:
    "Official site of E. Ness (Ness Cheesecake). Stream the music, watch the videos, and book him to perform live at your party, club, or event. Made with brotherly love.",
  keywords: [
    "E. Ness",
    "Ness Cheesecake",
    "Philly rapper",
    "battle rap",
    "book a rapper",
    "live performance booking",
  ],
  openGraph: {
    title: "E. Ness · Ness Cheesecake",
    description: "Stream the music. Watch the videos. Book the show.",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0F0F23",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${righteous.variable} ${poppins.variable}`}>
      <body>{children}</body>
    </html>
  );
}
