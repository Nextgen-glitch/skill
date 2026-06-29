import { ask } from "@/lib/claude";
import { logActivity } from "@/lib/activity";
import { integrationMode } from "@/lib/env";

export type Platform = "facebook" | "instagram" | "tiktok";

export interface DraftPostInput {
  topic: string;
  platforms: Platform[];
  tone?: "elegant" | "playful" | "expert";
  productName?: string;
}

export interface DraftedPost {
  platform: Platform;
  caption: string;
  hashtags: string[];
}

const SYSTEM = `You are the social media voice for DELIX COSMETICS, a refined beauty brand.
Write captions that feel warm, confident, and product-focused.

Rules per platform:
- facebook: 2-3 short paragraphs, conversational. End with a soft CTA.
- instagram: 1-2 lines + a poetic hook. 5-8 hashtags.
- tiktok: punchy, under 150 chars. Hook in the first 6 words.

Return JSON only:
{ "caption": "...", "hashtags": ["..."] }`;

export async function draftPosts(input: DraftPostInput): Promise<DraftedPost[]> {
  const tone = input.tone ?? "elegant";
  const drafts: DraftedPost[] = [];

  for (const platform of input.platforms) {
    const userPrompt = [
      `Platform: ${platform}`,
      `Tone: ${tone}`,
      input.productName ? `Product: ${input.productName}` : null,
      `Topic: ${input.topic}`,
    ]
      .filter(Boolean)
      .join("\n");

    const raw = await ask(SYSTEM, userPrompt, { maxTokens: 600 });
    const parsed = safeParse(raw);
    drafts.push({
      platform,
      caption: parsed?.caption ?? raw,
      hashtags: parsed?.hashtags ?? [],
    });
  }

  await logActivity(
    "social",
    `Drafted ${drafts.length} post(s) for ${input.platforms.join(", ")}`,
    { topic: input.topic },
  );
  return drafts;
}

function safeParse(s: string): { caption: string; hashtags: string[] } | null {
  const match = s.match(/\{[\s\S]*\}/);
  if (!match) return null;
  try {
    const j = JSON.parse(match[0]);
    if (typeof j.caption === "string" && Array.isArray(j.hashtags)) return j;
  } catch {}
  return null;
}

// Publish adapter. Mock by default; flip INTEGRATION_MODE=live and wire real API calls.
export async function publishPost(
  platform: Platform,
  caption: string,
  hashtags: string[],
): Promise<{ id: string; url?: string }> {
  if (integrationMode() === "mock") {
    const id = `mock_${platform}_${Date.now()}`;
    await logActivity("social", `[mock] Published to ${platform}: ${id}`);
    return { id, url: `https://example.com/${platform}/${id}` };
  }

  // LIVE: fill in the platform-specific Graph API / TikTok API call here.
  // For Facebook page posts:
  //   POST https://graph.facebook.com/v21.0/{page-id}/feed
  //   { message, access_token }
  // For TikTok content posting (requires app review):
  //   POST https://open.tiktokapis.com/v2/post/publish/inbox/video/init/
  throw new Error(
    `Live publishing for ${platform} not implemented. Set INTEGRATION_MODE=mock or wire the API call.`,
  );
}
