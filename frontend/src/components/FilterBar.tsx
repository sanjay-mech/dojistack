import React, { useEffect, useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import { FilterState, ScanSource, SectorOption, Timeframe } from "../types";

interface FilterBarProps {
  filters: FilterState;
  sectors: SectorOption[];
  onChange: (patch: Partial<FilterState>) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  sectors,
  onChange,
}) => {
  const [searchDraft, setSearchDraft] = useState(filters.q);

  useEffect(() => {
    setSearchDraft(filters.q);
  }, [filters.q]);

  useEffect(() => {
    const t = setTimeout(() => {
      if (searchDraft !== filters.q) {
        onChange({ q: searchDraft });
      }
    }, 250);
    return () => clearTimeout(t);
  }, [searchDraft, filters.q, onChange]);

  const tfOptions: { value: Timeframe; label: string }[] = [
    { value: "75m", label: "75 minute" },
    { value: "1D", label: "Daily" },
    { value: "1W", label: "Weekly" },
  ];

  const srcOptions: { value: ScanSource; label: string }[] = [
    { value: "stock", label: "Underlying" },
    { value: "ce", label: "ATM Call" },
    { value: "pe", label: "ATM Put" },
  ];

  const minOptions = [2, 3, 4, 5];

  return (
    <section
      aria-label="Screener filters"
      className="rounded-2xl border border-[#1c232d] bg-[#0d1117] p-4"
    >
      <div className="flex flex-wrap items-end gap-4">
        {/* 1. TIMEFRAME */}
        <div className="flex flex-col gap-1.5">
          <span className="font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-[#7d8794]">
            TIMEFRAME
          </span>
          <div
            role="group"
            aria-label="Timeframe"
            className="inline-flex rounded-lg border border-[#1c232d] bg-[#07090d] p-0.5"
          >
            {tfOptions.map((opt) => {
              const active = filters.tf === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => onChange({ tf: opt.value })}
                  className={`rounded-md px-2.5 py-1.5 font-mono text-xs transition duration-150 ${
                    active
                      ? "bg-[#f5a524] font-semibold text-[#07090d]"
                      : "text-[#7d8794] hover:text-[#e8edf3]"
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* 2. SCAN CHART OF */}
        <div className="flex flex-col gap-1.5">
          <span className="font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-[#7d8794]">
            SCAN CHART OF
          </span>
          <div
            role="group"
            aria-label="Scan chart of"
            className="inline-flex rounded-lg border border-[#1c232d] bg-[#07090d] p-0.5"
          >
            {srcOptions.map((opt) => {
              const active = filters.src === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => onChange({ src: opt.value })}
                  className={`rounded-md px-2.5 py-1.5 font-mono text-xs transition duration-150 ${
                    active
                      ? "bg-[#f5a524] font-semibold text-[#07090d]"
                      : "text-[#7d8794] hover:text-[#e8edf3]"
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* 3. CONSECUTIVE DOJIS */}
        <div className="flex flex-col gap-1.5">
          <span className="font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-[#7d8794]">
            CONSECUTIVE DOJIS
          </span>
          <div
            role="group"
            aria-label="Consecutive dojis"
            className="inline-flex rounded-lg border border-[#1c232d] bg-[#07090d] p-0.5"
          >
            {minOptions.map((m) => {
              const active = filters.min === m;
              return (
                <button
                  key={m}
                  type="button"
                  onClick={() => onChange({ min: m })}
                  className={`rounded-md px-2.5 py-1.5 font-mono text-xs transition duration-150 ${
                    active
                      ? "bg-[#f5a524] font-semibold text-[#07090d]"
                      : "text-[#7d8794] hover:text-[#e8edf3]"
                  }`}
                >
                  {m}+
                </button>
              );
            })}
          </div>
        </div>

        {/* 4. DOJI BODY <= X% OF RANGE */}
        <div className="flex min-w-[180px] flex-1 flex-col gap-1.5">
          <label
            htmlFor="bodySlider"
            className="font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-[#7d8794]"
          >
            DOJI BODY ≤ <span className="text-[#f5a524]">{filters.body}%</span> OF RANGE
          </label>
          <div className="flex h-[34px] items-center gap-2 rounded-lg border border-[#1c232d] bg-[#07090d] px-3">
            <SlidersHorizontal className="h-3.5 w-3.5 shrink-0 text-[#f5a524]" />
            <input
              id="bodySlider"
              type="range"
              min={1}
              max={30}
              step={1}
              value={filters.body}
              onChange={(e) => onChange({ body: Number(e.target.value) })}
              className="amber-slider w-full"
            />
          </div>
        </div>

        {/* 5. SECTOR */}
        <div className="flex min-w-[155px] flex-col gap-1.5">
          <label
            htmlFor="sectorSelect"
            className="font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-[#7d8794]"
          >
            SECTOR
          </label>
          <select
            id="sectorSelect"
            value={filters.sector}
            onChange={(e) => onChange({ sector: e.target.value })}
            className="h-[34px] rounded-lg border border-[#1c232d] bg-[#07090d] px-2.5 text-xs text-[#e8edf3] outline-none transition duration-150 focus:border-[#f5a524]"
          >
            <option value="all">All sectors</option>
            {sectors.map((sec) => (
              <option key={sec.slug} value={sec.slug}>
                {sec.label}
              </option>
            ))}
          </select>
        </div>

        {/* 6. SYMBOL */}
        <div className="flex min-w-[190px] flex-1 flex-col gap-1.5">
          <label
            htmlFor="symbolSearch"
            className="font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-[#7d8794]"
          >
            SYMBOL
          </label>
          <div className="relative flex items-center">
            <Search className="pointer-events-none absolute left-2.5 h-3.5 w-3.5 text-[#7d8794]" />
            <input
              id="symbolSearch"
              type="search"
              value={searchDraft}
              onChange={(e) => setSearchDraft(e.target.value)}
              placeholder="RELIANCE, TCS…"
              className="h-[34px] w-full rounded-lg border border-[#1c232d] bg-[#07090d] pl-8 pr-3 font-mono text-xs text-[#e8edf3] placeholder-[#7d8794]/70 outline-none transition duration-150 focus:border-[#f5a524]"
            />
          </div>
        </div>
      </div>
    </section>
  );
};
