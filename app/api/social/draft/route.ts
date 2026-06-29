import { NextResponse } from "next/server";
import { z } from "zod";
import { draftPosts } from "@/lib/agents/social";

const Schema = z.object({
  topic: z.string().min(2),
  productName: z.string().optional(),
  platforms: z.array(z.enum(["facebook", "instagram", "tiktok"])).min(1),
  tone: z.enum(["elegant", "playful", "expert"]).optional(),
});

export async function POST(req: Request) {
  try {
    const body = Schema.parse(await req.json());
    const drafts = await draftPosts(body);
    return NextResponse.json({ drafts });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Bad request";
    return new NextResponse(msg, { status: 400 });
  }
}
