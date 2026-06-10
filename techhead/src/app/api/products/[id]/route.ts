import { NextRequest, NextResponse } from "next/server";
import { readProducts, writeProducts } from "@/lib/store";
import type { Product } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function PUT(req: NextRequest, { params }: { params: { id: string } }) {
  let body: Partial<Product>;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const products = await readProducts();
  const idx = products.findIndex((p) => p.id === params.id);
  if (idx === -1) return NextResponse.json({ error: "Not found" }, { status: 404 });

  products[idx] = { ...products[idx], ...body, id: params.id };
  await writeProducts(products);
  return NextResponse.json(products[idx]);
}

export async function DELETE(_req: NextRequest, { params }: { params: { id: string } }) {
  const products = await readProducts();
  const next = products.filter((p) => p.id !== params.id);
  if (next.length === products.length) return NextResponse.json({ error: "Not found" }, { status: 404 });
  await writeProducts(next);
  return NextResponse.json({ ok: true });
}
