import { NextResponse } from "next/server";
import { z } from "zod";
import { generateCopy } from "@/lib/agents/shopify";

const Schema = z.object({
  product: z.object({
    id: z.string(),
    title: z.string(),
    product_type: z.string().optional(),
    tags: z.array(z.string()).optional(),
  }),
});

export async function POST(req: Request) {
  try {
    const { product } = Schema.parse(await req.json());
    const copy = await generateCopy(product);
    return NextResponse.json(copy);
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Bad request";
    return new NextResponse(msg, { status: 400 });
  }
}
