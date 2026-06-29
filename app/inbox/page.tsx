"use client";

import { useEffect, useState } from "react";

interface DM {
  id: string;
  source: "facebook" | "tiktok";
  senderId: string;
  text?: string;
  imageUrl?: string;
  ts: number;
}

interface Reply {
  text: string;
  needsHumanReview: boolean;
  reason?: string;
}

export default function InboxPage() {
  const [messages, setMessages] = useState<DM[]>([]);
  const [replies, setReplies] = useState<Record<string, Reply>>({});
  const [working, setWorking] = useState<string | null>(null);

  async function load() {
    const r = await fetch("/api/inbox");
    const data = await r.json();
    setMessages(data.messages);
    setReplies(data.replies);
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  async function draft(dm: DM) {
    setWorking(dm.id);
    await fetch("/api/inbox/draft", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: dm.id }),
    });
    await load();
    setWorking(null);
  }

  async function send(dm: DM) {
    const r = replies[dm.id];
    if (!r) return;
    setWorking(dm.id);
    await fetch("/api/inbox/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: dm.id, text: r.text }),
    });
    setWorking(null);
    await load();
  }

  async function seed() {
    await fetch("/api/inbox/seed", { method: "POST" });
    await load();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-3xl">DM Inbox</h2>
        <button
          onClick={seed}
          className="text-xs px-3 py-1 border border-delix-ink rounded"
        >
          + Seed sample messages
        </button>
      </div>

      {messages.length === 0 ? (
        <p className="text-sm text-delix-ink/60">
          No messages yet. Use Seed to create sample ones, or point Facebook /
          TikTok webhooks at <code>/api/webhooks/facebook</code> and{" "}
          <code>/api/webhooks/tiktok</code>.
        </p>
      ) : (
        <ul className="space-y-3">
          {messages.map((dm) => {
            const reply = replies[dm.id];
            return (
              <li
                key={dm.id}
                className="bg-white rounded-xl border border-delix-rose/20 p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="text-xs text-delix-ink/50 mb-1">
                      <span className="uppercase tracking-widest">
                        {dm.source}
                      </span>{" "}
                      &middot; from {dm.senderId} &middot;{" "}
                      {new Date(dm.ts).toLocaleString()}
                    </div>
                    {dm.imageUrl && (
                      <img
                        src={dm.imageUrl}
                        alt=""
                        className="max-w-[160px] rounded mb-2"
                      />
                    )}
                    {dm.text && <p className="text-sm">{dm.text}</p>}
                  </div>
                  <div className="flex flex-col gap-2 shrink-0">
                    <button
                      onClick={() => draft(dm)}
                      disabled={working === dm.id}
                      className="text-xs px-3 py-1 border border-delix-ink rounded disabled:opacity-40"
                    >
                      {reply ? "Re-draft" : "Draft reply"}
                    </button>
                    {reply && !reply.needsHumanReview && (
                      <button
                        onClick={() => send(dm)}
                        disabled={working === dm.id}
                        className="text-xs px-3 py-1 bg-delix-ink text-white rounded disabled:opacity-40"
                      >
                        Send
                      </button>
                    )}
                  </div>
                </div>

                {reply && (
                  <div
                    className={`mt-3 border-t pt-3 text-sm ${
                      reply.needsHumanReview
                        ? "border-red-300 bg-red-50/40 -mx-4 -mb-4 px-4 pb-4 rounded-b-xl"
                        : "border-delix-rose/20"
                    }`}
                  >
                    {reply.needsHumanReview && (
                      <p className="text-xs text-red-700 mb-1">
                        ⚠ Needs human review{reply.reason ? `: ${reply.reason}` : ""}
                      </p>
                    )}
                    <p className="whitespace-pre-wrap">{reply.text}</p>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
