import { NextResponse } from "next/server";
import crypto from "crypto";
import { recordIncoming, draftReply } from "@/lib/agents/inbox";

// Meta webhook verification (GET) — point your Facebook app's webhook at this URL.
export async function GET(req: Request) {
  const url = new URL(req.url);
  const mode = url.searchParams.get("hub.mode");
  const token = url.searchParams.get("hub.verify_token");
  const challenge = url.searchParams.get("hub.challenge");

  if (
    mode === "subscribe" &&
    token &&
    token === process.env.META_VERIFY_TOKEN
  ) {
    return new NextResponse(challenge ?? "", { status: 200 });
  }
  return new NextResponse("Forbidden", { status: 403 });
}

// Meta sends message events as POST. We verify the X-Hub-Signature-256 header.
export async function POST(req: Request) {
  const body = await req.text();
  const signature = req.headers.get("x-hub-signature-256");
  const appSecret = process.env.META_APP_SECRET;

  if (appSecret && signature) {
    const expected =
      "sha256=" +
      crypto.createHmac("sha256", appSecret).update(body).digest("hex");
    if (
      signature.length !== expected.length ||
      !crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected))
    ) {
      return new NextResponse("Invalid signature", { status: 401 });
    }
  }

  let payload: any;
  try {
    payload = JSON.parse(body);
  } catch {
    return new NextResponse("Bad JSON", { status: 400 });
  }

  // Meta payload shape:
  // { object: "page", entry: [{ messaging: [{ sender: {id}, message: {text, attachments?} }] }] }
  for (const entry of payload.entry ?? []) {
    for (const event of entry.messaging ?? []) {
      const senderId: string | undefined = event.sender?.id;
      const text: string | undefined = event.message?.text;
      const imageUrl: string | undefined = event.message?.attachments?.find(
        (a: { type: string }) => a.type === "image",
      )?.payload?.url;
      if (!senderId) continue;

      const dm = {
        id: `fb_${event.message?.mid ?? Date.now()}`,
        source: "facebook" as const,
        senderId,
        text,
        imageUrl,
        ts: Date.now(),
      };
      await recordIncoming(dm);
      // Draft a reply in the background — the dashboard will show it.
      // (For production, push to a queue rather than awaiting in the handler.)
      draftReply(dm).catch((e) => console.error("draftReply failed", e));
    }
  }

  return NextResponse.json({ ok: true });
}
