import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

export async function fetchRuns() {
  const r = await axios.get(`${API_BASE}/runs`);
  return r.data;
}
export async function fetchBars(runId) {
  const r = await axios.get(`${API_BASE}/runs/${runId}/bars`);
  return r.data;
}
export async function fetchTrades(runId) {
  const r = await axios.get(`${API_BASE}/runs/${runId}/trades`);
  return r.data;
}
