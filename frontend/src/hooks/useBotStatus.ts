import { useState, useCallback } from "react";
import { getBotStatus } from "../api/bot";
import { usePolling } from "./usePolling";
import type { BotState } from "../types";

export function useBotStatus(intervalMs = 2000) {
  const [state, setState] = useState<BotState>("unknown");

  const poll = useCallback(async () => {
    try {
      setState(await getBotStatus());
    } catch {
      setState("unknown");
    }
  }, []);

  usePolling(poll, intervalMs);

  return { state, refresh: poll };
}
