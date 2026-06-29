import { NextResponse } from "next/server";
import { recordIncoming } from "@/lib/agents/inbox";

// Drops a couple of sample DMs into the inbox so you can demo the agent
// without setting up Facebook / TikTok webhooks first.
export async function POST() {
  const now = Date.now();
  await recordIncoming({
    id: `seed_${now}_1`,
    source: "facebook",
    senderId: "fb_user_42",
    text: "Hi! Is the rose serum good for oily skin?",
    ts: now,
  });
  await recordIncoming({
    id: `seed_${now}_2`,
    source: "tiktok",
    senderId: "tt_user_91",
    text: "Saw this on your TikTok — what is it?",
    imageUrl: "https://placehold.co/400x400/D4A5A5/ffffff?text=product+photo",
    ts: now + 1,
  });
  await recordIncoming({
    id: `seed_${now}_3`,
    source: "facebook",
    senderId: "fb_user_77",
    text: "My skin reacted badly to your cream and I want a refund.",
    ts: now + 2,
  });
  return NextResponse.json({ ok: true });
}
