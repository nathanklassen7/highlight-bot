import { useState, useCallback } from "react";
import { getTemperature } from "../api/temperature";
import { usePolling } from "./usePolling";

export function useTemperature(intervalMs = 5000) {
  const [temp, setTemp] = useState<number | null>(null);

  const poll = useCallback(async () => {
    setTemp(await getTemperature());
  }, []);

  usePolling(poll, intervalMs);

  return temp;
}
