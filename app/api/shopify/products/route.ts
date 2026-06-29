import { NextResponse } from "next/server";
import { listProducts } from "@/lib/agents/shopify";

export async function GET() {
  try {
    const products = await listProducts();
    return NextResponse.json({ products });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Failed";
    return new NextResponse(msg, { status: 500 });
  }
}
