import { useState, useEffect, type RefObject } from "react";
import { trimClip } from "../../api/clips";

interface TrimControlsProps {
  filename: string;
  videoRef: RefObject<HTMLVideoElement | null>;
}

function formatTime(frames: number): string {
  const seconds = Math.floor(frames / 60);
  const remainingFrames = Math.round(frames - seconds * 60);
  return `${seconds.toString().padStart(2, "0")}:${remainingFrames.toString().padStart(2, "0")}`;
}

export function TrimControls({ filename, videoRef }: TrimControlsProps) {
  const [maxVal, setMaxVal] = useState(100);
  const [startVal, setStartVal] = useState(0);
  const [endVal, setEndVal] = useState(100);
  const [trimming, setTrimming] = useState(false);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    function onMeta() {
      const dur = video!.duration * 60;
      setMaxVal(dur);
      setEndVal(dur);
    }
    video.addEventListener("loadedmetadata", onMeta);
    return () => video.removeEventListener("loadedmetadata", onMeta);
  }, [videoRef]);

  function handleStartChange(v: number) {
    setStartVal(v >= endVal ? endVal - 1 : v);
  }

  function handleEndChange(v: number) {
    setEndVal(v <= startVal ? startVal + 1 : v);
  }

  async function handleTrim() {
    setTrimming(true);
    try {
      const res = await trimClip(filename, startVal / 60, endVal / 60);
      if (res.error) {
        alert("Error trimming video");
      } else {
        window.location.reload();
      }
    } catch {
      alert("Error trimming video");
    } finally {
      setTrimming(false);
    }
  }

  return (
    <div className="bg-black/80 p-4 rounded-lg mt-4">
      <h3 className="text-lg font-semibold text-white mb-4">Trim Video</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-300">
            Start Time
          </label>
          <div className="mt-1 flex items-center space-x-2">
            <input
              type="range"
              min={0}
              max={maxVal}
              value={startVal}
              onChange={(e) => handleStartChange(Number(e.target.value))}
              className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
            />
            <span className="font-mono text-[1.1em] text-white">
              {formatTime(startVal)}
            </span>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300">
            End Time
          </label>
          <div className="mt-1 flex items-center space-x-2">
            <input
              type="range"
              min={0}
              max={maxVal}
              value={endVal}
              onChange={(e) => handleEndChange(Number(e.target.value))}
              className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
            />
            <span className="font-mono text-[1.1em] text-white">
              {formatTime(endVal)}
            </span>
          </div>
        </div>
      </div>
      <div className="mt-4 flex justify-end">
        <button
          onClick={handleTrim}
          disabled={trimming}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          {trimming ? "Trimming..." : "Trim Video"}
        </button>
      </div>
    </div>
  );
}
