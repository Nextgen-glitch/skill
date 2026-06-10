import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export function ComingSoon({
  title,
  blurb,
}: {
  title: string;
  blurb: string;
}) {
  return (
    <section className="container-px flex min-h-[70svh] flex-col items-center justify-center py-32 text-center">
      <span className="eyebrow">In the workshop</span>
      <h1 className="mt-5 text-balance text-4xl font-semibold tracking-tight sm:text-5xl">
        {title} <span className="text-gradient-gold">coming soon</span>
      </h1>
      <p className="mt-4 max-w-md text-base leading-relaxed text-secondary">{blurb}</p>
      <Link href="/" className="btn-ghost group mt-9">
        <ArrowLeft size={16} className="transition-transform group-hover:-translate-x-1" />
        Back home
      </Link>
    </section>
  );
}
