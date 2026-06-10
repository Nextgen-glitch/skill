export function Logo({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${className}`}>
      <svg width="30" height="30" viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <rect x="1" y="1" width="30" height="30" rx="9" stroke="url(#lg)" strokeWidth="1.5" />
        <path
          d="M9 11.5h14M16 11.5V23"
          stroke="url(#lg)"
          strokeWidth="2.4"
          strokeLinecap="round"
        />
        <circle cx="16" cy="11.5" r="2.4" fill="#0c0a09" stroke="url(#lg)" strokeWidth="1.6" />
        <defs>
          <linearGradient id="lg" x1="2" y1="2" x2="30" y2="30" gradientUnits="userSpaceOnUse">
            <stop stopColor="#f0b357" />
            <stop offset="1" stopColor="#d4922a" />
          </linearGradient>
        </defs>
      </svg>
      <span className="text-[17px] font-semibold tracking-tight">
        Tech<span className="text-gradient-gold">Head</span>
      </span>
    </span>
  );
}
