import { useRef, useCallback, useEffect, useState } from "react";

interface ThumbnailCyclerProps {
  snapshots: string[];
}

export function ThumbnailCycler({ snapshots }: ThumbnailCyclerProps) {
  const defaultIdx =
    snapshots.length > 1 ? snapshots.length - 2 : 0;
  const [currentSrc, setCurrentSrc] = useState(
    snapshots.length > 0
      ? `/clips/snapshot/${snapshots[defaultIdx]}`
      : "",
  );
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const idxRef = useRef(0);
  const holdTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const canCycle = snapshots.length >= 2;

  const startCycling = useCallback(() => {
    if (!canCycle || intervalRef.current != null) return;
    idxRef.current = 0;
    setCurrentSrc(`/clips/snapshot/${snapshots[0]}`);
    intervalRef.current = setInterval(() => {
      idxRef.current = (idxRef.current + 1) % snapshots.length;
      setCurrentSrc(`/clips/snapshot/${snapshots[idxRef.current]}`);
    }, 500);
  }, [snapshots, canCycle]);

  const stopCycling = useCallback(() => {
    if (holdTimerRef.current != null) clearTimeout(holdTimerRef.current);
    if (intervalRef.current != null) clearInterval(intervalRef.current);
    intervalRef.current = null;
    if (snapshots.length > 0) {
      setCurrentSrc(`/clips/snapshot/${snapshots[defaultIdx]}`);
    }
  }, [snapshots, defaultIdx]);

  useEffect(() => {
    return () => {
      if (intervalRef.current != null) clearInterval(intervalRef.current);
      if (holdTimerRef.current != null) clearTimeout(holdTimerRef.current);
    };
  }, []);

  const handleTouchStart = useCallback(
    (e: React.TouchEvent) => {
      holdTimerRef.current = setTimeout(() => {
        e.preventDefault();
        startCycling();
      }, 200);
    },
    [startCycling],
  );

  return (
    <div
      className="relative pt-[56.25%] bg-black cursor-pointer"
      onMouseEnter={startCycling}
      onMouseLeave={stopCycling}
      onTouchStart={handleTouchStart}
      onTouchEnd={stopCycling}
      onTouchCancel={stopCycling}
    >
      <img
        src={currentSrc}
        alt="Clip thumbnail"
        loading="lazy"
        className="absolute top-0 left-0 w-full h-full object-cover"
      />
    </div>
  );
}
