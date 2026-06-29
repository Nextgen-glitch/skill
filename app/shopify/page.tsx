"use client";

import { useEffect, useState } from "react";

interface Product {
  id: string;
  title: string;
  product_type?: string;
  tags?: string[];
}

interface Copy {
  titleSuggestion: string;
  descriptionHtml: string;
}

export default function ShopifyPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [drafts, setDrafts] = useState<Record<string, Copy>>({});
  const [working, setWorking] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/shopify/products")
      .then((r) => r.json())
      .then((d) => setProducts(d.products))
      .finally(() => setLoading(false));
  }, []);

  async function generate(p: Product) {
    setWorking(p.id);
    const r = await fetch("/api/shopify/generate-copy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product: p }),
    });
    const data = await r.json();
    setDrafts((prev) => ({ ...prev, [p.id]: data }));
    setWorking(null);
  }

  async function push(p: Product) {
    const copy = drafts[p.id];
    if (!copy) return;
    setWorking(p.id);
    const r = await fetch("/api/shopify/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: p.id,
        title: copy.titleSuggestion,
        body_html: copy.descriptionHtml,
      }),
    });
    setWorking(null);
    if (r.ok) alert("Pushed to Shopify.");
    else alert(await r.text());
  }

  return (
    <div className="space-y-6">
      <h2 className="font-display text-3xl">Shopify Product Sync</h2>
      {loading ? (
        <p className="text-sm text-delix-ink/60">Loading products...</p>
      ) : (
        <div className="space-y-4">
          {products.map((p) => (
            <div
              key={p.id}
              className="bg-white rounded-xl border border-delix-gold/30 p-5"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-display text-lg">{p.title}</h3>
                  <p className="text-xs text-delix-ink/50">
                    {p.product_type} &middot; {p.tags?.join(", ")}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => generate(p)}
                    disabled={working === p.id}
                    className="text-xs px-3 py-1 border border-delix-ink rounded disabled:opacity-40"
                  >
                    Generate copy
                  </button>
                  {drafts[p.id] && (
                    <button
                      onClick={() => push(p)}
                      disabled={working === p.id}
                      className="text-xs px-3 py-1 bg-delix-ink text-white rounded disabled:opacity-40"
                    >
                      Push to Shopify
                    </button>
                  )}
                </div>
              </div>
              {drafts[p.id] && (
                <div className="mt-3 border-t border-delix-gold/20 pt-3 text-sm space-y-2">
                  <p className="text-xs text-delix-ink/50">
                    Suggested title: <strong>{drafts[p.id].titleSuggestion}</strong>
                  </p>
                  <div
                    className="prose prose-sm"
                    dangerouslySetInnerHTML={{
                      __html: drafts[p.id].descriptionHtml,
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
