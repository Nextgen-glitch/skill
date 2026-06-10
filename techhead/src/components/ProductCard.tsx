import Link from "next/link";
import { Star, Plus } from "lucide-react";
import type { Product } from "@/lib/types";
import { formatPrice, discountPct } from "@/lib/format";
import { ProductImage } from "./ProductImage";

export function ProductCard({ product }: { product: Product }) {
  const off = discountPct(product.price, product.originalPrice);

  return (
    <Link
      href={`/shop/${product.id}`}
      className="card-glass group flex flex-col"
      aria-label={`${product.name} — ${formatPrice(product.price)}`}
    >
      <div className="relative aspect-square overflow-hidden">
        <ProductImage
          src={product.image}
          alt={product.name}
          category={product.category}
          className="h-full w-full transition-transform duration-700 ease-out group-hover:scale-[1.06]"
        />
        <div className="absolute inset-x-0 top-0 flex items-start justify-between p-3">
          <div className="flex flex-col gap-1.5">
            {product.condition === "Refurbished" && (
              <span className="rounded-full border border-white/10 bg-black/50 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-secondary backdrop-blur">
                Refurbished
              </span>
            )}
            {off && (
              <span className="rounded-full bg-accent px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-[#1a1207]">
                -{off}%
              </span>
            )}
          </div>
          <span className="rounded-full border border-white/10 bg-black/40 px-2.5 py-1 text-[10px] font-medium text-secondary backdrop-blur">
            {product.category}
          </span>
        </div>
      </div>

      <div className="flex flex-1 flex-col p-5">
        <div className="flex items-center gap-1 text-xs text-secondary">
          <Star size={13} className="fill-accent text-accent" />
          <span className="font-medium text-foreground">{product.rating.toFixed(1)}</span>
          <span>({product.reviews})</span>
          <span className="mx-1.5 h-1 w-1 rounded-full bg-border" />
          <span>{product.brand}</span>
        </div>

        <h3 className="mt-2 text-base font-semibold leading-snug text-foreground transition-colors group-hover:text-accent-soft">
          {product.name}
        </h3>
        <p className="mt-1.5 line-clamp-2 text-sm leading-relaxed text-secondary">
          {product.description}
        </p>

        <div className="mt-auto flex items-end justify-between pt-4">
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-semibold tabular-nums text-foreground">
              {formatPrice(product.price)}
            </span>
            {product.originalPrice && (
              <span className="text-sm tabular-nums text-secondary line-through">
                {formatPrice(product.originalPrice)}
              </span>
            )}
          </div>
          <span
            className="flex h-9 w-9 items-center justify-center rounded-full border border-border text-secondary transition-all duration-300 group-hover:border-accent group-hover:bg-accent group-hover:text-[#1a1207]"
            aria-hidden="true"
          >
            <Plus size={16} />
          </span>
        </div>
      </div>
    </Link>
  );
}
