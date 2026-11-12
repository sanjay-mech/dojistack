import React from "react";
import { FilterState } from "../types";
import { DojiCrossRow } from "./DojiIcons";

interface SummaryCardsProps {
  filters: FilterState;
  summary: {
    double: number;
    triple: number;
    four_plus: number;
    matching: number;
  };
  universeSize: number;
  expiry: string;
  onSelectMin: (min: number) => void;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({
  filters,
  summary,
  universeSize,
  expiry,
  onSelectMin,
}) => {
  const tfLabel =
    filters.tf === "75m" ? "75 minute" : filters.tf === "1W" ? "Weekly" : "Daily";
  const srcLabel =
    filters.src === "ce"
      ? "ATM Call"
      : filters.src === "pe"
        ? "ATM Put"
        : "Underlying";

  const cards = [
    {
      title: "Double doji",
      count: summary.double,
      minTarget: 2,
      crosses: 2,
      active: filters.min === 2,
    },
    {
      title: "Triple doji",
      count: summary.triple,
      minTarget: 3,
      crosses: 3,
      active: filters.min === 3,
    },
    {
      title: "4 or more",
      count: summary.four_plus,
      minTarget: 4,
      crosses: 4,
      active: filters.min >= 4,
    },
  ];

  return (
    <section
      aria-label="Summary counts"
      className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4"
    >
      {cards.map((c) => (
        <button
          key={c.title}
          type="button"
          onClick={() => onSelectMin(c.minTarget)}
          className={`group flex flex-col justify-between rounded-xl border p-4 text-left transition duration-150 ${
            c.active
              ? "border-[#f5a524] bg-[#f5a524]/10"
              : "border-[#1c232d] bg-[#0d1117] hover:border-[#f5a524]/50"
          }`}
        >
          <div className="flex w-full items-center justify-between">
            <span className="text-xs font-medium text-[#7d8794]">{c.title}</span>
            <DojiCrossRow count={c.crosses} />
          </div>
          <div className="mt-2 font-mono text-2xl font-bold text-[#e8edf3]">
            {c.count}
          </div>
          <div className="mt-1 font-mono text-[11px] text-[#7d8794]">
            stocks · tap to filter
          </div>
        </button>
      ))}

      <div className="flex flex-col justify-between rounded-xl border border-[#1c232d] bg-[#0d1117] p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-[#7d8794]">Matching now</span>
          <span className="h-2 w-2 rounded-full bg-[#2ee6a6]" />
        </div>
        <div className="mt-2 font-mono text-2xl font-bold text-[#e8edf3]">
          {summary.matching}{" "}
          <span className="text-base font-normal text-[#7d8794]">
            / {universeSize}
          </span>
        </div>
        <div className="mt-1 font-mono text-[11px] text-[#7d8794]">
          {tfLabel} · {srcLabel} · exp {expiry}
        </div>
      </div>
    </section>
  );
};
