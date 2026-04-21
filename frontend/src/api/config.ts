import type { ConfigData } from "../types";

export async function getConfig(): Promise<ConfigData> {
  const res = await fetch("/api/config");
  return res.json();
}

export async function updateConfigField(
  key: string,
  value: string,
): Promise<{ status?: string; error?: string }> {
  const res = await fetch("/api/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key, value }),
  });
  return res.json();
}

export async function applyPreset(
  preset: string,
): Promise<{ status?: string; error?: string }> {
  const res = await fetch("/api/config/preset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preset }),
  });
  return res.json();
}

export async function updateTimeout(
  value: string,
): Promise<{ status?: string; error?: string }> {
  const res = await fetch("/api/config/timeout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value }),
  });
  return res.json();
}

export async function resetConfig(): Promise<{
  status?: string;
  error?: string;
}> {
  const res = await fetch("/api/config/reset", { method: "POST" });
  return res.json();
}

export async function captureSnapshot(): Promise<{
  status?: string;
  ts?: number;
  error?: string;
}> {
  const res = await fetch("/api/snapshot", { method: "POST" });
  return res.json();
}
