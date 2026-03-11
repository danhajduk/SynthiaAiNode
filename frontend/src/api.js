export function getApiBase() {
  if (import.meta.env.VITE_API_BASE) {
    return import.meta.env.VITE_API_BASE;
  }
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  return `${protocol}//${hostname}:9002`;
}

export async function apiGet(path) {
  const response = await fetch(`${getApiBase()}${path}`);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || payload.error || `request failed (${response.status})`);
  }
  return payload;
}

export async function apiPost(path, body) {
  const response = await fetch(`${getApiBase()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || payload.error || `request failed (${response.status})`);
  }
  return payload;
}
