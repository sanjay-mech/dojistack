import React, { useState } from "react";

type StoryPhase = "trend" | "coil" | "resolution";

interface HeroProps {
  universeSize: number;
}

export const Hero: React.FC<HeroProps> = ({ universeSize }) => {
  const [phase, setPhase] = useState<StoryPhase>("coil");

  const trendOpacity = phase === "trend" ? 1 : 0.45;
  const coilOpacity = phase === "coil" ? 1 : 0.55;
  const resOpacity = phase === "resolution" ? 1 : 0.45;

  return (
    <section className="hero-grid-bg border-b border-[#1c232d]/80">
      <div className="mx-auto grid max-w-[1400px] grid-cols-1 items-center gap-8 px-4 py-10 sm:px-6 lg:grid-cols-12 lg:py-12">
        {/* Left column */}
        <div className="lg:col-span-7">
          <p className="mb-3 font-mono text-[11px] font-semibold uppercase tracking-[0.18em] text-[#f5a524]">
            MULTIPLE DOJI SCREENER
          </p>
          <h1 className="font-display text-4xl font-bold leading-[1.03] tracking-[-0.035em] text-[#e8edf3] sm:text-5xl lg:text-[56px]">
            Find the coil
            <br />
            before the move.
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-relaxed text-[#7d8794] sm:text-[15px]">
            Scans {universeSize} NSE F&amp;O stocks — and their {universeSize} ATM calls and{" "}
            {universeSize} ATM puts ({universeSize * 3} charts) — for back-to-back doji candles on
            the 75-minute, daily and weekly charts. Double, triple and longer streaks mark
            indecision that often resolves with a sharp breakout.
          </p>
        </div>

        {/* Right column: Animated Triple Doji Story Card */}
        <div className="lg:col-span-5">
          <div className="rounded-2xl border border-[#1c232d] bg-[#0d1117] p-4 shadow-2xl shadow-black/50">
            <div className="mb-3 flex items-center justify-between">
              <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-[#7d8794]">
                TRIPLE DOJI · 75m
              </span>
              <span className="font-mono text-[11px] font-semibold text-[#2ee6a6]">
                breakout ↑
              </span>
            </div>

            <div className="rounded-xl border border-[#1c232d]/80 bg-[#07090d] p-3">
              <svg
                viewBox="0 0 380 175"
                className="h-44 w-full"
                role="img"
                aria-label="Triple Doji coil followed by upward breakout"
              >
                {/* Faint horizontal reference lines */}
                <line x1="12" y1="35" x2="368" y2="35" stroke="#1c232d" strokeWidth="1" strokeDasharray="2 4" />
                <line x1="12" y1="88" x2="368" y2="88" stroke="#1c232d" strokeWidth="1" strokeDasharray="2 4" />
                <line x1="12" y1="140" x2="368" y2="140" stroke="#1c232d" strokeWidth="1" strokeDasharray="2 4" />

                {/* Phase 1: Trend candles */}
                <g style={{ opacity: trendOpacity, transition: "opacity 200ms ease" }}>
                  {/* Bar 1 */}
                  <line x1="34" y1="118" x2="34" y2="150" stroke="#2ee6a6" strokeWidth="1.6" />
                  <rect x="27" y="124" width="14" height="20" rx="1.5" fill="#2ee6a6" />
                  {/* Bar 2 */}
                  <line x1="66" y1="100" x2="66" y2="134" stroke="#2ee6a6" strokeWidth="1.6" />
                  <rect x="59" y="106" width="14" height="21" rx="1.5" fill="#2ee6a6" />
                  {/* Bar 3 */}
                  <line x1="98" y1="82" x2="98" y2="118" stroke="#2ee6a6" strokeWidth="1.6" />
                  <rect x="91" y="88" width="14" height="22" rx="1.5" fill="#2ee6a6" />
                  {/* Bar 4 */}
                  <line x1="130" y1="68" x2="130" y2="104" stroke="#2ee6a6" strokeWidth="1.6" />
                  <rect x="123" y="75" width="14" height="19" rx="1.5" fill="#2ee6a6" />
                </g>

                {/* Break above & Break below dashed lines */}
                <line
                  x1="154"
                  y1="62"
                  x2="362"
                  y2="62"
                  stroke="#2ee6a6"
                  strokeWidth="1.2"
                  strokeDasharray="4 4"
                  opacity={phase === "trend" ? 0.35 : 0.85}
                />
                <text x="292" y="56" fill="#2ee6a6" fontSize="9" fontFamily="JetBrains Mono, monospace">
                  break above
                </text>

                <line
                  x1="154"
                  y1="98"
                  x2="362"
                  y2="98"
                  stroke="#ff4d5e"
                  strokeWidth="1.2"
                  strokeDasharray="4 4"
                  opacity={phase === "trend" ? 0.35 : 0.85}
                />
                <text x="292" y="110" fill="#ff4d5e" fontSize="9" fontFamily="JetBrains Mono, monospace">
                  break below
                </text>

                {/* Phase 2: 3x Doji Coil inside dashed amber rectangle */}
                <g style={{ opacity: coilOpacity, transition: "opacity 200ms ease" }}>
                  <rect
                    x="154"
                    y="62"
                    width="102"
                    height="36"
                    rx="4"
                    fill="#f5a524"
                    fillOpacity="0.06"
                    stroke="#f5a524"
                    strokeWidth="1.4"
                    strokeDasharray="4 3"
                  />
                  {/* Doji 1 */}
                  <line x1="173" y1="66" x2="173" y2="94" stroke="#f5a524" strokeWidth="1.8" />
                  <rect x="166" y="78" width="14" height="3" rx="1" fill="#f5a524" />
                  {/* Doji 2 */}
                  <line x1="205" y1="68" x2="205" y2="92" stroke="#f5a524" strokeWidth="1.8" />
                  <rect x="198" y="79" width="14" height="2.5" rx="1" fill="#f5a524" />
                  {/* Doji 3 */}
                  <line x1="237" y1="65" x2="237" y2="95" stroke="#f5a524" strokeWidth="1.8" />
                  <rect x="230" y="78.5" width="14" height="2.8" rx="1" fill="#f5a524" />
                </g>

                {/* Phase 3: Breakout candle */}
                <g style={{ opacity: resOpacity, transition: "opacity 200ms ease" }}>
                  <line x1="280" y1="24" x2="280" y2="82" stroke="#2ee6a6" strokeWidth="1.8" />
                  <rect x="272" y="30" width="16" height="44" rx="2" fill="#2ee6a6" />
                </g>
              </svg>
            </div>

            <div className="mt-3 grid grid-cols-3 gap-2">
              {(
                [
                  { id: "trend", label: "Trend" },
                  { id: "coil", label: "3× doji coil" },
                  { id: "resolution", label: "Resolution" },
                ] as const
              ).map((tab) => {
                const active = phase === tab.id;
                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setPhase(tab.id)}
                    className={`rounded-lg border px-2.5 py-1.5 font-mono text-[11px] font-medium transition duration-150 ${
                      active
                        ? "border-[#f5a524] bg-[#f5a524]/15 text-[#f5a524]"
                        : "border-[#1c232d] bg-[#07090d] text-[#7d8794] hover:text-[#e8edf3]"
                    }`}
                  >
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
