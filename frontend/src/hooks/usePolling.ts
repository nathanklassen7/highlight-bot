import { useEffect, useRef } from "react";

export function usePolling(fn: () => void, intervalMs: number) {
  const savedFn = useRef(fn);
  savedFn.current = fn;

  useEffect(() => {
    savedFn.current();
    const id = setInterval(() => savedFn.current(), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
}
