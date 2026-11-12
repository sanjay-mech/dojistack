import {
  FilterState,
  MetaResponse,
  ScreenResponse,
  StockDetailResponse,
  Timeframe,
} from "./types";

const API_BASE = (import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");

export async function fetchMeta(): Promise<MetaResponse> {
  const res = await fetch(`${API_BASE}/api/meta`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchScreen(
  filters: FilterState,
  refresh = false
): Promise<ScreenResponse> {
  const params = new URLSearchParams({
    tf: filters.tf,
    src: filters.src,
    min: String(filters.min),
    body: String(filters.body),
    sector: filters.sector,
    q: filters.q,
    refresh: refresh ? "true" : "false",
  });
  const res = await fetch(`${API_BASE}/api/screen?${params.toString()}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchStockDetail(
  symbol: string,
  tf: Timeframe,
  body: number
): Promise<StockDetailResponse> {
  const params = new URLSearchParams({ tf, body: String(body) });
  const res = await fetch(
    `${API_BASE}/api/stock/${encodeURIComponent(symbol)}?${params.toString()}`
  );
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
