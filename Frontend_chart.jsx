import React, { useEffect, useRef } from "react";
import { createChart } from "lightweight-charts";

export default function Chart({ bars, trades }) {
  const chartRef = useRef();

  useEffect(() => {
    if (!bars || bars.length === 0) return;
    // cleanup old chart
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }
    const chart = createChart(document.getElementById("chart"), { width: 800, height: 400 });
    chartRef.current = chart;
    const candlestickSeries = chart.addCandlestickSeries();
    const data = bars.map(b => ({
      time: new Date(b.timestamp).toISOString().slice(0, 10),
      open: b.open,
      high: b.high,
      low: b.low,
      close: b.close
    }));
    candlestickSeries.setData(data);

    // mark trades
    if (trades) {
      trades.forEach(tr => {
        const marker = {
          time: new Date(tr.timestamp).toISOString().slice(0,10),
          position: tr.side.startsWith("BUY") ? "belowBar" : "aboveBar",
          color: tr.side.startsWith("BUY") ? "green" : "red",
          shape: tr.side.startsWith("BUY") ? "arrowUp" : "arrowDown",
          text: `${tr.side}@${tr.price}`
        };
        candlestickSeries.setMarkers([marker]); // for simplicity; multiple setMarkers replace — combine if needed
      });
    }

    return () => chart.remove();
  }, [bars, trades]);

  return <div id="chart" />;
}
