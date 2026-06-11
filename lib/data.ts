// Central content source — swap these for real tracks/videos in Phase 2.

export const artist = {
  name: "E. Ness",
  brand: "Ness Cheesecake",
  tagline: "Made With Brotherly Love",
  city: "Philadelphia, PA",
  bookingEmail: "booking@nesscheesecake.com", // TODO: confirm real booking inbox
  socials: {
    instagram: "https://www.instagram.com/theofficialeness",
    facebook: "https://www.facebook.com/share/1J8umQgFb8/",
  },
  bio: [
    "E. Ness is a Philadelphia institution — a battle rap legend who took the raw cadence of the city's streets and carried it all the way to the national stage. From corner ciphers to coast-to-coast attention, his name has long been synonymous with that unmistakable Philly hunger.",
    "That same energy now fuels Ness Cheesecake: an artist and a movement, built with brotherly love. Whether it's a packed club, a private party, or a festival crowd, E. Ness brings the authentic fire and crowd-moving presence that only a true performer can deliver.",
  ],
};

// Featured promo clip provided by the artist.
export const featuredVideo = {
  src: "/media/eness-clip.mp4",
  title: "E. Ness — Live & Direct",
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
