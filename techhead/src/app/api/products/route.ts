import { NextRequest, NextResponse } from "next/server";
import { readProducts, writeProducts, slugify } from "@/lib/store";
import { CATEGORIES, type Product } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function GET() {
  const products = await readProducts();
  return NextResponse.json(products);
}

export async function POST(req: NextRequest) {
  let body: Partial<Product>;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const errors: string[] = [];
  if (!body.name?.trim()) errors.push("name is required");
  if (!body.category || !CATEGORIES.includes(body.category)) errors.push("valid category is required");
  if (typeof body.price !== "number" || body.price < 0) errors.push("price must be a positive number");
  if (errors.length) return NextResponse.json({ error: errors.join(", ") }, { status: 400 });

  const products = await readProducts();
  const id = `p-${slugify(body.name!)}-${Date.now().toString(36)}`;
  const product: Product = {
    id,
    name: body.name!.trim(),
    brand: body.brand?.trim() || "TechHead",
    category: body.category!,
    condition: body.condition === "Refurbished" ? "Refurbished" : "New",
    price: body.price!,
    originalPrice: body.originalPrice ?? null,
    description: body.description?.trim() || "",
    specs: Array.isArray(body.specs) ? body.specs.filter(Boolean).slice(0, 8) : [],
    image: body.image?.trim() || null,
    rating: typeof body.rating === "number" ? Math.min(5, Math.max(0, body.rating)) : 5,
    reviews: typeof body.reviews === "number" ? body.reviews : 0,
    stock: typeof body.stock === "number" ? body.stock : 0,
    featured: Boolean(body.featured),
    createdAt: new Date().toISOString(),
  };

  products.unshift(product);
  await writeProducts(products);
  return NextResponse.json(product, { status: 201 });
}
