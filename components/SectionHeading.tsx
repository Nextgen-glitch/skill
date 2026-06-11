"use client";

import { motion } from "framer-motion";

export default function SectionHeading({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: React.ReactNode;
  subtitle?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="max-w-2xl"
    >
      <span className="eyebrow">{eyebrow}</span>
      <h2 className="heading-lg mt-3 text-brand-white">{title}</h2>
      {subtitle && (
        <p className="mt-4 text-base text-brand-white/65 sm:text-lg">{subtitle}</p>
      )}
    </motion.div>
  );
}
