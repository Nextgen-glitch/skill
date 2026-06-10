import { Reveal } from "./Reveal";

export function SectionHeading({
  eyebrow,
  title,
  subtitle,
  align = "left",
}: {
  eyebrow: string;
  title: React.ReactNode;
  subtitle?: string;
  align?: "left" | "center";
}) {
  return (
    <div className={align === "center" ? "mx-auto max-w-2xl text-center" : "max-w-2xl"}>
      <Reveal>
        <span className="eyebrow">{eyebrow}</span>
      </Reveal>
      <Reveal delay={0.05}>
        <h2 className="mt-4 text-balance text-3xl font-semibold tracking-tight sm:text-4xl lg:text-[2.75rem] lg:leading-[1.1]">
          {title}
        </h2>
      </Reveal>
      {subtitle && (
        <Reveal delay={0.1}>
          <p className="mt-4 text-base leading-relaxed text-secondary sm:text-lg">{subtitle}</p>
        </Reveal>
      )}
    </div>
  );
}
