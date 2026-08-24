import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export async function fetchMapState() {
  const { data } = await axios.get(`${API}/map/state`);
  return data;
}

export async function fetchNation(nationId) {
  const { data } = await axios.get(`${API}/nation/${nationId}`);
  return data;
}

export async function fetchSettlement(id) {
  const { data } = await axios.get(`${API}/settlement/${id}`);
  return data;
}

export async function transferTerritory(sourceNationId, targetNationId, lasso) {
  const { data } = await axios.post(`${API}/map/transfer`, {
    source_nation_id: sourceNationId,
    target_nation_id: targetNationId,
    lasso,
  });
  return data;
}

export async function resetWorld(clearTraces = false) {
  const { data } = await axios.post(`${API}/map/reset`, null, {
    params: clearTraces ? { clear_traces: true } : {},
  });
  return data;
}

export async function applyTrace(type, polygon, value = null) {
  const { data } = await axios.post(`${API}/trace/apply`, { type, polygon, value });
  return data;
}

export async function getTraces() {
  const { data } = await axios.get(`${API}/trace/overrides`);
  return data;
}

export async function deleteTrace(traceId) {
  const { data } = await axios.delete(`${API}/trace/overrides/${traceId}`);
  return data;
}
