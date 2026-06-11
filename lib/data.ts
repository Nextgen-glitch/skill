// Central content source — swap these for real tracks/videos in Phase 2.

export const artist = {
  name: "E. Ness",
  brand: "Ness Cheesecake",
  tagline: "Made With Brotherly Love",
  city: "Philadelphia, PA",
  bookingEmail: "booking@nesscheesecake.com",
  socials: {
    instagram: "https://instagram.com/",
    youtube: "https://youtube.com/",
    spotify: "https://spotify.com/",
    apple: "https://music.apple.com/",
  },
};

export type Song = {
  id: string;
  title: string;
  length: string;
  cover?: string;
  src?: string; // audio file — wired in Phase 3
};

export const songs: Song[] = [
  { id: "s1", title: "Brotherly Love", length: "3:14" },
  { id: "s2", title: "Philly Skyline", length: "2:58" },
  { id: "s3", title: "Battle Tested", length: "3:41" },
  { id: "s4", title: "Street Cadence", length: "3:05" },
  { id: "s5", title: "Cheesecake Flow", length: "2:47" },
];

export type Video = {
  id: string;
  title: string;
  thumb?: string;
  url?: string; // embed/Higgsfield clip — wired in Phase 4
};

export const videos: Video[] = [
  { id: "v1", title: "Official Music Video" },
  { id: "v2", title: "Live Performance" },
  { id: "v3", title: "Behind The Scenes" },
  { id: "v4", title: "Studio Session" },
];

export const eventTypes = [
  "Private Party",
  "Club / Venue",
  "Corporate Event",
  "Festival",
  "Wedding",
  "Other",
];

export const navLinks = [
  { label: "Home", href: "#home" },
  { label: "Music", href: "#music" },
  { label: "Videos", href: "#videos" },
  { label: "About", href: "#about" },
  { label: "Book", href: "#book" },
];
