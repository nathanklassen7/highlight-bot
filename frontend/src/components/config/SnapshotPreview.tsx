import { useState } from "react";
import { captureSnapshot } from "../../api/config";
import { useToast } from "../shared/Toast";

export function SnapshotPreview() {
  const [src, setSrc] = useState("/api/snapshot");
  const [refreshing, setRefreshing] = useState(false);
  const { showError } = useToast();

  async function handleRefresh() {
    setRefreshing(true);
    try {
      const data = await captureSnapshot();
      if (data.status === "ok") {
        setSrc(`/api/snapshot?${data.ts}`);
      } else {
        showError("Snapshot failed");
      }
    } catch {
      showError("Failed to capture frame");
    }
    setRefreshing(false);
  }

  return (
    <>
      <div className="bg-black rounded-lg overflow-hidden">
        <img
          src={src}
          alt="Camera snapshot"
          className="w-full rounded-lg bg-[#111] min-h-[180px] object-contain"
        />
      </div>
      <button
        onClick={handleRefresh}
        disabled={refreshing}
        className="w-full p-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 text-sm disabled:opacity-50"
      >
        {refreshing ? "Capturing..." : "Refresh Snapshot"}
      </button>
    </>
  );
}
