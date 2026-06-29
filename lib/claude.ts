import Anthropic from "@anthropic-ai/sdk";

let _client: Anthropic | null = null;

export function claude(): Anthropic {
  if (_client) return _client;
  if (!process.env.ANTHROPIC_API_KEY) {
    throw new Error(
      "ANTHROPIC_API_KEY is not set. Add it to .env.local (see .env.example).",
    );
  }
  _client = new Anthropic();
  return _client;
}

// Default model for agent tasks: fast, capable, cost-effective.
// Override per-call when a task needs deeper reasoning.
export const DEFAULT_MODEL = "claude-sonnet-4-6";

export type TextPart = { type: "text"; text: string };
export type ImagePart = {
  type: "image";
  source:
    | { type: "url"; url: string }
    | { type: "base64"; media_type: string; data: string };
};
export type UserContent = string | Array<TextPart | ImagePart>;

export async function ask(
  system: string,
  user: UserContent,
  opts: { maxTokens?: number; model?: string } = {},
): Promise<string> {
  const res = await claude().messages.create({
    model: opts.model ?? DEFAULT_MODEL,
    max_tokens: opts.maxTokens ?? 1024,
    system,
    messages: [
      {
        role: "user",
        content: typeof user === "string" ? user : user,
      },
    ],
  });

  return res.content
    .filter((b): b is Anthropic.TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("\n");
}
