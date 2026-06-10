import type { RepairService } from "./types";

export const REPAIRS: RepairService[] = [
  {
    id: "screen",
    title: "Screen Replacement",
    blurb: "Cracked or unresponsive display? We fit genuine-grade panels and restore true color and touch.",
    from: 79,
    turnaround: "From 45 min",
  },
  {
    id: "battery",
    title: "Battery Service",
    blurb: "New cells for phones, tablets and laptops — get a full day of life back with a tested battery.",
    from: 49,
    turnaround: "Same day",
  },
  {
    id: "computer",
    title: "Computer Repair",
    blurb: "Laptops & desktops of every brand — hardware faults, upgrades, SSD swaps and thermal fixes.",
    from: 89,
    turnaround: "1–3 days",
  },
  {
    id: "diagnostics",
    title: "Software & Virus",
    blurb: "Slowdowns, glitches and infections cleared. Data-safe diagnostics with a clear quote first.",
    from: 39,
    turnaround: "Free diagnosis",
  },
];
