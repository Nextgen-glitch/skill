"use client";

import { useState } from "react";
import { Smartphone, Tablet, Watch, Headphones, Home, Cable, Package } from "lucide-react";
import type { Category } from "@/lib/types";

const ICON: Record<Category, typeof Smartphone> = {
  Smartphones: Smartphone,
  Tablets: Tablet,
  Smartwatches: Watch,
  Audio: Headphones,
  "Smart Home": Home,
  Accessories: Cable,
};

export function ProductImage({
  src,
  alt,
  category,
  className = "",
}: {
  src?: string | null;
  alt: string;
  category: Category;
  className?: string;
}) {
  const [failed, setFailed] = useState(false);
  const Icon = ICON[category] ?? Package;

  if (!src || failed) {
    return (
      <div
        className={`relative flex items-center justify-center overflow-hidden bg-gradient-to-br from-[#1c1916] to-[#0f0d0b] ${className}`}
      >
        <div className="absolute inset-0 bg-[radial-gradient(60%_60%_at_50%_35%,rgba(212,146,42,0.14),transparent_70%)]" />
        <Icon className="relative h-16 w-16 text-accent/40" strokeWidth={1.2} />
      </div>
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      loading="lazy"
      onError={() => setFailed(true)}
      className={`object-cover ${className}`}
    />
  );
}
