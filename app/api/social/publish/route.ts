import { NextResponse } from "next/server";
import { z } from "zod";
import { publishPost } from "@/lib/agents/social";

const Schema = z.object({
  platform: z.enum(["facebook", "instagram", "tiktok"]),
  caption: z.string().min(1),
  hashtags: z.array(z.string()),
});

export async function POST(req: Request) {
  try {
    const { platform, caption, hashtags } = Schema.parse(await req.json());
    const result = await publishPost(platform, caption, hashtags);
    return NextResponse.json(result);
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Failed";
    return new NextResponse(msg, { status: 400 });
  }
}
