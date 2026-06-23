const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function sendChat(message, history = []) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  });
  if (!res.ok) throw new Error(`Chat API error: ${res.status}`);
  return res.json();
}

export async function getHistory() {
  const res = await fetch(`${BASE}/api/history`);
  return res.json();
}

export async function checkHealth() {
  try {
    const res = await fetch(`${BASE}/api/health`);
    return res.json();
  } catch {
    return { status: 'offline' };
  }
}

export function connectTaskSocket(taskId, onMessage, onDone, onError) {
  const wsBase = BASE.replace('http', 'ws');
  const ws = new WebSocket(`${wsBase}/ws/run/${taskId}`);

  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.type === 'log')   onMessage(data.message);
    if (data.type === 'done')  onDone(data.message);
    if (data.type === 'error') onError(data.message);
  };

  ws.onerror = () => onError('WebSocket connection failed');
  return ws;
}
