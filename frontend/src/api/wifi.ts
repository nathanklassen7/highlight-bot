import type { WifiStatus } from "../types";

export async function getWifiStatus(): Promise<WifiStatus> {
  const res = await fetch("/api/wifi/status");
  return res.json();
}

export async function connectWifi(
  ssid: string,
  password: string,
): Promise<void> {
  await fetch("/api/wifi/connect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ssid, password }),
  });
}

export async function enableHotspot(): Promise<void> {
  await fetch("/api/wifi/hotspot", { method: "POST" });
}
