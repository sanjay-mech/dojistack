import React from "react";
import { RefreshCw } from "lucide-react";
import { DojiCrossRow } from "./DojiIcons";

interface NavbarProps {
  isLive: boolean;
  lastUpdated: string;
  source: string;
  loading: boolean;
  onRefresh: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  isLive,
  lastUpdated,
  source,
  loading,
  onRefresh,
}) => {
  return (
    <header className="sticky top-0 z-30 border-b border-[#1c232d] bg-[#07090d]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1400px] items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-xl border border-[#f5a524]/45 bg-[#f5a524]/10 px-2.5 py-1.5">
            <DojiCrossRow count={3} />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-display text-lg font-bold tracking-tight text-[#e8edf3]">
              DojiStack
            </span>
            <span className="rounded border border-[#f5a524]/35 bg-[#f5a524]/10 px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider text-[#f5a524]">
              NSE F&amp;O
            </span>
          </div>
          <span className="hidden rounded-full border border-[#1c232d] bg-[#0d1117] px-3 py-1 text-xs font-medium text-[#e8edf3] sm:inline-flex">
            Screener
          </span>
        </div>

        <div className="flex items-center gap-2.5">
          <span className="hidden rounded-full border border-[#1c232d] bg-[#0d1117] px-2.5 py-1 font-mono text-[11px] text-[#7d8794] md:inline-flex">
            {source}
          </span>

          <div className="flex items-center gap-2 rounded-full border border-[#1c232d] bg-[#0d1117] px-3 py-1 font-mono text-[11px] text-[#e8edf3]">
            {isLive ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#2ee6a6] opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-[#2ee6a6]" />
                </span>
                <span className="text-[#2ee6a6] font-semibold">LIVE</span>
                <span className="hidden text-[#7d8794] sm:inline">· {lastUpdated}</span>
              </>
            ) : (
              <>
                <span className="h-2 w-2 rounded-full bg-[#f5a524]" />
                <span className="text-[#7d8794]">
                  Preview feed · <span className="text-[#e8edf3]">{lastUpdated}</span>
                </span>
              </>
            )}
          </div>

          <button
            type="button"
            onClick={onRefresh}
            disabled={loading}
            aria-label="Refresh market scan"
            className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-[#1c232d] bg-[#0d1117] text-[#7d8794] transition duration-150 hover:border-[#f5a524]/50 hover:text-[#e8edf3] disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin text-[#f5a524]" : ""}`} />
          </button>
        </div>
      </div>
    </header>
  );
};
