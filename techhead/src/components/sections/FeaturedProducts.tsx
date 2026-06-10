import Link from "next/link";
import { ArrowRight } from "lucide-react";
import type { Product } from "@/lib/types";
import { SectionHeading } from "../SectionHeading";
import { Stagger, StaggerItem } from "../Reveal";
import { ProductCard } from "../ProductCard";

export function FeaturedProducts({ products }: { products: Product[] }) {
  if (!products.length) return null;
  return (
    <section className="container-px py-20 sm:py-28" id="featured">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <SectionHeading
          eyebrow="Trending now"
          title={<>Featured <span className="text-gradient-gold">picks</span></>}
          subtitle="Hand-selected gadgets our customers love — in stock and ready to ship."
        />
        <Link
          href="/shop"
          className="group inline-flex items-center gap-2 text-sm font-semibold text-accent"
        >
          View all products
          <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
        </Link>
      </div>

      <Stagger className="mt-12 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {products.slice(0, 8).map((p) => (
          <StaggerItem key={p.id}>
            <ProductCard product={p} />
          </StaggerItem>
        ))}
      </Stagger>
    </section>
  );
}
