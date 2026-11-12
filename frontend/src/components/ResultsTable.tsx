import React, { useMemo, useState } from "react";
import { ArrowDown, ArrowUp, ChevronRight, Download } from "lucide-react";
import { ScreenerRow, Timeframe } from "../types";
import { DojiCrossRow } from "./DojiIcons";

interface ResultsTableProps {
  rows: ScreenerRow[];
  tf: Timeframe;
  loading: boolean;
  onRowClick: (symbol: string) => void;
}

type SortKey =
  | "symbol"
  | "ltp"
  | "streak"
  | "coil_range_pct"
  | "atm_strike"
  | "last_bar";

function patternLabel(streak: number): string {
  if (streak === 2) return "Double doji";
  if (streak === 3) return "Triple doji";
  if (streak === 4) return "Quadruple doji";
  if (streak === 5) return "Quintuple doji";
  return `${streak}× doji`;
}

function formatLastBar(raw: string): string {
  if (!raw) return "—";
  const datePart = raw.slice(0, 10);
  const dt = new Date(`${datePart}T00:00:00`);
  if (Number.isNaN(dt.getTime())) return raw;
  const day = dt.getDate();
  const mon = dt.toLocaleString("en-US", { month: "short" });
  const yr = String(dt.getFullYear()).slice(-2);
  const timePart = raw.length > 10 ? ` ${raw.slice(11, 16)}` : "";
  return `${day} ${mon} '${yr}${timePart}`;
}

export const ResultsTable: React.FC<ResultsTableProps> = ({
  rows,
  tf,
  loading,
  onRowClick,
}) => {
  const [sortKey, setSortKey] = useState<SortKey>("streak");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const tfHeader =
    tf === "75m" ? "75M" : tf === "1W" ? "WEEKLY" : "DAILY";

  const sortedRows = useMemo(() => {
    const copy = [...rows];
    copy.sort((a, b) => {
      if (sortKey === "streak") {
        const diff =
          sortDir === "desc" ? b.streak - a.streak : a.streak - b.streak;
        if (diff !== 0) return diff;
        return a.coil_range_pct - b.coil_range_pct;
      }
      const va = a[sortKey];
      const vb = b[sortKey];
      if (typeof va === "string" && typeof vb === "string") {
        return sortDir === "asc"
          ? va.localeCompare(vb)
          : vb.localeCompare(va);
      }
      const numA = Number(va ?? 0);
      const numB = Number(vb ?? 0);
      return sortDir === "asc" ? numA - numB : numB - numA;
    });
    return copy;
  }, [rows, sortKey, sortDir]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "desc" ? "asc" : "desc"));
    } else {
      setSortKey(key);
      setSortDir(key === "symbol" || key === "coil_range_pct" ? "asc" : "desc");
    }
  };

  const downloadCsv = () => {
    if (!sortedRows.length) return;
    const headers = [
      "Symbol",
      "Name",
      "Sector",
      "LTP",
      "ChangePct",
      "Streak",
      "Pattern",
      "CoilRangePct",
      "BreakAbove",
      "BreakBelow",
      "ATMStrike",
      "CELTP",
      "PELTP",
      "STKStreak",
      "CEStreak",
      "PEStreak",
      "LastBar",
    ];
    const lines = [headers.join(",")];
    sortedRows.forEach((r) => {
      lines.push(
        [
          r.symbol,
          `"${r.name.replace(/"/g, '""')}"`,
          `"${r.sector}"`,
          r.ltp.toFixed(2),
          r.change_pct.toFixed(2),
          r.streak,
          `"${patternLabel(r.streak)}"`,
          r.coil_range_pct.toFixed(2),
          r.break_above.toFixed(2),
          r.break_below.toFixed(2),
          r.atm_strike,
          r.ce_ltp !== null ? r.ce_ltp.toFixed(2) : "",
          r.pe_ltp !== null ? r.pe_ltp.toFixed(2) : "",
          r.stk_streak,
          r.ce_streak,
          r.pe_streak,
          `"${r.last_bar}"`,
        ].join(",")
      );
    });
    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `dojistack-${tf}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const SortIcon = ({ col }: { col: SortKey }) => {
    if (sortKey !== col) return null;
    return sortDir === "desc" ? (
      <ArrowDown className="ml-1 inline h-3 w-3 text-[#f5a524]" />
    ) : (
      <ArrowUp className="ml-1 inline h-3 w-3 text-[#f5a524]" />
    );
  };

  return (
    <section className="rounded-2xl border border-[#1c232d] bg-[#0d1117]">
      {/* Table toolbar */}
      <div className="flex items-center justify-between border-b border-[#1c232d] px-4 py-3">
        <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-[#7d8794]">
          SCREENER RESULTS · {sortedRows.length} STOCKS
        </span>
        <button
          type="button"
          onClick={downloadCsv}
          disabled={!sortedRows.length}
          className="inline-flex items-center gap-1.5 rounded-lg border border-[#1c232d] bg-[#07090d] px-3 py-1.5 font-mono text-[11px] font-medium text-[#e8edf3] transition duration-150 hover:border-[#f5a524]/50 disabled:opacity-40"
        >
          <Download className="h-3.5 w-3.5 text-[#f5a524]" />
          Download CSV
        </button>
      </div>

      {/* Skeleton loading */}
      {loading ? (
        <div className="space-y-2.5 p-4">
          {Array.from({ length: 6 }).map((_, idx) => (
            <div
              key={idx}
              className="h-14 animate-pulse rounded-xl border border-[#1c232d] bg-[#07090d]/80"
            />
          ))}
        </div>
      ) : !sortedRows.length ? (
        <div className="px-6 py-16 text-center">
          <p className="font-display text-lg font-semibold text-[#e8edf3]">
            No stocks match
          </p>
          <p className="mt-1 font-mono text-xs text-[#7d8794]">
            Try lowering Consecutive Dojis or raising Doji Body % of range.
          </p>
        </div>
      ) : (
        <>
          {/* Desktop / Tablet Table */}
          <div className="hidden overflow-x-auto md:block">
            <table className="w-full border-collapse text-left">
              <thead className="sticky top-0 z-10 bg-[#0d1117] font-mono text-[10px] font-semibold uppercase tracking-[0.1em] text-[#7d8794]">
                <tr className="border-b border-[#1c232d]">
                  <th
                    onClick={() => toggleSort("symbol")}
                    className="cursor-pointer px-4 py-3 hover:text-[#e8edf3]"
                  >
                    STOCK <SortIcon col="symbol" />
                  </th>
                  <th
                    onClick={() => toggleSort("ltp")}
                    className="cursor-pointer px-3 py-3 text-right hover:text-[#e8edf3]"
                  >
                    LTP <SortIcon col="ltp" />
                  </th>
                  <th
                    onClick={() => toggleSort("streak")}
                    className="cursor-pointer px-3 py-3 hover:text-[#e8edf3]"
                  >
                    PATTERN ({tfHeader}) <SortIcon col="streak" />
                  </th>
                  <th
                    onClick={() => toggleSort("coil_range_pct")}
                    className="cursor-pointer px-3 py-3 text-right hover:text-[#e8edf3]"
                  >
                    COIL RANGE <SortIcon col="coil_range_pct" />
                  </th>
                  <th className="px-3 py-3 text-right">BREAK ABOVE / BELOW</th>
                  <th
                    onClick={() => toggleSort("atm_strike")}
                    className="cursor-pointer px-3 py-3 text-right hover:text-[#e8edf3]"
                  >
                    ATM STRIKE <SortIcon col="atm_strike" />
                  </th>
                  <th className="px-3 py-3 text-right">CE · PE</th>
                  <th className="px-3 py-3">CONFLUENCE</th>
                  <th
                    onClick={() => toggleSort("last_bar")}
                    className="cursor-pointer px-4 py-3 text-right hover:text-[#e8edf3]"
                  >
                    LAST BAR <SortIcon col="last_bar" />
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1c232d]/80">
                {sortedRows.map((r) => {
                  const pos = r.change_pct >= 0;
                  return (
                    <tr
                      key={r.symbol}
                      onClick={() => onRowClick(r.symbol)}
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          onRowClick(r.symbol);
                        }
                      }}
                      className="cursor-pointer transition duration-150 hover:bg-[#1c232d]/35 focus:bg-[#1c232d]/45 focus:outline-none"
                    >
                      <td className="px-4 py-3">
                        <div className="font-mono text-sm font-bold text-[#e8edf3]">
                          {r.symbol}
                        </div>
                        <div className="max-w-[200px] truncate text-xs text-[#7d8794]">
                          {r.name} · {r.sector}
                        </div>
                      </td>

                      <td className="px-3 py-3 text-right font-mono">
                        <div className="text-sm font-semibold text-[#e8edf3]">
                          {r.ltp.toFixed(2)}
                        </div>
                        <div
                          className={`text-[11px] ${
                            pos ? "text-[#2ee6a6]" : "text-[#ff4d5e]"
                          }`}
                        >
                          {pos ? "+" : ""}
                          {r.change_pct.toFixed(2)}%
                        </div>
                      </td>

                      <td className="px-3 py-3">
                        <div className="flex items-center gap-2">
                          <DojiCrossRow count={r.streak} />
                          <span className="font-mono text-xs font-medium text-[#e8edf3]">
                            {patternLabel(r.streak)}
                          </span>
                        </div>
                      </td>

                      <td className="px-3 py-3 text-right font-mono text-sm font-semibold text-[#e8edf3]">
                        {r.coil_range_pct.toFixed(2)}%
                      </td>

                      <td className="px-3 py-3 text-right font-mono text-xs">
                        <div className="text-[#2ee6a6]">↗ {r.break_above.toFixed(2)}</div>
                        <div className="text-[#ff4d5e]">↘ {r.break_below.toFixed(2)}</div>
                      </td>

                      <td className="px-3 py-3 text-right font-mono text-sm font-bold text-[#e8edf3]">
                        {r.atm_strike}
                      </td>

                      <td className="px-3 py-3 text-right font-mono text-xs text-[#e8edf3]">
                        <div>
                          <span className="text-[#7d8794]">CE</span>{" "}
                          {r.ce_ltp !== null ? r.ce_ltp.toFixed(2) : "—"}
                        </div>
                        <div>
                          <span className="text-[#7d8794]">PE</span>{" "}
                          {r.pe_ltp !== null ? r.pe_ltp.toFixed(2) : "—"}
                        </div>
                      </td>

                      <td className="px-3 py-3">
                        <div className="flex flex-wrap items-center gap-1 font-mono text-[10px] font-semibold">
                          <span className="rounded border border-[#f5a524]/40 bg-[#f5a524]/15 px-1.5 py-0.5 text-[#f5a524]">
                            STK {r.stk_streak}
                          </span>
                          <span
                            className={`rounded border px-1.5 py-0.5 ${
                              r.ce_streak >= 2
                                ? "border-[#f5a524]/40 bg-[#f5a524]/15 text-[#f5a524]"
                                : "border-[#1c232d] bg-[#07090d] text-[#7d8794]"
                            }`}
                          >
                            CE {r.ce_streak}
                          </span>
                          <span
                            className={`rounded border px-1.5 py-0.5 ${
                              r.pe_streak >= 2
                                ? "border-[#f5a524]/40 bg-[#f5a524]/15 text-[#f5a524]"
                                : "border-[#1c232d] bg-[#07090d] text-[#7d8794]"
                            }`}
                          >
                            PE {r.pe_streak}
                          </span>
                        </div>
                      </td>

                      <td className="px-4 py-3 text-right font-mono text-xs text-[#7d8794]">
                        <span className="inline-flex items-center gap-1.5">
                          {formatLastBar(r.last_bar)}
                          <ChevronRight className="h-4 w-4 text-[#7d8794]" />
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Mobile Cards */}
          <div className="divide-y divide-[#1c232d] md:hidden">
            {sortedRows.map((r) => {
              const pos = r.change_pct >= 0;
              return (
                <button
                  key={r.symbol}
                  type="button"
                  onClick={() => onRowClick(r.symbol)}
                  className="flex w-full flex-col gap-2.5 p-4 text-left transition duration-150 hover:bg-[#1c232d]/30"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-mono text-sm font-bold text-[#e8edf3]">
                        {r.symbol}
                      </div>
                      <div className="text-xs text-[#7d8794]">
                        {r.name} · {r.sector}
                      </div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-sm font-semibold text-[#e8edf3]">
                        {r.ltp.toFixed(2)}
                      </div>
                      <div
                        className={`text-xs ${
                          pos ? "text-[#2ee6a6]" : "text-[#ff4d5e]"
                        }`}
                      >
                        {pos ? "+" : ""}
                        {r.change_pct.toFixed(2)}%
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <DojiCrossRow count={r.streak} />
                      <span className="font-mono text-xs text-[#f5a524]">
                        {patternLabel(r.streak)}
                      </span>
                    </div>
                    <span className="font-mono text-xs text-[#e8edf3]">
                      Coil {r.coil_range_pct.toFixed(2)}% · Strike {r.atm_strike}
                    </span>
                  </div>

                  <div className="flex items-center justify-between font-mono text-[11px]">
                    <span className="text-[#2ee6a6]">↗ {r.break_above.toFixed(2)}</span>
                    <span className="text-[#ff4d5e]">↘ {r.break_below.toFixed(2)}</span>
                    <span className="text-[#7d8794]">
                      STK {r.stk_streak} · CE {r.ce_streak} · PE {r.pe_streak}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </>
      )}
    </section>
  );
};
