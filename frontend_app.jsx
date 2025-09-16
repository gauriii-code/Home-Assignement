import React, { useEffect, useState } from "react";
import { fetchRuns, fetchBars, fetchTrades } from "./api";
import Chart from "./Chart";

function App() {
  const [runs, setRuns] = useState([]);
  const [selected, setSelected] = useState(null);
  const [bars, setBars] = useState([]);
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    fetchRuns().then(setRuns);
  }, []);

  useEffect(() => {
    if (!selected) return;
    Promise.all([fetchBars(selected.id), fetchTrades(selected.id)])
      .then(([barsData, tradesData]) => {
        setBars(barsData);
        setTrades(tradesData);
      })
  }, [selected]);

  return (
    <div style={{ padding: 20 }}>
      <h2>Backtest Runs</h2>
      <ul>
        {runs.map(r => (
          <li key={r.id}>
            <button onClick={() => setSelected(r)}>{r.run_name} - {r.symbol}</button>
          </li>
        ))}
      </ul>
      {selected && (
        <div>
          <h3>{selected.run_name} ({selected.symbol})</h3>
          <pre>{JSON.stringify(selected.metrics, null, 2)}</pre>
          <Chart bars={bars} trades={trades} />
        </div>
      )}
    </div>
  );
}

export default App;
