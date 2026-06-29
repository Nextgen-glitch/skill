import { ask } from "@/lib/claude";
import { logActivity } from "@/lib/activity";
import { integrationMode } from "@/lib/env";

export interface ShopifyProduct {
  id: string;
  title: string;
  handle?: string;
  body_html?: string;
  vendor?: string;
  product_type?: string;
  tags?: string[];
}

const MOCK_PRODUCTS: ShopifyProduct[] = [
  {
    id: "gid://shopify/Product/1001",
    title: "Rose Hydration Serum",
    handle: "rose-hydration-serum",
    body_html: "",
    vendor: "Delix",
    product_type: "Serum",
    tags: ["hydration", "rose", "all skin types"],
  },
  {
    id: "gid://shopify/Product/1002",
    title: "Golden Glow Day Cream",
    handle: "golden-glow-day-cream",
    body_html: "",
    vendor: "Delix",
    product_type: "Moisturizer",
    tags: ["glow", "spf", "day"],
  },
  {
    id: "gid://shopify/Product/1003",
    title: "Midnight Repair Mask",
    handle: "midnight-repair-mask",
    body_html: "",
    vendor: "Delix",
    product_type: "Mask",
    tags: ["overnight", "repair"],
  },
];

export async function listProducts(): Promise<ShopifyProduct[]> {
  if (integrationMode() === "mock") return MOCK_PRODUCTS;

  // LIVE: Shopify Admin REST API
  // GET https://{store}.myshopify.com/admin/api/{version}/products.json
  const domain = process.env.SHOPIFY_STORE_DOMAIN;
  const token = process.env.SHOPIFY_ADMIN_ACCESS_TOKEN;
  const version = process.env.SHOPIFY_API_VERSION ?? "2024-10";
  if (!domain || !token) {
    throw new Error("Set SHOPIFY_STORE_DOMAIN and SHOPIFY_ADMIN_ACCESS_TOKEN.");
  }
  const r = await fetch(
    `https://${domain}/admin/api/${version}/products.json?limit=50`,
    { headers: { "X-Shopify-Access-Token": token } },
  );
  if (!r.ok) throw new Error(`Shopify ${r.status}: ${await r.text()}`);
  const data = (await r.json()) as { products: ShopifyProduct[] };
  return data.products;
}

const COPY_SYSTEM = `You write product descriptions for DELIX COSMETICS.
Keep it sensory, specific, and confident. 2 short paragraphs.

Return JSON only:
{ "title_suggestion": "...", "description_html": "<p>...</p><p>...</p>" }`;

export async function generateCopy(product: ShopifyProduct): Promise<{
  titleSuggestion: string;
  descriptionHtml: string;
}> {
  const prompt = [
    `Product: ${product.title}`,
    product.product_type ? `Type: ${product.product_type}` : "",
    product.tags?.length ? `Tags: ${product.tags.join(", ")}` : "",
  ]
    .filter(Boolean)
    .join("\n");

  const raw = await ask(COPY_SYSTEM, prompt, { maxTokens: 700 });
  const match = raw.match(/\{[\s\S]*\}/);
  if (!match) {
    return { titleSuggestion: product.title, descriptionHtml: `<p>${raw}</p>` };
  }
  try {
    const parsed = JSON.parse(match[0]);
    await logActivity("shopify", `Generated copy for "${product.title}"`);
    return {
      titleSuggestion: parsed.title_suggestion ?? product.title,
      descriptionHtml: parsed.description_html ?? `<p>${raw}</p>`,
    };
  } catch {
    return { titleSuggestion: product.title, descriptionHtml: `<p>${raw}</p>` };
  }
}

export async function updateProduct(
  id: string,
  fields: { title?: string; body_html?: string },
): Promise<{ ok: true }> {
  if (integrationMode() === "mock") {
    await logActivity(
      "shopify",
      `[mock] Updated product ${id}: ${Object.keys(fields).join(", ")}`,
    );
    return { ok: true };
  }

  // LIVE: Shopify Admin REST API
  // PUT /admin/api/{version}/products/{id}.json
  const domain = process.env.SHOPIFY_STORE_DOMAIN;
  const token = process.env.SHOPIFY_ADMIN_ACCESS_TOKEN;
  const version = process.env.SHOPIFY_API_VERSION ?? "2024-10";
  if (!domain || !token) {
    throw new Error("Set SHOPIFY_STORE_DOMAIN and SHOPIFY_ADMIN_ACCESS_TOKEN.");
  }
  // Shopify REST product IDs are numeric, not GIDs. Strip prefix.
  const numericId = id.replace(/^gid:\/\/shopify\/Product\//, "");
  const r = await fetch(
    `https://${domain}/admin/api/${version}/products/${numericId}.json`,
    {
      method: "PUT",
      headers: {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ product: { id: numericId, ...fields } }),
    },
  );
  if (!r.ok) throw new Error(`Shopify ${r.status}: ${await r.text()}`);
  await logActivity("shopify", `Updated product ${numericId}`);
  return { ok: true };
}
