import React from "react";

export const DojiCrossIcon: React.FC<{ className?: string }> = ({
  className = "w-3 h-3 text-[#f5a524]",
}) => (
  <svg
    viewBox="0 0 12 16"
    fill="none"
    className={className}
    aria-hidden="true"
  >
    <line x1="6" y1="1" x2="6" y2="15" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    <line x1="2.2" y1="8" x2="9.8" y2="8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

export const DojiCrossRow: React.FC<{ count: number; max?: number }> = ({
  count,
  max = 5,
}) => {
  const n = Math.min(Math.max(1, count), max);
  return (
    <span className="inline-flex items-center gap-0.5" aria-hidden="true">
      {Array.from({ length: n }).map((_, idx) => (
        <DojiCrossIcon key={idx} className="w-2.5 h-3.5 text-[#f5a524]" />
      ))}
    </span>
  );
};
