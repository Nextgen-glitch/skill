import { NextResponse } from "next/server";
import { recordIncoming, draftReply } from "@/lib/agents/inbox";

// TikTok webhook verification varies by product (Business / Shop / Direct Messages).
// Most send a `challenge` query param to confirm the URL — we echo it back.
export async function GET(req: Request) {
  const url = new URL(req.url);
  const challenge = url.searchParams.get("challenge");
  if (challenge) return new NextResponse(challenge, { status: 200 });
  return new NextResponse("OK", { status: 200 });
}

// TikTok DM webhook payload (varies by product). We extract sender + text + image
// from a best-effort shape and you'll likely need to adjust this once you have
// real webhook samples from TikTok's docs for your approved product.
export async function POST(req: Request) {
  // TODO: Verify TikTok signature here. As of writing, TikTok signature schemes
  // differ across their APIs (Shop / Business). Add the verification once you
  // know which product issued your webhook secret.

  const payload = await req.json().catch(() => null);
  if (!payload) return new NextResponse("Bad JSON", { status: 400 });

  // Best-effort field extraction. Adjust to the actual payload shape your
  // approved TikTok product sends.
  const events: Array<{ sender_id?: string; text?: string; image_url?: string; id?: string }> =
    payload.events ?? payload.data?.events ?? [];

  for (const e of events) {
    if (!e.sender_id) continue;
    const dm = {
      id: `tt_${e.id ?? Date.now()}`,
      source: "tiktok" as const,
      senderId: e.sender_id,
      text: e.text,
      imageUrl: e.image_url,
      ts: Date.now(),
    };
    await recordIncoming(dm);
    draftReply(dm).catch((e) => console.error("draftReply failed", e));
  }

  return NextResponse.json({ ok: true });
}
