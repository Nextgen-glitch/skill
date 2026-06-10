import { ShieldCheck, Truck, Wrench, RefreshCw, CreditCard, Headset } from "lucide-react";
import { SectionHeading } from "../SectionHeading";
import { Stagger, StaggerItem } from "../Reveal";

const features = [
  { icon: ShieldCheck, title: "Quality, guaranteed", body: "Every device is tested and sourced for quality, with a 12-month warranty as standard." },
  { icon: Wrench, title: "Certified repair lab", body: "In-house technicians with genuine-grade parts and a 90-day repair warranty." },
  { icon: Truck, title: "Fast, tracked delivery", body: "Island-wide shipping with real-time tracking and express options at checkout." },
  { icon: RefreshCw, title: "Easy 14-day returns", body: "Changed your mind? Return any unused item within 14 days, no fuss." },
  { icon: CreditCard, title: "Secure payments", body: "Encrypted checkout with multiple payment methods you already trust." },
  { icon: Headset, title: "Real human support", body: "Talk to people who actually know tech — before and after you buy." },
];

export function WhyUs() {
  return (
    <section className="container-px py-20 sm:py-28">
      <SectionHeading
        eyebrow="Why TechHead"
        title={<>Built on trust, <span className="text-gradient-gold">backed by service</span></>}
        subtitle="We don't just sell gadgets — we stand behind them. Here's what you get with every order."
        align="center"
      />

      <Stagger className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => {
          const Icon = f.icon;
          return (
            <StaggerItem key={f.title}>
              <div className="card-glass group h-full p-7">
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-white/[0.03] text-accent transition-colors group-hover:border-accent/50 group-hover:bg-accent/10">
                  <Icon size={22} strokeWidth={1.6} />
                </span>
                <h3 className="mt-5 text-lg font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-secondary">{f.body}</p>
              </div>
            </StaggerItem>
          );
        })}
      </Stagger>
    </section>
  );
}
