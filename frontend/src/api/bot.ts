import type { BotState } from "../types";

export async function getBotStatus(): Promise<BotState> {
  const res = await fetch("/api/bot/status");
  const data = await res.json();
  return data.state;
}

export async function postBotAction(
  action: "start" | "stop" | "clip" | "poke",
): Promise<void> {
  await fetch("/api/bot/action", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
}
