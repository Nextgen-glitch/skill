import type { ActivityEntry } from "@/lib/activity";

export default function ActivityFeed({ items }: { items: ActivityEntry[] }) {
  if (items.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-delix-rose/20 p-6 text-sm text-delix-ink/50">
        No activity yet. Trigger an agent to see entries here.
      </div>
    );
  }

  return (
    <ul className="bg-white rounded-xl border border-delix-rose/20 divide-y divide-delix-rose/10">
      {items.map((item) => (
        <li key={item.id} className="px-5 py-3 flex items-start gap-4">
          <span className="text-xs font-mono text-delix-ink/40 w-16 shrink-0">
            {item.agent}
          </span>
          <span className="text-sm flex-1">{item.message}</span>
          <span className="text-xs text-delix-ink/40">
            {new Date(item.ts).toLocaleTimeString()}
          </span>
        </li>
      ))}
    </ul>
  );
}
