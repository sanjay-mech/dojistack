import React, { useCallback, useEffect, useState } from "react";
import { Lock } from "lucide-react";
import { fetchMeta, fetchScreen, fetchStockDetail } from "./api";
import { FilterBar } from "./components/FilterBar";
import { Hero } from "./components/Hero";
import { Navbar } from "./components/Navbar";
import { ResultsTable } from "./components/ResultsTable";
import { StockDrawer } from "./components/StockDrawer";
import { SummaryCards } from "./components/SummaryCards";
import {
  FilterState,
  ScanSource,
  ScreenResponse,
  SectorOption,
  StockDetailResponse,
  Timeframe,
} from "./types";

function parseFiltersFromUrl(): FilterState {
  const params = new URLSearchParams(window.location.search);
  const tfRaw = params.get("tf");
  const tf: Timeframe =
    tfRaw === "75m" || tfRaw === "1D" || tfRaw === "1W" ? tfRaw : "1D";

  const srcRaw = (params.get("src") || "stock").toLowerCase();
  const src: ScanSource =
    srcRaw === "ce" || srcRaw === "pe" || srcRaw === "stock" ? srcRaw : "stock";

  const minParsed = parseInt(params.get("min") || "2", 10);
  const min = [2, 3, 4, 5].includes(minParsed) ? minParsed : 2;

  const bodyParsed = parseInt(params.get("body") || "10", 10);
  const body =
    Number.isFinite(bodyParsed) && bodyParsed >= 1 && bodyParsed <= 30
      ? bodyParsed
      : 10;

  const sector = params.get("sector") || "all";
  const q = params.get("q") || "";

  return { tf, src, min, body, sector, q };
}

function writeFiltersToUrl(f: FilterState) {
  const params = new URLSearchParams();
  params.set("tf", f.tf);
  params.set("src", f.src);
  params.set("min", String(f.min));
  params.set("body", String(f.body));
  params.set("sector", f.sector);
  params.set("q", f.q);
  const next = `${window.location.pathname}?${params.toString()}`;
  window.history.replaceState(null, "", next);
}

export function App() {
  const [filters, setFilters] = useState<FilterState>(() => parseFiltersFromUrl());
  const [sectors, setSectors] = useState<SectorOption[]>([]);
  const [universeSize, setUniverseSize] = useState<number>(76);
  const [screenData, setScreenData] = useState<ScreenResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [stockDetail, setStockDetail] = useState<StockDetailResponse | null>(null);

  const updateFilters = useCallback((patch: Partial<FilterState>) => {
    setFilters((prev) => {
      const next = { ...prev, ...patch };
      writeFiltersToUrl(next);
      return next;
    });
  }, []);

  useEffect(() => {
    writeFiltersToUrl(filters);
  }, []); // ensure initial URL sync

  useEffect(() => {
    fetchMeta()
      .then((m) => {
        setSectors(m.sectors || []);
        setUniverseSize(m.universe_size || 76);
      })
      .catch(() => {
        // Ignore; screen call handles error state
      });
  }, []);

  const loadScreen = useCallback(
    async (refresh = false) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchScreen(filters, refresh);
        setScreenData(res);
        setUniverseSize(res.universe_size);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to connect to backend API"
        );
      } finally {
        setLoading(false);
      }
    },
    [filters]
  );

  useEffect(() => {
    loadScreen(false);
  }, [loadScreen]);

  const handleRowClick = async (symbol: string) => {
    setDrawerOpen(true);
    setDrawerLoading(true);
    setStockDetail(null);
    try {
      const detail = await fetchStockDetail(symbol, filters.tf, filters.body);
      setStockDetail(detail);
    } catch {
      setStockDetail(null);
    } finally {
      setDrawerLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#07090d] text-[#e8edf3]">
      <Navbar
        isLive={screenData?.is_live ?? false}
        lastUpdated={screenData?.last_updated ?? "12 Nov 2026 · 15:30 IST"}
        source={screenData?.source ?? "Yahoo + Bhavcopy"}
        loading={loading}
        onRefresh={() => loadScreen(true)}
      />

      <Hero universeSize={universeSize} />

      <main className="mx-auto max-w-[1400px] space-y-5 px-4 py-6 sm:px-6">
        <FilterBar
          filters={filters}
          sectors={sectors}
          onChange={updateFilters}
        />

        <SummaryCards
          filters={filters}
          summary={
            screenData?.summary ?? {
              double: 0,
              triple: 0,
              four_plus: 0,
              matching: 0,
            }
          }
          universeSize={universeSize}
          expiry={screenData?.expiry ?? "2026-11-26"}
          onSelectMin={(min) => updateFilters({ min })}
        />

        {error && (
          <div className="rounded-xl border border-[#ff4d5e]/40 bg-[#ff4d5e]/10 px-4 py-3 font-mono text-xs text-[#ff4d5e]">
            Backend unreachable ({error}). Start FastAPI with{" "}
            <span className="underline">uvicorn backend.main:app --reload</span>.
          </div>
        )}

        <ResultsTable
          rows={screenData?.rows ?? []}
          tf={filters.tf}
          loading={loading}
          onRowClick={handleRowClick}
        />
      </main>

      <footer className="mx-auto max-w-[1400px] border-t border-[#1c232d] px-4 py-6 text-center font-mono text-[11px] text-[#7d8794] sm:px-6">
        For educational use. Not investment advice.
      </footer>

      {/* Floating Private Pill */}
      <div className="fixed bottom-4 right-4 z-40 inline-flex items-center gap-1.5 rounded-full border border-[#1c232d] bg-[#0d1117]/95 px-3 py-1.5 font-mono text-[11px] text-[#7d8794] shadow-lg backdrop-blur">
        <Lock className="h-3 w-3 text-[#f5a524]" />
        <span>Private</span>
      </div>

      <StockDrawer
        detail={stockDetail}
        loading={drawerLoading}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
}

export default App;
