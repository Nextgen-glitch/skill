"use client";

import { useState } from "react";

type Platform = "facebook" | "instagram" | "tiktok";

interface Draft {
  platform: Platform;
  caption: string;
  hashtags: string[];
}

export default function SocialPage() {
  const [topic, setTopic] = useState("");
  const [productName, setProductName] = useState("");
  const [platforms, setPlatforms] = useState<Platform[]>([
    "facebook",
    "instagram",
    "tiktok",
  ]);
  const [tone, setTone] = useState<"elegant" | "playful" | "expert">("elegant");
  const [loading, setLoading] = useState(false);
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [err, setErr] = useState<string | null>(null);

  const toggle = (p: Platform) =>
    setPlatforms((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p],
    );

  async function generate() {
    setLoading(true);
    setErr(null);
    setDrafts([]);
    try {
      const r = await fetch("/api/social/draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, productName, platforms, tone }),
      });
      if (!r.ok) throw new Error(await r.text());
      const data = await r.json();
      setDrafts(data.drafts);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  async function publish(d: Draft) {
    const r = await fetch("/api/social/publish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(d),
    });
    if (!r.ok) {
      alert(await r.text());
      return;
    }
    const data = await r.json();
    alert(`Published: ${data.id}`);
  }

  return (
    <div className="space-y-6">
      <h2 className="font-display text-3xl">Social Media Poster</h2>
      <div className="bg-white rounded-2xl border border-delix-rose/30 p-6 space-y-4">
        <div>
          <label className="block text-sm mb-1">Topic / angle</label>
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. our new hydrating rose serum"
            className="w-full px-3 py-2 border border-delix-rose/30 rounded-lg"
          />
        </div>
        <div>
          <label className="block text-sm mb-1">Product name (optional)</label>
          <input
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            className="w-full px-3 py-2 border border-delix-rose/30 rounded-lg"
          />
        </div>
        <div className="flex gap-3 items-center">
          <span className="text-sm">Platforms:</span>
          {(["facebook", "instagram", "tiktok"] as Platform[]).map((p) => (
            <label key={p} className="text-sm flex items-center gap-1">
              <input
                type="checkbox"
                checked={platforms.includes(p)}
                onChange={() => toggle(p)}
              />
              {p}
            </label>
          ))}
        </div>
        <div className="flex gap-3 items-center">
          <span className="text-sm">Tone:</span>
          {(["elegant", "playful", "expert"] as const).map((t) => (
            <label key={t} className="text-sm flex items-center gap-1">
              <input
                type="radio"
                checked={tone === t}
                onChange={() => setTone(t)}
              />
              {t}
            </label>
          ))}
        </div>
        <button
          onClick={generate}
          disabled={loading || !topic}
          className="px-4 py-2 bg-delix-ink text-white rounded-lg disabled:opacity-40"
        >
          {loading ? "Drafting..." : "Generate drafts"}
        </button>
        {err && <p className="text-sm text-red-600">{err}</p>}
      </div>

      {drafts.length > 0 && (
        <div className="space-y-4">
          {drafts.map((d) => (
            <div
              key={d.platform}
              className="bg-white rounded-xl border border-delix-rose/20 p-5"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs uppercase tracking-widest text-delix-gold">
                  {d.platform}
                </span>
                <button
                  onClick={() => publish(d)}
                  className="text-xs px-3 py-1 border border-delix-ink rounded hover:bg-delix-ink hover:text-white"
                >
                  Publish
                </button>
              </div>
              <p className="whitespace-pre-wrap text-sm">{d.caption}</p>
              {d.hashtags.length > 0 && (
                <p className="mt-2 text-xs text-delix-ink/60">
                  {d.hashtags.map((h) => `#${h.replace(/^#/, "")}`).join(" ")}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
