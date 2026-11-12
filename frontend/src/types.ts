export type Timeframe = "75m" | "1D" | "1W";
export type ScanSource = "stock" | "ce" | "pe";

export interface FilterState {
  tf: Timeframe;
  src: ScanSource;
  min: number;
  body: number;
  sector: string;
  q: string;
}

export interface SectorOption {
  slug: string;
  label: string;
}

export interface ScreenerRow {
  symbol: string;
  name: string;
  sector: string;
  sector_slug: string;
  ltp: number;
  change_pct: number;
  streak: number;
  coil_range_pct: number;
  break_above: number;
  break_below: number;
  atm_strike: number;
  ce_ltp: number | null;
  pe_ltp: number | null;
  stk_streak: number;
  ce_streak: number;
  pe_streak: number;
  last_bar: string;
}

export interface ScreenResponse {
  rows: ScreenerRow[];
  summary: {
    double: number;
    triple: number;
    four_plus: number;
    matching: number;
  };
  expiry: string;
  universe_size: number;
  tf: Timeframe;
  src: ScanSource;
  source: string;
  is_live: boolean;
  last_updated: string;
  latest_bar: string;
}

export interface MetaResponse {
  sectors: SectorOption[];
  universe_size: number;
  expiry: string;
  data_source: string;
  last_updated: string;
  is_live: boolean;
}

export interface CandlePoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface ChartPanelData {
  label: string;
  candles: CandlePoint[];
  doji_indices: number[];
  streak: number;
  break_above: number | null;
  break_below: number | null;
  coil_range_pct: number;
}

export interface StockDetailResponse {
  symbol: string;
  name: string;
  sector: string;
  tf: Timeframe;
  strike: number;
  expiry: string;
  spot: ChartPanelData;
  ce: ChartPanelData;
  pe: ChartPanelData;
}
