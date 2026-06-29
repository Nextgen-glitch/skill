import Anthropic from "@anthropic-ai/sdk";
import { claude, DEFAULT_MODEL } from "@/lib/claude";
import { logActivity } from "@/lib/activity";
import { integrationMode } from "@/lib/env";

export type DMSource = "facebook" | "tiktok";

export interface IncomingDM {
  id: string;
  source: DMSource;
  senderId: string;
  text?: string;
  imageUrl?: string;
  ts: number;
}

export interface DMReply {
  text: string;
  needsHumanReview: boolean;
  reason?: string;
}

const inbox: IncomingDM[] = [];
const replies: Record<string, DMReply> = {};

export async function recordIncoming(dm: IncomingDM): Promise<void> {
  inbox.unshift(dm);
  if (inbox.length > 500) inbox.length = 500;
  await logActivity(
    "inbox",
    `Incoming ${dm.source} message from ${dm.senderId}${dm.imageUrl ? " [image]" : ""}`,
  );
}

export async function getInbox(): Promise<{
  messages: IncomingDM[];
  replies: Record<string, DMReply>;
}> {
  return { messages: inbox.slice(0, 50), replies };
}

const REPLY_SYSTEM = `You are the customer-care voice of DELIX COSMETICS — a refined beauty brand.
Reply to customer DMs in a warm, helpful, on-brand tone. 1-3 sentences.

If the customer sends a photo, look at it and respond to what's actually shown:
- A product photo → identify it if you can, answer the question, recommend complementary items.
- A skin concern photo → be gentle and helpful, suggest 1-2 products. Do NOT give medical advice; recommend a dermatologist for anything beyond cosmetic concerns.
- An unclear photo → ask one clarifying question.

Escalate to a human (set needs_human_review=true) when:
- The customer is upset, asking for a refund, or reporting an adverse reaction
- The question requires order-specific data (tracking, shipping address change)
- The photo shows something concerning (severe irritation, allergic reaction)

Return JSON only:
{ "reply": "...", "needs_human_review": true|false, "reason": "..." }`;

export async function draftReply(dm: IncomingDM): Promise<DMReply> {
  const userContent: Array<
    | { type: "text"; text: string }
    | { type: "image"; source: { type: "url"; url: string } }
  > = [];

  if (dm.imageUrl) {
    userContent.push({ type: "image", source: { type: "url", url: dm.imageUrl } });
  }
  userContent.push({
    type: "text",
    text:
      `From ${dm.source} user ${dm.senderId}:\n` +
      (dm.text || "(no text — photo only)"),
  });

  const res = await claude().messages.create({
    model: DEFAULT_MODEL,
    max_tokens: 500,
    system: REPLY_SYSTEM,
    messages: [{ role: "user", content: userContent }],
  });

  const raw = res.content
    .filter((b): b is Anthropic.TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("\n");

  const match = raw.match(/\{[\s\S]*\}/);
  let reply: DMReply = {
    text: raw,
    needsHumanReview: false,
  };
  if (match) {
    try {
      const j = JSON.parse(match[0]);
      reply = {
        text: typeof j.reply === "string" ? j.reply : raw,
        needsHumanReview: Boolean(j.needs_human_review),
        reason: typeof j.reason === "string" ? j.reason : undefined,
      };
    } catch {}
  }

  replies[dm.id] = reply;
  await logActivity(
    "inbox",
    `Drafted reply for ${dm.id}${reply.needsHumanReview ? " (needs review)" : ""}`,
  );
  return reply;
}

export async function sendReply(
  dm: IncomingDM,
  text: string,
): Promise<{ id: string }> {
  if (integrationMode() === "mock") {
    const id = `mock_reply_${Date.now()}`;
    await logActivity("inbox", `[mock] Sent reply to ${dm.senderId}: ${id}`);
    return { id };
  }

  if (dm.source === "facebook") {
    // POST https://graph.facebook.com/v21.0/me/messages?access_token=PAGE_TOKEN
    const token = process.env.META_PAGE_ACCESS_TOKEN;
    if (!token) throw new Error("META_PAGE_ACCESS_TOKEN not set");
    const r = await fetch(
      `https://graph.facebook.com/v21.0/me/messages?access_token=${token}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          recipient: { id: dm.senderId },
          message: { text },
          messaging_type: "RESPONSE",
        }),
      },
    );
    if (!r.ok) throw new Error(`Meta ${r.status}: ${await r.text()}`);
    const data = await r.json();
    return { id: data.message_id ?? `fb_${Date.now()}` };
  }

  // TikTok messaging API requires special approval and the endpoint shape
  // depends on which TikTok product (Business / Shop / Direct Messages) you
  // were approved for. Fill in once you have credentials.
  throw new Error(
    "Live TikTok reply not implemented — requires TikTok business messaging access.",
  );
}
