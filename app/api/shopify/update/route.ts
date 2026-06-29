import { NextResponse } from "next/server";
import { z } from "zod";
import { updateProduct } from "@/lib/agents/shopify";

const Schema = z.object({
  id: z.string(),
  title: z.string().optional(),
  body_html: z.string().optional(),
});

export async function POST(req: Request) {
  try {
    const { id, ...fields } = Schema.parse(await req.json());
    const result = await updateProduct(id, fields);
    return NextResponse.json(result);
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Failed";
    return new NextResponse(msg, { status: 400 });
  }
}
