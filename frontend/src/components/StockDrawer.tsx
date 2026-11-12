import React, { useEffect, useRef } from "react";
import {
  ColorType,
  CrosshairMode,
  LineStyle,
  Time,
  createChart,
} from "lightweight-charts";
import { X } from "lucide-react";
import { ChartPanelData, StockDetailResponse } from "../types";

interface StockDrawerProps {
  detail: StockDetailResponse | null;
  loading: boolean;
  open: boolean;
  onClose: () => void;
}

function toChartTime(raw: string): Time {
  if (raw.length <= 10) {
    return raw as Time; // YYYY-MM-DD
  }
  // Intraday "YYYY-MM-DD HH:MM" -> epoch seconds
  const iso = raw.replace(" ", "T") + ":00+05:30";
  return Math.floor(new Date(iso).getTime() / 1000) as Time;
}

const CandlePanel: React.FC<{ panel: ChartPanelData }> = ({ panel }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el || !panel.candles.length) return;

    const chart = createChart(el, {
      width: el.clientWidth,
      height: 210,
      layout: {
        background: { type: ColorType.Solid, color: "#07090d" },
        textColor: "#7d8794",
        fontFamily: "JetBrains Mono, monospace",
        fontSize: 10,
      },
      grid: {
        vertLines: { color: "#1c232d" },
        horzLines: { color: "#1c232d" },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: "#1c232d",
      },
      timeScale: {
        borderColor: "#1c232d",
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const series = chart.addCandlestickSeries({
      upColor: "#2ee6a6",
      downColor: "#ff4d5e",
      wickUpColor: "#2ee6a6",
      wickDownColor: "#ff4d5e",
      borderVisible: false,
    });

    const dojiSet = new Set(panel.doji_indices);
    const data = panel.candles.map((c, idx) => {
      const isDoji = dojiSet.has(idx);
      const base = {
        time: toChartTime(c.time),
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      };
      if (isDoji) {
        return {
          ...base,
          color: "#f5a524",
          wickColor: "#f5a524",
          borderColor: "#f5a524",
        };
      }
      return base;
    });

    series.setData(data);

    if (panel.break_above !== null) {
      series.createPriceLine({
        price: panel.break_above,
        color: "#2ee6a6",
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: true,
        title: "Break ↑",
      });
    }
    if (panel.break_below !== null) {
      series.createPriceLine({
        price: panel.break_below,
        color: "#ff4d5e",
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: true,
        title: "Break ↓",
      });
    }

    chart.timeScale().fitContent();

    const ro = new ResizeObserver(() => {
      if (el) {
        chart.applyOptions({ width: el.clientWidth });
      }
    });
    ro.observe(el);

    return () => {
      ro.disconnect();
      chart.remove();
    };
  }, [panel]);

  return (
    <div className="rounded-xl border border-[#1c232d] bg-[#07090d] p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="font-mono text-xs font-semibold text-[#e8edf3]">
          {panel.label}
        </span>
        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span
            className={`rounded px-1.5 py-0.5 ${
              panel.streak >= 2
                ? "bg-[#f5a524]/15 text-[#f5a524]"
                : "bg-[#1c232d] text-[#7d8794]"
            }`}
          >
            {panel.streak}× doji
          </span>
          {panel.break_above !== null && (
            <span className="text-[#2ee6a6]">↗ {panel.break_above.toFixed(2)}</span>
          )}
          {panel.break_below !== null && (
            <span className="text-[#ff4d5e]">↘ {panel.break_below.toFixed(2)}</span>
          )}
        </div>
      </div>

      {panel.candles.length ? (
        <div ref={containerRef} className="w-full" />
      ) : (
        <div className="flex h-[140px] items-center justify-center font-mono text-xs text-[#7d8794]">
          No option candles available (ingest Bhavcopy or enable LIVE_MODE for 75m options)
        </div>
      )}
    </div>
  );
};

export const StockDrawer: React.FC<StockDrawerProps> = ({
  detail,
  loading,
  open,
  onClose,
}) => {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (open) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end"
      role="dialog"
      aria-modal="true"
      aria-label="Stock chart drawer"
    >
      <div
        className="fixed inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      <aside className="relative z-10 flex h-full w-full max-w-2xl flex-col overflow-y-auto border-l border-[#1c232d] bg-[#0d1117] p-5 shadow-2xl">
        <div className="mb-4 flex items-start justify-between border-b border-[#1c232d] pb-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-mono text-xl font-bold text-[#e8edf3]">
                {detail?.symbol || "Loading…"}
              </h2>
              {detail && (
                <span className="rounded border border-[#f5a524]/40 bg-[#f5a524]/15 px-2 py-0.5 font-mono text-[11px] font-semibold text-[#f5a524]">
                  {detail.tf} · ATM {detail.strike}
                </span>
              )}
            </div>
            {detail && (
              <p className="mt-0.5 text-xs text-[#7d8794]">
                {detail.name} · {detail.sector} · exp {detail.expiry}
              </p>
            )}
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close drawer"
            className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-[#1c232d] bg-[#07090d] text-[#7d8794] transition duration-150 hover:text-[#e8edf3]"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {loading || !detail ? (
          <div className="space-y-4">
            {[1, 2, 3].map((k) => (
              <div
                key={k}
                className="h-56 animate-pulse rounded-xl border border-[#1c232d] bg-[#07090d]"
              />
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            <CandlePanel panel={detail.spot} />
            <CandlePanel panel={detail.ce} />
            <CandlePanel panel={detail.pe} />
          </div>
        )}
      </aside>
    </div>
  );
};
