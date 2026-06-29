import Link from "next/link";

type Accent = "rose" | "gold" | "ink";

const accentClasses: Record<Accent, string> = {
  rose: "border-delix-rose/60 hover:border-delix-rose",
  gold: "border-delix-gold/60 hover:border-delix-gold",
  ink: "border-delix-ink/40 hover:border-delix-ink",
};

export default function AgentCard({
  name,
  href,
  accent,
  description,
  actions,
}: {
  name: string;
  href: string;
  accent: Accent;
  description: string;
  actions: string[];
}) {
  return (
    <Link
      href={href}
      className={`block bg-white rounded-2xl border-2 ${accentClasses[accent]} p-5 transition`}
    >
      <h3 className="font-display text-xl mb-2">{name}</h3>
      <p className="text-sm text-delix-ink/70 mb-4">{description}</p>
      <ul className="text-xs text-delix-ink/60 space-y-1">
        {actions.map((a) => (
          <li key={a} className="flex items-center gap-2">
            <span className="inline-block w-1 h-1 rounded-full bg-delix-ink/40" />
            {a}
          </li>
        ))}
      </ul>
    </Link>
  );
}
